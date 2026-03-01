"""Unit tests for the HelloClubClient.

All HTTP calls are mocked — no real API requests are made.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import httpx
import pytest

from helloclub.client import HelloClubClient, V1_BASE_URL
from helloclub.exceptions import HelloClubError, RateLimitError
from tests.conftest import make_response, patch_http


# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------


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

    def test_context_manager(self):
        with HelloClubClient(api_key="test-key") as client:
            assert client._api_key == "test-key"


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------


class TestGetEvents:
    def test_returns_events(self, client, mock_events):
        resp = make_response({"events": mock_events, "meta": {"total": 2}})
        patch_http(client, resp)
        events = client.get_events(days_ahead=7)
        assert len(events) == 2
        assert events[0]["name"] == "Friday Night Badminton"

    def test_handles_list_response(self, client, mock_events):
        resp = make_response(mock_events)
        patch_http(client, resp)
        events = client.get_events()
        assert len(events) == 2

    def test_get_single_event(self, client, mock_events):
        resp = make_response(mock_events[0])
        mock_req = patch_http(client, resp)
        event = client.get_event("evt-001")
        assert event["id"] == "evt-001"
        mock_req.assert_called_once()
        assert "/event/evt-001" in mock_req.call_args[0][1]


# ---------------------------------------------------------------------------
# Members
# ---------------------------------------------------------------------------


class TestGetMembers:
    def test_returns_member_list(self, client, mock_members):
        resp = make_response({"members": mock_members, "meta": {"total": 2}})
        patch_http(client, resp)
        result = client.get_members()
        assert len(result) == 2
        assert result[0]["firstName"] == "Jane"

    def test_get_members_page_returns_meta(self, client, mock_members):
        resp = make_response({"members": mock_members, "meta": {"total": 2}})
        patch_http(client, resp)
        result = client.get_members_page()
        assert result["meta"]["total"] == 2
        assert len(result["members"]) == 2

    def test_get_single_member(self, client, mock_members):
        resp = make_response(mock_members[0])
        patch_http(client, resp)
        member = client.get_member("mem-001")
        assert member["id"] == "mem-001"

    def test_update_member(self, client):
        updated = {"id": "mem-001", "firstName": "Janet", "lastName": "Smith"}
        resp = make_response(updated)
        mock_req = patch_http(client, resp)
        result = client.update_member("mem-001", firstName="Janet")
        assert result["firstName"] == "Janet"
        # Verify PATCH method was used
        assert mock_req.call_args[0][0] == "PATCH"


# ---------------------------------------------------------------------------
# Attendees
# ---------------------------------------------------------------------------


class TestGetAttendees:
    def test_returns_attendees(self, client, mock_attendees):
        resp = make_response({"attendees": mock_attendees})
        patch_http(client, resp)
        attendees = client.get_attendees(event_id="evt-001")
        assert len(attendees) == 1
        assert attendees[0]["firstName"] == "Jane"

    def test_handles_list_response(self, client, mock_attendees):
        resp = make_response(mock_attendees)
        patch_http(client, resp)
        attendees = client.get_attendees(event_id="evt-001")
        assert len(attendees) == 1


# ---------------------------------------------------------------------------
# Create Member
# ---------------------------------------------------------------------------


class TestCreateMember:
    def test_returns_member_id(self, client):
        resp = make_response({"id": "new-mem-001"})
        patch_http(client, resp)
        member_id = client.create_member("Jane", "Smith", "female")
        assert member_id == "new-mem-001"

    def test_raises_on_missing_id(self, client):
        resp = make_response({})
        patch_http(client, resp)
        with pytest.raises(HelloClubError, match="did not return a member ID"):
            client.create_member("Jane", "Smith", "female")

    def test_rejects_invalid_gender(self, client):
        with pytest.raises(ValueError, match="must be one of"):
            client.create_member("Jane", "Smith", "Female")

    def test_rejects_abbreviated_gender(self, client):
        with pytest.raises(ValueError, match="requires lowercase"):
            client.create_member("Jane", "Smith", "f")


# ---------------------------------------------------------------------------
# Mark Attended
# ---------------------------------------------------------------------------


class TestMarkAttended:
    def test_returns_attendee_record(self, client):
        attendee = {"id": "att-new", "event": "evt-1", "member": {"id": "mem-1"}}
        resp = make_response(attendee)
        patch_http(client, resp)
        result = client.mark_attended(event_id="evt-1", member_id="mem-1")
        assert result["id"] == "att-new"


# ---------------------------------------------------------------------------
# Memberships
# ---------------------------------------------------------------------------


class TestMemberships:
    def test_get_memberships(self, client):
        memberships = [{"id": "ms-1", "name": "Annual"}, {"id": "ms-2", "name": "Monthly"}]
        resp = make_response({"memberships": memberships})
        patch_http(client, resp)
        result = client.get_memberships()
        assert len(result) == 2
        assert result[0]["name"] == "Annual"

    def test_get_single_membership(self, client):
        membership = {"id": "ms-1", "name": "Annual", "fee": 100}
        resp = make_response(membership)
        mock_req = patch_http(client, resp)
        result = client.get_membership("ms-1")
        assert result["name"] == "Annual"
        assert "/membership/ms-1" in mock_req.call_args[0][1]


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------


class TestTransactions:
    def test_get_transactions(self, client):
        txns = [{"id": "txn-1", "amount": 1500, "isPaid": True}]
        resp = make_response({"transactions": txns, "meta": {"total": 1}})
        patch_http(client, resp)
        result = client.get_transactions()
        assert len(result) == 1
        assert result[0]["amount"] == 1500

    def test_get_transactions_page_returns_meta(self, client):
        txns = [{"id": "txn-1", "amount": 1500}]
        resp = make_response({"transactions": txns, "meta": {"total": 1}})
        patch_http(client, resp)
        result = client.get_transactions_page()
        assert result["meta"]["total"] == 1


# ---------------------------------------------------------------------------
# Bookings
# ---------------------------------------------------------------------------


class TestBookings:
    def test_get_bookings(self, client):
        bookings = [{"id": "bk-1", "startDate": "2026-03-01T10:00:00Z"}]
        resp = make_response({"bookings": bookings})
        patch_http(client, resp)
        result = client.get_bookings()
        assert len(result) == 1

    def test_get_single_booking(self, client):
        booking = {"id": "bk-1", "startDate": "2026-03-01T10:00:00Z"}
        resp = make_response(booking)
        mock_req = patch_http(client, resp)
        result = client.get_booking("bk-1")
        assert result["id"] == "bk-1"
        assert "/booking/bk-1" in mock_req.call_args[0][1]


# ---------------------------------------------------------------------------
# Logs
# ---------------------------------------------------------------------------


class TestLogs:
    def test_get_access_logs(self, client):
        logs = [{"id": "log-1", "state": "tag", "wasOpened": True}]
        resp = make_response({"accessLogs": logs})
        patch_http(client, resp)
        result = client.get_logs("accessLog", "2026-01-01T00:00:00Z", "2026-03-01T00:00:00Z")
        assert len(result) == 1
        assert result[0]["state"] == "tag"

    def test_get_email_logs(self, client):
        logs = [{"id": "log-1", "subject": "Payment due", "status": "delivered"}]
        resp = make_response({"emailLogs": logs})
        patch_http(client, resp)
        result = client.get_logs("emailLog", "2026-01-01T00:00:00Z", "2026-03-01T00:00:00Z")
        assert len(result) == 1

    def test_rejects_invalid_log_type(self, client):
        with pytest.raises(ValueError, match="must be one of"):
            client.get_logs("invalidLog", "2026-01-01T00:00:00Z", "2026-03-01T00:00:00Z")


# ---------------------------------------------------------------------------
# Error Handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    def test_4xx_raises_immediately(self, client):
        resp = make_response({"error": "not found"}, status_code=404)
        patch_http(client, resp)
        with pytest.raises(HelloClubError, match="API error 404"):
            client.get_events()

    def test_5xx_retries_then_raises(self, client):
        resp = make_response({"error": "internal"}, status_code=500)
        patch_http(client, resp)
        client._max_retries = 1
        with pytest.raises(HelloClubError, match="API unreachable"):
            client.get_events()

    def test_network_error_retries_then_raises(self, client):
        client._max_retries = 1
        client._http = MagicMock()
        client._http.request.side_effect = httpx.ConnectError("Connection refused")
        with pytest.raises(HelloClubError, match="API unreachable"):
            client.get_events()

    def test_rate_limit_raises_after_retries(self, client):
        client._max_retries = 1
        resp = make_response(None, status_code=429, headers={"Retry-After": "10"})
        # Override raise_for_status since 429 is handled before it
        resp.raise_for_status = MagicMock()
        patch_http(client, resp)
        with pytest.raises(RateLimitError, match="Rate limit exceeded") as exc_info:
            client.get_events()
        assert exc_info.value.retry_after == 10

    def test_rate_limit_without_retry_after_header(self, client):
        client._max_retries = 1
        resp = make_response(None, status_code=429, headers={})
        resp.raise_for_status = MagicMock()
        patch_http(client, resp)
        with pytest.raises(RateLimitError) as exc_info:
            client.get_events()
        assert exc_info.value.retry_after is None


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class TestExceptions:
    def test_hello_club_error(self):
        err = HelloClubError("test error")
        assert str(err) == "test error"

    def test_rate_limit_error_with_retry_after(self):
        err = RateLimitError("rate limited", retry_after=30)
        assert err.retry_after == 30

    def test_rate_limit_error_without_retry_after(self):
        err = RateLimitError("rate limited")
        assert err.retry_after is None

    def test_rate_limit_is_hello_club_error(self):
        assert issubclass(RateLimitError, HelloClubError)
