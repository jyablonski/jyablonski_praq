/* https://platform.stratascratch.com/coding/10156-number-of-units-per-nationality?code_type=1

We have data on rental properties and their owners. Write a query that figures out how many
different apartments (use unit_id) are owned by people under 30, broken down by their
nationality. We want to see which nationality owns the most apartments, so make sure to
sort the results accordingly. */

-- really dumb, the airbnb_hosts dataset had a fuckton of dupes
select
    airbnb_hosts.nationality,
    count(distinct airbnb_units.unit_id) as apartment_count

from airbnb_units
inner join airbnb_hosts
    on airbnb_units.host_id = airbnb_hosts.host_id
where
    airbnb_hosts.age < 30
    and unit_type = 'Apartment'
group by airbnb_hosts.nationality
order by 2 desc