import os
import pkg_resources


# run python3 generic_python/python_package_sizes.py
def calc_container(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


dists = [d for d in pkg_resources.working_set]

for dist in dists:
    try:
        path = os.path.join(dist.location, dist.project_name)
        size = calc_container(path)
        if size / 1000 > 1.0:
            print(f"{dist}: {round((size/1000) / 1000, 3)} MB")
            print("-" * 40)
    except OSError:
        "{} no longer exists".format(dist.project_name)
