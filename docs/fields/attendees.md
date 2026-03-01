# Event Attendee Fields

**Endpoint:** `GET /eventAttendee` | **Sample size:** 100 attendees (broad sample, sorted by most recent sign-up)

Fields marked **UNDOCUMENTED** are not in the official OpenAPI spec but are returned by the live API.

## Core Identity

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `id` | string (ObjectId) | 20/20 | Yes | Attendee record ID |
| `club` | string (ObjectId) | 20/20 | Yes | Club ID |
| `personId` | string | 20/20 | Yes | Stringified member or guest ID |
| `name` | string | 20/20 | Yes | Full name (virtual) |
| `firstName` | string | 20/20 | Yes | First name (virtual) |
| `lastName` | string | 20/20 | Yes | Last name (virtual) |
| `email` | string | 20/20 | Yes | Email (virtual) |
| `phone` | string | 19/20 | Yes | Phone (virtual) |

## Event Reference

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `event` | object | 20/20 | Yes | Event reference |
| `event.id` | string | 20/20 | Yes | Event ID |
| `event.series` | string | 20/20 | Yes | Event series ID |
| `event.name` | string | 20/20 | Yes | Event name |
| `event.startDate` | string | 20/20 | Yes | Event start |
| `event.endDate` | string | 20/20 | Yes | Event end |

## Member / Guest Reference

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `member` | object/null | 19/20 | Yes | Member reference (null for guests) |
| `member.id` | string | 19/20 | Yes | Member ID |
| `member.firstName` | string | 19/20 | Yes | |
| `member.lastName` | string | 19/20 | Yes | |
| `member.email` | string | 19/20 | Yes | |
| `member.mobile` | string | 19/20 | Yes | |
| `member.color` | string | 19/20 | Yes | Avatar color |
| `member.name` | string | 19/20 | **No** | Full name (virtual) |
| `member.avatar` | object | 3/20 | **No** | Avatar image |
| `member.vaccination` | object | 19/20 | **No** | Vaccination status |
| `guest` | object/null | 1/20 | Yes | Guest reference (null for members) |
| `guest.id` | string | 1/20 | Yes | Guest ID |
| `guest.firstName` | string | 1/20 | Yes | |
| `guest.lastName` | string | 1/20 | Yes | |
| `guest.name` | string | 1/20 | **No** | Full name (virtual) |

## Dates

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `signUpDate` | string (ISO) | 20/20 | Yes | When they signed up |
| `createdAt` | string (ISO) | 20/20 | **No** | Record creation timestamp |
| `updatedAt` | string (ISO) | 20/20 | **No** | Last update timestamp |
| `pushNotificationSent` | string (ISO) | 18/20 | Yes | Notification sent date |

## Series Reference

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `series` | string (ObjectId) | 40/100 | Yes | Reference to primary attendee if recurring series |

## Attendance Status

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `hasAttended` | boolean | 20/20 | Yes | Actually attended |
| `isSeries` | boolean | 20/20 | Yes | Series attendance |
| `isCreatedByAdmin` | boolean | 20/20 | Yes | Admin-created |
| `isMember` | boolean | 20/20 | Yes | Is a club member |
| `isGuest` | boolean | 20/20 | Yes | Is external guest |
| `isVaccinationValid` | boolean | 20/20 | **No** | Vaccination valid |

## Payment & Fees

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `isPaid` | boolean | 20/20 | Yes | Payment received |
| `isRefunded` | boolean | 20/20 | **No** | Has been refunded |
| `isStillRefundable` | boolean | 20/20 | **No** | Can still be refunded |
| `needsPayment` | boolean | 20/20 | Yes | Outstanding payment |
| `transaction` | string/null | 6/20 | Yes | Linked transaction ID |
| `answers` | array | 20/20 | Yes | Question answers |

## Rule (Applied Pricing)

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `rule` | object | 20/20 | Yes | Applied pricing rule |
| `rule.id` | string | 20/20 | **No** | Rule instance ID |
| `rule.type` | string | 20/20 | Yes | "free" / "fee" / "coupon" / "membership" |
| `rule.fee` | number | 20/20 | Yes | Fee charged |
| `rule.isPayableInAdvance` | boolean | 20/20 | Yes | Advance payment allowed |
| `rule.isRefundable` | boolean | 20/20 | Yes | Refundable |
| `rule.isSeries` | boolean | 20/20 | **No** | Series rule |
| `rule.isStillRefundable` | boolean | 20/20 | **No** | Currently refundable |
| `rule.refundableUntil` | string/null | 20/20 | **No** | Refund deadline |

## Fee Booleans

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `hasFee` | boolean | 20/20 | Yes | Has a fee |
| `hasFeeRule` | boolean | 20/20 | Yes | Fee rule applied |
| `hasFreeRule` | boolean | 20/20 | Yes | Free rule applied |
| `hasMembershipRule` | boolean | 20/20 | Yes | Membership rule applied |
| `hasCouponRule` | boolean | 20/20 | Yes | Coupon rule applied |
| `hasPaidFee` | boolean | 20/20 | Yes | Fee has been paid |
| `hasUsedCoupon` | boolean | 20/20 | Yes | Coupon was used |
| `hasUsedSubscription` | boolean | 20/20 | Yes | Subscription was used |
