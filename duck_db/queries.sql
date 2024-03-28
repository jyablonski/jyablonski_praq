-- https://duckdb.org/docs/extensions/tpch.html
-- it has queries
select *
from nba_prod.reddit_comments
qualify row_number() over(partition by author order by scrape_ts desc) = 1; 

select count(*) from main.customer;

PRAGMA tpch(4);
FROM tpch_queries();