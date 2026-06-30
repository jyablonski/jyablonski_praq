/* https://platform.stratascratch.com/coding/10182-number-of-streets-per-zip-code?code_type=1

Count the number of unique street names for each postal code in the business dataset. Use only
the first word of the street name, case insensitive (e.g., "FOLSOM" and "Folsom" are the same).
If the structure is reversed (e.g., "Pier 39" and "39 Pier"), count them as the same street.
Output the results with postal codes, ordered by the number of streets (descending) and
postal code (ascending). */

-- have to wrap it lower case and use split_part function
-- because of the pier 39 or 39 pier constraint they throw in, you need to catch these data scenarios
-- with a case when to skip the number if possible.

-- this uses a regex filter ot detect if the string is purely numeric, and if so it skips it and ujses the word value
WITH extracted_street_names AS (
    SELECT 
        business_postal_code,
        LOWER(
            CASE
                WHEN split_part(business_address, ' ', 1) ~ '^[0-9]+$' THEN split_part(business_address, ' ', 2)
                WHEN split_part(business_address, ' ', 2) ~ '^[0-9]+$' THEN split_part(business_address, ' ', 1)
                ELSE split_part(business_address, ' ', 1)
            END
        ) AS street_name
    FROM sf_restaurant_health_violations
    WHERE business_postal_code IS NOT NULL
)

-- then after you get the cleaned up street_name you can just do a distinct count
SELECT 
    business_postal_code,
    COUNT(DISTINCT street_name) AS n_streets
FROM extracted_street_names
GROUP BY business_postal_code
ORDER BY
    n_streets DESC,
    business_postal_code ASC;