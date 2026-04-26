#!/usr/bin/env bash

# script which symlinks cursor's config files to the corresponding vscode ones, so that changes in vscode are 
# reflected in cursor. 
# vscode is the source of truth, so changes in cursor will not be reflected in vscode.
set -euo pipefail
DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
fi
echo "== Cursor <- VS Code settings linker =="
$DRY_RUN && echo "[DRY RUN] No files will be changed."
CURSOR_USER_DIR="${HOME}/.config/Cursor/User"
VSCODE_USER_DIR=""
run_cmd() {
  if $DRY_RUN; then
    echo "[DRY RUN] $*"
  else
    "$@"
  fi
}
# Detect VS Code user dir
if [[ -d "${HOME}/.config/Code/User" ]]; then
  VSCODE_USER_DIR="${HOME}/.config/Code/User"
elif [[ -d "${HOME}/.config/Code - Insiders/User" ]]; then
  VSCODE_USER_DIR="${HOME}/.config/Code - Insiders/User"
else
  echo "ERROR: Could not find VS Code user config directory."
  echo "Expected one of:"
  echo "  ~/.config/Code/User"
  echo "  ~/.config/Code - Insiders/User"
  exit 1
fi
echo "Using VS Code user dir: ${VSCODE_USER_DIR}"
echo "Using Cursor user dir:  ${CURSOR_USER_DIR}"
run_cmd mkdir -p "${CURSOR_USER_DIR}"
# Ensure source files/folders exist
run_cmd touch "${VSCODE_USER_DIR}/settings.json"
run_cmd touch "${VSCODE_USER_DIR}/keybindings.json"
run_cmd mkdir -p "${VSCODE_USER_DIR}/snippets"
# Backup current Cursor config (normal run only)
BACKUP_DIR="${HOME}/.config/Cursor/User.backup.$(date +%Y%m%d-%H%M%S)"
if $DRY_RUN; then
  echo "[DRY RUN] Would create backup dir: ${BACKUP_DIR}"
  for item in settings.json keybindings.json snippets; do
    if [[ -e "${CURSOR_USER_DIR}/${item}" || -L "${CURSOR_USER_DIR}/${item}" ]]; then
      echo "[DRY RUN] Would backup: ${CURSOR_USER_DIR}/${item} -> ${BACKUP_DIR}/"
    else
      echo "[DRY RUN] No existing ${CURSOR_USER_DIR}/${item} to back up"
    fi
  done
else
  mkdir -p "${BACKUP_DIR}"
  for item in settings.json keybindings.json snippets; do
    if [[ -e "${CURSOR_USER_DIR}/${item}" || -L "${CURSOR_USER_DIR}/${item}" ]]; then
      cp -a "${CURSOR_USER_DIR}/${item}" "${BACKUP_DIR}/" 2>/dev/null || true
    fi
  done
  echo "Backup saved to: ${BACKUP_DIR}"
fi
# Replace with symlinks
run_cmd rm -f "${CURSOR_USER_DIR}/settings.json"
run_cmd ln -s "${VSCODE_USER_DIR}/settings.json" "${CURSOR_USER_DIR}/settings.json"
run_cmd rm -f "${CURSOR_USER_DIR}/keybindings.json"
run_cmd ln -s "${VSCODE_USER_DIR}/keybindings.json" "${CURSOR_USER_DIR}/keybindings.json"
run_cmd rm -rf "${CURSOR_USER_DIR}/snippets"
run_cmd ln -s "${VSCODE_USER_DIR}/snippets" "${CURSOR_USER_DIR}/snippets"
echo
if $DRY_RUN; then
  echo "[DRY RUN] Would verify symlinks with:"
  echo "ls -l \"${CURSOR_USER_DIR}/settings.json\" \"${CURSOR_USER_DIR}/keybindings.json\" \"${CURSOR_USER_DIR}/snippets\""
else
  echo "Symlinks created. Verifying:"
  ls -l "${CURSOR_USER_DIR}/settings.json" "${CURSOR_USER_DIR}/keybindings.json" "${CURSOR_USER_DIR}/snippets"
fi
echo
$DRY_RUN && echo "[DRY RUN] Complete. No changes made."
! $DRY_RUN && echo "Done. Restart Cursor (and VS Code) to ensure both pick up changes."