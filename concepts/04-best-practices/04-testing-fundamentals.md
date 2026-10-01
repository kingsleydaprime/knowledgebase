# Testing Fundamentals — Unit, Integration, E2E, Test Doubles, TDD

> **[Beginner→Intermediate]** · Tests answer one question quickly, without a human re-checking by hand: *does this still work?* This lesson covers the kinds of test, the stand-ins you use in them, the tests that fail for no reason, and getting all of it running on every push.

## Before you start

You can already:

- Write functions in JavaScript or TypeScript and run a file with Node.
- Pass a dependency into a function instead of creating it inside → [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring|dependency injection]] (the other core lesson this week).

After this lesson you will be able to:

1. Choose between a unit, integration and end-to-end test for a given behaviour, and say what each can't catch.
2. Use a stub, a fake, a spy and a mock for what each is for — and know which one to reach for by default.
3. Find and remove the two commonest causes of flaky tests: the real clock, and tests that depend on each other's order.
4. Run your tests automatically on every push.

**Study route.** The kid version and §1–5 are the ideas; §6 is the one that bites in production. Run the worked example, making the prediction first. The practice task is this week's flagship milestone.

## The kid version

You've built a bike. You can check it three ways. **On the workbench**, one part at a time: does the wheel spin, does the brake lever move? Quick, and if something's wrong you know exactly which part. **Parts together**: when you pull the lever, does the brake actually grip the wheel? Every part can be fine on its own and still not work together. **Ride it round the block**: the real thing, the way a person uses it — the surest check, but slow, and if it fails you don't know why.

Good testing uses all three: lots of workbench checks, some parts-together checks, and a few rides round the block.

**Where the analogy stops working.** You check a bike once and ride it for years. Code changes every day, so the checks have to run again after **every** change — automatically, because nobody re-checks a hundred things by hand each time.

## 1. Why this exists

A SaaS app emails users the day before their free trial ends. It worked through October. On the 31st, nobody got an email. The code built "tomorrow" by adding 1 to the day of the month, and on the 31st that produced the 32nd — a date no user's trial ends on. There *were* tests, and they passed, because they ran on whatever day the developer happened to run them. **A test that only passes on most days is worse than useless: it says "fine" and is wrong.** The worked example reproduces this bug exactly, then removes the cause.

## Terms used in this lesson

1. **Test**: This is code that runs some of your code with known inputs and checks the result automatically.
2. **Assertion**: This is the check inside a test — "this should equal that". A test with no assertion checks nothing, even if it runs lines of code.
3. **Arrange, act, assert**: This is the usual shape of a test. Set up the inputs and stand-ins, do the one thing being tested, then check the outcome.
4. **Unit test**: This is a test of one small piece — a function or a class — with its collaborators replaced by stand-ins.
5. **Integration test**: This is a test of several real pieces working together, such as a route handler with a real database.
6. **E2E (end-to-end) test**: The letters stand for "end to end". It drives the whole running application the way a user does, usually through a real browser.
7. **Test double**: This is any stand-in used in a test instead of a real collaborator. The name comes from a stunt double. Stubs, fakes, spies and mocks are all test doubles.
8. **Flaky test**: This is a test that sometimes passes and sometimes fails without the code changing.
9. **Deterministic**: This describes something that always gives the same result for the same inputs. Tests must be deterministic.
10. **Regression**: This is something that used to work and has stopped working after a change. Catching regressions is most of what tests are for.
11. **CI (continuous integration)**: The letters stand for those two words. It means automatically building and testing the code on every push, on a server, before anything is merged.

## 2. The shape of a test

```javascript
test("dayAfter rolls over the end of the month", () => {
  const oct31 = new Date("2026-10-31T12:00:00Z");   // arrange
  const result = dayAfter(oct31);                     // act
  assert.equal(result, "2026-11-01");                 // assert
});
```

**One behaviour per test, named as a sentence.** When it fails, the name alone should tell you what broke. "dayAfter rolls over the end of the month" does; "test 3" doesn't.

## 3. Unit, integration, end-to-end — and the pyramid

```
        /\
       /E2E\        <- few, slow, expensive, but test the real user flow end to end
      /------\
     /Integr. \     <- some, moderate speed, test how pieces work together
    /----------\
   / Unit tests \   <- many, fast, cheap, test one small piece in isolation
  /--------------\
```

- **Unit tests** — one function or class, collaborators replaced. Milliseconds each, and when one fails you know exactly where. **What they can't catch:** two pieces that each work alone but disagree with each other — a unit test can pass while the real integration is broken.
- **Integration tests** — real pieces together, such as a handler writing to a real test database. Catch the mismatches unit tests can't: SQL that's wrong, a constraint you forgot, a field named differently on each side. Slower, and they need setup and cleanup.
- **E2E tests** — the whole app through a real browser, with a tool like Playwright or Cypress. The surest evidence a user flow works; also the slowest and most brittle, since an unrelated layout change can break them.

**The pyramid is a cost trade-off, not a law.** Many cheap tests for logic, fewer expensive ones for the joins between pieces. Inverting it — mostly E2E — gives a slow, flaky suite that's bad at saying *what* broke. Some teams, especially on the frontend, prefer a **"testing trophy"** with integration tests as the largest layer, because in UI code the bugs live mostly in how pieces connect. Both agree on the principle: **put each check at the cheapest level that can actually catch the bug.**

## 4. Test doubles — stub, fake, spy, mock

A unit test replaces collaborators so it tests one thing, fast, without a network. The four kinds of stand-in do different jobs:

1. **Stub** — returns canned answers. *"When asked for users on trial, return these two."* Use it to feed the code under test.
2. **Fake** — a working, simplified implementation: an in-memory repository instead of Postgres, a clock you can set. Use it when the code needs a collaborator that behaves realistically across several calls.
3. **Spy** — records how it was called. *"Was `send` called once, with this address?"* Use it to check that the code *did* something to the outside world.
4. **Mock** — a double programmed in advance with the calls it expects, which fails the test if they don't happen. In practice, libraries blur mock and spy; `node:test`'s `mock.fn()` is a spy you assert on afterwards.

**The default rule: stub or fake the things your code asks for, and spy on the things your code tells.** Reading users is a question — stub it, and check the *result*. Sending an email is a command with no useful return value — the only way to know it happened is to spy on it. Don't assert on calls to things that only answer questions; that's testing *how* the code works instead of *what* it does.

## 5. What makes a test worth having

- **It tests behaviour, not implementation.** A test that breaks when you rename a private helper — without any visible behaviour changing — is testing the wrong thing, and it punishes exactly the refactoring tests are supposed to make safe.
- **It's deterministic.** §6.
- **It's fast enough to run constantly.** A suite you avoid running because it takes five minutes isn't giving feedback.
- **It fails for one reason, with a clear message.** One behaviour per test.

**What not to test:** the framework itself (Express routes requests, you don't need to prove it); third-party libraries; trivial code with no logic, like a getter; private functions directly — test them through the public function that uses them.

## 6. Flaky tests, and the two commonest causes

A flaky test is worse than no test: the team learns to re-run red builds until they're green, and one day a real failure gets re-run too.

**Cause 1 — the real clock.** Code that calls `new Date()` or `Date.now()` inside gives different answers on different days, and the bugs live at boundaries: month ends, year ends, leap days, midnight, daylight saving. **Fix:** pass "now" in — a clock object or a date — so the test chooses the day. Where you can't change the code, `node:test` can fake the clock: `mock.timers.enable({ apis: ["Date"], now: ... })`.

**Cause 2 — tests that depend on each other.** Test B passes only because test A ran first and left data behind. Run B alone, or in a different order, and it fails. **Fix:** every test arranges its own data. **Find them:** run the suite in random order — `node --test --test-randomize` — a few times; a test that fails only sometimes is depending on order.

Others to know: real network calls (replace with a stub or fake), random values (pass in the random source or seed it), and shared ports (listen on port 0, so the operating system picks a free one).

## 7. TDD — test-driven development

Write a failing test *first*, for behaviour that doesn't exist yet. Write the minimum code to make it pass. Then refactor with the test as a safety net: **red, green, refactor.**

```javascript
// 1. Red: the test, for behaviour that doesn't exist yet — this fails
test("formatKobo formats kobo as naira", () => {
  assert.equal(formatKobo(150), "₦1.50");
});

// 2. Green: the minimum implementation that passes
const formatKobo = (kobo) => `₦${(kobo / 100).toFixed(2)}`;

// 3. Refactor: improve it freely — the test catches any regression at once
```

The benefit isn't the tests — you'd write those anyway. It's that writing the test first forces you to decide the interface and the expected behaviour **before** writing code, and it's the natural way to fix a bug: first a test that reproduces it, then the fix.

## 8. Running tests on every push

Tests nobody runs catch nothing. Make them run automatically:

1. A script in `package.json`: `"test": "node --test"` (or your runner: Vitest, Jest).
2. A CI workflow that installs dependencies and runs that script on every push and pull request. For GitHub Actions — a fragment, not executed here; check the current major versions of the two actions when you copy it:

```yaml
# .github/workflows/ci.yml — run the tests on every push and pull request
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 24
      - run: npm ci
      - run: npm test
```

3. In the repository settings, make the check **required** before merging, so a red build can't be merged.

## Worked example — the month-end bug, and a real database

Two files of code and two of tests, all built into Node: `node:test`, `node:http` and `node:sqlite`, so there's nothing to install.

**Part 1 — unit tests and test doubles.**

```javascript
// reminders.mjs — email users whose free trial ends tomorrow.

// Dates are "YYYY-MM-DD" strings in UTC, so comparisons are plain string equality.
export function dayAfter(date) {
  const next = new Date(date.getTime());
  next.setUTCDate(next.getUTCDate() + 1); // rolls over months and years correctly
  return next.toISOString().slice(0, 10);
}

// BUG, kept on purpose: reads the real clock and does date arithmetic by hand.
export function tomorrowBuggy() {
  const now = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  return `${now.getUTCFullYear()}-${pad(now.getUTCMonth() + 1)}-${pad(now.getUTCDate() + 1)}`;
}

export function endingTomorrow(users, today) {
  const target = dayAfter(today);
  return users.filter((user) => user.trialEndsOn === target);
}

// Everything it touches is passed in: where users come from, how mail is sent, what "now" is.
export async function sendTrialReminders({ users, mailer, clock }) {
  const due = endingTomorrow(await users.listOnTrial(), clock.now());
  for (const user of due) {
    await mailer.send(user.email, "Your trial ends tomorrow");
  }
  return due.length;
}
```

**Predict before running.** `tomorrowBuggy` reads the real clock. What does it return when "now" is 14 October? And on 31 October?

```javascript
// Unit tests: one module, every collaborator replaced by a test double.
import { test, mock } from "node:test";
import assert from "node:assert/strict";
import { dayAfter, endingTomorrow, sendTrialReminders, tomorrowBuggy } from "./reminders.mjs";

const oct31 = new Date("2026-10-31T12:00:00Z");
const users = [
  { email: "ada@x.com", trialEndsOn: "2026-11-01" },
  { email: "bayo@x.com", trialEndsOn: "2026-11-05" },
];

test("dayAfter rolls over month and year boundaries", () => {
  assert.equal(dayAfter(oct31), "2026-11-01");
  assert.equal(dayAfter(new Date("2026-12-31T23:00:00Z")), "2027-01-01");
  assert.equal(dayAfter(new Date("2028-02-28T00:00:00Z")), "2028-02-29"); // leap year
});

test("endingTomorrow picks only trials ending the day after today", () => {
  assert.deepEqual(endingTomorrow(users, oct31), [users[0]]);
});

test("sendTrialReminders, with a stub, a spy and a fake clock", async () => {
  const stubUsers = { listOnTrial: async () => users };      // STUB: returns canned data
  const mailer = { send: mock.fn(async () => {}) };          // SPY: records every call
  const fakeClock = { now: () => oct31 };                    // FAKE: a working, controllable clock

  const sent = await sendTrialReminders({ users: stubUsers, mailer, clock: fakeClock });

  assert.equal(sent, 1);
  assert.equal(mailer.send.mock.callCount(), 1);
  assert.deepEqual(mailer.send.mock.calls[0].arguments, ["ada@x.com", "Your trial ends tomorrow"]);
});

test("FLAKY: code that reads the real clock passes 30 days a month, then fails", () => {
  mock.timers.enable({ apis: ["Date"], now: new Date("2026-10-14T12:00:00Z") });
  assert.equal(tomorrowBuggy(), "2026-10-15"); // a normal day: looks fine
  mock.timers.setTime(oct31.getTime());
  assert.equal(tomorrowBuggy(), "2026-10-32"); // the 31st: a date that doesn't exist
  mock.timers.reset();
});
```

**Part 2 — integration tests: a real server and a real database.**

```javascript
// app.mjs — a tiny HTTP API over a real database. Nothing to install: node:http + node:sqlite.
import { createServer } from "node:http";
import { DatabaseSync } from "node:sqlite";

export function openDb() {
  const db = new DatabaseSync(":memory:");
  db.exec(`CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    trial_ends_on TEXT NOT NULL
  )`);
  return db;
}

const json = (res, status, body) => {
  res.writeHead(status, { "content-type": "application/json" });
  res.end(JSON.stringify(body));
};

export function createApp(db) {
  return createServer(async (req, res) => {
    if (req.method === "POST" && req.url === "/users") {
      let raw = "";
      for await (const chunk of req) raw += chunk;
      const { email, trialEndsOn } = JSON.parse(raw);
      if (!email?.includes("@")) return json(res, 400, { error: "invalid email" });
      try {
        const { lastInsertRowid } = db
          .prepare("INSERT INTO users (email, trial_ends_on) VALUES (?, ?)")
          .run(email, trialEndsOn);
        return json(res, 201, { id: Number(lastInsertRowid) });
      } catch (err) {
        if (String(err.message).includes("UNIQUE")) return json(res, 409, { error: "email taken" });
        throw err;
      }
    }
    json(res, 404, { error: "not found" });
  });
}
```

```javascript
// Integration tests: a real server and a real database, talking over a real socket.
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { createApp, openDb } from "./app.mjs";

let server, base, db;

before(async () => {
  db = openDb();
  server = createApp(db).listen(0); // port 0: the OS picks a free port, so tests never collide
  await new Promise((resolve) => server.once("listening", resolve));
  base = `http://127.0.0.1:${server.address().port}`;
});
after(() => server.close());

const post = (body) =>
  fetch(`${base}/users`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });

test("POST /users stores the user — checked in the database, not just the response", async () => {
  const res = await post({ email: "ada@x.com", trialEndsOn: "2026-11-01" });
  assert.equal(res.status, 201);
  const { id } = await res.json();
  const row = db.prepare("SELECT email, trial_ends_on FROM users WHERE id = ?").get(id);
  assert.deepEqual({ ...row }, { email: "ada@x.com", trial_ends_on: "2026-11-01" });
});

test("a duplicate email is a 409 — even with different capitals", async () => {
  // Arrange its own data rather than relying on the test above having run first.
  assert.equal((await post({ email: "bayo@x.com", trialEndsOn: "2026-11-02" })).status, 201);
  const res = await post({ email: "BAYO@x.com", trialEndsOn: "2026-11-02" });
  assert.equal(res.status, 409);
});

test("an invalid email is a 400, and nothing is written", async () => {
  const before = db.prepare("SELECT COUNT(*) AS n FROM users").get().n;
  const res = await post({ email: "not-an-email", trialEndsOn: "2026-11-01" });
  assert.equal(res.status, 400);
  assert.equal(db.prepare("SELECT COUNT(*) AS n FROM users").get().n, before);
});
```

**Lab:** these files are in `labs/testing-fundamentals/`. From the vault root, `python3 labs/run.py testing-fundamentals` runs them and checks this page still shows the same code.

**Run it.** From `labs/testing-fundamentals/`, run `node --test`. It needs Node 22.5 or later (for `node:sqlite`); checked with Node 26. Expected:

```
ℹ tests 7
ℹ pass 7
ℹ fail 0
```

Then run `node --test --test-randomize` a few times. It still passes every time, because each test arranges its own data.

**The answers.** On 14 October, `tomorrowBuggy` returns `"2026-10-15"` — correct, so any test run that day passes. On 31 October it returns **`"2026-10-32"`**. The test asserts that wrong value on purpose, to make the bug visible. `dayAfter` has no such bug: it lets `Date` roll the month over, and it takes the date as an argument, so the test picks the day instead of the calendar.

**Notice in part 1:** the stub, the spy and the fake clock each do one job, and `sendTrialReminders` needed no changes to be tested, because everything it touches is passed in. That's what the dependency-injection lesson buys you. **Notice in part 2:** the first test checks the **database**, not only the response. An endpoint can return `201` and store the wrong thing. And the duplicate-email test only proves the case-insensitive rule because it runs against real SQLite. A stubbed repository would have passed whatever the database does.

## Common pitfalls

1. **Treating coverage as quality.** 100% coverage means every line *ran*, not that anything was checked. A test with no meaningful assertion adds coverage and no confidence.
2. **Mocking everything.** If every collaborator is a double, the test proves the code calls doubles correctly — the real interactions are untested. That's what integration tests are for.
3. **Asserting on how instead of what.** Checking that `listOnTrial` was called once, instead of checking who got emailed, breaks on every refactor and catches nothing.
4. **Leaving flaky tests in.** Quarantine or fix them immediately. A suite that's sometimes red trains everyone to ignore red.
5. **Sharing state between tests.** A global, a database row, a module-level variable. Each test arranges its own.
6. **Fixing a bug without a test first.** Write the test that reproduces it, watch it fail, then fix. Otherwise the bug can come back unnoticed.

## Check your understanding

1. Give a bug a unit test can't catch but an integration test can.
2. Name the four kinds of test double and what each is for. Which do you use to check that an email was sent, and why?
3. Why is "stub the questions, spy on the commands" a better default than asserting on every call?
4. A test passes alone and fails in the full suite. What's the likely cause, and how do you find it?
5. **Predict.** In the worked example, if `sendTrialReminders` called `new Date()` itself instead of `clock.now()`, which test would become flaky, and on which days would it fail?

<details>
<summary>Answers — after your attempt</summary>

1. Any mismatch between real pieces: a misspelt column name in SQL, a missing unique constraint, a handler and a database that disagree about case — like the duplicate-email test, which only proves anything against real SQLite.
2. Stub — returns canned data. Fake — a working simplified implementation. Spy — records calls. Mock — pre-programmed with expected calls. To check an email was sent, use a spy: sending returns nothing useful, so the call itself is the only evidence.
3. Questions are checked through the result, so the test survives refactors. Asserting on query calls ties the test to *how* the code works, so it breaks when the implementation changes and catches no real bug.
4. Shared state — it depends on data or settings left by another test, or another test leaves state that breaks it. Run with `--test-randomize` and alone (`--test-name-pattern`) to confirm, then make it arrange its own data.
5. The `sendTrialReminders` test. Its expected result (one email, to Ada) assumes today is 31 October; run on any other day, "tomorrow" is a different date and nobody matches. It would pass on exactly one day — 31 October 2026 — and fail on every other.

</details>

## Practice — independent task

**This is SWE 101's week 2 milestone: real tests in CI on the flagship.**

1. Pick the flagship's most important rule — the one that costs money or loses data if it breaks. Write unit tests for it, with every collaborator passed in and replaced by a stub, fake or spy.
2. Write one integration test that hits a real endpoint against a real test database and checks the database afterwards.
3. Find every `new Date()` or `Date.now()` in the flagship's business logic. Replace one with an injected clock, and add a test at a boundary — month end, year end, or midnight.
4. Add the CI workflow and make it a required check.

**Done when:** CI runs on every push and is green; a pull request that breaks the rule turns it red; `node --test --test-randomize` (or your runner's equivalent) passes five times in a row; and you can explain without notes why you chose a stub, fake or spy for each collaborator.

For backend-specific depth — real databases in disposable containers, test data, auth and time — read [[backend/07-practices/02-testing-a-backend|testing a backend]], this week's optional lesson.

## Before moving on

You can pick the right level for a test, use each kind of test double for its job, remove flakiness caused by time and order, and you have tests running in CI.

**Recap.** Many unit tests, some integration tests, a few end-to-end tests — each check at the cheapest level that can catch the bug. Stub the questions, spy on the commands, fake what needs realistic behaviour. Pass the clock in. Every test arranges its own data. Test behaviour, not implementation. Run it all on every push.

**Next.** Week 3: [[concepts/04-best-practices/08-coupling-and-cohesion|coupling and cohesion]] — and a tool that measures the flagship's.

## Related
- [[concepts/04-best-practices/04b-testing-fundamentals-in-other-languages|Testing Fundamentals in Other Languages]] — runners, doubles, clocks and integration tools in seven languages
- [[backend/07-practices/02-testing-a-backend|Testing a backend]] — Testcontainers, test data, time, auth
- [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring|Dependency injection]] — what makes code testable with doubles
- [[concepts/04-best-practices/01-clean-code|Clean code]] — pinning behaviour with tests before refactoring
- [[concepts/04-best-practices/02-pr-structure|PR structure]] · [[concepts/04-best-practices/03-documentation-practices|documentation practices]]
