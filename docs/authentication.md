# Authentication

## Getting Your API Key

1. Log in to your Hello Club admin panel
2. Navigate to **Settings** > **Integrations** > **API**
3. Generate or copy your API key

Your API key is tied to your club and has full read/write access to your club's data.

## Making Requests

All requests require the `X-Api-Key` header:

```
X-Api-Key: your-api-key-here
```

## Base URLs

| Version | Base URL | Status |
|---------|----------|--------|
| V1 (current) | `https://api.helloclub.com` | Active |
| V2 (upcoming) | `https://api-v2.helloclub.com` | Rolling out per-club |

V2 activates after your club portal is upgraded by Hello Club. See the [V2 Migration Guide](v2-migration.md) for details.

## Example Request

```python
import os
import httpx

API_KEY = os.environ["HELLOCLUB_API_KEY"]

response = httpx.get(
    "https://api.helloclub.com/event",
    headers={"X-Api-Key": API_KEY},
    params={"limit": 10},
)
response.raise_for_status()
data = response.json()

print(f"Found {data['meta']['total']} events")
for event in data["events"]:
    print(f"  {event['name']} — {event['startDate']}")
```

## Environment Variable

We recommend storing your API key as an environment variable:

```bash
# Linux/macOS
export HELLOCLUB_API_KEY="your-api-key-here"

# Windows (PowerShell)
$env:HELLOCLUB_API_KEY = "your-api-key-here"

# Windows (cmd)
set HELLOCLUB_API_KEY=your-api-key-here
```

All example scripts in this repo read from `HELLOCLUB_API_KEY`.

## Response Format

Successful responses return JSON. List endpoints wrap results in an object with a `meta` field for pagination:

```json
{
  "events": [...],
  "meta": {
    "total": 971,
    "limit": 100,
    "offset": 0
  }
}
```

The wrapper key varies by entity: `events`, `members`, `attendees`, `memberships`, `transactions`, `bookings`, etc.

## Error Responses

| Status | Meaning |
|--------|---------|
| 400 | Bad request (invalid parameters) |
| 401 | Invalid or missing API key |
| 404 | Resource not found |
| 422 | Validation error (e.g. missing required date params) |
| 429 | Rate limit exceeded (30 req/min) |
| 500+ | Server error |

Error responses include a message:

```json
{
  "error": "TooManyRequestsError",
  "message": "You have exceeded the API rate limit of 30 requests per minute"
}
```
