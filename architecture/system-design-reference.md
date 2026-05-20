# System Design — Comprehensive Reference Guide

> Everything you need to design, explain, and draw any system.
> From first principles to real-world examples. Built for interviews and actual engineering.

---

## Table of Contents

1. [How to Think About System Design](#1-how-to-think-about-system-design)
2. [Numbers Every Engineer Should Know](#2-numbers-every-engineer-should-know)
3. [Requirements and Estimation](#3-requirements-and-estimation)
4. [How to Answer a System Design Interview](#4-how-to-answer-a-system-design-interview)
5. [How to Draw Your Own System Design](#5-how-to-draw-your-own-system-design)
6. [How to Read System Design Diagrams](#6-how-to-read-system-design-diagrams)
7. [DNS](#7-dns)
8. [Load Balancers](#8-load-balancers)
9. [API Gateway](#9-api-gateway)
10. [CDN](#10-cdn)
11. [Forward Proxy vs Reverse Proxy](#11-forward-proxy-vs-reverse-proxy)
12. [Scalability](#12-scalability)
13. [Availability and Reliability](#13-availability-and-reliability)
14. [CAP Theorem](#14-cap-theorem)
15. [Consistency Patterns](#15-consistency-patterns)
16. [Caching](#16-caching)
17. [Databases — SQL vs NoSQL](#17-databases--sql-vs-nosql)
18. [Database Replication](#18-database-replication)
19. [Data Partitioning and Sharding](#19-data-partitioning-and-sharding)
20. [Message Queues and Event Streaming](#20-message-queues-and-event-streaming)
21. [Storage Systems](#21-storage-systems)
22. [Real-time and WebSockets](#22-real-time-and-websockets)
23. [API Design Patterns](#23-api-design-patterns)
24. [Microservices vs Monolith](#24-microservices-vs-monolith)
25. [Key Design Patterns](#25-key-design-patterns)
26. [Distributed Coordination and Heartbeat](#26-distributed-coordination-and-heartbeat)
27. [Distributed File Systems](#27-distributed-file-systems)
28. [Full-Text Search at Scale](#28-full-text-search-at-scale)
29. [Notification Systems](#29-notification-systems)
30. [Security Fundamentals](#30-security-fundamentals)
31. [Big Data and Stream Processing](#31-big-data-and-stream-processing)
32. [Production Infrastructure Patterns](#32-production-infrastructure-patterns)
33. [Classic Design: URL Shortener](#33-classic-design-url-shortener)
34. [Classic Design: Social Media Feed](#34-classic-design-social-media-feed)
35. [Classic Design: Chat System](#35-classic-design-chat-system)
36. [Classic Design: Rate Limiter](#36-classic-design-rate-limiter)
37. [Classic Design: Search Autocomplete](#37-classic-design-search-autocomplete)
38. [Classic Design: Notification System](#38-classic-design-notification-system)
39. [Real-World: Design YouTube](#39-real-world-design-youtube)
40. [Real-World: Design Netflix](#40-real-world-design-netflix)
41. [Real-World: Design Facebook](#41-real-world-design-facebook)

---

## 1. How to Think About System Design

### 1.1 The Mental Model

System design is not about memorising architectures. It is about understanding tradeoffs. Every decision — SQL vs NoSQL, sync vs async, monolith vs microservices — is a tradeoff between competing constraints. Your job is to understand the constraints clearly enough to make the right tradeoff for the problem at hand.

The best system designers ask more questions than they answer. They clarify before they commit.

### 1.2 The 4-Step Framework

Use this structure every single time, whether in an interview or real life.

**Step 1 — Clarify requirements (5 min)**

Never start drawing boxes. Ask first.

```
Who uses it? Consumers, businesses, internal tool?
What are the core features? Pick 2–3 to focus on.
What is the scale? DAU, requests/sec, data volume.
Any constraints? Latency requirements, consistency needs, budget.
Read-heavy or write-heavy? This drives almost every decision.
Is strong consistency required or is eventual consistency acceptable?
What does failure look like? What must never be lost?
```

Say out loud: *"Before I start designing, let me make sure I understand the requirements."* This signals maturity even before you draw anything.

**Step 2 — Estimate scale (3 min)**

Back-of-envelope calculations tell you what kind of system you need.

```
Example: Design Twitter

DAU:             100M users
Tweets/day:      100M × 2 tweets = 200M/day
Writes/sec:      200M / 86,400 ≈ 2,300 writes/sec
Reads/sec:       reads are 100× writes ≈ 230,000 reads/sec
Storage/day:     200M × 280 chars × 2 bytes ≈ 100 GB/day
Storage/5yr:     100 GB × 365 × 5 ≈ 180 TB
Bandwidth:       230,000 reads/sec × 1 KB avg = 230 MB/sec outbound
```

These numbers immediately tell you: you need horizontal scaling, a CDN, caching everywhere, and a read-heavy database strategy.

**Step 3 — High-level design (10 min)**

Draw the major components and how they connect. Don't go deep yet. Get the whole picture.

```
Client → CDN → Load Balancer → API Servers → Cache → Database
                                           ↓
                                    Message Queue → Workers → Object Storage
```

**Step 4 — Deep dive (15 min)**

Pick the hardest or most interesting parts and go deep. The interviewer will guide you. Common deep dives: database schema, feed generation, caching strategy, failure modes, consistency model.

---

## 2. Numbers Every Engineer Should Know

### 2.1 Latency Reference

| Operation | Latency | What it means |
|---|---|---|
| L1 cache read | 0.5 ns | Fastest possible |
| L2 cache read | 7 ns | Still extremely fast |
| RAM read | 100 ns | 200× slower than L1 |
| SSD read | 150 µs | 1,500× slower than RAM |
| HDD seek | 10 ms | 100,000× slower than RAM |
| Same datacenter network | 0.5 ms | Use freely |
| Cross-region network | 150 ms | Noticeable to users |
| Redis GET | ~0.1 ms | Order of magnitude faster than DB |
| Postgres query (indexed) | ~1 ms | Good — aim for this |
| Postgres query (full scan) | 100 ms+ | Problem at scale |

**Key insight:** RAM is 1,000× faster than SSD. SSD is 100× faster than HDD. A cached result is 1,000× faster than a database query. These numbers drive every caching decision you make.

### 2.2 Powers of 2

| Power | Approximate Value |
|---|---|
| 2¹⁰ | 1 thousand (1 KB) |
| 2²⁰ | 1 million (1 MB) |
| 2³⁰ | 1 billion (1 GB) |
| 2⁴⁰ | 1 trillion (1 TB) |

### 2.3 Traffic Estimation Shortcuts

```
Seconds in a day:     86,400 ≈ 100,000
1M requests/day:      ~12 requests/sec
1B requests/day:      ~12,000 requests/sec

1 server handles:     ~1,000–10,000 req/sec depending on work
Read:write ratio:     100:1 for social apps (assume unless told otherwise)
Average tweet/post:   ~300 bytes
Average image:        ~300 KB, thumbnail ~10 KB
Average video (1 min): ~6 MB compressed
Average webpage:      ~2 MB with assets
```

---

## 3. Requirements and Estimation

### 3.1 Functional vs Non-Functional

**Functional requirements** — what the system does. Features users interact with.
- "Users can post tweets"
- "Users can follow others"
- "Users can search for content"

Focus on 2–3 core features. Don't try to design everything.

**Non-functional requirements** — how well it works. These drive architecture more than functional requirements.
- **Availability:** 99.9%, 99.99%?
- **Latency:** < 200 ms? < 50 ms?
- **Consistency:** Strong or eventual?
- **Durability:** Can we lose any data?
- **Scalability:** 10K users or 100M?

### 3.2 Estimation Formulas

```
QPS = DAU × actions_per_day / 86,400
Storage/day = writes_per_day × avg_record_size
Bandwidth = QPS × avg_response_size
Servers needed = peak_QPS / requests_per_server
Cache size = QPS × avg_response_size × seconds_to_cache
```

### 3.3 Worked Example: Design Instagram

```
DAU: 500M users
Photos uploaded/day: 500M × 0.1 = 50M photos/day
Photo size: 3 MB average, thumbnail 20 KB
Write QPS: 50M / 86,400 ≈ 580 writes/sec
Read QPS: 580 × 100 (read-heavy) = 58,000 reads/sec
Storage/day: 50M × 3 MB = 150 TB/day (photos only)
Storage/year: 150 TB × 365 ≈ 55 PB/year

Conclusions:
- Object storage (S3/MinIO) for photos — DB can't handle 150 TB/day
- CDN is mandatory — 58,000 reads/sec of media from one origin = impossible
- Read replicas needed for metadata DB
- Caching critical for feed and profile data
```

---

## 4. How to Answer a System Design Interview

### 4.1 What Interviewers Actually Evaluate

Interviewers are not checking if you know the "right" answer. There is no right answer. They are watching:

1. **Do you ask clarifying questions before diving in?** Jumping straight to drawing boxes is a red flag — real engineers clarify first.
2. **Can you reason about tradeoffs?** "I'd use Cassandra here because X, though the tradeoff is Y" is better than "I'd use Cassandra because it's fast."
3. **Do you know when to go deep vs stay high-level?** Spending 10 minutes on a schema detail when the interviewer wants the broad architecture is a waste.
4. **Can you handle pushback?** "What if we need strong consistency here?" — can you adapt?
5. **Do you think about failure modes?** What happens when the database goes down? When the cache misses?

### 4.2 The Verbal Framework — What to Say

**Opening (30 seconds):**
> "Before I start drawing, I want to make sure I understand the requirements. Can I ask a few questions?"

Then ask the questions from Step 1 of the framework. Write the answers on the board.

**After requirements:**
> "Let me do some quick back-of-envelope estimates to understand the scale we're dealing with."

Run through QPS, storage, bandwidth. Write numbers on the board.

**High-level design:**
> "I'll start with a simple high-level design and we can drill into the parts that matter most."

Draw the boxes. Narrate as you draw. Don't go silent.

**Transitioning to deep dive:**
> "There are a few interesting problems here — feed generation, caching strategy, and the database schema. Which would you like to dig into?"

Let the interviewer steer. If they have no preference, pick the hardest problem.

**Handling tradeoffs:**
> "We could go with approach A which gives us X but costs us Y, or approach B which gives us Y but costs us X. Given the scale requirements, I'd lean toward A because..."

Always explain the why.

### 4.3 Common Mistakes

| Mistake | What to do instead |
|---|---|
| Start drawing without clarifying | Ask at least 3 questions first |
| Go too deep too fast | Get the full picture first, then drill |
| Say "I'd use microservices" without reason | Justify every major decision |
| Ignore failure modes | Always ask: what happens when X fails? |
| Use buzzwords without depth | Only mention something if you can explain it |
| Stay silent | Narrate your thinking constantly |
| Claim a perfect solution | Acknowledge tradeoffs — there are always tradeoffs |

### 4.4 The D.E.S.I.G.N Framework (Alternative Structure)

An alternative to the 4-step framework:

- **D** — Define and clarify requirements
- **E** — Establish architecture (high-level)
- **S** — Specify components (deep dive)
- **I** — Identify bottlenecks and failure modes
- **G** — Go deeper on critical paths
- **N** — Nail the tradeoffs and summarise

---

## 5. How to Draw Your Own System Design

### 5.1 The Drawing Principles

System design diagrams communicate architecture. They are not art — they communicate decisions. A good diagram makes the flow of data and control obvious at a glance.

**Rule 1: Draw data flow, not just components.** Arrows should show what data moves where. Label the arrows if the relationship isn't obvious.

**Rule 2: Group by responsibility.** Client layer, gateway layer, service layer, data layer. Keep similar things together.

**Rule 3: Name everything.** Every box gets a label. "DB" is not a label — "PostgreSQL (primary)" is.

**Rule 4: Left to right or top to bottom.** Pick a direction for data flow and be consistent.

**Rule 5: Don't over-detail.** A system design diagram is not a code diagram. You don't need to show every table or every endpoint. Show the major components and how they connect.

### 5.2 Standard Component Shapes (Whiteboard Convention)

```
[Box]                → Service or server
[Cylinder]           → Database
[Parallelogram]      → Queue / message broker
[Cloud shape]        → External service / CDN / internet
[Diamond]            → Decision point or load balancer
─────────────►       → Synchronous request/response
- - - - - - ►       → Asynchronous message
══════════════       → Data replication
```

On a whiteboard, just be consistent. Label everything if the shape is ambiguous.

### 5.3 The Layered Drawing Approach

Draw in this order:

**Layer 1 — Clients**
```
Mobile App    Web Browser    External API Consumers
```

**Layer 2 — Edge / Entry**
```
CDN → DNS → Load Balancer → API Gateway
```

**Layer 3 — Application**
```
Auth Service    API Servers    Worker Services
```

**Layer 4 — Data**
```
Cache (Redis)    Primary DB    Read Replicas    Object Storage
```

**Layer 5 — Async Infrastructure**
```
Message Queue → Workers → Notification Service
```

**Then add arrows** showing data flow between layers.

### 5.4 A Worked Drawing Example: Design a Job Board

```
Step 1: Identify components
- Users (job seekers, employers)
- API servers
- Search service
- Database (jobs, users, applications)
- File storage (resumes, company logos)
- Email notifications
- CDN for static assets

Step 2: Draw the layers
┌──────────────────────────────────────────────────┐
│  Browser / Mobile App                            │
└──────────────┬───────────────────────────────────┘
               │ HTTPS
┌──────────────▼───────────────────────────────────┐
│  CDN (static assets: logos, CSS, JS)             │
│  DNS → Load Balancer                             │
└──────────────┬───────────────────────────────────┘
               │
┌──────────────▼───────────────────────────────────┐
│  API Servers (stateless, horizontally scaled)    │
│  POST /jobs  GET /jobs/search  POST /applications│
└──┬───────────┬───────────────────┬───────────────┘
   │           │                   │
   ▼           ▼                   ▼
[Redis]  [Elasticsearch]    [PostgreSQL]
Cache    (job search)       (jobs, users,
                            applications)
                                   │
                                   ▼
                            [S3 / MinIO]
                            (resumes, logos)
   │
   ▼ (async)
[Queue] → [Email Worker] → [SendGrid]
```

Step 3: Annotate decisions
- Why CDN? Static assets, reduce origin load
- Why Elasticsearch? Full-text job search, faceting by location/salary
- Why Redis? Cache popular job listings, session storage
- Why queue for email? Decouple notification from API response

### 5.5 Drawing for an Interview vs for Engineering

**Interview:** Draw fast, narrate as you go, use shorthand. The diagram is a communication tool, not documentation.

**Engineering:** Use a proper tool (Excalidraw, Lucidchart, draw.io, Mermaid in code). Include a legend. Version control your diagrams alongside your code.

---

## 6. How to Read System Design Diagrams

### 6.1 The Reading Strategy

When you encounter a system design diagram — in a book, blog post, pull request, or interview — use this reading strategy:

1. **Find the entry point.** Where does data enter the system? Usually top-left or labeled "Client." Start there.
2. **Follow the arrows.** Arrows show data flow. Follow them from source to destination.
3. **Identify the layers.** Group components by responsibility — edge, application, data, async.
4. **Find the databases.** Cylinders or boxes labeled "DB." Multiple databases means different data models or scaling strategies.
5. **Find the queues.** Parallelograms or boxes labeled "Queue/Kafka/RabbitMQ." They indicate async processing.
6. **Look for caches.** Redis boxes between the application and database. Why are they there?
7. **Read the annotations.** Numbers, labels on arrows, and notes next to components explain the non-obvious decisions.
8. **Ask about failure modes.** For every component: what happens when it fails?

### 6.2 Common Patterns to Recognise

**The Cache-Aside Pattern:**
```
Client → API → Cache? No → DB → Store in Cache → Return
                Yes → Return from Cache
```
When you see an API server with Redis between it and the DB, this is cache-aside.

**Fan-Out Pattern:**
```
Event → Queue → Worker 1 (email)
             → Worker 2 (push notification)
             → Worker 3 (analytics)
```
One event triggers multiple downstream effects. Identifies as a queue with multiple consumers.

**CQRS Pattern:**
```
Write Path: Client → API → Command Handler → Write DB
Read Path:  Client → API → Query Handler  → Read DB (optimised)
```
Two separate paths for reads and writes. Different databases or at least different models.

**Sharded Database:**
```
API → Shard Router → DB Shard 1 (user_id 0-25M)
                  → DB Shard 2 (user_id 25M-50M)
                  → DB Shard 3 (user_id 50M-75M)
```
Multiple databases with the same schema, each holding a subset of data.

**Read Replica Pattern:**
```
Write → Primary DB ──replication──► Replica 1 (reads)
                                 ► Replica 2 (reads)
                                 ► Replica 3 (reads)
```
One primary handles all writes, replicas handle reads.

### 6.3 What Each Symbol Means

| What you see | What it means |
|---|---|
| Box between client and database | Caching layer — check the label |
| Multiple boxes with a load balancer in front | Horizontally scaled service |
| Dotted arrow | Asynchronous communication |
| Solid arrow | Synchronous (request-response) |
| Two databases with an arrow between them | Replication |
| A box labeled "CDN" near the client | Static asset delivery at edge |
| A router/gateway box at the entry | API Gateway — auth, routing, rate limiting |
| Multiple databases with a router | Sharding |

---

## 7. DNS

### 7.1 What DNS Does

DNS (Domain Name System) translates human-readable domain names into IP addresses. When you type `api.example.com`, DNS returns `203.0.113.42` so your browser knows where to connect.

DNS is the internet's phone book. Every network request starts with a DNS lookup.

### 7.2 How DNS Resolution Works

```
Browser → OS cache → check
          Router cache → check
          ISP Resolver (Recursive) → check
          Root Nameserver → "Try .com TLD server"
          .com TLD Server → "Try example.com nameserver"
          Authoritative Nameserver → "203.0.113.42"
                                 ↓
                            Cache at each step with TTL
```

**TTL (Time To Live)** — how long each cache holds the result. Low TTL (60s) = faster failover but more DNS queries. High TTL (86400s) = fewer queries but slow failover.

### 7.3 DNS Record Types

| Record | Purpose | Example |
|---|---|---|
| A | Maps hostname to IPv4 | `api.example.com → 203.0.113.42` |
| AAAA | Maps hostname to IPv6 | `api.example.com → 2001:db8::1` |
| CNAME | Alias to another hostname | `www.example.com → example.com` |
| MX | Mail server for domain | `example.com → mail.example.com` |
| TXT | Arbitrary text (SPF, DKIM) | `example.com → "v=spf1 include:..."` |
| NS | Nameservers for domain | `example.com → ns1.cloudflare.com` |
| SOA | Start of authority | Zone metadata |

### 7.4 DNS in System Design

**Geo DNS** — return different IPs based on the user's location. Users in Europe get the EU server IP, users in Africa get the AF server IP. Reduces cross-continent latency.

**DNS-based load balancing** — return multiple A records. Client picks one. No guarantee of even distribution but works for simple cases.

**Failover** — when a primary server goes down, update the DNS record to point to the backup. Limited by TTL — if TTL is 3600s, failover takes up to an hour to propagate.

**Cloudflare / Route 53** — managed DNS with DDoS protection, anycast routing, and < 1ms resolution from edge locations.

---

## 8. Load Balancers

### 8.1 What Load Balancers Do

A load balancer distributes incoming traffic across multiple servers. Without it, one server receives all traffic and becomes a bottleneck and single point of failure.

```
Client → Load Balancer → Server 1
                      → Server 2
                      → Server 3
```

Load balancers also do health checking — if Server 2 is down, traffic goes to Server 1 and 3 only.

### 8.2 Load Balancing Algorithms

| Algorithm | How it works | Best for |
|---|---|---|
| Round robin | Distribute evenly in sequence | Servers with equal capacity |
| Weighted round robin | More requests to stronger servers | Mixed server capacities |
| Least connections | Route to server with fewest active connections | Long-lived connections (WebSockets) |
| IP hash | Same client always hits same server | Session affinity (sticky sessions) |
| Least response time | Route to fastest responding server | Latency-sensitive workloads |
| Random | Pick a random server | Simple, works well in practice |

### 8.3 Layer 4 vs Layer 7 Load Balancing

**Layer 4 (Transport layer)** — routes based on IP address and TCP/UDP port. Faster but dumb — can't inspect the HTTP content.

**Layer 7 (Application layer)** — routes based on HTTP headers, URL path, cookie, content type. Can route `/api/*` to API servers and `/static/*` to static file servers. Slower but intelligent.

Most modern systems use Layer 7 load balancers (Nginx, HAProxy, AWS ALB).

### 8.4 Session Affinity (Sticky Sessions)

Some applications store session state on the server (bad practice, but common in legacy systems). Sticky sessions ensure the same client always hits the same server.

Problem: if that server goes down, the session is lost. Better approach: store session state in a shared Redis cache — then any server can handle any request.

### 8.5 Health Checks

Load balancers continuously ping each server (usually `GET /health`). If a server fails to respond within a threshold, it's removed from rotation. When it recovers, it's added back.

---

## 9. API Gateway

### 9.1 What an API Gateway Does

An API Gateway is a single entry point for all client requests. It sits in front of your services and handles cross-cutting concerns:

- **Authentication** — verify JWT before any service sees the request
- **Rate limiting** — 100 requests/minute per user, enforced at the gateway
- **Routing** — `/api/users/*` → User Service, `/api/orders/*` → Order Service
- **Request/response transformation** — translate between client format and internal format
- **SSL termination** — handle HTTPS at the gateway, internal traffic uses HTTP
- **Logging and monitoring** — every request logged in one place
- **Circuit breaking** — stop routing to services that are failing

```
Client → API Gateway → Auth Service
                    → User Service
                    → Order Service
                    → Payment Service
```

### 9.2 API Gateway vs Load Balancer

| | Load Balancer | API Gateway |
|---|---|---|
| Primary job | Distribute traffic | Route, authenticate, transform |
| Works at | Layer 4 or 7 | Layer 7 |
| Knows about | IPs and ports | HTTP methods, paths, headers |
| Authentication | No | Yes |
| Rate limiting | No | Yes |
| Examples | Nginx, HAProxy, AWS NLB | Kong, AWS API GW, Traefik |

In practice, you often have both: a load balancer distributes traffic to multiple API Gateway instances, and the API Gateway handles routing and auth.

---

## 10. CDN

### 10.1 What a CDN Does

A Content Delivery Network is a distributed network of servers (edge locations) around the world. It caches your content close to users. Instead of a user in Lagos downloading a file from a server in Virginia (150ms latency), they get it from an edge server in Lagos (5ms latency).

```
User (Lagos) → Edge Server (Lagos) → Cache hit? → Serve directly
                                   → Cache miss → Origin Server (Virginia)
                                                → Cache it → Serve
```

### 10.2 What to Put on a CDN

**Always:** Static assets — images, videos, CSS, JavaScript, fonts, PDFs.

**Sometimes:** API responses for public, cacheable data (product catalogue, news feed for non-logged-in users).

**Never:** User-specific data, authentication endpoints, real-time data that must always be fresh.

### 10.3 CDN Cache Invalidation

When you update a file, the old version may be cached at edge nodes for the TTL duration.

**Strategy 1 — URL versioning:** `app.js?v=abc123` — change the hash when the file changes. Cache never serves stale content.

**Strategy 2 — Path versioning:** `/v2/app.js` — same idea, different URL.

**Strategy 3 — Manual purge:** Call CDN API to invalidate specific URLs. Cloudflare, CloudFront support this.

### 10.4 Push vs Pull CDN

**Pull CDN** — CDN fetches from origin on first cache miss, caches it. Zero setup. Slight latency on first request. Best for most cases.

**Push CDN** — You push files to CDN proactively before anyone requests them. Good for large files (videos) where you want zero first-load latency.

---

## 11. Forward Proxy vs Reverse Proxy

### 11.1 Forward Proxy

A forward proxy sits between clients and the internet. Clients talk to the proxy, which makes requests on their behalf.

```
Client → Forward Proxy → Internet
```

**Use cases:** Corporate firewalls (monitor/control employee internet), bypassing geo-restrictions (VPN), anonymising client IP, caching for office networks.

The server sees the proxy's IP, not the client's IP.

### 11.2 Reverse Proxy

A reverse proxy sits between the internet and your servers. Clients think they're talking to your servers directly, but they're talking to the proxy.

```
Internet → Reverse Proxy → Server 1
                        → Server 2
```

**Use cases:** Load balancing, SSL termination, caching, DDoS protection, hiding internal infrastructure. Nginx is the most common reverse proxy.

**Key difference:** A forward proxy hides the client from the server. A reverse proxy hides the server from the client.

---

## 12. Scalability

### 12.1 Vertical vs Horizontal Scaling

**Vertical scaling (scale up)** — add more CPU, RAM, or faster disk to an existing server.
- Simple — no code changes
- Hard limit — biggest machine is still one machine
- Single point of failure
- Good starting point for most systems

**Horizontal scaling (scale out)** — add more servers.
- Theoretically unlimited
- Requires stateless application layer
- Needs load balancer
- Industry standard for large systems

### 12.2 Stateless vs Stateful Architecture

Horizontal scaling requires stateless servers. State (sessions, user data) must live in a shared store.

```
Stateful (can't scale):
User → Server A (has their session)
     ← if Server A dies, session lost

Stateless (scales freely):
User → Load Balancer → Server A or B or C
                       All servers read session from Redis
     ← any server can handle any request
```

The rule: **servers should be disposable.** Killing and replacing a server should have zero user impact.

### 12.3 Database Scaling

**Read replicas** — primary handles all writes, replicas handle reads. Most effective when read:write ratio is high.

```
Writes → Primary DB
Reads  → Replica 1, Replica 2, Replica 3

Replication lag: replica is 1–100ms behind primary
For reads requiring consistency: always read from primary
```

**Connection pooling** — databases handle a limited number of connections. PgBouncer (PostgreSQL) or HikariCP (Java) pool connections so 1,000 application instances don't open 1,000 direct DB connections.

**Caching** — the most impactful scaling tool. If 80% of reads hit the same 20% of data, caching that 20% eliminates 80% of database reads.

**Vertical partitioning** — split different tables to different databases. User profile data on one DB, activity data on another.

**Horizontal partitioning (sharding)** — see Section 19.

---

## 13. Availability and Reliability

### 13.1 Availability Numbers

| Availability | Downtime/year | Downtime/month |
|---|---|---|
| 99% | 3.65 days | 7.2 hours |
| 99.9% | 8.7 hours | 43.8 minutes |
| 99.99% | 52.6 minutes | 4.4 minutes |
| 99.999% | 5.26 minutes | 26 seconds |

Getting from three nines to four nines is a 10× engineering effort. Getting from four to five nines is another 10× on top of that. Know your SLA requirements before over-engineering.

### 13.2 Failure Modes and Mitigations

| Failure | Mitigation |
|---|---|
| Single server failure | Multiple instances + load balancer |
| Database failure | Primary-replica setup, automatic failover |
| Datacenter outage | Multi-region deployment, geo DNS |
| Cascading failures | Circuit breakers, timeouts, bulkheads |
| Slow dependency | Timeouts, fallbacks, async processing |
| Traffic spike | Auto-scaling, rate limiting, queue buffering |
| Memory leak | Health checks, auto-restart, canary deploys |
| Bad deploy | Blue-green deployment, feature flags, rollback |

### 13.3 Circuit Breaker Pattern

Prevents cascading failures when a downstream service is slow or down.

```
States:
CLOSED   → normal operation, requests pass through
OPEN     → too many failures, reject immediately (fast fail)
HALF-OPEN → trial period, allow some requests to test recovery

Threshold: 5 failures in 10 seconds → trip to OPEN
Recovery:  30 seconds later → try HALF-OPEN → success → CLOSED
```

Without a circuit breaker: slow dependency causes request queues to fill up, threads to exhaust, memory to spike, your service goes down. With a circuit breaker: your service fast-fails immediately and remains healthy.

### 13.4 Redundancy Strategies

**Active-Active** — multiple instances all serving traffic. If one dies, others absorb load. No failover delay.

**Active-Passive** — one primary serves traffic, standbys ready to take over. Failover takes time (seconds to minutes). Simpler to manage.

**Geographic redundancy** — replicate across regions. Protects against datacenter failures. DNS-based or anycast routing switches traffic.

---

## 14. CAP Theorem

### 14.1 The Theorem

In a distributed system you can only guarantee two of three properties simultaneously:

**Consistency (C)** — every read gets the most recent write or an error. All nodes see the same data at the same time.

**Availability (A)** — every request receives a response (not necessarily the latest data). System is always accessible.

**Partition Tolerance (P)** — system continues operating even when network partitions (communication failures between nodes) occur.

**Network partitions are inevitable in distributed systems.** You always need P. The real choice is between C and A during a partition.

### 14.2 CP vs AP in Practice

| Type | What it means | Examples | Use when |
|---|---|---|---|
| CP | Returns error rather than stale data | PostgreSQL, MongoDB (strong), HBase, ZooKeeper | Banking, inventory, anything where stale data causes real harm |
| AP | Returns possibly stale data rather than error | Cassandra, DynamoDB, CouchDB | Social feeds, likes counts, shopping carts — eventual consistency acceptable |

**Example:** Bank balance must be CP. If two servers disagree on your balance, the system must refuse to serve rather than show you a wrong balance. A "likes" counter on a post can be AP — seeing 1,003 instead of 1,004 likes for a second is fine.

---

## 15. Consistency Patterns

### 15.1 Strong Consistency

After a write completes, all subsequent reads return that value. Achieved with synchronous replication or consensus protocols (Raft, Paxos).

```
Write "balance=5000" → synchronously replicate → acknowledge
Any read after: always gets balance=5000
Cost: higher write latency (must wait for all replicas)
```

### 15.2 Eventual Consistency

Writes propagate asynchronously. Replicas converge over time. Briefly, you might read stale data.

```
Write "likes=100" → acknowledge → async replicate
Read immediately: might get likes=99 (replica not yet updated)
Read 1 second later: gets likes=100
Benefit: faster writes, higher availability
```

### 15.3 Read-Your-Own-Writes Consistency

After a user writes, they always see their own write. Other users might see stale data. Common compromise for social apps.

**Implementation:** Route the same user's reads to the primary for X seconds after a write. Or store a `wrote_at` timestamp in the session — read from primary if recent.

### 15.4 Monotonic Reads

A user never sees older data on a subsequent read. Prevents time-travel confusion (you see a comment, refresh, and it disappears).

**Implementation:** Sticky sessions — route each user to the same replica consistently.

### 15.5 ACID vs BASE

**ACID (relational DBs):**
- **A**tomic — all or nothing
- **C**onsistent — data always valid
- **I**solated — transactions don't interfere
- **D**urable — committed data persists

**BASE (NoSQL):**
- **B**asically **A**vailable — system is always up
- **S**oft state — state may change without input (replication)
- **E**ventually consistent — converges over time

---

## 16. Caching

### 16.1 What Caching Solves

A database query takes ~1ms (indexed). A cache read takes ~0.1ms. At 100,000 reads/sec, caching the top 20% of data eliminates 80,000 database queries per second. This is the single most impactful scaling technique.

### 16.2 Caching Strategies

**Cache-aside (lazy loading)** — most common.
```
1. App checks cache
2. Cache miss → fetch from DB → store in cache → return
3. Cache hit → return from cache
Pro: only caches what's actually needed
Con: cache miss causes two round trips (cache + DB)
```

**Write-through** — write to cache and DB simultaneously.
```
1. App writes to cache
2. Cache synchronously writes to DB
3. Cache always has fresh data
Pro: no stale reads
Con: every write goes to both — slower writes
```

**Write-behind (write-back)** — write to cache only, flush to DB async.
```
1. Write to cache only, return immediately
2. Async flush to DB in batches
Pro: extremely fast writes
Con: risk of data loss if cache crashes before flush
```

**Read-through** — cache sits in front of DB, handles misses automatically.
```
App always reads from cache only
Cache fetches from DB on miss automatically
Pro: app code simpler
Con: less control over what gets cached
```

### 16.3 Cache Eviction Policies

| Policy | How it works | Best for |
|---|---|---|
| LRU (Least Recently Used) | Evict item not accessed for longest time | General purpose — most common |
| LFU (Least Frequently Used) | Evict item accessed least often | Trending content |
| FIFO | Evict oldest inserted item | When recency doesn't matter |
| TTL | Items expire after set time | Time-sensitive data (sessions, OTPs) |

### 16.4 Cache Stampede (Thundering Herd)

When a popular cache key expires, thousands of requests simultaneously miss and all try to rebuild the cache, slamming the database.

**Solutions:**
1. **Mutex/lock** — only one request rebuilds, others wait
2. **Probabilistic early expiry** — randomly refresh before TTL expires
3. **Background refresh** — async job refreshes cache before it expires
4. **Staggered TTL** — add random jitter to TTL (`TTL + rand(0, 300)`)

### 16.5 What Not to Cache

- Passwords or secrets
- Data that must always be real-time fresh (bank balance, seat availability)
- Large objects that fill cache and evict useful entries
- Data accessed only once — caching only pays off with repeated access

### 16.6 Cache Key Design

```
# Pattern: entity:id:field or entity:params_hash

user:{userId}                    → user profile
event:{eventId}                  → event details
feed:{userId}:{page}             → user's feed
search:{query_hash}              → search results
rate:{userId}:{current_minute}   → rate limit counter
session:{sessionId}              → user session
```

When an entity changes, delete or update all related cache keys.

---

## 17. Databases — SQL vs NoSQL

### 17.1 SQL vs NoSQL

| | SQL | NoSQL |
|---|---|---|
| Structure | Fixed schema, tables, rows | Flexible schema, various data models |
| Scaling | Primarily vertical, complex horizontal | Designed for horizontal scaling |
| Consistency | ACID guaranteed | Eventual consistency (usually) |
| Joins | Native, efficient | Application-level, expensive |
| Query flexibility | Very high (SQL) | Limited — optimised for specific patterns |
| Best for | Complex queries, transactions, relationships | High write throughput, flexible schema, huge scale |

### 17.2 NoSQL Types

| Type | Examples | Best for |
|---|---|---|
| Key-Value | Redis, DynamoDB, Memcached | Caching, sessions, simple lookups. O(1) access. |
| Document | MongoDB, CouchDB, Firestore | Flexible schema, nested objects, content management |
| Wide-column | Cassandra, HBase, BigTable | Time-series, analytics, write-heavy at massive scale |
| Graph | Neo4j, Amazon Neptune | Social graphs, recommendations, fraud detection |
| Search | Elasticsearch, Typesense | Full-text search, faceted search, log analytics |
| Time-series | InfluxDB, TimescaleDB | Metrics, monitoring, IoT data |
| Vector | Pinecone, pgvector | ML embeddings, semantic search |

### 17.3 When to Use Which

**Use PostgreSQL/MySQL when:**
- Data is relational and has clear entities with relationships
- You need transactions (money, orders)
- You need complex queries across multiple tables
- Team knows SQL well
- Default choice for most web applications

**Use MongoDB when:**
- Schema changes frequently and is truly unpredictable
- Documents are naturally nested and rarely cross-referenced
- Rapid prototyping where schema flexibility matters

**Use Cassandra/HBase when:**
- Write throughput is extreme (millions/sec)
- Data is time-series or has a clear partition key
- You can tolerate eventual consistency
- Scale is truly massive (billions of rows)

**Use Redis when:**
- Caching
- Sessions
- Rate limiting counters
- Real-time leaderboards (sorted sets)
- Pub/sub messaging

**Use Elasticsearch when:**
- Full-text search
- Log aggregation and analysis
- Faceted search (filter by multiple attributes)

---

## 18. Database Replication

### 18.1 How Replication Works

The primary database writes every change to a replication log (WAL in PostgreSQL, binary log in MySQL). Replicas read this log and replay the changes. Replicas are eventually consistent with the primary.

### 18.2 Synchronous vs Asynchronous Replication

**Synchronous:**
```
Write → Primary → wait for replica ACK → respond to client
Pros: zero data loss
Cons: slower writes, replica failure blocks primary writes
Use for: financial systems, anything where data loss is unacceptable
```

**Asynchronous:**
```
Write → Primary → respond to client → replicate async
Pros: fast writes
Cons: potential data loss if primary fails before replica syncs
Replication lag: typically 1–100ms, can spike under load
Use for: most web applications where slight lag is acceptable
```

### 18.3 Replication Topologies

**Primary-Replica (most common):**
```
Primary (writes + reads)
    ↓ replication
Replica 1 (reads only)
Replica 2 (reads only)
```

**Primary-Primary (multi-master):**
```
Primary 1 ←→ Primary 2
Both accept writes — conflict resolution required
Use for: geo-distributed systems where users write to local region
```

**Cascaded replication:**
```
Primary → Replica 1 → Replica 2 → Replica 3
Reduces load on primary, increases replication lag
```

### 18.4 What to Route Where

```
All writes           → Primary
Strong-consistency reads → Primary
Feed reads, profile reads → Replicas
Analytics queries    → Dedicated replica (or warehouse)
```

---

## 19. Data Partitioning and Sharding

### 19.1 Partitioning vs Sharding

**Partitioning** — same database server, different physical files. Transparent to the application. PostgreSQL manages it. Use for tables with 100M+ rows.

**Sharding** — different database servers. Application must know which shard to query. Much more complex. Use when a single server can't handle the load (typically 10B+ rows or millions of writes/sec).

### 19.2 Partitioning Strategies

**Range partitioning (most common):** Split by time range — perfect for logs, events, transactions.

```sql
PARTITION BY RANGE (created_at);
-- transactions_2024: 2024-01-01 to 2025-01-01
-- transactions_2025: 2025-01-01 to 2026-01-01
-- Query for 2025 → only scans the 2025 partition
```

**List partitioning:** Split by discrete values.
```sql
PARTITION BY LIST (region);
-- events_west_africa: NG, GH, SN
-- events_east_africa: KE, TZ, ET
```

**Hash partitioning:** Distribute rows evenly.
```sql
PARTITION BY HASH (user_id);
-- partition 0: user_id % 4 = 0
-- partition 1: user_id % 4 = 1
```

### 19.3 Sharding

Split rows across multiple database servers based on a shard key.

```
API → Shard Router → DB 1 (user_id % 4 == 0)
                  → DB 2 (user_id % 4 == 1)
                  → DB 3 (user_id % 4 == 2)
                  → DB 4 (user_id % 4 == 3)
```

**Shard key requirements:**
- High cardinality (many unique values)
- Even distribution (no hot shards)
- Queries rarely cross shard boundaries
- Don't shard by status or country — creates hot shards

**The cross-shard query problem:**
```
Works well:  "Get all posts by user X" → all on one shard
Breaks:      "Get trending posts across all users" → must query ALL shards
```
Design your access patterns around your shard key.

**Consistent hashing** — used in distributed caches. Servers on a ring. Key maps to nearest server clockwise. Adding a server remaps only 1/N keys instead of nearly all keys.

**Don't shard prematurely.** A well-optimised single PostgreSQL instance with read replicas can handle billions of rows and thousands of queries per second. Sharding adds enormous operational complexity. Shard when you've exhausted every other option.

---

## 20. Message Queues and Event Streaming

### 20.1 Why Queues

Queues decouple producers from consumers. The producer puts a message in the queue and moves on. Consumers process at their own rate. This enables:
- **Async processing** — API responds instantly, work happens in background
- **Load buffering** — queue absorbs traffic spikes
- **Retry logic** — failed jobs requeue automatically
- **Fan-out** — one event triggers multiple downstream effects

### 20.2 Message Queue vs Event Stream

| | Message Queue (RabbitMQ, SQS, BullMQ) | Event Stream (Kafka) |
|---|---|---|
| Message lifetime | Consumed and deleted | Retained for days/forever |
| Consumers | One consumer per message | Multiple consumers read same event |
| Replay | No | Yes — replay historical events |
| Use for | Task distribution, email, jobs | Audit logs, analytics pipelines, event sourcing |

### 20.3 Delivery Guarantees

| Guarantee | Meaning | Risk |
|---|---|---|
| At-most-once | Sent once, may be lost | Data loss |
| At-least-once | Retried until acknowledged, may duplicate | Duplicate processing |
| Exactly-once | Processed exactly one time | Complex, expensive |

**Design consumers to be idempotent.** Processing the same message twice should have the same result as once. Use an idempotency key (`hash(userId + eventId + channel)`). This makes at-least-once delivery safe and is simpler than exactly-once semantics.

### 20.4 Queue Pitfalls

**Dead letter queue (DLQ)** — always have a DLQ for messages that fail repeatedly. Without it, poison messages are lost silently.

**Poison messages** — a message that always causes the consumer to crash. Without a DLQ, it blocks the queue forever.

**Consumer lag** — producers faster than consumers → queue grows unbounded. Add more consumers or scale consumer compute.

**Message ordering** — queues don't guarantee order by default. Use Kafka partition keys if order within a partition matters.

---

## 21. Storage Systems

### 21.1 Block vs File vs Object Storage

| Type | What it is | Examples | Best for |
|---|---|---|---|
| Block storage | Raw storage blocks, like a hard drive | AWS EBS, local SSD | Database volumes, OS disks, low latency I/O |
| File storage | Hierarchical filesystem with directories | AWS EFS, NFS | Shared filesystems, home directories |
| Object storage | Flat namespace, key-value for blobs | S3, MinIO, R2, GCS | Images, videos, backups, logs — any unstructured data |

### 21.2 Object Storage Pattern

Object = data + metadata + unique key. Bucket = container for objects.

**Presigned URL pattern** (client uploads directly — server never handles bytes):

```
1. Client → POST /storage/presigned-url → Server generates signed S3 URL
2. Client → PUT signedUrl (with file bytes) → S3/MinIO directly
3. Client → POST /api/confirm (with file key) → Server saves the key to DB

Benefit: server doesn't become a bandwidth bottleneck
         S3 handles the upload, scaling, and durability
```

### 21.3 Storage Durability

S3 provides 11 nines of durability (99.999999999%). Data is replicated across multiple availability zones. You're unlikely to lose data from storage failure — the risk is application bugs deleting data.

Always have:
- Versioning enabled on critical buckets
- Cross-region replication for disaster recovery
- Lifecycle policies to move old data to cheaper tiers (S3 Glacier)

---

## 22. Real-time and WebSockets

### 22.1 Options for Real-Time

| Method | How it works | Latency | Server load | Best for |
|---|---|---|---|---|
| Polling | Client requests every N seconds | Up to N sec | High | Infrequent updates |
| Long-polling | Server holds request until data available | Near real-time | Medium | Chat fallback |
| WebSockets | Persistent bidirectional TCP connection | Real-time | Low per connection | Chat, live games |
| SSE (Server-Sent Events) | Server pushes over HTTP, one direction | Real-time | Low | Live feeds, dashboards |

### 22.2 WebSocket Scaling Challenge

```
Problem:
User A (on Server 1) sends message to User B (on Server 2)
Server 1 has no direct connection to User B → message lost

Solution: Redis pub/sub as message broker
Server 1 → publish to Redis channel "user:B"
Server 2 → subscribed to "user:B" → receives it → delivers to User B

All servers subscribe. Any server can deliver to any user.
```

### 22.3 Presence System (Online/Offline)

```
On connect:     SET user:{id}:online "1" EX 30  (Redis, 30s TTL)
Heartbeat:      Client sends ping every 15s → server resets TTL
On disconnect:  Key expires naturally after 30s → user appears offline
Query:          GET user:{id}:online → null = offline
```

---

## 23. API Design Patterns

### 23.1 REST vs GraphQL vs gRPC

| | REST | GraphQL | gRPC |
|---|---|---|---|
| Protocol | HTTP/1.1 | HTTP/1.1 | HTTP/2 |
| Data format | JSON | JSON | Protocol Buffers (binary) |
| Fetching | Multiple endpoints, fixed responses | Single endpoint, client specifies fields | Defined service contracts |
| Over/under-fetching | Common problem | Solved by design | Solved by design |
| Performance | Good | Good (N+1 risk) | Excellent |
| Best for | Public APIs, CRUD, mobile | Complex frontends, multiple clients | Internal microservices, streaming |

### 23.2 REST Best Practices

```
Nouns not verbs:    /events not /getEvents
Plural resources:   /events not /event
HTTP verbs:         GET reads, POST creates, PUT/PATCH updates, DELETE removes
Nested resources:   /events/:id/backdrops
Versioning:         /v1/events — never break existing clients
Pagination:         all list endpoints paginated from day one
Consistent errors:  { "success": false, "error": { "code": "...", "message": "..." } }
Idempotency keys:   for POST requests that must not duplicate (payments)
```

### 23.3 Rate Limiting Algorithms

| Algorithm | How it works | Pros/Cons |
|---|---|---|
| Fixed window | Count requests in fixed time windows | Simple. Burst at window boundary — 2× limit possible |
| Sliding window log | Track timestamp of each request | Precise. High memory — stores all timestamps |
| Sliding window counter | Weighted combo of current + previous window | Good approximation. Low memory. Standard choice |
| Token bucket | Tokens added at fixed rate, consumed per request | Allows controlled bursts. AWS uses this |
| Leaky bucket | Requests queued, processed at fixed rate | Smooth output. Queue can fill under load |

---

## 24. Microservices vs Monolith

### 24.1 The Spectrum

```
Monolith → Modular Monolith → Microservices → Serverless Functions
```

| | Monolith | Microservices |
|---|---|---|
| Deployment | One unit | Each service independently |
| Scaling | Scale everything together | Scale bottleneck services only |
| Team size | Small teams | Multiple independent teams |
| Complexity | Simple operationally | Complex (networking, service discovery, tracing) |
| Data | Shared database | Each service owns its data |
| Failure | One failure can take everything down | Isolated failures |
| Best for | Early stage, small teams, MVPs | Large teams, mature products, different scaling needs |

**Start with a modular monolith.** Extract services when you have a concrete reason: a team needs to deploy independently, a service has genuinely different scaling needs, or a bounded context is truly separate. Premature microservices are the most common senior engineering mistake.

### 24.2 Service Communication

| Method | When to use | Trade-off |
|---|---|---|
| Synchronous REST/gRPC | Need immediate response | Tight coupling, latency adds up |
| Async messaging | Result not needed immediately | Loose coupling, harder to trace |
| Event streaming | Multiple consumers need same event | Complex infrastructure, powerful fan-out |

### 24.3 Service Mesh

Infrastructure layer handling service-to-service communication. Provides service discovery, load balancing, TLS, circuit breaking, and observability without changing application code. Examples: Istio, Linkerd.

---

## 25. Key Design Patterns

### 25.1 Saga Pattern — Distributed Transactions

When a transaction spans multiple services, you can't use a database transaction. Saga breaks it into local transactions with compensating transactions for rollback.

**Choreography saga (event-driven):**
```
1. TicketService: reserve ticket → emit "ticket.reserved"
2. PaymentService: charge card   → emit "payment.success"
3. TicketService: confirm ticket → emit "ticket.confirmed"

On failure: emit failure event → each service rolls back its own state
```

**Orchestration saga:**
```
Saga coordinator calls services in sequence
On failure: coordinator calls compensating transactions
```

### 25.2 CQRS — Command Query Responsibility Segregation

Separate read and write models.

```
Commands (writes) → Update write store
Queries  (reads)  → Read from optimised read store

Example: social feed
Write: user posts → saved to main DB
Read:  user loads feed → read from pre-computed feed cache
Feed computed asynchronously, optimised for reading
```

### 25.3 Event Sourcing

Store every state change as an immutable event instead of current state. Reconstruct state by replaying events.

```
Instead of: accounts table with current balance
Store events:
  AccountCreated  { userId, initialBalance: 0 }
  MoneyDeposited  { userId, amount: 1000 }
  MoneyWithdrawn  { userId, amount: 200 }

Current balance = replay all events = 800

Benefits: complete audit trail, replay history, debug by replaying
Costs: complex queries, event schema evolution, large storage
```

### 25.4 Consistent Hashing

Used in distributed caches and load balancers. When nodes are added/removed, only a fraction of keys need remapping.

```
Regular hashing: key % N servers
Add 1 server: nearly ALL keys remap → cache stampede

Consistent hashing:
Servers placed on a ring. Key maps to nearest server clockwise.
Add 1 server: only keys between new server and its predecessor remap.
Typically 1/N keys move — dramatically less disruption.

Used by: Cassandra, Dynamo, Memcached, Nginx
```

### 25.5 Two-Phase Commit (2PC)

```
Phase 1 (Prepare): coordinator asks all participants "can you commit?"
Phase 2 (Commit):  if all yes → commit. If any no → rollback all.

Problem: coordinator failure during phase 2 leaves participants uncertain.
Use Saga pattern for better failure handling.
```

### 25.6 Idempotency

An operation is idempotent if performing it multiple times has the same effect as performing it once.

```
GET requests are naturally idempotent.
DELETE requests should be idempotent.
POST requests are NOT by default — payment charged twice on retry.

Implementation:
Client generates unique idempotency key for each operation.
Server stores key + result.
On retry: return stored result without re-processing.

idempotency_key = UUID generated by client
Store: (key, result) in Redis with TTL or in DB
On request: check key exists → return stored result
            key not found → process → store result → return
```

---

## 26. Distributed Coordination and Heartbeat

### 26.1 The Problem

In a distributed system with N servers, how does each server know which others are alive? How do you elect a leader? How do you coordinate shared state?

### 26.2 Heartbeat Mechanism

Every server periodically sends a heartbeat (a small ping) to a central coordinator or to its peers. If a heartbeat is not received within a threshold, the server is assumed dead.

```
Periodic heartbeat:
  Server → coordinator: "I'm alive" every 5 seconds
  If coordinator doesn't hear from server in 15 seconds → server assumed down
  Coordinator redistributes server's tasks to healthy servers

Gossip protocol (peer-to-peer):
  Each server gossips health info to a few random peers
  Peer forwards to more peers
  Eventually all servers know about failures
  Used by: Cassandra, Consul, DynamoDB
```

### 26.3 Leader Election

Used when exactly one node must be responsible for something (primary database, partition leader, job scheduler).

**Approaches:**
- **ZooKeeper/etcd** — distributed coordination services with built-in leader election via ephemeral nodes. If the leader's process dies, its node disappears and a new election occurs.
- **Raft consensus** — all nodes vote, majority wins. Used by etcd, CockroachDB, Consul.
- **Bully algorithm** — node with highest ID becomes leader.

### 26.4 Distributed Locks

When multiple servers must not do the same operation simultaneously (processing the same job, sending the same notification):

```
Redis distributed lock (Redlock):
  SET lock:{resource} {uuid} NX EX 30
  NX = only set if Not eXists
  EX 30 = expire in 30 seconds (auto-release if process dies)

  If SET succeeds → you have the lock, proceed
  If SET fails    → another process has the lock, wait or skip

  Release:
  Only delete if the UUID matches yours (prevents releasing another's lock)
  Use Lua script for atomic check-and-delete
```

---

## 27. Distributed File Systems

### 27.1 What They Are

Distributed file systems store and serve files across multiple machines, appearing as a single filesystem to clients. Designed for scale (petabytes), high throughput, and fault tolerance.

### 27.2 Google File System (GFS) / HDFS

**Architecture:**
```
Client
  ↓
Master Node (metadata: file locations, chunk map)
  ↓ (where is this file?)
Chunk Servers (actual data, in 64MB–128MB chunks)

Files split into chunks. Each chunk replicated on 3 servers.
Master tracks which chunks are on which servers.
Client asks master for chunk locations, then reads directly from chunk servers.
```

**Key properties:**
- Optimised for large sequential reads and appends (not random access)
- Chunk replication for fault tolerance
- Master is the bottleneck — mitigated by caching chunk locations on client
- HDFS is the open-source implementation used by Hadoop

### 27.3 Modern Object Storage as Distributed FS

In practice, most systems use object storage (S3, GCS, MinIO) instead of HDFS. Object storage is simpler, more scalable, and managed. Use HDFS/GFS patterns only when you need the specific guarantees of a proper filesystem (random access, POSIX operations).

---

## 28. Full-Text Search at Scale

### 28.1 Why Databases Are Bad at Text Search

```
-- This query does a full table scan on every row:
SELECT * FROM posts WHERE body LIKE '%machine learning%';

-- Can't use a B-tree index for contains searches
-- Gets slower linearly as table grows
-- No relevance ranking
-- No stemming (learning ≠ learned ≠ learns)
```

### 28.2 How Search Engines Work

**Inverted index** — maps each word to all documents containing it.

```
"machine" → [doc1, doc3, doc7, doc42]
"learning" → [doc1, doc3, doc8, doc19]

Query "machine learning":
→ intersect both lists → [doc1, doc3]
→ rank by TF-IDF or BM25
→ return ranked results

Building:
Tokenise text → remove stop words → stem (learning→learn)
→ build inverted index → store
```

### 28.3 Elasticsearch Architecture

```
Index = collection of documents (like a database)
Shard = a Lucene index (horizontal partition of an index)
Replica = copy of a shard (for redundancy and read scaling)

Index with 5 shards, 1 replica = 10 total shards across cluster

Write: document → routed to primary shard → replicated
Read: query → fan out to all shards → merge results → rank
```

### 28.4 Search Sync Pattern

```
Write to PostgreSQL (source of truth)
     ↓ (async — via queue or CDC)
Index in Elasticsearch (search replica)

CDC (Change Data Capture): Debezium reads PostgreSQL WAL,
publishes change events, worker indexes in Elasticsearch.
Lag: typically < 1 second.
```

### 28.5 Trie for Autocomplete

```
Prefix tree for search suggestions:
root → a → af → afr → afri → afric → africa

Each node stores: prefix, top-N suggestions, frequency

Query "afr" → traverse to "afr" node → return stored suggestions
Pre-compute top 5 suggestions at each node (avoid traversal on query)
Shard by first character for scale
Update hourly via batch job over search logs
```

---

## 29. Notification Systems

### 29.1 Architecture

```
Event (like, follow, comment)
  → Notification Service
    → Notification DB (persist first — then queue)
    → Priority Queue
      → Workers by channel:
          Push worker  → FCM (Android) / APNs (iOS)
          Email worker → SendGrid / Resend
          SMS worker   → Twilio
```

### 29.2 Why Separate Queues Per Channel

- SMS is expensive → throttle separately
- Push is high volume → scale push workers independently
- Email has daily digests → batch processing

### 29.3 Delivery Guarantees

```
Persist notification to DB first, then enqueue.
If queue fails: re-enqueue from DB.
Worker: process → mark delivered in DB → acknowledge queue.
If worker crashes after processing but before ACK:
  message requeued → idempotency key prevents duplicate.

idempotency_key = hash(userId + eventId + channel)
```

### 29.4 User Preferences

Check before sending:
- Has user disabled push notifications?
- Has user set quiet hours?
- Has user unsubscribed from email?
- Is this notification type enabled for this channel?

Load preferences from Redis cache — checked on every notification.

---

## 30. Security Fundamentals

### 30.1 Authentication vs Authorisation

**Authentication** — who are you? (login, JWT verification)
**Authorisation** — what are you allowed to do? (permissions, ownership checks)

### 30.2 JWT Anatomy

```
Header.Payload.Signature
  ↓
eyJhbGc.eyJzdWIi.signature

Header:    { "alg": "HS256", "typ": "JWT" }
Payload:   { "sub": "userId", "exp": 1234567890, "role": "user" }
Signature: HMACSHA256(base64(header) + "." + base64(payload), secret)

Access token:  short-lived (15 min), stateless, sent on every request
Refresh token: long-lived (30 days), stored in Redis, used only to rotate tokens
```

### 30.3 Common Vulnerabilities

| Attack | Description | Prevention |
|---|---|---|
| SQL injection | Attacker injects SQL through user input | Parameterised queries, ORMs |
| XSS | Inject malicious scripts into pages | Escape output, Content Security Policy |
| CSRF | Trick browser into making requests | CSRF tokens, SameSite cookies |
| DDoS | Flood server with requests | Rate limiting, CDN, WAF |
| MITM | Intercept communications | HTTPS/TLS everywhere, HSTS |
| Broken access control | User accesses other users' data | Server-side ownership checks on every mutation |

### 30.4 Password Storage

```
Never: plaintext or MD5/SHA1 hashes
Avoid: bcrypt is fine but Argon2 is the modern standard
Always: slow adaptive hash (bcrypt, Argon2) with salt

Salt prevents rainbow table attacks.
Same password → different hash every time.
```

---

## 31. Big Data and Stream Processing

### 31.1 The Big Data Problem

When data volume exceeds what a single server can process in reasonable time, you need distributed computation. At billions of events per day, even simple aggregations require distributed systems.

### 31.2 Batch Processing (MapReduce / Spark)

```
Input Data (HDFS/S3)
  ↓ Map: split into key-value pairs
  ↓ Shuffle: group by key
  ↓ Reduce: aggregate per key
  ↓ Output (HDFS/S3)

Use for: daily aggregations, training ML models,
         large-scale ETL, historical analytics
Latency: minutes to hours (batch, not real-time)
```

### 31.3 Stream Processing (Kafka + Flink/Spark Streaming)

```
Events → Kafka (event stream)
            ↓
        Flink / Spark Streaming / Kafka Streams
        (continuous computation on event windows)
            ↓
        Output: real-time dashboards, alerts, aggregated DB

Use for: real-time analytics, fraud detection,
         live leaderboards, monitoring
Latency: milliseconds to seconds
```

### 31.4 Lambda Architecture

Combines batch and stream for full coverage:

```
Incoming Data
  ├── Batch layer:  process all historical data periodically (high accuracy)
  └── Speed layer:  process recent data in real-time (low latency, approximate)
                              ↓
                      Serving layer: merge batch + speed results

Use for: dashboards showing both historical trends and real-time current state
```

### 31.5 Data Warehouse vs Data Lake

| | Data Warehouse | Data Lake |
|---|---|---|
| Storage | Structured, schema-on-write | Raw, schema-on-read |
| Query | Fast (pre-structured) | Flexible (query raw data) |
| Cost | Higher | Lower |
| Examples | Snowflake, BigQuery, Redshift | S3 + Athena, Azure Data Lake |
| Best for | Business intelligence, known queries | Exploration, ML training data |

---

## 32. Production Infrastructure Patterns

### 32.1 Multi-Region Architecture

```
Region: US-East           Region: EU-West           Region: AP-Southeast
  Load Balancer             Load Balancer             Load Balancer
  API Servers               API Servers               API Servers
  PostgreSQL Primary ──────►PostgreSQL Replica ──────►PostgreSQL Replica
  Redis Cluster             Redis Cluster             Redis Cluster
  Object Storage            Object Storage            Object Storage (CDN)

Global DNS → Route users to nearest region
Active-Active: all regions serve traffic
Failover: if US-East goes down, DNS routes to EU-West
```

### 32.2 Infrastructure as Code (Terraform)

Define infrastructure in code. Version controlled, repeatable, auditable.

```
Database servers, load balancers, networking,
security groups, DNS records — all defined in .tf files.
Apply once → same infrastructure every time.
```

### 32.3 Container Orchestration (Kubernetes)

```
Node 1          Node 2          Node 3
Pod (API)       Pod (API)       Pod (Worker)
Pod (API)       Pod (Worker)    Pod (Worker)

Kubernetes handles:
- Scheduling pods across nodes
- Health checks and restart on failure
- Horizontal pod autoscaler (add pods under load)
- Rolling deployments (zero downtime)
- Service discovery
```

### 32.4 Observability — The Three Pillars

**Metrics** — numeric measurements over time. CPU, memory, request rate, error rate, latency. Use Prometheus + Grafana.

**Logs** — structured event records. Every request, error, significant action. Use ELK stack or Loki + Grafana.

**Traces** — distributed request traces. Follow a single request across multiple services. Use OpenTelemetry + Jaeger.

**The SLO/SLA/SLI triangle:**
```
SLI (Service Level Indicator) — the actual measurement
    e.g. 99th percentile API latency = 180ms

SLO (Service Level Objective) — the target
    e.g. 99th percentile latency < 200ms

SLA (Service Level Agreement) — contractual commitment
    e.g. "We guarantee 99.9% availability or credit is issued"
```

---

## 33. Classic Design: URL Shortener

**Requirements:** Given a long URL, return a short URL. Given a short URL, redirect to the long URL. 100M URLs created/day, 10B redirects/day.

### 33.1 Scale Estimates

```
Writes/sec: 100M / 86,400 ≈ 1,160 writes/sec
Reads/sec:  10B  / 86,400 ≈ 115,700 reads/sec (100× write-heavy on reads)
Storage:    100M × 500 bytes avg ≈ 50 GB/day
5-year:     50 GB × 365 × 5 ≈ 90 TB
Read:write = 100:1 → cache aggressively
```

### 33.2 Short URL Generation

**Option 1 — Hash + truncate:**
```
MD5(longUrl) → take first 7 chars
Problem: collisions — different long URLs can produce same short URL
Collision handling adds complexity
```

**Option 2 — Base62 encode auto-increment ID (recommended):**
```
DB auto-increments integer ID → encode in base62 (a-z A-Z 0-9)
ID 1 → "1", ID 1,000,000 → "4c92", ID 3.5 trillion → 7 chars
No collisions. Predictable length.
```

**Option 3 — Pre-generated keys:**
```
Background job pre-generates millions of unique 7-char strings.
Claim one on each URL creation.
Fast creation. No hashing/encoding at request time.
```

### 33.3 Architecture

```
Create:    POST /shorten → API Server → DB (store mapping) → return short code
Redirect:  GET /abc123  → API Server → Cache hit? → 301/302 redirect
                                     → Cache miss → DB → cache → redirect

Cache: Redis  key=short_code  value=long_url  TTL=24h
```

**301 vs 302:**
- 301 Permanent → browser caches, subsequent requests skip your server (lose analytics)
- 302 Temporary → every redirect hits your server (needed for analytics)

### 33.4 Schema

```sql
urls (
  id          BIGINT AUTO_INCREMENT,
  short_code  VARCHAR(7) UNIQUE,
  long_url    TEXT,
  user_id     BIGINT (nullable),
  created_at  TIMESTAMP,
  expires_at  TIMESTAMP (nullable)
)
```

---

## 34. Classic Design: Social Media Feed

**Problem:** When user A (1M followers) posts, show it in all followers' feeds. Two strategies: fan-out on write vs fan-out on read.

### 34.1 Fan-Out on Write (Push Model)

```
When user posts:
→ Save post to DB
→ For each of their N followers: write post ID to follower's feed cache

Pros: feed reads are O(1) — just read pre-built feed
Cons: celebrities with 1M followers → 1M writes on every post
```

### 34.2 Fan-Out on Read (Pull Model)

```
When user loads feed:
→ Fetch list of people they follow
→ Fetch recent posts from each
→ Merge and sort

Pros: posting is instant
Cons: reading is expensive — query all followed accounts
      User follows 5,000 people → 5,000 DB queries
```

### 34.3 Hybrid Approach (Twitter/Instagram)

```
Regular users (< 1M followers): fan-out on write
Celebrities (> 1M followers):   fan-out on read

When loading feed:
1. Read pre-built feed from cache (fan-out-write users)
2. Fetch recent posts from celebrities user follows
3. Merge both lists, sort by timestamp/score
4. Cache the merged result for a few minutes
```

### 34.4 Feed Ranking

```
Chronological:   sort by created_at DESC — simple, predictable
Algorithmic:     score = recency × engagement × relationship_strength
Score factors:   likes, comments, shares, time decay, author interaction history
```

---

## 35. Classic Design: Chat System

**Goal:** Design WhatsApp / Slack — real-time 1:1 and group messaging.

### 35.1 Architecture

```
Client A → WebSocket → Chat Server 1
                            ↕ Redis pub/sub
Client B → WebSocket → Chat Server 2

Message flow:
1. Client A sends message via WebSocket
2. Server saves to DB (async — don't block)
3. Server publishes to Redis channel for conversation
4. All servers subscribed to that channel receive it
5. Server with Client B's connection delivers it
6. Client B sends ACK → server marks as delivered
```

### 35.2 Message Storage

```sql
messages (
  id              BIGINT,         -- sequential: enables cursor pagination
  conversation_id UUID,
  sender_id       UUID,
  body            TEXT,
  created_at      TIMESTAMP,
  INDEX(conversation_id, id DESC)  -- paginate conversation history
)
```

For 1:1 chats: `conversation_id = sort_and_join(user_id_a, user_id_b)`.
For group chats: `conversation_id → group_id`.

### 35.3 Delivery States

```
Sent     → server received the message
Delivered → recipient's device received it (ACK from client)
Read     → recipient opened the conversation
```

### 35.4 Offline Messages

```
User is offline → server stores message in DB
When user reconnects → server pushes undelivered messages
Or: push notification (FCM/APNs) wakes the app
```

---

## 36. Classic Design: Rate Limiter

**Goal:** Limit each user to N requests per minute across all servers.

### 36.1 Where to Put It

```
Client → Rate Limiter → API Gateway → Services
Or: middleware inside each service
Or: at CDN/proxy layer (Cloudflare, Nginx)
```

### 36.2 Sliding Window Counter with Redis

```python
# For each request:
key = f"rate:{userId}:{current_minute}"
count = redis.INCR(key)
if count == 1:
    redis.EXPIRE(key, 60)   # set TTL on first request only
if count > limit:
    return 429 Too Many Requests

# Sliding window (more accurate):
current_count  = redis.GET(f"rate:{userId}:{current_minute}")
previous_count = redis.GET(f"rate:{userId}:{previous_minute}")
elapsed = seconds_elapsed_in_current_minute / 60
estimated = previous_count × (1 - elapsed) + current_count
if estimated > limit:
    return 429
```

### 36.3 Distributed Rate Limiting

```
Problem: each server has its own counter
Server 1 allows 100, Server 2 allows 100 = user gets 200 total

Fix: centralized counter in Redis
All servers read/write the same Redis key
Redis INCR is atomic — no race conditions
Use Lua scripts for compound operations (check + increment atomically)
```

---

## 37. Classic Design: Search Autocomplete

**Goal:** Return search suggestions as the user types.

### 37.1 Trie Data Structure

```
root
  ├── a
  │   └── am
  │       ├── amazon (count: 10M)
  │       └── amc (count: 500K)
  └── ne
      ├── netflix (count: 8M)
      └── new (count: 5M)

Each node: prefix, top-5 suggestions, frequency
Query "ne" → traverse → return ["netflix", "new york", "news", "nextvibe", "neymar"]
Pre-compute top 5 at each node to avoid traversal at query time
```

### 37.2 Scale Considerations

```
Trie lives in memory — fast but single-server limited
For scale: shard by first character (a-f → shard 1, g-m → shard 2)

Update strategy:
  Real-time: too slow — every search modifies the trie
  Better: batch update every hour using map-reduce over search logs
  Hourly: aggregate counts, rebuild affected nodes, deploy new trie

Caching:
  Top ~10,000 prefixes drive 80% of queries
  Cache suggestions per prefix in Redis, TTL 1 hour
```

---

## 38. Classic Design: Notification System

**Goal:** Send push, email, and SMS notifications reliably at scale.

See Section 29 for detailed architecture. Key points:

- **Persist first, queue second** — if queue goes down, re-enqueue from DB
- **Separate queues per channel** — different throttle, cost, and scale requirements
- **Idempotency key** — `hash(userId + eventId + channel)` prevents duplicates on retry
- **User preferences** — load from Redis cache, check before every send
- **Exponential backoff** — retry with increasing delay (1s, 2s, 4s, 8s, max 32s)

---

## 39. Real-World: Design YouTube

### 39.1 Scale (2026 reference)

```
2.7B monthly active users
500 hours of video uploaded per minute
1B+ hours watched per day
```

### 39.2 Core Requirements

**Functional:** Upload video, stream video, search, comments, likes, subscriptions, recommendations.
**Non-functional:** High availability, low latency streaming, eventual consistency on counts is fine.

### 39.3 Video Upload Flow

```
Client → Upload Service → Raw Video Storage (S3)
                       → Transcoding Queue
                       → Transcoding Workers:
                           → Multiple resolutions (360p, 720p, 1080p, 4K)
                           → Multiple formats (MP4/H.264, WebM/VP9)
                           → Thumbnail generation
                       → CDN (upload processed video)
                       → Update DB (video metadata, CDN URLs)
                       → Notify uploader
```

**Why transcode to multiple resolutions?**
- Adaptive bitrate streaming (ABR) — player switches quality based on bandwidth
- 4K for desktop, 720p for mobile on 4G, 360p for slow connections
- Reduces buffering significantly

### 39.4 Video Streaming Flow

```
Client → CDN (edge node near user)
       → Cache hit: serve video chunks directly
       → Cache miss: fetch from origin (S3) → cache at edge → serve

HLS (HTTP Live Streaming):
  Video split into 10-second chunks (.ts files)
  Manifest file (.m3u8) lists available qualities and chunk URLs
  Player downloads manifest → picks quality → downloads chunks
  Adapts quality mid-stream based on bandwidth measurements
```

### 39.5 Database Design

```
metadata DB (MySQL/PostgreSQL):
  videos (id, user_id, title, description, duration, status, created_at)
  video_urls (video_id, quality, cdn_url, format)

search (Elasticsearch):
  video_id, title, description, tags, transcript

counts (eventually consistent):
  views, likes — updated async via Kafka
  store in Redis for fast reads, flush to DB periodically

recommendations:
  ML model trained on watch history, interactions
  Pre-compute recommendations per user, store in Cassandra
  Real-time signals (just watched X) → adjust ranking
```

### 39.6 Key Decisions

- **CDN is mandatory** — video can't be served from origin at this scale
- **Transcoding is async** — API returns immediately, video appears after processing
- **View counts are approximate** — exact consistency on view count is not worth the cost
- **Search via Elasticsearch** — full-text on title, description, tags
- **Recommendations are ML-driven** — matrix factorisation or two-tower model

---

## 40. Real-World: Design Netflix

### 40.1 Scale

```
230M+ subscribers in 190 countries
~15% of global internet bandwidth (peak)
Content library: 36,000+ hours
```

### 40.2 Architecture Layers

**Content ingestion pipeline:**
```
Studio delivers master files (4K uncompressed, 100s of GBs)
→ Ingest servers
→ Transcode to 2,200+ encodings (resolution × bitrate × codec × device)
→ Quality validation
→ Push to S3 (origin)
→ Push to Open Connect Appliances (OCA — Netflix's own CDN)
```

**Open Connect (Netflix's CDN):**
```
Netflix operates their own CDN — 17,000+ servers in 1,000+ ISP locations.
ISPs host Netflix servers for free in exchange for free bandwidth.
User requests → routed to nearest OCA server.
ISP benefits: less bandwidth out of their network.
Netflix benefits: ultra-low latency, no third-party CDN costs.
```

**Playback flow:**
```
Client opens Netflix
  → Load service (catalog, personalized rows)
  → User selects content
  → License service (DRM — Widevine/PlayReady/FairPlay)
  → Steering service (which OCA server to use)
  → Stream from OCA via HTTPS
```

### 40.3 Personalization

```
Two-tower neural network:
  User tower:    embeddings of watch history, ratings, demographics
  Content tower: embeddings of genre, cast, description, visual features

Cosine similarity → ranking score

Pre-compute recommendations nightly for all users (batch)
Real-time signals (just started watching thriller) → adjust live
A/B test thumbnails — Netflix shows different thumbnails to different users
  and picks whichever gets clicked more
```

### 40.4 Chaos Engineering

Netflix's famous resilience approach — deliberately inject failures in production to find weaknesses before real failures do.

```
Chaos Monkey: randomly kills production services
Chaos Kong:   kills an entire AWS region
Latency Monkey: adds artificial latency to service calls

Philosophy: "The best way to avoid failure is to fail constantly."
Every service must be designed to degrade gracefully.
```

---

## 41. Real-World: Design Facebook

### 41.1 Scale

```
3B+ monthly active users
100B+ messages per day (Messenger)
350M+ photos uploaded per day
```

### 41.2 News Feed — The Hardest Part

Facebook's newsfeed is the most complex at-scale feed problem. You have friends, groups, pages, ads, and multiple content types all competing for ranking.

```
Fan-out: Facebook uses fan-out on write for regular users,
         fan-out on read for pages with millions of followers.

Ranking:
  EdgeRank (original algorithm):
    Score = affinity × weight × decay
    affinity:  how much you've interacted with this person
    weight:    content type (video > photo > link > status)
    decay:     how old the content is

  Modern: deep learning model with 100,000+ features
  Inputs: engagement history, content type, recency, relationship closeness
  Output: probability you'll engage with each candidate post
```

### 41.3 Messenger Architecture

```
Scale: 100B messages/day = 1.16M messages/second

Storage: MySQL + Cassandra
  MySQL: conversation metadata, contacts
  Cassandra: message storage (append-only, time-series, massive write throughput)

Message ID: use Snowflake-style IDs (time-based + worker ID + sequence)
  Enables time-ordering without a timestamp sort
  Enables cursor-based pagination efficiently
```

### 41.4 Photo Storage (Haystack)

Facebook built Haystack specifically for storing billions of small photos efficiently:

```
Problem with regular filesystems:
  Each photo = a file = filesystem metadata overhead
  At billions of photos: metadata I/O becomes the bottleneck
  Disk seek to metadata + disk seek to data = 2 seeks per photo read

Haystack solution:
  Pack many photos into one large "haystack" file
  Maintain index in memory (photo_id → offset in haystack file)
  One disk seek to the offset → read photo data
  Dramatically fewer filesystem metadata operations

Modern equivalent: Most systems just use S3 with a database table
  mapping (photo_id → s3_key). S3 handles the storage problem.
```

### 41.5 Social Graph

```
6B friendship edges (bidirectional)
Who knows whom? Who are mutual friends?

TAO (The Associations and Objects):
  Facebook's distributed graph data store
  Objects: users, photos, videos, comments
  Associations: likes, friendships, tags

Built on MySQL with a caching layer
Replicated to multiple datacenters
Read-heavy: cache aggressively (Memcached)
```

---

*Last updated: 2026 — Built from first principles, real-world architectures, and systems engineering practice.*
