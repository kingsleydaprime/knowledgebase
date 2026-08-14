# Projects — Learning Logs

**42% of this vault by word count lives here**, and until now it was almost entirely disconnected from the courses. This README is the join.

Each folder is a real project with two things in it:
- `learning/` — domain-split notes teaching what that project taught, in the context of its actual code and actual bugs
- `interview/` — the same material as questions with model answers (the pattern that [[INTERVIEW|the domain interview banks]] were generalised from)

**The overlap with the general folders is deliberate, not duplication.** A project note teaches a domain *as it showed up here*, with the real problem attached. The general folder ([[git/git-reference|git]], [[devops/01-linux/README|linux]], [[concepts/README|concepts]]) is the standalone reference for the same material. Both should exist, and they should point at each other — which is what this file is for.

---

## The map — what each project exercises

| Project | What it is | Domains it exercises |
|---|---|---|
| **[[projects/nextvibe/learning/00-sys-design\|nextvibe]]** (142k words — the biggest) | NestJS platform: auth, realtime, games/AI, payments ledger | [[backend/README\|backend]] · [[backend/05-auth/01-authentication-flows\|auth]] · [[architecture/02-building-blocks/04-messaging-and-async\|realtime/async]] · [[databases/database-design-reference\|data modelling]] · [[foundations/networking/11-http-evolution\|websockets/HTTP]] |
| **[[projects/socioboom/learning/archive/original-flat-backend-learning\|socioboom]]** (67k) | Social publishing + AI agents + queues | [[architecture/02-building-blocks/04-messaging-and-async\|queues]] · [[ai-ml/03-ai-engineer/08-agents\|agents]] · [[devops/README\|deployment]] |
| **[[projects/gees-arise/learning/09-sys-design\|gees-arise]]** (32k) | Next.js + Supabase, Postgres RLS | [[databases/sql-reference\|SQL]] · [[backend/05-auth/02-authorization\|authorization]] · [[cybersecurity/04-web-security/README\|web security]] · [[git/git-reference\|git]] · [[devops/01-linux/README\|shell]] |
| **[[projects/record-id-generator-java/learning/01-java-fundamentals\|record-id-generator-java]]** (31k) | High-throughput ID generation, RabbitMQ, MySQL | [[languages/01-java/README\|Java]] · [[languages/01-java/02-jvm-and-concurrency/README\|concurrency]] · [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq\|messaging]] · [[databases/mysql-reference\|MySQL]] · [[architecture/README\|throughput/perf]] |
| **[[projects/direct-debit-sandbox-java/learning/01-java-fundamentals\|direct-debit-sandbox-java]]** (27k) | Spring Boot payments sandbox, async + retries | [[languages/01-java/05-web-and-api/01-spring-boot\|Spring Boot]] · [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency\|idempotency]] · [[architecture/03-architectural-patterns/02-resilience-patterns\|retries/resilience]] |
| **[[projects/iot-bridge-pcb/kicad-walkthrough\|iot-bridge-pcb]]** (25k) | Hardware — schematic, power, RF, KiCad | [[hardware/README\|hardware]] · [[hardware/10-kicad-basics\|KiCad]] |
| **[[projects/arete/learning/backend/01-fundamentals-and-nestjs\|arete]]** (20k) | NestJS + Prisma + React Native | [[backend/README\|backend]] · [[devops/01-linux/README\|shell/devops]] · frontend (mobile) |
| **[[projects/json-healer/learning\|json-healer]]** (13k) | TS library — parsing/repair, packaging | [[foundations/dsa/05-algorithms/01-algorithms\|algorithms]] · [[concepts/04-best-practices/README\|library design]] |
| **[[projects/strictenv/learning\|strictenv]]** (9k) | TS library — typed env validation | [[concepts/04-best-practices/README\|API design]] · [[devops/09-secret-management/README\|config/secrets]] |
| **[[projects/sorepoint/learning/README\|sorepoint]]** (9k) | Crawling pipeline + Supabase/Postgres | [[backend/README\|backend]] · [[databases/sql-reference\|Postgres]] · [[devops/01-linux/README\|shell]] |
| **[[projects/my-applicant/learning/02-ai-sdk-and-byok\|my-applicant]]** (7k) | AI pipeline, BYOK, AI SDK | [[ai-ml/03-ai-engineer/README\|AI engineering]] · [[ai-ml/03-ai-engineer/04-calling-models\|calling models]] |

---

## The reverse map — "where have I actually done this?"

Use this when a course note feels abstract and you want the real instance:

| Concept | Where you hit it for real |
|---|---|
| **Idempotency keys** | [[projects/direct-debit-sandbox-java/learning/05-async-scheduling-retry\|direct-debit]] · [[projects/record-id-generator-java/learning/07-id-generation-and-idempotency\|record-id-generator]] |
| **Concurrency & threads** | [[projects/record-id-generator-java/learning/06-concurrency-and-threads\|record-id-generator]] |
| **Message queues** | [[projects/record-id-generator-java/learning/05-rabbitmq-messaging\|RabbitMQ]] · [[projects/socioboom/learning/archive/original-flat-backend-learning\|socioboom queues]] |
| **Row-level security / authz** | [[projects/gees-arise/learning/04-supabase\|gees-arise RLS]] |
| **Auth flows** | [[projects/nextvibe/learning/backend/02-auth\|nextvibe]] · [[projects/arete/learning/backend/04-auth\|arete]] |
| **Money & ledgers** | [[projects/nextvibe/learning/backend/06-money-ledger-and-payouts\|nextvibe]] |
| **Realtime / websockets** | [[projects/nextvibe/learning/backend/05-realtime\|nextvibe]] |
| **AI agents & LLM plumbing** | [[projects/my-applicant/learning/02-ai-sdk-and-byok\|my-applicant]] · [[projects/socioboom/interview/03-ai-and-agents\|socioboom]] |
| **Shell / grep / sed / regex** | [[projects/arete/learning/devops/05-grep-in-depth\|arete devops notes]] — the deepest shell material in the vault |
| **Postmortems & real bugs** | [[projects/arete/learning/backend/06-advanced-habits-and-bug-postmortems\|arete]] · [[projects/gees-arise/interview/04-bugs-and-story\|gees-arise]] |
| **Observability / logging** | [[projects/record-id-generator-java/learning/09-logging-and-observability\|record-id-generator]] |
| **Docker & perf tuning** | [[projects/record-id-generator-java/learning/10-docker-and-performance-tuning\|record-id-generator]] |

---

## Known gaps worth fixing

- **[[projects/arete/learning/devops/05-grep-in-depth|grep]], [[projects/arete/learning/devops/06-find-in-depth|find]], [[projects/arete/learning/devops/07-regex-from-zero-to-advanced|regex]], and [[projects/arete/learning/devops/08-sed-and-awk|sed/awk]]** in arete are **general knowledge sitting in a project folder** with no counterpart in [[devops/01-linux/README|devops/01-linux]] (which only has `16-sed-and-awk`). They're invisible from the course structure. Worth promoting.
- **`munakalati/` was an empty folder** — removed 2026-08-13. Recreate it with a `learning/` folder if the project restarts.
- **No project has exercised the [[architecture/04-distributed-systems/README|distributed systems]] material.** That's the Rank IV gap in [[PRIMETECHIE|the Primetechie path]], and the Raft KV store in [[project-ideas|project-ideas]] is the fix.

## Related
- [[README|Vault README]] · [[project-ideas|Project Ideas]] — what to build next
- [[INTERVIEW|Interview index]] — every project's `interview/` folder plus the domain banks
- [[PRIMETECHIE|The Primetechie Path]] — where these projects sit in the progression
