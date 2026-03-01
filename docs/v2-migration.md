# V2 API Migration Guide

> **Source:** [Hello Club — V2: Transitioning the API](https://help.helloclub.com/en/articles/9978567-v2-transitioning-the-api)

Hello Club is migrating to a V2 API. The transition activates after your club portal is upgraded by Hello Club. All fields documented in this guide remain relevant — the changes below are additive.

## Domain Change

| Version | Base URL |
|---------|----------|
| V1 (current) | `https://api.helloclub.com` |
| V2 (new) | `https://api-v2.helloclub.com` |

## Endpoint Pluralisation

All endpoints switch to plural forms:

| V1 (current) | V2 (new) |
|---|---|
| `GET /event` | `GET /events` |
| `GET /member` | `GET /members` |
| `GET /eventAttendee` | `GET /eventAttendees` |
| `GET /membership` | `GET /memberships` |
| `GET /transaction` | `GET /transactions` |
| `GET /booking` | `GET /bookings` |
| `GET /accessLog` | `GET /accessLogs` |
| `GET /activityLog` | `GET /activityLogs` |
| `GET /auditLog` | `GET /auditLogs` |
| `GET /checkInLog` | `GET /checkInLogs` |
| `GET /emailLog` | `GET /emailLogs` |

## HTTP Method Changes

| Operation | V1 | V2 |
|-----------|----|----|
| Update a resource | `PUT /member/{id}` | `PATCH /members/{id}` |

## Terminology Renames

Field and entity naming changes throughout the API:

| V1 term | V2 term | Impact |
|---|---|---|
| `club` | `org` | Field names referencing club IDs |
| `member` | `profile` | Endpoint paths and response fields |
| `membership` | `membershipType` | What V1 calls "membership types" |
| `subscription` | `membership` | What V1 calls "subscriptions" on members |

## Response Wrapper Key Changes

Since entity names change, the JSON wrapper keys in list responses likely change too:

| V1 wrapper key | V2 wrapper key (expected) |
|---|---|
| `"events"` | `"events"` (unchanged) |
| `"members"` | `"profiles"` |
| `"attendees"` | `"eventAttendees"` |
| `"memberships"` | `"membershipTypes"` |
| `"transactions"` | `"transactions"` (unchanged) |
| `"bookings"` | `"bookings"` (unchanged) |

> **Note:** These wrapper key changes are inferred from the terminology renames. Test against the V2 API after your club portal is upgraded to confirm the exact keys.

## Profile Creation Change

When creating profiles (members) in V2, a new `type` property is required:

```python
# V1
client.post("/member", json={
    "firstName": "Jane",
    "lastName": "Smith",
    "gender": "female",
})

# V2
client.post("/members", json={
    "type": "person",  # NEW — required in V2
    "firstName": "Jane",
    "lastName": "Smith",
    "gender": "female",
})
```

## Address Structure Update

V2 standardises address fields to:

- `line1`, `line2`, `suburb`, `postalCode`, `city`, `state`, `country`

This aligns with what the V1 API already returns in practice (the spec had `streetNumber` + `streetName`, but the live API already uses `line1` + `line2`).

## Rate Limiting Update

- Rate limit remains **30 requests/minute**
- V2 adds a **`Retry-After` header** on 429 responses (value in seconds)
- Use the header value dynamically instead of fixed backoff delays

## Migration Checklist

1. Update base URL from `api.helloclub.com` to `api-v2.helloclub.com`
2. Update all endpoint paths to plural forms (e.g. `/event` → `/events`)
3. Change PUT calls to PATCH for update operations
4. Use `Retry-After` header value for 429 backoff
5. Rename field references: `club` → `org`, `member` → `profile`
6. Add `type: "person"` to profile/member creation requests
7. Update response parsing for renamed wrapper keys
8. Test after your club portal is upgraded — changes only apply once Hello Club upgrades your portal

## Side-by-Side Example

### Fetching Events

```python
# V1
response = httpx.get(
    "https://api.helloclub.com/event",
    headers={"X-Api-Key": API_KEY},
    params={"fromDate": "2026-03-01T00:00:00Z", "limit": 10},
)
events = response.json()["events"]

# V2
response = httpx.get(
    "https://api-v2.helloclub.com/events",
    headers={"X-Api-Key": API_KEY},
    params={"fromDate": "2026-03-01T00:00:00Z", "limit": 10},
)
events = response.json()["events"]
```

### Updating a Member

```python
# V1
httpx.put(
    f"https://api.helloclub.com/member/{member_id}",
    headers={"X-Api-Key": API_KEY},
    json={"firstName": "Jane"},
)

# V2
httpx.patch(
    f"https://api-v2.helloclub.com/members/{member_id}",
    headers={"X-Api-Key": API_KEY},
    json={"firstName": "Jane"},
)
```
