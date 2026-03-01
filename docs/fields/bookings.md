# Booking Fields

**Endpoint:** `GET /booking` | **Sample size:** 100 bookings (of 640 in past 90 days)

Fields marked **UNDOCUMENTED** are not in the official OpenAPI spec but are returned by the live API.

## Core

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `id` | string (ObjectId) | 100/100 | Yes | Booking ID |
| `club` | string (ObjectId) | 100/100 | Yes | Club ID |
| `startDate` | string (ISO) | 100/100 | Yes | Booking start |
| `endDate` | string (ISO) | 100/100 | Yes | Booking end |
| `timezone` | string | 100/100 | Yes | e.g. "Pacific/Auckland" |
| `series` | string (ObjectId) | 8/100 | Yes | Series ID (if recurring) |
| `emailConfirmationSent` | string (ISO) | 100/100 | **No** | Confirmation email time |

## Activity, Area & Mode

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `activity` | object | 100/100 | Yes | Activity reference |
| `activity.id` | string | 100/100 | Yes | Activity ID |
| `activity.name` | string | 100/100 | Yes | e.g. "Function Areas" |
| `activity.identifier` | string | 100/100 | Yes | e.g. "function-areas" |
| `activity.areaSingular` | string | 100/100 | Yes | e.g. "room" |
| `activity.areaPlural` | string | 100/100 | Yes | e.g. "rooms" |
| `area` | object | 100/100 | Yes | Area reference |
| `area.id` | string | 100/100 | Yes | Area ID |
| `area.name` | string | 100/100 | Yes | e.g. "Dance Room" |
| `mode` | object | 100/100 | Yes | Booking mode |
| `mode.id` | string | 100/100 | Yes | Mode ID |
| `mode.name` | string | 100/100 | Yes | e.g. "Function Room" |

## Owner & Members

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `owner` | object | 100/100 | Yes | Booking owner |
| `owner.id` | string | 100/100 | Yes | Member ID |
| `owner.firstName` | string | 100/100 | Yes | |
| `owner.lastName` | string | 100/100 | Yes | |
| `owner.name` | string | 100/100 | **No** | Full name (virtual) |
| `members` | array | 100/100 | Yes | Members in booking |
| `members[].id` | string | 100/100 | Yes | Member ID |
| `members[].firstName` | string | 100/100 | Yes | |
| `members[].lastName` | string | 99/100 | Yes | |
| `members[].name` | string | 100/100 | **No** | Full name (virtual) |
| `members[].color` | string | 100/100 | Yes | Avatar color |
| `members[].avatar` | object | 25/100 | Yes | Avatar image |
| `members[].avatar.url` | string | 25/100 | **No** | Full image URL |
| `hasMembers` | boolean | 100/100 | **No** | Has members assigned |
| `visitors` | array | 100/100 | Yes | External guests |
| `hasVisitors` | boolean | 100/100 | **No** | Has visitors |
| `hideMemberDetails` | boolean | 100/100 | **No** | Hide member details |

## Status & Flags

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `isTemporary` | boolean | 100/100 | **No** | Temporary/pending booking |
| `isFeeWaived` | boolean | 100/100 | **No** | Fee has been waived |
| `isRefundable` | boolean | 100/100 | **No** | Can be refunded |
| `isRefunded` | boolean | 100/100 | **No** | Has been refunded |
| `isUsedForSession` | boolean | 76/100 | **No** | Used for an activity session |
| `isRemoved` | boolean | 8/100 | **No** | Booking was removed |
| `removalReason` | string | 1/100 | **No** | e.g. "Not paid in time" |
| `removedBy` | object | 8/100 | **No** | Who removed the booking |
| `removedBy.name` | string | 7/100 | **No** | Full name |
| `removedOn` | string (ISO) | 8/100 | **No** | Removal timestamp |

## Recurrence

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `recurrence` | object | 100/100 | Yes | Recurrence settings |
| `recurrence.frequency` | integer | 8/100 | Yes | Repeat frequency |
| `recurrence.interval` | string | 8/100 | Yes | "weeks", "days", etc. |
| `recurrence.days` | array (int) | 8/100 | Yes | Weekdays (1-7) |
| `recurrence.ends` | string | 8/100 | Yes | "lastDate" / "amount" / "never" |
| `isLimitedSeries` | boolean | 100/100 | **No** | Series has defined end |
| `hasLimitedRecurrence` | boolean | 100/100 | **No** | Recurrence is limited |

## Tags & Transactions

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `tags` | array | 100/100 | **No** | Access tags used |
| `tags[].id` | string | 53/100 | **No** | Tag ID |
| `tags[].member` | string | 53/100 | **No** | Member who used tag |
| `transaction` | string (ObjectId) | 69/100 | Yes | Linked transaction ID |
| `activityLogs` | array | 100/100 | **No** | Linked activity log IDs |
