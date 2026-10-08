# MyPaddie — Learning

MyPaddie is a private life-coaching system: a rules engine (XP, modes, money
stages) on Supabase Postgres with RLS, an MCP connector, and a Next.js PWA.
Blueprint: `~/code/personal/mypaddie/docs/BLUEPRINT.md`. Decisions:
`~/code/personal/mypaddie/DECISIONS.md`.

Read in order:

1. [[01-supabase-schema-and-rls]] — owning rows, composite FKs, deferred constraint triggers, ledgers, the 2026 grants change
2. [[02-rules-engine-design]] — pure functions, injecting `now`, largest remainder, the rolling-window bug
3. [[03-testing]] — `bun test`, testing time, table tests, pgTAP for RLS
4. [[04-shell]] — slow networks, `--prefer-offline`, `timeout` exit codes, zsh vs bash `PIPESTATUS`; re-creating SQL functions with `awk` + `sed` + `diff <(…)`, proving a test can fail
5. [[05-mcp-server]] — the remote MCP server: auth, per-user context, `ok`/`toolError`, and tool-design lessons from real bugs
6. [[06-scheduling-and-push]] — `pg_cron` every minute, the database decides and the app delivers, unique indexes as memory, holds
7. [[07-time]] — local days, the 23:59 "any time" sentinel, quiet hours as the day's end, "later", Sunday vs Monday weeks
8. [[08-data-modelling-choices]] — `started_at` over a new status, derive vs store, jsonb vs table, defaulted flags, two limits
9. [[09-nextjs-app]] — feature folders, server components read, server actions write, small client islands

See also (general vault): [[ai-ml/03-ai-engineer/07-tools-and-mcp/index|tools and MCP]] · [[devops/01-linux/16-sed-and-awk|sed and awk]] · [[databases/sql-reference]] · [[backend/05-auth/02-authorization]] ·
[[projects/gees-arise/learning/09-sys-design|gees-arise]] (the previous Supabase + RLS project) ·
[[devops/01-linux/index|linux]]
