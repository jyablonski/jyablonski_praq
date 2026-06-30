from datetime import datetime, timezone
import logging

import requests
from requests.adapters import HTTPAdapter, Retry
import polars as pl
import s3fs

HUBSPOT_URL = "https://hubspot.com/v1/contacts"
REQUIRED_COLS = ["col1", "col2", "col3"]

# pull 10 records at a time - this is often called `limit` as well
PAGE_SIZE = 10

# assuming we know this in advance for demonstration, but this is often returned from the API
# so we know when to continue or stop pulling data
TOTAL_PAGES = 10

# {
#   "results": [...],         // the current page of data
#   "total": 235,             // total records available
#   "page": 1,                // current page number
#   "pageSize": 10,           // size per page (requested or default)
#   "totalPages": 24,         // total pages available (optional)
#   "nextPage": 2,            // next page number (optional)
#   "nextCursor": "abc123"    // cursor token for next page (optional)
# }


def get_secret(secret_name: str) -> str:
    logging.info(f"Retrieving Secret {secret_name} from Session Parameter Store")
    return secret_name


# use a session when you're going to make a minimum of 2 requests or more
def create_session(api_key: str) -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )

    # replace the default HTTPS adapter with this one to handle retries
    # for any `https://` request we make
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.headers.update({"Authorization": api_key})
    return session


def get_hubspot_contacts(url: str, api_key: str) -> pl.DataFrame:
    # create 1 session to handle all requests
    session = create_session(api_key)
    all_frames = []

    for page in range(1, TOTAL_PAGES + 1):
        params = {"page": page, "pageSize": PAGE_SIZE}
        logging.info(f"Fetching page {page} of {TOTAL_PAGES} from HubSpot")

        resp = session.get(url, params=params, timeout=30)
        resp.raise_for_status()

        try:
            json_data = resp.json()
        except ValueError:
            logging.error(f"Invalid JSON on page {page}")
            raise

        missing_cols = [col for col in REQUIRED_COLS if col not in json_data]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols} on page {page}")

        df = pl.DataFrame(json_data)
        df = df.with_columns(pl.lit(datetime.now(timezone.utc)).alias("__created_at"))
        all_frames.append(df)

    # combine data from all 10 pages
    if not all_frames:
        raise ValueError("No data retrieved from API")

    return pl.concat(all_frames)


def write_df_to_s3(df: pl.DataFrame, s3_uri: str, compression: str = "snappy") -> None:
    fs = s3fs.S3FileSystem()
    logging.info(f"Writing Parquet File to {s3_uri}")
    with fs.open(s3_uri, mode="wb") as f:
        df.write_parquet(f, compression=compression)


def main():
    api_key = get_secret("HUBSPOT_KEY")
    contacts = get_hubspot_contacts(url=HUBSPOT_URL, api_key=api_key)
    write_df_to_s3(df=contacts, s3_uri="s3://my-bucket/hubspot_contacts.parquet")


if __name__ == "__main__":
    main()
