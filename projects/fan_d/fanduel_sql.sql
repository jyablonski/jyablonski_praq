-- note: i moved the tables into postgres and wrote the queries in dbt.
-- i've converted the table names back to how they are in the sheet as requested.

-- fanduel question 1
with customers as (
    select
        *
    from customers
),

-- only 34 customers have casino data
casino_stakes as (
    select
        *
    from casino
),

customer_bets_placed as (
    select 
        customer_id,
        count(bet_id) as total_bets_placed,
        sum(bet_stake) as total_bet_stakes,
        sum(bet_revenue) as total_bet_revenue
    from sportsbook_bets
    group by customer_id

),

final as (
    select 
        customer_id,
        registration_state,
        total_bets_placed,
        total_bet_stakes,
        total_bet_revenue,
        casino_stakes
    from customers
    left join casino_stakes using (customer_id)
    left join customer_bets_placed using (customer_id)
    order by customer_id
)

select *
from final;

-- fanduel question 2
-- aggregate by sport_name + in_play_yn first
with customer_sport_bets_placed as (
    select 
        customer_id,
        sport_name,
        in_play_yn,
        count(bet_id) as total_sport_bets_placed,
        sum(bet_stake) as total_sport_bet_stakes,
        sum(bet_revenue) as total_sport_bet_revenue
    from sportsbook_bets
    group by customer_id, sport_name, in_play_yn

),

-- then join totals on
customer_total_bets_placed as (
    select 
        customer_id,
        count(bet_id) as total_bets_placed,
        sum(bet_stake) as total_bet_stakes,
        sum(bet_revenue) as total_bet_revenue
    from sportsbook_bets
    group by customer_id

),

-- divide football in_play bet stakes by their total bet stakes
final as (
    select 
        *,
        round(total_sport_bet_stakes::numeric / total_bet_stakes::numeric, 3)::numeric as pct_total_sport_bet_stake
    from customer_sport_bets_placed
    left join customer_total_bets_placed using (customer_id)
    where sport_name = 'football' and in_play_yn = 'Y' -- i cant reference the pct_total_sport_bet_stake alias here bc postgres
)

-- 27 customers returned who have bet at least 10% of their stakes on in-play football
select 
    customer_id
from final
where pct_total_sport_bet_stake >= 0.10;

-- fanduel question 3
with customers as (
    select
        *
    from customers
),

bets as (
    select 
        customer_id,
        bet_id,
        bet_state
    from sportsbook_bets
),

-- 461 unique bets returned
final as (
    select *
    from customers
    left join bets using (customer_id)
    where registration_state != bet_state
),

-- have to write this funky 'join' as join_col to join these 2 metrics later on
tot_customers as (
    select 
        count(customer_id) as num_total_bettors,
        'join' as join_col
    from customers
),

-- count distinct bc we're only looking for the # of customers doing this, not the total # of bets.
mismatch_aggs as (
select 
    count(distinct(final.customer_id)) as num_state_mismatch_bettors,
    'join' as join_col
from final
)

-- 23 / 99 which is 23.2% of the provided customers
select 
    round(num_state_mismatch_bettors::numeric / num_total_bettors::numeric, 3)::numeric as pct_state_mismatch_customers
from mismatch_aggs
left join tot_customers using (join_col);

-- fanduel question 4
with customers as (
    select 
        *
    from customers
),

-- only select the distinct state that each customer has bet in
customer_state_bets as (
    select distinct
        customer_id,
        bet_state
    from sportsbook_bets
    order by customer_id
),

-- group by customer_id and create a comma separated string of all the states a customer has bet in
customer_state_bets_concat as (
    select
        customer_id,
        string_agg(bet_state, ', ') as total_bet_states
    from customer_state_bets
    group by customer_id
),

-- have to join back to customers bc it says for each customer in that table
final as (
    select
        customer_id,
        total_bet_states
    from customers
    left join customer_state_bets_concat using (customer_id)
    order by customer_id
)

-- 97, 98, 99 missing - probably registered an account but never placed a bet?
select 
    customer_id,
    total_bet_states
from final;

-- fanduel question 5
-- I made 2 solutions: 1 to recreate the entire table and another to do an upsert (which is what i think you're asking for).

-- SOLUTION 1) Re-creating the table
with customer_bets_placed as (
    select 
        customer_id,
        count(bet_id) as total_bets_placed,
        sum(bet_stake) as total_bet_stakes,
        sum(bet_revenue) as total_bet_revenue,
        max(bet_placed_date) as last_sportsbook_bet_placed_date
    from sportsbook_bets
    group by customer_id
    order by customer_id

)

select *
from sportsbook_totals;

-- SOLUTION 2) Upsert - insert new records if customer_id isnt found, and upsert new data in existing records ONLY if the last_sportsbook_bet_placed_date
--   in the sportsbook_bets table is less than what's already in the sportsbook_total table.
INSERT INTO sportsbook_totals as T (customer_id, total_bets, total_bet_stakes, total_bet_revenue, last_sportsbook_bet_placed_date)
select 
    customer_id,
    count(bet_id) as total_bets,
    sum(bet_stake) as total_bet_stakes,
    sum(bet_revenue) as total_bet_revenue,
    max(bet_placed_date) as last_sportsbook_bet_placed_date
from sportsbook_bets as B
group by customer_id

ON CONFLICT (customer_id)
    DO UPDATE SET total_bets=excluded.total_bets,
                  total_bet_stakes=excluded.total_bet_stakes,
                  total_bet_revenue=excluded.total_bet_revenue,
                  last_sportsbook_bet_placed_date=excluded.last_sportsbook_bet_placed_date
                   WHERE T.last_sportsbook_bet_placed_date < excluded.last_sportsbook_bet_placed_date;