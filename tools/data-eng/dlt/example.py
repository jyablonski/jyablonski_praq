import dlt
from dlt.sources.rest_api import rest_api_source

source = rest_api_source(
    {
        "client": {
            "base_url": "https://api.example.com/",
            "auth": {
                "token": dlt.secrets["your_api_token"],
            },
            "paginator": {
                "type": "json_link",
                "next_url_path": "paging.next",
            },
        },
        "resources": [
            # "posts" will be used as the endpoint path, the resource name,
            # and the table name in the destination. The HTTP client will send
            # a request to "https://api.example.com/posts".
            "posts",
            # The explicit configuration allows you to link resources
            # and define query string parameters.
            {
                "name": "comments",
                "endpoint": {
                    "path": "posts/{resources.posts.id}/comments",
                    "params": {
                        "sort": "created_at",
                    },
                },
            },
        ],
    }
)

pipeline = dlt.pipeline(
    pipeline_name="rest_api_example",
    destination="duckdb",
    dataset_name="rest_api_data",
)

load_info = pipeline.run(source)
