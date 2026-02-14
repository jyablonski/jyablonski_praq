# LLM Agent Configuration Files, Patterns, and Techniques

A comprehensive reference of every known mechanism for providing context, instructions, and capabilities to LLM-powered coding tools and agents as of early 2026.

______________________________________________________________________

## 1. The Emerging Universal Standard: AGENTS.md

AGENTS.md is the closest thing the ecosystem has to a cross-tool standard. It sits in your project root (or nested in subdirectories for monorepos) and provides project context to any AI agent that reads it.

Who supports it: Cursor (v1.6+), OpenAI Codex CLI, GitHub Copilot (VS Code), OpenCode, Gemini CLI, Firebender, Builder.io, and others. Claude Code does not natively read AGENTS.md but can be pointed to it via `CLAUDE.md`.

What goes in it:

- Project architecture overview
- Tech stack and dependencies
- Coding standards and conventions
- File organization patterns
- Build/test/deploy commands
- Domain-specific knowledge

Directory-level scoping: Most tools support nested `AGENTS.md` files in subdirectories, so monorepo modules can carry their own context that only activates when the agent works in that directory.

The workaround for Claude Code:

```
echo 'See @AGENTS.md' > CLAUDE.md
```

Or use a symlink: `ln -s AGENTS.md CLAUDE.md`

______________________________________________________________________

## 2. Tool-Specific Configuration Files

### Claude Code

Claude Code has the richest configuration surface of any tool. Its full directory structure:

```
project-root/
├── CLAUDE.md                    # Project memory, loaded at session start
├── .mcp.json                    # MCP server configuration
├── .claude/
│   ├── settings.json            # Hooks, env vars, permissions
│   ├── settings.local.json      # Personal overrides (gitignored)
│   ├── rules/                   # Path-specific rules (glob matching)
│   │   ├── security.md
│   │   ├── coding-style.md
│   │   └── testing.md
│   ├── agents/                  # Custom subagents
│   │   ├── code-reviewer.md
│   │   ├── planner.md
│   │   └── architect.md
│   ├── commands/                # Slash commands (/command-name)
│   │   ├── tdd.md
│   │   ├── pr-review.md
│   │   └── onboard.md
│   └── skills/                  # Workflow definitions with SKILL.md
│       └── my-skill/
│           └── SKILL.md
```

Global (user-level) equivalents: `~/.claude/CLAUDE.md`, `~/.claude/commands/`, `~/.claude/skills/`, `~/.claude/rules/`

Unique to Claude Code:

| Concept | What it does |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CLAUDE.md | Persistent project memory loaded every session. The root context file. |
| Skills | Self-contained instruction bundles with frontmatter metadata (name, description, allowed-tools). Discovered automatically or on demand. Support subagent execution, argument passing, and dynamic context injection. |
| Slash Commands | Markdown files that define reusable prompts triggered via `/command-name`. Can include bash execution (`!git status`) and file references. Support argument hints. |
| Agents (Subagents) | Specialized Claude instances with isolated context windows. Defined with frontmatter (name, description, model, color). Used for delegation to prevent context bloat. |
| Hooks | Deterministic shell commands triggered by lifecycle events (PreToolUse, PostToolUse, etc.). Can block actions, provide feedback, auto-format code, run linters. Configured in `settings.json`. |
| Rules | Always-follow guidelines with glob-based path matching. Similar to Cursor rules but without the typed scoping (Always/Auto Attached/etc). |
| Plugins | Distributable bundles of commands, agents, hooks, skills, and metadata. Installable from marketplaces. |

Skill frontmatter example:

```yaml
---
name: code-reviewer
description: Review code for best practices. Use when reviewing code or PRs.
allowed-tools: Read, Grep, Glob
---
```

### Cursor

```
project-root/
├── .cursorrules              # Legacy single-file rules (deprecated)
├── .cursor/
│   ├── rules/                # Modern rules directory
│   │   ├── frontend.mdc     # .mdc format with frontmatter
│   │   ├── backend.mdc
│   │   └── testing.mdc
│   └── mcp.json              # MCP server configuration
```

Rule types (unique to Cursor):

| Type | Behavior |
| --------------- | ----------------------------------------------------------------------------------------- |
| Always | Included in every request. Use sparingly (burns context tokens). |
| Auto Attached | Triggers when files matching a glob pattern are referenced. Recommended for 80% of rules. |
| Agent Requested | The AI decides whether to include based on task relevance. Requires a good description. |
| Manual | Only activated when explicitly referenced via `@ruleName`. |

Rule frontmatter (.mdc format):

```yaml
---
description: Django best practices for models, views, templates
globs: ["*.py"]
alwaysApply: false
---
```

Cursor also supports User Rules (personal preferences across all projects) configured in `File > Preferences > Cursor Settings > Rules`.

The `/rules` CLI command (added January 2026) lets you create and edit rule files directly from the terminal.

### GitHub Copilot

```
project-root/
├── .github/
│   ├── copilot-instructions.md    # Repository-wide instructions
│   ├── instructions/              # Directory for path-specific instructions
│   │   └── *.instructions.md      # Glob-matched instruction files
│   └── agents/                    # Custom agents for coding agent
│       └── technical-doc-writer.agent.md
```

Key details:

- `copilot-instructions.md` applies to all chat requests within the repo
- `*.instructions.md` files support path-specific scoping
- Custom agents (`.agent.md`) are referenced in workflow frontmatter
- VS Code also reads `AGENTS.md` from project root
- The `/init` command can auto-generate instructions by analyzing your project
- Organization-level instructions can be shared across repos
- Hooks triggered by session events (sessionStart, sessionEnd, userPromptSubmitted)

### OpenAI Codex CLI

```
~/.codex/
├── config.toml                  # Profiles, model providers, approval policy
├── instructions.md              # Global instructions (or AGENTS.md)
├── prompts/                     # Custom prompts accessible via /prompts:
│   └── deep-reflector.md
└── skills/                      # Skill bundles
    └── my-skill/
        └── SKILL.md
```

Configuration layers:

1. System instructions (`experimental_instructions_file`) -- overrides default prompt
1. Developer instructions (`--config developer_instructions`) -- conversation messages with "developer" role
1. AGENTS.md -- project-level context, injected as user-role message
1. Custom prompts -- reusable templates in `~/.codex/prompts/`
1. Skills -- stored in `~/.codex/skills//SKILL.md`

Codex supports multiple model providers via `config.toml` profiles (OpenAI direct, GitHub Copilot proxy, Azure OpenAI, OpenRouter).

### Google Gemini CLI

```
~/.gemini/
├── settings.json              # Context file configuration
│   # e.g., {"context":{"fileName":["AGENTS.md"]}}
└── GEMINI.md                  # Global instructions
```

Gemini CLI reads `AGENTS.md` natively. MCP support is available. Context is configured through `settings.json`.

______________________________________________________________________

## 3. Cross-Tool Patterns and Standards

### Model Context Protocol (MCP)

MCP is the closest thing to a universal standard for extending LLM tool capabilities. It standardizes how AI tools connect to external services (databases, APIs, GitHub, Jira, Slack, etc.).

Supported by: Claude Code, Cursor, VS Code Copilot, Windsurf, Cline/Roo Code, Gemini CLI, OpenCode, JetBrains IDEs

Configuration file: `.mcp.json` (project root) or tool-specific locations

Transport types: stdio, SSE, HTTP

Growth: From 100k downloads in Nov 2024 to 8M+ by April 2025. Over 300 integrations exist.

What MCP servers provide:

- Tools (functions the agent can call)
- Resources (data the agent can read)
- Prompts (reusable prompt templates exposed as slash commands)

### llms.txt / llms-full.txt

A proposed web standard for making website content LLM-friendly. Not a coding tool config, but relevant for providing documentation context to agents.

- llms.txt -- concise markdown file at site root with key links and descriptions
- llms-full.txt -- expanded version with full documentation content

Adoption: ~844k websites (BuiltWith, Oct 2025), including Anthropic, Cloudflare, Stripe, Vercel. However, no major AI platform has confirmed they read these files during inference. Primary practical use is for developer documentation consumed by coding agents via MCP or direct fetch.

### .aiignore / .codeiumignore

Files to exclude from AI processing. Follows `.gitignore` syntax. Supported by Junie (`.aiignore`), Windsurf (`.codeiumignore`), and increasingly others.

______________________________________________________________________

## 4. Architectural Patterns for Agent Systems

These are design patterns that apply regardless of which specific tool you use:

### ReAct (Reasoning + Acting)

The most fundamental agent pattern. The LLM alternates between reasoning about what to do and taking actions, observing results after each step. Used internally by most coding agents.

### Plan-then-Execute

The LLM creates a complete plan first, then a separate executor carries it out step by step. Trades flexibility for predictability and reduced API costs. The planning phase is front-loaded.

### Multi-Agent / Subagent Delegation

Spawn specialized agents with isolated contexts for focused work. Prevents context bloat in the main conversation. Results return as summaries.

Three-layer model (Claude Code):

1. Core Layer -- main conversation, shared 200k token window
1. Delegation Layer -- subagents with clean contexts (up to 10 parallel)
1. Extension Layer -- MCP, hooks, skills, plugins

### Sequential Pipeline

Agents organized in a linear sequence. Each agent's output becomes the next agent's input. Good for well-defined workflows (research > draft > edit > publish).

### Map-Reduce

Multiple sub-agents process items in parallel (map), then results are aggregated (reduce). Used for tasks like processing multiple files or reviewing multiple PRs.

### Dual LLM (Security Pattern)

A privileged LLM coordinates a quarantined LLM. The quarantined LLM handles untrusted content and returns symbolic variables. The privileged LLM never sees raw untrusted content. Designed to mitigate prompt injection.

### Progressive Summarization (Memory)

Maintain a condensed summary of conversation history. As new interactions occur, update the summary and discard less relevant details. Keeps earlier context alive within token limits.

______________________________________________________________________

## 5. Practical Sync Strategy

Since fragmentation is the core problem, here's the recommended approach for multi-tool teams:

```
project-root/
├── AGENTS.md                  # Single source of truth
├── CLAUDE.md                  # Symlink or "See @AGENTS.md"
├── .cursorrules               # Symlink to AGENTS.md (legacy support)
├── .cursor/rules/             # Tool-specific scoped rules (if needed)
├── .github/
│   └── copilot-instructions.md
├── .mcp.json                  # Shared MCP config
├── .agents/                   # Optional shared assets
│   ├── skills/                # Skill definitions
│   ├── plans/                 # Technical execution plans
│   └── rules/                 # Modular rule files
```

Global (user-level):

```bash
mkdir -p ~/.agents
# Write master instructions in ~/.agents/AGENTS.md

# Claude Code
ln -sfn ~/.agents/AGENTS.md ~/.claude/CLAUDE.md

# Codex
ln -sfn ~/.agents/AGENTS.md ~/.codex/AGENTS.md

# Gemini CLI
echo '{"context":{"fileName":["AGENTS.md"]}}' > ~/.gemini/settings.json

# Firebender
ln -sfn ~/.agents/AGENTS.md ~/.firebender/AGENTS.md
```

______________________________________________________________________

## 6. Quick Reference Matrix

| Feature | Claude Code | Cursor | Copilot | Codex CLI | Windsurf | Cline/Roo | Gemini CLI |
| ------------------ | ----------------------- | ------------------- | ----------------------- | ----------------- | -------------- | ----------- | ----------------- |
| AGENTS.md | Via CLAUDE.md | Native | Native | Native | Via rules | Partial | Native |
| Custom rules file | CLAUDE.md | .cursor/rules/\*.mdc | copilot-instructions.md | AGENTS.md | .windsurfrules | .clinerules | GEMINI.md |
| Path-scoped rules | .claude/rules/ | Glob frontmatter | \*.instructions.md | -- | -- | -- | -- |
| Rule type scoping | No | Yes (4 types) | Always-on + path | No | No | No | No |
| Skills | Yes (SKILL.md) | No | Yes (folders) | Yes (SKILL.md) | No | No | No |
| Slash commands | Yes (.claude/commands/) | No | Yes (prompt files) | Yes (/prompts:) | No | No | No |
| Custom subagents | Yes (.claude/agents/) | No | Yes (.agent.md) | No | No | Modes | No |
| Hooks | Yes (settings.json) | Yes (v1.7+) | Yes (events) | No | No | No | No |
| MCP | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Plugins | Yes | Extensions | Extensions | No | Extensions | Extensions | No |
| Nested dir configs | CLAUDE.md per dir | AGENTS.md per dir | \*.instructions.md | AGENTS.md per dir | No | No | AGENTS.md per dir |
| Auto-generate | /init | -- | /init | /init | -- | -- | -- |

______________________________________________________________________

## Summary

The landscape is converging but not yet unified. AGENTS.md is the closest to a universal standard for project context, and MCP is the universal standard for tool integration. Beyond those two, every tool has its own configuration surface with varying levels of sophistication.

Claude Code currently has the deepest feature set (skills, agents, commands, hooks, plugins, rules), followed by Cursor (typed rule scoping, hooks) and GitHub Copilot (custom agents, instruction files, hooks). The practical move is to keep AGENTS.md as your single source of truth and use symlinks or pointer files for tool-specific paths.
