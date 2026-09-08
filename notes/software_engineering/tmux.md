# tmux

tmux (terminal multiplexer) is a program that lets you run multiple terminal sessions inside a single terminal window, and more importantly, lets those sessions persist independently of the terminal that created them.

### What it does

At its core, tmux sits between your shell and your terminal emulator. When you start a tmux session, it creates a server process that manages one or more virtual terminals. Your terminal emulator connects to that server as a "client." The key insight is that the server keeps running even if the client disconnects, which means your shell sessions survive if your terminal closes, your SSH connection drops, or you deliberately detach.

### How it's structured

tmux organizes things in a three-level hierarchy:

- **Sessions** are the top-level container. Each session is an independent workspace that can hold multiple windows. You might have one session for work and another for a personal project.
- **Windows** live inside a session and behave like tabs. Each window runs its own shell (or whatever program you launch in it). You switch between them with keyboard shortcuts.
- **Panes** split a single window into multiple visible regions. You can split horizontally or vertically, so you get side-by-side or stacked terminals within one window.

### How it works under the hood

When you run `tmux`, it spawns a server process (if one isn't already running) and creates a new session. Your terminal attaches to that session as a client. All interaction goes through a prefix key (default `Ctrl-b`), followed by a command key. For example, `Ctrl-b c` creates a new window, `Ctrl-b %` splits a pane vertically, `Ctrl-b d` detaches the client.

The server owns the pseudo-terminals (ptys) that your shells run in. Because the server is a separate long-lived process, detaching just disconnects your view. Reattaching with `tmux attach` hooks you right back in, with all output history and running processes intact.

Configuration lives in `~/.tmux.conf`, where you can rebind keys, set status bar appearance, change default behaviors, etc.

### Use cases

**Remote work over SSH.** This is the classic use case. You SSH into a server, start a tmux session, kick off a long-running job, detach, close your laptop, and reattach later. The job keeps running because the tmux server on the remote machine never stopped.

**Pair programming / shared sessions.** Two people can attach to the same tmux session simultaneously and see the same terminal in real time. Useful for remote debugging or teaching.

**Persistent dev environments.** You set up a session with windows for your editor, a build watcher, a log tail, a database shell, etc. Detach at the end of the day, reattach the next morning, and everything is exactly where you left it.

**Scripting reproducible layouts.** You can script tmux to create sessions with specific window/pane arrangements programmatically. Tools like tmuxinator or tmux-resurrect build on this to let you define and restore complex workspace layouts from config files.

**Running multiple things visually.** Even locally, panes let you watch logs, run tests, and edit code all in one terminal window without alt-tabbing between multiple terminal instances.

Since you're on Arch with a Wayland compositor, tmux pairs well with a minimal setup where you might not want a heavy tabbed terminal emulator handling multiplexing for you. It also means your session state isn't tied to any particular terminal app.

## Commands

```sh
tmux new -s work              # start a named session
tmux attach -t work           # reattach to it later
Ctrl-b d                      # detach (leave session running in background)
Ctrl-b c / Ctrl-b 0-9         # create a new window / switch between them
Ctrl-b % / Ctrl-b "           # split panes vertically / horizontally
```
