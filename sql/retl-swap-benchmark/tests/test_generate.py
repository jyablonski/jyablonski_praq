from benchmark.generate import generate_rows, generate_row
from benchmark.config import Config


def test_generate_row_returns_correct_number_of_fields():
    row = generate_row(user_id=1, fake=None, rng=__import__("random").Random(42))
    # user_id + 20 analytics columns = 21 fields
    assert len(row) == 21


def test_generate_row_user_id_is_first_field():
    row = generate_row(user_id=999, fake=None, rng=__import__("random").Random(42))
    assert row[0] == 999


def test_generate_rows_yields_correct_count():
    config = Config(row_count=100, seed=42)
    rows = list(generate_rows(config))
    assert len(rows) == 100


def test_generate_rows_deterministic_with_seed():
    config = Config(row_count=50, seed=42)
    rows_a = list(generate_rows(config))
    rows_b = list(generate_rows(config))
    assert rows_a == rows_b


def test_generate_rows_user_ids_are_sequential():
    config = Config(row_count=100, seed=42)
    rows = list(generate_rows(config))
    user_ids = [r[0] for r in rows]
    assert user_ids == list(range(1, 101))
