"""Fetch attendees for an event.

Gets the attendee list for a specific event, showing attendance and payment status.

Usage:
    export HELLOCLUB_API_KEY="your-api-key-here"
    python examples/fetch_attendees.py [event_id]

If no event_id is provided, fetches the next upcoming event and uses that.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone

import httpx

API_KEY = os.environ["HELLOCLUB_API_KEY"]
BASE_URL = "https://api.helloclub.com"
HEADERS = {"X-Api-Key": API_KEY}


def get_next_event() -> dict | None:
    """Find the next upcoming event."""
    now = datetime.now(timezone.utc)
    resp = httpx.get(
        f"{BASE_URL}/event",
        headers=HEADERS,
        params={
            "fromDate": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "toDate": (now + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sort": "startDate",
            "limit": 1,
        },
    )
    resp.raise_for_status()
    events = resp.json().get("events", [])
    return events[0] if events else None


def get_attendees(event_id: str) -> list[dict]:
    """Fetch all attendees for an event."""
    resp = httpx.get(
        f"{BASE_URL}/eventAttendee",
        headers=HEADERS,
        params={"event": event_id, "limit": 100},
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("attendees", []) if isinstance(data, dict) else data


# Determine event ID
event_id = sys.argv[1] if len(sys.argv) > 1 else None

if not event_id:
    event = get_next_event()
    if not event:
        print("No upcoming events found.")
        sys.exit(0)
    event_id = event["id"]
    print(f"Using next event: {event['name']} ({event['startDate'][:10]})")
    print()

# Fetch and display attendees
attendees = get_attendees(event_id)
print(f"Attendees: {len(attendees)}\n")

print(f"{'Name':<25} {'Type':<8} {'Attended':<10} {'Paid':<6} {'Fee'}")
print("-" * 65)

for att in attendees:
    name = f"{att['firstName']} {att['lastName']}"[:24]
    att_type = "Guest" if att.get("isGuest") else "Member"
    attended = "Yes" if att.get("hasAttended") else "No"
    paid = "Yes" if att.get("isPaid") else "No"

    # Parse fee from rule
    rule = att.get("rule", {})
    rule_type = rule.get("type", "")
    fee = rule.get("fee", 0)
    if att.get("hasMembershipRule") or rule_type == "membership":
        fee_str = "Membership"
    elif rule_type == "fee" and fee:
        fee_str = f"${fee:.2f}"
    elif rule_type == "free":
        fee_str = "Free"
    else:
        fee_str = ""

    print(f"  {name:<25} {att_type:<8} {attended:<10} {paid:<6} {fee_str}")
