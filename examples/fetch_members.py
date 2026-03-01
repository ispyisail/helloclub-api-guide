"""Fetch members with search and filtering.

Lists members with their contact details and membership status.

Usage:
    export HELLOCLUB_API_KEY="your-api-key-here"
    python examples/fetch_members.py
"""

import os

import httpx

API_KEY = os.environ["HELLOCLUB_API_KEY"]
BASE_URL = "https://api.helloclub.com"

# Fetch first 20 members sorted by most recently active
response = httpx.get(
    f"{BASE_URL}/member",
    headers={"X-Api-Key": API_KEY},
    params={
        "limit": 20,
        "sort": "-lastOnline",  # Most recently active first
    },
)
response.raise_for_status()
data = response.json()

members = data.get("members", [])
total = data.get("meta", {}).get("total", len(members))

print(f"Total members: {total}")
print(f"Showing {len(members)} most recently active:\n")

print(f"{'Name':<25} {'Email':<30} {'Membership':<20} {'Last Online'}")
print("-" * 90)

for member in members:
    name = f"{member['firstName']} {member['lastName']}"[:24]
    email = (member.get("email") or "")[:29]

    # Get current membership name
    membership = ""
    for sub in member.get("subscriptions", []):
        if sub.get("isCurrent"):  # Note: isCurrent is undocumented
            membership = sub.get("membership", {}).get("name", "")[:19]
            break

    last_online = (member.get("lastOnline") or "")[:10]

    print(f"  {name:<25} {email:<30} {membership:<20} {last_online}")

# Search example — find members by name
print("\n--- Search example ---")
search_response = httpx.get(
    f"{BASE_URL}/member",
    headers={"X-Api-Key": API_KEY},
    params={"search": "Smith", "limit": 5},
)
search_response.raise_for_status()
search_data = search_response.json()

results = search_data.get("members", [])
print(f"Search 'Smith': {len(results)} results")
for m in results:
    print(f"  {m['firstName']} {m['lastName']} ({m.get('email', 'no email')})")
