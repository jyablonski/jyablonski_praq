import pytest
from pytest_mock import MockerFixture
import requests

from crypto.api_scrape import get_bitcoin_information


# When you use mocker.Mock() from pytest_mock, you can configure it to behave like
# any Python object, setting attributes and defining return values as needed.
def test_get_bitcoin_information(
    mocker: MockerFixture, valid_bitcoin_json_data: dict[str, str]
):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = valid_bitcoin_json_data

    mocker.patch("crypto.api_scrape.requests.get", return_value=mock_response)

    df = get_bitcoin_information(url="http://example.com/bitcoin")

    assert len(df) == 1
    assert df.columns == ["symbol", "open", "high", "low", "close", "bid", "ask"]
    assert df["open"][0] == 100.91999816894531


# def test_get_bitcoin_information_url_error(
#     mocker: MockerFixture, valid_bitcoin_json_data: dict[str, str]
# ):
#     mock_response = mocker.Mock()
#     mock_response.status_code = 403
#     mock_response.json.return_value = valid_bitcoin_json_data

#     mocker.patch("crypto.api_scrape.requests.get", return_value=mock_response)

#     # Call the function under test
#     with pytest.raises(requests.RequestException):
#         get_bitcoin_information(url="http://example.com/bitcoin")

#     # Ensure that raise_for_status was called
#     mock_response.raise_for_status.assert_called_once()


def test_get_bitcoin_information_json_error(
    mocker: MockerFixture, invalid_bitcoin_json_data: dict[str, str]
):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = invalid_bitcoin_json_data

    mocker.patch("crypto.api_scrape.requests.get", return_value=mock_response)

    df = get_bitcoin_information(url="http://example.com/bitcoin")

    assert len(df) == 5
