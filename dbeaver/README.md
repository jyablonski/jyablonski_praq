# DBeaver Preferences

Personal DBeaver settings exported for cross-device consistency. Tested on DBeaver 26.x.

## What's customized

**Editor behavior**

- Blank line is statement delimiter: **Never** (so multi-CTE queries execute fully on Ctrl+Enter)
- Statement delimiter: `;`
- Auto-activation on typing: **disabled** (autocomplete still works on `.` and Ctrl+Space)
- Auto activation delay: `300ms`

**Appearance**

- Theme: Dark
- Font: JetBrains Mono Medium, 15pt (Text Font + SQL Editor Text Font)
- Line numbers enabled
- Current line highlight enabled
- Custom syntax colors approximating VSCode Dark+

**Toolbars (trimmed)**

- SQL Editor top toolbar: only Execute SQL query + Execute SQL script
- SQL Editor bottom toolbar: disabled
- Result set bottom toolbar: kept Apply/Reject/Refresh/Export/Fetch All

## Exporting from DBeaver

1. `File → Export…`
1. Expand **General → Preferences**
1. Choose **Export all** (or pick specific categories)
1. Save to a folder — DBeaver writes per-plugin `.prefs` files

Then copy the resulting files into this directory:

## Importing on a new device

1. Install DBeaver (matching major version recommended)
1. `File → Import…`
1. Expand **General → Preferences**
1. Browse to this directory and select the `.prefs` files (or parent folder)
1. Restart DBeaver

## What's NOT included

- **Database connections** — export separately via `File → Export → DBeaver → Project` (contains credentials, do not commit publicly)
- **JDBC drivers** — re-download on first connection
- **Workspace layout** — panel positions reset to defaults
- **Saved scripts** — live in `~/.local/share/DBeaverData/workspace*/General/Scripts/`

## Notes

- `.prefs` files are plain Java properties text — diffable, greppable, safe to commit
- Preferences are loosely tied to DBeaver versions; expect minor cleanup after major upgrades
- Caret may appear invisible on some Linux/Wayland setups (known SWT/GTK quirk, not a settings issue)
