/* https://platform.stratascratch.com/coding/9650-find-the-top-10-ranked-songs-in-2010?code_type=1

Find the top 10 ranked songs in 2010. Output the rank, group name, and song name, but do not
show the same song twice. Sort the result based on the rank in ascending order. */

-- sigh
select distinct
    year_rank,
    group_name,
    song_name
from billboard_top_100_year_end
where year = 2010
order by
    year_rank
limit 10