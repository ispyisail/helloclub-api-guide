# Hello Club API Guide

> **Tested against live API — Feb 2026** | API spec version: 2021-08-30 | ~40% of returned fields are undocumented in the official spec

## V2 Migration Notice

Hello Club is migrating to a **V2 API** (`api-v2.helloclub.com`). Endpoints become plural, `club` becomes `org`, `member` becomes `profile`, and PUT becomes PATCH. See the [V2 Migration Guide](docs/v2-migration.md) for full details.

---

## What is the Hello Club API?

[Hello Club](https://www.helloclub.com) is a club management platform used by sports clubs, community organisations, and co-working spaces. Their REST API lets you programmatically access members, events, attendees, bookings, transactions, and more.

The official OpenAPI spec (2021-08-30) is significantly out of date. This guide documents what the API **actually returns** based on live testing against a production club with 2,137 members and 971 events.

## Requirements

- Python 3.10+
- [httpx](https://www.python-httpx.org/)

## Quickstart

```python
import os
import httpx

API_KEY = os.environ["HELLOCLUB_API_KEY"]

with httpx.Client(
    base_url="https://api.helloclub.com",
    headers={"X-Api-Key": API_KEY},
) as client:
    data = client.get("/event", params={"limit": 10, "sort": "startDate"}).json()

for event in data.get("events", []):
    print(f"{event['name']} — {event['startDate'][:10]}")
```

Set your API key as an environment variable:

```bash
export HELLOCLUB_API_KEY="your-api-key-here"
```

Then run any example:

```bash
pip install httpx
python examples/quickstart.py
```

## Getting an API Key

See [Authentication](docs/authentication.md) for how to get your API key from the Hello Club admin panel.

## Documentation

| Topic | Description |
|---|---|
| [Authentication](docs/authentication.md) | API key setup, headers, base URLs |
| [Endpoints](docs/endpoints.md) | All endpoints with status, parameters, and quirks |
| [Rate Limiting](docs/rate-limiting.md) | 30 req/min limit, 429 handling, retry strategy |
| [V2 Migration](docs/v2-migration.md) | V2 transition guide with side-by-side comparison |
| [Gotchas](docs/gotchas.md) | Broken endpoints, spec vs reality, known issues |

## Field Reference

Detailed field documentation for every entity type, including undocumented fields discovered through live probing:

| Entity | Fields |
|---|---|
| [Events](docs/fields/events.md) | 80+ fields across identity, dates, attendance, rules, recurrence |
| [Members](docs/fields/members.md) | 120+ fields including contact, financial, subscriptions, grades |
| [Attendees](docs/fields/attendees.md) | 50+ fields covering attendance, payment, pricing rules |
| [Memberships](docs/fields/memberships.md) | 40+ fields for membership type configuration |
| [Transactions](docs/fields/transactions.md) | 30+ fields with financial details and tax info |
| [Bookings](docs/fields/bookings.md) | 70+ fields including areas, tags, recurrence |
| [Logs](docs/fields/logs.md) | Access, activity, audit, check-in, and email logs |
| [Custom Fields](docs/fields/custom-fields.md) | Club-specific dynamic fields on events and members |

## Examples

| Script | Description |
|---|---|
| [quickstart.py](examples/quickstart.py) | Minimal auth + fetch events (< 30 lines) |
| [fetch_events.py](examples/fetch_events.py) | List events with date filtering |
| [fetch_members.py](examples/fetch_members.py) | List members with search/filter |
| [fetch_attendees.py](examples/fetch_attendees.py) | Get attendees for an event |
| [manage_members.py](examples/manage_members.py) | Create a member, mark as attended |
| [pagination.py](examples/pagination.py) | Handle paginated responses |
| [rate_limit_handler.py](examples/rate_limit_handler.py) | Retry with backoff + Retry-After |
| [field_discovery.py](examples/field_discovery.py) | Probe script to discover fields for your club |

## Client Library

A lightweight, reusable client with auth, retry, and rate limiting:

```python
from helloclub import HelloClubClient

client = HelloClubClient(api_key="your-key")
events = client.get_events(days_ahead=7)
members = client.get_members(limit=50)
```

See [helloclub/client.py](helloclub/client.py) for the full implementation.

## License

MIT — see [LICENSE](LICENSE).
