"""Shared fixtures and mock responses for Hello Club client tests."""

from __future__ import annotations

import pytest


@pytest.fixture()
def api_key() -> str:
    return "test-api-key-123"


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
def mock_members() -> dict:
    return {
        "members": [
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
        ],
        "meta": {"total": 2, "limit": 100, "offset": 0},
    }


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
