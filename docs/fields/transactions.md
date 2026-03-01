# Transaction Fields

**Endpoint:** `GET /transaction` | **Sample size:** 100 transactions (of 14,714 total)

Fields marked **UNDOCUMENTED** are not in the official OpenAPI spec but are returned by the live API.

## Core

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `id` | string (ObjectId) | 100/100 | Yes | Transaction ID |
| `club` | string (ObjectId) | 100/100 | Yes | Club ID |
| `type` | string | 100/100 | Yes | "subscription" / "event" / "booking" / "accountCredit" / "custom" |
| `date` | string (ISO) | 100/100 | Yes | Transaction date |
| `dueDate` | string (ISO) | 100/100 | **No** | Payment due date |
| `details` | string | 100/100 | Yes | Description (e.g. "Junior Club membership") |
| `detailsShort` | string | 100/100 | **No** | Shortened description |
| `invoiceNumber` | string | 100/100 | Yes | e.g. "INV-0103" |
| `createdAt` | string (ISO) | 100/100 | **No** | Creation timestamp |
| `updatedAt` | string (ISO) | 100/100 | **No** | Last update timestamp |

## Financial

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `amount` | integer | 100/100 | Yes | Amount in cents |
| `isPaid` | boolean | 100/100 | Yes | Payment received |
| `isCredit` | boolean | 100/100 | Yes | Is a credit (refund/top-up) |
| `isForAccountCredit` | boolean | 100/100 | **No** | Account credit transaction |
| `autoCollect` | boolean | 100/100 | **No** | Auto-collection enabled |
| `canPayWithAccountCredit` | boolean | 100/100 | **No** | Can use account credit |
| `canSplit` | boolean | 100/100 | **No** | Can be split |
| `isMuted` | boolean | 100/100 | **No** | Notifications muted |
| `isMultiLine` | boolean | 100/100 | **No** | Multi-line invoice |

## Tax

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `tax` | object | 100/100 | **No** | Tax details |
| `tax.type` | string | 100/100 | **No** | Tax type (e.g. "gst") |
| `tax.percentage` | integer | 100/100 | **No** | Tax rate (e.g. 15) |
| `tax.amount` | float | 100/100 | **No** | Tax amount |

## Member / Guest Reference

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `isForMember` | boolean | 100/100 | **No** | Transaction for a member |
| `isForGuest` | boolean | 100/100 | **No** | Transaction for a guest |
| `member` | object | 77/100 | Yes | Member reference |
| `member.id` | string | 77/100 | Yes | Member ID |
| `member.firstName` | string | 77/100 | Yes | |
| `member.lastName` | string | 77/100 | Yes | |
| `member.name` | string | 77/100 | **No** | Full name (virtual) |
| `member.isArchived` | boolean | 20/100 | **No** | Member is archived |
| `guest` | object | 23/100 | **No** | Guest reference |
| `guest.id` | string | 23/100 | **No** | Guest ID |
| `guest.firstName` | string | 23/100 | **No** | |
| `guest.lastName` | string | 23/100 | **No** | |
| `guest.name` | string | 23/100 | **No** | Full name (virtual) |
