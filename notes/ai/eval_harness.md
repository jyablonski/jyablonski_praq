# Evaluating an AI Analytics Assistant

## 1. What an eval harness is

An eval harness is a repeatable test framework for LLM-powered features. It runs a fixed set of test cases (questions with known correct answers) through the system, scores each response, and records the results so you can compare runs over time.

The closest analogy from data engineering is **dbt tests plus data observability**:

- **Offline evals** are like dbt tests: a known set of checks you run before or after changes to catch regressions.
- **Online evals** are like observability: monitoring real production traffic for failures your test set didn't anticipate.

You need both. Offline evals only cover questions you thought of. Online evals only catch problems after users hit them.

## 2. Why use one

An analytics assistant's main failure mode is a **confident, plausible, wrong number**. Unlike a broken dashboard, a wrong answer looks correct, so errors go unnoticed and end up in decks and decisions.

An eval harness gives you:

- **A measurable accuracy number** per domain, instead of "it seems to work."
- **Regression detection** when semantic views, agent instructions, or underlying models change.
- **Visibility into upstream changes you don't control**, such as model updates from Snowflake or OpenAI.
- **Forced clarity on metric definitions**, since you can't write a correct answer for "active users" until someone agrees on what it means.
- **Evidence for stakeholders**: "finance accuracy is 94% on 60 real questions" builds more trust than a disclaimer.

## 3. What to evaluate

Each layer can fail independently, so score them separately to know where something broke.

| Layer | Failure example |
| ------------------ | ------------------------------------------------------------------- |
| Routing | Agent picks the wrong semantic view or domain |
| Query generation | Wrong metric, filter, grain, or time window |
| Result correctness | Query runs but returns the wrong numbers |
| Narration | Correct data, but the answer misstates it ("flat" when it rose 30%) |
| Boundaries | Answers out-of-scope or unauthorized questions instead of declining |

## 4. The golden set

The core asset is a set of test cases, each with a question, the correct (gold) SQL, and tags.

```yaml
- id: fin_001
  question: "What was subscription revenue last month vs the month before?"
  domain: finance
  expected_view: semantic_finance
  gold_sql: |
    select ...
  tags: [time_comparison, simple]
  expect: answer            # answer | clarify | decline
  run_as_role: FINANCE_ANALYST
  source: pilot_intake      # pilot_intake | production_trace | handwritten
```

Guidelines:

- **Source questions from real stakeholders.** Engineers write clean questions; stakeholders write vague, jargon-heavy ones. Test the latter.
- **Store gold SQL, not gold numbers.** Data changes daily; hardcoded answers go stale.
- **Include negative cases**: ambiguous questions (`clarify`), nonexistent metrics and out-of-scope or unauthorized requests (`decline`).
- **Avoid leakage.** If verified queries are shown to the model, paraphrase them in the eval set or you're testing memorization.
- **Start small.** 20 to 30 questions per domain is enough to catch regressions; grow it from real failures.

## 5. How scoring works

The harness actually calls Snowflake. Gold SQL is the answer key; the agent is the test taker.

```
question --> Cortex Agent --> generated SQL --> result rows A --+
                                                                +--> diff: same numbers?
gold SQL -----------------------------------------> result rows B --+

agent's answer text + result rows A --> LLM judge: does the text match its own data?
```

Two independent checks:

- **Result-set diff (deterministic):** compares rows, with tolerance for column order, naming, row order (unless ranking was the point), and rounding. The SQL text itself is never compared; different queries can both be correct.
- **LLM judge:** checks narration faithfulness with a tight rubric and binary or 3-point scores. Periodically spot-check the judge against human grading.

For `clarify` and `decline` cases there is no gold SQL; the check is simply whether the agent asked or declined instead of returning numbers.

Practical notes:

- **Both queries must see the same data.** Run against a zero-copy clone or a fixed time-travel timestamp. Gold results can be cached per snapshot.
- **LLMs are nondeterministic.** Running each case a few times shows consistency; a question that's right 3 of 5 times is a trust problem.
- **Cost is small.** ~150 agent calls plus ~150 gold queries per full run is a few dollars of credits.

## 6. Snowflake architecture

- 1 semantic view per domain (~5 domains)
- 1 Cortex Agent with access to all semantic views
- 1 Snowflake MCP connected to the agent
- 1 ChatGPT plugin connected to the MCP, given to stakeholders

**Key point: there are two LLMs in the loop and we control only one.** ChatGPT decides whether to call the tool, rewrites the user's question before sending it, and re-narrates the agent's answer.

| Layer | What breaks | Control | Eval approach |
| -------------- | --------------------------------------------------- | ----------- | ------------------------------------------------- |
| Semantic views | Wrong metric, join, filter, grain | Us | Per-domain suite via Cortex Analyst directly |
| Cortex Agent | Wrong routing, unfaithful answer | Us | Full suite via agent; Snowflake agent evaluations |
| Snowflake MCP | Auth, role mapping, tool description | Us (config) | Small smoke suite |
| ChatGPT | Skips the tool, mangles question, re-narrates wrong | OpenAI | Periodic manual end-to-end check |

## 7. Offline evals in Snowflake

**Cadence: weekly scheduled run plus ad hoc runs.** Routine dbt and pipeline merges don't touch the agent and don't need the suite. Run it ad hoc (manually, or via a CI path filter) only for changes that affect answers:

- Semantic view YAML (metrics, dimensions, verified queries)
- Agent instructions or tool config
- Model or MCP config

The weekly run catches what our merges never would: model updates from Snowflake or OpenAI and upstream data shifts.

**Suites:**

- **Semantic view suite (per domain):** call Cortex Analyst directly against one semantic view. Isolates "is this view good" from routing. Only the changed domain's suite needs to run.
- **Agent suite:** full golden set through the agent, including routing, cross-domain, ambiguous, out-of-scope, and role-boundary cases run under representative stakeholder roles. Snowflake's native agent evaluations (`EXECUTE_AI_EVALUATION` with a YAML config) provide LLM-judge metrics; keep our own result-set diff for numeric correctness. Agent versioning lets us evaluate a draft version before promoting it.
- **MCP smoke tests:** 10 to 20 cases through an MCP client authenticated as test users per role. Checks plumbing and access boundaries, not accuracy.
- **ChatGPT end-to-end:** a short manual checklist before releases and after known OpenAI model changes. Watch for the tool not being called, questions losing filters, and numbers re-summarized incorrectly. Returning structured results (numbers, SQL, caveats) from the agent limits ChatGPT's room to paraphrase.

Results go to an `eval_results` table keyed by run, git sha, and agent version, so regressions are a SQL comparison against the previous run.

## 8. Online evals in Snowflake

**What Snowflake provides:** Cortex Agent traces (planning, tool selection, generated SQL, results, final response, tokens, user feedback) are logged to `SNOWFLAKE.LOCAL.AI_OBSERVABILITY_EVENTS`, readable via `GET_AI_OBSERVABILITY_EVENTS`.

**What we build:** a small dbt project over that table.

```sql
-- fct_agent_turns
select
    trace_id, thread_id, user_name, agent_version,
    tool_view_used, generated_sql,
    sql_error is not null        as had_sql_error,
    result_row_count = 0         as empty_result,
    is_rephrase_of_prior_turn,   -- same thread, similar question within N minutes
    latency_ms, total_tokens
from {{ ref('stg_agent_events') }}
```

Signals to watch: SQL errors, empty results, rephrases, follow-ups like "that's wrong," declines, latency, and token usage, sliced by domain and agent version.

**Sampled scoring:** weekly, sample turns per domain and run an LLM judge (`AI_COMPLETE`) to check whether the agent's answer matches the result it received.

**Blind spot:** from Snowflake we only see what ChatGPT sent and what the agent returned. We do not see the user's original prompt, ChatGPT's final answer, or ChatGPT thumbs up/down. Mitigations:

- A simple feedback channel (Slack workflow or form) for reporting bad answers.
- The custom page in the internal app, where we control the full surface, as a high-fidelity feedback source.

**Governance:** traces contain business data. Viewing unredacted content requires a specific account privilege; decide deliberately who gets it. Use usage views, not the event table, for cost reporting since trace delivery is best effort.

## 9. The flywheel

1. Flagged turns (errors, rephrases, low judge scores, user reports) go to a weekly review queue.
1. Each real failure becomes a golden case with `source: production_trace` and gold SQL.
1. The next weekly run includes it, so every failure becomes a permanent regression test.

Over time the eval set shifts from "questions we imagined" to "questions that actually broke."

## 10. Code layout sketch

```
evals/
  golden/
    finance.yaml
    editorial.yaml
    growth.yaml
    ...
  harness/
    runners.py     # call Cortex Analyst, Cortex Agent, MCP
    graders.py     # result-set diff, routing check, LLM judge
    run.py         # CLI: --target analyst|agent|mcp --domain finance
  smoke/
    test_mcp.py    # pytest, cases tagged `smoke`
dbt/models/ai_observability/
  stg_agent_events.sql
  fct_agent_turns.sql
  fct_eval_results.sql
```

```python
def run_case(case, target):
    resp = runners[target](case.question, role=case.run_as_role)
    return {
        "case_id": case.id,
        "routed_view": resp.view_used,
        "sql": resp.sql,
        "answer": resp.text,
        "scores": {
            "execution_match": diff_results(resp.sql, case.gold_sql) if case.gold_sql else None,
            "routing_ok": resp.view_used == case.expected_view,
            "behavior_ok": classify(resp) == case.expect,
            "faithful": llm_judge(resp.result_rows, resp.text),
        },
    }
```

The golden YAML files and the dbt trace models can exist from day one; the harness reads from them once it's built.

## 11. Recommended rollout path

**Phase 1: Build the end-to-end workflow**
Semantic views, Cortex Agent, MCP, ChatGPT plugin. Confirm trace logging works and the data team can query it.

**Phase 2: Internal testing with the data team**
Test under real stakeholder roles to exercise OAuth, role mapping, and access boundaries. Every bad answer gets written down with gold SQL; this is the first source of golden cases. Failures stay in-house where they're cheap.

**Phase 2 (parallel): Build the eval harness**

- Golden set YAML per domain, seeded from internal testing.
- Result-set diff, routing check, LLM judge.
- dbt models over the observability events.
- Feedback channel for ChatGPT users.
- **Stakeholder question intake:** ask each future pilot group for ~20 questions they'd want answered. Run them internally so the pilot isn't the first time the agent sees how stakeholders actually talk.

**Readiness criteria for pilot (define up front):**

- Golden set for pilot domains passes at an agreed threshold.
- Declines and role boundaries behave correctly.
- Trace models and feedback channel are live.

**Phase 3: Stakeholder pilot**
Start with one or two domains and engaged stakeholders who will check answers and report problems. Be explicit that numbers should be verified before use in decisions; a pilot cohort that treats it as a test protects the broader rollout.

**Phase 4: Steady state**
Weekly scheduled eval run, ad hoc runs for semantic view and agent changes, weekly trace review, and continuous promotion of real failures into the golden set.
