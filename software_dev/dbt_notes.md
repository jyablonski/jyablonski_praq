# dbt
[CTE Passthroughs](https://discourse.getdbt.com/t/ctes-are-passthroughs-some-research/155/3)

## Schema Management

`dbt_project.yml`
```
models:
  +on_schema_change: "sync_all_columns"
```

`models/fact/table_incremental.sql`
```
{{
    config(
        materialized='incremental',
        unique_key='date_day',
        on_schema_change='fail'
    )
}}
```

## Environment Management
`models/source.yml`
```
version: 2
 
sources:
  - name: source_name 
    database: |
      {%- if  target.name == "dev" -%} development
      {%- elif target.name == "stg"  -%} staging
      {%- elif target.name == "prod"  -%} production
      {%- else -%} invalid_database
      {%- endif -%}
    schema: source_schema
```

`models/fact/table1.sql`
```
select
    *
from {{ source('my_src', 'table1') }}

{% if target.name == 'dev' %}
limit 1000
{% endif %}
```

## Delete + Merge
Option 1: Filter
Filter them out in the where clause `WHERE __deleted != true`.

Option 2: Delete
```
{{
    config(
        materialized=’incremental’,
        unique_key=’order_pk’,
        post_hook=’delete from {{this}} where __deleted = true’
    )
}}
``` 