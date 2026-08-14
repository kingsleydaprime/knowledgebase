# What a Backend Actually Is

**[Beginner]** — the orientation note. Short, but it sets up the vocabulary the rest of the course uses.

## The kid version first

A restaurant has a **dining room** and a **kitchen**.

The dining room is what customers see and touch — the menus, the tables, the plates. The kitchen is where the food actually gets made, where the ingredients are stored, and where the rules live ("we're out of fish", "you can't order breakfast at 9pm").

You could redecorate the dining room completely and the kitchen wouldn't change. You could replace the kitchen equipment and diners wouldn't notice. That separation is the whole idea.

**The backend is the kitchen.** And the important consequence: *the kitchen is the one that can't lie.* A diner can ask for anything; the kitchen decides what's actually true and what actually happens.

## What a backend is responsible for

Strip away frameworks and it's four things:

1. **Persist state** — remember things after the request ends and the process restarts. → [[backend/04-data-and-persistence/README|data & persistence]]
2. **Enforce rules** — the invariants that must hold no matter who asks or how. *You can't withdraw more than your balance. You can't book a taken seat.*
3. **Decide who may do what** — authentication and authorization. → [[backend/05-auth/README|auth]]
4. **Integrate** — talk to other systems (payment providers, email, other services) and to other clients.

Everything else — routing, serialisation, middleware, ORMs — is machinery in service of those four.

## The rule that everything else follows from

> **Never trust the client.**

Not because users are malicious (mostly they aren't) but because **you do not control the client**. A browser can be modified, a mobile app decompiled, and your API called directly with `curl`. Any check that exists only on the frontend does not exist.

This single rule generates most of the backend's design:

- Validate **on the server**, always — client validation is UX, not security. → [[backend/01-foundations/03-the-request-lifecycle|the request lifecycle]]
- Authorise on the server, at the **data** layer — hiding a button isn't a permission check.
- Prices, totals, and permissions are computed server-side; never accept an amount the client calculated.
- Sensitive logic and secrets live server-side, because anything shipped to a client is public.

## Where the boundary sits

The frontend/backend line has moved a lot, and the vocabulary reflects that:

- **Server-rendered** — the server sends HTML. The original model, and back in fashion (Next.js server components, Rails/Hotwire, HTMX).
- **API + SPA** — the server sends JSON, the client renders. → [[backend/02-api-design/README|API design]]
- **BFF (backend-for-frontend)** — a thin server per client type, shaping data for that client, in front of shared services.
- **Serverless** — the same responsibilities, but the runtime is managed and scales per request. Changes the *operations*, not the *concerns* — though it makes connection pooling genuinely harder.

**The four responsibilities don't move.** Whichever shape you pick, something still has to hold state, enforce rules, decide permission, and integrate. That's why this course is framework-agnostic and why [[backend/frameworks/README|frameworks/]] is a subfolder rather than the main event.

## What makes backend work hard

Not the syntax. The three things that actually generate difficulty:

- **Concurrency** — many requests at once, touching the same data. Two users buying the last item is a *correctness* problem, not a performance one. → [[backend/04-data-and-persistence/README|transactions and isolation]]
- **Failure** — networks time out, databases fail over, your process dies mid-operation. A request that "failed" may have succeeded. → [[backend/interview/01-production-debugging|retry safety]]
- **Change over time** — the schema, the API, and the code all have to evolve while running, without downtime and without breaking existing clients.

A backend that works for one user on a laptop is easy. All the difficulty comes from *many*, *unreliable*, and *over time*.

## Key insight

The backend is **the boundary where claims become facts.** The client can request anything; the backend decides what is true, records it durably, and makes sure it stays consistent when a thousand people ask at once and a third of the infrastructure is on fire. Every practice in this course — validation at the boundary, transactions, idempotency, authorization at the data layer — exists to defend that single job.

## Related
- [[backend/01-foundations/02-http-servers|HTTP Servers]] — how requests physically arrive
- [[backend/01-foundations/03-the-request-lifecycle|The Request Lifecycle]] — what happens to one
- [[backend/01-foundations/04-runtime-and-concurrency-models|Runtime & Concurrency Models]] — how many happen at once
- [[foundations/networking/README|Networking]] — the layer underneath all of it
