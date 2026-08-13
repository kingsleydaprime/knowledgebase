# Spring Boot & Scheduling

**Source:** merged from `direct-debit-sandbox-java/learning/02-spring-boot-basics.md` and `05-async-scheduling-retry.md`.

## What Spring Boot actually does

Without a framework, standing up an HTTP service means writing your own server, manually wiring every class to every dependency it needs, and hand-rolling JSON parsing. Spring Boot handles all of it — you annotate classes and it wires the object graph at startup:

```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) { SpringApplication.run(Application.class, args); }
}
```

`SpringApplication.run()` scans the classpath for annotated classes, instantiates them, wires their dependencies, and starts listening on a port. Annotations are inert metadata by themselves — `@RestController`, `@Service`, `@RequestMapping` do nothing unless something (Spring's startup scan) reads and acts on them. Forget an annotation and Spring simply doesn't know the class exists.

## Dependency injection

Without DI, a class constructs its own dependencies directly, coupling it to one concrete implementation and making it hard to test:

```java
public class SubscriptionService {
    private InMemoryStore store = new InMemoryStore();   // hardcoded — can't substitute a test double
}
```

With DI, a class declares what it needs and Spring supplies it:

```java
@Service
@RequiredArgsConstructor      // Lombok: generates a constructor for every `private final` field
public class SubscriptionService {
    private final Store store;   // Spring injects whatever implementation is registered
}
```

Spring sees the Lombok-generated constructor and calls it with the beans it manages. Consequences: implementations become swappable (a test can inject a mock `Store`), and `final` prevents any code from reassigning the dependency mid-lifetime — a class can't accidentally end up split across two different store instances with diverging data.

## The layered architecture

```
HTTP request → Controller (headers/body in, calls the service)
             → Service (business logic: validate, decide, orchestrate)
             → Store/Repository (persistence)
             → (async) downstream effects — e.g. firing webhooks
```

Each layer talks only to the layer directly below it. The controller never touches the store; the store never knows HTTP exists. This isolation is what makes each layer independently testable and independently replaceable.

```java
@RestController
@RequestMapping("/subscription")
public class SubscriptionController {
    @PostMapping("/subscribe")
    public Map<String, Object> subscribe(
            @RequestHeader("x-transflowId") String transflowId,
            @RequestBody SubscriptionRequestDto req) { ... }
}
```

`@RestController` = `@Controller` + automatic JSON serialization of return values (without it, Spring returns an HTML view, not JSON). `@RequestMapping` scopes every method's path under a prefix; `@PostMapping("/subscribe")` maps one method to one route + verb.

## Validation

```java
@Data
public class SubscriptionRequestDto {
    @NotBlank private String merchantId;         // not null, not empty, not whitespace-only
    @NotNull  private FrequencyType frequencyType; // enum — Jackson rejects unmatched strings before this even fires
}
```

`@Valid` on the controller parameter triggers the check before the method body runs:

```java
public Map<String, Object> subscribe(@Valid @RequestBody SubscriptionRequestDto req) { ... }
```

Without `@Valid`, the annotations on the DTO are inert. A failed check short-circuits into Spring's generic `400 Bad Request` — see the header-handling section below for when you'd rather intercept that manually.

## ResponseEntity and explicit status codes

A plain return type (`Map<String, Object>`) always serializes with `200 OK`. `ResponseEntity<?>` gives explicit control over status code, body, and headers when different outcomes need different HTTP codes:

```java
@PostMapping("/pause")
public ResponseEntity<?> pause(...) {
    if (isUnauthorized(...)) {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(errorDto);
    }
    return ResponseEntity.ok(service.pause(request));
}
```

`ResponseEntity.ok(body)` is shorthand for `.status(200).body(body)`. Use `ResponseEntity` when status codes genuinely branch; return the object directly when every path is `200 OK`.

## Manual vs automatic header validation

```java
@RequestHeader("x-transflowId") String id                       // strict: Spring 400s automatically if missing
@RequestHeader(value = "x-transflowId", required = false) String id  // lenient: id is null, you decide the response
```

The lenient form lets you return a structured error body with your own error code instead of Spring's generic 400 — useful when a missing auth header should read as `401`, not `400`, which Spring's automatic strict-header rejection can't express.

## HandlerInterceptor — a gate before every controller

An interceptor runs before any matching controller method executes. Returning `false` from `preHandle()` stops the request there — the controller body never runs:

```java
@Component
@RequiredArgsConstructor
public class AuthGuardInterceptor implements HandlerInterceptor {
    @Override
    public boolean preHandle(HttpServletRequest req, HttpServletResponse resp, Object handler) throws Exception {
        if (invalid(req)) {
            resp.setStatus(HttpServletResponse.SC_OK);
            objectMapper.writeValue(resp.getWriter(), Map.of("responseCode", "107"));
            return false;
        }
        return true;
    }
}
```

Registered with path exclusions for public routes:

```java
registry.addInterceptor(authGuardInterceptor)
        .addPathPatterns("/**")
        .excludePathPatterns("/provision", "/docs/**", "/v3/api-docs", "/v3/api-docs/**");
```

**Gotcha**: Spring's `AntPathMatcher` treats `/**` as "this path and everything under it" but does **not** match the bare path itself. `/v3/api-docs/**` matches `/v3/api-docs/openapi.json` but not `/v3/api-docs` — both the bare path and the `/**` variant need listing whenever a route and its sub-routes should both be public. `@RequiredArgsConstructor` only generates a constructor parameter for `final` fields *without* an inline initializer — `private final ObjectMapper m = new ObjectMapper()` is excluded, so `ObjectMapper` doesn't need to be a registered Spring bean.

## @Async — offloading work from the request thread

A caller shouldn't block on slow downstream work (e.g. firing a webhook) that doesn't affect the HTTP response:

```java
@Async("callbackExecutor")
public void fireCallbacks(SubscriptionRecord record) {
    Thread.sleep(2000);
    firePreapprovalCallback(record);
}
```

`@Async` tells Spring to run the method on a background thread pool and return immediately — configured with the same `corePoolSize`/`maxPoolSize`/`queueCapacity` knobs covered in [[languages/01-java/02-jvm-and-concurrency/02-concurrency]]. **Gotcha**: `@Async` only takes effect when the method is called from **outside** the declaring class. Spring implements it via a runtime proxy; an internal call (`this.fireCallbacks(...)`) bypasses the proxy entirely and runs synchronously with no warning.

## @Scheduled — periodic background tasks

```java
@SpringBootApplication
@EnableScheduling   // without this, every @Scheduled method in the app is silently ignored — no error
public class Application { ... }
```

```java
@Component
public class RetryScheduler {
    @Scheduled(fixedDelay = 30_000)   // 30_000 — underscore digit separators, purely a readability feature
    public void processRetries() { ... }
}
```

The annotated class must itself be a Spring-managed bean (`@Component`/`@Service`) for the schedule to register.

**`fixedDelay` vs `fixedRate`**: `fixedDelay` waits N ms *after the previous run finishes* before starting again — runs never overlap or pile up, correct for anything where concurrent runs would conflict (like a retry pass). `fixedRate` starts a new run every N ms *regardless of how long the previous run took* — if a run overruns the interval, Spring queues the next one to start immediately after, which can pile up under sustained slowness. Use `fixedDelay` for polling/retry/cleanup jobs that need a cooldown; `fixedRate` for time-sensitive heartbeats where cadence matters more than run duration.

## A retry state machine, as a general pattern

A failed operation isn't always left at a bare `FAILED` — a proper retry loop needs states beyond success/failure:

| Status | Meaning |
|---|---|
| `PROCESSING` | Initial state, result not yet known |
| `SUCCESS` | Terminal — succeeded |
| `FAILED` | Failed, eligible for another retry attempt |
| `RETRYING` | A retry attempt is currently in flight — blocks a concurrent manual retry |
| `EXHAUSTED` | Terminal — all attempts used, will never be retried again |

The `RETRYING` state exists specifically to close a race condition: without it, a scheduled retry firing at the same moment as a manual retry trigger produces two concurrent attempts for the same operation. `EXHAUSTED` is redundant for a filter query (`status = FAILED AND attempts < max` already excludes it) but essential for a human — or another engineer — reading a record and immediately knowing it's permanently done, rather than back-computing that from a field comparison. This is a reusable shape for **any** retry-with-limit system, not specific to payments.

## Related
- [[languages/01-java/03-tooling/03-lombok-and-builders|Lombok & the Builder Pattern]] — `@RequiredArgsConstructor` and DI
- [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency]] — the thread pool sizing behind `@Async`
- [[languages/01-java/05-web-and-api/03-api-design-and-documentation|API Design & Documentation]] — config-resolution and validation patterns that build on this layering

## Seen in the wild
- [[projects/direct-debit-sandbox-java/learning/02-spring-boot-basics|direct-debit-sandbox]] — Spring Boot on a real payments domain
- [[projects/direct-debit-sandbox-java/interview/01-java-and-spring-boot|its interview notes]] — the same material as questions
