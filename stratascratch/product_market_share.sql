{# https://platform.stratascratch.com/coding/2112-product-market-share?code_type=1
Write a query to find the market share at the product brand level for each territory,
for the Q4-2021 time period.

Market share is defined as the number of orders of a certain product brand sold in a territory
divided by the total number of orders sold in this territory.

Output the ID of the territory, name of the product brand and the corresponding market share in
percentages. Only include these product brands that had at least one sale in a given territory.
 #}

with q4_2021_sales as (
    select
        fct_customer_sales.order_id,
        fct_customer_sales.prod_sku_id,
        dim_product.prod_brand,
        map_customer_territory.territory_id
    from fct_customer_sales
    inner join dim_product
        on fct_customer_sales.prod_sku_id = dim_product.prod_sku_id
    inner join map_customer_territory
        on fct_customer_sales.cust_id = map_customer_territory.cust_id
    where
        fct_customer_sales.order_date >= '2021-10-01'
        and fct_customer_sales.order_date <= '2021-12-31'
        
),

sales_agg as (
    select
        prod_brand,
        territory_id,
        count(*) as num_products_sold
    from q4_2021_sales
    group by
        prod_brand,
        territory_id
)

select
    territory_id,
    prod_brand,
    round(num_products_sold * 100.0 / sum(num_products_sold) over (partition by territory_id), 3) as market_share_pct
from sales_agg
order by
    territory_id,
    market_share_pct desc