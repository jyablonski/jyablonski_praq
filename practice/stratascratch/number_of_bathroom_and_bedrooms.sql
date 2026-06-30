{# https://platform.stratascratch.com/coding/9622-number-of-bathrooms-and-bedrooms?code_type=1

Find the average number of bathrooms and bedrooms for each city’s property types. Output the result along with the city name and the property type.
 #}

with city_property_type_avgs as (
    select
        city,
        property_type,
        avg(bedrooms) as n_bedrooms_avg,
        avg(bathrooms) as n_bathrooms_avg
    from airbnb_search_details
    group by
        city,
        property_type
)

select
    city,
    property_type,
    n_bathrooms_avg,
    n_bedrooms_avg
from city_property_type_avgs
