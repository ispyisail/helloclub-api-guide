# Gotchas & Known Issues

Common pitfalls when working with the Hello Club API, discovered through live testing.

## Broken Endpoint: `/event/upcoming`

`GET /event/upcoming` returns `400 BadRequestError: "Invalid request"` for **all parameter combinations**. This endpoint appears to have been removed or disabled.

**Workaround:** Use `GET /event` with `fromDate` and `toDate`:

```python
from datetime import datetime, timedelta, timezone

now = datetime.now(timezone.utc)
events = client.get("/event", params={
    "fromDate": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "toDate": (now + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "sort": "startDate",
})
```

> **Note:** Use `strftime("%Y-%m-%dT%H:%M:%SZ")` rather than `isoformat()`. Python's `isoformat()` includes microseconds and `+00:00` offset which the API may not accept.

## Date-Required Endpoints (Spec Says Optional)

The spec says `fromDate`/`toDate` are optional for these endpoints, but the API returns **422** without them:

- `GET /checkInLog` — returns 422 without dates
- `GET /emailLog` — returns 422 without dates

**Fix:** Always provide both `fromDate` and `toDate`:

```python
logs = client.get("/checkInLog", params={
    "fromDate": "2025-01-01T00:00:00Z",
    "toDate": "2026-03-01T00:00:00Z",
})
```

## OpenAPI Spec Is ~40% Incomplete

The official spec (version 2021-08-30) is significantly out of date. Roughly 40% of fields returned by the live API are undocumented. Key areas:

- Event `categories` array (name, color, id) — completely absent from spec
- Member `grades`, `circles`, `groups` (expanded objects), `directory`, `vaccination`
- Attendee `isStillRefundable`, `rule.refundableUntil`
- Computed booleans like `hasSpacesLeft`, `hasMembers`, `canSignIn`
- Full `tax` objects on transactions
- Activity log `stoppedBy` details

**Recommendation:** Use the [field reference docs](fields/) in this guide instead of the spec, or run the [field discovery script](../examples/field_discovery.py) against your own club.

## Field Renames Since Spec

Several fields were renamed in the live API compared to the spec:

| Spec Field | Actual Field | Entity |
|-----------|-------------|--------|
| `hash` | `intercomHash` | Member |
| `tagLastUsed` | `lastTagUse` | Member |
| `welcomeEmailLastSent` | `lastWelcomeEmail` | Member |
| `lowAccountCreditEmailLastSent` | `lastLowAccountCreditWarning` | Member |
| `group` (singular ID) | `groups` (array of objects) | Member |
| `canBeRefunded` | `isStillRefundable` | Attendee |
| `privacy` (single object) | `directory` / `staff` / `highlight` | Member |

## Address Format Change

The spec documents address fields as `streetNumber` + `streetName`, but the API returns:

```json
{
  "address": {
    "line1": "123 Main Street",
    "line2": "Unit 4",
    "suburb": "Kensington",
    "city": "Whangarei",
    "state": "Northland",
    "postalCode": "0112",
    "country": "New Zealand",
    "formatted": "123 Main Street, Kensington, Whangarei 0112",
    "mapsLink": "https://www.google.com/maps/...",
    "embedLink": "https://www.google.com/maps/embed/...",
    "placeId": "ChIJ..."
  }
}
```

The `formatted`, `mapsLink`, `embedLink`, and `placeId` fields are all undocumented.

## Date Format: DOB as Integer

Member `dob` (date of birth) is an **integer** in `YYYYMMDD` format, not an ISO 8601 string:

```json
{
  "dob": 19850315
}
```

Parse it as: year=1985, month=03, day=15.

## Pagination Meta

List responses include a `meta` object, but the wrapper key varies by entity type. Don't assume a fixed key:

| Endpoint | Wrapper Key |
|----------|-------------|
| `/event` | `events` |
| `/member` | `members` |
| `/eventAttendee` | `attendees` |
| `/membership` | `memberships` |
| `/transaction` | `transactions` |
| `/booking` | `bookings` |

## Custom Fields Are Dynamic

Both events and members have a `customFields` object with club-configured fields. These vary completely between clubs. Don't hardcode field names — use the [field discovery script](../examples/field_discovery.py) to find your club's custom fields.

## Rate Limit Applies Per API Key

The 30 req/min limit is per API key, not per IP. Multiple applications sharing the same key share the same rate limit budget.

## Empty Arrays vs Null

The API is inconsistent with empty values:
- Some fields return `[]` when empty, others return `null`
- Some string fields return `""`, others return `null`
- The `guest` field on attendees is `null` for members, and `member` is `null` for guests

Always check for both `null` and empty values when parsing.
