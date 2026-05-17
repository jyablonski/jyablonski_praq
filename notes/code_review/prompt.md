# Prompt

Act as a senior software engineer helping me improve my code review skills.

Create 5 code review exercises in Python, with a mix of data pipeline code, web service handlers, and CLI utilities. Each exercise should include a realistic code snippet under 25 lines.

Issues should be the kind that pass linters and unit tests but cause incidents in production. Avoid anything findable by mypy, ruff, or a basic test suite. Across the five exercises, cover at least four of the categories below. A snippet can contain more than one issue, but at least one issue per snippet should come from this list:

- silent data corruption
- unbounded growth (memory, queues, log volume, retries)
- hangs and deadlocks
- partial failures and inconsistent state
- incorrect behavior under load or concurrency
- contract violations across service or version boundaries
- security and trust boundary violations

Do not provide the answers yet.

For each exercise, include:

1. A short title
1. The code snippet
1. 1-3 sentences of production context: what the code does, where it runs, and what depends on it

I'll reply with my notes per exercise, numbered. My notes may be terse.

After I send my review notes, grade them. For each exercise, tell me:

1. What I nailed
1. What I partially caught
1. What I missed
1. What I flagged that wasn't actually a problem
1. The top 2-3 issues a strong reviewer should catch
1. For the top issue, show a corrected snippet or describe the fix concretely (not "add error handling" but what specifically)

Don't soften feedback to be polite. If I missed something obvious, say so. If my review was strong, say that without padding. Prioritize production-impact issues over style nitpicks. Rank findings by severity: security, correctness, data loss, hangs, resource leaks, bad retries, scaling problems, and maintainability.
