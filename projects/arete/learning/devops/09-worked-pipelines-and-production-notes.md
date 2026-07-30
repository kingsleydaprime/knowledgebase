# Arete DevOps — Worked Pipelines & Production Notes

Split out from the original single-file `devops-learning.md`. Full worked shell pipelines from
real sessions, plus Arete-specific production/release notes and the devops study path.

---

## Part 9 — Full Worked Pipelines (from this session)

```bash
# 1. Start stack → wait → verify health, as one guarded chain:
systemctl --user start podman.socket && \
podman compose -f docker-compose.dev.yml up -d && \
sleep 8 && podman ps --format '{{.Names}} {{.Status}}'
# `&&` gates each step on the previous one succeeding.

# 2. Apply migrations, show only the outcome (stderr merged so failures are visible):
bunx prisma migrate deploy 2>&1 | tail -6

# 3. Write a throwaway TS script via heredoc, run it, remove it — leave no trace:
cat > verify.tmp.ts << 'EOF'
...script...
EOF
bun verify.tmp.ts; rm verify.tmp.ts
# `;` not `&&` before rm: clean up even if the script failed.

# 4. Count call sites of a pattern to gauge blast radius before refactoring:
grep -rn "cache.del" backend/src --include="*.ts" | wc -l

# 5. Locate → preview → cut (the safe file-surgery ritual):
grep -n "Seed complete\|^}" prisma/seed.ts     # find boundaries
sed -n '335,388p' prisma/seed.ts               # preview exactly what will die
sed -i '335,388d' prisma/seed.ts               # cut

# 6. Prove a rate limit actually fires (never assume security config works):
for i in $(seq 1 7); do
  code=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:3000/v1/auth/login \
    -H "Content-Type: application/json" -d '{"email":"x@x.com","password":"wrong"}')
  echo "attempt $i: HTTP $code"
done
# curl flags: -s silent · -o /dev/null discard body · -w "%{http_code}" print ONLY the status.
# Expected: 401 ×5 then 429 ×2. If you never see 429, the limiter is configured but not enforced
# (in NestJS: ThrottlerModule without an APP_GUARD binding — a real bug caught this way).
```

---

## Part 10 — Production Notes (Arete specifics) & Study Path

### Release checklist for the current setup (Render + managed Postgres)

```bash
# The Docker image now runs `migrate deploy && db seed` on every boot, so a
# normal deploy is self-contained. The manual commands remain useful for
# out-of-band runs (e.g. seeding before a deploy, or a non-Docker environment):
DATABASE_URL="<render-url>" bunx prisma migrate deploy
DATABASE_URL="<render-url>" bunx prisma db seed
# Mobile: EAS build only if native config changed; OTA update otherwise.
```

Notes to remember:
- All crons are **UTC**; Lagos is UTC+1 (that's why quest-reminder is `0 6 * * *` = 7 AM WAT).
- `docker-compose.prod.yml` and `Dockerfile` exist in backend/ — the prod image builds the Nest app; env comes from Render's dashboard, not a .env file.
- Podman socket must be enabled after reboots unless you ran `systemctl --user enable --now podman.socket`.

### Study path

1. **Week 1:** Pipes, redirection, `grep -rn`, `head/tail/wc`. Do all code exploration in the terminal for a week.
2. **Week 2:** `find` with `-name/-type/-o/-prune/-exec`; write five real queries against this repo.
3. **Weeks 3–4:** Regex — do the worked examples, then [regex101.com](https://regex101.com) with real log lines. Learn BRE vs ERE once, properly.
4. **Month 2:** Containers — rebuild the compose file from memory; break it (wrong port, missing volume) and diagnose via `logs`/`inspect`. Learn volumes by destroying one on purpose (in dev!).
5. **Month 3:** Write a Dockerfile for a Nest app from scratch (multi-stage: build → slim runtime). Understand every line of the existing one.
6. **Advanced:** CI pipelines (GitHub Actions running migrate deploy + tests), monitoring (uptime checks, log aggregation), backup/restore drills for Postgres (`pg_dump`/`pg_restore` — practice the restore, not just the dump).
