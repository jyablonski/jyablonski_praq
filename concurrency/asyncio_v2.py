import asyncio
from datetime import datetime
import time

import aiohttp


async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        await session.get(url)
        async with session.get(url) as response:
            print(f"API Request Status: {response.status} at {datetime.now()}")
            data = await response.text()
            return data


async def trigger_hello_world():
    print(f"Hello, World! Timestamp: {datetime.now()}")


async def io_related(name):
    print(f"{name} started")
    await asyncio.sleep(1)
    print(f"{name} finished")


async def main():
    url = "https://search.worldbank.org/api/v2/wds?format=json&qterm=wind%20turbine&fl=docdt,count"

    # Trigger the GET request
    data = await fetch_data(url)
    await asyncio.gather(
        io_related("first"),
        io_related("second"),
    )
    await trigger_hello_world()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
