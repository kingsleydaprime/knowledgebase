# direct-debit-sandbox-java — Java & Spring Boot

From [`../learning/01-java-fundamentals.md`](../learning/01-java-fundamentals.md),
[`02-spring-boot-basics.md`](../learning/02-spring-boot-basics.md),
[`03-dtos-lombok-builder.md`](../learning/03-dtos-lombok-builder.md),
[`07-build-tools-and-project-structure.md`](../learning/07-build-tools-and-project-structure.md).

---

### Q1. [Beginner] 🔥 Explain the three layers — Controller, Service, Store — and why the boundaries matter.

**Strong answer covers:** the **controller** owns HTTP: routes, headers, request/response DTOs,
status codes. The **service** owns business logic — validation rules, state transitions, callback
orchestration — and knows nothing about HTTP. The **store** owns persistence and lookup.

The value is testability and change isolation: swapping the in-memory store for a real database
touches one layer, and business rules can be tested without a servlet. The rule to state: **each
layer talks only to the one below it**, and HTTP concepts must not leak downward — a service that
returns a `ResponseEntity` has already broken the boundary.

---

### Q2. [Beginner] 🔥 How does dependency injection work here, and what does `@RequiredArgsConstructor` have to do with it?

**Strong answer covers:** Spring builds the object graph — components are registered
(`@RestController`, `@Service`, `@Component`) and Spring supplies their dependencies at
construction. `@RequiredArgsConstructor` is Lombok generating a constructor for all `final` fields;
Spring sees a single constructor and injects by type without needing `@Autowired`.

**Why constructor injection over field injection:** dependencies are `final` (immutable, and
impossible to forget), the class is constructible in a plain unit test with `new`, and a missing
dependency fails at startup rather than as a `NullPointerException` at request time.

---

### Q3. [Beginner] What actually happens when an HTTP request arrives at a `@RestController` method?

**Strong answer covers:** the servlet container hands the request to Spring's `DispatcherServlet`,
which matches a handler by path and method, runs any registered interceptors' `preHandle`, binds
path variables/query params/headers, deserialises the JSON body into the DTO via Jackson, applies
`@Valid` if present, invokes the method, then serialises the return value back to JSON.
`@RestController` is `@Controller` + `@ResponseBody`, which is what makes the return value the body
rather than a view name.

---

### Q4. [Intermediate] 🔥 How does validation work, and what's the difference between `@NotBlank`, `@NotNull` and `@Valid`?

**Strong answer covers:** `@NotNull` rejects null but allows `""`; `@NotBlank` (Strings only)
rejects null, empty, and whitespace-only — which is what you almost always want for an identifier or
account number. `@Valid` on the controller parameter is what *triggers* the validation of the
annotated DTO; without it the constraints are inert decoration.

**The trap to name:** `@Valid` doesn't cascade into nested objects unless the nested field is itself
annotated `@Valid`. A DTO with a validated inner object silently skips those rules otherwise.

---

### Q5. [Intermediate] 🔥 Why does this API have so many small DTO classes instead of passing entities around?

**Strong answer covers:** the DTO is the **contract**; the internal record is an implementation
detail. Returning an internal record directly means every field you add internally leaks into the
public API, a rename becomes a breaking change, and sensitive fields escape by default rather than
by mistake. Separate request and response DTOs also mean validation constraints live on the input
shape without polluting the storage shape.

**The specific rule from the project:** don't return internal records directly — map to a response
DTO explicitly, even when the shapes currently match, because "currently match" is a temporary
condition.

---

### Q6. [Intermediate] What does Lombok's `@Builder` give you over a constructor, and when is it wrong?

**Strong answer covers:** for a class with many optional fields, a builder is readable at the call
site (`.merchantId(x).productId(y).build()`) and immune to the classic bug of two adjacent
same-typed constructor parameters being swapped silently. It's wrong when the class has few fields
(a constructor is clearer), or when it lets you `build()` an object missing required fields — a
builder makes everything optional by default, so required-field enforcement has to be added
deliberately.

**Follow-up from the notes — conditional field preservation in builders:** when rebuilding a record
to change one field, `.toBuilder()` preserves the rest; constructing a fresh builder silently drops
every field you didn't set. That's a real source of "the field mysteriously became null after an
update."

---

### Q7. [Intermediate] 🔥 `Boolean.TRUE.equals(flag)` instead of `if (flag)`. Why?

**Strong answer covers:** a boxed `Boolean` can be `null`, and `if (flag)` auto-unboxes, so a null
throws `NullPointerException` at runtime. `Boolean.TRUE.equals(flag)` treats null as false without
throwing. It matters here because request DTO fields are boxed types precisely so that "absent" is
distinguishable from `false` — which is the right modelling choice, and this idiom is the cost of it.

---

### Q8. [Intermediate] Why enums rather than String constants for things like channel and product type?

**Strong answer covers:** the compiler enforces the set — an invalid value is impossible rather than
merely unlikely, `switch` can be checked for exhaustiveness, and the valid values are discoverable
from the type rather than from documentation. Strings give you typos that compile fine and fail at
runtime, and no way to enumerate what's legal.

**Project-specific follow-up — channel aliasing:** a deprecated channel value is remapped to its
replacement internally, so old clients keep working while the internal code deals with one canonical
set. That's the general pattern for evolving an enum in a public API: accept the old name at the
boundary, normalise immediately, never let both spellings into the core.

---

### Q9. [Intermediate] `Optional` and `OptionalInt` — where did they help?

**Strong answer covers:** `Optional` makes "may be absent" part of the *type*, so the caller can't
forget to handle it, unlike a nullable return where nothing prompts them. `OptionalInt` specifically
avoids boxing when pulling a nullable primitive `int` out of a stream — `max()`/`min()` return
`OptionalInt` because an empty stream has no answer, and forcing the caller through `isPresent()` /
`orElse()` is exactly right there.

**The idiom to avoid:** `Optional` as a field or a method parameter. It's designed as a return type;
using it elsewhere adds a wrapper without adding safety.

---

### Q10. [Advanced] 🔥 Explain the `HandlerInterceptor` auth guard. Why an interceptor rather than checking in every controller?

**Strong answer covers:** `preHandle` runs before any controller method, and returning `false` stops
the chain — the controller is never invoked. That's the right place for a cross-cutting concern like
"every endpoint requires these headers": one implementation, impossible to forget on a new endpoint,
and the controllers stay free of auth code.

**The project-specific detail:** rather than returning 401, the interceptor writes the JSON body
itself with `response.setStatus(SC_OK)` and a business `responseCode` of `107`, matching the API's
convention that everything is HTTP 200 (see
[02-domain-and-api-design.md](02-domain-and-api-design.md) Q6). It uses `ObjectMapper` directly
because at that point in the chain there's no controller return value for Spring to serialise.

---

### Q11. [Advanced] 🔥 You registered path exclusions on the interceptor and hit a bare-path vs `/**` gotcha. Explain.

**Strong answer covers:** `excludePathPatterns("/docs")` matches *exactly* `/docs` and nothing
beneath it; `"/docs/**"` matches the subtree but — depending on the matcher — may not match the bare
`/docs` itself. So excluding a docs portal or a Swagger UI needs **both** patterns, or you get the
confusing result where the index page is reachable and its assets 107 out (or vice versa). The
general lesson: path-pattern matching is not intuitive at the boundary between a path and its
subtree, and "it works for the page but not the CSS" is the signature of exactly this.

---

### Q12. [Intermediate] `required = false` on a header — why would you deliberately turn off automatic validation?

**Strong answer covers:** with `required = true`, a missing header makes Spring reject the request
with its own 400 error *shape*, which doesn't match this API's `{responseCode, responseMessage}`
convention. Setting `required = false` lets the header arrive as null and be validated manually, so
the error response is consistent with every other error the API produces. It's trading framework
convenience for a uniform contract — and worth naming that the cost is manual checks that can be
forgotten, which is exactly why the interceptor exists to centralise them.

---

### Q13. [Beginner] What is `ResponseEntity` and when do you need it?

**Strong answer covers:** it wraps body + status + headers, so you can vary the status or add
headers rather than always returning 200 with the serialised return value. In this project it's used
even for errors — but with `ResponseEntity.ok(...)` carrying a business error code, because the
convention is 200-for-everything. Worth adding: once that migration happened, the `HttpStatus`
import became unused and removing it is part of finishing the change.

---

### Q14. [Beginner] Maven vs Gradle — what did you use, and what's the actual difference?

**Strong answer covers:** Maven is declarative XML with a fixed lifecycle — verbose but utterly
predictable, and still the default in most enterprise Java. Gradle is a programmable build
(Groovy/Kotlin DSL) with incremental builds and a daemon, so it's faster and more flexible at the
cost of a build file that can contain real logic. Both resolve the same dependencies from the same
repositories; the artefacts land in the local cache (`~/.m2` or `~/.gradle`), which is worth knowing
when a "missing dependency" is really a corrupt cache.

---

### Q15. [Intermediate] 🔥 What's "the hidden danger of the Spring Security dependency"?

**Strong answer covers:** adding `spring-boot-starter-security` doesn't just make security
*available* — auto-configuration immediately **activates** it. Every endpoint becomes authenticated
by default, a login form appears, a generated password is printed to the console, and CSRF
protection starts rejecting your POSTs. A dependency added "for later" instantly breaks a working
API, and the symptom (401s everywhere, or a redirect to a login page) doesn't obviously point at a
line in `build.gradle`.

**The general lesson:** in Spring Boot, adding a starter is a behavioural change, not just a
classpath change. That's the whole point of auto-configuration and it's also its sharpest edge.

---

### Q16. [Beginner] What belongs in git and what doesn't, for a Java project?

**Strong answer covers:** commit sources, `build.gradle`/`pom.xml`, and the **wrapper** (`gradlew`,
`gradle/wrapper/`) so everyone builds with the same tool version. Ignore `build/`, `target/`, IDE
directories, and anything holding credentials. The wrapper is the one people get wrong — it looks
like a generated artefact and is actually the reproducibility mechanism.
