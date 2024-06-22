import socket

import pytest


def guard(*args, **kwargs):
    raise Exception("you're using the internet hoe")


socket.socket = guard


@pytest.fixture(scope="function")
def valid_bitcoin_json_data() -> dict:
    return {
        "symbol": "BTCUSD",
        "open": "100.92",
        "high": "100.27",
        "low": "100.25",
        "close": "100.71",
        "changes": [
            "100.5",
            "100.92",
        ],
        "bid": "100.49",
        "ask": "100.58",
    }


@pytest.fixture(scope="function")
def invalid_bitcoin_json_data() -> dict:
    return {"hello": "world"}
