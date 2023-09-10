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


# Incremental 

When you mark a model as incremental, the entire model (not specific cte's) will be incremental. This means the final query will be built according to your incremental strategy (delete+insert, or merge).
The is_incremental() macro allows you to (for example) filter your source data to reduce the number of rows that you will add to your final materialization.
This means that if you have something like this
```
with cte1 as
(
SELECT * FROM my_source
{% if is_incremental() %}

WHERE my_col > (select max(my_col) from {{ this }})

{% endif %}
)
, cte2 as 
(
SELECT col1 + col2 FROM cte1
)
select * from cte1, cte2
For normal (not full-refresh) runs, your final query is going to create the first cte (cte1) with the where clause included, and your second cte (which references cte1) will only get rows that meet the criteria in the WHERE clause of cte1.
I hope I explained this somewhat better :neutral_face:

with cte1 as
(
SELECT * FROM my_source
{% if is_incremental() %}

WHERE my_col > (select max(my_col) from {{ this }})

{% endif %}
)
, cte2 as 
(
SELECT col1 + col2 FROM cte1
)
select * from cte1, cte2
```

## Source Freshness
[Article](https://www.datafold.com/blog/dbt-source-freshness)