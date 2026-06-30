#!/usr/bin/env bash
# setup_shared_skills.sh
#
# Consolidates AI skills from Claude / Codex / Cursor / opencode into a single
# canonical directory (~/ai/skills) and symlinks each provider back to it.
#
# Usage:
#   ./setup_shared_skills.sh              # dry run, prints what it would do
#   ./setup_shared_skills.sh --apply      # actually do it
#
# Idempotent: safe to run multiple times. Existing correct symlinks are left
# alone; existing real directories are migrated into the canonical dir.
#
# Assumptions (verified on this machine at time of writing):
#   - ~/.claude, ~/.codex, ~/.cursor, and ~/.config are all root-owned.
#     The script auto-detects this per path (sudo_for) and uses sudo only
#     where needed; it will work on a machine where those are user-owned too.
#   - ~/.cursor/skills-cursor contains Cursor-managed skills we must NOT touch.
#   - opencode auto-discovers ~/.claude/skills, so no explicit opencode symlink
#     is strictly needed; script still creates one under ~/.config/opencode for
#     robustness.

set -euo pipefail

# -------- configuration --------

CANONICAL="${HOME}/ai"
SKILLS_DIR="${CANONICAL}/skills"
AGENTS_FILE="${CANONICAL}/AGENTS.md"

CLAUDE_SKILLS="${HOME}/.claude/skills"
CODEX_SKILLS="${HOME}/.codex/skills"
OPENCODE_SKILLS="${HOME}/.config/opencode/skills"
CURSOR_SKILLS="${HOME}/.cursor/skills-cursor"

CLAUDE_RULES="${HOME}/.claude/CLAUDE.md"
CODEX_RULES="${HOME}/.codex/AGENTS.md"
OPENCODE_RULES="${HOME}/.config/opencode/AGENTS.md"

# Skills that are provider-managed or repo-scoped -- never touch these.
CURSOR_MANAGED=(
  babysit canvas create-hook create-rule create-skill create-subagent
  migrate-to-skills shell statusline update-cli-config update-cursor-settings
)
CLAUDE_SKIP=( add-backend-endpoint )   # already a repo-scoped symlink
CODEX_SKIP=( .system )                 # Codex built-ins

# -------- flags --------

APPLY=0
for arg in "$@"; do
  case "$arg" in
    --apply) APPLY=1 ;;
    -h|--help)
      sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "unknown argument: $arg" >&2
      echo "usage: $0 [--apply]" >&2
      exit 2
      ;;
  esac
done

# -------- helpers --------

log()  { printf '  %s\n' "$*"; }
step() { printf '\n==> %s\n' "$*"; }

# Returns "--sudo" if the given path (or its nearest existing ancestor) is not
# writable by the current user. On this machine ~/.claude, ~/.codex, ~/.cursor,
# and ~/.config are all root-owned, so writes into them need sudo.
sudo_for() {
  local p="$1"
  while [[ ! -e "$p" ]]; do p="$(dirname "$p")"; done
  if [[ -w "$p" ]]; then
    echo ""
  else
    echo "--sudo"
  fi
}

# run [--sudo] CMD ARG... -- prints the command and executes it as argv (no
# eval, no shell expansion of args). In dry-run mode, prints only.
run() {
  local -a prefix=()
  if [[ "${1:-}" == "--sudo" ]]; then
    prefix=(sudo)
    shift
  fi
  # Print a shell-quoted version so the user can copy/paste if they want.
  printf '   $'
  for a in "${prefix[@]}" "$@"; do printf ' %q' "$a"; done
  printf '\n'
  if (( APPLY )); then
    "${prefix[@]}" "$@"
  fi
}

# Does $1 exist as a symlink whose resolved target equals $2?
link_points_to() {
  local link="$1" target="$2"
  [[ -L "$link" ]] && [[ "$(readlink -f "$link")" == "$(readlink -f "$target")" ]]
}

in_array() {
  local needle="$1"; shift
  local hay
  for hay in "$@"; do [[ "$hay" == "$needle" ]] && return 0; done
  return 1
}

# -------- steps --------

ensure_canonical() {
  step "Canonical dir: ${CANONICAL}"
  if [[ ! -d "$SKILLS_DIR" ]]; then
    run mkdir -p "$SKILLS_DIR"
  else
    log "exists: ${SKILLS_DIR}"
  fi
  if [[ ! -f "$AGENTS_FILE" ]]; then
    run touch "$AGENTS_FILE"
    log "(put your global rules into ${AGENTS_FILE} later)"
  fi
}

# Move a real skill dir from a provider into the canonical dir, then leave a
# symlink behind.
#
# Collision handling (the safe bit): if ${SKILLS_DIR}/${name} already exists,
# we compare contents via `diff -r`:
#   - identical  -> the provider copy is a true duplicate, safe to delete and
#                   replace with a symlink.
#   - different  -> DO NOT touch either copy. Move the provider copy aside to
#                   ${src}.conflict.<timestamp> and bail out. User must resolve
#                   manually.
migrate_skill() {
  local src="$1"
  local name; name="$(basename "$src")"
  local dest="${SKILLS_DIR}/${name}"
  local needs_src; needs_src="$(sudo_for "$src")"

  if link_points_to "$src" "$dest"; then
    log "ok: ${src} already -> ${dest}"
    return
  fi

  if [[ -L "$src" ]]; then
    log "skip (external symlink, left alone): ${src} -> $(readlink "$src")"
    return
  fi

  if [[ ! -d "$src" ]]; then
    log "skip (not a directory): ${src}"
    return
  fi

  if [[ -e "$dest" ]]; then
    if diff -rq "$src" "$dest" >/dev/null 2>&1; then
      log "duplicate (byte-identical) of canonical ${name}; removing ${src}"
      run $needs_src rm -rf "$src"
    else
      local backup
      backup="${src}.conflict.$(date +%s)"
      log "CONFLICT: ${src} differs from canonical ${dest}"
      log "  provider copy will be moved to ${backup} for manual review"
      log "  resolve with: diff -r '${backup}' '${dest}'"
      run $needs_src mv "$src" "$backup"
      return
    fi
  else
    log "migrating ${src} -> ${dest}"
    # Copy-then-remove across owners. cp -a preserves root ownership from
    # ~/.claude etc., so chown back to the user afterwards (needs sudo because
    # only the current owner or root can chown).
    run $needs_src cp -a "$src" "$dest"
    if [[ -n "$needs_src" ]]; then
      run --sudo chown -R "${USER}:${USER}" "$dest"
    fi
    run $needs_src rm -rf "$src"
  fi
  run $needs_src ln -s "$dest" "$src"
}

# After all skills are in the canonical dir, make sure each provider has a
# symlink for every canonical skill (skipping provider-managed ones).
link_provider() {
  local provider_dir="$1"; shift
  local -a skip=( "$@" )
  local needs_dir; needs_dir="$(sudo_for "$provider_dir")"

  step "Link ${provider_dir} -> canonical"
  run $needs_dir mkdir -p "$provider_dir"

  local skill name target link
  for skill in "${SKILLS_DIR}"/*; do
    [[ -d "$skill" ]] || continue
    name="$(basename "$skill")"
    if in_array "$name" "${skip[@]}"; then
      log "skip (provider-managed): ${name}"
      continue
    fi
    target="$skill"
    link="${provider_dir}/${name}"
    if link_points_to "$link" "$target"; then
      log "ok: ${link}"
    elif [[ -L "$link" ]]; then
      log "conflict (symlink points elsewhere, manual review): ${link} -> $(readlink "$link")"
    elif [[ -e "$link" ]]; then
      # A real file/dir with this name exists in the provider dir. Never
      # overwrite -- for Cursor this catches any provider-managed skill not
      # yet in the static skip list.
      log "conflict (real file/dir in provider slot, manual review): ${link}"
    else
      run $needs_dir ln -s "$target" "$link"
    fi
  done
}

link_rules_file() {
  local link="$1"
  local needs_link; needs_link="$(sudo_for "$link")"
  local parent; parent="$(dirname "$link")"
  local needs_parent; needs_parent="$(sudo_for "$parent")"

  if link_points_to "$link" "$AGENTS_FILE"; then
    log "ok: ${link}"
    return
  fi
  if [[ -e "$link" && ! -L "$link" ]]; then
    # Real file with existing content -- refuse to clobber even if empty.
    # User can delete it manually if they're sure.
    log "conflict (not a symlink, manual review): ${link}"
    return
  fi
  run $needs_parent mkdir -p "$parent"
  # -sf here only replaces an existing *symlink* (we already refused above
  # if it's a real file), which is the intended behavior.
  run $needs_link ln -sf "$AGENTS_FILE" "$link"
}

# -------- main --------

if (( APPLY )); then
  echo "MODE: APPLY (changes will be made)"
else
  echo "MODE: DRY RUN (re-run with --apply to execute)"
  echo "NOTE: dry-run does not replay side effects between steps. For example,"
  echo "      if two providers both have skill 'X', the second migration shows"
  echo "      a plain 'migrating' line but under --apply the script will detect"
  echo "      the duplicate and either deduplicate (identical) or move the"
  echo "      loser to X.conflict.<ts> for manual review (different)."
fi

ensure_canonical

step "Migrate existing skills into ${SKILLS_DIR}"
migrate_from_provider() {
  local provider_dir="$1"; shift
  local reason="$1"; shift
  local -a skip=( "$@" )
  [[ -d "$provider_dir" ]] || return 0
  local d name
  for d in "$provider_dir"/*; do
    [[ -e "$d" ]] || continue
    name="$(basename "$d")"
    if in_array "$name" "${skip[@]}"; then
      log "skip (${reason}): ${d}"
      continue
    fi
    # Only real directories or symlinks-to-dirs count as skills.
    if [[ ! -d "$d" ]]; then
      log "skip (not a directory): ${d}"
      continue
    fi
    migrate_skill "$d"
  done
}
migrate_from_provider "$CLAUDE_SKILLS" "repo-scoped"       "${CLAUDE_SKIP[@]}"
migrate_from_provider "$CODEX_SKILLS"  "provider built-in" "${CODEX_SKIP[@]}"

# Ensure every provider has per-skill symlinks back to canonical.
link_provider "$CLAUDE_SKILLS"    "${CLAUDE_SKIP[@]}"
link_provider "$CODEX_SKILLS"     "${CODEX_SKIP[@]}"
link_provider "$OPENCODE_SKILLS"
link_provider "$CURSOR_SKILLS"    "${CURSOR_MANAGED[@]}"

step "Link shared AGENTS.md"
link_rules_file "$CLAUDE_RULES"
link_rules_file "$CODEX_RULES"
link_rules_file "$OPENCODE_RULES"

step "Done"
if (( APPLY )); then
  echo "Verify with:"
  echo "  ls -la ~/.claude/skills ~/.codex/skills ~/.cursor/skills-cursor ~/.config/opencode/skills"
  echo "  ls -la ~/.claude/CLAUDE.md ~/.codex/AGENTS.md ~/.config/opencode/AGENTS.md"
else
  echo "No changes made. Re-run with --apply when you're ready."
fi
