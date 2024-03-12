import argparse
import importlib
import os
import sys


def _always_run() -> frozenset[str]:
    ret = [
        "python_path_gahbage/print_test.py",
    ]
    return frozenset(ret)


# python3 python_path_gahbage/main.py
# python3 generic_python/main.py --test 1
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", default=True)
    parser.add_argument("--test")
    args = parser.parse_args()

    files = _always_run()
    for fname in files:
        # Import the print_test module
        importlib.import_module("print_test")
        assert os.path.exists(fname), fname

    if not args.all:
        print("didnt run with --all mfer")
        return 1

    print("hello run before")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
