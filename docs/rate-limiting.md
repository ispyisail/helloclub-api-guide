# Rate Limiting

## Limits

- **30 requests per minute** per API key
- Applies to all endpoints equally
- Resets on a rolling window

## 429 Response

When you exceed the rate limit, the API returns:

```
HTTP/1.1 429 Too Many Requests
```

```json
{
  "error": "TooManyRequestsError",
  "message": "You have exceeded the API rate limit of 30 requests per minute"
}
```

## V2 Retry-After Header

The V2 API adds a `Retry-After` header on 429 responses, indicating the number of seconds to wait:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 12
```

Use this value dynamically instead of fixed backoff delays.

## Recommended Strategy

1. **Respect the limit** — space requests at least 2 seconds apart for sustained operations
2. **Handle 429s** — catch the status code and wait before retrying
3. **Use Retry-After** — if present (V2), use the header value; otherwise back off exponentially
4. **Limit concurrency** — avoid parallel requests to the same API key

### Example: Rate-Aware Client

```python
import time
import httpx

def request_with_retry(client, method, url, max_retries=3, **kwargs):
    """Make a request with rate limit handling and exponential backoff."""
    for attempt in range(max_retries):
        response = client.request(method, url, **kwargs)

        if response.status_code == 429:
            # Use Retry-After header if available (V2 API)
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                wait = int(retry_after)
            else:
                wait = 2 ** (attempt + 1)  # 2, 4, 8 seconds
            print(f"Rate limited. Waiting {wait}s...")
            if attempt < max_retries - 1:
                time.sleep(wait)
                continue
            raise Exception("Rate limit exceeded after all retries")

        response.raise_for_status()
        return response

    raise Exception(f"Failed after {max_retries} retries")
```

### Example: Batch Operations

When processing many items (e.g. iterating over all members), add a delay between requests:

```python
import time

members = []
offset = 0

while True:
    response = client.get("/member", params={"limit": 100, "offset": offset})
    data = response.json()
    batch = data.get("members", [])
    members.extend(batch)

    if len(batch) < 100:
        break

    offset += 100
    time.sleep(2)  # Stay well under 30 req/min

print(f"Fetched {len(members)} members")
```

## Tips

- **Pagination** is the most common cause of hitting rate limits. A club with 2,000+ members requires 20+ requests to page through all of them.
- **Cache responses** where possible — member data doesn't change frequently.
- **Use `fields` parameter** to reduce response size (won't reduce rate limit consumption, but speeds up responses).
- **Use `updatedAt` filter** on members to only fetch recently changed records instead of the full list.
