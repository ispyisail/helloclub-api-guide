# Custom Fields

Custom fields are club-specific fields stored in the `customFields` object on events and members. They are configured per-club in the Hello Club admin panel and are **not part of the API spec**.

Every club will have different custom fields. Use the [field discovery script](../../examples/field_discovery.py) to find your club's custom fields.

## How Custom Fields Work

Custom fields appear as properties of the `customFields` object:

```json
{
  "id": "abc123",
  "firstName": "Jane",
  "lastName": "Smith",
  "customFields": {
    "occupation": "Engineer",
    "emergencyContact": "John Smith, 021-555-1234",
    "badmintonGrade": "Advanced"
  }
}
```

Field types vary: strings, booleans, arrays (for multi-select), dates, and nulls.

## Example: Event Custom Fields

These are from a real club — yours will differ:

| Custom Field | Type | Description |
|-------------|------|-------------|
| `addToWaitingList` | boolean | Waiting list toggle |
| `catering` | boolean | Catering option |
| `chargesProcessed` | boolean | Admin: charges processed |
| `dinner` | boolean | Dinner option |
| `group` | string/null | Group assignment |
| `locationCode` | string/null | Location code |
| `training` | boolean | Training session flag |

## Example: Member Custom Fields

| Custom Field | Type | Description |
|-------------|------|-------------|
| `badmintonGrade` | string/null | Grade level (e.g. "Advanced", "Beginner") |
| `occupation` | string | Occupation |
| `school` | string | School (for juniors) |
| `parentcaregiver` | string | Parent/caregiver (for juniors) |
| `emergencyContact` | string | Emergency contact info |
| `secondaryEmailAddress` | string | Alternative email |
| `badmintonHallUse` | array (string) | Multi-select: how they use the hall |

## Discovering Your Club's Custom Fields

Run the field discovery script to see what custom fields your club has:

```bash
export HELLOCLUB_API_KEY="your-key"
python examples/field_discovery.py
```

This fetches a sample of events and members and prints all field paths, including custom fields.
