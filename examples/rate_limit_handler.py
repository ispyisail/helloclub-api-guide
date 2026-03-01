"""Rate limit handling with exponential backoff.

Demonstrates proper handling of 429 responses from the Hello Club API.

Usage:
    export HELLOCLUB_API_KEY="your-api-key-here"
    python examples/rate_limit_handler.py
"""

import os
import time
from datetime import datetime, timezone

import httpx

API_KEY = os.environ["HELLOCLUB_API_KEY"]
BASE_URL = "https://api.helloclub.com"
HEADERS = {"X-Api-Key": API_KEY}


def request_with_retry(
    method: str,
    path: str,
    max_retries: int = 3,
    **kwargs,
) -> httpx.Response:
    """Make an API request with rate limit and error handling.

    - 429 (rate limit): Wait using Retry-After header (V2) or exponential backoff
    - 5xx (server error): Retry with exponential backoff
    - 4xx (client error): Raise immediately (no retry)
    """
    url = f"{BASE_URL}{path}"

    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.request(method, url, headers=HEADERS, **kwargs)

            # Rate limit — wait and retry
            if resp.status_code == 429:
                # V2 API provides Retry-After header (seconds to wait)
                retry_after = resp.headers.get("Retry-After")
                if retry_after:
                    wait = int(retry_after)
                    print(f"  Rate limited. Retry-After: {wait}s")
                else:
                    wait = 2 ** (attempt + 1)  # 2, 4, 8 seconds
                    print(f"  Rate limited. Backing off: {wait}s")

                if attempt < max_retries - 1:
                    time.sleep(wait)
                    continue

            resp.raise_for_status()
            return resp

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code < 500:
                # Client errors (4xx) — don't retry
                raise
            # Server errors (5xx) — retry with backoff
            if attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)
                print(f"  Server error {exc.response.status_code}. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise

        except httpx.RequestError as exc:
            if attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)
                print(f"  Connection error. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise

    raise RuntimeError(f"Failed after {max_retries} attempts")


if __name__ == "__main__":
    print("Rate Limit Handler — Demo")
    print("=" * 40)
    print()

    # Make a few requests to demonstrate rate-aware fetching
    print("Fetching events...")
    resp = request_with_retry("GET", "/event", params={"limit": 5})
    data = resp.json()
    events = data.get("events", [])
    print(f"  Got {len(events)} events")

    print("\nFetching members...")
    resp = request_with_retry("GET", "/member", params={"limit": 5})
    data = resp.json()
    members = data.get("members", [])
    print(f"  Got {len(members)} members")

    print("\nFetching membership types...")
    resp = request_with_retry("GET", "/membership", params={"limit": 5})
    data = resp.json()
    memberships = data.get("memberships", [])
    print(f"  Got {len(memberships)} membership types")

    print("\nAll requests completed successfully.")
