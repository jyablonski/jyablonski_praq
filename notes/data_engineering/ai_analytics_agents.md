# AI Agents, Semantic Layers, and Text-to-SQL

## Is a Semantic Layer a Prerequisite?

A formal semantic-layer product is not a technical prerequisite for building an AI analytics agent. A governed semantic contract is, however, effectively a prerequisite for delivering consistent and trustworthy answers at scale.

Without that contract, the agent must infer business logic from raw schemas, documentation, and historical SQL. It can generate syntactically valid SQL while selecting the wrong revenue definition, join path, date field, filter, or grain.

A semantic layer gives the agent approved metric definitions, valid dimensions and relationships, consistent access policies, and a constrained query surface. Once the agent selects a governed metric such as `monthly_revenue`, its calculation is deterministic even though the LLM's interpretation of the stakeholder's question is not.

For a narrow assistant that supports a fixed set of known questions, curated marts, precomputed metrics, approved parameterized queries, stored procedures, or a certified query library can provide the same contract without a dedicated semantic-layer product. As the number of metrics, dimensions, consumers, and possible questions grows, a formal semantic layer becomes the cleanest way to manage and enforce that contract.

```text
Reliable analytics agent =
  governed semantic definitions
  + constrained execution
  + user-level authorization
  + validated queries
  + regression evaluations
  + faithful result interpretation
  + explicit uncertainty
```

The semantic layer is therefore an important foundation, not a complete reliability solution. Credentials, runtime policies, evaluations, and response validation remain necessary around it.

## The Goal

The useful product is not merely text-to-SQL. It is an analytics agent that can accept an ambiguous stakeholder question, determine which governed business concepts are relevant, run one or more safe queries, inspect the results, and return a concise answer with enough context to trust it.

A request such as "How is revenue trending, and which customer segment drove the latest change?" is not a single SQL-generation task. The agent must identify the approved revenue metric, establish the intended time range and grain, query the overall trend, detect the period worth investigating, run a segment breakdown, and explain what the results do and do not show.

The semantic layer makes this tractable by constraining the agent to business concepts that have already been defined and reviewed.

## Separation of Responsibilities

The semantic layer and the agent are separate components with different responsibilities:

- The semantic layer defines metrics, dimensions, relationships, filters, access rules, and the supported query surface. Depending on the implementation, it also compiles and executes queries.
- The agent interprets natural language, resolves ambiguity, chooses semantic members, plans an investigation, calls query tools, evaluates the returned data, and writes the stakeholder-facing response.
- The warehouse stores the data and performs the underlying computation.
- A catalog such as OpenMetadata provides human-facing discovery, ownership, lineage, certification, and glossary context.

The semantic layer is deterministic for a given query. The LLM is not. Governance comes from keeping metric calculation and access enforcement in deterministic systems while using the LLM for intent interpretation, planning, and explanation.

## Reference Architecture

```text
Stakeholder
    |
    | natural-language question
    v
Chat, Slack, Teams, ticket, or application UI
    |
    v
Agent orchestrator
    |-- discovers approved metrics and dimensions
    |-- resolves ambiguity and plans the analysis
    |-- generates structured queries or Semantic SQL
    |-- validates queries and enforces budgets
    |
    v
Semantic layer API or semantic SQL endpoint
    |-- validates members, joins, filters, and access
    |-- compiles governed definitions into warehouse SQL
    v
Warehouse
    |
    | result rows
    v
Agent orchestrator
    |-- checks and compares results
    |-- runs bounded follow-up queries when needed
    |-- produces an answer with provenance and limitations
    v
Stakeholder
```

The preferred boundary is that the agent receives credentials for the semantic layer, not credentials for the underlying warehouse tables.

## The Agent Query Loop

A production analytics agent should follow a bounded loop rather than generate one query and immediately narrate the result.

1. Receive the ask. Capture the user's identity, role, conversation context, locale, and current time.
1. Resolve intent. Identify the requested metric, dimensions, grain, filters, comparison period, and output shape. Ask a clarification question when phrases such as "revenue," "recent," or "best customer" are materially ambiguous.
1. Discover the governed model. Retrieve only the relevant semantic metadata: member names, descriptions, formats, relationships, supported granularities, synonyms, ownership, and certification.
1. Plan the analysis. Break a broad question into a small sequence of answerable queries before executing anything.
1. Generate a semantic query. Prefer a structured API request when possible; use Semantic SQL when the analysis needs SQL expressiveness.
1. Validate before execution. Reject unknown members, DDL/DML, unrestricted raw columns, missing tenant context, excessive time ranges, or queries without a row limit.
1. Execute through the semantic layer. Preserve the requesting user's authorization context so row-level and member-level policies remain effective.
1. Inspect the result. Check empty results, nulls, unexpected totals, incomplete periods, units, and whether the output actually answers the question.
1. Iterate when justified. Run a limited number of follow-up queries for breakdowns, comparisons, or reconciliation. Stop when the answer is supported or the query budget is exhausted.
1. Respond with provenance. Return the conclusion, supporting values, metric definition, filters, time range, data freshness, and any material limitation.

The agent should be allowed to say that the semantic model cannot answer a question. That is preferable to silently inventing a join, metric, or causal explanation.

## Why an Agent May Run Several Queries

Stakeholder questions often contain both a measurement request and an investigation request. Consider:

> How did monthly revenue change over the last six months, and which segment caused the latest decline?

A reasonable plan is:

1. Query monthly revenue for the requested period.
1. Identify the most recent complete month and calculate the change from the prior month.
1. Query revenue by customer segment for those two months.
1. Query revenue by region if the segment result does not explain the change.
1. Reconcile the breakdown totals to the overall metric.
1. Report which segment contributed most to the decline, while avoiding a stronger causal claim than the data supports.

The queries are dynamic, but their building blocks are controlled. The agent chooses from approved metrics and dimensions rather than recreating the definition of revenue in every generated statement.

## Three Query Paths

| Path | How it works | Strength | Risk and limitation |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Structured semantic API | The agent selects measures, dimensions, filters, time grains, and ordering in a typed request | Small attack surface and easy validation | Limited to operations exposed by the API and model |
| Semantic SQL | The agent writes SQL against semantic cubes or views and uses governed metric functions such as `MEASURE()` or `AGG()` | Familiar and expressive while retaining governed metrics | Requires SQL parsing, cost controls, and careful handling of supported SQL |
| Direct warehouse SQL | The agent reads semantic documentation but queries physical tables directly | Maximum flexibility for uncovered questions | Bypasses the semantic runtime, can recreate metrics incorrectly, and requires tightly constrained warehouse access |

The first two should be the default. Direct warehouse SQL is an explicit escape hatch for specialized analyst workflows, not the normal stakeholder path. If it exists, use a separate read-only role, isolated execution environment, strict cost limits, and clear labeling that the result is not a certified semantic-layer answer.

## Cube Pattern

Cube operates as an external semantic-layer service between the agent and the warehouse.

For a custom agent built on Cube Core:

1. Call the Meta API to discover public cubes, measures, dimensions, descriptions, types, and custom metadata.
1. Provide relevant metadata to the LLM or expose it through a model-discovery tool.
1. Let the LLM produce a Cube REST/GraphQL request or Semantic SQL query.
1. Validate and execute the request through Cube.
1. Return the result rows to the LLM for analysis and presentation.

The agent can use Cube without receiving warehouse credentials. Cube holds the warehouse connection and applies the metric definitions, join graph, and access policies. Cube Core is headless, so the chat interface and orchestration are custom application concerns. The hosted Cube platform additionally supplies direct MCP and Chat API integrations.

A Cube Semantic SQL query for monthly revenue might look like:

```sql
SELECT
  DATE_TRUNC('month', order_date) AS month,
  MEASURE(monthly_revenue) AS monthly_revenue
FROM orders
GROUP BY 1
ORDER BY 1;
```

The LLM chooses the month grain and requested period, but it does not redefine `monthly_revenue`. Cube evaluates the governed measure definition.

## Snowflake Pattern

Snowflake Semantic Views embed the semantic layer in the warehouse. A user or agent connects with a Snowflake identity and queries metrics and dimensions defined in the semantic view. The role can be granted access to the semantic view without receiving `SELECT` on its underlying tables.

Cortex Analyst provides a native natural-language path. Its REST API accepts a stakeholder question plus one or more semantic views and can return generated SQL, clarification suggestions, warnings, and verified-query provenance. It also supports multi-turn conversations. Cortex Agents can use Cortex Analyst as a tool for structured-data retrieval.

This is operationally different from Cube: Snowflake authenticates the consumer or agent and performs the query directly, while Cube authenticates the consumer at an external service and connects to the warehouse on the consumer's behalf.

Snowflake's current Cortex Analyst routing can fall back from semantic SQL to standard SQL when a semantic view cannot cover an ask. That flexibility should be treated as an explicit governance decision. A role restricted to the semantic view preserves a strict semantic-only boundary because it cannot read the base tables used by a fallback query.

## Tool Design for a Custom Agent

Do not give the LLM a general database shell when a narrow tool contract will work. A minimal agent can operate with three tools:

```text
search_semantic_model(question)
  -> relevant metrics, dimensions, descriptions, and relationships

run_semantic_query(query, user_context, row_limit, timeout)
  -> columns, rows, freshness, request ID, and execution metadata

get_metric_definition(metric_name)
  -> business definition, owner, certification, format, and source assets
```

The orchestrator—not the LLM—should attach authorization context, enforce limits, parse or validate queries, redact sensitive fields, and decide whether another query is allowed.

Metadata retrieval should also be selective. Sending an entire enterprise semantic model on every prompt increases cost and makes incorrect member selection more likely. Retrieve the smallest connected portion of the model that covers the question, then expand only when the initial plan requires it.

## Stakeholder Response Contract

A good response is more than a prose answer. It should include:

- Direct answer: the conclusion in business language.
- Supporting data: the values, comparison, or compact table used to reach it.
- Metric definition: which governed metric was used and what it includes or excludes.
- Scope: filters, dimensions, date range, timezone, currency, and whether the latest period is complete.
- Provenance: semantic view or Cube measure, query/request ID, and data freshness.
- Limitations: ambiguity, missing dimensions, small samples, fallback to non-certified SQL, or inability to establish causation.

For higher-risk use cases, expose the generated semantic query and provide a link to reproduce the result in the BI or semantic-layer interface.

## Accuracy and Evaluation

Evaluate the complete system rather than asking whether the generated SQL parses. A useful test set pairs representative stakeholder questions with expected semantic members, queries or result sets, and response requirements.

Maintain a library of verified stakeholder questions. These examples serve as regression tests, onboarding prompts, and retrieval context. Snowflake Semantic Views support verified queries directly, while a custom Cube agent can keep the same question/query pairs in its own evaluation suite.

## Automation Use Cases

Once the interactive question-answering path is reliable, the same agent pattern can support:

- Slack or Teams analytics assistants w/ slash commands
- Automated responses to routine data-support tickets.
- Dashboard companions that explain a selected chart or filter state.
- Metric-definition lookup and lineage questions through a catalog integration.

Automation should initially stop at analysis and recommendation. Actions that change customer state, financial records, forecasts, or operational systems require a separate approval and control model.

## Practical Starting Point for the Cube POC

The smallest useful implementation on top of the local Cube project is:

1. Expose the stakeholder question to an LLM application.
1. Fetch `http://localhost:4000/cubejs-api/v1/meta` and retrieve the relevant measure and dimensions.
1. Ask the model to return a structured Cube REST query or read-only Semantic SQL, not arbitrary Postgres SQL.
1. Validate the selected members and enforce a row limit, time range, timeout, and maximum of three query attempts.
1. Execute against Cube's REST or SQL API.
1. Pass only the result rows and metric metadata back to the model.
1. Require the final answer to state the metric, filters, period, result, and limitations.
1. Test it against a fixed set of stakeholder questions before exposing it broadly.

That POC demonstrates the essential value proposition: natural-language flexibility on top of deterministic, governed metric execution. The LLM decides what to ask; the semantic layer remains authoritative for how the answer is calculated.
