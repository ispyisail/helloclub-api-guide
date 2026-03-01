# Log Fields

Hello Club provides five log types. All require `fromDate` and `toDate` parameters (despite the spec saying they're optional for some).

## Access Log

**Endpoint:** `GET /accessLog` | **Sample size:** 100 records (of 1,625 in past 90 days)

Records door/tag events — when members scan their tags or use access control.

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `id` | string (ObjectId) | 100/100 | Yes | Log entry ID |
| `club` | string (ObjectId) | 100/100 | Yes | Club ID |
| `date` | string (ISO) | 100/100 | Yes | Event timestamp |
| `state` | string | 100/100 | Yes | "tag" / "button" / "auto" |
| `wasOpened` | boolean | 100/100 | Yes | Whether the door was opened |
| `duration` | integer | 100/100 | **No** | Duration in seconds |
| `reason` | string | 3/100 | **No** | e.g. "already open for event" |
| `door` | object | 100/100 | Yes | Door reference |
| `door.id` | string | 100/100 | Yes | Door identifier |
| `door.name` | string | 100/100 | Yes | e.g. "Entrance" |
| `member` | object | 69/100 | Yes | Member who accessed |
| `member.id` | string | 69/100 | Yes | Member ID |
| `member.name` | string | 69/100 | **No** | Full name (virtual) |
| `event` | object | 21/100 | **No** | Associated event |
| `tag` | object | 79/100 | Yes | Tag used |
| `tag.number` | string | 79/100 | Yes | e.g. "33011:00119" |
| `tag.type` | string | 79/100 | Yes | "tag" / "pin" |
| `tag.isMain` | boolean | 79/100 | **No** | Is main tag |

## Activity Log

**Endpoint:** `GET /activityLog` | **Sample size:** 100 records (of 1,146 in past 90 days)

Records area/court usage sessions — when courts are activated and when they stop.

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `id` | string (ObjectId) | 100/100 | Yes | Log entry ID |
| `club` | string (ObjectId) | 100/100 | Yes | Club ID |
| `date` | string (ISO) | 100/100 | Yes | Session start time |
| `duration` | integer | 100/100 | Yes | Duration in seconds |
| `state` | string | 100/100 | Yes | "event" / "booking" / "tag" / "manual" |
| `isProcessed` | boolean | 100/100 | **No** | Processing complete |
| `isStopped` | boolean | 7/100 | **No** | Manually stopped |
| `activity` | object | 100/100 | Yes | Activity reference |
| `activity.name` | string | 100/100 | Yes | e.g. "Badminton Hall" |
| `area` | object | 100/100 | Yes | Area/court reference |
| `area.name` | string | 100/100 | Yes | e.g. "Court 4" |
| `event` | object | 73/100 | Yes | Associated event |
| `members` | array | 100/100 | Yes | Members involved |
| `tags` | array | 100/100 | **No** | Tags used |
| `stoppedBy` | object | 100/100 | **No** | How session was stopped |
| `stoppedBy.member` | object | 7/100 | **No** | Member who stopped it |
| `stoppedBy.tag` | object | 7/100 | **No** | Tag used to stop |
| `stoppedOn` | string (ISO) | 7/100 | **No** | Stop timestamp |
| `bookings` | array | 100/100 | **No** | Related booking IDs |
| `transactions` | array | 100/100 | **No** | Related transaction IDs |

## Audit Log

**Endpoint:** `GET /auditLog` | **Sample size:** 100 records (of 6,776 in past 90 days)

Records all admin/system actions. The `data` field is **polymorphic** — its structure depends on the action type.

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `id` | string (ObjectId) | 100/100 | Yes | Audit entry ID |
| `club` | string (ObjectId) | 100/100 | Yes | Club ID |
| `date` | string (ISO) | 100/100 | Yes | Action timestamp |
| `type` | string | 100/100 | Yes | "update" / "create" / "delete" / "restore" |
| `action` | string | 100/100 | Yes | Human-readable description |
| `ip` | string | 100/100 | **No** | IP address of actor |
| `bySuper` | boolean | 100/100 | **No** | Action by superadmin |
| `member` | object | 100/100 | Yes | Actor |
| `member.name` | string | 100/100 | **No** | Full name (virtual) |
| `item` | object | 98/100 | Yes | Entity being modified |
| `item.model` | string | 98/100 | Yes | "Member" / "EventAttendee" / "Booking" / etc. |
| `item.name` | string | 98/100 | Yes | Entity display name |
| `parent` | object | 80/100 | **No** | Parent entity |
| `parent.model` | string | 80/100 | **No** | "Event" / "Member" / etc. |
| `data` | object | varies | Yes | Entity snapshot (polymorphic, 150+ unique paths) |

## Check-In Log

**Endpoint:** `GET /checkInLog` | **Sample size:** 2 records (of 2 total in past year)

Records manual check-ins (rarely used if tag-based access is primary).

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `id` | string (ObjectId) | 2/2 | Yes | Log entry ID |
| `club` | string (ObjectId) | 2/2 | Yes | Club ID |
| `date` | string (ISO) | 2/2 | Yes | Check-in timestamp |
| `type` | string | 2/2 | Yes | "Check-in" |
| `wasCheckedIn` | boolean | 2/2 | **No** | Whether check-in succeeded |
| `reason` | string | 2/2 | **No** | e.g. "Manual check-in" |
| `member` | object | 2/2 | Yes | Member who checked in |
| `member.name` | string | 2/2 | **No** | Full name (virtual) |

## Email Log

**Endpoint:** `GET /emailLog` | **Sample size:** 100 records (of 8,895 in past 90 days)

Records all emails sent by Hello Club.

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `id` | string (ObjectId) | 100/100 | Yes | Log entry ID |
| `club` | string (ObjectId) | 100/100 | Yes | Club ID |
| `date` | string (ISO) | 100/100 | Yes | Send timestamp |
| `to` | string | 100/100 | Yes | Recipient email |
| `subject` | string | 100/100 | Yes | Email subject |
| `category` | string | 100/100 | **No** | e.g. "Transaction reminder" |
| `status` | string | 100/100 | **No** | "processed" / "delivered" / "open" / "click" |
| `messageId` | string | 100/100 | **No** | Unique message ID |
| `reason` | string | 1/100 | **No** | Failure reason (only on errors) |
