[Article Link](https://realpython.com/python-concurrency/)
[Stackoverflow](https://stackoverflow.com/questions/27435284/multiprocessing-vs-multithreading-vs-asyncio)
[Informative Stackoverflow](https://stackoverflow.com/questions/60236745/is-it-true-that-in-multiprocessing-each-process-gets-its-own-gil-in-cpython-h)

# Concurrency
Concurrency means simultaneous occurrence.  Python can achieve this in multiple ways for different use cases.  Concurrency can mean starting 2 tasks at the same time, but this does not mean they're both running in parallel.

Concurrency solves 2 main problems: CPU-bound and I/O-bound issues which slow down our programs.
    * I/O problems cause the program to slow down because you're waiting for IO from some external/remote resource.  Typically file system or network connections, you actually spend more time waiting for these than the time your program is executing its processing code.
      * Solution is typically threading or Asyncio.
    * CPU-bound problems are where the speed of your program is limited by the speed of your CPU.
      * Solution is typically multiprocessing.

# Parallelism
Using multiple CPU Cores available on your PC to spawn multiple processes.

## Threading
Runs on a single processor and only one at a time.  The OS knows about all of the threads and can interrupt it at any time to start doing something with another thread called `pre-emptive multitasking`.

In `threading_prac_async.py`, to turn a synchronous program into async you have to add in `import concurrent.futures` and `import threading` and create a `concurrent.futures.ThreadPoolExecutor(max_workers=5)` pool of threads to use, each running concurrently.  The executor controls how and when each of the threads will run.  The context manager (`with x as executor:`) creates and destroys these resources for you.
    * The `.map` method is available to run the passed in function, in this case `download_site`.
    * The executor does a ton of shit for you, so you don't have to call `thread.start`, `thread.stop` etc.
    * Each thread is creating its own `requests.Session()` object, which the creators of requests mention in their documentation.
    * There is a `threading.lock` to ensure only one thread can access a block of code or a bit of memory at a time.
    * `thread_local = threading.local()` called at the top looks like a global object, but it is actually specific to each individual thread.
    * There's overhead with creating threads and having to wait on the starting and stopping of threads.  If you have 20 urls, it's not necessarily best to use 20 threads.  Might be best to use somewhere between 5-10 instead for maximum time savings.
    * The example took ~15 seconds without threading and ~3.7 seconds with threading.

The downside to threading here is it can cause small, cumbersome bugs that are hard to track and debug.  You don't have direct control over the underlying processes. 

## Asyncio
Runs on a single processor and only one at a time, similar to threading.  Uses `cooperative multitasking` with each task announcing when they are ready to be switched out.  You have to write code in a special way in order to accomodate this, but the benefit is that you're controlling that "switching out" process.

A single python object, the `event loop`, controls how and when each task gets run.  It knows the state each task is in.  The ready state is when a task has some work to do and is ready to be run, and the waiting state means the task is waiting for some external thing to finish like a network operation.  It picks the task that has been waiting the longest to run and then runs that.

Tasks never give up control without intentionally doing so and they never get interrupted mid-operation.  This makes it easier to share resources than threading.  

`await` is the magic that allows the task to hand control back to the event loop.  `aysnc` tells python that the function has to use `await` somewhere.  Context managers can still be used.

There's complexity with managing the interaction between event loops and tasks.

All tasks share session in `asyncio_prac.py` because they all run on the same thread.  Even with less threads this asyncio alternative performs better than the threading one above.  However, there is no executor like in threading so there's a bit more work to get this set up and to manage.

To use `asyncio` properly, the libraries you use need to have special async libraries to take advantage of the technique.  Another problem is if one task has an issue or starts taking forever, there's no way for the event loop to break in if the task doesn't hand control back to it.

## Multiprocessing
Using all of the CPU Cores available on your PC.  Python does this by literally creating new processes, so like 8 different Python programs running at once and each have their own Python interpreter.  Each task can then run on their own core at the same time, but complication arise from doing this.

The above processes only used 1 CPU Core on your computer because of the Global Interpreter Lock, or GIL.  Multiprocessing allows you to use all cores and break this GIL.

The `multiprocessing` module handles the communication process between the main script being run and the pool of cpu core tasks it generates.  It will automatically determine the number of CPU cores in your computer and use that.

Using all your cores for certain tasks will not make things faster, because there is network overhead of those extra resources having to communicate back to the main task and also having to tear those resources down.

These tasks cannot share the `requests.session()` object, so they each have to create their own.  


## Final Notes
Threading and Async will not speed up CPU-bound problems.  You're waiting for the CPU to crank away at completing the process.  Threading and Async use the same exact CPU Core, so if you apply these techniques to a CPU bound problem it will be slower because now you have the overhead of setting all of the extra threading/async resources up.