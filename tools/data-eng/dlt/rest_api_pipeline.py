from typing import Any, Optional

import dlt
from dlt.common.pendulum import pendulum
from dlt.sources.rest_api import (
    check_connection,
    rest_api_resources,
    rest_api_source,
)


@dlt.source(name="github")
def github_source(access_token: Optional[str] = dlt.secrets.value) -> Any:
    config = {
        "client": {
            "base_url": "https://api.github.com/repos/dlt-hub/dlt/",
            "auth": (
                {
                    "type": "bearer",
                    "token": access_token,
                }
                if access_token
                else None
            ),
        },
        "resource_defaults": {
            "primary_key": "id",
            "write_disposition": "merge",
            "endpoint": {
                "params": {
                    "per_page": 100,
                },
            },
        },
        "resources": [
            {
                "name": "issues",
                "endpoint": {
                    "path": "issues",
                    "params": {
                        "sort": "updated",
                        "direction": "desc",
                        "state": "open",
                        "since": "{incremental.start_value}",
                    },
                    "incremental": {
                        "cursor_path": "updated_at",
                        "initial_value": pendulum.today()
                        .subtract(days=30)
                        .to_iso8601_string(),
                    },
                },
            },
            {
                "name": "issue_comments",
                "endpoint": {
                    "path": "issues/{resources.issues.number}/comments",
                },
                "include_from_parent": ["id"],
            },
        ],
    }

    yield from rest_api_resources(config)


def load_pokemon() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="rest_api_pokemon",
        destination="duckdb",
        dataset_name="rest_api_data",
    )

    pokemon_source = rest_api_source(
        {
            "client": {
                "base_url": "https://pokeapi.co/api/v2/",
            },
            "resource_defaults": {
                "endpoint": {
                    "params": {
                        "limit": 1000,
                    },
                },
            },
            "resources": [
                "pokemon",
                "berry",
                "location",
            ],
        }
    )

    def check_network_and_authentication() -> None:
        (can_connect, error_msg) = check_connection(
            pokemon_source,
            "not_existing_endpoint",
        )
        if not can_connect:
            pass  # do something with the error message

    check_network_and_authentication()

    load_info = pipeline.run(pokemon_source)
    print(load_info)  # noqa: T201


if __name__ == "__main__":
    load_pokemon()
