"""Shared test helpers for creating mock responses."""

from __future__ import annotations

from unittest.mock import MagicMock

import httpx

from helloclub.client import HelloClubClient


def make_response(
    json_data: dict | list | None = None,
    status_code: int = 200,
    headers: dict | None = None,
    content: bytes | None = None,
) -> MagicMock:
    """Create a mock httpx.Response with the given data.

    Reduces boilerplate across all test methods.
    """
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.headers = headers or {}

    if json_data is not None:
        resp.content = content or b'{"mock": true}'
        resp.json.return_value = json_data
    else:
        resp.content = content or b""
        resp.json.return_value = {}

    if status_code < 400:
        resp.raise_for_status = MagicMock()
    else:
        mock_request = MagicMock()
        resp.request = mock_request
        resp.text = str(json_data)
        error = httpx.HTTPStatusError(
            f"HTTP {status_code}", request=mock_request, response=resp
        )
        resp.raise_for_status = MagicMock(side_effect=error)

    return resp


def patch_http(client: HelloClubClient, response: MagicMock) -> MagicMock:
    """Patch the client's internal httpx.Client.request to return a mock response.

    Returns the mock request method for assertion.
    """
    mock_request = MagicMock(return_value=response)
    client._http = MagicMock()
    client._http.request = mock_request
    return mock_request
