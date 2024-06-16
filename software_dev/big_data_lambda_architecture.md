# Lambda Architecture

![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/d3f9865f-8399-4b8a-be02-8ad6ecc7e87a)


Lambda Architecture is a technique used to process and analyze large streams of data in real-time.


## Batch Layer

The Batch Layer handles large scale data processing and computations on batch data. It's typically pre-built and ready for querying, and includes historical data + metrics

## Speed Layer

The Speed Layer typically includes real-time data processing for all records that have been generated since the last time the Batch Layer was updated

## Serving Layer

The Serving Layer combines data from the batch / pre-computed view layer and the speed layer to merge the result together and provide a single unified view for the data. This allows users to have access to the historical data + metrics in the Batch Layer while also having access to data in the Speed Layer which enables users to gather accurate and timely insights.


## How it Looks in Practice

Various business logic can go into these tables, but basically you're just querying the old data and unioning the more recent. This can get more complex with various aggregations as well.

Again, things should already be computed in the Batch Layer.  The streaming layer may have to run various computations and aggregations on the fly if needed in order to stay in sync with the batch layer.


- `batch_payments.sql`
- `streaming_payments.sql`
- `serving_payments_layer`

``` sql
-- batch_payments
with payments_data as (
    select
        payment_id,
        invoice_id,
        customer_id,
        payment_type_id,
        payment_amount,
        is_voided,
        payment_created_at
    from {{ source('application_db_source', 'payments')}}
    where 
        is_voided = 0
        and date(payment_created_at) < current_date
)

select *
from payments_data
```


``` sql
-- streaming_payments

-- maybe payments aren't valid until they're >= 4 hrs old
-- at which point they're moved from some unverified source into the actual table
with payments_data as (
    select
        payment_id,
        invoice_id,
        customer_id,
        payment_type_id,
        payment_amount,
        payment_created_at
    from {{ source('application_db_source', 'payments_unverified')}}
    where 
        date(payment_created_at) >= current_date
        and payment_type_id in (1, 23, 55)
        and payment_created_at >= current_timestamp - interval '4 hours'

)

select *
from payments_data
```



``` sql
-- serving_payments_layer

with batch_data as (
    select
        payment_id,
        invoice_id,
        customer_id,
        payment_type_id,
        payment_amount,
        payment_created_at
    from {{ ref('batch_payments') }}
),

streaming_data as (
    select
        payment_id,
        invoice_id,
        customer_id,
        payment_type_id,
        payment_amount,
        payment_created_at
    from {{ ref('streaming_payments') }}
)

select *
from batch_data
union
select *
from streaming_data

```