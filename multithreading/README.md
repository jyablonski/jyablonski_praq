# Python

The `base_python_example.py` file is a synchronous script that executes each request one-by-one and prints some status about the response.

The `multithreading_python_example.py` file is a script which utilizes multithreading to execute each request in its own thread, achieving performance gains

- This is basically a copy of the base script, but it takes advantage of multithreading to trigger multiple requests concurrently instead of synchronously waiting for each response to start the next reqest

The `asyncio_python_example.py` file is a script which utilizes asynchronous code and an event loop to execute each request concurrently on a single thread

- This uses the `aiohttp` library instead of `requests` to execute the HTTP calls
- This has to encapsulate all logic inside a special `handle_endpoint` function to pull the data and write it to S3 afterwards
- This cannot be done in separate functions, because then we wouldn't be able to use async code w/ it.

``` py
async with aiohttp.ClientSession() as session:

    # tasks is a list of tasks that correspond to querying each endpoint. 
    # the important thing here is this has to all be done inside 1 function `handle_endpoint`
    tasks = [
        handle_endpoint(session, f"{BASE_URL}/{endpoint}") for endpoint in ENDPOINTS
    ]
```

- ~3 seconds w/ base version
- ~1 second w/ multithreaded version

Multithreading:

- Limited by number of OS threads that can be efficiently managed

Async:

- Can handle thousands of connections with a single thread using non-blocking I/O.
- Ideal for high-throughput web scraping, API polling, or microservices
- Avoids thread safety issues
- Works with async HTTP libraries like aiohttp, which are designed for non-blocking requests.