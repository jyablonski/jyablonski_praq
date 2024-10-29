import concurrent.futures
import os
import time


# Task that simulates an I/O-bound operation (e.g., waiting for an external resource)
def io_bound_task(task_id: int) -> int:
    print(f"Starting task {task_id}")
    time.sleep(1)  # Simulates a delay (e.g., file I/O, network request)
    print(f"Finished task {task_id}")
    return task_id


# Function to run tasks sequentially (single-threaded)
def run_single_threaded(num_tasks: int) -> None:
    print("Running tasks sequentially (single-threaded)...")
    start_time = time.time()

    for task_id in range(num_tasks):
        io_bound_task(task_id)

    end_time = time.time()
    print(f"Single-threaded execution time: {end_time - start_time:.2f} seconds\n")


# Function to run tasks concurrently using multithreading
def run_multithreaded(num_tasks: int) -> None:
    print("Running tasks concurrently (multithreaded)...")
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        # Submit tasks to the thread pool and execute them in parallel
        futures = [
            executor.submit(io_bound_task, task_id) for task_id in range(num_tasks)
        ]
        # Ensure all tasks are completed
        for future in concurrent.futures.as_completed(futures):
            future.result()  # We could also handle the result here

    end_time = time.time()
    print(f"Multithreaded execution time: {end_time - start_time:.2f} seconds\n")


if __name__ == "__main__":
    num_tasks = 14
    run_single_threaded(num_tasks=num_tasks)
    run_multithreaded(num_tasks=num_tasks)
