# Direct Debit Sandbox — Business Domain Flow

Split out from the original single-file `learning.md`. Covers RestTemplate, the end-to-end
subscription request flow, the Scenario Engine, common errors, the Provision pattern, channel
aliasing, subscription vs mandate trigger-debit, the Preauthorization feature, product type
enforcement, debitDay validation, config resolution, and DAILY-frequency constraints. See also
`05-async-scheduling-retry.md` and `04-data-storage-patterns.md`.

---

## 23. RestTemplate: making HTTP requests from Java

`RestTemplate` is Spring's built-in HTTP client. In `CallbackService`, after processing a debit, the sandbox needs to POST a notification to the merchant's server:

```java
HttpHeaders headers = new HttpHeaders();
headers.setContentType(MediaType.APPLICATION_JSON);
HttpEntity<Object> entity = new HttpEntity<>(payload, headers);

ResponseEntity<String> response = restTemplate.exchange(
    callbackUrl, HttpMethod.POST, entity, String.class
);
```

Breaking it down:
- `HttpHeaders` — the HTTP headers to attach
- `HttpEntity<Object>` — wraps the payload (body) + headers into one object
- `restTemplate.exchange(...)` — makes the HTTP call
  - `callbackUrl` — the URL to POST to
  - `HttpMethod.POST` — the HTTP method
  - `entity` — the body + headers
  - `String.class` — what type to deserialize the response body as

The `RestTemplate` bean is created once in [AppConfig.java](src/main/java/com/itc/direct_debit_sandbox/config/AppConfig.java) and injected wherever it's needed.

---


---

## 26. How a subscription request flows end-to-end

Here is the full journey of `POST /subscription/subscribe`:

```
1. HTTP POST arrives at port 8080
         ↓
2. Spring routes it to SubscriptionController.subscribe()
   - Reads headers: x-transflowId, x-key, x-country
   - Reads JSON body → SubscriptionRequestDto (Spring does this automatically)
   - @Valid checks all @NotBlank fields
         ↓
3. SubscriptionService.subscribe() is called
   a. validateHeaders() — are headers non-blank?
   b. Duplicate check — does a subscription with this referenceNo already exist?
   c. Generate subscriptionId = "SUB" + random
   d. Generate mandateId     = "MAND" + random
   e. Build SubscriptionRecord with all fields
   f. store.createSubscription(id, record)  — saved in primary map + secondary indexes
   g. callbackService.fireCallbacks(record)  — starts ASYNC background thread
   h. Return { "responseCode": "03", "responseMessage": "your request is being processed" }
         ↓
4. Spring converts the Map to JSON and sends the HTTP response.
   The caller gets the response IMMEDIATELY, while step 3g is still running.
         ↓
5. In the background (2 seconds later):
   CallbackService.firePreapprovalCallback()
   - resolveCallbackUrl() checks provision store for merchantId+productId first
   - Falls back to record.callbackUrl if no provision found
   - Sends POST to the resolved URL
         ↓
6. In the background (5 more seconds later):
   CallbackService.fireTransactionCallback()
   - ScenarioEngine determines outcome from debitAccount's last 3 digits
   - Saves TransactionRecord to store
   - resolveCallbackUrl() resolves the URL the same way as step 5
   - Sends POST with transaction result to the resolved URL
```

---


---

## 28. The Scenario Engine: simulating outcomes without a real bank

In a real payment system, the bank decides whether a transaction succeeds. In a sandbox, we simulate this with a simple rule: **the last 3 digits of the debit account number determine the outcome**.

```java
case "001" -> "01";   // Success — use account ending in 001
case "101" -> "101";  // Insufficient funds — use account ending in 101
case "131" -> "131";  // Timeout — use account ending in 131
```

This means a tester can control which scenario fires just by choosing their account number:
- Account `0241234001` → always succeeds
- Account `0241234101` → always fails with insufficient funds
- Account `0241234131` → always times out

This is a common sandbox design pattern. It makes testing predictable without needing a real bank to cooperate.

See [ScenarioEngine.java](src/main/java/com/itc/direct_debit_sandbox/scenarios/ScenarioEngine.java).

---

## 29. Common mistakes and what the errors mean

**`NullPointerException`**
You called a method on an object that is `null`. Check for null before using it:
```java
if (record != null) { record.getStatus(); }
```

**`HttpMessageNotReadableException`**
Spring couldn't parse the JSON body. Usually means:
- JSON is malformed (missing comma, wrong quotes)
- A field has the wrong type (e.g., sending `"true"` as a string for a `Boolean` field)
- An enum value doesn't match (e.g., `"monthly"` instead of `"MONTHLY"`)

**`MethodArgumentNotValidException`**
A `@NotBlank` or `@NotNull` check failed. One of the required fields was empty or missing.

**`NoSuchBeanDefinitionException`**
Spring can't find a dependency to inject. Check that the class you depend on has `@Service`, `@Component`, or `@Bean`, and that it's in a package Spring scans.

**`@Async` method doesn't run asynchronously**
`@Async` only works when the method is called from **outside** the class. If a method calls another async method in the same class, it runs synchronously. This is a Spring limitation.

**`ConcurrentModificationException`**
You're modifying a plain `HashMap` while iterating over it from another thread. Use `ConcurrentHashMap` instead.

**Port 8080 already in use**
Another process is using port 8080. Either stop it, or change `server.port` in `application.properties`.

---

## 30. The Provision pattern: registering configuration once

In the original design, every subscribe request had to include a `callbackUrl` field. This is awkward — if the merchant has 1000 subscribers, every single request needs to carry the same URL.

The **provision pattern** solves this: the merchant calls `POST /provision` once to register their callback URL for a given `merchantId + productId` combination. Every callback fired for that merchant+product automatically goes to the registered URL, forever, without the subscriber needing to send it again.

```
First (once):   POST /provision  → stores callbackUrl for MERCH_123 + PROD_001
Later (many):   POST /subscription/subscribe → no callbackUrl needed in body
                Callback fires → resolveCallbackUrl looks up MERCH_123 + PROD_001 → gets the URL
```

This is a real-world pattern used when a single piece of config (URL, API key, webhook secret) belongs to the merchant, not to each individual transaction. The merchant registers it once at onboarding; every subsequent operation inherits it automatically.

In this project the provision also stores catalogue configuration (`retryAttempts`, `skipFactor`, `daysToDebitDayNotice`) — again, things set once at the merchant level rather than repeated on every request.

See [ProvisionController.java](src/main/java/com/itc/direct_debit_sandbox/provision/ProvisionController.java) and [ProvisionService.java](src/main/java/com/itc/direct_debit_sandbox/provision/ProvisionService.java).

---


---

## 48. Enum-based channel validation

Before this change, `channel` in `SubscriptionRequestDto` was a plain `String`. That meant any value — `"MTN"`, `"VODAFONE"`, `"banana"` — was accepted without complaint. The only supported channels are `MTN`, `TELECEL`, `AT`, `AIRTEL`, `BANK`, and `CARD`.

The fix: change the field from `String` to a `Channel` enum.

```java
public enum Channel {
    MTN, TELECEL, AT, AIRTEL, BANK, CARD
}
```

```java
// In SubscriptionRequestDto
@NotNull
private Channel channel;   // was: @NotBlank private String channel
```

**Why this works automatically:**

When Jackson (Spring's JSON deserializer) reads `"channel": "MTN"` from the request body, it maps the string `"MTN"` to `Channel.MTN`. If the string doesn't match any enum constant, Jackson throws a `HttpMessageNotReadableException` and Spring returns a `400 Bad Request` — no manual validation code required.

**Storing it:**

The `SubscriptionRecord` (and other store models) keeps `channel` as a plain `String`, because the store is just data storage and doesn't need to know about enum types. When the service writes the record it calls `.name()` to convert the enum back to a string:

```java
.channel(req.getChannel().name())   // Channel.MTN → "MTN"
```

When updating (where channel is optional), guard for null first:

```java
if (req.getChannel() != null) existing.setChannel(req.getChannel().name());
```

**The pattern generalises:** any field with a fixed set of values should be an enum in the DTO. You get free validation, IDE autocomplete, and compile-time safety all at once.

---

## 49. startDate / endDate validation

The `endDate` field on a subscription is optional (no end means "run forever"). But when it is provided, it must be strictly after `startDate`. This is a **business rule**, not a framework constraint, so it can't be expressed with a `@NotNull` or `@NotBlank` annotation — it has to be enforced in the service.

```java
if (req.getEndDate() != null && !req.getEndDate().isBlank()) {
    try {
        LocalDate start = LocalDate.parse(req.getStartDate());
        LocalDate end   = LocalDate.parse(req.getEndDate());
        if (!end.isAfter(start)) {
            // return error: "endDate must be after startDate"
        }
    } catch (Exception e) {
        // return error: "Invalid date format. Expected yyyy-MM-dd"
    }
}
```

`LocalDate.parse()` expects the ISO-8601 format `yyyy-MM-dd`. If the string doesn't match, it throws a `DateTimeParseException` — which we catch and turn into a readable error response.

`isAfter(start)` returns true only when `end` is strictly later than `start`. Equal dates are rejected (a subscription that starts and ends on the same day is meaningless).

The same rule applies to preauthorization mandates — and there `endDate` is required (not optional), so we always run the check.

---

## 50. The difference between subscription trigger-debit and mandate trigger-debit

This is the most important conceptual distinction in the whole API.

**Subscription trigger-debit** (`POST /subscription/trigger-debit`)

A subscription runs automatic debits on a schedule. When a scheduled debit fails, the system retries it automatically a number of times (configured by `retryAttempts`). The `trigger-debit` endpoint only makes sense *after all those retries have finished and they all failed*. It lets the merchant make one last manual attempt. 

If you call it while retries are still in progress (transaction status is `PROCESSING`), the sandbox blocks the call:

```json
{ "responseCode": "100", "responseMessage": "Automatic retries are still in progress..." }
```

The sandbox checks this by looking up the `TransactionRecord` stored under the subscription's `referenceNo`:

```java
TransactionRecord existingTx = store.getTransaction(request.getReferenceId());
if (existingTx != null && "PROCESSING".equalsIgnoreCase(existingTx.getStatus())) {
    return error("Automatic retries are still in progress...");
}
```

**Mandate trigger-debit** (`POST /mandate/trigger-debit`)

A preauthorization is not a schedule — it is a *standing permission*. The merchant can debit the customer at any time within the `startDate`–`endDate` window. There is no automatic schedule, no retry loop, no concept of "retries in progress". Every call to `/mandate/trigger-debit` is a deliberate, on-demand action by the merchant.

Because each mandate debit is independent, the caller supplies the specific debit details (amount, narration, reference) in the request body — unlike subscription trigger-debit where those details already live in the subscription record.

The body difference makes this concrete:

```
Subscription trigger:   { "referenceId": "REF_001", "productId": "..." }
Mandate trigger:        { "mandateId": "...", "productId": "...", "debitAmount": "...",
                          "narration": "...", "referenceNo": "...", "debitAccount": "...",
                          "currency": "..." }
```

One looks up an existing record and retries it. The other starts a fresh debit with parameters supplied right now.

---

## 51. The Preauthorization feature: how it fits together

A preauth has five operations and they use three different IDs. Understanding which ID each operation uses is the key to not getting confused.

| Operation | Endpoint | Lookup key |
|---|---|---|
| Create | `POST /pre-authorization/authorize` | — (creates IDs) |
| Trigger debit | `POST /mandate/trigger-debit` | `mandateId` (from preapproval callback) |
| Check status | `POST /mandate/check-status` | `reference` (= referenceNo from creation) |
| Get details | `POST /direct-debit/pre-authorization/retrieve/details` | `referenceId` (= referenceNo) |
| Cancel | `POST /pre-authorization/cancel` | `preApprovalId` (from preapproval callback) |

**Why three different IDs?**

- `preApprovalId` — the internal ID for the mandate record itself. Used for cancellation because cancellation is a direct operation on the mandate, not on a transaction.
- `mandateId` — the ID that represents "permission to debit". It appears in callbacks and is what the trigger uses to prove the mandate was set up.
- `referenceNo` — the third-party reference supplied at creation. It's the merchant's own identifier and is how they look up their own records.

The sandbox stores `PreAuthRecord` under `preApprovalId` as the primary key, then maintains two secondary indexes so all three lookup paths resolve in O(1):

```
preAuthReferenceIndex:  referenceNo  → preApprovalId
preAuthMandateIndex:    mandateId    → preApprovalId
```

**The lifecycle:**

```
createPreAuth()
  ↓ (stores record, fires preapproval callback after 2s)
  ↓ callback contains: preApprovalId, mandateId
  ↓
triggerMandateDebit(mandateId, ...)
  ↓ (validates window, fires transaction callback after 5s)
  ↓
cancelPreAuth(preApprovalId, ...)
  ↓ status → CANCELLED
```

**Guards on trigger:**
- Status must be `ACTIVE` (not cancelled)
- Today must be ≥ `startDate` (window hasn't started yet)
- Today must be ≤ `endDate` (window has not expired)

**Guards on cancel:**
- Status must be `ACTIVE`
- `debitAccount`, `channel`, and `country` must match the stored record — this prevents one merchant from cancelling another merchant's mandate

---

## 52. Why the same callback payload works for both subscriptions and preauths

Both `fireCallbacks()` (subscription) and `firePreAuthCallbacks()` (preauth) send a `PreapprovalCallbackPayloadDto` to the merchant's webhook. The payload structure is identical because the real ITC API uses the same callback format for both — what changes is only the source of the data.

For subscriptions the mandate is an implied consequence of setting up a schedule. For preauths the mandate is the primary thing being set up. Both produce a `mandateId` and fire the same preapproval event.

The transaction callback works the same way too. Whether the debit was triggered by a subscription schedule or a merchant calling `/mandate/trigger-debit`, the merchant receives a `TransactionCallbackPayloadDto` with the same fields.

---

---

## 53. Product type enforcement on preauth endpoints

The `ProductType` enum (values: `SUBSCRIPTIONS_ONLY`, `HYBRID`, `PREAUTHORIZED_ONLY`) is stored on `ProvisionRecord` when the merchant provisions. This determines which API operations that **product** may use. Note: it is `productType`, not `merchantType` — a single merchant can have multiple products, each with a different type (e.g., one SUBSCRIPTIONS_ONLY product for a weekly streaming service and one PREAUTHORIZED_ONLY product for on-demand utility billing).

**Rule:** `/pre-authorization/authorize` and `/mandate/trigger-debit` are only available to `PREAUTHORIZED_ONLY` products. `HYBRID` and `SUBSCRIPTIONS_ONLY` products are blocked with a `100` response.

The check lives in a private `checkProductType(merchantId, productId)` helper in `PreAuthService`. It is called:

- In `createPreAuth()` — immediately after header validation, before any other logic.
- In `triggerMandateDebit()` — after the preAuth record is found (because the request only carries `mandateId`, so we need the stored record to know `merchantId`/`productId`).

```java
ProvisionRecord provision = store.getProvision(merchantId, productId);
if (provision == null || provision.getProductType() == null) {
    return error("Product type not configured...");
}
if (provision.getProductType() != ProductType.PREAUTHORIZED_ONLY) {
    return error("This operation is only available to PREAUTHORIZED_ONLY products");
}
```

Other preauth operations (check-status, retrieve-details, cancel) do **not** enforce type — they are read/cancel operations that any merchant with a valid record can use.

---

## 54. debitDay validation by frequencyType

`debitDay` specifies which unit within the frequency cycle to debit on. Its valid range depends on `frequencyType`:

| frequencyType | allowed debitDay |
|---|---|
| DAILY | 1 (only valid value — "every day") |
| WEEKLY | 1–7 (1 = Monday … 7 = Sunday) |
| MONTHLY | 1–28 |
| YEARLY | 1–28 |

**Why 1–28 for MONTHLY/YEARLY?** Capping at 28 avoids the February edge case — day 29/30/31 does not exist in all months. The real API applies the same cap.

**Where it is validated:**

- `SubscriptionService.subscribe()` — after the date check, before the record is built.
- `SubscriptionService.update()` — before applying field updates. The validation uses the *effective* frequency and debitDay: the new value if provided in the request, the stored value otherwise. This catches the case where the merchant changes `frequencyType` but does not change `debitDay`, leaving a value that was valid for the old frequency but is out of range for the new one (e.g., `debitDay=20` is valid for MONTHLY but not for WEEKLY).

The helper is `validateDebitDay(FrequencyType frequency, String debitDay)`. It parses `debitDay` as an integer and uses a `switch` expression over `FrequencyType`. Returns `null` on success; an error map with code `"100"` on failure.

---

## 55. ProductType vs MerchantType — why types belong to products, not merchants

This project originally had a `MerchantType` field on `ProvisionRecord`. It was renamed to `ProductType` for a precise reason: **the type is a property of the product, not the merchant**.

A single merchant can offer multiple products at the same time:
- `PROD_WEEKLY_STREAMING` — auto-debit every week → `SUBSCRIPTIONS_ONLY`
- `PROD_UTILITY_BILL` — debit on demand when the meter is read → `PREAUTHORIZED_ONLY`

If the type lived on the merchant, both products would have to share the same type, which is wrong. By moving the type to the provision record (keyed by `merchantId + productId`), each product can have its own type.

This is a general design principle: **put attributes where they actually belong**. Ask "what entity does this fact describe?" — and the answer tells you where it should live.

In code, the change was:

```java
// ProvisionRecord.java — before
private MerchantType merchantType;

// ProvisionRecord.java — after
private ProductType productType;
```

The JSON key in API requests changed from `"merchantType"` to `"productType"`. Any existing requests that used the old key will be ignored (the field will be null, and the type check will return an error).

---


---

## 59. resolveEffectiveConfig — merging request config with provision defaults

When a merchant subscribes, they can optionally pass a `configuration` list. If they don't, the system should fall back to the defaults registered at provision time.

The `resolveEffectiveConfig()` helper in `SubscriptionService` handles this merge:

```java
private List<ConfigurationItem> resolveEffectiveConfig(
        List<ConfigurationItem> requested, ProvisionRecord provision) {

    List<ConfigurationItem> resolved = requested != null
            ? new ArrayList<>(requested)  // start with what the caller sent
            : new ArrayList<>();          // or an empty list if nothing was sent

    Set<String> present = resolved.stream()
            .map(ConfigurationItem::getName)
            .collect(Collectors.toSet());

    // For each default on the provision, only add it if the caller didn't already set it
    if (provision != null) {
        if (!present.contains("retryAttempts") && provision.getRetryAttempts() != null) {
            ConfigurationItem item = new ConfigurationItem();
            item.setName("retryAttempts");
            item.setValue(provision.getRetryAttempts().toString());
            resolved.add(item);
        }
        // same for skipFactor, daysToDebitDayNotice ...
    }
    return resolved;
}
```

Key design choices:

1. **Caller wins** — if the caller sent `retryAttempts`, the provision default is ignored. This respects the principle that explicit input beats inferred defaults.
2. **Never overwrite** — we build a `Set<String>` of names already present before checking the provision, so we only fill gaps.
3. **Null-safe** — the caller might not send any configuration at all (`requested` is null), so we start from an empty list.

The resolved config is saved on `SubscriptionRecord.configuration`, so every subsequent operation (callback, retry scheduler) reads the effective values directly from the record without re-resolving.

---

## 60. Frequency-based validation constraints (DAILY)

Not all configuration is valid for all frequencies. Two rules are specific to `DAILY` subscriptions:

**Rule 1: `notificationStatus` cannot be `true`**

`notificationStatus=true` means "notify the account holder before each debit." For a daily debit, sending a notification every single day is noise. The API specification explicitly disallows it.

```java
if (FrequencyType.DAILY == req.getFrequencyType()
        && Boolean.TRUE.equals(req.getNotificationStatus())) {
    return error("notificationStatus cannot be enabled for DAILY subscriptions");
}
```

**Rule 2: `retryAttempts` cannot exceed 1**

A retry is fired one day after the failed attempt. For a daily subscription, "retry in one day" means the retry fires on the same day as the next scheduled debit. Retrying more than once would mean the retries pile up into the next cycles. The API treats one retry as the maximum sensible value for daily frequency.

```java
if (FrequencyType.DAILY == req.getFrequencyType()) {
    OptionalInt retryAttempts = getConfigIntValue(effectiveConfig, "retryAttempts");
    if (retryAttempts.isPresent() && retryAttempts.getAsInt() > 1) {
        return error("retryAttempts cannot exceed 1 for DAILY subscriptions");
    }
}
```

Note that this check runs against the **effective config** (after fallback resolution from the provision), not just the raw request config. This means if the provision sets `retryAttempts=3` and the caller sends a DAILY subscribe request with no config override, the check will still catch it.

---


---

## 73. Channel aliasing — remapping deprecated values internally

In Ghana (`x-country: GH`), the carrier previously known as Vodafone rebranded to Telecel. The API spec uses `TELECEL` as the canonical value, but existing integrations may still send `VODAFONE`. Rather than rejecting those requests or maintaining two code paths forever, the service silently remaps the alias before any validation logic runs:

```java
if (country.equals("GH") && Channel.VODAFONE == req.getChannel()) {
    req.setChannel(Channel.TELECEL);
    log.info("Channel changed from VODAFONE to TELECEL");
}
```

To make this possible, `VODAFONE` is kept in the `Channel` enum as a valid deserialization target:

```java
public enum Channel {
    MTN, TELECEL, AT, AIRTEL, BANK, CARD,
    VODAFONE,  // alias for TELECEL in GH — remapped in SubscriptionService before any logic runs
}
```

**Why this approach is better than rejecting `VODAFONE`:**

- Breaking old integrations is expensive. Callers may have the value hardcoded in their production systems.
- Internal logic only ever sees `TELECEL` — one canonical path, no `if (ch == VODAFONE || ch == TELECEL)` scattered everywhere.
- The remap is logged at INFO level, so you have an audit trail in production.

**The general pattern:**

1. Keep the alias in the enum (so Jackson can deserialize it without a 400 error).
2. Add one early-exit remap block at the top of the service method, before guards.
3. Log the remap so it's visible.
4. All subsequent logic uses only the canonical value.

This is sometimes called a **value migration shim** — you're absorbing the caller's stale vocabulary at the boundary so the core domain stays clean.

---


---

## 89. Product type access control

When a system has multiple product types (`SUBSCRIPTIONS_ONLY`, `PREAUTHORIZED_ONLY`, `HYBRID`), endpoints should reject requests from the wrong type early — before touching the database:

```java
// In SubscriptionService:
private Map<String, Object> checkSubscriptionProductType(String merchantId, String productId) {
    ProvisionRecord provision = store.getProvision(merchantId, productId);
    if (provision == null || provision.getProductType() == null) {
        return error("Product type not configured...");
    }
    if (provision.getProductType() == ProductType.PREAUTHORIZED_ONLY) {
        return error("PREAUTHORIZED_ONLY products cannot use subscription endpoints");
    }
    return null; // allowed
}
```

The enforcement matrix:

| `productType` | Subscription endpoints | Preauth endpoints |
|---|---|---|
| `SUBSCRIPTIONS_ONLY` | ✅ | ❌ |
| `PREAUTHORIZED_ONLY` | ❌ | ✅ |
| `HYBRID` | ✅ | ✅ |
| `null` | ❌ | ❌ |

A common mistake: checking `productType != PREAUTHORIZED_ONLY` as the preauth guard. This blocks `HYBRID` merchants. The correct check is `productType == SUBSCRIPTIONS_ONLY`.

---

## 90. Migrating HTTP 4xx errors to 200 + business code

Real banking and fintech APIs typically return HTTP 200 for everything and communicate errors through a `responseCode` in the body. This avoids clients needing to handle two different error paths (HTTP status AND body).

**Before:**
```java
return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
        .body(ApiResponseDto.builder()
                .responseCode("401")
                .responseMessage("Unauthorized...")
                .build());
```

**After:**
```java
return ResponseEntity.ok(ApiResponseDto.builder()
        .responseCode("107")
        .responseMessage("Invalid credentials: missing or blank required headers")
        .build());
```

Once you make this change, the `HttpStatus` import becomes unused — remove it to keep the file clean.

The interceptor follows the same pattern: it writes directly to the `HttpServletResponse` with `response.setStatus(HttpServletResponse.SC_OK)` (which is `200`) rather than returning a non-2xx status.

---

## 91. Parsing JSON string examples from OpenAPI schema

When you annotate a `List` field with `@Schema(example = "...")`, springdoc stores the example as a raw JSON string in the OpenAPI JSON:

```json
"configuration": {
  "type": "array",
  "example": "[{\"name\":\"retryAttempts\",\"value\":\"3\"}]"
}
```

A custom docs UI that builds example payloads with `buildExampleFromSchema()` receives `p.example` as the string `"[{...}]"` — not as a parsed array. If you assign it as-is, the textarea shows a JSON-encoded string instead of an actual array.

Fix: try to parse any string example as JSON before using it:

```js
if (p.example !== undefined) {
  let v = p.example;
  if (typeof v === 'string') { try { v = JSON.parse(v); } catch {} }
  out[name] = v;
  continue;
}
```

The `try/catch` is intentionally silent — if the string isn't valid JSON (e.g. it's just a plain string example like `"GH"`), `JSON.parse` throws and `v` stays as the original string. Only actual JSON arrays and objects get promoted.

---

