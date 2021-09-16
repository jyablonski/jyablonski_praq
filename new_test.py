""" Example of pytest module """

from new.py import total

def test_total_empty() -> None:
    assert total([]) == 0.0