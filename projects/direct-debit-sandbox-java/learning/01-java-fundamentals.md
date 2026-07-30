# Learning Guide: Direct Debit Sandbox in Java + Spring Boot

This guide is written for someone who has never written Java or Spring Boot before.
Every concept is explained from scratch, using examples drawn directly from this codebase.
If you see a piece of syntax in a file and wonder "what does that even mean?" — look it up here.

# Direct Debit Sandbox — Java Fundamentals

Split out from the original single-file `learning.md` (a from-scratch guide to Java and Spring
Boot, written against this codebase). See also `02-spring-boot-basics.md`,
`03-dtos-lombok-builder.md`, `04-data-storage-patterns.md`, `05-async-scheduling-retry.md`,
`06-business-domain-flow.md`, `07-build-tools-and-project-structure.md`,
`08-openapi-and-swagger-docs.md`, and `09-custom-docs-portal-ui.md`.

---

## 1. What is Java, and why does it look like this?

Java is a **statically typed** language. That means you must tell it the type of every variable before you use it. You cannot just write:

```
name = "Kingsley"   // This is Python/JavaScript. Java will refuse.
```

In Java you write:

```java
String name = "Kingsley";  // You declare the type (String) first.
```

Java is also **compiled**. Your code is converted into bytecode before it runs. This is why errors show up at "compile time" before the program even starts — the compiler checks everything first.

Java is **verbose** compared to Python or JavaScript. You will see a lot of `{}` braces, semicolons, and type declarations. This is intentional — it makes large codebases easier to understand because everything is explicit.

---

## 2. Packages and imports

Every Java file starts with a `package` declaration:

```java
package com.itc.direct_debit_sandbox.subscriptions;
```

A package is just a folder path. This file lives in:
`src/main/java/com/itc/direct_debit_sandbox/subscriptions/`

If you want to use a class from a different package, you must `import` it:

```java
import com.itc.direct_debit_sandbox.store.SubscriptionRecord;
```

Without the import, Java doesn't know what `SubscriptionRecord` refers to. Think of imports as "hey Java, this is where that class lives."

---

## 3. Classes, and why everything is inside one

In Java, **all code lives inside a class**. There is no such thing as a loose function floating around. Every method must belong to a class.

```java
public class SubscriptionService {
    // everything in here belongs to this class
}
```

The file name must match the class name exactly. `SubscriptionService.java` must contain `class SubscriptionService`.

---

## 4. Access modifiers: public, private, protected

These control who can see and use things.

| Modifier    | Who can access it                           |
|-------------|---------------------------------------------|
| `public`    | Anyone, from anywhere                       |
| `private`   | Only code inside the same class             |
| `protected` | Same class + subclasses                     |
| (none)      | Only code in the same package               |

In this project you will see:

```java
private final InMemoryStore store;       // Only SubscriptionService can use this
public Map<String, Object> subscribe()   // Anyone can call this (Spring needs it to be public)
private Map<String, Object> validateHeaders()  // Helper used internally only
```

Rule of thumb: make things `private` unless they absolutely need to be public.

---

## 5. Data types: String, int, boolean, List, Map

Java has two kinds of types: **primitives** and **objects**.

Primitives:
```java
int count = 5;           // whole numbers
boolean active = true;   // true or false
double price = 9.99;     // decimal numbers
```

Objects (capital letter, more features):
```java
String name = "Kingsley";          // text
Integer count = 5;                 // int but as an object (can be null)
Boolean active = true;             // boolean but as an object (can be null)
```

Collections:
```java
List<String> names = new ArrayList<>();    // an ordered list of Strings
Map<String, Object> response = new HashMap<>();  // key-value pairs, like a dictionary
```

`Map<String, Object>` means: keys are Strings, values can be anything. You see this heavily used in service return types in this project because the API responses have varying shapes.

---

## 6. Methods: how functions work in Java

A method signature looks like this:

```java
public Map<String, Object> subscribe(String transflowId, String apiKey) {
    // body
}
```

Breaking it down:
- `public` — access modifier (anyone can call this)
- `Map<String, Object>` — the **return type** (what this method gives back)
- `subscribe` — the method name
- `(String transflowId, String apiKey)` — parameters (inputs)

`void` means the method returns nothing:

```java
public void sendCallback(String url) {
    // does something, returns nothing
}
```

---

## 7. null, and why it causes so many bugs

`null` means "no value". In Java, any object variable can be `null`.

```java
SubscriptionRecord record = store.getSubscription("some-id");
// If "some-id" doesn't exist, record is null

record.getStatus();  // CRASH — NullPointerException, because record is null
```

This is why you see null checks everywhere in the services:

```java
if (record == null) {
    // return an error response instead of crashing
    return errorMap;
}
```

The most common Java runtime error is `NullPointerException` (NPE). It means you tried to call a method on something that was null.

---


---

## 16. Enums: a fixed list of choices

An enum is a type with a fixed set of allowed values.

```java
public enum FrequencyType {
    DAILY,
    WEEKLY,
    MONTHLY,
    YEARLY
}
```

Usage in code:
```java
FrequencyType type = FrequencyType.MONTHLY;
```

Usage in JSON: when Jackson (Spring's JSON library) sees `"frequencyType": "MONTHLY"` in a request body, it converts the string `"MONTHLY"` into `FrequencyType.MONTHLY` automatically — because the field in the DTO is typed as `FrequencyType`.

Why use an enum instead of a `String`? Because you can't accidentally send `"MONTHLYYY"` — it will fail validation. The compiler also catches typos.

---

## 17. Interfaces: a contract, not an implementation

An interface says "any class that implements me must have these methods." It doesn't contain any logic itself.

```java
public interface Store {
    void createSubscription(String id, SubscriptionRecord record);
    void updateSubscription(String id, SubscriptionRecord record);
    SubscriptionRecord getSubscription(String id);
    // ... etc
}
```

`InMemoryStore` implements this:
```java
public class InMemoryStore implements Store {
    // provides the actual code for every method in Store
}
```

Why? Because if you later want a database-backed store, you create `DatabaseStore implements Store`. All the services that depend on `Store` work without any changes — they don't care how data is stored, just that it has those methods.

---


---

## 21. The Stream API: filter, map, toList

Java 8 introduced Streams — a way to process collections in a readable, pipeline style.

```java
return subscriptions.values().stream()
        .filter(s -> s.getDebitAccount().equals(debitAccount)
                  && s.getProductId().equals(productId))
        .toList();
```

Reading it left to right:
- `subscriptions.values()` — all SubscriptionRecord objects in the map
- `.stream()` — start processing them as a stream
- `.filter(s -> ...)` — keep only records where the condition is true (`s` is each record)
- `.toList()` — collect the surviving records into a List

The `s -> s.getDebitAccount().equals(debitAccount)` part is a **lambda** — an inline anonymous function. `s` is the parameter, `s.getDebitAccount()...` is the body.

Without streams you would write:
```java
List<SubscriptionRecord> result = new ArrayList<>();
for (SubscriptionRecord s : subscriptions.values()) {
    if (s.getDebitAccount().equals(debitAccount) && s.getProductId().equals(productId)) {
        result.add(s);
    }
}
return result;
```

Same thing, more lines.

---

## 22. The switch expression (the modern kind)

Old Java switch (still valid, but verbose):
```java
String message;
switch (responseCode) {
    case "01":
        message = "Success";
        break;
    case "100":
        message = "Failed";
        break;
    default:
        message = "Unknown";
}
```

Modern Java switch expression (used in [ScenarioEngine.java](src/main/java/com/itc/direct_debit_sandbox/scenarios/ScenarioEngine.java)):
```java
String message = switch (responseCode) {
    case "01"  -> "Transaction processed successfully";
    case "100" -> "Payment failed";
    default    -> "Payment failed";
};
```

- No `break` needed
- The whole thing is an expression — it produces a value you can assign directly
- `->` means "for this case, produce this value"

---


---

## 34. Boolean.TRUE.equals() — handling nullable booleans safely

In Java, `boolean` (lowercase) is a primitive — it can only be `true` or `false`, never `null`.
But `Boolean` (uppercase) is an object — it can be `true`, `false`, **or `null`**.

In DTOs you often use `Boolean` (uppercase) so that a missing field deserializes as `null` rather than defaulting to `false`. But then you have to check for null before using it.

This crashes if `req.getTriggerDebitStatus()` is `null`:
```java
if (req.getTriggerDebitStatus() == true)  // NullPointerException if null
```

This is safe:
```java
Boolean.TRUE.equals(req.getTriggerDebitStatus())
// Returns true  if the value is Boolean.TRUE
// Returns false if the value is Boolean.FALSE
// Returns false if the value is null  — no crash
```

You see this in `SubscriptionService.subscribe()`:
```java
.triggerDebitStatus(Boolean.TRUE.equals(req.getTriggerDebitStatus()))
```

The `SubscriptionRecord` field is a primitive `boolean` — it can't be null. So we convert the nullable `Boolean` from the DTO into a non-nullable `boolean` by using `Boolean.TRUE.equals()`, which turns `null` into `false` safely.

---


---

## 62. OptionalInt — safely extracting a nullable primitive int from a stream

In `SubscriptionService`, the code needs to read a numeric configuration value from a list. The value might not be present at all (the list is empty or the name wasn't found).

Java has `Optional<T>` for objects and `OptionalInt` specifically for the `int` primitive. Using `OptionalInt` avoids the boxing overhead of `Optional<Integer>` and makes the absence case explicit.

```java
private OptionalInt getConfigIntValue(List<ConfigurationItem> config, String name) {
    if (config == null) return OptionalInt.empty();
    return config.stream()
            .filter(c -> name.equals(c.getName()))
            .mapToInt(c -> {
                try { return Integer.parseInt(c.getValue()); }
                catch (NumberFormatException e) { return -1; }
            })
            .findFirst();
    // Returns OptionalInt.of(3) if found, OptionalInt.empty() if not found
}
```

Usage:

```java
OptionalInt retryAttempts = getConfigIntValue(effectiveConfig, "retryAttempts");
if (retryAttempts.isPresent() && retryAttempts.getAsInt() > 1) {
    // validation error
}
```

Why not just return `-1` as a sentinel for "not found"? Because `-1` is a valid return value for a parse failure and would be confusing. `OptionalInt` makes the two cases unambiguous: *absent* (key not in list) vs *present but invalid* (you could refine this further, but here the `catch` maps both to the same downstream behaviour).

The key `OptionalInt` methods:
- `OptionalInt.empty()` — create an absent value
- `OptionalInt.of(value)` — wrap a found value
- `.isPresent()` — returns `true` if a value exists
- `.getAsInt()` — returns the value (throws if called when empty — always check `isPresent()` first)

---


---

## 72. Text blocks — multiline strings in Java

In `OpenApiConfig.java`, the API description is written as a **text block**:

```java
.description("""
    Sandbox environment for testing ITC Direct Debit v2 integrations.

    ## Before you start

    Every API flow begins with a call to **POST /provision**.
    """)
```

Text blocks were introduced in Java 15. Before them, multiline strings required concatenation:

```java
// Old way — unreadable
.description("Sandbox environment for testing ITC Direct Debit v2 integrations.\n\n" +
             "## Before you start\n\n" +
             "Every API flow begins with a call to **POST /provision**.")
```

**Text block rules:**

- Opened with `"""` followed by a newline. You cannot start content on the same line as the opening `"""`.
- Closed with `"""` which can be on its own line (then there's a trailing newline) or at the end of the last content line (no trailing newline).
- Leading whitespace is stripped based on the least-indented line — so you can indent the content to match the surrounding code without that indentation appearing in the final string.
- Escape sequences (`\n`, `\t`, `\"`) still work but are rarely needed since you can just write the actual newline or quote.

Text blocks are useful wherever you need a long string: SQL queries, JSON templates, HTML snippets, Markdown documentation. They make the code far more readable than string concatenation.

The `\s` at the end of a line forces a trailing space that would otherwise be stripped by the indentation normalization. You can see this used in the description:

```java
`merchantId` and `productId` must be **UUIDs**\s
(e.g. `c64bf5f9-f147-4232-8d00-f28105823d6a`).
```

Without `\s`, the two lines would be joined without a space; with it, a single space separates them.

---


---

## 84. UUID validation with `UUID.fromString()`

The simplest way to validate that a string is a well-formed UUID in Java:

```java
private boolean isValidUuid(String value) {
    if (value == null || value.isBlank()) return false;
    try {
        UUID.fromString(value);
        return true;
    } catch (IllegalArgumentException e) {
        return false;
    }
}
```

`UUID.fromString()` throws `IllegalArgumentException` if the string doesn't match the canonical UUID format (`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`). You can also use `@Pattern` on a DTO field if you want Jakarta Validation to handle it:

```java
@Pattern(
  regexp = "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
  message = "merchantId must be a valid UUID"
)
private String merchantId;
```

`@Pattern` fires during `@Valid` processing (before the method body runs), while `UUID.fromString()` in a `try/catch` lets you control the exact error response yourself.

---

## 85. Enum as a utility — `CountryDialingCode`

Enums in Java can hold fields and methods, not just names. This makes them ideal for lookup tables:

```java
public enum CountryDialingCode {
    GH("GH", "233"),
    RW("RW", "250"),
    UG("UG", "256");

    private final String isoCode;
    private final String prefix;

    CountryDialingCode(String isoCode, String prefix) {
        this.isoCode = isoCode;
        this.prefix  = prefix;
    }

    public static Optional<CountryDialingCode> fromIso(String iso) {
        return Arrays.stream(values())
                .filter(c -> c.isoCode.equalsIgnoreCase(iso.trim()))
                .findFirst();
    }

    public Optional<String> validatePhone(String fieldName, String phone) {
        if (!phone.startsWith(prefix))
            return Optional.of(fieldName + " must start with " + prefix);
        return Optional.empty();
    }
}
```

Usage in a service:

```java
CountryDialingCode.fromIso(country)          // Optional<CountryDialingCode>
    .flatMap(c -> c.validatePhone("debitAccount", phone))  // Optional<String> error
    .map(msg -> buildError("100", msg))      // Optional<Map> error response
    .orElse(null);                           // null means valid
```

This chains three Optional operations: find the country, validate the phone, build an error — all without null checks or if-statements.

---

