{# Table: Insurance

+-------------+-------+
| Column Name | Type  |
+-------------+-------+
| pid         | int   |
| tiv_2015    | float |
| tiv_2016    | float |
| lat         | float |
| lon         | float |
+-------------+-------+
pid is the primary key (column with unique values) for this table.
Each row of this table contains information about one policy where:
pid is the policyholder's policy ID.
tiv_2015 is the total investment value in 2015 and tiv_2016 is the total investment value in 2016.
lat is the latitude of the policy holder's city. It's guaranteed that lat is not NULL.
lon is the longitude of the policy holder's city. It's guaranteed that lon is not NULL. #}
{# 
Write a solution to report the sum of all total investment values in 2016 tiv_2016, for all policyholders who:

have the same tiv_2015 value as one or more other policyholders, and
are not located in the same city as any other policyholder (i.e., the (lat, lon) attribute pairs must be unique).
Round tiv_2016 to two decimal places.

The result format is in the following example.

  #}


with dupe_tiv_2015 as (
    select
        tiv_2015,
        count(*) as tiv_2015_num_copies
    from Insurance
    group by tiv_2015
),

dupe_lat_lon as (
    select
        lat,
        lon,
        count(*) as latlon_num_copies
    from Insurance
    group by lat, lon
)

select
    round(sum(tiv_2016), 2) as tiv_2016
from Insurance
    left join dupe_tiv_2015 on Insurance.tiv_2015 = dupe_tiv_2015.tiv_2015
    left join dupe_lat_lon
        on Insurance.lat = dupe_lat_lon.lat
        and Insurance.lon = dupe_lat_lon.lon
where
    dupe_tiv_2015.tiv_2015_num_copies > 1
    and dupe_lat_lon.latlon_num_copies = 1