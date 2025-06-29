# Data Mesh

> Data Mesh is a sociotechnical approach where individual business domains (like marketing, sales, product) are responsible for owning, producing, and serving their data as products, with a self-serve platform enabling interoperability and governance.

It's a modern approach to organizing data architecture and data ownership across large, complex organizations. It shifts from centralized data teams and monolithic data lakes to a decentralized, domain-oriented model, borrowing heavily from principles of microservices and DevOps. It’s not a tool or product, it’s a paradigm shift in how data is managed in large orgs, aiming to scale analytics and unlock domain expertise.

Data Mesh is really only possible at medium to large orgs right because of the decentralized and domain-oriented nature of the approach. You need enough engineering talent to support each of the different departments while still operating at a high level and not sacrificing quality or throughput.

It's quite a natural and obvious transition as orgs get larger. You're not going to have 25+ people in the same standup or in the same data team, you have to branch out into separate teams with specific focus and areas of expertise.

- The goal when branching out though is you continue using the same shared data platform architecture & services, while you're all operating on different teams and serving different areas of the business
- It also requires strong internal platforms for data infrastructure, observability, cataloging to maintain all of that and allow teams to operate independently without each team having to reinvent the wheel.

The strengths of Data Mesh are:

- Fewer bottlenecks (not everything has to run through a central team)
- Clear and defined ownership & responsibilities
- Domain expertise and data maturity

Data Mesh doesn't make sense when:

- You're in a small company
- The organization doesn't have clear domain boundaries
- There's not enough engineering bandwidth to support robust platform tooling across the different teams

## Core Principles of Data Mesh

| Principle                        | Meaning                                                                                                                   |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| 1. Domain-Oriented Ownership | Data is owned and managed by the teams who know it best (e.g., Sales owns sales data).                            |
| 2. Data as a Product         | Teams treat their datasets like products: discoverable, trustworthy, well-documented, with clear SLAs.                |
| 3. Self-Serve Data Platform  | A shared platform provides tools, infrastructure, and standards to enable domains to own and serve data autonomously. |
| 4. Federated Governance      | Governance is shared: central standards (e.g. PII policies), but implementation is distributed across domains.        |

## What It Replaces (and Why)

| Traditional Data Lake / Warehouse Model | Data Mesh Alternative                                                |
| --------------------------------------- | -------------------------------------------------------------------- |
| Centralized data team owns everything   | Each domain owns its own data products                               |
| Monolithic ETL pipelines                | Decentralized pipelines built and owned by domains                   |
| Bottlenecks and lack of context         | Domain teams bring domain knowledge                                  |
| One-size-fits-all schema                | Tailored schemas per domain, but with standards for interoperability |


## Example

Imagine a company with:

- Sales Team: owns sales pipeline, revenue data
- Marketing Team: owns campaign, ad spend data
- Product Team: owns user engagement, feature usage

In a Data Mesh world:

- Each team publishes clean, governed, discoverable data products (like `daily_sales_metrics`, `campaign_performance`, `feature_engagement`)
- Other teams can consume these products via the self-serve platform
- Data platform team provides tools (e.g., Kafka, dbt, access control, observability) — not the pipelines themselves

## Benefits

- Scales with org size and team growth
- Enables faster data delivery - fewer bottlenecks
- Brings data ownership closer to the domain experts
- Encourages better data quality (teams own their mess)
- Supports multiple data modalities (batch, real-time, events)

## Challenges

- Requires mature data culture and cross-team collaboration
- Risk of data silos if standards aren’t enforced
- Domains must have each a team of software engineers to support the work
- Platform team must invest heavily in infrastructure & tooling
- Hard to retrofit into companies with deeply centralized legacy systems

## Tools That Support Data Mesh

| Layer                           | Examples                                                                   |
| ------------------------------- | -------------------------------------------------------------------------- |
| Modeling / Orchestration    | dbt, Dagster, Airflow                                                      |
| Data Catalog / Discovery    | Atlan, DataHub, Collibra                                                   |
| Access Control / Governance | Immuta, Okera, Monte Carlo                                                 |
| Infrastructure / Platform   | Snowflake, Kafka, Redpanda, Lakehouse tools (Iceberg, Delta, Hudi)         |
| Delivery / Serving          | APIs, data contracts, warehouse tables, semantic layers (Cube, MetricFlow) |
