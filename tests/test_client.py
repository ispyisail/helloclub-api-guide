"""Unit tests for the HelloClubClient.

All HTTP calls are mocked — no real API requests are made.
"""

from __future__ import annotations

from unittest.mock import patch, MagicMock

import httpx
import pytest

from helloclub.client import HelloClubClient, V1_BASE_URL
from helloclub.exceptions import HelloClubError, RateLimitError


class TestClientInit:
    def test_requires_api_key(self):
        with pytest.raises(HelloClubError, match="API key is required"):
            HelloClubClient(api_key="")

    def test_accepts_valid_key(self):
        client = HelloClubClient(api_key="test-key")
        assert client._api_key == "test-key"
        assert client._base_url == V1_BASE_URL

    def test_custom_base_url(self):
        client = HelloClubClient(api_key="test-key", base_url="https://api-v2.helloclub.com")
        assert client._base_url == "https://api-v2.helloclub.com"


class TestGetEvents:
    def test_returns_events(self, api_key, mock_events):
        client = HelloClubClient(api_key=api_key)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"events": []}'
        mock_resp.json.return_value = {"events": mock_events, "meta": {"total": 2}}
        mock_resp.raise_for_status = MagicMock()

        with patch("httpx.Client") as MockClient:
            MockClient.return_value.__enter__ = MagicMock(return_value=MagicMock(
                request=MagicMock(return_value=mock_resp)
            ))
            MockClient.return_value.__exit__ = MagicMock(return_value=False)
            events = client.get_events(days_ahead=7)

        assert len(events) == 2
        assert events[0]["name"] == "Friday Night Badminton"

    def test_handles_list_response(self, api_key, mock_events):
        client = HelloClubClient(api_key=api_key)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"[]"
        mock_resp.json.return_value = mock_events  # Direct list, not wrapped
        mock_resp.raise_for_status = MagicMock()

        with patch("httpx.Client") as MockClient:
            MockClient.return_value.__enter__ = MagicMock(return_value=MagicMock(
                request=MagicMock(return_value=mock_resp)
            ))
            MockClient.return_value.__exit__ = MagicMock(return_value=False)
            events = client.get_events()

        assert len(events) == 2


class TestGetMembers:
    def test_returns_members(self, api_key, mock_members):
        client = HelloClubClient(api_key=api_key)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"members": []}'
        mock_resp.json.return_value = mock_members
        mock_resp.raise_for_status = MagicMock()

        with patch("httpx.Client") as MockClient:
            MockClient.return_value.__enter__ = MagicMock(return_value=MagicMock(
                request=MagicMock(return_value=mock_resp)
            ))
            MockClient.return_value.__exit__ = MagicMock(return_value=False)
            result = client.get_members()

        assert len(result["members"]) == 2
        assert result["meta"]["total"] == 2


class TestGetAttendees:
    def test_returns_attendees(self, api_key, mock_attendees):
        client = HelloClubClient(api_key=api_key)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"attendees": []}'
        mock_resp.json.return_value = {"attendees": mock_attendees}
        mock_resp.raise_for_status = MagicMock()

        with patch("httpx.Client") as MockClient:
            MockClient.return_value.__enter__ = MagicMock(return_value=MagicMock(
                request=MagicMock(return_value=mock_resp)
            ))
            MockClient.return_value.__exit__ = MagicMock(return_value=False)
            attendees = client.get_attendees(event_id="evt-001")

        assert len(attendees) == 1
        assert attendees[0]["firstName"] == "Jane"


class TestCreateMember:
    def test_returns_member_id(self, api_key):
        client = HelloClubClient(api_key=api_key)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"id": "new-mem-001"}'
        mock_resp.json.return_value = {"id": "new-mem-001"}
        mock_resp.raise_for_status = MagicMock()

        with patch("httpx.Client") as MockClient:
            MockClient.return_value.__enter__ = MagicMock(return_value=MagicMock(
                request=MagicMock(return_value=mock_resp)
            ))
            MockClient.return_value.__exit__ = MagicMock(return_value=False)
            member_id = client.create_member("Jane", "Smith", "female")

        assert member_id == "new-mem-001"

    def test_raises_on_missing_id(self, api_key):
        client = HelloClubClient(api_key=api_key)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"{}"
        mock_resp.json.return_value = {}
        mock_resp.raise_for_status = MagicMock()

        with patch("httpx.Client") as MockClient:
            MockClient.return_value.__enter__ = MagicMock(return_value=MagicMock(
                request=MagicMock(return_value=mock_resp)
            ))
            MockClient.return_value.__exit__ = MagicMock(return_value=False)
            with pytest.raises(HelloClubError, match="did not return a member ID"):
                client.create_member("Jane", "Smith", "female")


class TestErrorHandling:
    def test_4xx_raises_immediately(self, api_key):
        client = HelloClubClient(api_key=api_key)
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.text = "Not found"
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not found", request=MagicMock(), response=mock_resp
        )

        with patch("httpx.Client") as MockClient:
            MockClient.return_value.__enter__ = MagicMock(return_value=MagicMock(
                request=MagicMock(return_value=mock_resp)
            ))
            MockClient.return_value.__exit__ = MagicMock(return_value=False)
            with pytest.raises(HelloClubError, match="API error 404"):
                client.get_events()

    def test_rate_limit_raises_after_retries(self, api_key):
        client = HelloClubClient(api_key=api_key, max_retries=1)
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_resp.headers = {"Retry-After": "10"}
        mock_resp.content = b'{"error": "rate limit"}'

        with patch("httpx.Client") as MockClient:
            MockClient.return_value.__enter__ = MagicMock(return_value=MagicMock(
                request=MagicMock(return_value=mock_resp)
            ))
            MockClient.return_value.__exit__ = MagicMock(return_value=False)
            with pytest.raises(RateLimitError, match="Rate limit exceeded"):
                client.get_events()


class TestExceptions:
    def test_hello_club_error(self):
        err = HelloClubError("test error")
        assert str(err) == "test error"

    def test_rate_limit_error_with_retry_after(self):
        err = RateLimitError("rate limited", retry_after=30)
        assert err.retry_after == 30
        assert str(err) == "rate limited"

    def test_rate_limit_error_without_retry_after(self):
        err = RateLimitError("rate limited")
        assert err.retry_after is None

    def test_rate_limit_is_hello_club_error(self):
        err = RateLimitError("test")
        assert isinstance(err, HelloClubError)
