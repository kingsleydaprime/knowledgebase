# NextVibe — Backend Load Testing & Concurrency

Split out from the load testing analysis on 2026-10-13. See also
`learning/backend/01-core.md` through `learning/backend/08-payments-and-webhooks.md`
for the rest of the backend implementation notes, and the general reference at
[[backend/07-practices/03-load-and-performance-testing|Load & Performance Testing]].

---

## 1. Why NextVibe Needs Load Testing

NextVibe is a live event and social ticketing platform. Unlike steady-state enterprise software, event traffic is **inherently spiky**:
- A popular creator drops tickets or an RSVP link.
- Hundreds of users open the app simultaneously to view details, claim tickets, and join event group chats.
- Write operations concentrate on the same database rows (`Event`, `Rsvp`, `TicketTier`).

Concurrency bugs in NextVibe show up in three distinct areas:
1. **Contention on RSVP and Ticket Inventory**: Multiple transactions attempting to check capacity and write RSVPs or decrement ticket inventory concurrently.
2. **Prisma Connection Exhaustion**: Event feeds querying nested relations (organizers, vibe tags, media assets) saturating Postgres connections.
3. **Socket.IO Messaging Fan-out**: Chat rooms broadcasting messages and typing events across connected sockets.

---

## 2. Choosing k6 for NextVibe

**k6** is the ideal testing harness for this stack:
- **Language consistency**: Scripts are written in JavaScript/TypeScript, matching the team's stack.
- **Protocol coverage**: Native support for HTTP REST routes and WebSocket transports.
- **Low overhead**: Single binary written in Go; easily generates high concurrency from a single machine without distorting measurements.

### Installing k6
```bash
# Ubuntu / Debian
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update && sudo apt-get install k6

# macOS
brew install k6
```

---

## 3. NextVibe's Key Pressure Points

| Route / System | Type | What Breaks Under Concurrency |
|---|---|---|
| `GET /v1/events` | Read (Public) | Deep relation joins (`include: { tags, organizer }`) causing heavy database scans. |
| `GET /v1/events/:id` | Read (Authenticated) | Checks whether the requesting user has already RSVP'd or holds a ticket. |
| `POST /v1/events/:id/rsvp` | Write (High contention) | Unique constraint race conditions on `(userId, eventId)` and concurrent capacity limits. |
| `POST /v1/auth/login` | CPU-bound | Password verification uses `argon2`. High concurrent logins will peg the server CPU at 100%. |
| Socket.IO `/messaging` | WebSocket | Memory consumption per open socket connection and message broadcast fan-out. |

---

## 4. The Auth & Rate-Limiting Challenge

NextVibe guards routes with `@nestjs/throttler` (defined in `src/modules/auth/auth.controller.ts`):
- `POST /v1/auth/login`: Limited to **5 requests per minute** per IP.
- `POST /v1/auth/register`: Limited to **20 requests per 5 minutes**.

### Why You Cannot Run Login Inside Virtual Users
1. **Throttler lockouts**: The first 5 requests succeed; the remaining 495 fail immediately with `429 Too Many Requests`.
2. **CPU starvation**: NextVibe uses argon2 hashing (`"argon2": "^0.44.0"`). Each argon2 verification deliberately consumes hundreds of milliseconds of CPU time to thwart brute-force attacks. Hashing during a load test tests argon2 rather than your business logic.

### Solution: Database Seeding & Token Pooling
1. **Seed test users directly into PostgreSQL** with pre-computed password hashes.
2. In k6's `setup()` function, authenticate 20–50 users once to obtain JWT tokens.
3. Pass the token pool to virtual users, which cycle through them using `__VU % tokens.length`.
4. Bypass or increase `@nestjs/throttler` limits in your local testing environment:
```typescript
// Example: disable in test/loadtest environments in AppModule
ThrottlerModule.forRootAsync({
  inject: [ConfigService],
  useFactory: (config: ConfigService) => ({
    throttlers: [{
      ttl: 60000,
      limit: config.get('NODE_ENV') === 'loadtest' ? 100000 : 10,
    }],
  }),
})
```

---

## 5. Prisma Connection Pool Configuration

Prisma manages its own connection pool to PostgreSQL. By default, Prisma sets the pool size to:
$$\text{num\_physical\_cpus} \times 2 + 1$$

On a standard 4-core machine, this defaults to **9 connections**.

Under 50 concurrent requests, 41 requests are queued inside Prisma waiting for an available database socket. When query durations exceed the pool timeout, requests fail with:
`Timed out fetching a new connection from the connection pool`.

### Tuning the Pool Size
Set `connection_limit` and `pool_timeout` directly in `DATABASE_URL`:
```env
DATABASE_URL="postgresql://postgres:password@localhost:5432/nextvibe?connection_limit=25&pool_timeout=15"
```
Ensure Postgres's global `max_connections` (in `postgresql.conf` or Docker container) is greater than:
$$\text{connection\_limit} \times \text{number of backend app instances}$$

---

## 6. Complete k6 NextVibe Test Script

Save as `loadtest/events-flow.js`:

```javascript
import http from 'k6/http';
import { check, sleep, group } from 'k6';

const BASE_URL = 'http://localhost:3000/v1';

export const options = {
  stages: [
    { duration: '30s', target: 20 }, // Ramp up to 20 virtual users
    { duration: '2m',  target: 20 }, // Sustained load
    { duration: '30s', target: 0 },  // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<450'], // 95% of requests under 450ms
    http_req_failed: ['rate<0.02'],   // Under 2% failure rate
  },
};

export function setup() {
  const tokens = [];
  // Assumes users test1@example.com through test10@example.com exist
  for (let i = 1; i <= 10; i++) {
    const res = http.post(`${BASE_URL}/auth/login`, JSON.stringify({
      email: `test${i}@example.com`,
      password: 'Password123!',
    }), {
      headers: { 'Content-Type': 'application/json' },
    });

    if (res.status === 200) {
      const body = JSON.parse(res.body);
      tokens.push(body.data.accessToken);
    }
  }

  // Fetch a valid event ID to target during the test
  const eventsRes = http.get(`${BASE_URL}/events?page=1&limit=5`);
  const events = JSON.parse(eventsRes.body).data || [];
  const targetEventId = events.length > 0 ? events[0].id : null;

  return { tokens, targetEventId };
}

export default function (data) {
  // Distribute tokens among VUs
  const token = data.tokens.length > 0
    ? data.tokens[__VU % data.tokens.length]
    : null;

  const authHeaders = {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  };

  group('Browse Event Feed', () => {
    const res = http.get(`${BASE_URL}/events?page=1&limit=10`);
    check(res, {
      'events feed is 200': (r) => r.status === 200,
      'events list has data': (r) => JSON.parse(r.body).data !== undefined,
    });
    sleep(1);
  });

  if (data.targetEventId) {
    group('View Event Details', () => {
      const res = http.get(`${BASE_URL}/events/${data.targetEventId}`, authHeaders);
      check(res, {
        'event detail is 200': (r) => r.status === 200,
      });
      sleep(2);
    });

    group('RSVP to Event', () => {
      const res = http.post(`${BASE_URL}/events/${data.targetEventId}/rsvp`, null, authHeaders);
      check(res, {
        'rsvp succeeded or already rsvp-ed': (r) => r.status === 201 || r.status === 400,
      });
      sleep(1);
    });
  }
}
```

---

## 7. Metrics to Monitor During Execution

While running `k6 run loadtest/events-flow.js`, monitor the local stack:

1. **Database Connections**:
```bash
# Check active Postgres connections
docker exec -it nextvibe_db psql -U postgres -d nextvibe -c "SELECT count(*) FROM pg_stat_activity WHERE datname = 'nextvibe';"
```

2. **Container CPU & Memory**:
```bash
docker stats nextvibe_db nextvibe_redis nextvibe_storage
```

3. **Node.js Process Metrics**:
Watch for memory climbing continuously without dropping after load drops, which signals event listener or cache leaks.

---

## Related
- [[backend/07-practices/03-load-and-performance-testing|Load & Performance Testing (General)]]
- [[projects/nextvibe/learning/backend/01-core|01 — Backend Core & Architecture]]
- [[projects/nextvibe/learning/09-devops|09 — DevOps, Docker & Infrastructure]]
- [[projects/nextvibe/learning/frontend/13-testing|13 — Frontend Testing]]
