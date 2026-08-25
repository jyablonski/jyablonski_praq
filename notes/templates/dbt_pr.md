# dbt PR Template

JIRA-1234

## What

\<1-2 sentence summary of the change>

## Why

3-4 bullets explaining why this change is necessary

## Change type

- [ ] New model
- [ ] Change to an existing model
- [ ] Non-model (macro, test, seed, source, docs)

## Downstream impact

- [ ] None, or additive only (new column, new model)
- [ ] Breaking: column renamed, dropped, retyped, or grain changed
- [ ] Consumers notified (dashboards, semantic views, reverse ETL)

## PII

- [ ] No PII
- [ ] Contains PII, columns tagged and masking policy applied

## Performance

Materialization: table / view / incremental / ephemeral

Expected runtime:

- [ ] under 20s
- [ ] under 5 min
- [ ] under 30 min
- [ ] over 30 min (justify below)

## Validation

- [ ] `dbt build --select state:modified+` passes
- [ ] Row count and spot check against current prod
