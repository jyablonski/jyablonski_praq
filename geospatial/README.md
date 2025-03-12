# Geospatial data

Geospatial data represents locations, shapes, and spatial relationships using coordinates, geometries, and spatial reference systems.

GeoPandas is a python library that gives support for spatial joins, coordinate reference system (CRS) handling, and spatial operations like the distance between 2 points, or if a location intersects with some area.

- It uses the shapely library for data types like `Point`, which is essentially a tuple of latitute + longitude points.

For SQL, an extension called PostGIS can be installed on a Postgres Database to enable similar functionality within a Database context.

- This is typically available on most managed Postgres databases from cloud providers, but you probably have to manually enable it
- `SELECT * FROM pg_available_extensions;`

- `docker run --name postgis-db -e POSTGRES_USER=myuser -e POSTGRES_PASSWORD=mypassword -e POSTGRES_DB=mydatabase -p 5432:5432 -d postgis/postgis`
- [Docs](https://postgis.net/documentation/getting_started/)

### Coordinates (Latitude & Longitude)
- Latitude (lat): How far north or south a point is from the Equator (-90 to 90).  
- Longitude (lon): How far east or west a point is from the Prime Meridian (-180 to 180).  
- Example:  
  - 🗺️ San Francisco: `(37.7749, -122.4194)`  
  - 🗺️ New York: `(40.7128, -74.0060)`

---

### Geospatial Data Types
Geospatial data is usually represented as Points, Lines, and Polygons.

| Type     | Example Use Case                     | Representation |
|----------|--------------------------------------|---------------|
| Point  | Store locations (stores, cities, users) | `(lat, lon)` or `POINT(x, y)` |
| Line   | Roads, rivers, travel routes | `LINESTRING(x1 y1, x2 y2, ...)` |
| Polygon | Boundaries (countries, zones, delivery areas) | `POLYGON((x1 y1, x2 y2, x3 y3, ...))` |

PostGIS Example:
```sql
SELECT ST_AsText(ST_MakePoint(-122.4194, 37.7749));  -- POINT(-122.4194 37.7749)
```

---

## Geospatial Data Types in Databases

### Geometry vs. Geography
PostGIS provides two ways to store spatial data:

1. GEOMETRY:  
   - Uses a flat, Cartesian coordinate system (XY).
   - Good for small-scale maps (city planning, CAD systems).
   - Distances are calculated in the unit of the coordinate system.
   - Example:  
     ```sql
     CREATE TABLE places (
         id SERIAL PRIMARY KEY,
         name TEXT,
         geom GEOMETRY(Point, 4326)
     );
     ```
    - 4326 refers to the EPSG code for the WGS 84 (World Geodetic System 1984) coordinate reference system (CRS). This is the standard coordinate system used for latitude and longitude in GPS and mapping applications.


2. GEOGRAPHY:  
   - Uses a spherical model of the Earth (lat/lon).
   - Best for global-scale calculations (distances, GPS data).
   - Automatically accounts for the Earth's curvature.
   - Example:  
     ```sql
     CREATE TABLE locations (
         id SERIAL PRIMARY KEY,
         name TEXT,
         geom GEOGRAPHY(Point, 4326)
     );
     ```
   
💡 Key Difference:  
- GEOMETRY: Fast but assumes a flat world.  
- GEOGRAPHY: Accurate for distances but slower.  

---

# Spatial Reference Systems (SRS) & EPSG Codes

### What is an SRS?
A Spatial Reference System (SRS) defines how lat/lon coordinates map to real-world locations. Every SRS has a unique EPSG code.

| EPSG Code | Name | Use Case |
|-----------|------------|------------|
| 4326 | WGS 84 | GPS coordinates (Lat/Lon) |
| 3857 | Web Mercator | Web mapping (Google Maps, OpenStreetMap) |
| 27700 | OSGB 1936 | UK Ordnance Survey |

💡 PostGIS Example: Convert Between SRS
```sql
SELECT ST_Transform(ST_SetSRID(ST_MakePoint(-122.4194, 37.7749), 4326), 3857);
```
✅ Converts a point from WGS 84 (lat/lon) to Web Mercator (meters).

---

### Find Locations Within a Radius
```sql
SELECT name
FROM locations
WHERE ST_DWithin(
    geom, 
    ST_SetSRID(ST_MakePoint(-122.4194, 37.7749), 4326), 
    16093.4  -- 10 miles in meters
);
```

### Calculate Distance Between Two Points
```sql
SELECT ST_Distance(
    ST_SetSRID(ST_MakePoint(-122.4194, 37.7749), 4326), 
    ST_SetSRID(ST_MakePoint(-74.0060, 40.7128), 4326)
) / 1609.34 AS distance_miles;
```

### Find Which Region a Point is In
```sql
SELECT region_name
FROM regions
WHERE ST_Contains(regions.geom, ST_SetSRID(ST_MakePoint(-122.4194, 37.7749), 4326));
```

---

# 6️⃣ Why Use Geospatial Databases?
🔹 Store and query millions of locations efficiently.  
🔹 Perform fast distance and area calculations.  
🔹 Optimize location-based services (e.g., "Find nearby stores").  
🔹 Power GIS applications, delivery systems, and GPS tracking.  
