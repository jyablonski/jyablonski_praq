from collections.abc import Iterable


def process_lines(lines: Iterable[str]) -> None:
    """Prints each line in uppercase without loading all lines into memory."""
    for line in lines:
        print(line.strip().upper())


# use generator to yield 1 line at a time
def read_large_file(filename: str) -> Iterable[str]:
    with open(filename, "r") as f:
        for line in f:
            yield line


# process the file 1 line at a time
process_lines(read_large_file("huge_file.txt"))  # ✅ Works with the generator

# alternative: This would load all lines into memory at once (not ideal for large files)
with open("huge_file.txt", "r") as f:
    lines = f.readlines()  # ❌ Loads everything into memory
    process_lines(lines)
