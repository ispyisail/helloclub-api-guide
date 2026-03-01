# Event Fields

**Endpoint:** `GET /event` | **Sample size:** 50 events (180-day range)

Fields marked **UNDOCUMENTED** are not in the official OpenAPI spec but are returned by the live API.

## Core Identity

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `id` | string (ObjectId) | 10/10 | Yes | Event ID |
| `series` | string (ObjectId) | 10/10 | Yes | Primary event ID if recurring series |
| `club` | string (ObjectId) | 10/10 | Yes | Club ID |
| `name` | string | 10/10 | Yes | Event name (e.g. "Monday Pickleball") |
| `slug` | string | 10/10 | **No** | URL-friendly slug |
| `publicPath` | string | 10/10 | **No** | Full public URL path |

## Activity & Areas

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `activity` | object | 10/10 | Yes | Activity reference |
| `activity.id` | string | 10/10 | Yes | Activity ID |
| `activity.name` | string | 10/10 | Yes | e.g. "Badminton Hall" |
| `activity.identifier` | string | 10/10 | Yes | e.g. "badminton-hall" |
| `activity.areaSingular` | string | 10/10 | Yes | e.g. "court" |
| `activity.areaPlural` | string | 10/10 | Yes | e.g. "courts" |
| `areas` | array | 10/10 | Yes | Linked areas |
| `areas[].id` | string | all | Yes | Area ID |
| `areas[].name` | string | all | Yes | e.g. "Court 1" |

## Categories

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `categories` | array | 10/10 | **No** | Event categories (not in spec) |
| `categories[].id` | string | 7/10 | **No** | Category ID |
| `categories[].name` | string | 7/10 | **No** | e.g. "Pickleball" |
| `categories[].color` | string | 7/10 | **No** | Hex color e.g. "#00ae28" |

## Date & Time

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `startDate` | string (ISO 8601) | 10/10 | Yes | Event start |
| `endDate` | string (ISO 8601) | 10/10 | Yes | Event end |
| `timezone` | string | 10/10 | Yes | e.g. "Pacific/Auckland" |
| `createdAt` | string (ISO 8601) | 10/10 | **No** | Creation timestamp |
| `updatedAt` | string (ISO 8601) | 10/10 | **No** | Last update timestamp |

## Event Type & Visibility

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `type` | string | 10/10 | Yes | "local" / "external" / "virtual" |
| `isLocal` | boolean | 10/10 | **No** | Virtual helper: type == "local" |
| `isExternal` | boolean | 10/10 | **No** | Virtual helper: type == "external" |
| `isVirtual` | boolean | 10/10 | **No** | Virtual helper: type == "virtual" |
| `isMultiDay` | boolean | 10/10 | Yes | Multi-day event |
| `isRecurring` | boolean | 10/10 | Yes | Recurring event |
| `isHidden` | boolean | 10/10 | Yes | Hidden from members |
| `isPublic` | boolean | 10/10 | Yes | Open to external guests |
| `showOnHomepage` | boolean | 10/10 | Yes | Shown on home page |
| `showAttendeeNames` | boolean | 10/10 | **No** | Show names of attendees |
| `showAttendanceNumbers` | boolean | 10/10 | **No** | Show attendance count |
| `isInterestEnabled` | boolean | 10/10 | **No** | Allow "interested" marking |
| `isLimitedSeries` | boolean | 10/10 | **No** | Series has a defined end |
| `hasLimitedRecurrence` | boolean | 10/10 | **No** | Recurrence is limited |

## Attendance & Capacity

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `maxAttendees` | integer | 10/10 | Yes | Max capacity |
| `numAttendees` | integer | 10/10 | Yes | Total signed up |
| `numAttended` | integer | 10/10 | Yes | Actually attended |
| `numInterested` | integer | 10/10 | Yes | People interested |
| `numSpacesLeft` | integer | 10/10 | **No** | Computed: maxAttendees - numAttendees |
| `hasSpacesLeft` | boolean | 10/10 | **No** | numSpacesLeft > 0 |
| `hasLimitedSpacesLeft` | boolean | 10/10 | **No** | Spaces running low |
| `lastAttendees` | array | 10/10 | Yes | Last 3 attendees (firstName, lastName, id) |

## Computed Booleans

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `hasAreas` | boolean | 10/10 | **No** | Has linked areas |
| `hasOrganisers` | boolean | 10/10 | **No** | Has assigned organisers |
| `hasMemberRules` | boolean | 10/10 | **No** | Has rules for members |
| `hasGuestRules` | boolean | 10/10 | **No** | Has rules for guests |

## Age Restrictions

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `minAge` | integer | 5/10 | Yes | Minimum age (null if unrestricted) |
| `maxAge` | integer | 4/10 | Yes | Maximum age (null if unrestricted) |
| `allowUnknownAge` | boolean | 5/10 | Yes | Allow unknown age attendees |

## Content & Media

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `description` | string | 6/10 | Yes | Markdown event description |
| `address` | object/null | 10/10 | Yes | Venue address (null for most) |
| `banner` | object | 4/10 | **No** | Event banner image |
| `banner.bucket` | string | 4/10 | **No** | S3 bucket |
| `banner.path` | string | 4/10 | **No** | Image path |
| `banner.url` | string | 4/10 | **No** | Full image URL |
| `notifyOrganisers` | boolean | 10/10 | Yes | Notify on new signup |

## Organisers

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `organisers` | array | 10/10 | Yes | Event organisers |
| `organisers[].id` | string | all | Yes | Member ID |
| `organisers[].firstName` | string | all | Yes | |
| `organisers[].lastName` | string | all | Yes | |
| `organisers[].color` | string | all | Yes | Avatar color |
| `organisers[].name` | string | all | **No** | Full name (virtual) |
| `organisers[].avatar` | object | some | Yes | Avatar image object |
| `organisers[].avatar.url` | string | some | **No** | Full image URL |

## Rules (Pricing)

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `rules` | array | 10/10 | Yes | Pricing rules |
| `rules[].id` | string | all | **No** | Rule ID |
| `rules[].type` | string | all | Yes | "free" / "fee" / "coupon" / "membership" |
| `rules[].constraint` | string | all | Yes | "all" / "with" / "without" / "specific" / "guest" |
| `rules[].memberships` | array (IDs) | all | Yes | Applicable membership IDs |
| `rules[].groups` | array (IDs) | all | **No** | Applicable group IDs |
| `rules[].couponTypes` | array (IDs) | all | Yes | Applicable coupon types |
| `rules[].fee` | number | all | Yes | Fee amount |
| `rules[].isEnabled` | boolean | all | Yes | Rule is active |
| `rules[].isSeries` | boolean | all | Yes | Applies to whole series |
| `rules[].isPayableInAdvance` | boolean | all | Yes | Advance payment allowed |
| `rules[].isRefundable` | boolean | all | Yes | Refundable |
| `rules[].isValid` | boolean | all | **No** | Currently valid (computed) |
| `rules[].isForMember` | boolean | all | **No** | Applies to members |
| `rules[].isForGuest` | boolean | all | **No** | Applies to guests |
| `rules[].requiresVaccination` | boolean | all | **No** | Vaccination required |
| `rules[].validFrom` | string/null | all | Yes | Validity start |
| `rules[].validTill` | string/null | all | Yes | Validity end |
| `rules[].label` | string | all | Yes | Custom label for "free" rules |
| `rules[].refundThreshold` | object | 6/10 | Yes | Refund time limit |
| `rules[].refundThreshold.amount` | integer | 5/10 | Yes | Amount |
| `rules[].refundThreshold.unit` | string | 5/10 | Yes | "minutes" / "hours" / "days" |
| `rules[].refundableUntil` | string | 5/10 | **No** | Computed refund deadline |

## Recurrence

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `recurrence` | object | 10/10 | Yes | Recurrence settings |
| `recurrence.frequency` | integer | 10/10 | Yes | e.g. 1 (every week) |
| `recurrence.interval` | string | 10/10 | Yes | "days" / "weeks" / "months" / "years" |
| `recurrence.monthlyDayOf` | string | 10/10 | Yes | "week" / "month" |
| `recurrence.days` | array (int) | 10/10 | Yes | Weekdays (1-7) |
| `recurrence.ends` | string | 10/10 | Yes | "amount" / "lastDate" / "never" |
| `recurrence.amount` | integer | 10/10 | Yes | Instances if ends="amount" |
| `recurrence.firstDate` | string | 10/10 | Yes | Series start date |
| `recurrence.lastDate` | string | 10/10 | Yes | Series end date |

## Notifications & Integrations

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `notifications` | array | 10/10 | Yes | Scheduled notifications |
| `notifications[].type` | string | 1/10 | Yes | "promotion" / "reminder" / "postEvent" |
| `notifications[].audience` | string | 1/10 | Yes | Target audience |
| `notifications[].subject` | string | 1/10 | Yes | Email subject |
| `notifications[].isEnabled` | boolean | 1/10 | Yes | Active |
| `notifications[].isSent` | boolean | 1/10 | **No** | Already sent |
| `notifications[].isEligible` | boolean | 1/10 | **No** | Eligible to send |
| `notifications[].dueDate` | string | 1/10 | Yes | Scheduled send date |
| `googleCalendar` | object | 4/10 | **No** | Google Calendar sync |
| `isOnGoogleCalendar` | boolean | 4/10 | **No** | Synced to Google Calendar |

## Other

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `questions` | array | 10/10 | Yes | Sign-up questions |
| `multiDay` | object/null | 6/10 | Yes | Multi-day details |
| `customFields` | object | 10/10 | Yes | Club-specific custom fields |
| `customFiles` | object | 10/10 | Yes | Custom file attachments |
