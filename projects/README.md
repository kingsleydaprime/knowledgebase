# Projects — Learning Logs

**42% of this vault by word count lives here**, and until now it was almost entirely disconnected from the courses. This README is the join.

Each folder is a real project with two things in it:
- `learning/` — domain-split notes teaching what that project taught, in the context of its actual code and actual bugs
- `interview/` — the same material as questions with model answers (the pattern that [[INTERVIEW|the domain interview banks]] were generalised from)

**The overlap with the general folders is deliberate, not duplication.** A project note teaches a domain *as it showed up here*, with the real problem attached. The general folder ([[git/README|git]], [[devops/01-linux/README|linux]], [[concepts/README|concepts]]) is the standalone reference for the same material. Both should exist, and they should point at each other — which is what this file is for.

---

## The map — what each project exercises

| Project | What it is | Domains it exercises |
|---|---|---|
| **[[projects/nextvibe/learning/00-sys-design\|nextvibe]]** (142k words — the biggest) | NestJS platform: auth, realtime, games/AI, payments ledger | [[backend/README\|backend]] · [[backend/05-auth/01-authentication-flows\|auth]] · [[architecture/02-building-blocks/04-messaging-and-async\|realtime/async]] · [[databases/database-design-reference\|data modelling]] · [[foundations/networking/11-http-evolution\|websockets/HTTP]] |
| **[[projects/socioboom/learning/archive/original-flat-backend-learning\|socioboom]]** (67k) | Social publishing + AI agents + queues | [[architecture/02-building-blocks/04-messaging-and-async\|queues]] · [[ai-ml/03-ai-engineer/08-agents\|agents]] · [[devops/README\|deployment]] |
| **[[projects/gees-arise/learning/09-sys-design\|gees-arise]]** (32k) | Next.js + Supabase, Postgres RLS | [[databases/sql-reference\|SQL]] · [[backend/05-auth/02-authorization\|authorization]] · [[cybersecurity/04-web-security/README\|web security]] · [[git/README\|git]] · [[devops/01-linux/README\|shell]] |
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

## Topics that live ONLY here

A sweep in **August 2026** measured every project topic against the course folders. These are subjects where the project logs are the vault's *only real coverage* — the courses mention them in passing at best. Listed with the honest word counts, worst ratio first.

| Topic | In courses | In projects | Where |
|---|---|---|---|
| **React / Next.js** | 419 w (two stub READMEs) | **~44,000 w** | 105× — see [[frontend/README\|the frontend index]], now written |
| **Tailwind / shadcn** | **zero mentions, anywhere** | 1.6k w | [[projects/socioboom/learning/frontend/03-styling-and-ui\|socioboom — styling]] |
| **Supabase / BaaS** | 3 passing mentions | 4.0k w | [[projects/gees-arise/learning/04-supabase\|gees-arise]] · [[projects/sorepoint/learning/supabase\|sorepoint]] |
| **Money, ledgers, payouts** | mentioned, no note | 12.9k w | [[projects/nextvibe/learning/backend/06-money-ledger-and-payouts\|nextvibe]] |
| **Realtime / WebSockets** | mentioned, no note | 11.2k w | [[projects/nextvibe/learning/backend/05-realtime\|backend]] · [[projects/nextvibe/learning/frontend/06-realtime\|frontend]] |
| **React Native / mobile** | **zero** | 3.1k w | [[projects/arete/learning/mobile/01-react-native-fundamentals\|arete mobile]] (7 notes) |
| **grep, find, regex, sed/awk** | only `16-sed-and-awk` | 2.1k w | [[projects/arete/learning/devops/05-grep-in-depth\|arete devops notes]] — the deepest shell material in the vault |

**This is not a filing error, and the fix is not "move it."** A project note teaches a topic *as it showed up*, with the real bug attached — often better than a standalone note. The failure is only that it was **unfindable from the course structure**, so a reader concluded the vault had nothing on Next.js when it has 44,000 words.

Two of these are now fixed by indexing rather than moving: [[frontend/README|frontend]] carries a full topic→project table, as do [[frontend/01-react/README|01-react]] and [[frontend/02-next/README|02-next]]. The rest are still only reachable from this page.

**Worth a real course eventually:** money/ledgers and realtime are both large, general, and genuinely absent — they'd sit in [[backend/README|backend/]] as `08-realtime` and a financial-systems section. Mobile would be a new `frontend/06-react-native/`. Do the distillation when you next touch that code, not as a documentation project.

## Other known gaps

- **`munakalati/` was an empty folder** — removed 2026-08-13. Recreate it with a `learning/` folder if the project restarts.
- **No project has exercised the [[architecture/04-distributed-systems/README|distributed systems]] material.** That's the Rank IV gap in [[PRIMETECHIE|the Primetechie path]], and the Raft KV store in [[project-ideas|project-ideas]] is the fix.
- **No project has a unit-testing story.** The only testing notes are [[projects/gees-arise/learning/07-testing|gees-arise's Playwright E2E]] and Java's JUnit work — which is why [[backend/07-practices/02-testing-a-backend|testing a backend]] had to be written from scratch rather than distilled.

## Related
- [[README|Vault README]] · [[project-ideas|Project Ideas]] — what to build next
- [[INTERVIEW|Interview index]] — every project's `interview/` folder plus the domain banks
- [[PRIMETECHIE|The Primetechie Path]] — where these projects sit in the progression
