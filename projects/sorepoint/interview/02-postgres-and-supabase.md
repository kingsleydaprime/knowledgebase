# Sorepoint — Postgres, Supabase & the Local Stack

From [`../learning/supabase.md`](../learning/supabase.md) and
[`../learning/shell.md`](../learning/shell.md).

---

### Q1. [Advanced] 🔥🔥 Your service-role client got `42501 permission denied for table scans`. But service_role bypasses RLS. Explain.

**This is the single best question in the project. Know it cold.**

**Strong answer covers:** RLS wasn't the gate — **table GRANTs** were. They're two independent
gates:
- **GRANT** decides whether a role may touch a table *at all* (SELECT/INSERT/UPDATE/DELETE).
- **RLS** decides which *rows* are visible once the role can touch the table.

`service_role` bypasses RLS but still needs the GRANT.

**Why the GRANT was missing:** migrations run as the **`postgres`** role, and `postgres`'s *default
privileges* in schema `public` grant the API roles only partial rights (DELETE/TRUNCATE/REFERENCES/
TRIGGER — notably **no** SELECT/INSERT/UPDATE). Supabase's *full* default grants are attached to
the `supabase_admin` role, so objects created by `postgres` — i.e. everything in your migrations —
don't inherit them. Confirmed by inspecting `pg_default_acl`.

**The fix, and why it's a separate migration:**
```sql
grant select, insert, update, delete on all tables in schema public to service_role;
alter default privileges in schema public
  grant select, insert, update, delete on tables to service_role;   -- future tables too
```
Separate because the schema migration was already committed and **migrations are append-only** —
you add a new one rather than editing history that other environments have already applied.

**Three takeaways to state:** (1) `permission denied` on Supabase is usually a GRANT problem, not an
RLS one — read the error's `hint`, it literally tells you. (2) Never edit a committed migration.
(3) `alter default privileges` fixes the *next* tables too, so you don't rediscover this every time
you add one.

---

### Q2. [Intermediate] What's the difference between a GRANT and an RLS policy, in one sentence each, for someone who's only used an ORM?

**Strong answer covers:** a GRANT is *may this role use this table at all*; an RLS policy is *which
rows of that table this role may see or change*. An ORM typically connects as a single superuser-ish
role, so neither is visible — which is exactly why the first move to a role-per-audience model
surprises people.

---

### Q3. [Intermediate] 🔥 Why run Supabase locally at all, and why was Podman the interesting part?

**Strong answer covers:** the local stack gives real Postgres + the API layer, so migrations, RLS,
GRANTs and TypeGen are all exercised before anything touches a hosted project — the GRANT bug
above is precisely the kind of thing that's cheap to find locally and expensive to find in
production. The container runtime is the friction: the Supabase CLI needs a runtime it can reach,
and **rootless Podman** on Fedora is not a drop-in Docker replacement.

**The Fedora-specific detail:** `supabase start` failures there come down to SELinux versus
rootless Podman — volume mounts get denied by policy rather than by permissions, so the error looks
like a container problem and is actually a labelling one. Being able to say "the symptom pointed at
the container runtime, the cause was SELinux context on the mount" is the answer.

---

### Q4. [Beginner] Why install the Supabase CLI as a dev dependency instead of globally?

**Strong answer covers:** the CLI version is part of the project's reproducible toolchain — it
determines migration behaviour and the local stack's images. A global install drifts per machine
and per contributor, and CI has no global install at all. Same reasoning as pinning any other build
tool.

---

### Q5. [Intermediate] Why let the CLI name your migration files?

**Strong answer covers:** migrations are applied in filename order, so the timestamp prefix *is* the
ordering mechanism. Hand-naming invites two developers to produce files that sort wrongly relative
to when they were written, which surfaces as a migration that runs before the table it alters
exists. Letting the tool generate the timestamp removes a whole class of merge-order bug.

---

### Q6. [Intermediate] 🔥 What is TypeGen and why does it matter more than it sounds?

**Strong answer covers:** it generates TypeScript types directly from the live database schema, so
the client is typed by the *actual* schema rather than by a hand-written interface someone updates
from memory. The failure it prevents is silent: a column renamed in a migration breaks compilation
everywhere it's referenced, instead of returning `undefined` at runtime in one code path nobody
tested. The workflow rule that comes with it — regenerate after every migration, and treat a
generated-types diff as part of the same commit.

---

### Q7. [Intermediate] Explain the idempotent upsert in Stage 1 at the SQL level.

**Strong answer covers:** there's a `unique (scan_id, place_id)` constraint, and the write is
`upsert(rows, { onConflict: 'scan_id,place_id' })` — Postgres `INSERT ... ON CONFLICT` under the
hood. The uniqueness is scoped to `(scan_id, place_id)`, not `place_id` alone, because the same
business legitimately appears in multiple scans; it's the same business *within one scan* that must
not duplicate. Verified empirically: a `--force` re-fetch of 123 rows left the total at 123.

**Follow-up:** *"What if the source's `place_id` changes?"* — then you get a duplicate row, and no
constraint can save you; that's an argument for the semantic normalisation done at the adapter
boundary rather than trusting source IDs to be stable.

---

### Q8. [Advanced] Where do RLS policies matter in this product, given the worker bypasses them?

**Strong answer covers:** the worker uses the service-role key and bypasses RLS by design — it's
trusted server-side code with no user context. RLS matters for the **dashboard**, where a real user
session must only see their own tenant's scans and businesses. That's the actual multi-tenancy
boundary, and `tenant_id` on every row is what the policies key off. The important discipline: the
service-role key must never reach the browser, because it defeats every policy simultaneously.

---

### Q9. [Intermediate] How do you verify a migration did what you intended rather than assuming it did?

**Strong answer covers:** query the resulting state, don't trust the "applied" message — check the
columns/constraints exist (`\d table` or an information_schema query), and for a grant/policy
migration, actually attempt the operation as the target role. The GRANT bug is the case in point:
the migration applied cleanly and the permission was still missing, because "the migration ran" and
"the intended privilege exists" are different claims.

---

### Q10. [Beginner] How did you scaffold into a non-empty repo, and why does that come up?

**Strong answer covers:** `create-next-app` refuses a non-empty directory, so the existing files
(docs, notes, git metadata) get moved aside with `mv`, the scaffold runs, then they're moved back.
Trivial mechanically, but worth knowing because the alternative people reach for — scaffolding
elsewhere and copying in — loses the git history that motivated having the repo first.
