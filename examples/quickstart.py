"""Hello Club API — Quickstart example.

Fetches upcoming events and prints their names and dates.

Usage:
    export HELLOCLUB_API_KEY="your-api-key-here"
    python examples/quickstart.py
"""

import os

import httpx

API_KEY = os.environ["HELLOCLUB_API_KEY"]

client = httpx.Client(
    base_url="https://api.helloclub.com",
    headers={"X-Api-Key": API_KEY},
)

response = client.get("/event", params={"limit": 10, "sort": "startDate"})
response.raise_for_status()
data = response.json()

print(f"Found {data['meta']['total']} events total. Showing first {len(data['events'])}:\n")
for event in data["events"]:
    print(f"  {event['name']} — {event['startDate'][:10]}")
