"""Verify Hello Club's suggested fixes and document the results.

Tests:
  1. Stable sort: does sort=-updatedAt,id eliminate pagination duplicates?
  2. updatedAt filter: does ?updatedAt=<date> work for incremental sync?
  3. /event/upcoming: confirm it still returns 400
  4. Date-required logs: confirm checkInLog and emailLog return 422 without dates

Usage:
    export HELLOCLUB_API_KEY="your-key"
    python scripts/verify_fixes.py
"""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx

API_KEY = os.environ.get("HELLOCLUB_API_KEY")
if not API_KEY:
    print("ERROR: Set HELLOCLUB_API_KEY in .env or environment")
    sys.exit(1)

BASE_URL = "https://api.helloclub.com"
RATE_LIMIT_DELAY = 2.1  # seconds between requests (30 req/min = 2s each, plus buffer)

results: list[dict] = []


def api_get(client: httpx.Client, path: str, params: dict | None = None) -> httpx.Response:
    """Make a rate-limited GET request."""
    time.sleep(RATE_LIMIT_DELAY)
    return client.get(f"{BASE_URL}{path}", params=params or {})


def test_stable_sort(client: httpx.Client) -> None:
    """Test 1: Does sort=-updatedAt,id produce stable pagination (no duplicates)?"""
    print("\n" + "=" * 70)
    print("TEST 1: Stable sort with ,id tiebreaker")
    print("=" * 70)

    # Fetch 3 pages with unstable sort (baseline)
    print("\n  [a] Baseline: sort=-updatedAt (no tiebreaker)")
    unstable_ids: list[str] = []
    for page_num in range(3):
        resp = api_get(client, "/member", {
            "limit": 100,
            "offset": page_num * 100,
            "sort": "-updatedAt",
        })
        if resp.status_code != 200:
            print(f"      Page {page_num + 1}: ERROR {resp.status_code}")
            continue
        members = resp.json().get("members", [])
        unstable_ids.extend(m["id"] for m in members)
        print(f"      Page {page_num + 1}: {len(members)} members")

    unstable_unique = len(set(unstable_ids))
    unstable_dupes = len(unstable_ids) - unstable_unique
    print(f"      Total: {len(unstable_ids)} records, {unstable_unique} unique, {unstable_dupes} duplicates")

    # Fetch 3 pages with stable sort
    print("\n  [b] Fix: sort=-updatedAt,id (with tiebreaker)")
    stable_ids: list[str] = []
    for page_num in range(3):
        resp = api_get(client, "/member", {
            "limit": 100,
            "offset": page_num * 100,
            "sort": "-updatedAt,id",
        })
        if resp.status_code != 200:
            print(f"      Page {page_num + 1}: ERROR {resp.status_code} — {resp.text[:200]}")
            continue
        members = resp.json().get("members", [])
        stable_ids.extend(m["id"] for m in members)
        print(f"      Page {page_num + 1}: {len(members)} members")

    stable_unique = len(set(stable_ids))
    stable_dupes = len(stable_ids) - stable_unique
    print(f"      Total: {len(stable_ids)} records, {stable_unique} unique, {stable_dupes} duplicates")

    # Check page overlap
    if len(stable_ids) >= 200:
        page1_ids = set(stable_ids[:100])
        page2_ids = set(stable_ids[100:200])
        overlap = page1_ids & page2_ids
        print(f"      Page 1<->2 overlap: {len(overlap)} members")

    fixed = stable_dupes < unstable_dupes
    results.append({
        "test": "Stable sort (sort=-updatedAt,id)",
        "status": "PASS" if stable_dupes == 0 else "IMPROVED" if fixed else "FAIL",
        "detail": f"Unstable: {unstable_dupes} dupes -> Stable: {stable_dupes} dupes across 3 pages",
    })

    print(f"\n  Result: {'PASS' if stable_dupes == 0 else 'IMPROVED' if fixed else 'FAIL'}")


def test_updated_at_filter(client: httpx.Client) -> None:
    """Test 2: Does ?updatedAt=<date> filter work for incremental sync?"""
    print("\n" + "=" * 70)
    print("TEST 2: updatedAt filter for incremental sync")
    print("=" * 70)

    # Filter to members updated in the last 7 days
    since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"\n  Filtering: updatedAt={since}")

    resp = api_get(client, "/member", {
        "limit": 100,
        "updatedAt": since,
    })

    if resp.status_code != 200:
        print(f"  ERROR: {resp.status_code} — {resp.text[:300]}")
        results.append({
            "test": "updatedAt filter",
            "status": "FAIL",
            "detail": f"HTTP {resp.status_code}: {resp.text[:200]}",
        })
        return

    data = resp.json()
    members = data.get("members", [])
    total = data.get("meta", {}).get("total", len(members))
    print(f"  Returned: {len(members)} members (total matching: {total})")

    # Verify the returned members actually have updatedAt >= since
    if members:
        dates_ok = 0
        dates_bad = 0
        for m in members:
            updated = m.get("updatedAt", "")
            if updated >= since:
                dates_ok += 1
            else:
                dates_bad += 1
                if dates_bad <= 3:
                    print(f"  WARNING: member {m['id']} updatedAt={updated} is before filter date")
        print(f"  Date check: {dates_ok}/{len(members)} members have updatedAt >= filter date")

        passed = dates_bad == 0 and len(members) > 0
        results.append({
            "test": "updatedAt filter",
            "status": "PASS" if passed else "PARTIAL",
            "detail": f"{total} members matched, {dates_ok}/{len(members)} with correct dates",
        })
    else:
        # No members updated in 7 days — try 30 days
        print("  No members in last 7 days, trying 30 days...")
        since_30 = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        resp2 = api_get(client, "/member", {"limit": 10, "updatedAt": since_30})
        if resp2.status_code == 200:
            members_30 = resp2.json().get("members", [])
            total_30 = resp2.json().get("meta", {}).get("total", len(members_30))
            print(f"  30-day filter: {total_30} members")
            results.append({
                "test": "updatedAt filter",
                "status": "PASS" if total_30 > 0 else "INCONCLUSIVE",
                "detail": f"7-day: 0 results, 30-day: {total_30} results",
            })
        else:
            results.append({
                "test": "updatedAt filter",
                "status": "FAIL",
                "detail": f"30-day filter also failed: HTTP {resp2.status_code}",
            })

    print(f"\n  Result: {results[-1]['status']}")


def test_event_upcoming(client: httpx.Client) -> None:
    """Test 3: Confirm /event/upcoming still returns 400."""
    print("\n" + "=" * 70)
    print("TEST 3: /event/upcoming returns 400 (removed endpoint)")
    print("=" * 70)

    resp = api_get(client, "/event/upcoming")
    print(f"\n  Status: {resp.status_code}")
    print(f"  Body: {resp.text[:200]}")

    results.append({
        "test": "/event/upcoming removed",
        "status": "CONFIRMED" if resp.status_code == 400 else f"UNEXPECTED ({resp.status_code})",
        "detail": f"HTTP {resp.status_code}: {resp.text[:100]}",
    })

    print(f"\n  Result: {results[-1]['status']}")


def test_date_required_logs(client: httpx.Client) -> None:
    """Test 4: Confirm checkInLog and emailLog require dates."""
    print("\n" + "=" * 70)
    print("TEST 4: Log endpoints require fromDate/toDate")
    print("=" * 70)

    for endpoint in ["/checkInLog", "/emailLog"]:
        # Without dates — should fail
        print(f"\n  [a] {endpoint} without dates:")
        resp_no_dates = api_get(client, endpoint)
        print(f"      Status: {resp_no_dates.status_code}")
        if resp_no_dates.status_code != 200:
            print(f"      Body: {resp_no_dates.text[:200]}")

        # With dates — should succeed
        print(f"  [b] {endpoint} with dates:")
        now = datetime.now(timezone.utc)
        resp_with_dates = api_get(client, endpoint, {
            "fromDate": (now - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "toDate": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        })
        print(f"      Status: {resp_with_dates.status_code}")
        if resp_with_dates.status_code == 200:
            data = resp_with_dates.json()
            # Find the wrapper key
            keys = [k for k in data if k != "meta"]
            count = len(data.get(keys[0], [])) if keys else 0
            print(f"      Records: {count}")

        no_dates_fails = resp_no_dates.status_code in (400, 422)
        with_dates_works = resp_with_dates.status_code == 200
        results.append({
            "test": f"{endpoint} requires dates",
            "status": "CONFIRMED" if no_dates_fails and with_dates_works else "UNEXPECTED",
            "detail": f"Without dates: {resp_no_dates.status_code}, with dates: {resp_with_dates.status_code}",
        })

    print(f"\n  Result: {results[-1]['status']}")


def print_summary() -> None:
    """Print a summary of all test results."""
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for r in results:
        status = r["status"]
        icon = "+" if status in ("PASS", "CONFIRMED", "IMPROVED") else "-" if status == "FAIL" else "?"
        print(f"  [{icon}] {r['test']}: {r['status']}")
        print(f"      {r['detail']}")
    print()


def main() -> None:
    print("Hello Club API — Verify Suggested Fixes")
    print(f"Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"Rate limit delay: {RATE_LIMIT_DELAY}s between requests")

    with httpx.Client(headers={"X-Api-Key": API_KEY}, timeout=15.0) as client:
        test_event_upcoming(client)
        test_date_required_logs(client)
        test_updated_at_filter(client)
        test_stable_sort(client)

    print_summary()


if __name__ == "__main__":
    main()
