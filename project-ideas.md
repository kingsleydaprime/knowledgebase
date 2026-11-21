# Project Ideas — turning notes into ability

The notes in this vault are a **map**. Projects are the **territory** — what turns "I read about it" into "I built it and can prove it." Reading is not reps; building is.

**This file is now the index.** Every course domain has its own `projects.md` sitting next to its notes, so the reps are findable from the course rather than from here.

## How to use this

- **Pick one and finish it.** One shipped project beats five half-started ones. Finishing — deployed, tested, written up — is the skill.
- **Extend your real projects where you can.** Adding CI/CD or benchmarks to something you already built is higher-signal than a toy, and faster to start → [[projects/index|projects/]].
- **Write it up.** A short README with the *why* and what you learned turns a project into portfolio signal.
- **Every entry has a *done when*.** If you can't say when a project is finished, you'll either stop early or never stop.

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

---

## The per-domain ladders

| Domain | The one to do first |
|---|---|
| [[backend/projects\|Backend]] | Load-test and fix your own p99 |
| [[frontend/projects\|Frontend]] | The same app three ways — local state, server state, RSC |
| [[databases/projects\|Databases]] | A zero-downtime migration on a live table |
| [[data-engineering/projects\|Data Engineering]] | The end-to-end mini-pipeline, then break its idempotency |
| [[data-analysis/projects\|Data Analysis]] | A real diagnostic ("why did this change?"), then the full analyst one-pager |
| [[architecture/projects\|Architecture]] | **A Raft key-value store** |
| [[devops/projects\|DevOps]] | Containerize and deploy one app end to end |
| [[cybersecurity/projects\|Cybersecurity]] | PortSwigger's Academy, then secure your own app |
| [[web3/projects\|Web3]] | Token and wallet from scratch, then break your own contract |
| [[ai-ml/projects\|AI & ML]] | **RAG over this vault** |
| [[projects\|Foundations]] | The regex engine — one evening, theory becomes code |
| [[languages/projects\|Languages]] | The same program in three languages |
| [[mobile/projects\|Mobile]] | Survive process death, then **ship a small app to a store** |
| [[git/projects\|Git]] | The disaster drill — an hour, and git stops being scary |
| [[hardware/projects\|Hardware]] | Rev 2 of the IoT Bridge |
| [[robotics/projects\|Robotics]] | Something moving in ROS 2 + Gazebo |
| [[game-development/projects\|Game Dev]] | Ship a game jam entry |
| [[control-theory/projects\|Control theory]] | Balance a physical inverted pendulum |
| [[operations-research/projects\|Operations research]] | Model a decision you actually make, and live with the answer for a week |

---

## If you only do five

Highest signal for where you're aiming, across all four columns of [[PRIMETECHIE|the path]]:

1. 🔴 ⭐ **The order-book matching engine** (Java / systems) — below
2. 🔴 ⭐ **RAG over this vault** (AI engineering) → [[ai-ml/projects|ai-ml projects]]
3. 🔴 ⭐ **An end-to-end MLOps project** (ML engineering) → [[ai-ml/projects|ai-ml projects]]
4. 🟢 ⭐ **Containerize + deploy one app** (DevOps) → [[devops/projects|devops projects]]
5. 🟡 ⭐ **Secure your own app, then attack your own lab** (security) → [[cybersecurity/projects|cybersecurity projects]]

**Hardware is the exception** — the one column where you already have more built than written, so it needs the fewest new projects and gives the fastest returns → [[hardware/projects|hardware projects]].

---

## Java / JVM & Systems
*The low-latency / systems signal — what a firm doing market-data / FPGA work actually screens for. This is where you have the most to prove and the most upside. Kept here rather than in [[languages/projects|languages/projects]] because it's a career target, not a language tour.*

- 🟢 **Solve the concurrency exercises** — the [[languages/01-java/02-jvm-and-concurrency/exercises/index|bounded blocking queue and token-bucket rate limiter]] already have a red→green test harness. Do both — once with `synchronized`, once lock-free with `ReentrantLock`/atomics. Exercises: [[languages/01-java/02-jvm-and-concurrency/02-concurrency|concurrency]].
- 🟡 **Lock-free ring buffer (SPSC/MPSC queue)** — a bounded ring buffer using `AtomicLong` cursors and CAS, no locks. Benchmark it against `ArrayBlockingQueue`. The canonical low-latency data structure (the LMAX Disruptor's core). Exercises: [[languages/01-java/02-jvm-and-concurrency/02-concurrency|atomics/CAS]], [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|memory model]].
- 🔴 ⭐ **In-memory order book + matching engine** — a limit-order book (price levels, bid/ask, add/cancel/match) with a matching engine, single-threaded on the hot path for determinism. Feed it a synthetic order stream, measure throughput and p99 latency. *This is the single most on-target project for a trading firm* — it's literally the domain.
- 🟡 **Market-data feed parser** — parse a binary/CSV market-data feed (or a simplified FIX/ITCH-style format) at high throughput, zero-allocation on the hot path. Ties [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|batch/streaming]] to [[languages/01-java/01-language/01-fundamentals|the language]].
- 🟡 **JMH benchmark + GC tuning study** on your record-generator pipeline — add [[languages/01-java/03-tooling/04-testing|JMH]] microbenchmarks, then run it under different collectors (Parallel vs G1 vs ZGC), capture GC logs / a JFR recording, and write up the latency-vs-throughput tradeoff. Exercises: [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|JVM internals]] — GC/JIT in practice, the exact thing the notes say only *doing* teaches.
- 🟢 **Add a real test suite** to one of your Java projects — JUnit + Mockito + a Testcontainers integration test against real MySQL/RabbitMQ. The projects shipped without tests; fixing that is direct engineering-maturity signal. Exercises: [[languages/01-java/03-tooling/04-testing|testing]].

---

## ⭐ Build-Your-Own — systems mastery
*The deepest reps in the vault. Each one turns a whole topic from words into bone-deep understanding.*

> **These now have full build guides in [[build-your-own-shit/index|build-your-own-shit/]]** — numbered milestones, each independently testable, with per-language toolkits and a "where to stop". Read the guide rather than this list; the entries below are the one-line pitch and the difficulty rating.

| | Guide | Why |
|---|---|---|
| 🟠 | [[build-your-own-shit/01-http-server\|HTTP server]] | **Start here.** A weekend; a real browser is the test |
| 🟠 | [[build-your-own-shit/07-your-own-shell\|Shell]] | The smallest one that teaches the most — `fork`/`exec`, fds, pipes |
| 🟠 | [[build-your-own-shit/08-your-own-container\|Container]] | ~200 lines, one evening, and Docker stops being magical |
| 🔴 | [[build-your-own-shit/02-your-own-git\|Git]] | Real Git reads your repository. Permanently demystifies it |
| 🔴 ⭐ | [[build-your-own-shit/03-your-own-redis\|Redis]] | Data structures + networking + durability. The real `redis-cli` connects |
| 🔴 | [[build-your-own-shit/04-your-own-language\|Language / interpreter]] | The deepest single lesson. → [[compilers/index\|compilers]] is the course behind it |
| 🔴 | [[build-your-own-shit/06-your-own-database\|Database]] | B-tree, SQL subset, WAL. `kill -9` mid-write and the data survives |
| 🔴 | [[build-your-own-shit/05-your-own-os\|Operating system]] | Weeks, not a weekend. Boots from a USB stick → [[os/index\|os]] |
| 🔴 ⭐ | [[build-your-own-shit/20-your-own-raft-kv-store\|Raft key-value store]] | **The best distributed-systems project there is.** Kill the leader mid-write and nothing committed is lost |
| 🔴 | [[build-your-own-shit/19-your-own-tcp-ip-stack\|TCP/IP stack]] | `ping` answers, then the HTTP server above runs on your own TCP |
| 🟠 | [[build-your-own-shit/21-your-own-compressor\|Compressor]] | A weekend, and `gunzip` reads your output |
| 🟠 | [[build-your-own-shit/22-your-own-ray-tracer\|Ray tracer]] | The shortest path here to something you want to look at |
| 🔴 | [[build-your-own-shit/23-your-own-debugger\|Debugger]] | `ptrace`, ELF and DWARF — and `gdb` to check yourself against |
| 🔴 | [[build-your-own-shit/24-your-own-llm\|Your own LLM]] | Attention, trained from scratch. The sequel to the neural network |

Pair each with a short write-up of what you learned; these are portfolio-grade signal on their own.

---

## Product ideas
*Ideas for things other people would use, not just practice reps. The e-learning platform became active on 2026-11-14; the interactive knowledgebase is its prototype.*

- 🔴 **An e-learning platform, W3Schools-style.** Lessons in order with next/back, quizzes after every few lessons, and "write your own code" exercises checked by real tests. The vault already has the content (course standard, checks sections, labs with tests), so the platform is the product, not the material. What makes it a platform rather than a static site:
  - **Accounts and progress** that follow you across devices (auth plus a database).
  - **A code runner.** JS/TS in a Web Worker and Python via Pyodide both run in the browser. Go, Rust, C, Java and C# need a sandboxed server that runs untrusted code (Judge0-style), which is its own security project.
  - **Grading:** the learner's code runs against the lesson's lab tests, and the pass/fail result is stored.
  - Later, maybe: certificates, payments, authoring tools for other teachers.
  - *Who it's for (decided 2026-11-14):* a junior developer (0–2 years) who can ship apps but stalls on the fundamentals underneath them, and wants to become a genuinely strong engineer and get to mid-level. Students are the second audience: a CS student becomes this person a year later. Launch for the junior, because they can pay, they already know what they're missing, and I am one.
  - *Why they'd pick it:* the real competitors are boot.dev, Frontend Masters, Educative, ByteByteGo, roadmap.sh, Exercism, YouTube and AI. Draft pitch: **"The CS degree you didn't get, taught through the systems you use at work, with labs that run on real tools, in your language."**
    - **University depth for practitioners** is the headline. Depth alone isn't unique; what's unique is that every theory is tied back to a system the learner uses at work.
    - **Labs verified with real tools** are the proof. They're also the most expensive feature, because real tools mostly need servers.
    - **Eight languages**, sold as "in your language" (learn it in the stack you use at work) rather than as a comparison of languages.
  - *Languages at launch:* code you can **read** is shown in every language from day one, since it's already in the vault and is just static text. Code you can **run and get graded** is JS/TS and Python only at launch, since both run in the browser for free. Go, Java and the rest become runnable later, on a server. Label the read-only samples clearly ("Go: read-only for now"). SQL may be runnable early through PGlite.
  - *Plans (decided 2026-11-14):* the content is free, because the vault is already public and nobody pays to read. Free users get a taste of graded exercises, so they feel the difference before being asked to pay.

    | | Free | Plus | Pro |
    |---|---|---|---|
    | All lessons, every language | ✅ | ✅ | ✅ |
    | Progress tracking | ✅ | ✅ | ✅ |
    | Quizzes | ✅ | ✅ | ✅ |
    | Graded exercises (JS/TS, Python) | First lesson per course | All | All |
    | Certificates and portfolio | — | ✅ | ✅ |
    | AI tutor | — | Limited | ✅ |
    | Human review of projects | — | — | ✅ |

  - *Testing before payments:* no payment gateway yet. A plan switch in settings lets coursemates try every tier. The plan is stored on the server, and the server checks it before anything paid runs, so the gateway later only changes how the plan gets set. The switch shows the price it would cost, every click is logged, and testers are asked "would you have paid this?" Coursemates are students (the second audience), so read their price feedback with that in mind.
  - *Content architecture (decided 2026-11-14):*

    | Where | What |
    |---|---|
    | Public vault | Lessons (each with a UUID `id` in frontmatter), code in every language, visible tests (the labs), quiz questions |
    | Private repo | Hidden tests, quiz answers, reference solutions, linked by lesson UUID |
    | Platform repo | The app code |
    | Database | Users, plans, progress, submissions, plan-switch clicks |

    - The vault stays the only place lessons are edited. The platform reads it at build time as a git submodule.
    - IDs are UUIDs, added by a script. A check fails the build on a missing ID, a duplicate ID, or a removed ID that users may have progress on (compared against the previous ID list).
    - A second check makes sure every hidden test points at a lesson ID that exists and passes against the reference solution.
    - Practice exercises run in the browser against the visible tests. Certificate exercises run on the server against the hidden tests, because anything sent to the browser can be read.
  - *Stack (default decisions, 2026-11-14):*
    - **Next.js (App Router) + TypeScript**, one app with no separate backend. It's already the stack I know.
    - **Supabase** for Postgres, auth (email plus Google) and row-level security. The plan is a column on `profiles`, and only the server can change it.
    - **A web app, phone first (default, 2026-11-21).** It's designed for phones and still works on a laptop. It's also an installable PWA (progressive web app), so it gets a home-screen icon and can send streak reminders as push notifications, with no app store. A native app waits until people ask for one.
    - **Vercel** for hosting. The free tiers of Vercel and Supabase are enough for the coursemate test.
    - **Markdown rendering** with unified/remark/rehype, the same pipeline as Quartz, plus a resolver for `[[wikilinks]]`. Lesson order comes from the course index files.
    - **Browser runner:** JS/TS in a Web Worker, with TypeScript types stripped by sucrase, and a timeout that kills runaway loops. Python through Pyodide, loaded only when someone opens a Python exercise.
    - **Server runner** for certificate grading: deferred until after the first milestone. When it's needed, use a self-hosted sandbox such as Judge0 or Piston rather than building one.
    - **Payments:** deferred, as decided. Paystack is the first candidate, since it handles Naira.
  - *Lesson size (decided 2026-11-21):* Duolingo-like. One sitting takes 3–4 minutes, so a learner never gets worn out. Vault lessons today run 2,500–3,000 words (12–15 minutes), so **the platform cuts each lesson into short pieces when it builds**, one per `##` section, each with a stable `<!-- bite: uuid -->` marker so renaming a heading doesn't wipe progress. The vault stays deep and is still the only place lessons are edited. *Later, maybe:* split the vault itself into deep and short versions.
  - *Streaks (decided 2026-11-21):*
    - A day counts when the learner **finishes** a short lesson. Opening one doesn't count.
    - The day ends at midnight in the **learner's own timezone**, which is stored on their profile.
    - **Streak freezes:** a missed day uses up a freeze instead of resetting the streak. A learner holds **at most 2** (Plus: **at most 3**). They get them by:
      - **Free, every 7 days:** finishing 7 streak days earns one. After it's used, another 7 days earns the next.
      - **Free, at 30 days:** a 30-day streak earns a second one.
      - **Buying with points.**
      - **The Plus plan**, which also raises the cap to 3.
    - **Points** are earned by finishing a short lesson and by answering a quiz question correctly. **Still open (tuning numbers, pick defaults at build time):** points per lesson, per correct answer, and the price of a freeze.
  - *Milestone 1, the coursemate test:* sign up, read SWE 101 with next/back, take quizzes, run graded JS/TS and Python practice exercises in the browser, see progress, and switch plans with the price shown and clicks logged. Certificates, the AI tutor, human review and the server runner wait until after this.
  - *Name (decided 2026-11-21, may change later):* **EruditeMe**, a Spectroniq product. Written "EruditeMe" in text, and `eruditeme` in URLs and the repo name. Domain: `eruditeme.com` (unregistered on 2026-11-21, so register it). Replaces the earlier working name I Sabi.
    - **Keep the name easy to change.** The brand lives in one file, `src/config/brand.ts` (name, tagline, domain, support email, logo path), and every page, email and meta tag reads from it. The site URL comes from an environment variable.
    - **Nothing stored uses the brand name.** Database tables, columns, Supabase buckets, cookie names, `localStorage` keys, environment variable names and analytics event names stay generic (`profiles`, `streak_freezes`, `APP_URL`, not `eruditeme_*`). Code can be changed with a find-and-replace, but data and users' browsers can't.
    - **Things a rename still touches** (list them in the repo's README): the domain and a redirect from the old one, Google OAuth consent screen and callback URLs, Supabase auth email templates and redirect URLs, the email sender address, social handles, and the repo name (GitHub redirects renamed repos).
  - *Status:* **active since 2026-11-14**, alongside NextVibe.
  - *Done when:* one full course (SWE 101) is live with accounts, quizzes and in-browser JS + Python exercises, and 10 people outside my circle have finished at least one week of it.
- 🟢 **Interactive knowledgebase (the small version of the above).** Add it to the Quartz site, all on the front end: prev/next links from the course index order, a ```` ```quiz ```` block plugin (like `quartz-plugins/abbreviations`) with progress in `localStorage`, and an in-browser JS/Python runner for one lesson. Doubles as the prototype for the platform's lesson and quiz format.
  - *Done when:* one SWE 101 lesson has all three, and I've used its quiz while actually studying it.

---

## Related
- [[build-your-own-shit/index|Build Your Own Shit]] — the twenty-four full build guides
- [[BUILD-PLAN|Build Plan]] — what gets written next
- [[PRIMETECHIE|The Primetechie Path]] — where these sit as rank gates
- [[INTERVIEW|Interview Prep Index]] — the other half of proving ability
