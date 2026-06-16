# Async

At its core, async is about making progress on multiple pieces of work that spend most of their time *waiting* (on I/O — network, disk, a database) without blocking. It's concurrency on a single thread, not parallelism: there's one thread the whole time, and tasks take turns at their suspension points. In Python this is provided by the `asyncio` library, built around coroutines.

You define coroutines with `async def`, and use `await` to yield control back to the event loop at a suspension point (like waiting for I/O). While one task is parked at an `await`, the loop runs others — that overlap is the entire benefit. `await` only yields if the awaited thing actually suspends, and it's only legal inside an `async def`.

`await` must target an *awaitable*: a coroutine, a Task, or a Future. The event loop schedules these and resumes each one when its result is ready.

> Async helps with I/O-bound work (lots of waiting). It does not help with CPU-bound work (genuine computation) — for that, use multiprocessing. A coroutine that does heavy CPU work with no `await` hogs the loop and stalls everything.

## Core APIs

- `asyncio.run()` — the bridge from synchronous code into the async world. Creates an event loop, runs the given coroutine to completion, then closes the loop. Call it from top-level sync code; never from inside a running loop (that raises an error). You *can* call it more than once sequentially, as the TaskGroup example below does.
- `asyncio.gather()` — runs multiple coroutines concurrently and waits for all of them, returning results in the order passed in (not finish order). Use for a fixed batch where you want all results together. Note: by default, if one task raises, the exception propagates but the *others keep running* in the background — pass `return_exceptions=True` to collect outcomes instead of raising.
- `asyncio.create_task()` — schedules a coroutine to run in the background *now* and returns a `Task` handle. You don't get the result until you `await` the task or read `.result()` after it's done. Two gotchas: keep a reference to the task (a loose task can be garbage-collected mid-flight), and an exception in a task you never await can be silently swallowed.
- `asyncio.as_completed()` — takes an iterable of awaitables and yields them in finish order, regardless of start order. Each iteration gives you an awaitable you must `await` to get its value. Use when you want to process each result the instant it's ready instead of waiting for the slowest.
- `asyncio.TaskGroup()` *(3.11+, recommended default)* — a context manager for a batch of tasks. You can't exit the `async with` block until every task resolves. You hold the handles and read `.result()` after the block (safe without `await`, since completion is guaranteed by then). Collection order is whatever order *you* read the handles — only finish order is nondeterministic. Advantages over `gather`: if one task fails, the rest are cancelled automatically, and failures surface as an `ExceptionGroup` caught with `except*`.

### Choosing between them

- Fixed batch, want all results together, want cancel-on-failure safety → `TaskGroup`
- Fixed batch, just want an auto-collected ordered list, don't need cancel-on-failure → `gather`
- Long-lived background work that outlives the current scope → `create_task`
- Want to handle each result the moment it lands → `as_completed`

## Code Example — gather + manual collection

```py
import asyncio
import time

# A stand-in for a real network call. asyncio.sleep is the non-blocking
# equivalent of time.sleep -- it HAS a suspension point, so it yields to
# the loop instead of freezing it. In real code this is where an
# `async with session.get(url)` would go.
async def fetch(name, delay):
    start = time.perf_counter()
    print(f"  [{time.perf_counter() - START:5.2f}s] {name} started")
    await asyncio.sleep(delay)          # <-- the yield point
    elapsed = time.perf_counter() - start
    print(f"  [{time.perf_counter() - START:5.2f}s] {name} done after {elapsed:.2f}s")
    return f"{name}:result"


async def main():
    # Kick off all three concurrently and wait for the whole batch.
    # gather RETURNS a new list -- one entry per coroutine, in the order
    # we passed them in (NOT the order they finished).
    print("gather: starting all three at once")
    results = await asyncio.gather(
        fetch("A", 1.0),
        fetch("B", 2.0),
        fetch("C", 1.5),
    )
    # gather results (positional order): ['A:result', 'B:result', 'C:result']
    print(f"gather results (positional order): {results}\n")

    # Total wall-clock time will be ~2.0s (the slowest one), not 4.5s,
    # because the three sleeps overlap.

    # ---------------------------------------------------------------
    # The "build up a list manually" pattern. This is what gather saves
    # you from writing. Here YOU own the list and append to it -- and the
    # ordering is finish-dependent, which is exactly why gather is handy.
    # ---------------------------------------------------------------
    print("manual: scheduling tasks and collecting as they finish")
    manual_results = []
    tasks = [
        asyncio.create_task(fetch("X", 1.0)),
        asyncio.create_task(fetch("Y", 0.5)),
        asyncio.create_task(fetch("Z", 1.5)),
    ]
    for coro in asyncio.as_completed(tasks):
        result = await coro  # resolves in FINISH order: Y, X, Z
        manual_results.append(result)

    # manual results (finish order): ['Y:result', 'X:result', 'Z:result']
    print(f"manual results (finish order): {manual_results}")


START = time.perf_counter()

if __name__ == "__main__":
    # Bridge from sync into async: starts the loop, runs main() to
    # completion, then closes the loop.
    asyncio.run(main())
```

## Code Example — TaskGroup (modern default)

```py
import asyncio
import time


async def fetch(name, delay):
    print(f"  [{time.perf_counter() - START:5.2f}s] {name} started")
    await asyncio.sleep(delay)
    print(f"  [{time.perf_counter() - START:5.2f}s] {name} done")
    return f"{name}:result"


async def main():
    # The TaskGroup is an async context manager. You create tasks INSIDE
    # the `async with` block. When the block exits, it waits for every
    # task to finish before continuing -- you don't await them yourself.
    print("TaskGroup: scheduling tasks")
    async with asyncio.TaskGroup() as tg:
        task_a = tg.create_task(fetch("A", 1.0))
        task_b = tg.create_task(fetch("B", 2.0))
        task_c = tg.create_task(fetch("C", 1.5))
        # <-- execution pauses at the END of this block until A, B, C all finish

    # Past this line, the group is guaranteed complete. Now it's safe to
    # read results synchronously with .result() -- no await needed,
    # because completion is already guaranteed by the block exiting.
    # Collection order is whatever order WE read the handles (input order here).
    results = [task_a.result(), task_b.result(), task_c.result()]
    print(f"results: {results}\n")


# --- What happens when a task fails ---------------------------------
async def flaky(name, delay, boom=False):
    await asyncio.sleep(delay)
    if boom:
        raise ValueError(f"{name} blew up")
    print(f"  {name} finished fine")
    return name


async def failure_demo():
    print("Failure demo: one task raises")
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(flaky("X", 0.5, boom=True))   # fails fast
            tg.create_task(flaky("Y", 5.0))              # gets CANCELLED
            tg.create_task(flaky("Z", 5.0))              # gets CANCELLED
    except* ValueError as eg:                            # note: except* (ExceptionGroup)
        for exc in eg.exceptions:
            print(f"  caught: {exc}")
    print("  (Y and Z were cancelled automatically -- they never finished)")


START = time.perf_counter()

if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(failure_demo())
```

## Version notes (3.13 / 3.14)

The `TaskGroup` API is stable since 3.11, but two things matter for current best practice:

- 3.13 hardened cancellation — better handling of simultaneous internal/external cancellations and correct cancellation-count preservation. No code changes needed; it's just more correct under edge cases.
- 3.14 (released Oct 2025):
  - `eager_start` — `create_task` now forwards arbitrary kwargs, including `eager_start=True`, which runs the coroutine synchronously up to its first `await` at creation time instead of waiting for the next loop tick.
  - Live introspection — `python -m asyncio ps <PID>` lists a running process's tasks, and `pstree` shows the await hierarchy, without modifying code. Plus `capture_call_graph()` / `print_call_graph()` in code.
  - The event loop is now thread-safe in free-threaded builds (previously you couldn't run asyncio off the main thread there).
- Looking ahead (3.15): a `TaskGroup.cancel()` method for clean external cancellation of a whole group, replacing today's awkward raise-a-sentinel-exception workaround.
