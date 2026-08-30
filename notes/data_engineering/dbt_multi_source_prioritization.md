# Prioritizing Attributes Across Sources in dbt

## The problem

Suppose you have a business attribute such as `job_title` may be available from several vendors, and vendors may disagree or return the attribute at different times.

The final model should expose one canonical value per entity while making the selection rule explicit and easy to change.

For each entity, the business rule is:

- Ignore missing attribute values.
- Prefer the highest-priority vendor that has a value.
- If the same vendor has multiple values, prefer the most recently observed value.
- Keep one selected value and retain its vendor and observation timestamp for traceability.

This is a ranking problem, not a series of `COALESCE` calls. Rank the available rows first, then keep the winning row.

## Example input

Store candidate values in a long-format staging model so each vendor value is a row:

```text
user_id | attribute_value          | vendor     | observed_at
42      | Director of Engineering  | zoominfo   | 2026-01-10
42      | VP Engineering           | clearbit        | 2025-12-15
42      | Engineering Director     | data_axle  | 2026-01-20
```

The canonical result for user `42` is `VP Engineering` from `clearbit` because `clearbit` has the highest priority, even though another vendor has a newer value.

## dbt model

Use a Jinja dictionary to map each vendor to a business-defined priority. A lower number means a higher priority.

```sql
{% set vendor_priority = {
    'clearbit': 1,
    'zoominfo': 2,
    'dun_and_bradstreet': 3,
    'data_axle': 4
} %}

WITH candidates AS (

    SELECT
        user_id,
        attribute_value,
        vendor,
        observed_at
    FROM {{ ref('stg_user_attribute_values') }}
    WHERE
        attribute_name = 'job_title'
        AND attribute_value IS NOT NULL

),

prioritized AS (

    SELECT
        user_id,
        attribute_value,
        vendor,
        observed_at,
        CASE
            {% for vendor, priority in vendor_priority.items() %}
            WHEN vendor = '{{ vendor }}' THEN {{ priority }}
            {% endfor %}
            ELSE 999
        END AS vendor_rank
    FROM candidates

),

selected AS (

    SELECT
        user_id,
        attribute_value,
        vendor,
        observed_at
    FROM prioritized
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY user_id
        ORDER BY vendor_rank ASC, observed_at DESC
    ) = 1

)

SELECT
    user_id,
    attribute_value AS job_title,
    vendor AS job_title_vendor,
    observed_at AS job_title_observed_at
FROM selected
```

## Why this works

Filtering out nulls before ranking means an unavailable value does not block a lower-priority vendor from being selected.

`vendor_rank ASC` makes vendor priority the primary rule, and `observed_at DESC` breaks ties when the same entity has multiple values from the same vendor.

The result keeps both the selected value and its provenance, so downstream users can see where the canonical value came from.

If freshness should beat vendor trust, reverse the sort keys: `ORDER BY observed_at DESC, vendor_rank ASC`.

## Practical notes

- Normalize vendor names before applying the mapping so casing and aliases do not create unexpected ranks.
- Give unknown vendors a low fallback priority such as `999`, then monitor them with a data-quality test or query.
- Add uniqueness and not-null tests to the final model so each `user_id` has at most one selected value.
- Keep the priority mapping close to the model while the rule is small and easy to review; move it to a seed or mapping model if many attributes share it.
