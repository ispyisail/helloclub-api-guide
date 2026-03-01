"""Create a member and mark them as attended at an event.

Demonstrates write operations: POST /member and POST /eventAttendee.

Usage:
    export HELLOCLUB_API_KEY="your-api-key-here"
    python examples/manage_members.py

WARNING: This creates real data in your club. Use with caution.
"""

import os
import sys

import httpx

API_KEY = os.environ["HELLOCLUB_API_KEY"]
BASE_URL = "https://api.helloclub.com"
HEADERS = {"X-Api-Key": API_KEY}


def create_member(first_name: str, last_name: str, gender: str, email: str | None = None) -> dict:
    """Create a new club member. Returns the created member data."""
    body = {
        "firstName": first_name,
        "lastName": last_name,
        "gender": gender,  # "male", "female", or "other"
    }
    if email:
        body["email"] = email

    resp = httpx.post(f"{BASE_URL}/member", headers=HEADERS, json=body)
    resp.raise_for_status()
    return resp.json()


def mark_attended(event_id: str, member_id: str) -> dict:
    """Register a member as an attendee for an event."""
    resp = httpx.post(
        f"{BASE_URL}/eventAttendee",
        headers=HEADERS,
        json={"event": event_id, "member": member_id},
    )
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    print("Hello Club API — Member Management Example")
    print("=" * 50)
    print()
    print("This script demonstrates creating a member and marking attendance.")
    print("It does NOT actually run unless you uncomment the code below.")
    print()
    print("Example usage:")
    print()
    print('  # Create a member')
    print('  member = create_member("Jane", "Smith", "female", "jane@example.com")')
    print(f'  print(f"Created member: {{member[\'id\']}}")')
    print()
    print('  # Mark them as attended at an event')
    print('  mark_attended(event_id="your-event-id", member_id=member["id"])')
    print('  print("Marked as attended")')
    print()
    print("To run for real, uncomment the code at the bottom of this file.")

    # UNCOMMENT TO RUN:
    # member = create_member("Jane", "Smith", "female", "jane@example.com")
    # print(f"Created member: {member['id']}")
    #
    # mark_attended(event_id="your-event-id", member_id=member["id"])
    # print("Marked as attended")
