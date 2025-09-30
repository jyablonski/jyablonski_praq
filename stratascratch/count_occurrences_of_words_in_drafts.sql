/* https://platform.stratascratch.com/coding/9817-find-the-number-of-times-each-word-appears-in-drafts?code_type=1

Find the number of times each word appears in the contents column across all rows in the google_file_store dataset.
Output two columns: word and occurrences.

you just have to do the following operations, in order:

1. lowercase the `contents` text
2. convert the `contents` column into an array of words, split by `' '`
3. unnest that array to create 1 row for every word
4. regexp replace any punctuation with an empty space. this could be done in step 1 as well

*/


select
    regexp_replace(unnest(string_to_array(lower(contents), ' ')), '[.,!?]', '') as word,
    count(*) as occurrences
from google_file_store
group by 1
order by 2 desc