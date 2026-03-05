# Gotchas & Known Issues

Common pitfalls when working with the Hello Club API, discovered through live testing.

## Removed Endpoint: `/event/upcoming`

`GET /event/upcoming` returns `400 BadRequestError: "Invalid request"` for **all parameter combinations**. Hello Club have confirmed this is not a bug — the endpoint has been removed, though it remains in the outdated OpenAPI spec. The same behaviour applies in V2.

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

The spec says `fromDate`/`toDate` are optional for these endpoints, but the API returns **422** without them. Hello Club have confirmed this is intentional — the spec is outdated, not the API. The same behaviour applies in V2.

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

## Updating Member Groups: PUT Only, Objects Only

To update a member's groups, you **must** use `PUT /member/{id}` (not PATCH). The `groups` field is rejected by PATCH with a 422 "not allowed" error.

The `groups` field must be an **array of objects** with at least `id`, `name`, and `color`. Sending an array of ID strings returns 422 ("must be of type object").

```python
# WORKS — PUT with group objects
client._request("PUT", f"/member/{member_id}", json={
    "firstName": member["firstName"],
    "lastName": member["lastName"],
    "gender": member["gender"],
    "groups": [
        {"id": "abc123", "name": "Pickleball", "color": "#cc0c98"},
        {"id": "def456", "name": "Badminton", "color": "#ff0000"},
    ],
})

# FAILS (422) — PATCH with groups
client._request("PATCH", f"/member/{member_id}", json={"groups": [...]})

# FAILS (422) — PUT with ID strings
client._request("PUT", f"/member/{member_id}", json={"groups": ["abc123"]})
```

> **Note:** PUT requires `firstName`, `lastName`, and `gender` as mandatory fields. GET the member first to preserve existing values.

> **Tested:** Mar 2026. Round-trip verified (add group → confirm → remove → confirm).

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

## Unstable Pagination with Non-Default Sort Orders

**Severity: High** — causes silent data loss when paginating through members.

Sorting `GET /member` by anything other than the default (`-lastOnline`) produces **duplicate records** across pages, causing other members to be silently skipped. The offset-based pagination uses an unstable sort when records share the same sort value, so the same member can appear at different offsets on subsequent pages.

**Root cause (confirmed by Hello Club, Mar 2026):** The sort is unstable when multiple records share the same value for the sort field. To ensure stable sorting, append `,id` to your sort specifier (e.g. `sort=-updatedAt,id`). Hello Club may change the API to do this automatically in future.

### Test Results (Mar 2026, 2,143 total members)

| Sort | Records Returned | Unique Members | Duplicates | Missing Members |
|------|----------------:|---------------:|-----------:|----------------:|
| `-lastOnline` (default) | 2,143 | 2,115 | 28 | 0 |
| `-updatedAt` | 2,143 | 1,423 | 720 | 697 |
| `updatedAt` (ascending) | 2,143 | 1,060 | 1,083 | 1,060 |

### How to Reproduce

Fetch page 1 and page 2 with `sort=-updatedAt` and compare member IDs:

```python
page1 = client.get("/member", params={"limit": 100, "offset": 0, "sort": "-updatedAt"})
page2 = client.get("/member", params={"limit": 100, "offset": 100, "sort": "-updatedAt"})

ids_1 = {m["id"] for m in page1["members"]}
ids_2 = {m["id"] for m in page2["members"]}

overlap = ids_1 & ids_2
print(f"Members on BOTH pages: {len(overlap)}")  # Expected: 0, Actual: 41
```

Adjacent pages share **41 out of 100** members. Some members appear up to **6 times** across the full result set, while ~700 members never appear at all.

The same test with the default sort shows **0 overlap** — pagination is stable.

### Impact

Any code that paginates through all members using `sort=-updatedAt` (e.g., for incremental sync based on last-modified date) will:
1. Miss ~33% of members entirely
2. Process ~33% of members multiple times
3. Return a "complete" result set that is actually incomplete

### Workaround

**Fix (confirmed by Hello Club, Mar 2026):** Append `,id` to your sort to make pagination stable:

```python
# Stable sort — no duplicates or missing records
page = client.get("/member", params={
    "limit": 100,
    "offset": 0,
    "sort": "-updatedAt,id",  # id tiebreaker ensures stable ordering
})
```

**For incremental sync**, Hello Club also recommends filtering by `updatedAt` instead of sorting by it:

```python
# Fetch only members updated since your last sync
last_sync = "2026-03-01T00:00:00Z"  # store and update this after each sync
members = {}
offset = 0
while True:
    page = client.get("/member", params={
        "limit": 100,
        "offset": offset,
        "updatedAt": last_sync,
    })
    for m in page["members"]:
        members[m["id"]] = m
    if len(page["members"]) < 100:
        break
    offset += 100
```

**For full dataset fetches**, use the default sort (`-lastOnline`) and deduplicate by member ID:

```python
members = {}
offset = 0
while True:
    page = client.get("/member", params={"limit": 100, "offset": offset})
    for m in page["members"]:
        members[m["id"]] = m  # upsert — handles the rare default-sort duplicates
    if len(page["members"]) < 100:
        break
    offset += 100
```

> **Note:** Even the default sort has ~28 duplicates out of 2,143 (1.3%), likely from members coming online during the paginated fetch. Always deduplicate by ID.

> **Tested:** Mar 2026 against a club with 2,143 members. Test script: [`scripts/test_api_sort_bug.py`](https://github.com/ispyisail/hc-group-fixer/blob/master/scripts/test_api_sort_bug.py)
