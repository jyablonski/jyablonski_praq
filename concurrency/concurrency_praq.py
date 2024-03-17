import multiprocessing
import os
from threading import Thread


# create a coroutine function
async def hello_world():
    print("hello world")
    return


# just creates the coroutine object of type `coroutine`.  doesnt actually run it
coro = hello_world()

# actually run it
await coro


def cpu_count() -> int:
    try:
        # On systems that support it, this will return a more accurate count of
        # usable CPUs for the current process, which will take into account
        # cgroup limits
        return len(os.sched_getaffinity(0))
    except AttributeError:
        pass

    try:
        return multiprocessing.cpu_count()
    except NotImplementedError:
        return 1


cpu_count()


# create a coroutine function
def hello_world():
    print("hello world")
    return


# create a thread
thread = Thread(target=hello_world())
# start the new thread
thread.start()
