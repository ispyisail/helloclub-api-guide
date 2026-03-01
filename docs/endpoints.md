# API Endpoints

> **Tested:** Feb 2026 | **61 endpoint variations tested** | **17 endpoints working, 1 broken**

## Endpoint Status

### Events

| Method | Path | Status | Description |
|--------|------|--------|-------------|
| GET | `/event` | **Working** | Query events (supports fromDate, toDate, many filters) |
| GET | `/event/upcoming` | **Broken (400)** | Returns 400 for all params. Use `/event` with date range. |
| GET | `/event/{id}` | **Working** | Get single event by ID |
| POST | `/event` | Documented | Create event |
| DELETE | `/event/{id}` | Documented | Delete event |

### Members

| Method | Path | Status | Description |
|--------|------|--------|-------------|
| GET | `/member` | **Working** | Query members (many filter params) |
| GET | `/member/{id}` | **Working** | Get single member |
| POST | `/member` | **Working** | Create member |
| PUT | `/member/{id}` | Documented | Full update member |
| PATCH | `/member/{id}` | Documented | Partial update member |

### Event Attendees

| Method | Path | Status | Description |
|--------|------|--------|-------------|
| GET | `/eventAttendee` | **Working** | Query attendees (event, member, guest filters) |
| POST | `/eventAttendee` | **Working** | Create attendee (register for event) |

### Memberships

| Method | Path | Status | Description |
|--------|------|--------|-------------|
| GET | `/membership` | **Working** | Query all membership types |
| GET | `/membership/{id}` | **Working** | Get single membership type |

### Other Endpoints

| Method | Path | Status | Records | Description |
|--------|------|--------|---------|-------------|
| GET | `/user/me` | **Working** | 1 | Authenticated user info |
| GET | `/transaction` | **Working** | 14,714 | Query transactions |
| GET | `/booking` | **Working** | 640 (90d) | Query bookings |
| GET | `/page` | **Working** | 0 | Query custom pages |
| GET | `/accessLog` | **Working** | 1,625 (90d) | Requires fromDate + toDate |
| GET | `/activityLog` | **Working** | 1,146 (90d) | Requires fromDate + toDate |
| GET | `/auditLog` | **Working** | 6,776 (90d) | Requires fromDate + toDate |
| GET | `/checkInLog` | **Working** | 2 (365d) | Requires fromDate + toDate (spec says optional) |
| GET | `/emailLog` | **Working** | 8,895 (90d) | Requires fromDate + toDate (spec says optional) |

## Common Query Parameters

These parameters are supported across most GET list endpoints:

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer (0-100) | Results per page (default: 100) |
| `offset` | integer | Pagination offset |
| `sort` | string | Sort field (prefix `-` for descending, e.g. `-startDate`) |
| `fields` | string | Comma-separated field list to restrict response |
| `search` | string | Free text search |

### Event-Specific Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `fromDate` | ISO 8601 | Filter events starting from this date |
| `toDate` | ISO 8601 | Filter events ending before this date |
| `activity` | string | Filter by activity ID |

### Member-Specific Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `membership` | string | Filter by membership type ID |
| `group` | string | Filter by group ID |
| `updatedAt` | ISO 8601 | Filter by last update date |

### Event Attendee Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `event` | string | Filter by event ID |
| `member` | string | Filter by member ID |
| `guest` | boolean | Filter for guests only |

### Transaction Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `isPaid` | boolean | Filter by payment status |
| `isCredit` | boolean | Filter for credits/refunds |
| `type` | string | Filter by type (subscription, event, booking, etc.) |
| `member` | string | Filter by member ID |

### Log Endpoints (Access, Activity, Audit, Check-In, Email)

| Parameter | Type | Description |
|-----------|------|-------------|
| `fromDate` | ISO 8601 | **Required** — start date for log range |
| `toDate` | ISO 8601 | **Required** — end date for log range |

> **Note:** The spec says `fromDate`/`toDate` are optional for checkInLog and emailLog, but the API returns 422 without them.

## Response Structure

All list endpoints return results wrapped in an object:

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

The wrapper key matches the entity type: `events`, `members`, `attendees`, `memberships`, `transactions`, `bookings`, `accessLogs`, `activityLogs`, `auditLogs`, `checkInLogs`, `emailLogs`.

Single-entity endpoints (e.g. `GET /event/{id}`) return the entity directly without wrapping.
