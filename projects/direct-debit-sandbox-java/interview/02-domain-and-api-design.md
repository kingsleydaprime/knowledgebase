# direct-debit-sandbox-java — Domain & API Design

From [`../learning/06-business-domain-flow.md`](../learning/06-business-domain-flow.md). The most
interesting file in the project — these are API-design decisions, not framework mechanics.

---

### Q1. [Intermediate] 🔥🔥 Explain the scenario engine. How does a tester trigger a failure with no real bank?

**Strong answer covers:** the **last three digits of the debit account number determine the
outcome**. `...001` always succeeds (`responseCode 01`), `...101` always returns insufficient funds,
`...131` always times out. A tester picks the account number and gets a deterministic, repeatable
result.

**Why this is good design:** the alternative — a flag in the request body saying "please fail this
one" — pollutes the API contract with something that must not exist in production, so integrators
end up testing against a *different* request shape than they'll ship. Encoding the scenario in data
that's already part of the real payload means the sandbox request is byte-identical to a production
request. That's the point worth landing.

**Follow-up they'll ask:** *"What are the downsides?"* — real account numbers can accidentally end
in a magic suffix; the mapping has to be documented or it's undiscoverable; and it only covers
outcomes expressible per-account, so scenarios about timing or sequence need another mechanism (this
project uses suffixes `002`/`003` to simulate *transient* failures that later succeed, which is how
retries get exercised).

---

### Q2. [Intermediate] 🔥 Explain the provision pattern and the problem it solves.

**Strong answer covers:** originally every subscribe request had to carry a `callbackUrl`. With a
thousand subscribers that's the same URL repeated a thousand times — redundant, and a
consistency hazard when one request carries a stale value. With provisioning, the merchant calls
`POST /provision` **once** for a `merchantId + productId` pair, and every subsequent callback
resolves the URL by lookup.

The provision also holds catalogue configuration: `retryAttempts`, `skipFactor`,
`daysToDebitDayNotice` — set once at merchant level rather than repeated per transaction.

**The generalisable rule:** when a piece of config belongs to the *relationship* (URL, API key,
webhook secret, retry policy) rather than to the *transaction*, register it once at onboarding and
let every operation inherit it. Same idea as a webhook endpoint configured in a dashboard rather
than passed on each API call.

---

### Q3. [Advanced] 🔥 `resolveEffectiveConfig` merges request config with provision defaults. Why allow both?

**Strong answer covers:** the provision gives sensible defaults for the merchant; the request needs
an escape hatch for the transaction that legitimately differs. So the resolution is layered —
request value if present, else provision value, else system default — which is exactly the precedence
model of environment variables over config files over defaults.

**The design tension to name:** every value you allow to be overridden per request is a value that
can drift, and a value that must be validated in two places. The right answer isn't "allow
everything" or "allow nothing" — it's that overridable-per-request should be a deliberate, short
list, and the resolution order must be one function, not scattered null checks.

---

### Q4. [Intermediate] 🔥 Subscription trigger-debit versus mandate trigger-debit — what's the difference?

**Strong answer covers:** a **subscription** is a recurring arrangement — it carries a frequency, a
debit day, a start and end date, and the schedule is what drives debits. A **mandate** is standing
authorisation to debit an account; a debit against it is initiated on demand rather than by
schedule. So subscription trigger-debit fires the next scheduled instalment for an existing
recurring arrangement, while mandate trigger-debit fires an ad-hoc debit against an authorisation.
Same underlying account and callback mechanics, different lifecycle and different validation.

---

### Q5. [Intermediate] How does preauthorization fit in, and why does the same callback payload serve both preauths and subscriptions?

**Strong answer covers:** a preauthorization reserves the customer's agreement ahead of the actual
debit. It shares the callback shape with subscriptions because the callback answers the *same*
question in both cases — "did this attempt against this reference succeed, and with what code?" —
so the payload keys off the transaction reference, not the product that created it.

**The design lesson:** shared payloads are correct when the *event* is genuinely the same, and a
mistake when they merely look similar. Here the event is "an attempt resolved", which is
product-agnostic. Say that explicitly, because "we reused the DTO" is otherwise indistinguishable
from laziness.

---

### Q6. [Advanced] 🔥🔥 You migrated errors from HTTP 4xx to HTTP 200 with a business `responseCode`. Defend that — it looks like an anti-pattern.

**Strong answer covers:** it *is* against REST convention, and it's the near-universal convention in
banking and fintech APIs. The reason: clients otherwise have **two** error paths — HTTP status
handling and body-code handling — and every integrator has to get both right, in every language,
through every proxy and gateway in between. Collapsing to one path (always 200, always read
`responseCode`) makes the client's error handling uniform, and it's robust to middleboxes that treat
non-2xx responses differently.

**What you give up, and should say so:** HTTP caching and retry semantics stop being meaningful,
generic monitoring that alarms on 5xx/4xx rates goes blind, and anything that inspects status codes
without parsing bodies (load balancers, API gateways, log dashboards) sees a healthy API while it's
failing every request. That's a real operational cost, accepted deliberately because integrator
consistency was the priority.

**The strongest version of this answer** names both the convention it follows and the cost it pays.
Don't defend it as universally correct; defend it as correct for a payments API whose consumers are
integrating banks and merchants.

---

### Q7. [Intermediate] Walk me through a subscription request end to end.

**Strong answer covers, in order:** request arrives → interceptor validates auth headers (fails fast
with `107` and 200 if missing) → controller binds and `@Valid`-ates the DTO → service validates
business rules (channel is a legal enum value, product type is permitted for this endpoint, dates
are coherent, `debitDay` is valid for the frequency) → record is created in the store with a
generated ID and indexed by reference → the scenario engine derives the outcome from the account
suffix → an **async** callback is fired to the URL resolved from the provision → the caller has
already received its synchronous acknowledgement with the reference.

**The key structural point:** the synchronous response and the asynchronous callback are two
different messages answering two different questions — "did you accept my request?" and "what
happened to it?" Conflating them is what forces clients to hold connections open.

---

### Q8. [Intermediate] 🔥 `debitDay` validation depends on `frequencyType`. Why is that class of validation harder?

**Strong answer covers:** it's a **cross-field** rule — `debitDay = 15` is valid for MONTHLY and
meaningless for DAILY; `debitDay = 31` is valid in some months only. Bean Validation annotations are
per-field, so cross-field rules can't live on the field; they need either a class-level custom
constraint or explicit service-layer validation. This project puts them in the service, which is
defensible: the rule is business logic, and business logic belongs in the service rather than in an
annotation nobody reads.

**Related rule from the notes:** DAILY carries its own constraints — some fields become meaningless
or forbidden. Frequency isn't just a label; it changes which other fields are legal, which is the
definition of a cross-field constraint.

---

### Q9. [Intermediate] What does start/end date validation actually need to check?

**Strong answer covers:** more than "end after start" — a start date in the past (accept? reject?
back-date?), an end date so close to the start that no debit can occur given the frequency, and the
interaction with `daysToDebitDayNotice`, which requires a minimum lead time before the first debit.
Each of those is a real integrator support ticket if left unchecked. The general point: date
validation in a scheduling domain is about **whether a valid schedule exists**, not about ordering.

---

### Q10. [Advanced] 🔥 "Types belong to products, not merchants" — explain `ProductType` vs `MerchantType`.

**Strong answer covers:** a merchant may sell several products of different kinds, so putting the
type on the merchant forces a merchant to be exactly one thing and makes a second product line a
data-model change. Putting it on the **product** means a merchant is just an owner of products, and
the capability question ("may this be preauthorized?") is answered by the product being operated on,
not by who owns it.

**How it's enforced:** product-type checks on the preauth endpoints — a request to preauthorize a
product whose type doesn't support it is rejected with a business code. That's authorisation by
*capability of the thing*, not by *role of the caller*, which is the more robust model when the same
merchant does several kinds of business.

---

### Q11. [Intermediate] How is a request authenticated, and what would you change for production?

**Strong answer covers:** header-based credentials checked in the interceptor against provisioned
merchant data, uniformly across every endpoint, failing with business code `107`. For production the
honest list: credentials as opaque tokens rather than raw identifiers, per-merchant secrets with
rotation, request signing (HMAC over body + timestamp) so a captured request can't be replayed,
TLS-only, and rate limiting per merchant. Naming **replay protection** specifically is the answer
that shows you're thinking about a payments API rather than a generic one.

---

### Q12. [Advanced] What makes this a *sandbox* rather than a mock server, and where does the simulation break down?

**Strong answer covers:** it implements the real contract, real validation, real state transitions
and real asynchronous callbacks — an integrator's code is exercised properly and will run unchanged
against production. A mock returns canned responses and validates nothing, so it proves only that
you can deserialise JSON.

**Where it breaks down, and you should volunteer this:** no real settlement timing (a real debit
resolves in hours or days, not milliseconds), no partial failures or reversals, no bank downtime, no
duplicate-callback delivery — and *that last one matters*, because real webhook infrastructure
delivers at-least-once. A sandbox that always delivers exactly once trains integrators to write
non-idempotent handlers. That's the single most useful thing you could add to it.
