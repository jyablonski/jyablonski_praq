# Data Governance

Data governance is the system of policies, roles, processes, and technical controls that keeps data trustworthy, secure, discoverable, and used responsibly. It answers a few practical questions: who owns this data, what does it mean, can we trust it, who may access it, how long should we retain it, and what happens when something goes wrong?

Governance is not a single tool or a one-time project. It is an operating practice shared by data engineering, security, legal, and business teams. Good governance allows a company to scale analytics and data products without creating conflicting metrics, unmanaged risk, or fragile pipelines.

The areas below are closely related. Together, they create a data environment in which people can find the right data, understand it, use it safely, and act on it with confidence.

## Data quality and reliability

Data quality defines what “correct” means for important datasets and verifies that those expectations continue to hold. Typical dimensions include freshness, completeness, validity, uniqueness, referential integrity, and business-rule correctness. Reliability also covers the pipelines and services that produce or move the data.

Poor-quality data leads to incorrect decisions, broken customer experiences, rework, and loss of confidence in the data team. Detecting problems before they reach a dashboard, model, or operational workflow reduces the cost of incidents and makes business reporting dependable.

In practice, use unit and integration tests in ingestion and platform code, schema checks at system boundaries, and transformation tests in dbt. Add reconciliation checks between layers, such as comparing source record counts with the raw and transformed tables. Define freshness and quality SLAs for critical data, monitor each pipeline step, and document an incident path with an owner, severity, communication plan, and follow-up actions. CI/CD should run relevant checks before changes are merged.

For example, an orders table might require a unique order ID, a non-null customer ID, non-negative order totals, and arrival within two hours of the source update. A failed freshness check should alert the responsible team before the daily revenue report is consumed.

## Metadata, cataloging, and discoverability

Metadata makes data understandable and findable. It includes technical metadata such as schemas and owners, as well as business metadata such as definitions, classifications, freshness, quality status, and approved use cases. A catalog should help someone answer “what is this data and can I use it?” without relying on tribal knowledge.

Discoverable data reduces duplicated work, shortens analysis time, and enables self-service. Clear descriptions also reduce the risk that an analyst selects a similarly named but inappropriate table or misinterprets a field such as `is_active`.

In practice, start with a lightweight data dictionary or business glossary for important datasets. dbt Docs can provide model and column documentation for the transformation layer, although it may not cover source systems or BI assets. As the number of systems and consumers grows, evaluate a cross-system catalog such as OpenMetadata. Establish minimum documentation requirements for production datasets: purpose, owner, grain, key fields, refresh cadence, quality expectations, sensitivity, and known limitations.

For example, a customer table entry should state whether it represents one row per customer or one row per customer account, explain the difference between `created_at` and `first_order_at`, and identify whether the table contains personal information.

## Lineage and impact analysis

Lineage records where data comes from and where it goes: from source application to ingestion, raw storage, transformations, and finally dashboards, models, or downstream products. It supports both planned change management and incident investigation.

Lineage becomes especially valuable when a source field changes or a dataset becomes unreliable. It shows which reports, models, teams, and customer-facing features may be affected, reducing the time needed to assess risk, communicate impact, and find the root cause.

In practice, dbt provides model-level lineage within a dbt project. Cross-system lineage from source applications through the warehouse and into BI tools requires additional integration and discipline; tools such as OpenMetadata or Monte Carlo may help. Review lineage before changing or deprecating a field, and include downstream owners in the communication for material changes.

For example, before renaming `net_revenue`, an engineer should be able to identify the finance model, executive dashboard, forecasting job, and alert that depend on it. The change can then be versioned, migrated, and retired deliberately instead of breaking consumers unexpectedly.

## Access control and data security

Access control determines who may access data, which operations they may perform, and how precisely those permissions are enforced. The default should be least privilege: users and services receive only the access required for their responsibilities.

Strong access controls reduce the likelihood and scope of data exposure while allowing teams to work efficiently. They also provide evidence that sensitive information is being managed intentionally, which supports customer trust and security audits.

In practice, use role-based access control (RBAC), separate human and service identities, and manage grants through reviewable configuration where practical. Apply row-level security when users should see only a subset of records, column-level controls or masking for sensitive fields, and separate development, staging, and production access. Review permissions periodically and remove stale access promptly.

For example, a support analyst may see customer account status but not full payment details, while a regional manager may see only customers in their assigned region. In Snowflake, these controls can be implemented with role hierarchies, masking policies, and row-access policies.

## Privacy and compliance

Privacy and compliance govern how regulated or sensitive data is collected, used, shared, retained, and deleted. Relevant obligations may include GDPR, CCPA/CPRA, HIPAA, PCI DSS, or SOC 2 controls, depending on the organization and its markets. Legal, privacy, and security teams typically define the obligations; the data team implements and operates many of the technical controls.

Compliance is not a direct revenue-generating feature, but it protects the business from fines, litigation, contractual loss, forced remediation, service disruption, and damage to customer trust. Privacy practices also make it safer to launch new products and use cases involving customer data.

In practice, classify sensitive fields, record the purpose and lawful basis for collection where applicable, track consent requirements, define retention periods, and maintain audit trails for access and changes. Build repeatable workflows for subject-access and deletion requests, and ensure deletion or anonymization propagates to warehouse copies, derived tables, extracts, and backups according to the applicable policy. Partner with legal and security before introducing a new sensitive-data use case.

For example, a deletion request should identify all systems containing the customer’s personal data, remove or anonymize eligible records, record what was done, and preserve only the information that the organization is legally required to retain.

## Ownership and stewardship

Ownership assigns accountability for a data domain or dataset. A data owner is responsible for business meaning, access decisions, and acceptable use; a data steward is often the subject-matter expert who maintains definitions, coordinates quality issues, and helps consumers. Engineering remains responsible for implementing and operating the technical system.

Named owners turn governance from a general expectation into an actionable responsibility. They provide a clear escalation path when definitions are disputed, quality degrades, access is requested, or a dataset needs to change.

In practice, assign an owner and steward to critical domains and record them in the catalog. Define responsibilities in a simple RACI or ownership matrix, including who approves access, who responds to incidents, and who signs off on major definition changes. Review ownership when teams or systems change, and establish service-level expectations for responding to questions and incidents.

For example, the finance domain owner may approve the definition of recognized revenue, while a finance steward explains exceptions and validates reconciliation results. Data engineering owns the models, tests, and deployment process that implement that definition.

## Metric and definition consistency

Metric governance ensures that commonly used business terms have one agreed definition, calculation, grain, and time basis. The goal is a version-controlled source of truth that can be reused across dashboards, analysis, models, and products.

Conflicting definitions create avoidable debates and undermine confidence in reporting. Consistent metrics let teams make decisions from the same numbers and reduce the time spent reconciling dashboards that appear to disagree.

In practice, maintain a business glossary and a governed semantic layer, with metric definitions stored in version control and reviewed by the relevant business owner. Document filters, exclusions, joins, time zones, currency treatment, and the intended grain. Use dbt metrics, a warehouse semantic view, or a BI semantic layer depending on the platform, but avoid maintaining multiple independent definitions of the same metric.

For example, “active user” should specify the qualifying event, lookback window, account status, timezone, and whether bots or internal users are excluded. A dashboard and a customer-retention model should consume the same governed definition.

## Data lifecycle and cost management

Lifecycle governance covers how data is created, retained, archived, deprecated, and removed. It also includes the cost of storing and processing data, especially in platforms with consumption-based pricing.

Explicit lifecycle and cost controls prevent storage and compute from growing without accountability. They reduce operational clutter, make platforms easier to maintain, and ensure that teams can explain whether a dataset’s business value justifies its ongoing cost and risk.

In practice, define retention and archival rules by data class, tag datasets and warehouse workloads by owner or cost center, and review usage and spend regularly. Give production datasets a deprecation process with an owner, usage check, communication period, migration path, and removal date. Monitor expensive queries and unused tables, and use quotas or alerts where appropriate.

For example, a raw event table may be retained for a defined period in low-cost storage, while a curated customer summary is kept longer for reporting. A monthly review can identify an unused dashboard extract, trace its dependent jobs, notify its owner, and retire it safely.

## Putting governance into practice

Governance works best when it is built into normal delivery rather than handled as a separate approval queue. Start with the datasets and metrics that are most important to revenue, customers, regulatory obligations, and executive reporting.

A practical minimum operating model is:

- Assign an owner and steward to each critical domain.
- Document critical datasets, metrics, sensitivity, freshness, and lineage.
- Add automated quality, security, and compliance checks to pipeline and model delivery.
- Review access, incidents, data quality, and platform cost on a regular cadence.
- Provide a change and deprecation process for shared datasets and definitions.

The level of tooling should match the organization’s scale. A small team can begin with dbt Docs, version-controlled definitions, warehouse permissions, and a lightweight glossary. As the number of systems, users, and regulatory obligations grows, a dedicated catalog, observability platform, and semantic layer may provide enough value to justify their additional operating cost.
