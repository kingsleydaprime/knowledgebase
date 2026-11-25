---
id: 3b58cbb8-b8bf-4dd0-a5d4-9e15834ea17b
---

# Load and Performance Testing

Load testing means sending a backend many requests at once, the way real users would, to see how it copes. Some bugs only show up when lots of people use an app at the same time, like a ticket site on the day a big concert goes on sale. Normal tests with one user at a time will never find them.

## 1. Why Load Testing Is Different from Functional Testing
<!-- bite: 2963efa2-5e2a-441a-be48-29dc2f017608 -->

A unit or integration test executes in near-total isolation. The database connection pool has exactly one query queued. Memory usage is flat. CPU cores are mostly idle. Caches are warm or mock-controlled.

In production under concurrency, an entirely different class of bugs emerges:
- **Connection pool starvation**: All database pool connections are reserved; subsequent queries queue until HTTP timeouts fire.
- **Lock contention and deadlocks**: Two transactions simultaneously update related rows or insert colliding values across foreign keys.
- **Memory leaks**: Retained object allocations across requests compound rapidly under continuous throughput.
- **Event loop blocking (Node.js)**: Synchronous JSON serialization, cryptographic hashing (bcrypt/argon2), or unbounded regex backtracking stall all concurrent connections.
- **Cache stampedes**: An expired cache key causes 500 requests to hit the database for the exact same expensive calculation at the same millisecond.

Load testing stresses these shared resources so you discover your breaking points before users find them for you.

---

## 2. Types of Performance Tests
<!-- bite: 19661ea9-31fd-465c-bd79-18fc5aa688ca -->

| Type | Shape & Duration | What It Answers |
|---|---|---|
| **Smoke Test** | Minimal load (1–2 VUs, ~1 min) | Does the test script run without errors? Are endpoints answering? |
| **Load Test** | Expected peak traffic, sustained (e.g., 50–200 VUs for 10–30 min) | Can the system comfortably maintain SLAs under standard peak conditions? |
| **Stress Test** | Incremental ramp beyond expected peak until degradation | What is the upper breaking point, and how does the system fail (graceful 429/503 vs crash)? |
| **Spike Test** | Sudden, aggressive jump from 0 to peak within seconds | Can auto-scaling, thread pools, or rate limiters absorb sudden viral traffic bursts? |
| **Soak (Endurance) Test** | Moderate load held for hours (e.g. 4–12 hours) | Are there slow memory leaks, socket leaks, or unclosed DB connection pools? |
| **Breakpoint Test** | Continuous ramp with no ceiling until catastrophic failure | What is the absolute hardware/architecture ceiling? |

---

## 3. Tool Landscape
<!-- bite: 2692fe73-98d8-441b-8c2c-f80823d64622 -->

| Tool | Language | Best For | Trade-offs |
|---|---|---|---|
| **[k6](https://k6.io/)** (Grafana) | JavaScript / TypeScript | Modern dev workflows, HTTP, WebSocket, gRPC | Standard choice for JS/TS engineering teams; CLI-first; minimal resource footprint. |
| **Artillery** | YAML / JavaScript | HTTP & Socket.IO | Excellent built-in Socket.IO engine; very declarative. |
| **Locust** | Python | Complex user flow scripting in Python | Excellent live web UI, slightly higher resource usage per worker. |
| **autocannon** | Node.js | Micro-benchmarking single endpoints | Fast and zero-setup, but lacks multi-step scenarios or session pooling. |
| **JMeter** | Java / GUI | Enterprise legacy stacks | Feature-heavy, but heavy GUI-based test creation and steep learning curve. |

**Recommendation for modern web stacks**: **k6**. The tests are written in JavaScript, execution is handled by an ultra-fast Go runtime, and metrics/thresholds can be directly evaluated in CI pipelines.

---

## 4. Key Metrics: Why Averages Lie
<!-- bite: f8da8872-abf2-4e60-8c3c-c1b5ccdb11f1 -->

When reviewing performance test outputs, the single most dangerous metric is **Average Latency**.

If 99 users get a 20ms response and 1 user waits 10 seconds, the average is ~120ms. The average looks acceptable, but 1% of your user base suffered a terrible timeout.

Always measure percentile distributions:
- **p50 (Median)**: What normal traffic experiences.
- **p90 / p95**: What users experience during moderate load bursts.
- **p99**: The tail latency. Catches garbage collection pauses, connection pool queueing, and lock waits.

### The Throughput vs Latency Inflection Point
As concurrent virtual users (VUs) ramp up:
1. **Linear phase**: Throughput (requests/sec) scales up while latency remains flat.
2. **Saturation phase**: Throughput plateaus. The system has reached max capacity (CPU, DB pool, or I/O bottleneck).
3. **Cliff phase**: Throughput degrades or errors rise, while latency spikes exponentially due to queueing.

Your real operating capacity is just before the saturation point.

---

## 5. Anatomy of a k6 Load Test
<!-- bite: c87b1480-a113-4b3c-9c0f-6af226eafdd2 -->

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

// 1. Test configuration & pass/fail thresholds
export const options = {
  stages: [
    { duration: '1m', target: 50 },  // Ramp-up to 50 virtual users
    { duration: '3m', target: 50 },  // Hold sustained load
    { duration: '1m', target: 0 },   // Graceful ramp-down
  ],
  thresholds: {
    // 95% of requests must complete in under 400ms
    http_req_duration: ['p(95)<400'],
    // Less than 1% failed HTTP responses
    http_req_failed: ['rate<0.01'],
  },
};

// 2. Virtual User execution loop
export default function () {
  const res = http.get('http://localhost:3000/v1/events');

  // Assertions
  check(res, {
    'status is 200': (r) => r.status === 200,
    'latency under 400ms': (r) => r.timings.duration < 400,
  });

  // Think time: real humans pause between interactions
  sleep(1);
}
```

- **`options.stages`**: Controls the load curve (ramp up, hold, ramp down).
- **`thresholds`**: Pass/fail gates. If a threshold fails, k6 exits with a non-zero exit code (great for CI).
- **`check`**: Validates status codes or response bodies without aborting the run.
- **`sleep` (Think Time)**: Without pacing, a single virtual user fires continuous requests at network line-speed, distorting real-world server load.

---

## 6. The Auth Token Pooling Pattern
<!-- bite: 6f4bb453-4278-4091-8521-f134531e5ef1 -->

Do **not** place password authentication inside your default execution loop during a load test.

Why?
1. Password hashing (argon2, bcrypt) is intentionally CPU-intensive. A few login requests will consume 100% server CPU before your business logic is ever stressed.
2. Rate limiters often restrict login endpoints to 3–10 requests per minute.
3. You are testing your core API features, not the hashing algorithm.

### The Pattern: Pre-authenticate in `setup()`
k6 runs `setup()` once before starting virtual users. Pre-fetch tokens and pass them to the execution functions:

```javascript
import http from 'k6/http';

export function setup() {
  const tokens = [];
  // Authenticate a fixed pool of pre-seeded test accounts
  for (let i = 1; i <= 20; i++) {
    const res = http.post('http://localhost:3000/v1/auth/login', JSON.stringify({
      email: `loadtest_user_${i}@example.com`,
      password: 'TestPassword123!',
    }), {
      headers: { 'Content-Type': 'application/json' },
    });

    if (res.status === 200) {
      tokens.push(res.json('data.accessToken'));
    }
  }
  return { tokens };
}

export default function (data) {
  // Rotate tokens across virtual users
  const token = data.tokens[__VU % data.tokens.length];

  http.get('http://localhost:3000/v1/events', {
    headers: { Authorization: `Bearer ${token}` },
  });
}
```

---

## 7. Rate Limiting in Load Tests
<!-- bite: 6166abbd-344c-4a6a-847c-e4f592ce6b64 -->

Production backends use rate limiters (`@nestjs/throttler`, redis-based token buckets, or Cloudflare/Nginx limits). In a load test, these trigger `429 Too Many Requests` almost immediately.

Approaches:
1. **Test Environment Bypass (Recommended for internal load testing)**: Disable or raise thresholds when `NODE_ENV=test` or `LOAD_TEST=true`.
2. **Header Bypass**: Allow a secret header (e.g. `x-load-test-bypass: <secret>`) checked by the guard or middleware.
3. **Limiter Validation**: When specifically verifying that rate limiting works, test with small concurrency aimed directly at the throttle threshold.

---

## 8. What Breaks Under Concurrency
<!-- bite: 0a0b5d07-0c08-422b-92a9-51a9ce69ecf7 -->

1. **Database Connection Pool Exhaustion**: Most ORMs (Prisma, TypeORM) configure small connection pools by default (e.g., 5–10). Under 100 concurrent requests, 90+ queries wait in a software queue.
2. **Missing Indexes on Filter/Join Columns**: Fast on 50 records in local development; under load, sequential table scans freeze the database engine.
3. **N+1 Query Cascades**: Fetching a list of 20 items causes 21 database round trips. Under 100 requests/sec, that becomes 2,100 DB queries/sec.
4. **Unbounded Result Sets**: Endpoints that omit `LIMIT` / `take` will exhaust Node.js memory as table row counts grow.
5. **Node.js Single-Thread Event Loop Blocking**: CPU-bound tasks in the main thread (crypto, large file compression, large JSON parsing) freeze all concurrent HTTP requests.

---

## Related
<!-- bite: 4c3bb3e1-9b6d-403f-871a-a26361b84742 -->
- [[backend/07-practices/02-testing-a-backend|Testing a Backend]] — unit, integration, and E2E mechanics
- [[backend/06-cross-cutting/04-rate-limiting|Rate Limiting]] — token bucket and sliding window algorithms
- [[architecture/index|System Architecture]] — scaling, caching, and database read replicas

## Seen in the wild
<!-- bite: 361ccb88-182c-42ca-871c-1e03c6265f01 -->
- NextVibe — Backend Load Testing — real-world load testing of NestJS, Prisma, and Socket.IO
- NextVibe — Frontend Testing — testing Redux, RTK Query, and component validation

## About this lesson
<!-- bite: c9ba9b60-d258-4737-916c-e96c34fb1893 -->

**Level:** Intermediate. **Covers:** assumes [[backend/07-practices/02-testing-a-backend|Testing a Backend]] for unit, integration, and E2E mechanics. While functional testing asks *"does this code return the right answer for one user?"*, load testing asks *"does this system survive when 500 users do it simultaneously?"*
