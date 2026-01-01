# SQL Geospatial

Geometric and geospatial data types in a data warehouse, such as those available in Snowflake, are used to represent, store, and manipulate data related to locations, shapes, and distances on the Earth’s surface. These data types serve various purposes in spatial analysis, such as mapping, location-based queries, and geographic calculations. Here's a breakdown of their purpose, usage, and common use cases.

### **Geometric vs. Geospatial Data**

- **Geometric data** refers to shapes and structures that are mathematically defined (like points, lines, and polygons) but not tied to a specific location on Earth. These are used in scenarios where you care about the relative position of points or objects but not their location on a global scale.
- **Geospatial data** refers to spatial data that has geographic references—meaning it describes a location on the Earth’s surface. These include coordinates such as latitude and longitude, and they allow operations like calculating distances, finding points within certain regions, etc.

### **Geospatial Data Types in Snowflake**

1. **GEOGRAPHY**: This type stores spatial data representing locations on the Earth's surface. It supports latitude/longitude coordinates and can store complex objects like points, lines, and polygons.

   - **Point**: A single location (e.g., coordinates of a city).
   - **LineString**: A path made up of multiple connected points (e.g., a road or river).
   - **Polygon**: An enclosed shape (e.g., the boundary of a state or a lake).

   Snowflake supports operations like distance calculations, area measurements, determining whether a point lies inside a region, and more.

   - Storing your data in GEOGRAPHY columns can significantly improve the performance of queries that use geospatial functionality.

### **When to Use Geospatial Data Types**

1. **Location-based analysis**:
   Geospatial data is used when you need to analyze data that involves geographic locations. This includes:

   - Finding the nearest store or facility to a user’s location.
   - Determining which region (e.g., a state or district) a specific point falls within.

1. **Spatial relationships**:
   When you need to understand the relationships between different locations, such as:

   - Calculating distances between two geographic points (e.g., customer location to store).
   - Checking whether a point falls within a certain boundary or region (e.g., whether a house is within a flood zone).

1. **Mapping and visualization**:
   Geospatial data is often used when you want to generate maps or visualize data spatially. This could be used for:

   - Creating heat maps of data like sales density across a region.
   - Showing routes or areas of coverage for logistics or service companies.

### **Common Use Cases**

1. **Retail and Logistics**:

   - **Store locator**: Find the nearest store or warehouse for a customer based on their current geographic location.
   - **Delivery routing**: Calculate the best routes for delivery trucks or optimize logistics based on distance from distribution centers.
   - **Sales territory mapping**: Define sales regions and assign customers to specific representatives based on their locations.

1. **Real Estate**:

   - **Property location**: Analyze properties based on proximity to certain points of interest (e.g., schools, parks).
   - **Region zoning**: Determine which properties fall within particular zones (e.g., residential, commercial).

1. **Telecommunications**:

   - **Network coverage**: Map out cell tower coverage areas and ensure optimal placement of new towers to minimize dead zones.
   - **Service availability**: Check whether a potential customer location is within an area serviced by the provider.

1. **Transportation**:

   - **Route optimization**: For ride-sharing or delivery services, determine the fastest or most efficient routes using spatial analysis.
   - **Public transportation planning**: Analyze population density and travel patterns to optimize the placement of bus routes or subway lines.

1. **Environmental Studies**:

   - **Natural resource mapping**: Analyze geographic areas for resources like water bodies, forests, and mineral deposits.
   - **Disaster response**: Determine affected areas during events like wildfires or floods using polygon boundaries and spatial queries.

### **Functions for Geospatial Analysis**

- **ST_DISTANCE()**: Calculates the distance between two geospatial objects.
- **ST_WITHIN()**: Checks if one geospatial object is within another (e.g., if a point is inside a polygon).
- **ST_INTERSECTS()**: Determines if two geospatial objects intersect (e.g., if two paths cross each other).

### **Why Use These in Snowflake?**

Using geospatial data types in a cloud-based data warehouse like Snowflake allows for:

- **Scalability**: Handle large volumes of location data efficiently.
- **Integrated Analysis**: Combine geospatial data with other business data (e.g., customer demographics, sales) for richer insights.
- **SQL-Based**: Perform spatial queries directly within SQL, without needing external geospatial tools or libraries.

```sql
-- Create a table with sample geospatial data
CREATE OR REPLACE TABLE fact.locations (
    location_id INT,
    location_name STRING,
    location_type STRING,
    geography GEOGRAPHY
);

-- Insert sample data: Points (latitude/longitude)
INSERT INTO fact.locations VALUES
(1, 'New York City', 'City', 'POINT(-74.006 40.7128)'),
(2, 'Los Angeles', 'City', 'POINT(-118.2437 34.0522)'),
(3, 'San Francisco', 'City', 'POINT(-122.4194 37.7749)');

-- Insert sample data: Lines (for routes)
INSERT INTO fact.locations VALUES
(4, 'Road between NYC and LA', 'Route', 'LINESTRING(-74.006 40.7128, -118.2437 34.0522)');

-- Insert sample data: Polygon (for area)
INSERT INTO fact.locations VALUES
(5, 'Golden Gate Park', 'Park', 'POLYGON((-122.4862 37.7694, -122.4791 37.7694, -122.4791 37.7659, -122.4862 37.7659, -122.4862 37.7694))');

select *
from fact.locations;

-- snowflake is doing all of this in meters, so to go from meters -> miles you have to divide by 1609.34
SELECT
    round(ST_DISTANCE(
        (SELECT geography FROM locations WHERE location_name = 'New York City'),
        (SELECT geography FROM locations WHERE location_name = 'Los Angeles')
    ) / 1609.34, 2) AS distance_miles;


-- Check if San Francisco is within Golden Gate Park
SELECT
    location_name,
    ST_WITHIN(
        (SELECT geography FROM locations WHERE location_name = 'San Francisco'),
        (SELECT geography FROM locations WHERE location_name = 'Golden Gate Park')
    ) AS is_within_park
FROM locations
WHERE location_name = 'San Francisco';


-- Find the nearest city to a specific point (e.g., coordinates in the U.S.)
WITH point AS (
    SELECT TO_GEOGRAPHY('POINT(-119.4179 36.7783)') AS current_location -- This is somewhere in California
)
SELECT
    location_name,
    round(ST_DISTANCE(geography, (SELECT current_location FROM point)) / 1609.34, 2) AS distance_miles
FROM locations
WHERE location_type = 'City'
ORDER BY distance_miles ASC
LIMIT 10;  -- Get the top 10 nearest cities



-- Calculate the length of the route (in meters)
SELECT
    location_name,
    round(ST_LENGTH(geography) / 1609.34, 2) AS route_length_miles
FROM locations
WHERE location_type = 'Route';


-- Check if Los Angeles lies on the road between NYC and LA
SELECT
    location_name,
    ST_INTERSECTS(
        (SELECT geography FROM locations WHERE location_name = 'Los Angeles'),
        (SELECT geography FROM locations WHERE location_name = 'Road between NYC and LA')
    ) AS is_on_route
FROM locations
WHERE location_name = 'Los Angeles';
```
