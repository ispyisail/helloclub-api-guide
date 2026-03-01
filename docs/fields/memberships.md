# Membership Type Fields

**Endpoint:** `GET /membership` | **Sample size:** 70 membership types (all)

Fields marked **UNDOCUMENTED** are not in the official OpenAPI spec but are returned by the live API.

## Core

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `id` | string (ObjectId) | 70/70 | Yes | Membership type ID |
| `club` | string (ObjectId) | 70/70 | Yes | Club ID |
| `name` | string | 70/70 | Yes | e.g. "BMT Annual Senior" |
| `nameWithSuffix` | string | 70/70 | **No** | e.g. "BMT Annual Senior (Annual)" |
| `suffix` | string | 46/70 | **No** | e.g. "Annual", "Monthly" |
| `description` | string | 61/70 | Yes | Description text |
| `conditions` | string | 11/70 | Yes | Conditions text |
| `fee` | number | 70/70 | Yes | Membership fee |
| `ids` | array (string) | 70/70 | **No** | All associated IDs |
| `createdAt` | string (ISO) | 70/70 | **No** | Creation timestamp |
| `updatedAt` | string (ISO) | 70/70 | **No** | Last update timestamp |

## Term & Renewal

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `term` | object | 70/70 | Yes | Membership term |
| `isUnlimited` | boolean | 70/70 | Yes | No fixed term |
| `isAnchored` | boolean | 70/70 | Yes | Anchored start date |
| `anchor` | object | 70/70 | **No** | Anchor date configuration |
| `isProRated` | boolean | 70/70 | Yes | Pro-rated fees |
| `isRenewable` | boolean | 70/70 | Yes | Can be renewed |
| `autoRenewal` | object | 70/70 | **No** | Auto-renewal settings |
| `beforeExpiry` | object | 65/70 | Yes | Before-expiry notification term |
| `afterExpiry` | object | 65/70 | Yes | After-expiry grace term |
| `sendReminder` | boolean | 70/70 | Yes | Send renewal reminder |
| `hasTermGap` | boolean | 70/70 | **No** | Has gap between terms |

## Eligibility & Constraints

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `constraint` | string | 70/70 | **No** | Membership constraint |
| `memberships` | array (IDs) | 70/70 | **No** | Related membership IDs |
| `activities` | array (IDs) | 70/70 | Yes | Linked activity IDs |
| `couponTypes` | array (IDs) | 70/70 | **No** | Linked coupon types |
| `minAge` | integer | 43/70 | Yes | Minimum age |
| `maxAge` | integer | 29/70 | Yes | Maximum age |
| `limit` | integer | 55/70 | **No** | Member limit for this type |
| `bundleLimit` | null/integer | 61/70 | **No** | Bundle member limit |
| `numEventsLimit` | integer | 67/70 | **No** | Event attendance limit per term |
| `enforceSameHousehold` | boolean | 11/70 | **No** | Require same household |
| `requiresApproval` | string | 70/70 | **No** | Approval requirement |

## Registration & Payment

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `canSelectWhenRegistering` | boolean | 70/70 | Yes | Shown during registration |
| `canSelectWhenChanging` | boolean | 70/70 | Yes | Shown when changing membership |
| `canSelectForPurchase` | boolean | 70/70 | **No** | Available for purchase |
| `canUseForEvents` | boolean | 70/70 | **No** | Can be used for event attendance |
| `onlyViaDirectLink` | boolean | 70/70 | **No** | Only accessible via direct link |
| `registrationPayment` | string | 70/70 | **No** | Payment method at registration |
| `allowPayLater` | boolean | 70/70 | **No** | Allow deferred payment |
| `dueThreshold` | object | 12/70 | **No** | Payment due threshold |
| `invoiceDetails` | string | 51/70 | **No** | Invoice line item text |
| `autoAccountCredit` | number | 70/70 | Yes | Auto account credit amount |

## Status Flags

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `isDefault` | boolean | 70/70 | Yes | Default membership type |
| `isArchived` | boolean | 70/70 | Yes | Archived |
| `isLinked` | boolean | 70/70 | **No** | Is a linked/bundled membership |
| `hasLinked` | boolean | 70/70 | **No** | Has linked memberships |
| `linked` | array | 70/70 | **No** | Linked membership IDs |
| `primary` | object | 64/70 | **No** | Primary membership reference (if linked) |
