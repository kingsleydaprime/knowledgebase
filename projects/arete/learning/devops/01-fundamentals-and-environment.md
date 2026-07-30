# Arete DevOps — Fundamentals & Environment

Split out from the original single-file `devops-learning.md` (containers, database operations,
and a deep dive into find/grep/sed/regex). See also `02-containers-docker-podman.md`,
`03-database-operations-prisma.md`, `04-shell-pipes-and-text-toolkit.md`, `05-grep-in-depth.md`,
`06-find-in-depth.md`, `07-regex-from-zero-to-advanced.md`, `08-sed-and-awk.md`, and
`09-worked-pipelines-and-production-notes.md`.

---

# DevOps & Shell Mastery — Beginner to Advanced
### Containers (Docker & Podman), database operations, and a deep dive into find / grep / sed / regex — with the exact commands used on Arete

---

---

## Part 1 — Absolute Beginner

### What "DevOps" means for a solo founder

You are the ops team. Concretely that means owning:
1. **Environments** — your laptop (dev), and Render (prod). Same code, different config.
2. **Configuration** — secrets and URLs live in environment variables, never in code.
3. **Infrastructure** — Postgres and Redis running somewhere (containers locally, managed services in prod).
4. **Releases** — migrations, seeds, builds, in the right order, repeatably.

### Environment variables and .env files

```bash
# backend/.env  (dev — never commit real secrets)
DATABASE_URL=postgresql://arete:arete_dev_secret@localhost:5432/arete_dev
REDIS_URL=redis://localhost:6379
JWT_SECRET=dev_jwt_secret_change_in_production
```

The URL format to memorize: `protocol://user:password@host:port/database`.

Rules:
- `.env` is per-machine; `.env.prod.example` documents what prod needs without containing values.
- The same code reads `process.env.DATABASE_URL` everywhere — *config varies, code doesn't*. This is the single most important deployment principle (see "12-factor app").

---

