import logging
import time

import requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

BASE_URL = "https://api.jyablonski.dev"
ENDPOINTS = ["game_types", "injuries", "transactions", "babyy", ""]


def query_endpoint(url: str) -> list[dict]:
    """Queries an API endpoint and returns the JSON response as a list of dictionaries."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP failures (4xx, 5xx)
        data = response.json()

        if not isinstance(data, list):  # Ensure we get a list
            logging.warning(f"Unexpected response format from {url}")
            return []

        return data
    except requests.Timeout:
        logging.error(f"Timeout while requesting {url}")
    except requests.ConnectionError:
        logging.error(f"Connection error while requesting {url}")
    except requests.HTTPError as e:
        logging.error(f"HTTP error {e.response.status_code} for {url}")
    except requests.JSONDecodeError:
        logging.error(f"No JSON Data available for {url}")

    return []  # Return empty list on failure


def main():
    start_time = time.time()
    for endpoint in ENDPOINTS:
        endpoint_url = f"{BASE_URL}/{endpoint}"
        data = query_endpoint(url=endpoint_url)
        logging.info(f"Received {len(data)} data points from {endpoint_url}")

        # Example: Convert to DataFrame and save (Uncomment if needed)
        # df = pd.DataFrame(data)
        # save_to_s3(df)
    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info(f"Scraping took {elapsed_time:.3f} seconds")


if __name__ == "__main__":
    main()
