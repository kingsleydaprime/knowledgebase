# Direct Debit Sandbox — OpenAPI & Swagger Docs

Split out from the original single-file `learning.md`. Covers the OpenAPI specification,
springdoc, Swagger UI, security schemes, `@Tag`/`@Operation`/`@Schema` annotations, and
customizing Swagger UI via `application.properties`. See also `09-custom-docs-portal-ui.md`.

---

## 63. What is the OpenAPI specification?

OpenAPI (formerly Swagger) is a **standard format for describing HTTP APIs**. It is a JSON or YAML document that lists every endpoint, its method, its headers, its request body shape, and its response codes — all in a machine-readable format.

A minimal OpenAPI document looks like this (YAML):

```yaml
openapi: "3.0.3"
info:
  title: "ITC Direct Debit Sandbox API"
  version: "2.0"
paths:
  /subscription/subscribe:
    post:
      summary: "Create a subscription"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/SubscriptionRequestDto"
      responses:
        "200":
          description: "Processing started"
```

Why does this matter?

1. **Tools can read it** — documentation portals, code generators, API testing tools, and mock servers all know how to consume an OpenAPI spec without any custom code.
2. **It is language-neutral** — a Java backend, a Python client, and a JavaScript frontend can all work from the same spec file.
3. **It is the industry standard** — Postman, Insomnia, AWS API Gateway, and dozens of other tools import and export OpenAPI specs.

In this project, `springdoc` generates the spec **automatically from your Java code** and serves it at `/v3/api-docs`. You never write the YAML by hand.

---

## 64. Springdoc — auto-generating the spec from your code

`springdoc-openapi` is a library that inspects your Spring controllers at startup and builds an OpenAPI spec from what it finds.

**How it works:**

1. On startup, springdoc scans every class annotated with `@RestController`.
2. For each `@GetMapping`, `@PostMapping`, etc., it creates one entry in the spec.
3. For each `@RequestBody`, it reads the DTO class and generates a JSON schema from the field names and types.
4. For each `@RequestHeader`, it adds a header parameter.
5. If you add `@Operation`, `@Tag`, or `@Parameter` annotations, it uses those for names and descriptions. If you don't, it infers sensible defaults.
6. The finished spec is served as JSON at `/v3/api-docs`.

**Adding it to a Spring Boot project is one line in `build.gradle.kts`:**

```kotlin
implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:2.8.9")
```

That's it. No other configuration is required to get a working spec. The Swagger UI page is automatically available at `/swagger-ui.html` (or at `/docs` if you configure `springdoc.swagger-ui.path=/docs`).

**Where does the `@Bean OpenAPI` in `OpenApiConfig.java` fit in?**

Springdoc already generates the spec without it. The `@Bean` method only adds metadata: the API title, version, description, server URL, and which security schemes apply globally. Think of it as the "cover page" of the spec — without it the spec still works, it just has no title.

See [OpenApiConfig.java](src/main/java/com/itc/direct_debit_sandbox/config/OpenApiConfig.java).

---

## 65. Swagger UI — the browser interface that reads the spec

Swagger UI is a **single-page web application** bundled inside the `springdoc-openapi-starter-webmvc-ui` JAR. When Spring Boot starts, springdoc serves the Swagger UI static files (HTML, CSS, JavaScript) from inside its own JAR, at the path you configure.

The flow when you open `http://localhost:8080/docs`:

```
Browser loads Swagger UI HTML/JS
       ↓
Swagger UI fetches GET /v3/api-docs
       ↓ (receives the OpenAPI JSON spec)
Swagger UI parses the spec:
  - builds the left sidebar from the tags and operation summaries
  - renders the documentation from summaries and descriptions
  - builds the "Try it out" form fields from the request body schemas
       ↓
User sees the docs portal
```

Swagger UI itself is **just JavaScript** running in the browser. It doesn't know anything about Java, Spring, or your business logic. It only knows about the OpenAPI spec it downloaded from `/v3/api-docs`. If you want to update what Swagger UI shows, you update your annotations — the spec regenerates automatically on the next startup.

This is why the same Swagger UI can document any API regardless of the backend language: PHP, Go, Node.js — as long as the backend serves an OpenAPI spec, Swagger UI can display it.

---

## 66. How "Try it out" actually sends requests

When you click "Try it out" in Swagger UI, fill in the body, and click "Execute", the browser sends a real HTTP request directly from your browser to your server.

```
Browser (running Swagger UI JavaScript)
       ↓  (real HTTP POST to http://localhost:8080/subscription/subscribe)
Spring Boot on localhost:8080
       ↓
Response comes back
       ↓
Swagger UI displays: curl command, request URL, response body, status code
```

**This is important to understand:**

- It is not a simulated request. It is a live HTTP call.
- The request comes from your browser, not from a Postman desktop app or a separate process.
- Your Spring Boot server must be running for Execute to work.
- If your server restarts and resets its in-memory state, any IDs you filled in the form become invalid.

**The Authorize button:**

When you click Authorize and fill in `x-transflowId`, `x-key`, and `x-country`, Swagger UI stores those values in browser memory (not in a cookie, not in localStorage — just in the JavaScript object). Every request fired via Execute automatically includes those headers. This is equivalent to setting "Headers" in Postman.

**The curl preview:**

Below every Execute button, Swagger UI shows the equivalent `curl` command. This is exactly the command you could paste into a terminal and get the same result. It's a great way to learn curl syntax.

---

## 67. @Tag and @Operation — annotating controllers for the docs

Without annotations, springdoc still generates a working spec, but endpoint names are auto-inferred and everything lands in one unnamed group. Annotations are how you organize and describe the docs.

**`@Tag`** on a controller class groups all its endpoints under a named section in the left sidebar:

```java
@Tag(name = "Subscriptions", description = "Create and manage recurring debit subscriptions")
@RestController
@RequestMapping("/subscription")
public class SubscriptionController { ... }
```

All endpoints in this controller now appear under the "Subscriptions" heading. The `description` is shown as a subtitle under the heading.

**`@Operation`** on a method sets the summary and description for one endpoint:

```java
@Operation(
    summary = "Create a subscription",
    description = "Sets up a new recurring debit mandate. Returns `03` immediately. " +
        "A preapproval callback fires after ~2 s, followed by a transaction callback after ~5 s."
)
@PostMapping("/subscribe")
public Map<String, Object> subscribe(...) { ... }
```

- `summary` → the one-line label shown in the collapsed sidebar entry
- `description` → the longer text shown in the expanded documentation panel; supports Markdown

Without `@Operation`, springdoc uses the method name (`subscribe`) as the summary — readable but not ideal.

**Markdown in descriptions:**

Swagger UI renders Markdown inside `description` strings. You can use bold (`**text**`), backtick code spans (`` `fieldName` ``), tables, and bullet lists. This is how the API overview description in `OpenApiConfig.java` renders a full table of scenario outcomes.

---

## 68. Security schemes — the Authorize button

In the real ITC API, every request needs three custom headers: `x-transflowId`, `x-key`, and `x-country`. Filling them in on every individual Try It form would be tedious. Security schemes let you fill them in once.

**How it works in this project:**

Step 1 — declare the header as a security scheme in `OpenApiConfig.java`:

```java
@SecurityScheme(
    name = "x-transflowId",
    type = SecuritySchemeType.APIKEY,
    in = SecuritySchemeIn.HEADER,
    paramName = "x-transflowId",
    description = "Transflow session ID issued at login"
)
```

This tells Swagger UI: "there is a credential called `x-transflowId` that goes in a request header."

Step 2 — apply it globally via the `@Bean` method:

```java
.addSecurityItem(new SecurityRequirement()
    .addList("x-transflowId")
    .addList("x-key")
    .addList("x-country"))
```

This says: "every endpoint in this API requires all three of these credentials."

Step 3 — Swagger UI shows an **Authorize** button. The user fills in the three values once. From then on, every Execute call includes all three headers automatically.

**Why `SecuritySchemeType.APIKEY`?**

OpenAPI supports several security types: `HTTP` (for Bearer/Basic), `APIKEY`, `OAUTH2`, and `OPENIDCONNECT`. Since `x-transflowId` and `x-key` are custom string headers (not a standard Bearer token), `APIKEY` is the correct type. `SecuritySchemeIn.HEADER` tells Swagger UI to put the value in a request header rather than a query parameter or cookie.

---

## 69. @Parameter(hidden = true) — hiding headers from per-endpoint forms

When springdoc scans a method, it reads every `@RequestHeader` parameter and adds it to the "Parameters" section of that endpoint in Swagger UI. Without any extra work, `x-transflowId`, `x-key`, and `x-country` would appear as separate input fields on every single endpoint.

That would work, but it creates a bad experience: three redundant fields on every form, even though you already filled them in via the Authorize button.

The fix is `@Parameter(hidden = true)`:

```java
@PostMapping("/subscribe")
public Map<String, Object> subscribe(
    @Parameter(hidden = true) @RequestHeader("x-transflowId") String transflowId,
    @Parameter(hidden = true) @RequestHeader("x-key") String apiKey,
    @Parameter(hidden = true) @RequestHeader("x-country") String country,
    @Valid @RequestBody SubscriptionRequestDto req) { ... }
```

`hidden = true` tells springdoc: "don't include this parameter in the spec." The header is still injected by Spring at runtime (the method still receives the value) — `hidden` only affects the documentation, not the runtime behavior.

The result: the Try It form shows only the JSON body. The headers come from the Authorize button. This mirrors how the real MomoDeveloper portal works — credentials go in a separate auth section, not repeated on every form.

---

## 70. Customizing Swagger UI via application.properties

Springdoc exposes many settings as Spring Boot properties. All of them start with `springdoc.`:

```properties
# Where Swagger UI is served (default is /swagger-ui.html)
springdoc.swagger-ui.path=/docs

# Where the raw OpenAPI JSON spec is served
springdoc.api-docs.path=/v3/api-docs

# How tags and operations are sorted in the sidebar
springdoc.swagger-ui.tags-sorter=alpha          # alphabetical by tag name
springdoc.swagger-ui.operations-sorter=alpha    # alphabetical by path within each tag

# Show how long each request took in the Try It response panel
springdoc.swagger-ui.display-request-duration=true

# Start all endpoints in "Try it out" mode by default
springdoc.swagger-ui.try-it-out-enabled=true

# Collapse all endpoint groups by default (cleaner initial view)
springdoc.swagger-ui.doc-expansion=none
```

**`doc-expansion` options:**

| Value | Effect |
|-------|--------|
| `none` | All groups collapsed on load — clean, like the MomoDeveloper portal |
| `list` | Groups expanded, individual operations collapsed |
| `full` | Everything expanded (can be overwhelming for large APIs) |

**Excluding an endpoint from the docs** — use `@Hidden` on the class or method:

```java
@Hidden
@GetMapping("/internal-health")
public String health() { return "ok"; }
```

**Grouping into multiple separate docs** (useful for a public + internal split):

```properties
springdoc.group-configs[0].group=public
springdoc.group-configs[0].paths-to-match=/subscription/**, /transaction/**

springdoc.group-configs[1].group=internal
springdoc.group-configs[1].paths-to-match=/debug/**
```

Each group gets its own Swagger UI selector and its own `/v3/api-docs/public`, `/v3/api-docs/internal` URL.

---

## 71. @Schema — documenting individual DTO fields

`@Tag` and `@Operation` describe endpoints. `@Schema` describes individual fields on request/response DTOs.

Without `@Schema`, springdoc infers the field name and type from the Java declaration:

```java
private String debitAccount;
// → shows up in Swagger as: debitAccount (string)
```

With `@Schema`, you can add a description and an example:

```java
@Schema(description = "Mobile money or bank account number to debit",
        example = "0241234001")
private String debitAccount;
```

Swagger UI then shows the description and pre-fills the example value in the Try It body.

**`@Schema` on an enum** gives human-readable labels to each enum constant:

```java
public enum FrequencyType {
    @Schema(description = "Debit every day") DAILY,
    @Schema(description = "Debit every week") WEEKLY,
    @Schema(description = "Debit every month") MONTHLY,
    @Schema(description = "Debit every year") YEARLY
}
```

**`@Schema` on the DTO class itself** adds a top-level description:

```java
@Schema(description = "Request body for creating a recurring subscription")
@Data
public class SubscriptionRequestDto { ... }
```

This project doesn't use `@Schema` yet — the field names are descriptive enough for a sandbox. But in a production API facing external developers, `@Schema` on every field is standard practice.

---


---

## 75. @ApiResponse and @ApiResponses — documenting all possible responses

By default, springdoc only records that an endpoint returns HTTP 200. Every endpoint in this project also returns a business-level `responseCode` field inside the 200 body, and some return 400 (validation failure) or 401 (missing headers). The `@ApiResponse` annotation documents all of these so they appear in both Swagger UI and the custom portal's Responses table.

```java
@ApiResponses({
    @ApiResponse(responseCode = "200", description =
        "Always returned. Check `responseCode` in the body:\n\n" +
        "| Code | Meaning |\n" +
        "|------|---------|\n" +
        "| `03` | Request accepted |\n" +
        "| `100` | Business error — see responseMessage |\n"),
    @ApiResponse(responseCode = "400", description = "Jakarta validation failure"),
    @ApiResponse(responseCode = "401", description = "Missing required headers")
})
```

**Key points:**

- `@ApiResponses` is a container annotation that holds multiple `@ApiResponse` entries — you need it whenever you declare more than one response for an endpoint.
- The `description` field supports Markdown, including tables. Swagger UI renders them; the custom portal calls `marked.parse(r.description)` to do the same.
- The `responseCode` attribute is a **string**, not an integer — OpenAPI status codes are always strings (`"200"`, `"401"`).
- You can have multiple `@ApiResponse` entries for the same HTTP code (e.g. two `"200"` entries with different `content` schemas), but in practice a single 200 entry with a Markdown table of all business codes is cleaner.
- Springdoc merges the `@ApiResponses` you declare with any it infers from the method return type — if you declare at least one `"200"`, it won't auto-generate a second one.

**Why this matters for the custom portal** — the `buildResponsesSection()` function reads `op.responses` from the OpenAPI JSON. Without `@ApiResponse`, that object only has `"200": { description: "" }`. With it, each HTTP code has a rich description and the response table rows are coloured by family (green for 2xx, orange for 4xx, red for 5xx).

---

## 76. @Schema(example) — pre-filling Try It with real values

The `buildExampleFromSchema()` function in `docs.js` walks the OpenAPI schema for a DTO and builds a pre-filled JSON object. By default it uses type-based fallbacks: `""` for strings, `0` for integers, `false` for booleans, and the first enum value for enums. This gives a structurally correct body but every string is blank — not helpful.

Adding `@Schema(example = "...")` to a DTO field embeds the example value directly into the OpenAPI spec, and `buildExampleFromSchema` uses it first:

```java
@Schema(example = "0241234001",
        description = "Last 3 digits control the simulated outcome — 001=success, 002=fail+retry")
private String debitAccount;
```

In the generated OpenAPI JSON this becomes:

```json
"debitAccount": {
  "type": "string",
  "example": "0241234001",
  "description": "Last 3 digits control the simulated outcome..."
}
```

And in `docs.js`:

```js
function buildExampleFromSchema(schema, depth = 0) {
  for (const [name, rawProp] of Object.entries(props)) {
    const p = deref(rawProp);
    if (p.example !== undefined) { out[name] = p.example; continue; }  // ← used here
    // ... type-based fallbacks below
  }
}
```

**Best practices for example values:**

| Field type | What to put in `example` |
|------------|--------------------------|
| ID fields (`merchantId`, `productId`) | Real-looking UUID from your test data |
| Account numbers | An account that exercises the success path (`...001`) |
| Dates | A future date in `yyyy-MM-dd` format |
| Enums | The most common value (e.g. `"MTN"`, `"MONTHLY"`) |
| Runtime IDs (subscriptionId, mandateId) | `"replace-with-..."` — makes it obvious the user must fill it in |
| Optional fallbacks (callbackUrl) | The webhook.site URL from your own testing |

For enum fields, springdoc serialises `@Schema(example = "MTN")` as the string `"MTN"` in the JSON, and `buildExampleFromSchema` assigns it directly — no type coercion needed on the client side.

---

