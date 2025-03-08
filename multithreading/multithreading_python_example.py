import logging
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

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

    # create a list of full api urls that we need to query
    urls = [f"{BASE_URL}/{endpoint}" for endpoint in ENDPOINTS]

    # Start a Thread Pool Executor
    # ThreadPoolExecutor is a Python class that manages a pool of worker threads.
    # this means up to 5 threads will run concurrently, so at most 5 requests can be ran in parallel
    # when the `with` block exits, the executor shuts down and threads will be finished executing
    with ThreadPoolExecutor(max_workers=5) as executor:
        # This creates a dictionary that maps each future (a running thread) to its corresponding URL.
        # This immediately starts the API request but does not block execution.
        future_to_url = {executor.submit(query_endpoint, url): url for url in urls}

        # the result is a dictionary where the key is a future obj, and the value is the api url

        # Process Completed API Calls in Order of Completion
        # `as_completed(future_to_url)` is an iterator that yields futures as they complete.
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                # future.result() retrieves the return value of query_endpoint(url).
                data = future.result()
                logging.info(f"Received {len(data)} data points from {url}")

                # in a real world example you probably want to write this to s3 afterwards
                # write_to_s3(df=data)
            except Exception as e:
                logging.error(f"Error processing {url}: {e}")

    elapsed_time = time.time() - start_time
    logging.info(f"Scraping took {elapsed_time:.3f} seconds")


if __name__ == "__main__":
    main()
