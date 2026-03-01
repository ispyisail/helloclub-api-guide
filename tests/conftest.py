"""Shared fixtures and mock responses for Hello Club client tests."""

from __future__ import annotations

from unittest.mock import MagicMock

import httpx
import pytest

from helloclub.client import HelloClubClient


@pytest.fixture()
def api_key() -> str:
    return "test-api-key-123"


@pytest.fixture()
def client(api_key) -> HelloClubClient:
    """Pre-configured client for testing."""
    return HelloClubClient(api_key=api_key)


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


@pytest.fixture()
def mock_events() -> list[dict]:
    return [
        {
            "id": "evt-001",
            "name": "Friday Night Badminton",
            "startDate": "2026-03-06T18:00:00Z",
            "endDate": "2026-03-06T20:00:00Z",
            "activity": {"name": "Badminton Hall", "id": "act-1"},
            "categories": [{"name": "Senior", "id": "cat-1"}],
            "numAttendees": 12,
            "maxAttendees": 24,
        },
        {
            "id": "evt-002",
            "name": "Saturday Social",
            "startDate": "2026-03-07T14:00:00Z",
            "endDate": "2026-03-07T16:00:00Z",
            "activity": {"name": "Badminton Hall", "id": "act-1"},
            "categories": [],
            "numAttendees": 8,
            "maxAttendees": 20,
        },
    ]


@pytest.fixture()
def mock_members() -> list[dict]:
    return [
        {
            "id": "mem-001",
            "firstName": "Jane",
            "lastName": "Smith",
            "email": "jane@example.com",
            "gender": "female",
        },
        {
            "id": "mem-002",
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "gender": "male",
        },
    ]


@pytest.fixture()
def mock_attendees() -> list[dict]:
    return [
        {
            "id": "att-001",
            "firstName": "Jane",
            "lastName": "Smith",
            "member": {"id": "mem-001", "firstName": "Jane", "lastName": "Smith"},
            "guest": None,
            "isMember": True,
            "isGuest": False,
            "hasAttended": True,
            "isPaid": True,
            "rule": {"type": "fee", "fee": 15.0},
            "hasMembershipRule": False,
        },
    ]
