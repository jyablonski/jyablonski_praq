## Rank Functions
SCENARIO: you're ranking ppl based on these 5 salaries
    - 100k, 90k, 70k, 70k, 60k.
    - 5 salaries, but 4 unique values.

`Row_number` will return a unique value for each record, even if they're the same exact value.
    - ranks of 1, 2, 3, 4, 5 - even if all 5 values are the same
    - one person with 70k will have rank 3, the other will be rank 4 - but they're both the same salary at 70k.

`Rank` will have duplicate values for the same value in the order by column, skipping when going to the next rank (2 ranks of 4 will then skip 5 and go to 6).
    - ranks of 1, 2, 3, 3, 5
    - rank 4 gets completely skipped over
    - rank 3 is the one with the 2 70k values.
  
`Dense_rank` does no skipping, but still has duplicates of rank.
    - ranks of 1, 2, 3, 3, 4
    - there is no rank 5 bc dense_rank doesn't skip when there's a duplicate rank.


## Windows Functions
Performs a calculation across set of table rows that are related to the current row.  This allows you to do aggregation type stuff without group by.  The rows retain their unique identities. 

`round(avg(pts) over(partition by player ROWS BETWEEN '{{rolling_avg_parameter}}' PRECEDING AND CURRENT ROW), 1)::numeric as rolling_avg_pts,`
    - partition by basically means group by
    - you can also use order by after the partition statement.
    - `BETWEEN 9 PRECEDING AND CURRENT ROW` lets you make moving average stuff for the data.