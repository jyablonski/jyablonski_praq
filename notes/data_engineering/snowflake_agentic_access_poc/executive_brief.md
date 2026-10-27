# Brief

Business stakeholders want to ask questions about organizational data in plain language and trust the answers as much as their dashboards. This doc provides sa high level overview of how to accomplish that.

**Goal:** define business metrics once in Snowflake semantic views and reuse them in Sigma and a ChatGPT Analytics plugin. Dashboard and chat answers should agree.

**Expected Outcome:** let stakeholders ask routine business questions in plain language while reducing duplicated metric definitions and reliance on ad-hoc Analyst resources.

**Architecture:** ChatGPT uses each person's OAuth sign-in to call one Snowflake-hosted MCP endpoint exposing an `analytics` tool. ChatGPT invokes this when relevant questions inquiring about data are asked. A shared Cortex Agent uses domain-specific Analyst tools to generate SQL and executes it with the person's permissions. Sigma queries the semantic views directly.

**Access model:** Snowflake roles determine which data each person can retrieve. Consumers share the MCP endpoint, Agent, and OAuth client registration; their personal identity and role determine access.

- Stakeholders can only get relevant data returned based on their Snowflake role permissions.
- The Agent skips inaccessible domain views and returns warnings. ChatGPT preserves those limitations and communicates them clearly to users.

**Scaling:** 1 semantic view per domain with however many metric definitions we need, and as much AI context we want to give. Each domain gets a Snowflake Role we assign in Okta to stakeholders for access. All semantic views get bundled up into the Snowflake Cortex Agent for context. That agent is what gets used in the MCP that we connect to ChatGPT.

**Pilot:** We should pilot this across 1 specific domain (subscriptions -> growth?) first. Validate that it works end to end on a single domain, and then pick a second domain to incorporate next which will let us prove out scalability.

**Downsides**

- Requires business stakeholders to receive a Snowflake login for ChatGPT Plugin permissions/auth to work. Snowflake users are free to create, but now Snowflake will pop up in their Okta Apps and could potentially cause confusion. We should make stakeholder-facing documentation stating this, along with how to setup and use the ChatGPT plugin.
- Cortex Agent, MCP, ChatGPT OAuth are all in Terraform. We'll have to loop through the semantic views here too, but those are created in dbt, so potential for things to become out of sync (unlikely, but possible).
- We can't answer everything. 80/20 principle; lets identify the most common things we're asked or expected to answer so that our semantic views can solve those cases and be used downstream.

**Things to Know**

- If we decide to enable agentic access to Snowflake data outside of this ChatGPT plugin, we'll need the same semantic views and Cortex Agent anyways. The OAuth and role pattern might change. If we have plans to do this, like put it in the CMS or elsewhere, communicate it ASAP.
- We're charged for both Snowflake AI credits on these agent invocations, as well as query executions (normal warehouse usage). I expect this to be low and that we'll be covered fine in our current contract, but it's not free.
- This is entirely dependent upon solid Mart models and the Semantic Views reporting accurate data. The infrastructure, access permissions, and cross-platform boundary are separate.