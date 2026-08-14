# API Design & Documentation

**Source:** merged from `direct-debit-sandbox-java/learning/06-business-domain-flow.md` (the generally-applicable patterns extracted from that project's mandate/subscription domain) and `08-openapi-and-swagger-docs.md`. The custom vanilla-JS docs portal covered in `09-custom-docs-portal-ui.md` is frontend work, not Java — it's summarized here only as context for how a spec gets consumed; the full CSS/JS build (syntax highlighting, retractable sidebar, iframe embedding) is worth reading directly in the original if that's the part of interest.

## RestTemplate — outbound HTTP calls

Spring's built-in synchronous HTTP client, used for calling out to another service (e.g. firing a webhook after processing completes):

```java
HttpHeaders headers = new HttpHeaders();
headers.setContentType(MediaType.APPLICATION_JSON);
HttpEntity<Object> entity = new HttpEntity<>(payload, headers);
ResponseEntity<String> response = restTemplate.exchange(url, HttpMethod.POST, entity, String.class);
```

Defined once as a `@Bean` and injected wherever needed, same as any other Spring-managed dependency (see [[backend/frameworks/java/01-spring-boot]]).

## A catalogue of common Spring/Java runtime errors

| Exception | Usual cause |
|---|---|
| `NullPointerException` | Called a method on a `null` reference — guard with a null check before use (see [[languages/01-java/01-language/01-fundamentals]]) |
| `HttpMessageNotReadableException` | Malformed JSON body, wrong field type, or an enum value that doesn't match any constant |
| `MethodArgumentNotValidException` | A `@NotBlank`/`@NotNull` field failed validation |
| `NoSuchBeanDefinitionException` | Spring can't find a dependency to inject — the target class is missing `@Service`/`@Component`/`@Bean`, or sits outside the scanned package |
| `ConcurrentModificationException` | A plain `HashMap`/`ArrayList` mutated while another thread iterates it — use `ConcurrentHashMap` (see [[languages/01-java/02-jvm-and-concurrency/02-concurrency]]) |
| `@Async` method runs synchronously with no error | Called from inside the same class — Spring's proxy is bypassed (see [[backend/frameworks/java/01-spring-boot]]) |

## The config-resolution / fallback pattern

A common shape: a caller *may* supply configuration per-request, but should fall back to a default registered once elsewhere (at onboarding, in a cache, in an env var) if they don't:

```java
private List<ConfigurationItem> resolveEffectiveConfig(List<ConfigurationItem> requested, ProvisionRecord defaults) {
    List<ConfigurationItem> resolved = requested != null ? new ArrayList<>(requested) : new ArrayList<>();
    Set<String> present = resolved.stream().map(ConfigurationItem::getName).collect(Collectors.toSet());
    if (defaults != null && !present.contains("retryAttempts") && defaults.getRetryAttempts() != null) {
        resolved.add(new ConfigurationItem("retryAttempts", defaults.getRetryAttempts().toString()));
    }
    return resolved;
}
```

Three design choices worth naming explicitly: **caller wins** (an explicit value always beats a registered default), **never overwrite** (build the set of already-present keys first, only fill gaps), and **null-safe** (no config supplied at all still produces a valid, empty starting list). The same shape recurs constantly — cache-then-database, env-var-then-default, per-request-then-account-level-setting.

This is also the mechanism behind the **provision pattern**: instead of every request carrying repeated per-caller config (a webhook URL, retry limits), a caller registers it once, and every subsequent operation resolves it via a lookup rather than requiring it inline — a normalization decision at the API-design level, not just the schema level (see [[languages/01-java/04-persistence/01-jdbc-and-data-modeling]] for the same idea applied to storage).

## Enum-based validation and value migration shims

Accepting a field as a plain `String` accepts *anything*; typos and invalid values only surface downstream. Typing the field as an enum gets free validation from the JSON deserializer — an unmatched value throws before any handler code runs:

```java
public enum Channel { MTN, TELECEL, AT, AIRTEL, BANK, CARD }
@NotNull private Channel channel;   // was: @NotBlank private String channel
```

**When a value gets renamed but old callers still send the old one** (e.g. a rebrand), reject nothing — keep the old value as a valid enum constant and remap it internally before any business logic runs:

```java
public enum Channel { MTN, TELECEL, AT, AIRTEL, BANK, CARD, VODAFONE /* alias for TELECEL */ }

if (Channel.VODAFONE == req.getChannel()) {
    req.setChannel(Channel.TELECEL);
    log.info("Channel changed from VODAFONE to TELECEL");   // auditable in production
}
```

This is a **value migration shim** — absorbing a caller's stale vocabulary at the API boundary so every downstream code path only ever has to reason about one canonical value, instead of scattering `if (x == OLD || x == NEW)` checks throughout the codebase.

## Business codes over raw HTTP status

Real payment/banking APIs commonly return `HTTP 200` for nearly everything and communicate outcome through a `responseCode` field in the body — this avoids clients needing two separate error-handling paths (HTTP status *and* body):

```java
// Before: relies on the client correctly branching on HTTP status
return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(errorDto);

// After: one path — client always parses the body
return ResponseEntity.ok(ApiResponseDto.builder().responseCode("107").responseMessage("...").build());
```

Not universally correct (it breaks tooling and conventions that assume HTTP status carries meaning) — but it's a deliberate, common convention in this domain worth recognizing rather than "fixing" when working in an existing fintech API.

## OpenAPI and springdoc

OpenAPI (formerly Swagger) is a machine-readable JSON/YAML description of an HTTP API — every endpoint, header, request/response shape, in a format tooling (docs portals, code generators, Postman) can consume without custom integration per API.

`springdoc-openapi` generates this spec **from your code** at startup — no YAML hand-written — by scanning `@RestController` classes, reading each mapped method's parameters and `@RequestBody` DTO, and serving the result at `/v3/api-docs`:

```kotlin
implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:2.8.9")   // one line — Swagger UI ships at /swagger-ui.html
```

Annotations shape what the generated spec says without changing runtime behavior:

```java
@Tag(name = "Subscriptions", description = "Create and manage recurring debit subscriptions")   // groups endpoints in the sidebar
@Operation(summary = "Create a subscription", description = "Markdown supported here")           // per-endpoint docs
@Parameter(hidden = true)                                                                         // exclude from the docs form (still injected at runtime)
@Schema(description = "...", example = "0241234001")                                              // per-field docs + pre-filled example
@ApiResponses({ @ApiResponse(responseCode = "401", description = "Missing required headers") })   // document non-200 outcomes
```

**Security schemes** let a UI's "Authorize" button fill in custom auth headers once instead of repeating them on every endpoint's form:

```java
@SecurityScheme(name = "x-transflowId", type = SecuritySchemeType.APIKEY, in = SecuritySchemeIn.HEADER)
```

paired with `.addSecurityItem(new SecurityRequirement().addList("x-transflowId"))` on the spec's `@Bean` definition, and `@Parameter(hidden = true)` on the corresponding `@RequestHeader` parameters so they don't also appear as redundant per-endpoint fields.

## Consuming the spec — Swagger UI vs. a custom portal

Swagger UI is a JavaScript SPA bundled inside the springdoc jar — it fetches `/v3/api-docs` and renders a full docs UI from that JSON, knowing nothing about Java or Spring specifically (the same UI documents a Go or Node backend, given the same spec shape). "Try it out" fires a genuine HTTP request from the browser directly at the running server, not a simulation.

A hand-built portal can do exactly the same thing — fetch `/v3/api-docs`, walk the JSON (resolving `$ref` pointers into `components.schemas` manually), and render a custom UI — trading Swagger UI's zero-maintenance battle-testing for full control over branding and layout. Both read the same spec, so they never drift apart; this is the practical value of generating the spec from code rather than hand-maintaining a YAML file that two consumers could each go stale against independently.

## Related
- [[backend/frameworks/java/01-spring-boot|Spring Boot & Scheduling]] — the controller layer this whole file annotates
- [[languages/01-java/04-persistence/01-jdbc-and-data-modeling|Persistence & Data Modeling]] — the provision pattern as a normalization decision
- [[languages/01-java/01-language/01-fundamentals|Fundamentals]] — enums as a language feature, before their use here as a validation mechanism
