# 11 — Multi-tenancy & White-label Planning

*Written 2026-11-02, from reviewing a planning-only prompt for making NextVibe white-label.
Nothing is built yet. This is the thinking.*

See also: [[projects/nextvibe/learning/00-sys-design|00 — System Design]],
interview: [[projects/nextvibe/interview/06-wishlist-spin-wheel-and-multitenancy|06, Q11 + S4]]

---

## The goal

Other businesses run NextVibe under their own brand (domain, logo, colours, emails) on **one
codebase and one deployment**. NextVibe itself becomes tenant #1.

## The decisions, in the order they matter

1. **Isolation model**

   | Model | Cost | Isolation |
   |---|---|---|
   | Shared schema + `tenantId` column | Cheapest, one migration path | Only as good as your filtering |
   | Schema per tenant | Medium, migrations run N times | Stronger |
   | Database per tenant | Most expensive | Strongest, easy per-tenant backup/restore |

   Shared-schema is the usual start, and the rest of this note assumes it.

2. **Enforce isolation centrally, not by memory.**
   - **App layer:** a Prisma client extension adds `where tenantId = current` to every query and
     stamps it on every write. Weakness: `$queryRaw` / `$executeRaw` skip extensions completely.
   - **Database layer:** Postgres **Row-Level Security**. Policies check
     `current_setting('app.tenant_id')`. Weakness: the setting has to be applied per transaction
     (`set_config(…, true)`), and connection pooling makes "per request" harder.
   - Best answer: **both**. RLS is the backstop for the queries the extension misses.

3. **Tenant context.** Carry it with AsyncLocalStorage (`nestjs-cls`) rather than request-scoped
   providers, so it reaches services, queue jobs, cron jobs and websocket handlers without the
   performance cost.

4. **Resolving the tenant:** custom domain (Host header), then subdomain, then an explicit header
   for mobile.
   - The header must be **checked against the tenant in the JWT**, or a user of tenant A could
     send tenant B's id.
   - **Inbound callbacks have no tenant Host:** payment webhooks, OAuth callbacks, email links.
     With per-tenant payment keys, you need the tenant *before* you can check the webhook
     signature, so it must come from the payload or a per-tenant webhook URL.

5. **Identity is a product decision:** per-tenant users (simpler, safer) or one global identity
   with tenant memberships (one person, many branded apps).

6. **Everything outside the database needs the tenant too:** cache keys, queue jobs, file storage
   paths, websocket rooms, logs.

7. **Migration:** create tenant #1, then add a nullable `tenantId`, then backfill, then NOT NULL +
   indexes, then make unique constraints per-tenant (`@@unique([tenantId, email])`). Each step
   needs a way to roll back.

## Requirements that are easy to forget

- Offboarding: export and delete one tenant's data.
- Restoring one tenant from backup without touching the others.
- Per-tenant rate limits, so one noisy tenant can't slow down everyone.
- Data-protection law in the tenant's country (for Nigerian clients, NDPR/NDPA).
- Existing money flows (affiliates, organizer billing, payouts) colliding with per-tenant payment
  credentials and a platform fee.

## What the prompt review taught about writing prompts for agents

- **Too big for one pass:** split it into *discovery*, then *plan*, with your answers in between.
  "Ask me before assuming" can't work inside "give me one report", so tell the agent to mark
  assumptions and keep going.
- **Don't prescribe the solution before discovery.** "Don't assume the stack" plus "use an ORM
  subscriber" contradicts itself, and steers the agent past the RLS question.
- **Put YAGNI first:** custom-domain SSL, mobile build pipelines and revenue share can wait for the
  first real client.
- **Fix existing security debt as phase 0**, before building isolation on top of it.

## Open questions (product owner's to answer)

1. Is there a first client lined up, or is this preparation?
2. Can one person have accounts on several tenants' apps?
