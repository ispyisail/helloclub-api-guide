# Member Fields

**Endpoint:** `GET /member` | **Sample size:** 50 members (sorted by most recently active)

Fields marked **UNDOCUMENTED** are not in the official OpenAPI spec but are returned by the live API.

## Core Identity

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `id` | string (ObjectId) | 10/10 | Yes | Member ID |
| `club` | string (ObjectId) | 10/10 | Yes | Club ID |
| `firstName` | string | 10/10 | Yes | First name |
| `lastName` | string | 10/10 | Yes | Last name |
| `legalName` | string | seen | **No** | Legal/alternate name |
| `initials` | string | 10/10 | **No** | Computed initials |
| `number` | string | 10/10 | Yes | Member number |
| `gender` | string | 10/10 | Yes | "male" / "female" / "other" |
| `dob` | integer | 9/10 | Yes | Date of birth as YYYYMMDD integer |
| `age` | string | 10/10 | **No** | Computed age (can be empty string) |
| `countryCode` | string | 10/10 | **No** | e.g. "NZ" |

## Contact Details

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `email` | string | 10/10 | Yes | Primary email |
| `mobile` | string | 10/10 | Yes | Mobile number |
| `phone` | string | 8/10 | Yes | Phone number |
| `address` | object | 10/10 | Yes | Physical address |
| `address.line1` | string | 10/10 | **No** | Street address (replaces spec's streetNumber+streetName) |
| `address.line2` | string | 10/10 | **No** | Address line 2 |
| `address.suburb` | string | 10/10 | Yes | Suburb |
| `address.city` | string | 10/10 | Yes | City |
| `address.state` | string | 10/10 | **No** | State/region |
| `address.postalCode` | string | 10/10 | Yes | Postal code |
| `address.country` | string | 10/10 | Yes | Country |
| `address.formatted` | string | 10/10 | **No** | Full formatted address |
| `address.mapsLink` | string | 10/10 | **No** | Google Maps link |
| `address.embedLink` | string | 10/10 | **No** | Google Maps embed link |
| `address.placeId` | string | 9/10 | **No** | Google Places ID |
| `postalAddress` | object/null | 10/10 | **No** | Separate postal address |

## Account & Auth

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `username` | string | 10/10 | Yes | Login username |
| `roles` | array (string) | 10/10 | Yes | "admin" / "viewer" / "eventManager" / "member" |
| `locale` | string | 10/10 | Yes | e.g. "en" |
| `color` | string | 10/10 | Yes | Avatar color hex |
| `avatar` | object | 1/10 | Yes | Profile image |
| `avatar.url` | string | 1/10 | **No** | Full image URL |
| `profiles` | array | 10/10 | Yes | OAuth profiles |
| `profiles[].provider` | string | 7/10 | Yes | "google" / "facebook" |
| `profiles[].id` | string | 7/10 | Yes | Provider user ID |
| `profiles[].email` | string | 7/10 | Yes | Provider email |
| `hasProfiles` | boolean | 10/10 | **No** | Has OAuth profiles linked |
| `canSignIn` | boolean | 10/10 | **No** | Able to sign in |
| `intercomHash` | string | 1/10 | Partial | Intercom identity hash (spec had `hash`) |
| `isAccountOwner` | boolean | 1/10 | Yes | Club owner |
| `ids` | array (string) | 10/10 | **No** | All associated IDs |
| `profilePath` | string | 10/10 | **No** | Admin profile URL path |

## Status Flags

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `isSuspended` | boolean | 10/10 | Yes | Suspended |
| `isPending` | boolean | 10/10 | Yes | Awaiting approval |
| `isRejected` | boolean | 10/10 | **No** | Application rejected |
| `isArchived` | boolean | 10/10 | Yes | Archived |
| `isEmailVerified` | boolean | 10/10 | Yes | Email verified |
| `isUnsubscribed` | boolean | 10/10 | **No** | Unsubscribed from emails |
| `isVaccinationValid` | boolean | 10/10 | **No** | Vaccination status valid |

## Activity & Engagement Dates

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `signUpDate` | string (ISO) | 10/10 | Yes | Registration date |
| `createdAt` | string (ISO) | 10/10 | **No** | Account creation timestamp |
| `updatedAt` | string (ISO) | 10/10 | **No** | Last update timestamp |
| `firstOnline` | string (ISO) | 10/10 | Yes | First login |
| `lastOnline` | string (ISO) | 10/10 | Yes | Last login |
| `detailsLastUpdated` | string (ISO) | 8/10 | Yes | Details last changed |
| `lastBooking` | string/null | 10/10 | **No** | Last booking date |
| `lastEventAttendance` | string/null | 10/10 | **No** | Last event attended |
| `lastCheckIn` | string/null | 10/10 | **No** | Last check-in |
| `lastVisitLogged` | string/null | 10/10 | **No** | Last visit logged |
| `lastTagUse` | string/null | 3/10 | **No** | Last tag scan (spec: `tagLastUsed`) |
| `lastBirthdayEmail` | string/null | 7/10 | **No** | Last birthday email sent |
| `lastWelcomeEmail` | string/null | 3/10 | **No** | Last welcome email |
| `lastTransactionReminder` | string/null | 5/10 | **No** | Last payment reminder |
| `lastLowAccountCreditWarning` | string/null | 1/10 | **No** | Low credit warning |
| `yearsSinceSignedUp` | integer | 10/10 | **No** | Computed years since signup |

## Activity Counts

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `numSessions` | integer | 10/10 | **No** | Total activity sessions |
| `numBookings` | integer | 10/10 | **No** | Total bookings |
| `numComments` | integer | 10/10 | **No** | Total comments |

## Financial

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `accountCredit` | number | 10/10 | Yes | Account credit balance |
| `amountOwing` | number | 10/10 | Yes | Outstanding amount |
| `billing` | object | 10/10 | **No** | Billing settings |
| `billing.emails` | array | 10/10 | **No** | Additional billing emails |
| `stripe` | object | 10/10 | Partial | Stripe payment data |
| `stripe.customerId` | string | 7/10 | **No** | Stripe customer ID |
| `stripe.sources` | array | 10/10 | **No** | Payment methods |
| `stripe.sources[].type` | string | varies | **No** | "card" |
| `stripe.sources[].isDefault` | boolean | varies | **No** | Default payment method |
| `stripe.sources[].card.brand` | string | varies | **No** | e.g. "mastercard" |
| `stripe.sources[].card.last4` | string | varies | **No** | Last 4 digits |

## Memberships & Subscriptions

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `subscriptions` | array | 10/10 | Yes | Membership subscriptions |
| `subscriptions[].id` | string | all | Yes | Subscription ID |
| `subscriptions[].membership` | object | all | Yes | Linked membership type |
| `subscriptions[].membership.id` | string | all | Yes | Membership type ID |
| `subscriptions[].membership.name` | string | all | Yes | e.g. "BMT Family" |
| `subscriptions[].membership.nameWithSuffix` | string | all | **No** | e.g. "BMT Family (Monthly)" |
| `subscriptions[].startDate` | string | all | **No** | Start date |
| `subscriptions[].endDate` | string | all | **No** | End date |
| `subscriptions[].renewalDate` | string | some | **No** | Renewal date |
| `subscriptions[].isCurrent` | boolean | all | **No** | Currently active |
| `subscriptions[].isPast` | boolean | all | **No** | Expired |
| `subscriptions[].isUpcoming` | boolean | all | **No** | Future start |
| `subscriptions[].isStopped` | boolean | some | Yes | Manually stopped |
| `subscriptions[].autoRenews` | boolean | varies | Yes | Auto-renewal on |

## Coupons

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `coupons` | array | 10/10 | Yes | Member coupons |
| `coupons[].name` | string | varies | Yes | e.g. "50 Session" |
| `coupons[].isActive` | boolean | varies | Yes | Active |
| `coupons[].numSessions` | integer | varies | Yes | Total sessions |
| `coupons[].numSessionsLeft` | integer | varies | Yes | Remaining |
| `coupons[].numSessionsUsed` | integer | varies | Yes | Used |
| `coupons[].expiryDate` | string | varies | **No** | Expiry date |

## Activities & Access

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `activities` | array | 10/10 | Yes | Linked activities |
| `access` | array | 10/10 | Yes | Access control rules |
| `canOverrideLights` | boolean | 2/10 | Yes | Override lights |
| `canOverrideDoors` | boolean | 2/10 | Yes | Override doors |

## Grades

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `grades` | array | 10/10 | **No** | Activity grades |
| `grades[].name` | string | some | **No** | e.g. "A" |
| `grades[].color` | string | some | **No** | Hex color |
| `grades[].isCurrent` | boolean | some | **No** | Currently active |
| `grades[].activity.name` | string | some | **No** | Activity name |

## Groups & Circles

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `groups` | array | 10/10 | Yes | Member groups (expanded objects, not just IDs) |
| `groups[].id` | string | some | **No** | Group ID |
| `groups[].name` | string | some | **No** | Group name |
| `groups[].color` | string | some | **No** | Group color |
| `circles` | array | 10/10 | **No** | Member circles/families |
| `related` | array | 10/10 | **No** | Related members |

## Privacy & Directory

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `directory` | object | 10/10 | **No** | Directory visibility settings |
| `directory.isPublic` | boolean | 10/10 | **No** | Listed in directory |
| `directory.fields.email` | boolean | 10/10 | **No** | Show email |
| `directory.fields.mobile` | boolean | 10/10 | **No** | Show mobile |
| `staff` | object | 10/10 | **No** | Staff profile settings |
| `highlight` | object | 10/10 | **No** | Highlight profile settings |

## Vaccination

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `vaccination` | object | 10/10 | **No** | Vaccination data |
| `vaccination.status` | string | 10/10 | **No** | "vaccinated" / "unknown" |
| `vaccination.isValid` | boolean | 10/10 | **No** | Currently valid |

## Other

| Field | Type | Presence | Documented | Description |
|-------|------|----------|------------|-------------|
| `customFields` | object | 10/10 | Yes | Club-specific custom fields |
| `customFiles` | object | 10/10 | Yes | Custom file attachments |
| `reminders` | object | 10/10 | Partial | Reminder preferences |
| `push` | object | 10/10 | **No** | Push notification preferences |
| `termsAndConditions` | object | 10/10 | Yes | T&C agreement status |
