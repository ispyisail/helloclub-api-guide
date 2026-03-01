"""Handle paginated responses from the Hello Club API.

The API returns at most 100 results per request. Use offset to paginate.

Usage:
    export HELLOCLUB_API_KEY="your-api-key-here"
    python examples/pagination.py
"""

from __future__ import annotations

import os
import time

import httpx

API_KEY = os.environ["HELLOCLUB_API_KEY"]
BASE_URL = "https://api.helloclub.com"
HEADERS = {"X-Api-Key": API_KEY}


def fetch_all_members() -> list[dict]:
    """Fetch ALL members using pagination.

    The API limits responses to 100 items per request.
    We use the 'offset' parameter to page through all results.
    A 2-second delay between requests keeps us under the 30 req/min rate limit.
    """
    all_members = []
    offset = 0
    limit = 100

    while True:
        resp = httpx.get(
            f"{BASE_URL}/member",
            headers=HEADERS,
            params={"limit": limit, "offset": offset, "sort": "lastName"},
        )
        resp.raise_for_status()
        data = resp.json()

        members = data.get("members", [])
        total = data.get("meta", {}).get("total", None)
        all_members.extend(members)

        total_str = str(total) if total is not None else "?"
        print(f"  Fetched {len(all_members)}/{total_str} members...")

        # Stop when we get fewer results than requested (last page)
        if len(members) < limit:
            break

        # Also stop if we know the total and have reached it
        if total is not None and len(all_members) >= total:
            break

        offset += limit
        time.sleep(2)  # Stay under 30 req/min rate limit

    return all_members


if __name__ == "__main__":
    print("Fetching all members with pagination...\n")
    members = fetch_all_members()
    print(f"\nDone. Fetched {len(members)} total members.")

    # Show summary
    if members:
        print(f"\nFirst: {members[0]['firstName']} {members[0]['lastName']}")
        print(f"Last:  {members[-1]['firstName']} {members[-1]['lastName']}")
