import dlt
from dlt.sources.rest_api import rest_api_source
import duckdb

# Configure the REST API source with pagination
source = rest_api_source(
    {
        "client": {
            "base_url": "https://api.jyablonski.dev/v1/social/reddit/",
            "paginator": {
                "type": "page_number",
                "page_param": "page",
                "base_page": 1,  # Start at page 1 instead of 0
                "total_path": None,  # API doesn't return total pages
                "maximum_page": 6,  # Stop after 5 pages
            },
        },
        "resources": [
            {
                "name": "comments",
                "endpoint": {
                    "path": "comments",
                    "params": {
                        "limit": 20,
                        "page": 1,  # Starting page
                    },
                },
            },
        ],
    }
)

# Create an in-memory DuckDB connection
db = duckdb.connect(":memory:")

# Create the pipeline with the in-memory DuckDB instance
pipeline = dlt.pipeline(
    pipeline_name="reddit_comments_pipeline",
    destination=dlt.destinations.duckdb(db),
    dataset_name="reddit_data",
)

# Run the pipeline
print("Loading 5 pages of Reddit comments...")
load_info = pipeline.run(source)
print(load_info)

# Query the results
print("\n=== Total Records Loaded ===")
total = db.sql("SELECT COUNT(*) as total FROM reddit_data.comments").fetchdf()
print(f"Total comments: {total['total'].iloc[0]}")

print("\n=== Sample Data ===")
db.sql("""
    SELECT 
        scrape_date,
        author,
        LEFT(comment, 50) as comment_preview,
        score,
        flair
    FROM reddit_data.comments 
    ORDER BY score DESC 
    LIMIT 10
""").show()

print("\n=== Comments by Flair ===")
db.sql("""
    SELECT 
        COALESCE(flair, 'No Flair') as flair,
        COUNT(*) as count,
        AVG(score) as avg_score
    FROM reddit_data.comments
    GROUP BY flair
    ORDER BY count DESC
    LIMIT 10
""").show()

print("\n=== Sentiment Analysis ===")
db.sql("""
    SELECT 
        CASE 
            WHEN compound >= 0.05 THEN 'Positive'
            WHEN compound <= -0.05 THEN 'Negative'
            ELSE 'Neutral'
        END as sentiment,
        COUNT(*) as count,
        AVG(score) as avg_score
    FROM reddit_data.comments
    GROUP BY sentiment
    ORDER BY count DESC
""").show()
