"""Lightweight Hello Club API client with auth, retry, and rate limiting.

Usage:
    from helloclub import HelloClubClient

    client = HelloClubClient(api_key="your-key")
    events = client.get_events(days_ahead=7)
    members = client.get_members(limit=50)

The client reuses a single httpx.Client for connection pooling. Use it as a
context manager or call close() when done:

    with HelloClubClient(api_key="key") as client:
        events = client.get_events()

Requires Python 3.10+ (or 3.7+ with `from __future__ import annotations`).
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from helloclub.exceptions import HelloClubError, RateLimitError

V1_BASE_URL = "https://api.helloclub.com"
V2_BASE_URL = "https://api-v2.helloclub.com"

VALID_GENDERS = ("male", "female", "other")


class HelloClubClient:
    """Hello Club API client.

    Args:
        api_key: Your Hello Club API key.
        base_url: API base URL. Defaults to V1. Use V2_BASE_URL for V2.
        max_retries: Max retry attempts for server errors (default: 3).
        timeout: Request timeout in seconds (default: 15).
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = V1_BASE_URL,
        max_retries: int = 3,
        timeout: float = 15.0,
    ):
        if not api_key:
            raise HelloClubError(
                "API key is required. Get yours from Hello Club admin > Settings > Integrations > API."
            )
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._max_retries = max_retries
        self._http = httpx.Client(
            timeout=timeout,
            headers={"X-Api-Key": api_key},
        )

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._http.close()

    def __enter__(self) -> HelloClubClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Make an API request with retry and rate limit handling.

        Returns parsed JSON on success. Raises HelloClubError on failure.
        """
        url = f"{self._base_url}{path}"
        last_exc: Exception | None = None

        for attempt in range(self._max_retries):
            try:
                resp = self._http.request(method, url, **kwargs)

                # Rate limit handling
                if resp.status_code == 429:
                    retry_after = resp.headers.get("Retry-After")
                    wait = int(retry_after) if retry_after else 2 ** (attempt + 1)
                    if attempt < self._max_retries - 1:
                        time.sleep(wait)
                        continue
                    raise RateLimitError(
                        "Rate limit exceeded (30 req/min)",
                        retry_after=int(retry_after) if retry_after else None,
                    )

                resp.raise_for_status()
                if resp.content:
                    return resp.json()
                return {}

            except httpx.HTTPStatusError as exc:
                last_exc = exc
                if exc.response.status_code < 500:
                    raise HelloClubError(
                        f"API error {exc.response.status_code}: {exc.response.text}"
                    ) from exc
                # Server errors — retry with backoff
            except httpx.RequestError as exc:
                last_exc = exc

            if attempt < self._max_retries - 1:
                time.sleep(2 ** (attempt + 1))

        raise HelloClubError(
            f"API unreachable after {self._max_retries} attempts: {last_exc}"
        )

    # ----- Events -----

    def get_events(
        self,
        days_ahead: int = 7,
        from_date: str | None = None,
        to_date: str | None = None,
        limit: int = 100,
        offset: int = 0,
        sort: str = "startDate",
    ) -> list[dict]:
        """Fetch events within a date range.

        If from_date/to_date are not provided, defaults to [now, now + days_ahead].
        Returns a list of event dicts.
        """
        now = datetime.now(timezone.utc)
        if not from_date:
            from_date = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        if not to_date:
            to_date = (now + timedelta(days=days_ahead)).strftime("%Y-%m-%dT%H:%M:%SZ")

        data = self._request(
            "GET",
            "/event",
            params={
                "fromDate": from_date,
                "toDate": to_date,
                "sort": sort,
                "limit": limit,
                "offset": offset,
            },
        )
        if isinstance(data, list):
            return data
        return data.get("events", [])

    def get_event(self, event_id: str) -> dict:
        """Fetch a single event by ID."""
        return self._request("GET", f"/event/{event_id}")

    # ----- Members -----

    def get_members(
        self,
        limit: int = 100,
        offset: int = 0,
        sort: str = "-lastOnline",
        search: str | None = None,
    ) -> list[dict]:
        """Fetch members. Returns a list of member dicts."""
        params: dict[str, Any] = {"limit": limit, "offset": offset, "sort": sort}
        if search:
            params["search"] = search
        data = self._request("GET", "/member", params=params)
        if isinstance(data, list):
            return data
        return data.get("members", [])

    def get_members_page(
        self,
        limit: int = 100,
        offset: int = 0,
        sort: str = "-lastOnline",
        search: str | None = None,
    ) -> dict:
        """Fetch members with pagination metadata.

        Returns the full response dict with 'members' list and 'meta' dict
        (containing 'total', 'limit', 'offset').
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset, "sort": sort}
        if search:
            params["search"] = search
        data = self._request("GET", "/member", params=params)
        if isinstance(data, list):
            return {"members": data, "meta": {"total": len(data)}}
        return data

    def get_member(self, member_id: str) -> dict:
        """Fetch a single member by ID."""
        return self._request("GET", f"/member/{member_id}")

    def update_member(self, member_id: str, **fields: Any) -> dict:
        """Update a member (partial update via PATCH).

        Pass field names as keyword arguments using camelCase API names:
            client.update_member("mem-001", firstName="Jane", email="new@example.com")

        Returns the updated member dict.
        """
        return self._request("PATCH", f"/member/{member_id}", json=fields)

    # ----- Attendees -----

    def get_attendees(
        self,
        event_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        """Fetch attendees for an event. Returns a list of attendee dicts."""
        data = self._request(
            "GET",
            "/eventAttendee",
            params={"event": event_id, "limit": limit, "offset": offset},
        )
        if isinstance(data, list):
            return data
        return data.get("attendees", [])

    # ----- Write Operations -----

    def create_member(
        self,
        first_name: str,
        last_name: str,
        gender: str,
        email: str | None = None,
    ) -> str:
        """Create a new member. Returns the new member's ID.

        Args:
            gender: Must be "male", "female", or "other".
        """
        if gender not in VALID_GENDERS:
            raise ValueError(
                f"gender must be one of {VALID_GENDERS}, got {gender!r}. "
                f"Note: the API requires lowercase."
            )
        body: dict[str, Any] = {
            "firstName": first_name,
            "lastName": last_name,
            "gender": gender,
        }
        if email:
            body["email"] = email

        data = self._request("POST", "/member", json=body)
        member_id = data.get("id")
        if not member_id:
            raise HelloClubError("API did not return a member ID after creation")
        return str(member_id)

    def mark_attended(self, event_id: str, member_id: str) -> dict:
        """Register a member as an attendee for an event.

        Returns the created attendee record.
        """
        return self._request(
            "POST", "/eventAttendee", json={"event": event_id, "member": member_id}
        )

    # ----- Memberships -----

    def get_memberships(self, limit: int = 100) -> list[dict]:
        """Fetch all membership types."""
        data = self._request("GET", "/membership", params={"limit": limit})
        if isinstance(data, list):
            return data
        return data.get("memberships", [])

    def get_membership(self, membership_id: str) -> dict:
        """Fetch a single membership type by ID."""
        return self._request("GET", f"/membership/{membership_id}")

    # ----- Transactions -----

    def get_transactions(
        self,
        limit: int = 100,
        offset: int = 0,
        is_paid: bool | None = None,
        member: str | None = None,
    ) -> list[dict]:
        """Fetch transactions. Returns a list of transaction dicts."""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if is_paid is not None:
            params["isPaid"] = str(is_paid).lower()
        if member:
            params["member"] = member
        data = self._request("GET", "/transaction", params=params)
        if isinstance(data, list):
            return data
        return data.get("transactions", [])

    def get_transactions_page(
        self,
        limit: int = 100,
        offset: int = 0,
        is_paid: bool | None = None,
        member: str | None = None,
    ) -> dict:
        """Fetch transactions with pagination metadata.

        Returns the full response dict with 'transactions' list and 'meta' dict.
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if is_paid is not None:
            params["isPaid"] = str(is_paid).lower()
        if member:
            params["member"] = member
        data = self._request("GET", "/transaction", params=params)
        if isinstance(data, list):
            return {"transactions": data, "meta": {"total": len(data)}}
        return data

    # ----- Bookings -----

    def get_bookings(
        self,
        from_date: str | None = None,
        to_date: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """Fetch bookings within a date range."""
        params: dict[str, Any] = {"limit": limit}
        if from_date:
            params["fromDate"] = from_date
        if to_date:
            params["toDate"] = to_date
        data = self._request("GET", "/booking", params=params)
        if isinstance(data, list):
            return data
        return data.get("bookings", [])

    def get_booking(self, booking_id: str) -> dict:
        """Fetch a single booking by ID."""
        return self._request("GET", f"/booking/{booking_id}")

    # ----- Logs -----

    def get_logs(
        self,
        log_type: str,
        from_date: str,
        to_date: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        """Fetch log entries. All log endpoints require fromDate and toDate.

        Args:
            log_type: One of "accessLog", "activityLog", "auditLog",
                      "checkInLog", "emailLog".
            from_date: ISO 8601 start date (required).
            to_date: ISO 8601 end date (required).

        Returns a list of log entry dicts.
        """
        valid_types = ("accessLog", "activityLog", "auditLog", "checkInLog", "emailLog")
        if log_type not in valid_types:
            raise ValueError(f"log_type must be one of {valid_types}, got {log_type!r}")

        data = self._request(
            "GET",
            f"/{log_type}",
            params={
                "fromDate": from_date,
                "toDate": to_date,
                "limit": limit,
                "offset": offset,
            },
        )
        if isinstance(data, list):
            return data
        # Wrapper key is the plural form: accessLogs, activityLogs, etc.
        wrapper_key = f"{log_type}s"
        return data.get(wrapper_key, [])
