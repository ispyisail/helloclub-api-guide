# ESP32 Integration Guide

Using the Hello Club API from an ESP32 microcontroller. Covers TLS certificates, RAM management, and a working example.

> Based on a production ESP32 badminton court timer that polls Hello Club for bookings and auto-starts game timers.

## The Challenge

The ESP32-WROOM-32 has **~60KB usable RAM** after WiFi and FreeRTOS overhead. A single HTTPS connection uses **~40-50KB** for the TLS handshake (mbedTLS). That leaves almost nothing for parsing JSON responses. Getting HTTPS API calls to work reliably requires careful memory management at every step.

## Prerequisites

- **Arduino framework** with ESP32 board support
- **Libraries:** [ArduinoJson](https://arduinojson.org/) v7+, WiFiClientSecure (built-in)

```ini
# platformio.ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
lib_deps =
    bblanchon/ArduinoJson
```

## 1. TLS Certificates

`WiFiClientSecure` requires a root CA certificate to verify the API server identity. You have three options:

### Option A: Pin the Root CA (recommended)

Pin only the root CA(s) that sign `api.helloclub.com`. This uses minimal RAM and still validates the connection.

```cpp
#include <WiFiClientSecure.h>

// Google Trust Services Root R4 (ECDSA) - signs api.helloclub.com
// Valid until 2036-06-22
const char* rootCA =
"-----BEGIN CERTIFICATE-----\n"
"MIICCTCCAY6gAwIBAgINAgPlwGjvYxqccpBQUjAKBggqhkjOPQQDAzBHMQswCQYD\n"
"VQQGEwJVUzEiMCAGA1UEChMZR29vZ2xlIFRydXN0IFNlcnZpY2VzIExMQzEUMBIG\n"
"A1UEAxMLR1RTIFJvb3QgUjQwHhcNMTYwNjIyMDAwMDAwWhcNMzYwNjIyMDAwMDAw\n"
"WjBHMQswCQYDVQQGEwJVUzEiMCAGA1UEChMZR29vZ2xlIFRydXN0IFNlcnZpY2Vz\n"
"IExMQzEUMBIGA1UEAxMLR1RTIFJvb3QgUjQwdjAQBgcqhkjOPQIBBgUrgQQAIgNi\n"
"AATzdHOnaItgrkO4NcWBMHtLSZ37wWHO5t5GvWvVYRg1rkDdc/eJkTBa6zzuhXyi\n"
"QHY7qca4R9gq55KRanPpsXI5nymfopjTX15YhmUPoYRlBtHci8nHc8iMai/lxKvR\n"
"HYqjQjBAMA4GA1UdDwEB/wQEAwIBhjAPBgNVHRMBAf8EBTADAQH/MB0GA1UdDgQW\n"
"BBSATNbrdP9JNqPV2Py1PsVq8JQdjDAKBggqhkjOPQQDAwNpADBmAjEA6ED/g94D\n"
"9J+uHXqnLrmvT/aDHQ4thQEd0dlq7A/Cr8deVl5c1RxYIigL9zC2L7F8AjEA8GE8\n"
"p/SgguMh1YQdc4acLa/KNJvxn7kjNuK8YAOdgLOaVsjh4rsUecrNIdSUtUlD\n"
"-----END CERTIFICATE-----\n";
```

**How to find the right certificate:**
1. Run `openssl s_client -connect api.helloclub.com:443 -showcerts`
2. Copy the last certificate in the chain (the root CA)
3. Or check in a browser: click the padlock, view certificate, certification path, export root

**Tip:** Include a second root CA (e.g. Let's Encrypt ISRG Root X1) as a fallback. If Hello Club changes hosting provider, your device won't break until you can push a firmware update.

### Option B: setInsecure() - development only

```cpp
WiFiClientSecure client;
client.setInsecure();  // Skips certificate verification entirely
```

Works but provides **no protection against MITM attacks**. Your API key is sent in plaintext to whoever intercepts the connection. Never use this in production.

### Option C: ESP32 built-in CA bundle

```cpp
#include <esp_crt_bundle.h>

WiFiClientSecure client;
client.setCACertBundle(esp_crt_bundle_attach);
```

Uses Mozilla's CA bundle stored in flash. Convenient but uses more flash (~200KB) and may be outdated on older ESP-IDF versions.

### Certificate Expiry

Root CAs have long lifetimes (10-20 years), but they do expire. The current root for `api.helloclub.com` (GTS Root R4) expires **2036-06-22**. Consider implementing OTA firmware updates so you can rotate certificates without physical access to the device.

## 2. RAM Management: The Core Problem

Here is why naive HTTPS + JSON parsing crashes the ESP32:

```
Total usable RAM:     ~60 KB
TLS connection:       -45 KB  (mbedTLS handshake buffers)
JSON response:        -20 KB  (even a small /event response)
                      -------
Remaining:            -5 KB   <- CRASH (heap exhaustion)
```

### Solution: Sequential memory usage

The key insight is that you don't need TLS and JSON memory **at the same time**. Read the response as a String, close the TLS connection (freeing ~45KB), then parse the JSON:

```cpp
bool fetchEvents(const String& apiKey) {
    WiFiClientSecure client;
    client.setCACert(rootCA);

    HTTPClient http;
    http.begin(client, "https://api.helloclub.com/event?limit=5&sort=startDate");
    http.addHeader("X-Api-Key", apiKey);
    http.addHeader("Accept", "application/json");
    http.setTimeout(10000);

    int httpCode = http.GET();
    if (httpCode != HTTP_CODE_OK) {
        http.end();
        return false;
    }

    // Step 1: Read the full response as a String
    String payload = http.getString();

    // Step 2: FREE the TLS connection BEFORE parsing JSON
    http.end();
    client.stop();
    // ~45KB of RAM is now available again

    // Step 3: Parse JSON with the freed memory
    DynamicJsonDocument doc(8192);
    deserializeJson(doc, payload);

    // Step 4: Free the payload String too
    payload = String();

    // Process events...
    JsonArray events = doc["events"].as<JsonArray>();
    for (JsonObject event : events) {
        Serial.println(event["name"].as<const char*>());
    }

    return true;
}
```

### Don't keep persistent TLS clients

It's tempting to keep a `WiFiClientSecure` as a class member to reuse the TLS session. Don't - it holds ~45KB the entire time. Create it on the stack inside your request function so it's freed automatically when the function returns.

```cpp
// BAD - holds 45KB permanently
class ApiClient {
    WiFiClientSecure client;  // Allocated for the lifetime of the object
};

// GOOD - freed after each request
bool makeRequest() {
    WiFiClientSecure client;  // Stack-allocated, freed when function exits
    client.setCACert(rootCA);
    // ... make request ...
}   // client destructor frees TLS memory here
```

## 3. JSON Deserialization Filters

The Hello Club API returns large objects with many fields you probably don't need. ArduinoJson's `Filter` feature lets you specify which fields to keep during deserialization, reducing memory usage by up to 90%.

```cpp
// Define a filter - only keep these 5 fields per event
StaticJsonDocument<256> filter;
filter["events"][0]["id"] = true;
filter["events"][0]["name"] = true;
filter["events"][0]["description"] = true;
filter["events"][0]["startDate"] = true;
filter["events"][0]["endDate"] = true;

// Parse with filter - everything else is discarded
DynamicJsonDocument doc(8192);  // 8KB is enough for ~20 filtered events
deserializeJson(doc, payload, DeserializationOption::Filter(filter));
```

Without the filter, you'd need a `DynamicJsonDocument(65536)` or larger - more than the ESP32's entire free heap.

## 4. Pagination

A 7-day lookahead can return dozens of events. Fetching them all at once would require a huge response buffer. Instead, paginate with small pages:

```cpp
const int PAGE_SIZE = 5;

for (int offset = 0; offset < 100; offset += PAGE_SIZE) {
    String params = "fromDate=" + fromDate;
    params += "&toDate=" + toDate;
    params += "&sort=startDate";
    params += "&limit=" + String(PAGE_SIZE);
    params += "&offset=" + String(offset);

    DynamicJsonDocument doc(8192);
    if (!fetchPage("/event", params, doc)) break;

    JsonArray events = doc["events"].as<JsonArray>();
    if (events.size() == 0) break;        // No more events

    for (JsonObject event : events) {
        // Cache only the events you care about
    }

    if (events.size() < PAGE_SIZE) break; // Last page
}
```

**Why 5?** Each page creates a TLS connection (~45KB), parses response (~8KB), processes, then frees everything. A page of 5 events with filtered JSON fits comfortably in 8KB. Larger pages risk OOM.

## 5. Retry Strategy

The ESP32's WiFi stack is less reliable than a desktop HTTP client. Network glitches, DNS failures, and TLS handshake timeouts are common. But keep retries short - `delay()` blocks the entire main loop.

```cpp
const int MAX_RETRIES = 2;
const int RETRY_DELAYS[] = {500, 1000};  // milliseconds

for (int attempt = 0; attempt < MAX_RETRIES; attempt++) {
    // ... make request ...
    if (httpCode == HTTP_CODE_OK) return true;

    bool shouldRetry = (httpCode == 429 || httpCode == 503 || httpCode == 504 || httpCode < 0);
    if (httpCode == 401) shouldRetry = false;  // Bad API key - don't retry

    if (!shouldRetry || attempt == MAX_RETRIES - 1) return false;

    delay(RETRY_DELAYS[attempt]);
}
```

**Key points:**
- **Max 2 attempts** - more just wastes time and blocks your app
- **Short delays** (500ms, 1s) - the ESP32 can't do anything else during `delay()`
- **Don't retry 401** - the API key is wrong, retrying won't help
- **Do retry 429, 503, 504** - transient errors that may resolve
- **Retry on `httpCode < 0`** - means network/TLS failure (DNS, timeout, etc.)

For polling-based applications, also implement a **backoff at the poll level**: poll every hour normally, but switch to every 5 minutes after a failure.

## 6. NVS Caching (Offline Resilience)

ESP32's NVS (Non-Volatile Storage) lets you persist API data across reboots. If your device loses WiFi or the API is down, it can still work from cached data.

```cpp
#include <Preferences.h>

void saveEventsToNVS(const std::vector<Event>& events) {
    DynamicJsonDocument doc(4096);
    JsonArray arr = doc.to<JsonArray>();

    for (const auto& evt : events) {
        JsonObject obj = arr.createNestedObject();
        obj["i"] = evt.id;           // Short keys save NVS space
        obj["n"] = evt.name;
        obj["s"] = (long)evt.startTime;
        obj["e"] = (long)evt.endTime;
    }

    String json;
    serializeJson(doc, json);

    Preferences prefs;
    prefs.begin("helloclub", false);
    prefs.putString("events", json);
    prefs.end();
}

void loadEventsFromNVS() {
    Preferences prefs;
    prefs.begin("helloclub", true);  // true = read-only
    String json = prefs.getString("events", "[]");
    prefs.end();

    // Parse and populate your event cache...
}
```

**Tips:**
- Use **abbreviated key names** (`i`, `n`, `s` instead of `id`, `name`, `startTime`) - NVS has size limits
- **Truncate strings** - event IDs to 12 chars, names to 40 chars
- Call `loadFromNVS()` on boot **before** the first API poll
- NVS has limited write cycles (~100K) - don't write on every loop iteration

## 7. Heap Monitoring

Always log free heap before and after API calls during development. This is how you catch memory leaks:

```cpp
Serial.printf("Before request - free heap: %d bytes\n", ESP.getFreeHeap());

// ... make API request ...

Serial.printf("After request  - free heap: %d bytes\n", ESP.getFreeHeap());
```

If free heap keeps decreasing across multiple API calls, you have a memory leak (usually an unclosed HTTPClient or WiFiClientSecure that wasn't properly destructed).

## Memory Budget Reference

Typical heap usage measured on ESP32-WROOM-32 (4MB flash, 520KB SRAM):

| Component | RAM Usage | Notes |
|-----------|----------|-------|
| WiFi + FreeRTOS | ~200 KB | Always allocated after `WiFi.begin()` |
| Free heap (typical) | ~50-70 KB | What's left for your code |
| TLS handshake (mbedTLS) | ~40-50 KB | Allocated during HTTPS connection |
| `DynamicJsonDocument(8192)` | 8 KB | Enough for ~20 filtered events |
| `String` response body | 2-10 KB | Depends on response size and page limit |
| ArduinoJson filter | < 1 KB | `StaticJsonDocument<256>` |

**Critical threshold:** If `ESP.getFreeHeap()` drops below **10KB**, you're at risk of crashes from heap fragmentation. Monitor this in development.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ESP.getFreeHeap()` shows 15KB+ free but JSON parse fails | Heap fragmentation - no single contiguous block large enough | Free TLS before parsing (Section 2) |
| TLS handshake timeout (httpCode = -1) | Weak WiFi signal, underpowered USB cable, or NTP not synced | Check WiFi RSSI, use good USB cable, sync NTP before first request |
| `deserializeJson` returns `NoMemory` | Response too large for document buffer | Use JSON filter (Section 3) and pagination (Section 4) |
| Works once then crashes on second request | `WiFiClientSecure` or `HTTPClient` not properly freed | Always call `http.end()` and `client.stop()` |
| Certificate verification fails after months | Server changed intermediate CA | Pin the **root** CA (not intermediate), or include fallback roots |
| `WiFi.begin()` hangs or connects then drops | SSID is case-sensitive on ESP32 | Double-check exact case: "MyNetwork" != "mynetwork" |
