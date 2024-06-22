import json

import polars as pl
import requests

# https://docs.gemini.com/rest-api/#ticker
BASE_URL = "https://api.gemini.com/v2"


def get_bitcoin_information(url: str) -> pl.DataFrame:
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        print(f"Queried {url}, got {response.status_code} Code")
    except requests.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
        raise e

    try:
        btc_data = response.json()
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
        raise e

    btc_data.pop("changes", None)

    df = pl.DataFrame(
        data=btc_data,
        schema_overrides={
            "open": pl.Float32,
            "high": pl.Float32,
            "low": pl.Float32,
            "close": pl.Float32,
            "bid": pl.Float32,
            "ask": pl.Float32,
        },
    )

    print(f"Extracted {len(df)} rows from Bitcoin Ticker")
    return df


if __name__ == "__main__":
    df = get_bitcoin_information(url=f"{BASE_URL}/ticker/btcusd")
