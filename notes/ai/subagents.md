# Subagents: Context Isolation, Delegation, and Parallel Work

## What a subagent is

A subagent is an agent execution that another agent delegates work to. It usually has its own model context, instructions, tool loop, and lifecycle. The parent agent gives it a bounded task, the subagent works independently, and some result crosses back to the parent for synthesis or further action.

The underlying model/tool cycle is the same one described in [The Agent Tool-Use Loop](./agent_tool_loops.md). A subagent system adds orchestration around multiple such loops.

The stable mental model is:

```text
user request
    ↓
parent / orchestrator
    ├── delegation → subagent A → result A ──┐
    ├── delegation → subagent B → result B ──┼→ parent synthesis → final answer
    └── delegation → subagent C → result C ──┘
```

The result may be a summary, structured data, a patch, a file, or a reference to a durable artifact. Some products also expose the subagent transcript for inspection or let the parent send follow-up instructions. The important property is the explicit information boundary between the parent and worker, not a particular UI or tool name.

A subagent is not necessarily:

- A different model. Parent and child may use the same model or route to models with different cost and capability profiles.
- A separate user session. A product may keep several agent threads inside one session.
- A separate process, container, checkout, or security principal. Context isolation does not imply runtime isolation.
- A universal model-provider primitive. A harness or SDK can implement delegation with ordinary model and tool calls, although some providers now offer hosted multi-agent orchestration directly.

The concise definition is **a delegated agent loop with an explicit context boundary**.

## Who or what requests a subagent?

The short answer is: several layers can request delegation, but the **harness or orchestration runtime** is the component that actually creates and runs the subagent. It helps to separate declaration, routing, and execution:

```text
human prompt / project instruction / skill / application policy
                            ↓
             requests or constrains delegation
                            ↓
             parent LLM or deterministic controller
                            ↓
                  spawn / task / handoff call
                            ↓
                    harness or agent runtime
                            ↓
          new context + tools + permissions + lifecycle
```

The possible requesters are:

- **Human user:** The user can ask in natural language for parallel workers, name roles, or use product syntax such as an agent `@`-mention. Whether natural language is a requirement or only a hint depends on the harness. Some products make an explicit mention deterministic; others still route the request through the parent model.
- **Parent LLM:** When the harness exposes delegation as a tool, the parent model can decide that a task is worth splitting and emit a spawn or task call. The model proposes the decomposition; it does not create a process or context by itself.
- **System, developer, or project instructions:** A system prompt, `AGENTS.md`, `CLAUDE.md`, or similar file can require, encourage, or prohibit delegation. These instructions change the parent agent's routing policy but normally do not execute anything directly.
- **Skill or command:** A skill is a reusable workflow, not inherently a subagent. It may run in the parent context, tell the parent to delegate, be preloaded into a subagent, or use a harness-specific option to run in an isolated or forked context. The skill's effect therefore depends on both its contents and the host's skill semantics.
- **Agent definition:** A file such as `.claude/agents/reviewer.md`, `.gemini/agents/reviewer.md`, or a Codex agent TOML file registers a possible worker and describes when and how to use it. The definition usually does not trigger itself; its description becomes routing input for the parent model or harness.
- **Harness or application code:** A coding harness may automatically route matching tasks to built-in agents, while an SDK application can start a worker from a fixed graph, rule, event, or ordinary function call. This is the most deterministic option because code, rather than model judgment, chooses the topology.

There can therefore be a chain of requesters rather than one requester. For example, a user invokes a review skill; the skill instructs the parent to use three reviewers; the parent emits three delegation tool calls; and the harness validates permissions and concurrency before creating the workers. Saying “the skill spawned three agents” is convenient shorthand, but the runtime performed the spawn.

### Requested, selected, and spawned are different events

Use these terms precisely when debugging an orchestration system:

- **Requested:** A human, instruction, skill, model, or controller asks for delegation.
- **Selected:** The router chooses a particular agent definition, model, and execution mode.
- **Scheduled:** The selected work is admitted immediately or queued behind concurrency, rate, budget, or approval limits.
- **Spawned:** The runtime allocates a child context and begins its lifecycle.

A failed delegation may occur at any boundary: the model ignores an advisory request, no agent description matches, policy hides the delegation tool, the runtime rejects the spawn, or the worker waits indefinitely for a slot or approval.

## Behavior across providers and platforms

Subagent behavior is primarily a property of the **harness**, not the model brand. “Does Claude support subagents?” is underspecified: Claude in Claude Code, Claude through OpenCode, and Claude called from a custom application can have different delegation tools, context rules, and permissions. Conversely, a multi-provider harness can provide roughly the same orchestration behavior while swapping the underlying model.

The model still matters for decomposition quality, tool use, context capacity, latency, and cost. It just does not define the runtime boundary. As of `2026-08-11`, representative systems differ as follows:

| Platform or runtime | How delegation starts | Context and configuration | Runtime behavior |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| OpenAI Responses API Multi-agent | Application code enables Multi-agent; the root model can then use hosted spawn, message, follow-up, wait, interrupt, and list actions. Developer instructions can require explicit user requests or allow proactive routing. | Each worker has a focused context; `fork_turns` controls how much parent history is copied. Workers share the request's model and available tools. | OpenAI hosts the agent tree and coordination actions. Nested delegation is supported, the root synthesizes the answer, and the default recommended concurrency limit is three subagents. |
| ChatGPT Work and Codex | A user can ask directly. Current local Codex clients can also delegate when `AGENTS.md` or a skill requires it; eligible ChatGPT Ultra runs may delegate proactively. | Codex exposes separate agent threads and supports built-in or custom TOML agents with per-agent model, reasoning, sandbox, MCP, and skill settings. | The main thread collects results. App, CLI, and IDE surfaces differ, but allow some combination of inspecting, steering, stopping, or switching threads. Parent permission and sandbox choices constrain children. |
| Claude Code | Claude may route automatically from the request, agent description, and context. Natural-language naming is advisory; an agent `@`-mention guarantees a particular worker. Skills can preload into workers or use `context: fork`. | Named agents normally start fresh with their own prompt and task message plus selected injected state such as `CLAUDE.md`; a fork inherits the parent conversation. Agent Markdown controls model, tools, permissions, skills, memory, background mode, and optional worktree isolation. | Foreground and background execution are supported, with background now the usual default. Workers can be resumed and can delegate recursively up to a configurable depth. Transcripts remain separate from the main conversation. |
| OpenCode | A primary agent invokes a subagent automatically from its description or the user invokes one with `@name`. The model uses the Task tool for programmatic delegation. | Agents are defined in `opencode.json` or Markdown and can select any configured provider/model, prompt, mode, and permissions. Each invocation creates a navigable child session. | `permission.task` controls which workers the model can see or call; direct user `@` invocation remains available. Parent and child sessions can be navigated explicitly in the terminal UI. |
| Gemini CLI | The main model can automatically call a matching agent tool. A leading `@agent_name` adds a strong routing instruction for that worker. | Each agent has an independent context loop and its own prompt. Project or user Markdown definitions can select model, tools, MCP servers, turn limit, and timeout. | Local subagents cannot invoke other subagents. The policy engine can govern agents as virtual tools, and remote workers can be connected through A2A. |
| GitHub Copilot CLI | The main agent automatically chooses many built-in or custom agents from the prompt and context; some specialists, such as Research, require an explicit slash command. | Agent-profile Markdown defines prompts, tools, and optional MCP servers. Workers use separate context windows. | The main agent can run suitable workers in parallel. Built-ins intentionally differ in write access and tool scope, such as read-only exploration versus command execution. |

These are product snapshots, not portable guarantees. In particular, check the following before designing a workflow around any platform:

- **Trigger semantics:** advisory natural language, guaranteed mention or command, model-selected tool call, or deterministic application code.
- **Startup context:** fresh prompt, summarized handoff, selected project instructions, full transcript fork, or a product-specific mixture.
- **Model routing:** inherited model, per-agent override, model chosen at spawn time, or a provider-wide fixed model.
- **Tools and permissions:** inherited, filtered, independently configured, or approved through the parent UI.
- **Resource isolation:** shared files and checkout, a worktree, a container, a hosted environment, or a remote agent service.
- **Coordination topology:** one level only, nested trees, peer messaging, resumable workers, handoffs, or a fixed application graph.
- **Lifecycle and observability:** foreground versus background, concurrency and depth limits, cancellation, transcript visibility, retries, and result delivery.
- **Accounting:** whether child tokens, tool calls, rate limits, and budgets are reported separately or rolled into the parent run.

## The core mechanism: isolate, compress, synthesize

A fresh subagent commonly starts with:

- Its own system or developer instructions.
- A delegation message describing the task.
- A selected set of tools and permissions.
- Some environment and project instructions supplied by the harness.
- No parent transcript unless the runtime explicitly forks or forwards it.

It then performs its own sequence of model calls and tool calls. When it finishes, the harness returns its output to the parent. Large search results, test logs, and file contents can remain in the child context while the parent receives only the useful conclusions.

This makes subagents a form of **context isolation plus compression**. That has two consequences:

1. The parent stays focused on the user's requirements, decisions, and final deliverable.
1. The boundary is lossy unless the worker returns evidence or saves a durable artifact.

Compression is both the feature and the main failure mode. A beautifully concise summary is still defective if it drops the one file reference, caveat, failed test, or source the parent needs. Good delegation therefore specifies what evidence must survive the boundary.

### Fresh context versus forked context

There are two common startup models:

- **Fresh worker:** The child gets a new context containing its instructions and the parent's delegation message. This maximizes context isolation but makes the delegation message load-bearing.
- **Forked worker:** The child inherits some or all of the parent's conversation state and continues from there. This reduces briefing work but copies more irrelevant context and weakens the context-hygiene benefit.

Do not assume which behavior a product uses. Also do not assume that a child which starts fresh receives nothing else: harnesses may inject repository instructions, environment details, tool schemas, memory, or a git-status snapshot.

## Context isolation is not resource isolation

Several independent boundaries are often conflated:

| Boundary | What it isolates | Typical subagent behavior |
| --------------------- | ---------------------------------------------------------------- | ----------------------------------------------------------- |
| Model context | Messages, reasoning state, and tool results visible to the model | Usually separate, unless forked or explicitly forwarded |
| Filesystem | Files and uncommitted changes | Often shared |
| Git checkout | Branch, index, and working tree | Shared unless a worktree or clone is created |
| Process and network | Runtime, network routes, and environment variables | Product-specific |
| Tools and credentials | Actions and external systems the agent can reach | Often inherited, restricted, or explicitly configured |
| Memory | State retained across turns or sessions | Product-specific and not implied by a separate context |
| Budget | Token, turn, time, and concurrency limits | The child consumes its own work but may share global limits |

A worktree and a subagent solve different problems:

- **Subagent:** isolates context and reasoning state.
- **Worktree:** isolates a checkout so parallel writers do not edit the same working tree.
- **Sandbox or container:** isolates runtime capabilities and possibly the filesystem or network.
- **Permission policy:** limits which actions are authorized.

These mechanisms compose. For example, three read-only reviewers can safely share one checkout, while three implementation workers usually need disjoint file ownership or separate worktrees. Separate context windows alone do nothing to prevent conflicting writes.

## Common orchestration patterns

### Manager with agents as tools

The parent owns the user interaction and final answer. Specialists behave like bounded tools: they receive a task and return a result to the manager.

Use this when one agent must reconcile findings, enforce a common output format, or retain responsibility for the final decision. This is the pattern most people mean by "subagents."

### Parallel fan-out and fan-in

The parent divides work into independent lanes, runs workers concurrently, waits for them, and synthesizes their results.

Good examples include:

- Reviewing one change separately for correctness, security, performance, and test gaps.
- Researching independent companies, regions, sources, or hypotheses.
- Exploring separate modules of a large repository.
- Trying several independent solution approaches and comparing them against the same criteria.

Parallelism helps only when the lanes are genuinely independent. If worker B needs worker A's result, the work is a pipeline rather than a parallel fan-out.

### Sequential specialist pipeline

One worker's output becomes another worker's input, such as explorer → implementer → reviewer. The parent remains responsible for transferring the necessary state and evidence between stages.

This can keep roles focused, but every boundary can lose information. Prefer durable artifacts such as a plan file, patch, test report, or structured result when fidelity matters.

### Handoff

Control transfers from the current agent to a specialist, which becomes responsible for the next user-facing response. A handoff is related to delegation but differs from the manager pattern: the original agent is no longer synthesizing that branch behind the scenes.

Use a handoff when a specialist should own the conversation or operate under meaningfully different instructions and policy. Use a subagent-as-tool when a single manager should own the final response.

### Reviewer or evaluator

A worker independently checks an artifact produced by the parent or another worker. Independence is valuable here because the reviewer is less anchored to the original reasoning path.

The reviewer should receive the artifact, acceptance criteria, and necessary surrounding context, but not a long defense of why the original author believes the solution is correct.

## References

- [OpenAI: Multi-agent in the Responses API](https://developers.openai.com/api/docs/guides/responses-multi-agent)
- [OpenAI: Subagents in ChatGPT and Codex](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Anthropic: Create custom subagents in Claude Code](https://code.claude.com/docs/en/sub-agents)
- [OpenCode: Agents](https://opencode.ai/docs/agents)
- [Gemini CLI: Subagents](https://geminicli.com/docs/core/subagents/)
- [GitHub Copilot CLI: About custom agents](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents)
