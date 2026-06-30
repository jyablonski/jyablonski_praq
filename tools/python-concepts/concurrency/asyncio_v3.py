import asyncio
import dis

import time

# gather is used to run both functions concurrently
# the scrape function is started first and then while we wait for some io output
# we execute the test function


# gather accepts multiple awaitable arguments


# You need to use asyncio.to_thread() for the test() function in the example because
# test() is a synchronous function that you want to run concurrently with the asynchronous
# operation performed by example_async_function(). In asynchronous programming,
# it's important to avoid blocking the event loop with synchronous operations,
# as doing so can degrade performance and responsiveness.
async def example_scrape_function():
    print("Starting asynchronous operation...")
    # Simulate an asynchronous operation with asyncio.sleep
    await asyncio.sleep(2)
    print("My Asynchronous operation is completed")
    return


dis.dis(example_scrape_function())


def test():
    print("ya baby")
    time.sleep(5)
    print("my synchronous bullshit is completed")
    return


async def main():
    print("Calling the asynchronous function...")
    await asyncio.gather(example_scrape_function(), asyncio.to_thread(test))
    print("Both functions just finished, continuing execution ...")


# Run the event loop to execute the asynchronous tasks
asyncio.run(main())
