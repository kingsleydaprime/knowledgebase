# Testing Fundamentals — Unit, Integration, E2E, TDD

Tests exist to answer one question with confidence, quickly, without a human manually re-checking: "does this still work?" Different test types answer that question at different scopes, each with a different cost, and a healthy test suite deliberately uses all of them rather than over-relying on just one.

## The testing pyramid — why scope changes the tradeoffs

```
        /\
       /E2E\        <- few, slow, expensive, but test the real user flow end to end
      /------\
     /Integr. \     <- some, moderate speed, test how pieces work together
    /----------\
   / Unit tests \   <- many, fast, cheap, test one small piece in isolation
  /--------------\
```

- **Unit tests** — test one function/class in isolation, with dependencies mocked or stubbed out. Fast (milliseconds), cheap to write, and pinpoint exactly what broke when they fail — but they can't catch problems that only show up when real pieces interact (a unit test can pass while the actual integration between two correctly-unit-tested pieces is broken).
- **Integration tests** — test multiple real pieces working together (a route handler hitting a real test database, not a mocked one) — catch the class of bug unit tests structurally can't, at the cost of being slower and a bit more complex to set up and tear down reliably.
- **End-to-end (E2E) tests** — test a complete real user flow through the actual running application (often via a real browser, using something like Playwright or Cypress) — the highest confidence that a real user flow actually works, and the slowest, most expensive, most brittle (small unrelated UI changes can break an E2E test that wasn't testing that part at all).

```javascript
// unit test — this specific function, in isolation
test("calculateTotal sums item prices", () => {
  expect(calculateTotal([{ price: 10 }, { price: 5 }])).toBe(15);
});

// integration test — the route handler + a real (test) database together
test("POST /orders creates an order in the database", async () => {
  const res = await request(app).post("/orders").send({ items: [{ price: 10 }] });
  expect(res.status).toBe(201);
  const saved = await db.orders.findById(res.body.id);
  expect(saved.total).toBe(10);
});
```

## The pyramid shape is a deliberate cost tradeoff, not a rule to follow blindly

Many cheap, fast unit tests give quick, precise feedback on most logic; fewer, more expensive integration/E2E tests cover the interactions and real user flows unit tests structurally can't reach. Inverting this (mostly E2E tests, few unit tests — sometimes called an "ice cream cone" shape) tends to produce a slow, flaky, expensive-to-maintain suite that's still bad at pinpointing exactly what broke when something fails — which is why the pyramid shape is the common industry recommendation rather than an arbitrary preference.

## TDD — Test-Driven Development

Write a failing test *first*, for behavior that doesn't exist yet, then write the minimum code needed to make it pass, then refactor with the safety net of that passing test already in place ("red, green, refactor").

```javascript
// 1. Red: write the test first, for behavior that doesn't exist yet — this fails
test("formatCurrency formats cents as dollars", () => {
  expect(formatCurrency(150)).toBe("$1.50");
});

// 2. Green: write the minimum implementation to make it pass
function formatCurrency(cents) { return `$${(cents / 100).toFixed(2)}`; }

// 3. Refactor: now improve the implementation freely — the test catches any regression immediately
```

The claimed benefit isn't really "tests," which you'd write anyway — it's that writing the test *first* forces you to think through the interface and expected behavior before writing implementation code, and gives you an immediate, automatic signal the moment a refactor breaks something, rather than discovering it later.

## What makes a test actually valuable

- **Tests behavior, not implementation** — a test that breaks the moment you refactor internal implementation details (without changing any actual observable behavior) is testing the wrong thing, and actively discourages safe refactoring rather than enabling it.
- **Deterministic** — a flaky test (one that sometimes fails for no code-related reason, often due to timing or shared state between tests) is worse than no test — it erodes trust in the whole suite, to the point where failures start getting reflexively re-run and ignored instead of investigated.
- **Fast enough to actually run often** — a test suite so slow that it discourages developers from running it locally before pushing defeats much of its own purpose as a fast feedback loop.

## Gotchas

- 100% code coverage is a measure of *coverage*, not test quality — a test that executes a line without meaningfully asserting on its behavior counts toward coverage while providing close to zero real confidence.
- Over-mocking in unit tests can hide real integration bugs — if every dependency is mocked, a unit test can pass while the actual, real interaction between components is broken; this is exactly why integration tests exist as a separate, necessary layer, not a redundant one.
- Flaky tests left unfixed train a team to ignore CI failures generally, which is how a genuine, real failure eventually slips through unnoticed in the noise.

## Related
- [[01-clean-code|clean-code]]
- [[02-pr-structure|pr-structure]]
- [[03-documentation-practices|documentation-practices]]
