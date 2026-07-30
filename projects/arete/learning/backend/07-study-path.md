# Arete Backend — Study Path

Split out from the original single-file `backend-learning.md`. A suggested week-by-week learning
order across all the backend files in this folder.

---

## Part 9 — Study Path

1. **Weeks 1–2:** HTTP + REST + JSON. Build a 3-route Express/Nest toy API. Learn status codes by breaking things.
2. **Weeks 3–4:** Prisma + Postgres. Model User/Task/DailyQuest yourself; write the migration; break a unique constraint on purpose and read the error.
3. **Month 2:** Auth end-to-end (bcrypt, JWT, refresh flow). Then transactions and the guarded-decrement pattern until they're reflex.
4. **Month 3:** Redis caching + invalidation discipline; BullMQ cron jobs; the ledger pattern.
5. **Advanced:** idempotency everywhere, race conditions (write a test that fires 10 parallel purchases), N+1 hunting, observability (structured logs, request IDs), and reading production incident write-ups.
