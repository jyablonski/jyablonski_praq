# Headroom Proxy Setup

Headroom is a context optimization layer that sits between Claude Code and the Anthropic API. It reduces token usage via smart compression of tool outputs, prefix stabilization for prompt cache hits, and rolling context window management.

Repo: https://github.com/chopratejas/headroom/tree/main

## Installation

Installed via uv tool:

```bash
uv tool install "headroom-ai[all]"
# binary lands at ~/.local/bin/headroom
```

## Systemd User Service

Service file at `~/.config/systemd/user/headroom.service`:

```ini
[Unit]
Description=Headroom LLM Proxy
After=network.target

[Service]
ExecStart=%h/.local/bin/headroom proxy --port 8787
Restart=on-failure
RestartSec=5
Environment=PATH=%h/.local/bin:/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=default.target
```

Enabled with:

```bash
systemctl --user daemon-reload
systemctl --user enable headroom
systemctl --user start headroom
sudo loginctl enable-linger jacob  # start on boot without login
```

## Shell Config

Added to `~/.bashrc` / `~/.zshrc`:

```bash
export ANTHROPIC_BASE_URL=http://localhost:8787
```

This transparently routes Claude Code through the proxy with no other changes.

## Monitoring

Health check:

```bash
curl http://localhost:8787/health
```

Token savings stats:

```bash
curl http://localhost:8787/stats | python -m json.tool
```

Prometheus metrics (if scraping):

```bash
curl http://localhost:8787/metrics
```

Live logs:

```bash
journalctl --user -u headroom -f
```

Service status:

```bash
systemctl --user status headroom
```

## Upgrading

```bash
uv tool upgrade headroom-ai
systemctl --user restart headroom
```

## Disabling / Removing

Stop and disable the service:

```bash
systemctl --user stop headroom
systemctl --user disable headroom
```

Remove the service file:

```bash
rm ~/.config/systemd/user/headroom.service
systemctl --user daemon-reload
```

Remove the env var from `~/.bashrc` / `~/.zshrc`:

```bash
# delete or comment out:
# export ANTHROPIC_BASE_URL=http://localhost:8787
```

Uninstall the package:

```bash
uv tool uninstall headroom-ai
```

Optionally revoke lingering if no other user services need it:

```bash
sudo loginctl disable-linger jacob
```
