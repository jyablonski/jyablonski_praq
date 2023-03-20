import re
from datetime import datetime, timedelta
from functools import reduce
from typing import List


class RegexFail(Exception):
    pass


class InvalidFileType(Exception):
    pass


# great use of this is to assert whether a vendor or 3rd party provider is dumping files off in the correct format you're expecting.
def validate_file(filename: str, pattern: List[re.Pattern]) -> bool:
    """
    Regex Function that iteratively loops through a list of regex patterns to validate a file name.

    Args:
        filename (str): The Filename to be checked

        pattern (list[re.Pattern]): The Regex Pattern individually separated out in a list.

    Returns:
        True or False depending on whether the filename meets the regex pattern or not.
    """

    def _reductor(fn, rx):
        if fn is None:
            return None
        mo = rx.match(fn)
        if mo is None:
            print(f"File name mismatch: got {fn}, expected {rx.pattern}")

            # this compares the current string being checked to the regex rule being checked.
            raise RegexFail(f"File name mismatch: got {fn}, expected {rx.pattern}")
        # proceed with the remainder of the string where the loop left off
        return fn[mo.end() :]

    if not filename.endswith(("json", "csv", "parquet")):
        raise InvalidFileType(
            f"{filename} has an invalid file type: expecting json, csv, or parquet"
        )

    validate_obj = lambda fn: reduce(_reductor, pattern, fn) is not None
    is_filename_correct = validate_obj(filename)

    return is_filename_correct


# old way - not ideal bc it's 1 massive regex blob, hard to read, and debugging is difficult
pattern = re.compile(
    r"\w+\/\w+\/\w+\/\d{4}-\d{2}\/(\w+)_\d{4}-\d{2}-\d{2}.(csv|parquet|json|zip)$"
)

# split the pattern into individual bits so we can track which ones passed and which ones failed.
# bc we search text left to right - we can use this to identify the exact regex bits that caused a failure.
pattern = [
    re.compile(r"\w+\/"),
    re.compile(r"\w+\/"),
    re.compile(r"\w+\/"),
    re.compile(r"\d{4}-\d{2}\/"),
    re.compile(r"(\w+)_\d{4}-\d{2}-\d{2}"),
    re.compile(r".(csv|parquet|json|zip)$"),
]

string1 = "jacobsbucket97/sample_files/raw/2022-01/sample_files_2022-02-01.json"  # pass
string2 = "jacobsbucket97/sample_files/raw/2022-01/sample_files_2022-02-01.csv"  # pass
string3 = (
    "jacobsbucket97/sample_files/raw/2022-01/sample_files_2022-02-01.parquet"  # pass
)
string4 = "jacobsbucket97/sample_files/raw/2022-01/sample_files_2022-02-01.gz"  # fail, bc of .gz
string5 = "jacobsbucket97/sample_files/raw/2022-01/sample_files_2022-02-01.zip"  # pass
string6 = "jacobsbucket97/sample_files/raw/2022-01/sample_files_2022-02.parquet"  # fail, bc of date
