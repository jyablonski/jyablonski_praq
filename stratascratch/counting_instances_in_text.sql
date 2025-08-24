{# https://platform.stratascratch.com/coding/9814-counting-instances-in-text?code_type=1

Find the number of times the exact words bull and bear appear in the contents column.


Count all occurrences, even if they appear multiple times within the same row. Matches should be
case-insensitive and only count exact words, that is, exclude substrings like bullish or bearing.


Output the word (bull or bear) and the corresponding number of occurrences. #}

-- cant just do normal % query_txt %, you have to check all the conditions for whether the word is equal to, or before, or after, or in between
-- the rest of the string
with word_counts as (
    select 
        count(case when contents ilike '% bull %'
                    or contents ilike 'bull %'
                    or contents ilike '% bull'
                    or lower(contents) = 'bull' then 1 end) as bull_count,
        count(case when contents ilike '% bear %'
                    or contents ilike 'bear %'  
                    or contents ilike '% bear'
                    or lower(contents) = 'bear' then 1 end) as bear_count
    from google_file_store
)
select 'bull' as word, bull_count as nentry from word_counts
union all
select 'bear' as word, bear_count as nentry from word_counts;


-- what i was trying before
with exact_matches as (
    select
        filename,
        case
            when
                contents like '% bull %'
                or contents like 'bull %'
                or contents like '% bull'
                or contents = 'bull' then 1
            when
                contents like '% bear %'
                or contents like 'bear %'
                or contents like '% bear'
                or contents = 'bear' then 1
        end as exact_match_type
    from google_file_store
)

select *
from exact_matches