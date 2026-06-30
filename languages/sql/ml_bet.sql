{% set bet_parameter = 15 %}
{% set bet_amount = range(10, 25) %}

with schedule_wins as (
    select 
        a.team as home_team,
        s.date as proper_date,
        s.outcome as outcome
    from {{ ref('prep_schedule_analysis') }} as s
    left join {{ ref('staging_seed_team_attributes') }} as a on a.team_acronym = s.team
    where location = 'H'
),


my_cte as (
    select 
        *,
        case when home_team_predicted_win_pct >= 0.5 then 'Home Win'
            else 'Road Win' end as ml_prediction,
        case when outcome = 'W' then 'Home Win' 
            else 'Road Win' end as actual_outcome
    from {{ source('ml_models', 'tonights_games_ml') }}
    left join schedule_wins using (home_team, proper_date)
    where proper_date < date({{ dbt_utils.current_timestamp() }} - INTERVAL '6 hour')
),

-- the data points actually broken down
-- ml is correct when ml_accuracy = 1
game_predictions as (
    select distinct *,
        case when ml_prediction = actual_outcome then 1 else 0 end as ml_accuracy
    from my_cte
),

home_odds as (
    select
        a.team as home_team,
        date as proper_date,
        moneyline as home_moneyline
    from {{ ref('staging_aws_odds_table') }}
    left join {{ ref('staging_seed_team_attributes') }} a using (team_acronym)
),

away_odds as (
    select
        a.team as away_team,
        date as proper_date,
        moneyline as away_moneyline
    from {{ ref('staging_aws_odds_table') }}
    left join {{ ref('staging_seed_team_attributes') }} a using (team_acronym)
),
-- this shows the actual game outcomes that should be bet on
game_outcomes as (
    select
        away_team,
        home_team,
        proper_date,
        outcome,
        home_team_predicted_win_pct,
        away_team_predicted_win_pct,
        ml_prediction,
        actual_outcome,
        ml_accuracy,
        home_moneyline,
        away_moneyline,
        case when ml_accuracy = 1 and ml_prediction = 'Home Win' and home_moneyline < 0
                then round('{{ bet_parameter }}' * (-100 / home_moneyline), 2)
             when ml_accuracy = 1 and ml_prediction = 'Home Win' and home_moneyline > 0
                then round('{{ bet_parameter }}' * (home_moneyline / 100), 2)
             when ml_accuracy = 1 and ml_prediction = 'Road Win' and away_moneyline < 0
                then round('{{ bet_parameter }}' * (-100 / away_moneyline), 2)
             when ml_accuracy = 1 and ml_prediction = 'Road Win' and away_moneyline > 0
                then round('{{ bet_parameter }}' * (away_moneyline / 100), 2)
             when ml_accuracy = 0 then -1 * '{{ bet_parameter }}'
             else -10000  -- im testing to make sure it never hits -10000 - if it does then there's an error
             end as ml_money_col
    from game_predictions
    left join home_odds using (home_team, proper_date)
    left join away_odds using (away_team, proper_date)
    where (away_team_predicted_win_pct >= 0.55 AND away_team_predicted_win_pct <= 0.75)
         OR
          (home_team_predicted_win_pct >= 0.65 AND home_team_predicted_win_pct <= 0.67)
        AND proper_date < '2022-04-11' -- can choose to include playoffs or not - i find betting to be worse odds than during reg season
    order by proper_date desc
),

-- this cte shows the road vs home success of the betting strategy
final_aggs as (
    select 
        ml_prediction,
        ml_accuracy,
        sum(ml_money_col) as tot_profit,
        count(*) as games_bet
    from game_outcomes
    group by ml_accuracy, ml_prediction
),

-- $96 profit, 83 games bet, $1.15 per bet
-- this cte is the average $ per bet
profit_aggs as (
    select 
        sum(tot_profit) as sum_tot_profit,
        sum(games_bet) as tot_games_bet,
        round(sum(tot_profit) / sum(games_bet), 3) as tot_profit_per_bet,
        '{{ bet_parameter }}' as bet_amount
    from final_aggs
)

-- TO DO: do a for loop somehow to check out profit per $ changes based on different bet amounts from $5 - $25 
-- https://docs.getdbt.com/guides/getting-started/learning-more/using-jinja
select * 
from profit_aggs


-- NEW
select 
    tot_games_bet,
    {% for bet_amount in bet_amounts %}
    round(sum_tot_profit_{{ bet_amount }} / tot_games_bet, 2) as profit_per_bet_{{ bet_amount }},
    sum_tot_profit_{{ bet_amount }}
    {% if not loop.last %},{% endif %}
    {% endfor %}
from profit_aggs


select 
    tot_games_bet,
    unnest(array['sum_tot_profit_10', 'sum_tot_profit_11']) AS bets,
    unnest(array[sum_tot_profit_10, sum_tot_profit_11]) AS bet_values
from profit_aggs


,
        {% for bet_amount in bet_amounts %}
        bet_{{ bet_amount }}
        {% if not loop.last %},{% endif %}
        {% endfor %}


-- try 2
{% set bet_parameter = 15 %}
{% set bet_amounts = range(10, 26) %}

with schedule_wins as (
    select 
        a.team as home_team,
        s.date as proper_date,
        s.outcome as outcome
    from {{ ref('prep_schedule_analysis') }} as s
    left join {{ ref('staging_seed_team_attributes') }} as a on a.team_acronym = s.team
    where location = 'H'
),


my_cte as (
    select 
        *,
        case when home_team_predicted_win_pct >= 0.5 then 'Home Win'
            else 'Road Win' end as ml_prediction,
        case when outcome = 'W' then 'Home Win' 
            else 'Road Win' end as actual_outcome
    from {{ source('ml_models', 'tonights_games_ml') }}
    left join schedule_wins using (home_team, proper_date)
    where proper_date < date({{ dbt_utils.current_timestamp() }} - INTERVAL '6 hour')
),

-- the data points actually broken down
-- ml is correct when ml_accuracy = 1
game_predictions as (
    select distinct *,
        case when ml_prediction = actual_outcome then 1 else 0 end as ml_accuracy
    from my_cte
),

home_odds as (
    select
        a.team as home_team,
        date as proper_date,
        moneyline as home_moneyline
    from {{ ref('staging_aws_odds_table') }}
    left join {{ ref('staging_seed_team_attributes') }} a using (team_acronym)
),

away_odds as (
    select
        a.team as away_team,
        date as proper_date,
        moneyline as away_moneyline
    from {{ ref('staging_aws_odds_table') }}
    left join {{ ref('staging_seed_team_attributes') }} a using (team_acronym)
),
-- this shows the actual game outcomes that should be bet on
game_outcomes as (
    select
        away_team,
        home_team,
        proper_date,
        outcome,
        home_team_predicted_win_pct,
        away_team_predicted_win_pct,
        ml_prediction,
        actual_outcome,
        ml_accuracy,
        home_moneyline,
        away_moneyline,
        {% for bet_amount in bet_amounts %}
        case when ml_accuracy = 1 and ml_prediction = 'Home Win' and home_moneyline < 0
            then round('{{ bet_amount }}' * (-100 / home_moneyline), 2)
            when ml_accuracy = 1 and ml_prediction = 'Home Win' and home_moneyline > 0
                then round('{{ bet_amount }}' * (home_moneyline / 100), 2)
            when ml_accuracy = 1 and ml_prediction = 'Road Win' and away_moneyline < 0
                then round('{{ bet_amount }}' * (-100 / away_moneyline), 2)
            when ml_accuracy = 1 and ml_prediction = 'Road Win' and away_moneyline > 0
                then round('{{ bet_amount }}' * (away_moneyline / 100), 2)
            when ml_accuracy = 0 then -1 * '{{ bet_amount }}'
            else -10000  -- im testing to make sure it never hits -10000 - if it does then there's an error
            end as bet_{{bet_amount}}
        {% if not loop.last %},{% endif %} -- you're looping together a million different case whens, so you need commas for that.
        {% endfor %}
    from game_predictions
    left join home_odds using (home_team, proper_date)
    left join away_odds using (away_team, proper_date)
    where (away_team_predicted_win_pct >= 0.55 AND away_team_predicted_win_pct <= 0.75)
         OR
          (home_team_predicted_win_pct >= 0.65 AND home_team_predicted_win_pct <= 0.67)
        AND proper_date < '2022-04-11' -- can choose to include playoffs or not - i find betting to be worse odds than during reg season
    order by proper_date desc
),

final_aggs as (
    select 
        ml_prediction,
        ml_accuracy,
        count(*) as games_bet,
        {% for bet_amount in bet_amounts %}
        sum(bet_{{ bet_amount }}) as tot_profit_{{ bet_amount }}
        {% if not loop.last %},{% endif %}
        {% endfor %}
    from game_outcomes
    group by 
        ml_accuracy,
        ml_prediction
),


profit_aggs as (
    select 
        {% for bet_amount in bet_amounts %}
        sum(tot_profit_{{ bet_amount }}) as sum_tot_profit_{{ bet_amount }}
        {% if not loop.last %},{% endif %}
        {% endfor %},
        sum(games_bet) as tot_games_bet
    from final_aggs
),

unnest_aggs as (
    select 
        tot_games_bet,
        unnest(array[
        {% for bet_amount in bet_amounts %}
        {{ bet_amount }} 
        {% if not loop.last %},{% endif %}
        {% endfor %}
        ]) AS bet_amount,
        unnest(array[
        {% for bet_amount in bet_amounts %}
        sum_tot_profit_{{ bet_amount }}
        {% if not loop.last %},{% endif %}
        {% endfor %}
        ]) AS tot_bets_profit
    from profit_aggs   
),

final_metrics as (
    select
        tot_games_bet,
        bet_amount,
        tot_bets_profit,
        round(tot_bets_profit / tot_games_bet, 2) as tot_profit_per_bet
    from unnest_aggs
)

select *
from final_metrics