# direct-debit-sandbox-java — API Documentation & Project Story

From [`../learning/08-openapi-and-swagger-docs.md`](../learning/08-openapi-and-swagger-docs.md),
[`09-custom-docs-portal-ui.md`](../learning/09-custom-docs-portal-ui.md).

Documentation is a strange thing to be interviewed on — until you remember this product's *users
are developers*, which makes the docs part of the product rather than a supplement to it.

---

### Q1. [Beginner] 🔥 What is OpenAPI, and how does springdoc relate to Swagger UI?

**Strong answer covers:** **OpenAPI** is a specification format — a machine-readable JSON/YAML
description of every endpoint, parameter, schema and response. **springdoc** generates that document
by inspecting your controllers, DTOs and annotations at runtime. **Swagger UI** is a browser client
that reads the document and renders an interactive page. Three separate things: a format, a
generator, a renderer.

**Why generation matters:** hand-written API docs drift from the code the day after they're written.
Generated docs are wrong only if the code is wrong.

---

### Q2. [Intermediate] What do "Try it out" requests actually do?

**Strong answer covers:** Swagger UI builds a real HTTP request from the form and sends it from the
browser to your server — it's not a simulation. Consequences worth naming: it's subject to CORS if
the docs are served from a different origin, requests hit the real backend and create real records,
and auth headers must be supplied for the call to succeed, which is what the Authorize button is
for.

---

### Q3. [Intermediate] 🔥 Walk through the annotations you used and what each contributes.

**Strong answer covers:**
- `@Tag` — groups endpoints under a named section on the controller.
- `@Operation` — the summary and description for a single endpoint.
- `@Parameter(hidden = true)` — hides a parameter from the per-endpoint form. Used for the auth
  headers, because they're supplied globally via the security scheme and repeating them on every
  form is noise the integrator has to fill in over and over.
- `@Schema` — documents an individual DTO field, and `@Schema(example = "...")` pre-fills the
  Try-It form with a realistic value.
- `@ApiResponse` / `@ApiResponses` — documents every possible response, not just the happy path.

**The one to emphasise:** `@Schema(example)`. Pre-filled realistic values are the difference between
an integrator successfully calling your API in thirty seconds and giving up — especially here, where
the account-number suffix *is* the scenario selector, so the examples teach the mechanism.

---

### Q4. [Intermediate] What's a security scheme in OpenAPI, and what does the Authorize button do?

**Strong answer covers:** it declares how the API is authenticated (here: custom headers), which
makes Swagger UI render an Authorize button. You enter the credentials once and the UI attaches them
to every subsequent Try-It request. Without it, the alternative is documenting auth headers on every
endpoint and having the integrator paste them into each form individually — which combined with
`@Parameter(hidden = true)` is exactly the cleanup this project did.

---

### Q5. [Intermediate] 🔥 You documented *all* responses, not just 200. Why does that matter more here than in most APIs?

**Strong answer covers:** because this API returns HTTP 200 for everything (see
[02-domain-and-api-design.md](02-domain-and-api-design.md) Q6), the HTTP status carries no
information at all — the entire error contract lives in the body's `responseCode`. So documenting the
possible business codes and what each means *is* the error documentation. An integrator who only
reads the 200 response schema knows nothing about failure handling, and there's no status code to
tip them off.

---

### Q6. [Advanced] 🔥 You built a custom docs portal alongside Swagger UI. Why not just use Swagger UI?

**Strong answer covers:** Swagger UI is a *reference* — excellent at "what are the parameters of this
endpoint", poor at "how do I integrate with this system". A payments sandbox needs narrative: the
provisioning-first flow, what the account-suffix scenarios mean, how callbacks are delivered and what
to do with them, worked end-to-end examples. That's a documentation *site*, not an endpoint list.

**Be honest about the cost:** a hand-built portal is hand-maintained and can drift from the code, in
exactly the way generated docs can't. The mitigation used here is embedding the generated Swagger UI
inside the portal via an iframe — narrative content is authored, reference content stays generated —
plus a fallback for when the iframe can't load. Guided narrative around generated reference is the
right shape, and saying so shows you understand why both exist.

---

### Q7. [Intermediate] How do you serve a static HTML page at a custom route in Spring?

**Strong answer covers:** `WebMvcConfigurer.addViewControllers` maps a path to a view/resource with
no controller class at all — the right tool when there's no logic, just a page. The related gotcha
already covered elsewhere: that path must be excluded from the auth interceptor, and the exclusion
needs both the bare path and the `/**` subtree pattern or the page loads and its assets don't.

---

### Q8. [Intermediate] You wrote JSON and curl syntax highlighting in vanilla JS. Why not a library?

**Strong answer covers:** the scope is small and well-bounded — tokenise JSON into keys, strings,
numbers, literals and punctuation, wrap each in a span, style with CSS. Pulling in a full
highlighting library for two languages on a docs page costs bundle size and a dependency for
something that's a few dozen lines. The honest counterweight: hand-rolled highlighting is
regex-based and will mis-highlight edge cases (an escaped quote inside a string is the classic), and
that's acceptable for display purposes in a way it would never be for parsing.

---

### Q9. [Beginner] The retractable sidebar toggles a CSS Grid column to zero. Explain.

**Strong answer covers:** the layout is `grid-template-columns: 280px 1fr`, and collapsing sets the
first track to `0`. Because it's a grid track rather than a positioned overlay, the content column
reflows automatically and a CSS transition on the track width animates it — no JavaScript layout
maths, no absolute positioning, and no fighting with the content's width. It's a good demonstration
of choosing a layout primitive that makes the interaction fall out for free.

---

### Q10. [Advanced] Why does documentation belong in an interview answer about a backend project at all?

**Strong answer covers:** because for a sandbox, the docs are the product. Nobody uses this system to
move money — they use it to *learn how to integrate*, so time-to-first-successful-call is the
metric that matters. That reframes decisions elsewhere in the project too: the `@Schema(example)`
values, the scenario-by-account-suffix design (discoverable from an example, no extra request field
to explain), and the uniform 200-plus-`responseCode` convention are all integrator-experience
decisions. Being able to name a *product* metric behind engineering choices is unusual and it lands.

---

### Q11. [Intermediate] What was the hardest bug in this project?

**Strong answer covers — pick one and tell it properly:**
- **The interceptor path exclusions** — a docs page that loaded while its assets were rejected, which
  presents as a broken page rather than as an auth problem. The lesson: path patterns don't behave
  intuitively at the path/subtree boundary.
- **The Spring Security dependency** — added for later, immediately activated by auto-configuration,
  and suddenly every endpoint 401s with no code change anywhere. The lesson: in Spring Boot, adding a
  starter changes behaviour, not just the classpath.

Both are good because the symptom pointed somewhere other than the cause.

---

### Q12. [Advanced] 🔥 What would you change if this had to become a real product?

**Strong answer covers, in priority order:**
1. **Persistence** — an in-memory store means one instance, no durability, and a scheduler that
   would double-process under replication (see
   [03-storage-async-and-retries.md](03-storage-async-and-retries.md) Q14).
2. **Callback delivery guarantees** — real webhook delivery is at-least-once with retries and
   signing. The current exactly-once-in-practice delivery teaches integrators to write handlers that
   would break in production, which is arguably worse than not simulating callbacks at all.
3. **Replay protection and rotating secrets** on inbound auth.
4. **Observability** — every callback attempt and retry as a queryable record, not just a log line,
   because "did the callback fire and what did they return?" is the number one integrator support
   question.

Leading with persistence is fine, but leading with **callback delivery semantics** is better: it's
the item where the sandbox is actively teaching the wrong lesson, and spotting that shows product
thinking rather than a checklist.
