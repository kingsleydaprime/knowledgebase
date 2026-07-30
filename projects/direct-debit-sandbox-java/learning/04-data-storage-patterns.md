# Direct Debit Sandbox — Data & Storage Patterns

Split out from the original single-file `learning.md`. Covers `ConcurrentHashMap`, UUID
generation, composite map keys, fallback resolution, secondary indexes, separating create from
update, data normalization (1NF/2NF/3NF and deliberate denormalization), and a running recap of
everything covered up to this point in the original guide. See also
`03-dtos-lombok-builder.md` and `06-business-domain-flow.md`.

---

## 18. ConcurrentHashMap: thread-safe storage

A regular `HashMap` is not safe when multiple threads read and write at the same time. This project fires async callbacks (background threads) that write transaction records while incoming HTTP requests also write subscription records.

```java
private final Map<String, SubscriptionRecord> subscriptions = new ConcurrentHashMap<>();
```

`ConcurrentHashMap` handles concurrent access internally so two threads can write without corrupting the data. If you used a plain `HashMap`, you could get data corruption or crashes under load — a class of bug that only shows up in production and is very hard to reproduce.

---

## 19. UUID: generating unique IDs

`UUID` (Universally Unique Identifier) generates a random 128-bit number that is statistically guaranteed to be unique.

```java
String subscriptionId = "SUB" + UUID.randomUUID().toString().replace("-", "").substring(0, 12).toUpperCase();
// e.g. "SUBA3F82C1D9B47"
```

Breaking that chain down:
- `UUID.randomUUID()` — generates something like `a3f82c1d-9b47-4e3a-bc12-...`
- `.toString()` — converts it to a String
- `.replace("-", "")` — removes the dashes to get `a3f82c1d9b47...`
- `.substring(0, 12)` — takes only the first 12 characters
- `.toUpperCase()` — makes it uppercase

The prefix `"SUB"` makes it obvious at a glance that this ID belongs to a subscription.

---


---

## 31. Composite map keys

The provision store needs to look up a record by **two** values: `merchantId` and `productId`. But `ConcurrentHashMap` only takes one key.

The solution is to combine them into a single String:

```java
// Saving
provisions.put(merchantId + ":" + productId, record);
// e.g. key = "MERCH_123:PROD_001"

// Retrieving
provisions.get(merchantId + ":" + productId);
```

The `:` separator is important — it stops `"MERCH1"` + `"23:PROD"` from accidentally colliding with `"MERCH123"` + `":PROD"`. As long as your IDs never contain `:`, this is safe and simple.

This is called a **composite key**. You will see it everywhere in systems that use simple maps instead of databases. A database would use a multi-column primary key; here we simulate it by gluing strings together.

---

## 32. Extending an existing interface

When we added the provision feature, we needed to add two new methods to the data store: `saveProvision` and `getProvision`. Because `InMemoryStore` implements the `Store` interface, we had to add the methods to **both** places.

Step 1 — declare the contract in the interface:

```java
// Store.java
void saveProvision(String merchantId, String productId, ProvisionRecord record);
ProvisionRecord getProvision(String merchantId, String productId);
```

Step 2 — provide the implementation in the class:

```java
// InMemoryStore.java
public void saveProvision(String merchantId, String productId, ProvisionRecord record) {
    provisions.put(merchantId + ":" + productId, record);
}

public ProvisionRecord getProvision(String merchantId, String productId) {
    return provisions.get(merchantId + ":" + productId);
}
```

If you add methods to the interface but forget to add them to the implementing class, **the compiler will refuse to build**. You'll see:

```
InMemoryStore is not abstract and does not override abstract method saveProvision(...)
```

This is one of the main benefits of interfaces — they enforce that every implementation stays complete. You can never forget to implement a method.

---

## 33. Fallback resolution: trying one source, falling back to another

`resolveCallbackUrl()` in `CallbackService` is a classic example of a **fallback pattern**:

```java
private String resolveCallbackUrl(String merchantId, String productId, String fallback) {
    ProvisionRecord provision = store.getProvision(merchantId, productId);
    if (provision != null && provision.getCallbackUrl() != null) {
        return provision.getCallbackUrl();   // primary source
    }
    return fallback;                         // secondary source
}
```

Reading this: "try to get the URL from the provision store first. If it's not there (maybe the merchant hasn't provisioned yet), use whatever was passed in as a fallback."

This pattern appears constantly in real-world code:
- Try the cache → fall back to the database
- Try an environment variable → fall back to a default value
- Try a user-provided config → fall back to the system default

The method takes `fallback` as a parameter rather than hardcoding `null`. This makes the caller decide what "no provision" means in their context — some callers might have a per-request URL to fall back to; others might have nothing at all.

---


---

## 45. Secondary indexes — fast lookups at scale

When you store records in a `Map<String, SubscriptionRecord>` keyed by `subscriptionId`, looking up a record by its ID is **O(1)** — the map jumps straight to it. But what if you need to find a record by a *different* field, like `referenceNo`?

Without an index, you scan every value:

```java
subscriptions.values().stream()
    .filter(s -> s.getReferenceNo().equals(ref))
    .findFirst();
```

This is **O(n)** — it reads every record in the map until it finds a match. With 10 records it doesn't matter. With 1,000,000 records, that is up to one million reads per lookup.

The solution is a **secondary index**: a second map maintained alongside the primary one. Its key is the field you want to search by; its value is the primary key.

```java
// Primary map:      subscriptionId → SubscriptionRecord
Map<String, SubscriptionRecord> subscriptions = new ConcurrentHashMap<>();

// Secondary index:  referenceNo → subscriptionId
Map<String, String> referenceIndex = new ConcurrentHashMap<>();
```

Now a lookup by reference is a **two-hop O(1)**:

```java
String id     = referenceIndex.get(referenceNo);  // hop 1: ref → id
return subscriptions.get(id);                      // hop 2: id → record
```

Two instant hash lookups instead of scanning millions of records.

**The index must stay in sync.** Every time you create a record, add its entry to the index. Every time you delete a record, remove its entry from the index. If the indexes drift out of sync, lookups return wrong or null results.

This is the same concept databases use internally. A database index is a separate data structure (usually a B-tree) that maps a column value to the row ID — enabling fast lookups without a full table scan. Here we do the same thing manually with Java maps.

**Cost:** Each index is an extra map in memory, and every write must update all indexes. For a sandbox this is trivial. For very large datasets it is a deliberate tradeoff: more memory and more write work in exchange for faster reads. In systems that read far more than they write — like a payment sandbox with millions of lookups per subscription — it is always worth it.

---

## 46. Separating create from update in the store

The original `InMemoryStore` had a single `saveSubscription(id, record)` method used for both creating a new subscription and overwriting an existing one after an update.

This became a problem once secondary indexes were added: on **create**, the indexes must be populated. On **update**, they must NOT be touched — the fields the indexes track (`referenceNo`, `debitAccount`, `productId`) never change on update, so re-adding them is harmless, but if they ever *could* change it would create stale entries.

The solution is two explicit methods:

```java
// Creates a new record — populates primary map AND both indexes
void createSubscription(String id, SubscriptionRecord record);

// Updates an existing record — only touches the primary map
void updateSubscription(String id, SubscriptionRecord record);
```

Each method's name now tells the caller exactly what side effects it has. The caller no longer needs to decide whether to "save" — `save` is a meaningless word that describes the *how*. `create` and `update` describe the *why*.

This is a broader principle: **method names should reflect intent, not implementation**. A reader seeing `store.createSubscription(...)` immediately knows a new record is being inserted and indexes are being populated. Seeing `store.updateSubscription(...)` they know only data fields are changing and no index work is needed.

This also makes the code safer: if someone accidentally calls `createSubscription` on an already-existing ID, it would double-write the indexes (harmless here since it is the same key, but clearly wrong behaviour). With two methods, the distinction is encoded in the name and the code is self-documenting.

---

## 47. Data normalization — keeping your data lean

**Normalization** is the process of structuring your data so that every piece of information is stored in exactly one place. Your supervisor's description — "getting your data as lean as possible" — captures the goal: no redundancy, no duplication, no field that says the same thing twice.

The motivation is practical. If the same value (say, a merchant's callback URL) is stored in a hundred different records and the merchant changes it, you have to update a hundred records. If you stored it once, you change it once. Normalization eliminates that class of bug.

---

### The three normal forms

Normalization is usually described in levels called **normal forms**. Each one builds on the previous.

#### First Normal Form (1NF) — atomic values

Every field must hold a single, indivisible value. No field should contain a list or a comma-separated bundle of things.

**Violation:**
```
| subscriptionId | debitAccounts              |
|----------------|----------------------------|
| SUB001         | 0241234567, 0209876543     |  ← two values in one field
```

**1NF:**
```
| subscriptionId | debitAccount  |
|----------------|---------------|
| SUB001         | 0241234567    |
| SUB001         | 0209876543    |  ← separate rows, one value each
```

In this project every field in `SubscriptionRecord` holds one value — `debitAccount` is a single String, not a comma-separated list. That is 1NF.

---

#### Second Normal Form (2NF) — no partial dependencies

Every non-key field must depend on the **entire** primary key, not just part of it.

This only matters when your primary key is a composite key (two or more fields together). If your key is just one field, you are automatically 2NF once you are 1NF.

**Example violation** (hypothetical — imagine a transaction table keyed by `subscriptionId + date`):
```
| subscriptionId | date       | debitAmount | merchantName  |
|----------------|------------|-------------|---------------|
| SUB001         | 2026-05-01 | 50.00       | Acme Corp     |
```

`merchantName` depends only on `subscriptionId`, not on the combination of `subscriptionId + date`. That is a partial dependency — a 2NF violation. If the merchant changes their name, you have to update every row for every transaction date, not just one place.

**Fix:** move `merchantName` to a separate merchants table keyed by `subscriptionId` (or better, `merchantId`).

---

#### Third Normal Form (3NF) — no transitive dependencies

Every non-key field must depend **directly** on the primary key, not on another non-key field.

**Example violation:**
```
| subscriptionId | merchantId | callbackUrl              |
|----------------|------------|--------------------------|
| SUB001         | MERCH_123  | https://acme.com/webhook |
| SUB002         | MERCH_123  | https://acme.com/webhook |  ← repeated
| SUB003         | MERCH_456  | https://other.com/hook   |
```

Here `callbackUrl` depends on `merchantId`, not on `subscriptionId`. The dependency chain is:

```
subscriptionId → merchantId → callbackUrl
```

`callbackUrl` reaches the primary key only *through* `merchantId`. That is a transitive dependency — a 3NF violation. If Acme changes their URL, every one of their subscriptions must be updated.

**Fix:** move `callbackUrl` to a separate table keyed by `merchantId` (or `merchantId + productId`).

---

### How this project applies normalization

#### The provision pattern is a textbook 3NF fix

`SubscriptionRecord` originally carried a `callbackUrl` field. But that URL belongs to the merchant + product combination, not to any individual subscription. The same URL would be copied across every subscription that merchant registered — a transitive dependency.

The **provision pattern** is the normalized solution:

```java
// callbackUrl lives here — one record per merchant+product
ProvisionRecord {
    merchantId
    productId
    callbackUrl        ← stored once
    retryAttempts
    skipFactor
}

// SubscriptionRecord no longer needs to own the URL
SubscriptionRecord {
    id (subscriptionId)
    merchantId         ← points back to the provision record
    productId          ← together, these are the "foreign key"
    debitAccount
    debitAmount
    ...
}
```

When `CallbackService` needs the URL, it resolves it via `store.getProvision(merchantId, productId)` — one lookup, one source of truth. If the merchant changes their URL, they call `POST /provision` once. All future callbacks use the new URL automatically, for all their subscriptions, with no data migration.

This is 3NF applied directly: the field that was transitively dependent (`callbackUrl → merchantId`) has been moved to the table it actually belongs to.

---

### Where this project intentionally breaks normalization

Look at `TransactionRecord`:

```java
public class TransactionRecord {
    private String subscriptionId;  // ← link back to the subscription
    private String merchantId;      // ← also in SubscriptionRecord
    private String productId;       // ← also in SubscriptionRecord
    private String debitAccount;    // ← also in SubscriptionRecord
    private String debitAmount;     // ← also in SubscriptionRecord
    private String channel;         // ← also in SubscriptionRecord
    ...
}
```

All those fields already exist in the linked `SubscriptionRecord`. A fully normalised design would remove them from `TransactionRecord` and look them up via `subscriptionId` whenever needed. So why are they duplicated here?

This is a deliberate **denormalization** — a conscious choice to break the rule for a performance reason.

In a real system, transaction records are read far more often than they are written. Every time someone queries a transaction, they want to see the account number, the merchant, the amount — everything in one place. If that data lived only in the subscription record, every transaction query would require a second lookup. Under high read volume, that cost adds up.

By copying the fields into `TransactionRecord` at write time (when the transaction is created), reads become a single map lookup instead of two. The tradeoff is that if a subscription's fields ever change (the account is updated, for example), the already-recorded transactions will show the old values — but for a financial audit trail, that is actually correct behaviour. You want the transaction to record what the account was *at the time*, not what it is now.

---

### Summary: normalization tradeoffs at a glance

| Approach | Storage | Write complexity | Read complexity | Risk |
|----------|---------|------------------|-----------------|------|
| Fully normalised | Lean, no duplication | Simple | Requires joins/lookups | Stale reads impossible — one source of truth |
| Denormalized | Some duplication | Must update all copies | Single lookup, fast | Copies can drift out of sync |

The right answer is almost always: **normalize by default**, then **denormalize deliberately** where read performance justifies it — and document why.

---

## Things this project taught you

**Java fundamentals**
- Static typing forces you to be explicit — the compiler catches whole classes of bugs before the program runs
- `null` is the most dangerous value in Java; always check before using an object
- `Boolean` (object) vs `boolean` (primitive) — use `Boolean.TRUE.equals()` to safely handle nullable booleans
- Interfaces enforce completeness — if you add a method to an interface, every implementing class must implement it or the build fails

**Spring Boot**
- How Spring Boot routes HTTP requests to controller methods via `@RequestMapping` and `@PostMapping`
- How Java's annotation system works as a configuration mechanism — annotations are instructions to the framework, not the compiler
- `@RestController` automatically serialises return values to JSON; without it you get HTML
- `ResponseEntity` gives you control over HTTP status codes, not just the response body
- `required = false` on `@RequestHeader` lets you control your own error responses instead of Spring's generic 400
- The hidden danger of Spring Security: adding the dependency automatically locks down all endpoints with Basic Auth

**Architecture**
- Why layering (controller → service → store) makes code maintainable — each layer has one job
- Why DTOs exist — they protect internal models from external API changes and keep validation separate from storage
- The provision pattern: register shared configuration once at onboarding rather than repeating it on every request
- The fallback resolution pattern: try a primary source, fall back to a secondary source — useful for cache/database, provision/request, env/default

**Data and storage**
- `ConcurrentHashMap` vs `HashMap` — thread safety matters the moment you add async operations
- Composite map keys (`"merchantId:productId"`) — how to store and retrieve by multiple fields using a simple string map
- The partial update / merge pattern — only overwrite fields the caller explicitly provided
- Secondary indexes: a second map keyed by the lookup field points to the primary key, turning O(n) full-map scans into O(1) two-hop lookups — but the indexes must be kept in sync on every write and delete
- Separating `createSubscription` from `updateSubscription`: method names should reflect intent (what the caller is trying to do), not implementation (what the method does internally)
- Data normalization: store each fact in exactly one place — 1NF (atomic values), 2NF (no partial dependencies), 3NF (no transitive dependencies); the provision pattern is a real application of 3NF
- Deliberate denormalization: copying fields into `TransactionRecord` at write time trades storage for read speed and preserves a point-in-time audit trail — acceptable when the reason is explicit

**Tools and testing**
- How Lombok eliminates boilerplate (`@Data`, `@Builder`, `@Slf4j`, `@RequiredArgsConstructor`) while keeping code readable
- How the Builder pattern prevents bugs from argument ordering mistakes — named fields are unambiguous
- The `.http` file format — test requests that live inside the repository alongside the code
- The Scenario Engine pattern — deterministic test outcomes via account number suffixes, no real third-party required

**Build tools and project structure**
- Gradle vs Maven: Gradle is faster (incremental builds, build cache), more flexible, and uses Kotlin DSL with IDE autocomplete
- The Gradle wrapper (`./gradlew`) pins a specific Gradle version so every developer and CI server builds identically — no global install needed
- Feature-based packaging (`subscriptions/`, `transactions/`) keeps related code together; layer-based packaging (`controllers/`, `services/`) splits it apart
- `application.properties` is for config that changes per environment — never hardcode delays, URLs, or secrets in Java source files
- Gradle heavily depends on internal Java APIs, meaning every Gradle version has a maximum supported Java version. Using an unsupported Java version causes immediate crashes.
- Dependencies live in the `build.gradle.kts` `dependencies {}` block.
- Never commit `.gradle/` or `build/` to Git, but do commit your Gradle wrapper scripts and `.properties` so others can build easily.

**Async and callbacks**
- Why `@Async` only works when called from **outside** the class — Spring uses a proxy, and internal calls bypass it
- How thread pools work — core size, max size, queue capacity
- Why async matters for API responsiveness — return immediately, process in the background
- How to simulate realistic API behaviour (delays, staged callbacks) without a real payment network

**API documentation (OpenAPI / Swagger)**
- The OpenAPI specification is a machine-readable JSON/YAML description of every endpoint, header, body, and response — tools like Swagger UI, Postman, and code generators all consume it
- Springdoc scans `@RestController` classes at startup and auto-generates the spec from what it finds — one Gradle dependency is all it takes
- Swagger UI is a JavaScript SPA bundled inside the springdoc JAR; it fetches `/v3/api-docs` and renders the docs portal; it knows nothing about Java specifically
- "Try it out" fires real HTTP requests from the browser directly to your running server — not a simulation
- Security schemes (`@SecurityScheme` + `addSecurityItem`) create the Authorize button — fill headers in once, sent with every request
- `@Parameter(hidden = true)` removes a `@RequestHeader` from the per-endpoint form without affecting runtime injection — use this when the header is already in the Authorize dialog
- `@Tag(name, description)` groups controller endpoints into named sidebar sections; `@Operation(summary, description)` gives each endpoint its one-liner and detail text; both support Markdown
- Swagger UI appearance and behavior are controlled via `springdoc.swagger-ui.*` properties — path, sorters, doc-expansion, try-it-out enabled
- `@Schema` on DTO fields adds field-level descriptions and example values to the Try It body form — standard for production APIs facing external developers
- Java text blocks (`"""..."""`) make multiline strings readable; leading indent is stripped based on the least-indented line; `\s` forces a trailing space that would otherwise be trimmed

**Scheduling and retry logic**
- `@EnableScheduling` + `@Scheduled(fixedDelay = N)` — how to run a task periodically with Spring without any external job queue
- `fixedDelay` vs `fixedRate`: fixedDelay waits N ms *after* the previous run finishes (prevents overlap); fixedRate starts every N ms regardless of how long the task takes
- The retry state machine: `FAILED → RETRYING → SUCCESS | FAILED → EXHAUSTED` — why RETRYING and EXHAUSTED are explicit states rather than being inferred from field values
- Retry collision prevention: the RETRYING status blocks concurrent manual trigger-debit calls during an in-progress scheduler retry
- `OptionalInt` — the primitive-int counterpart to `Optional<T>`, returned by `mapToInt(...).findFirst()` when a stream might produce no value

**Configuration and validation**
- `resolveEffectiveConfig()` — merging caller-supplied config with provision defaults: caller wins, provision fills gaps, never overwrites
- Frequency-based validation constraints: DAILY subscriptions cannot have `notificationStatus=true` or `retryAttempts > 1`, because both make no operational sense at daily frequency
- ProductType vs MerchantType: the type belongs to the product (one merchant can have products of different types), not the merchant — always ask "which entity does this fact describe?" before deciding where a field lives
- Transient failure simulation via account suffixes 002 (fail once then succeed) and 003 (fail twice then succeed) — lets you test the full retry cycle without needing a real bank to misbehave

**Channel and value aliasing**
- Accept old or alias values in the API, remap them internally before any logic runs — callers using stale names don't break, and only one code path exists internally
- Log every remap at INFO level so you can audit it in production: "Channel changed from VODAFONE to TELECEL"

**Custom documentation portal**
- Spring Boot automatically serves files in `src/main/resources/static/` at `/` — no controller needed
- A custom portal reads `/v3/api-docs` via `fetch()` at page load and builds the entire UI from the returned JSON — one source of truth, no manual maintenance
- CSS Grid with `grid-template-columns: 280px 1fr` (two columns) that transitions to `280px 1fr 460px` (three columns) when a `.panel-open` class is toggled — the try-it panel slides in without a reflow of the rest of the page
- `sessionStorage` persists auth header values across page reloads but not across tabs — right tradeoff for a sandbox where you want headers to survive a Cmd+R but not leak into a different browser session
- `$ref` resolution in JavaScript: walk `spec.components.schemas` to turn `{"$ref": "#/components/schemas/Foo"}` into the actual schema object, enabling schema table and example generation
- `marked.js` (CDN) converts Markdown strings from the spec into HTML in one call — the entire API description, including tables, renders correctly without writing a Markdown parser

---


---

## 86. One-to-many secondary indexes with `computeIfAbsent`

The original `accountProductIndex` was `Map<String, String>` — one subscription per account+product. When you need multiple subscriptions per account you change it to `Map<String, Set<String>>`:

```java
// Before (one-to-one):
private final Map<String, String> accountProductIndex = new ConcurrentHashMap<>();
accountProductIndex.put(key, subscriptionId);  // overwrites the previous one

// After (one-to-many):
private final Map<String, Set<String>> accountProductIndex = new ConcurrentHashMap<>();
accountProductIndex
    .computeIfAbsent(key, k -> ConcurrentHashMap.newKeySet())
    .add(subscriptionId);
```

`computeIfAbsent(key, fn)` atomically: checks if the key exists; if not, calls `fn` to create the value and inserts it; then returns the (existing or new) value. `ConcurrentHashMap.newKeySet()` creates a thread-safe `Set` backed by a `ConcurrentHashMap`.

Lookup returns all records:

```java
public List<SubscriptionRecord> getSubscriptionsByAccount(String debitAccount, String productId) {
    Set<String> ids = accountProductIndex.get(debitAccount + ":" + productId);
    if (ids == null || ids.isEmpty()) return Collections.emptyList();
    return ids.stream()
              .map(subscriptions::get)
              .filter(Objects::nonNull)
              .collect(Collectors.toList());
}
```

Deletion removes only the cancelled ID, not the whole key:

```java
Set<String> ids = accountProductIndex.get(indexKey);
if (ids != null) {
    ids.remove(subscriptionId);
    if (ids.isEmpty()) accountProductIndex.remove(indexKey);
}
```

---


---

## 88. Deterministic fake data from a hash

In a sandbox you sometimes need to generate plausible-looking data (like a customer name) that doesn't come from the request, but should be *stable* — the same input always produces the same output. Use `hashCode()` modulo the pool size:

```java
private static final String[] SANDBOX_NAMES = {
    "Ama Owusu", "Kwame Mensah", "Abena Asante", ...
};

private String generateClientName(String debitAccount) {
    int idx = Math.abs(debitAccount.hashCode()) % SANDBOX_NAMES.length;
    return SANDBOX_NAMES[idx];
}
```

`Math.abs()` is needed because `hashCode()` can return a negative integer. The modulo (`%`) maps any integer into the range `[0, SANDBOX_NAMES.length)`. The same phone number will always resolve to the same name, which makes sandbox testing reproducible.

---

