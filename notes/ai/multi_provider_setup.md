# Multi-Provider AI Setup: Shared Skills & Resources

Goal: maintain a single source of truth for AI skills and global rules/AGENTS.md, and have every LLM provider on this machine consume them. No duplication, edit once, available everywhere.

Providers in scope:

- Claude (CLI / terminal)
- Codex (VSCode extension, backed by `~/.codex`)
- opencode (CLI)
- Cursor (IDE)

______________________________________________________________________

## TL;DR

1. Pick one canonical directory to hold every skill: `~/ai/skills/`.
1. Symlink each provider's skills directory (or individual skills inside it) to the canonical dir.
1. Keep a single `AGENTS.md` (global rules) in the canonical dir and symlink it to every provider that supports one.

Provider-specific skill directories on this machine:

| Provider | Skills path | Global rules file |
| --------- | ------------------------------------- | ---------------------------- |
| Claude | `~/.claude/skills/` | `~/.claude/CLAUDE.md` |
| Codex | `~/.codex/skills/` | `~/.codex/AGENTS.md` |
| opencode | `~/.config/opencode/skills/` *(also auto-reads `~/.claude/skills/` and `~/.agents/skills/`)* | `~/.config/opencode/AGENTS.md` |
| Cursor | `~/.cursor/skills-cursor/` | `~/.cursor/rules/` or project `AGENTS.md` |

Key insight: opencode natively falls back to `~/.claude/skills/` and `~/.agents/skills/`, so you don't even need a symlink for it if your canonical dir is one of those.

______________________________________________________________________

## Design Decision: Canonical Directory

Use `~/ai/` as the root:

```
~/ai/
├── skills/                 <- every SKILL.md lives under here
│   ├── grill-me/
│   │   └── SKILL.md
│   ├── create-pr/
│   │   └── SKILL.md
│   └── ...
├── AGENTS.md               <- shared global rules
└── README.md
```

Why not use `~/.claude/skills/` directly as canonical?

- It's provider-named, which is misleading once other tools point at it.
- Putting it under `~/ai/` keeps it tool-neutral.

______________________________________________________________________

## Step-by-Step Setup

### 1. Create the canonical directory

```bash
mkdir -p ~/ai/skills
```

Move any existing skills into it. On this machine, both `~/.claude/skills/grill-me/` and `~/.codex/skills/grill-me/` are real directories (duplicated). Consolidate:

```bash
mv ~/.claude/skills/grill-me ~/ai/skills/
rm -rf ~/.codex/skills/grill-me   # duplicate
```

Repeat for every other skill you've authored.

### 2. Wire up Claude

Claude reads `~/.claude/skills/<name>/SKILL.md`. Two options:

Option A — per-skill symlink (recommended): keeps Claude's dir usable for provider-specific skills that you *don't* want shared.

```bash
ln -s ~/ai/skills/grill-me ~/.claude/skills/grill-me
```

Option B — whole-directory symlink: simplest, but all-or-nothing.

```bash
rm -rf ~/.claude/skills
ln -s ~/ai/skills ~/.claude/skills
```

### 3. Wire up Codex

Same layout as Claude (`~/.codex/skills/<name>/SKILL.md`). Pick the same option you used for Claude:

```bash
ln -s ~/ai/skills/grill-me ~/.codex/skills/grill-me
# or, whole-directory:
rm -rf ~/.codex/skills && ln -s ~/ai/skills ~/.codex/skills
```

Note: Codex ships a `.system/` folder inside `~/.codex/skills/` with built-in skills. If you whole-dir-symlink, you'll lose those. Prefer per-skill symlinks for Codex unless you don't care about the built-ins.

### 4. Wire up opencode

opencode's search path already includes `~/.claude/skills/` and `~/.agents/skills/` globally, so if Claude is wired up, opencode works with zero extra config.

If you want it explicit (so it works even if `~/.claude/skills/` disappears):

```bash
mkdir -p ~/.config/opencode
ln -s ~/ai/skills ~/.config/opencode/skills
```

### 5. Wire up Cursor

Cursor looks in `~/.cursor/skills-cursor/<name>/SKILL.md`.

```bash
ln -s ~/ai/skills/grill-me ~/.cursor/skills-cursor/grill-me
```

Caveat: Cursor's built-in skills (`canvas`, `create-rule`, `statusline`, etc.) live in this same dir and are managed by Cursor itself (see `.cursor-managed-skills-manifest.json`). Use per-skill symlinks only — never whole-directory — or you'll clobber Cursor-managed skills.

### 6. Share the global rules file (AGENTS.md / CLAUDE.md)

Write your global guidance once at `~/ai/AGENTS.md`, then symlink:

```bash
ln -sf ~/ai/AGENTS.md ~/.codex/AGENTS.md
ln -sf ~/ai/AGENTS.md ~/.claude/CLAUDE.md
ln -sf ~/ai/AGENTS.md ~/.config/opencode/AGENTS.md
```

Cursor's equivalent is project-scoped (`AGENTS.md` or `.cursor/rules/*.mdc` at the repo root). For global Cursor rules, edit Settings → Rules for AI in the UI — it doesn't pull from a dotfile. Workaround: paste the contents of `~/ai/AGENTS.md` into that box and re-sync manually when it changes.

______________________________________________________________________

## Verification

After wiring, confirm each provider resolves to the same inode:

```bash
for p in ~/.claude/skills/grill-me \
         ~/.codex/skills/grill-me \
         ~/.cursor/skills-cursor/grill-me \
         ~/ai/skills/grill-me; do
  echo "$p -> $(readlink -f $p)"
done
```

All four should point to the same real path under `~/ai/skills/grill-me`.

Then open each tool and ask it to list its skills — `grill-me` (and every other shared skill) should appear in all of them.

______________________________________________________________________

## Gotchas

- Permissions. On this machine, `~/.claude` and `~/.codex` are root-owned. Either `chown -R $USER` those dirs first, or create the symlinks with `sudo`.
- Absolute paths in symlinks. Use `ln -s /home/jacob/ai/skills/...` (or `~` which expands to the same) rather than relative paths. Relative symlinks break when providers resolve from a different cwd.
- Per-skill vs whole-dir. Whole-dir symlinks are tempting but destroy provider-managed skills (Cursor's manifest, Codex's `.system/`). Per-skill symlinks are slightly more work but safe.
- File vs directory symlinks. A SKILL is a *directory* (may contain supporting files besides `SKILL.md`). Always symlink at the directory level, not just `SKILL.md`.
- Frontmatter compatibility. All four providers accept the same minimal `SKILL.md` frontmatter (`name`, `description`). Keep skills generic and don't use provider-specific fields, or you'll break portability.

______________________________________________________________________

## Adding a New Skill (the steady state)

```bash
mkdir ~/ai/skills/my-new-skill
$EDITOR ~/ai/skills/my-new-skill/SKILL.md

ln -s ~/ai/skills/my-new-skill ~/.claude/skills/my-new-skill
ln -s ~/ai/skills/my-new-skill ~/.codex/skills/my-new-skill
ln -s ~/ai/skills/my-new-skill ~/.cursor/skills-cursor/my-new-skill
# opencode: nothing to do, picks it up via ~/.claude/skills
```

A small shell function (`add-skill <name>`) can automate the three `ln -s` calls if it becomes routine.
