import logging
import time
import asyncio
import aiohttp
import boto3
import json
from botocore.exceptions import NoCredentialsError

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

BASE_URL = "https://api.jyablonski.dev"
ENDPOINTS = ["game_types", "injuries", "transactions", "babyy", ""]
S3_BUCKET_NAME = "your-s3-bucket-name"  # Replace with your bucket name
S3_PREFIX = "api_data/"  # Optional prefix for your S3 keys

# Initialize the S3 client
s3_client = boto3.client("s3")


# async def makes this function asynchronous
# It takes an aiohttp.ClientSession as an argument to reuse connections efficiently.
async def query_endpoint(session: aiohttp.ClientSession, url: str) -> list[dict]:
    """Queries an API endpoint asynchronously and returns the JSON response as a list of dictionaries."""
    try:
        async with session.get(url, timeout=10) as response:
            response.raise_for_status()  # Raise an error for HTTP failures (4xx, 5xx)
            data = await response.json()

            if not isinstance(data, list):  # Ensure we get a list
                logging.warning(f"Unexpected response format from {url}")
                return []

            return data
    except asyncio.TimeoutError:
        logging.error(f"Timeout while requesting {url}")
    except aiohttp.ClientConnectionError:
        logging.error(f"Connection error while requesting {url}")
    except aiohttp.ClientResponseError as e:
        logging.error(f"HTTP error {e.status} for {url}")
    except aiohttp.ContentTypeError:
        logging.error(f"No JSON Data available for {url}")

    return []  # Return empty list on failure


async def write_to_s3(url: str, data: list) -> None:
    """Uploads data to S3 after the API call is successful."""
    try:
        # Create a unique key for the S3 object (you can customize this format)
        s3_key = f"{S3_PREFIX}{url.split('/')[-1]}.json"

        # Convert the data to JSON string
        json_data = json.dumps(data)

        # Upload the data to S3
        s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=s3_key, Body=json_data)

        logging.info(f"Successfully uploaded data to S3: {s3_key}")
    except NoCredentialsError:
        logging.error("AWS credentials not found.")
    except Exception as e:
        logging.error(f"Error uploading data to S3: {e}")


async def handle_endpoint(session: aiohttp.ClientSession, url: str) -> None:
    """Handles querying the API and uploading data to S3."""
    data = await query_endpoint(session, url)
    print(data)

    # If data is not empty, upload it to S3
    # if data:
    #     await write_to_s3(url, data)


async def main():
    start_time = time.time()

    # opens an HTTP session to make requests. It’s used within an async
    # `with` block to ensure the session is properly closed when done.
    async with aiohttp.ClientSession() as session:
        # tasks is a list of tasks that correspond to querying each endpoint.
        # the important thing here is this has to all be done inside 1 function `handle_endpoint`
        tasks = [
            handle_endpoint(session, f"{BASE_URL}/{endpoint}") for endpoint in ENDPOINTS
        ]

        # this runs all tasks concurrently
        # await ensures that the script waits for all of these tasks to finish
        # before moving to the next line of code.
        await asyncio.gather(*tasks)

    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info(f"Scraping took {elapsed_time:.3f} seconds")


if __name__ == "__main__":
    # asyncio.run(main()) runs the asynchronous main function,
    # starting the event loop and handling the asynchronous operations.
    asyncio.run(main())
