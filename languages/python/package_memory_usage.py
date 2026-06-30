from memory_profiler import profile
from datetime import datetime

# run -- python3 generic_python/package_memory_usage.py -- to see how much memory is being used by each package


@profile
def find_import_memory_usage():

    pass


print(f"hello world at {datetime.now()}")
find_import_memory_usage()
