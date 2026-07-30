# Direct Debit Sandbox — Spring Boot Basics

Split out from the original single-file `learning.md`. Covers what Spring Boot is, annotations,
dependency injection, the controller/service/store layering, validation, ResponseEntity, header
handling, and request interceptors. See also `01-java-fundamentals.md`.

---

## 8. What is Spring Boot?

Spring Boot is a framework that eliminates enormous amounts of boilerplate. Without it, you would need to:
- Write your own HTTP server
- Manually wire every class to every other class
- Configure JSON parsing by hand

Spring Boot handles all of that. You just annotate your classes and it figures out the rest.

The entry point is [DirectDebitSandboxApplication.java](src/main/java/com/itc/direct_debit_sandbox/DirectDebitSandboxApplication.java):

```java
@SpringBootApplication
public class DirectDebitSandboxApplication {
    public static void main(String[] args) {
        SpringApplication.run(DirectDebitSandboxApplication.class, args);
    }
}
```

`SpringApplication.run(...)` boots the entire server. Spring scans all classes, finds annotations, creates objects, wires them together, and starts listening on port 8080.

---

## 9. Annotations: those @ symbols everywhere

An annotation is metadata attached to a class, method, or field. It tells Spring (or Java itself) to treat that thing specially.

```java
@RestController          // "This class handles HTTP requests"
@Service                 // "This class contains business logic"
@Component               // "This is a general-purpose Spring-managed object"
@RequestMapping("/subscription")   // "All endpoints in this class start with /subscription"
@PostMapping("/subscribe")         // "This method handles POST /subscription/subscribe"
@RequestBody             // "Read the JSON body and turn it into this object"
@RequestHeader("x-key")  // "Read the HTTP header named x-key"
@Async                   // "Run this method in a background thread"
@NotBlank                // "Validation: this field must not be blank"
```

Annotations don't do anything by themselves. Spring reads them at startup and decides what to do. If you forget an annotation, Spring doesn't know about your class and nothing will work.

---

## 10. Dependency Injection: the magic of @RequiredArgsConstructor

Dependency Injection (DI) means: instead of creating your own dependencies, you declare what you need and Spring hands them to you.

Without DI you would write:
```java
public class SubscriptionService {
    private InMemoryStore store = new InMemoryStore();  // you make it yourself
}
```

With DI you write:
```java
@Service
@RequiredArgsConstructor
public class SubscriptionService {
    private final InMemoryStore store;  // Spring gives this to you
}
```

`@RequiredArgsConstructor` is a Lombok annotation that generates a constructor for every `private final` field. Spring sees that constructor and calls it, passing in the objects it manages.

Why is this better? Because:
- You don't create objects, Spring does — so you can easily swap implementations
- Tests can inject fake/mock versions of dependencies
- You can't accidentally have two different stores with different data

The `private final` is important: `final` means the field cannot be reassigned after the constructor runs. This prevents accidental bugs where someone replaces your store mid-request.

---

## 11. The three layers: Controller, Service, Store

This project follows a standard layered architecture:

```
HTTP Request
     ↓
Controller   (receives the request, reads headers/body, calls the service)
     ↓
Service      (business logic: validate, process, decide what to do)
     ↓
Store        (saves/retrieves data from in-memory maps)
     ↓
(async) CallbackService  (fires HTTP callbacks to the merchant's server)
```

Each layer only talks to the layer directly below it. The controller doesn't touch the store directly. The store doesn't know about HTTP. This separation makes each piece easy to understand and change independently.

---

## 12. @RestController and how HTTP requests arrive

```java
@RestController
@RequestMapping("/subscription")
public class SubscriptionController {

    @PostMapping("/subscribe")
    public Map<String, Object> subscribe(
            @RequestHeader("x-transflowId") String transflowId,
            @RequestBody SubscriptionRequestDto req) {
        ...
    }
}
```

When a POST request arrives at `/subscription/subscribe`:

1. Spring finds this controller because of `@RequestMapping("/subscription")`
2. It finds this method because of `@PostMapping("/subscribe")`
3. It reads the `x-transflowId` header and passes it as `transflowId`
4. It takes the JSON body, converts it into a `SubscriptionRequestDto` object, and passes it as `req`
5. The method runs, returns a `Map<String, Object>`
6. Spring converts that Map back to JSON and sends it as the HTTP response

`@RestController` = `@Controller` + automatically convert return values to JSON. Without `@RestController` you would get an HTML page, not JSON.

---

## 13. @Service: where the real logic lives

The service layer is where decisions happen. Look at `subscribe()` in [SubscriptionService.java](src/main/java/com/itc/direct_debit_sandbox/subscriptions/SubscriptionService.java):

```java
// 1. Check if headers are valid
Map<String, Object> authError = validateHeaders(transflowId, apiKey, country);
if (authError != null) return authError;

// 2. Check for duplicate reference
if (store.getSubscriptionByReference(req.getReferenceNo()) != null) { ... }

// 3. Generate IDs
String subscriptionId = "SUB" + UUID.randomUUID()...

// 4. Build the record
SubscriptionRecord record = SubscriptionRecord.builder()...build();

// 5. Save it
store.createSubscription(subscriptionId, record);

// 6. Fire callbacks asynchronously
callbackService.fireCallbacks(record);

// 7. Return processing response
return response;
```

Every business rule lives here, not in the controller and not in the store. If you need to change what happens when someone subscribes, you change the service.

---


---

## 24. Validation: @NotBlank, @NotNull, @Valid

Spring's validation layer lets you declare rules on DTO fields and have them checked automatically before your method even runs.

```java
@Data
public class SubscriptionRequestDto {
    @NotBlank
    private String merchantId;    // must not be null, empty, or whitespace-only

    @NotNull
    private FrequencyType frequencyType;  // must not be null (but empty string doesn't apply to enums)

    private String endDate;  // no annotation = optional, can be null
}
```

In the controller, `@Valid` triggers the check:

```java
public Map<String, Object> subscribe(@Valid @RequestBody SubscriptionRequestDto req) {
```

If `merchantId` is blank, Spring automatically returns a 400 error before your code runs. Without `@Valid`, annotations on the DTO are ignored.

---


---

## 35. ResponseEntity — returning HTTP status codes alongside a body

Most endpoints in this project return a plain `Map<String, Object>`, which Spring serialises to JSON with a `200 OK` status automatically.

But `LifecycleController` uses `ResponseEntity<?>`:

```java
@PostMapping("/pause")
public ResponseEntity<?> pause(...) {
    if (isUnauthorized(transflowId, key, country)) {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                .body(ApiResponseDto.builder()
                        .responseCode("401")
                        .responseMessage("Unauthorized.")
                        .build());
    }
    return ResponseEntity.ok(lifecycleService.pause(request));
}
```

`ResponseEntity` lets you control:
- The **HTTP status code** (200, 401, 404, 500, etc.)
- The **response body**
- The **response headers** (if needed)

`ResponseEntity.ok(body)` is a shortcut for `ResponseEntity.status(200).body(body)`.

The `<?>` means "I don't know the exact type of the body at compile time" — it could be an `ApiResponseDto` (for errors) or a `Map` (for success). The `?` is a **wildcard** that says "any type is acceptable here."

When should you use `ResponseEntity` vs returning the object directly?
- Return `ResponseEntity` when different outcomes produce **different HTTP status codes** (200 vs 401 vs 404)
- Return the object directly when it's always `200 OK` and you just want the JSON body

---

## 36. required = false on headers — manual vs automatic validation

There are two ways to read request headers in Spring:

**Automatic (strict) — Spring throws an error if the header is missing:**
```java
@RequestHeader("x-transflowId") String transflowId
```
If the caller doesn't send `x-transflowId`, Spring returns a `400 Bad Request` before your code even runs.

**Manual (lenient) — your code receives null and decides what to do:**
```java
@RequestHeader(value = "x-transflowId", required = false) String transflowId
```
If the header is missing, `transflowId` is `null`. Your method runs, and you decide the response.

`LifecycleController` uses `required = false` and then calls `isUnauthorized()` manually:

```java
private boolean isUnauthorized(String transflowId, String key, String country) {
    return transflowId == null || transflowId.isEmpty() || ...;
}
```

This gives you control over the **exact error response** — instead of Spring's generic 400 message, you return a structured JSON body with your own `responseCode` and `responseMessage`.

`SubscriptionController` uses the strict version (no `required = false`). Both approaches work; the strict version is less code, the lenient version gives a friendlier error message.

---


---

## 83. HandlerInterceptor — a request gate before the controller

A `HandlerInterceptor` sits between the servlet and your controller. It runs `preHandle()` before any controller method executes. If `preHandle()` returns `false`, the request stops there — the controller is never called.

```java
@Component
@RequiredArgsConstructor
public class AuthGuardInterceptor implements HandlerInterceptor {

    private final Store store;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public boolean preHandle(HttpServletRequest request,
                             HttpServletResponse response,
                             Object handler) throws Exception {
        String transflowId = request.getHeader("x-transflowId");
        // ... validate ...
        if (invalid) {
            response.setStatus(HttpServletResponse.SC_OK);
            response.setContentType(MediaType.APPLICATION_JSON_VALUE);
            objectMapper.writeValue(response.getWriter(), Map.of("responseCode", "107", ...));
            return false;  // stops the chain
        }
        return true;  // proceeds to the controller
    }
}
```

Register it in `WebMvcConfigurer`:

```java
@Override
public void addInterceptors(InterceptorRegistry registry) {
    registry.addInterceptor(authGuardInterceptor)
            .addPathPatterns("/**")
            .excludePathPatterns("/provision", "/docs/**", "/v3/api-docs", ...);
}
```

**Key points:**
- `addPathPatterns("/**")` with `.excludePathPatterns(...)` is the standard way to apply an interceptor everywhere except public routes
- The pattern `/**` does NOT match `/v3/api-docs` (no trailing slash) — you must add that path explicitly as well as `/v3/api-docs/**`
- Writing directly to `response.getWriter()` bypasses the controller entirely — you're responsible for setting `Content-Type` and status yourself
- `@RequiredArgsConstructor` only generates constructor parameters for `final` fields **without initialisers** — `private final ObjectMapper m = new ObjectMapper()` is excluded from the constructor, so `ObjectMapper` doesn't need to be a Spring bean

---


---

## 93. InterceptorRegistry path exclusions — bare paths vs `/**`

Spring's `AntPathMatcher` treats `/**` as "this path and all sub-paths." It does **not** match the bare path without a trailing slash if the path has no sub-paths:

```java
.excludePathPatterns("/v3/api-docs/**")   // matches /v3/api-docs/openapi.json ✅
                                          // does NOT match /v3/api-docs         ❌
```

You must list both:

```java
.excludePathPatterns("/v3/api-docs", "/v3/api-docs/**")
```

The same applies to any endpoint where the bare URL and sub-URLs should both be public. A complete exclusion list for a typical Spring Boot + springdoc project:

```java
.excludePathPatterns(
    "/provision",
    "/", "/index.html", "/docs.js", "/docs.css",
    "/documentation", "/documentation.html",
    "/docs", "/docs/**",
    "/swagger-ui/**", "/swagger-ui.html",
    "/webjars/**",
    "/v3/api-docs", "/v3/api-docs/**",
    "/debug/**"
)
```

`/webjars/**` is easy to forget — springdoc loads its own JavaScript and CSS from `/webjars/`, and requests to those paths will hit the interceptor if not excluded.

*This guide reflects the state of the project as of May 2026.*
