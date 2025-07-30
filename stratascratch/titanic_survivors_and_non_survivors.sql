{# https://platform.stratascratch.com/coding/9881-make-a-report-showing-the-number-of-survivors-and-non-survivors-by-passenger-class?code_type=1

Make a report showing the number of survivors and non-survivors by passenger class. Classes are categorized based on the pclass value as:
•	First class: pclass = 1
•	Second class: pclass = 2
•	Third class: pclass = 3
Output the number of survivors and non-survivors by each class.#}

with survivor_aggs as (
    select
        survived,
        count(case when pclass = 1 then 1 end) as first_class,
        count(case when pclass = 2 then 1 end) as second_class,
        count(case when pclass = 3 then 1 end) as third_class
    from titanic
    group by survived
)

select
    survived,
    first_class,
    second_class,
    third_class
from survivor_aggs
