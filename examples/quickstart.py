"""Hello Club API — Quickstart example.

Fetches upcoming events and prints their names and dates.

Usage:
    export HELLOCLUB_API_KEY="your-api-key-here"
    python examples/quickstart.py
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import httpx

API_KEY = os.environ["HELLOCLUB_API_KEY"]

now = datetime.now(timezone.utc)

with httpx.Client(
    base_url="https://api.helloclub.com",
    headers={"X-Api-Key": API_KEY},
) as client:
    response = client.get("/event", params={
        "fromDate": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "toDate": (now + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sort": "startDate",
        "limit": 10,
    })
    response.raise_for_status()
    data = response.json()

events = data.get("events", [])
total = data.get("meta", {}).get("total", len(events))

print(f"Found {total} events in the next 30 days. Showing first {len(events)}:\n")
for event in events:
    print(f"  {event['name']} — {event['startDate'][:10]}")
