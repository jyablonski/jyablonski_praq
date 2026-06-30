SELECT * FROM pg_available_extensions;

CREATE EXTENSION postgis;

SELECT postgis_version();

CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name TEXT,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    geom GEOGRAPHY(Point, 4326) -- WGS 84 (Lat/Lon)
);

INSERT INTO locations (name, lat, lon, geom)
VALUES 
    ('Location A', 37.7749, -122.4194, ST_SetSRID(ST_MakePoint(-122.4194, 37.7749), 4326)),
    ('Location B', 37.8044, -122.2711, ST_SetSRID(ST_MakePoint(-122.2711, 37.8044), 4326)),
    ('Location C', 37.6879, -122.4702, ST_SetSRID(ST_MakePoint(-122.4702, 37.6879), 4326)),
    ('Location D', 37.3382, -121.8863, ST_SetSRID(ST_MakePoint(-121.8863, 37.3382), 4326));

select *
from locations;

SELECT id, name, lat, lon
FROM locations
WHERE ST_DWithin(
    geom, 
    ST_SetSRID(ST_MakePoint(-122.4194, 37.7749), 4326), 
    16093.4  -- 10 miles in meters
);

SELECT 
    l1.name AS location1, 
    l2.name AS location2, 
    ST_Distance(l1.geom, l2.geom) / 1609.34 AS distance_miles
FROM locations l1, locations l2
WHERE l1.id < l2.id;  -- Avoid duplicate pairs

CREATE INDEX locations_gix ON locations USING GIST (geom);

SELECT name, ST_Distance(geom, ST_SetSRID(ST_MakePoint(-122.4194, 37.7749), 4326)) AS distance_meters
FROM locations
ORDER BY distance_meters ASC
LIMIT 4;

