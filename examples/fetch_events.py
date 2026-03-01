"""Fetch events with date filtering.

Lists events in a date range, showing name, date, attendance, and activity.

Usage:
    export HELLOCLUB_API_KEY="your-api-key-here"
    python examples/fetch_events.py
"""

import os
from datetime import datetime, timedelta, timezone

import httpx

API_KEY = os.environ["HELLOCLUB_API_KEY"]
BASE_URL = "https://api.helloclub.com"

# Fetch events for the next 30 days
now = datetime.now(timezone.utc)
from_date = now.strftime("%Y-%m-%dT%H:%M:%SZ")
to_date = (now + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")

response = httpx.get(
    f"{BASE_URL}/event",
    headers={"X-Api-Key": API_KEY},
    params={
        "fromDate": from_date,
        "toDate": to_date,
        "sort": "startDate",
        "limit": 100,
    },
)
response.raise_for_status()
data = response.json()

events = data.get("events", [])
total = data.get("meta", {}).get("total", len(events))

print(f"Events in next 30 days: {total}")
print(f"{'Name':<35} {'Date':<12} {'Attendees':<10} {'Activity'}")
print("-" * 80)

for event in events:
    name = event["name"][:34]
    date = event["startDate"][:10]
    attendees = f"{event.get('numAttendees', 0)}/{event.get('maxAttendees', '?')}"
    activity = event.get("activity", {}).get("name", "")

    # Note: 'categories' is undocumented but useful for filtering
    categories = [c["name"] for c in event.get("categories", [])]
    cat_str = f" [{', '.join(categories)}]" if categories else ""

    print(f"  {name:<35} {date:<12} {attendees:<10} {activity}{cat_str}")

# Note: GET /event/upcoming is BROKEN (returns 400). Always use /event with date range.
