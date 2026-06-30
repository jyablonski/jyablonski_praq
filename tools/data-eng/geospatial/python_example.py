import geopandas as gpd
from shapely.geometry import Point
from geopy.distance import geodesic

# sample data: locations with (latitude, longitude)
locations = [
    {"name": "Location A", "lat": 37.7749, "lon": -122.4194},
    {"name": "Location B", "lat": 37.8044, "lon": -122.2711},
    {"name": "Location C", "lat": 37.6879, "lon": -122.4702},
    {"name": "Location D", "lat": 37.3382, "lon": -121.8863},
]

# convert sample data to GeoDataFrame
gdf = gpd.GeoDataFrame(
    locations, geometry=[Point(x["lon"], x["lat"]) for x in locations]
)

# reference point (e.g., Company HQ)
reference_point = (37.7749, -122.4194)  # Example: San Francisco, CA

radius_miles = 10


# function to check if a location is within the given radius
def within_radius(location, ref_point, radius):
    loc_point = (location.y, location.x)
    return geodesic(ref_point, loc_point).miles <= radius


# filter the dataframe for locations within x miles of the reference point
gdf["within_radius"] = gdf["geometry"].apply(
    lambda loc: within_radius(loc, reference_point, radius_miles)
)

# get locations within the radius
nearby_locations = gdf[gdf["within_radius"]]

# location D is not within the 10 mile radius
print(f"Locations within 10 miles:\n\n{nearby_locations[['name', 'lat', 'lon']]}")

cities = gpd.GeoDataFrame(
    {
        "name": ["San Francisco", "New York", "Los Angeles"],
        "geometry": [
            Point(-122.4194, 37.7749),
            Point(-74.006, 40.7128),
            Point(-118.2437, 34.0522),
        ],
    },
    crs="EPSG:4326",
)
