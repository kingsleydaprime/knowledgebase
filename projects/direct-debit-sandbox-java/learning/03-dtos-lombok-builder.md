# Direct Debit Sandbox — DTOs, Lombok & the Builder Pattern

Split out from the original single-file `learning.md`. Covers why DTOs exist, Lombok's
`@Data`/`@Builder`/`@Slf4j`, the Builder pattern, conditional field preservation on update, and
mapping internal records to API responses. See also `02-spring-boot-basics.md` and
`04-data-storage-patterns.md`.

---

## 14. DTOs: why we have so many small classes

DTO stands for **Data Transfer Object**. It's a class whose only job is to carry data.

When a JSON body arrives:
```json
{
  "merchantId": "MERCH_123",
  "debitAccount": "0241234567",
  "debitAmount": "50.00"
}
```

Spring needs somewhere to put this data. It creates a `SubscriptionRequestDto` and fills in the fields.

Why not use the `SubscriptionRecord` directly? Because:
- The request shape is different from the stored shape (e.g., `subscriptionId` and `mandateId` are generated, not sent by the caller)
- DTOs can have validation annotations without polluting the storage model
- Input and output can evolve independently

You will see many DTOs: `SubscriptionRequestDto`, `UpdateRequest`, `CancelRequest`, `CustomerSubRequest`, etc. Each matches exactly what one endpoint needs.

---

## 15. Lombok: @Data, @Builder, @Slf4j

Lombok is a library that generates Java boilerplate at compile time. It saves hundreds of lines.

**@Data** generates: getters, setters, `equals()`, `hashCode()`, `toString()`.

Without Lombok:
```java
public class CancelRequest {
    private String subscriptionId;
    
    public String getSubscriptionId() { return subscriptionId; }
    public void setSubscriptionId(String s) { this.subscriptionId = s; }
    // ... equals, hashCode, toString ...
}
```

With Lombok:
```java
@Data
public class CancelRequest {
    private String subscriptionId;
}
```

**@Builder** generates a fluent builder pattern (explained in section 25).

**@Slf4j** generates a logger field called `log`. Instead of writing:
```java
private static final Logger log = LoggerFactory.getLogger(CallbackService.class);
```
You just write `@Slf4j` on the class and then use `log.info(...)`, `log.error(...)` anywhere.

**@RequiredArgsConstructor** generates a constructor for all `final` fields (used for DI).

---


---

## 25. The Builder pattern

The Builder pattern solves a problem: constructors with many parameters are hard to read.

Without Builder:
```java
new SubscriptionRecord("SUB123", "MAND456", "MERCH789", "PROD001",
    "0241234567", "50.00", FrequencyType.MONTHLY, "2026-01-01",
    "2027-01-01", "15", "14:30", "REF001", "MTN", "GHS", "GH",
    "0241234567", "https://callback.url", "ACTIVE", true, true, null, "2026-05-07T12:00:00Z");
```

Which argument is which? Impossible to tell.

With `@Builder` (Lombok generates this):
```java
SubscriptionRecord record = SubscriptionRecord.builder()
        .subscriptionId("SUB123")
        .mandateId("MAND456")
        .merchantId("MERCH789")
        .debitAccount("0241234567")
        .debitAmount("50.00")
        .status("ACTIVE")
        .build();  // <-- the builder assembles the object
```

Every field is explicitly named. You can skip optional fields. You can read it without counting positions.

The `.build()` call at the end is required — it actually creates the object. Before `.build()`, you're talking to the Builder helper object, not the real SubscriptionRecord.

---


---

## 38. Conditional field preservation in builders

When `ProvisionService` updates an existing provision record, it needs to preserve any config values the caller didn't send:

```java
ProvisionRecord existing = store.getProvision(req.getMerchantId(), req.getProductId());

ProvisionRecord record = ProvisionRecord.builder()
        .callbackUrl(req.getCallbackUrl())   // always overwrite this
        .retryAttempts(
            req.getRetryAttempts() != null
                ? req.getRetryAttempts()              // caller sent a new value → use it
                : (existing != null ? existing.getRetryAttempts() : null)  // keep old value
        )
        .build();
```

Reading the ternary `? :` operator for the first time:
```java
condition ? valueIfTrue : valueIfFalse
```

So:
```java
req.getRetryAttempts() != null ? req.getRetryAttempts() : existing.getRetryAttempts()
```
means: "if the request included `retryAttempts`, use it; otherwise keep whatever was there before."

This is called a **partial update** or **merge** pattern. It means callers can update a single field without accidentally wiping out fields they didn't mention. You saw the same pattern earlier in `SubscriptionService.update()`:

```java
if (req.getDebitAmount() != null) existing.setDebitAmount(req.getDebitAmount());
if (req.getDebitDay()    != null) existing.setDebitDay(req.getDebitDay());
```

Both approaches do the same thing — only overwrite what was explicitly provided. The builder version combines everything into one construction step; the setter version mutates an existing object field by field. Neither is wrong; the builder is generally preferred for new objects, setters for patching existing ones.

---


---

## 87. Response mapping — don't return internal records directly

Returning a `PreAuthRecord` directly from a `retrievePreAuthDetails` endpoint leaks internal field names (`createdAt`, `channel`, `referenceNo`) that differ from the API contract (`created`, `debitSource`, `refNo`). The fix is a dedicated mapping method:

```java
private Map<String, Object> toRetrieveResponse(PreAuthRecord r) {
    Map<String, Object> m = new LinkedHashMap<>();
    m.put("preApprovalId", r.getPreApprovalId());
    m.put("debitSource",   r.getChannel());      // renamed
    m.put("refNo",         r.getReferenceNo());  // renamed
    m.put("mandateType",   "authorization");      // computed constant
    m.put("status",        r.getStatus().toLowerCase()); // normalised
    m.put("created",       r.getCreatedAt());    // renamed
    m.put("updated",       r.getUpdatedAt());    // renamed
    // callbackUrl intentionally omitted — internal only
    return m;
}
```

**Why `LinkedHashMap`?** A regular `HashMap` doesn't guarantee insertion order, so the JSON fields appear in a random order each call. `LinkedHashMap` preserves insertion order, giving you deterministic, readable JSON output that matches your API contract document.

---

