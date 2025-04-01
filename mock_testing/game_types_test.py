from unittest.mock import patch, Mock
from utils import get_game_types


# method 1
def test_get_game_types():
    mock_response = Mock()
    mock_response.json.return_value = [
        {"id": "1", "name": "Regular Season"},
        {"id": "2", "name": "Playoffs"},
    ]

    with patch("requests.get", return_value=mock_response) as mock_get:
        result = get_game_types()

    # Assert that requests.get was called with the correct URL
    mock_get.assert_called_once_with(url="https://api.jyablonski.dev/game_typeszxczx")

    # Assert that the function returns the expected result
    assert result == [
        {"id": "1", "name": "Regular Season"},
        {"id": "2", "name": "Playoffs"},
    ]


# method 2
@patch("requests.get")
def test_get_game_types_decorator(mock_get):
    data = [
        {"id": "1", "name": "Regular Season"},
        {"id": "2", "name": "Playoffs"},
    ]
    mock_get.return_value = Mock()
    mock_get.return_value.json.return_value = data

    result = get_game_types()

    mock_get.assert_called_once_with(url="https://api.jyablonski.dev/game_typeszxczx")
    assert result == data


def test_get_game_types_inline():
    with patch(
        "requests.get",
        return_value=Mock(json=lambda: [{"id": "1", "name": "Regular Season"}]),
    ) as mock_get:
        result = get_game_types()

    mock_get.assert_called_once_with(url="https://api.jyablonski.dev/game_typeszxczx")
    assert result == [{"id": "1", "name": "Regular Season"}]


# apparently you need pytest-mock for this to use `mocker`
def test_get_game_types_mocker(mocker):
    # This replaces requests.get with a mock object.
    # Any time requests.get is called in get_game_types, it will
    # now return this mock instead of actually making an HTTP request.
    mock_get = mocker.patch("requests.get")

    # mock_get.return_value represents the fake Response object that requests.get would normally return.
    # mock_get.return_value.json.return_value sets the return value for calling .json() on that response.

    mock_get.return_value.json.return_value = [{"id": "1", "name": "Regular Season"}]

    result = get_game_types()

    mock_get.assert_called_once_with(url="https://api.jyablonski.dev/game_typeszxczx")
    assert result == [{"id": "1", "name": "Regular Season"}]
