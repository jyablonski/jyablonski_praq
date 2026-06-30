import dlt
from dlt.sources.rest_api import rest_api_source

import duckdb

# Configure the REST API source
source = rest_api_source(
    {
        "client": {
            "base_url": "https://api.jyablonski.dev/v1/league/",
        },
        "resources": [
            {
                "name": "game_types",
                "endpoint": {
                    "path": "game_types",
                },
            },
        ],
    }
)


# Create an in-memory DuckDB connection
db = duckdb.connect(":memory:")

# Create the pipeline with the in-memory DuckDB instance
pipeline = dlt.pipeline(
    pipeline_name="game_types_pipeline",
    destination=dlt.destinations.duckdb(db),
    dataset_name="league_data",
)

# Run the pipeline
load_info = pipeline.run(source)
print(load_info)

# Now you can query directly using the db connection
result = db.sql("SELECT * FROM league_data.game_types").fetchdf()
print(result)

# Or query specific data
print("\nRegular Season Games:")
db.sql("""
    SELECT game_type, n, explanation 
    FROM league_data.game_types 
    WHERE season_type = 'Regular Season'
""").show()

# The database will exist in memory until the script ends
