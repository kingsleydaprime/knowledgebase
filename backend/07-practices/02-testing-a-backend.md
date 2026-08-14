# Testing a Backend

**[Intermediate]** — assumes [[concepts/04-best-practices/04-testing-fundamentals|Testing Fundamentals]] for the pyramid and TDD. This note is only the part that's *specific to a backend*: the database, the I/O boundaries, test data, and why backend suites go flaky.

## The kid version first

A pure function is easy to test: give it 2, expect 4. A backend is not a pure function. It talks to a database, a clock, a payment provider, a queue, and three other services — and **the bugs you actually ship live in exactly those conversations**, not in the arithmetic between them.

So backend testing is mostly one question: *for each thing my code talks to, do I use the real one, a fake one, or nothing at all?* Get that decision right and the suite is fast and trustworthy. Get it wrong and you either test nothing real or you build something so slow nobody runs it.

## What to use the real thing for

The single highest-value rule in backend testing:

> **Use a real database. Fake everything you don't own.**

| Dependency | Use | Why |
|---|---|---|
| **Your database** | **Real one**, in a container | The bugs are dialect-, constraint-, transaction- and index-specific. An in-memory substitute has none of those |
| **Your cache/queue** | Real one, containerised | Same reason, less acutely. Redis/Kafka semantics don't survive a hand-written fake |
| **Third-party HTTP APIs** | Fake at the HTTP boundary | You don't control them, you can't rate-limit-proof them, and you don't want your CI failing because Stripe is slow |
| **Time** | Injected, controllable | See below — the biggest silent source of flakiness |
| **Randomness / UUIDs** | Injected, seedable | Same |
| **Email/SMS/push** | Fake, and assert what was sent | Sending real email from tests is a career-defining mistake exactly once |
| **Your own other services** | Contract tests, not live calls | An integration suite that spins up five services tests your docker-compose file more than your code |

The in-memory-database shortcut (H2 standing in for Postgres, SQLite standing in for MySQL) is the classic false economy. It's fast and it's green, and it cannot catch a `ON CONFLICT` clause that Postgres accepts and H2 doesn't, a case-sensitivity difference, a JSONB query, a partial index, or any isolation-level behaviour. You get a suite that passes while production breaks — the worst possible outcome, because it's actively misleading.

## Testcontainers — the real database, disposably

This is the tool that makes "use a real database" practical, and it's the one the vault has been recommending without showing. It starts a throwaway container for the test run and gives you its connection URL.

```ts
// Node — one Postgres for the whole suite
import { PostgreSqlContainer } from "@testcontainers/postgresql";

let container, db;

beforeAll(async () => {
  container = await new PostgreSqlContainer("postgres:16-alpine").start();
  db = createPool({ connectionString: container.getConnectionUri() });
  await runMigrations(db);          // your real migrations, not a hand-written schema
}, 60_000);                          // first run pulls the image — give it room

afterAll(async () => {
  await db.end();
  await container.stop();
});
```

```java
// Java/Spring — the same idea
@Testcontainers
@SpringBootTest
class OrderRepositoryTest {
  @Container
  @ServiceConnection                 // Spring Boot 3.1+ wires the datasource automatically
  static PostgreSQLContainer<?> pg = new PostgreSQLContainer<>("postgres:16-alpine");
}
```

Two details that matter more than they look:

- **Run your real migrations against it.** If tests build their schema separately, you stop testing your migrations — and a broken migration is a production outage, not a test failure.
- **Start the container once per suite, not per test.** Per-test containers turn a 20-second suite into a 10-minute one, and a suite nobody runs has no value.

## Test data — isolation without a fresh database

If tests share a database (they should, for speed), each one must not see another's rows. Three strategies:

| Strategy | How | Cost |
|---|---|---|
| **Transaction rollback** | Open a transaction per test, roll back at the end | Fastest. Breaks if the code under test manages its own transactions or commits |
| **Truncate between tests** | `TRUNCATE` the tables afterwards | Simple, robust, moderately fast. The sane default |
| **Fresh schema per test** | New schema/database each time | Slowest, most isolated. For the rare test that needs it |

Build rows with **factories, not fixtures** — a function that creates a valid entity with sensible defaults and lets each test override only the field it cares about:

```ts
const user = await makeUser({ email: "x@y.com" });        // everything else defaulted
const order = await makeOrder({ userId: user.id, total: 0 });   // the case under test
```

A shared `fixtures.sql` starts out convenient and becomes a file nobody dares change, because forty tests depend on user #3 having exactly two orders. The factory version keeps each test's intent visible in the test.

## Time, and the tests that fail at midnight

Anything reading the clock directly is a latent flake. `expiresAt: new Date(Date.now() + 3600_000)` passes all day and fails in the CI run that straddles a DST boundary, and a test asserting "created today" fails for whoever runs it at 23:59.

Inject a clock, or use your framework's fake timers. Then you can also *test* the interesting cases — what happens when the token has expired, when the subscription lapses, when the retry window closes — which is otherwise nearly impossible.

The same applies to anything that generates ordering: `ORDER BY created_at` with rows created in the same millisecond returns an arbitrary order, which passes locally and fails on faster CI hardware. Order by something total.

## What to test at each layer

- **Unit** — pure domain logic: pricing rules, state machines, validation, permission checks. Fast, no I/O. This is where [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture|hexagonal architecture]] pays off — the more logic sits behind ports, the more of it is unit-testable.
- **Integration** — a repository against the real database, a service against real collaborators. The layer that catches the most real bugs per unit of effort in a typical backend.
- **API/E2E** — drive the actual HTTP endpoint: request in, status and body out, database in the expected state. Cover the main path of each endpoint plus its auth failures. Keep the count low; these are the slow, brittle ones.
- **Contract** — if other services call you, assert the shape of what you return, so you learn you've broken them before they do.

**Test through the public entry point wherever you can.** A test that calls the HTTP route survives a refactor that reshuffles your service layer; a test that pokes at a private method breaks the moment you rename something, which trains people to delete tests during refactors.

## Auth is the thing people skip

Every endpoint has at least three cases, and most suites only test the first:

1. Authenticated and permitted → works
2. **Not authenticated → 401**
3. **Authenticated as the wrong user → 403, and no data leaked in the error body**

Case 3 is where [[backend/05-auth/README|broken object-level authorization]] lives — the most common serious API vulnerability there is, and it's trivially testable: create two users, have one request the other's resource, assert it fails. If you write one new kind of test after this note, write that one.

## Why backend suites go flaky

In rough order of frequency:

- **Shared state between tests** — a row, a cache entry, a module-level singleton. Symptom: passes alone, fails in the suite, or fails only in a particular order. Run your suite in random order to flush these out.
- **Real time** — see above.
- **Async work not awaited** — the assertion runs before the background job finishes. Symptom: fails only on slow or loaded CI.
- **Ports and parallelism** — two suites binding the same port. Let the container assign one.
- **Network** — any test that reaches the real internet will eventually fail for reasons that have nothing to do with your code.

A flaky test is worse than no test, because it teaches the team to re-run CI without reading the failure. Fix it or delete it — quarantining it "for now" means forever.

## What not to test

Framework behaviour (your ORM can save a row), getters and setters, third-party libraries, and generated code. Coverage percentage is a diagnostic, not a target — the moment it becomes a target, people write tests that execute lines without asserting anything, and the number goes up while the safety net goes down.

## Key insight

Backend testing comes down to one decision repeated: real, faked, or ignored. Use a real database in a container against your real migrations, fake everything you don't own, inject the clock, and make every test build its own data. Almost every slow, flaky, or falsely-green backend suite is one of those four choices made wrong.

## Related
- [[concepts/04-best-practices/04-testing-fundamentals|Testing Fundamentals]] — the pyramid, TDD, and what makes any test valuable
- [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture|Hexagonal & Clean Architecture]] — why ports and adapters make more of your code unit-testable
- [[backend/05-auth/README|Auth]] — the 401/403 cases above
- [[languages/01-java/03-tooling/04-testing|Java Testing]] — JUnit 5, Mockito and Testcontainers in depth
- [[backend/frameworks/javascript/03-nest/01-nestjs-reference|NestJS reference]] — the three testing levels in that stack

## Seen in the wild
- [[projects/gees-arise/learning/07-testing|Gees Arise — Playwright]] — a real E2E suite driving a sign-up flow in a browser, walked through line by line
- [[projects/strictenv/interview/03-testing-packaging-and-story|strictenv]] — testing and packaging a library, where the public surface *is* the contract
