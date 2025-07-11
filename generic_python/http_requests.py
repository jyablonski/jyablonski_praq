from typing import Any
import requests


class InvalidJSONError(ValueError):
    """Raised when the response body is not valid JSON."""


class KeyNotFoundError(KeyError):
    """Raised when the expected key is absent from the JSON payload."""


def fetch_data(
    url: str,
    key_to_check: str,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 10,
) -> Any:
    """Fetch JSON from an API endpoint and return the value of a required key.

    Args:
        url: Fully-qualified HTTP(S) endpoint.

        key_to_check: Key that *must* be present in the final JSON response.

        params: Optional query-string parameters.

        headers: Optional request headers.

        timeout: Maximum seconds to wait for the server to respond.

    Returns:
        The value associated with `key_to_check` in the JSON payload.

    Raises:
        requests.exceptions.Timeout: Request exceeded `timeout`.

        requests.exceptions.ConnectionError: DNS failure, refused connection, etc.

        requests.exceptions.HTTPError: Non-2xx HTTP status.

        InvalidJSONError: Response body could not be decoded as JSON.

        KeyNotFoundError: `key_to_check` was not found in the decoded JSON.

        requests.exceptions.RequestException: Any other Requests-level error.
    """
    try:
        response: requests.Response = requests.get(
            url, params=params, headers=headers, timeout=timeout
        )
        response.raise_for_status()  # may raise HTTPError
        try:
            payload = response.json()
        except ValueError as exc:  # includes simplejson errors if installed
            raise InvalidJSONError("Response body is not valid JSON") from exc

        if key_to_check not in payload:
            raise KeyNotFoundError(
                f"Key '{key_to_check}' not found in response from {url}"
            )

        return payload

    except (
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError,
        requests.exceptions.HTTPError,
        requests.exceptions.RequestException,
        InvalidJSONError,
        KeyNotFoundError,
    ):
        raise
