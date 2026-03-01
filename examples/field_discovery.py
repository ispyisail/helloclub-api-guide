"""Discover all API fields for your Hello Club instance.

Probes events, members, and attendees, then prints every field path
with type and sample values. Useful for finding undocumented fields
specific to your club's configuration.

Usage:
    export HELLOCLUB_API_KEY="your-api-key-here"
    python examples/field_discovery.py
"""

import os
import sys
from datetime import datetime, timedelta, timezone

import httpx

API_KEY = os.environ.get("HELLOCLUB_API_KEY", "")
BASE_URL = "https://api.helloclub.com"
HEADERS = {"X-Api-Key": API_KEY}


def request(method: str, path: str, **kwargs):
    """Make an API request."""
    url = f"{BASE_URL}{path}"
    with httpx.Client(timeout=30.0) as client:
        resp = client.request(method, url, headers=HEADERS, **kwargs)
        resp.raise_for_status()
        return resp.json() if resp.content else {}


def collect_all_keys(items: list[dict], prefix: str = "") -> dict:
    """Recursively collect all unique keys and their types/sample values."""
    field_map: dict = {}
    for item in items:
        _collect(item, prefix, field_map)
    return field_map


def _collect(obj, prefix: str, field_map: dict):
    if isinstance(obj, dict):
        for key, val in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key
            val_type = type(val).__name__
            if val is None:
                val_type = "null"
            elif isinstance(val, list):
                val_type = f"array[{len(val)}]"
            elif isinstance(val, dict):
                val_type = "object"

            if full_key not in field_map:
                field_map[full_key] = {"type": val_type, "sample": _sample(val), "count": 1}
            else:
                field_map[full_key]["count"] += 1
                if field_map[full_key]["sample"] is None and val is not None:
                    field_map[full_key]["sample"] = _sample(val)
                    field_map[full_key]["type"] = val_type

            if isinstance(val, dict):
                _collect(val, full_key, field_map)
            elif isinstance(val, list) and val:
                for item in val[:3]:
                    if isinstance(item, dict):
                        _collect(item, f"{full_key}[]", field_map)


def _sample(val):
    if val is None:
        return None
    if isinstance(val, str):
        return val[:80]
    if isinstance(val, (int, float, bool)):
        return val
    if isinstance(val, list):
        return f"[{len(val)} items]"
    if isinstance(val, dict):
        return f"{{{len(val)} keys}}"
    return str(val)[:80]


def print_fields(fields: dict, entity_name: str, total: int):
    print(f"\n{'='*60}")
    print(f"{entity_name} FIELDS ({len(fields)} unique paths from {total} records)")
    print(f"{'='*60}")
    for key in sorted(fields.keys()):
        info = fields[key]
        sample_str = str(info["sample"])[:50] if info["sample"] is not None else "null"
        print(f"  {key}: {info['type']} ({info['count']}/{total}) | {sample_str}")


def probe_events():
    print("\nProbing events...")
    now = datetime.now(timezone.utc)
    data = request("GET", "/event", params={
        "fromDate": (now - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "toDate": (now + timedelta(days=60)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sort": "startDate",
        "limit": 10,
    })
    events = data.get("events", []) if isinstance(data, dict) else data
    print(f"  Got {len(events)} events")
    if events:
        fields = collect_all_keys(events)
        print_fields(fields, "EVENT", len(events))
        return events
    return []


def probe_members():
    print("\nProbing members...")
    data = request("GET", "/member", params={
        "limit": 10,
        "sort": "-lastOnline",
    })
    members = data.get("members", []) if isinstance(data, dict) else data
    print(f"  Got {len(members)} members")
    if members:
        fields = collect_all_keys(members)
        print_fields(fields, "MEMBER", len(members))
        return members
    return []


def probe_attendees(event_id: str | None = None):
    print(f"\nProbing attendees (event={event_id or 'any'})...")
    params: dict = {"limit": 20}
    if event_id:
        params["event"] = event_id
    data = request("GET", "/eventAttendee", params=params)
    attendees = data.get("attendees", []) if isinstance(data, dict) else data
    print(f"  Got {len(attendees)} attendees")
    if attendees:
        fields = collect_all_keys(attendees)
        print_fields(fields, "ATTENDEE", len(attendees))
        return attendees
    return []


if __name__ == "__main__":
    if not API_KEY:
        print("ERROR: Set HELLOCLUB_API_KEY environment variable")
        sys.exit(1)

    print("Hello Club API — Field Discovery")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print(f"Base URL: {BASE_URL}")

    # Get totals
    member_meta = request("GET", "/member", params={"limit": 1})
    if isinstance(member_meta, dict) and "meta" in member_meta:
        print(f"Total members: {member_meta['meta'].get('total', '?')}")

    # Probe each entity type
    events = probe_events()
    probe_members()

    event_id = events[0].get("id") if events else None
    probe_attendees(event_id)

    print(f"\n{'='*60}")
    print("Done. Review the field lists above to find your club's fields.")
    print(f"{'='*60}")
