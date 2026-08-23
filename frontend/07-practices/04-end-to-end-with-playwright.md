# End-to-End with Playwright

> **[Intermediate]** · A real browser, real navigation, real network. **Written to explain why the tests are shaped the way they are**, because the structure is the part that makes them stable.

**E2E tests are the top of the pyramid** → [[concepts/04-best-practices/04-testing-fundamentals|testing fundamentals]]: slowest, most expensive, and the only ones that prove the whole thing works together.

**Have few of them, and make those few reliable.** A flaky E2E suite is worse than none, because people start re-running until green — and then it catches nothing.

## Why auto-waiting is the whole design

**The historical problem with E2E testing was timing.** Selenium-era tests were full of sleeps, because the test could act before the page was ready.

**Playwright's central design decision: every action waits for the element to be actionable first** — attached to the DOM, visible, stable (not animating), enabled, and not obscured by something else.

```js
await page.getByRole("button", { name: "Save" }).click();
```

**That one line is doing a lot.** It polls until the button exists, is visible, has stopped moving, and can actually receive the click — then clicks. **If any condition never holds, it fails with a message saying which one.**

**Which is why you should never write:**

```js
await page.waitForTimeout(2000);        // ✗ the thing auto-waiting exists to replace
```

**A fixed sleep is simultaneously too short on a slow CI runner and too long everywhere else.** If you find yourself reaching for one, the real problem is usually that you're asserting on the wrong thing.

## Locators are lazy, and that's the point

```js
const saveButton = page.getByRole("button", { name: "Save" });   // resolves NOTHING yet
await saveButton.click();                                        // resolves HERE
```

**A locator is a *description* of how to find an element, not the element itself.** It re-resolves every time you use it.

**Why that matters:** in a React app, a re-render replaces DOM nodes. A held reference to an old node is stale — the classic "element is not attached to the document" error. **A locator can't go stale, because it looks the element up again each time.**

**Use the same query priority as component tests** → [[frontend/07-practices/03-testing-a-frontend|note 03]]: `getByRole` first, `getByLabel` for form fields, `getByTestId` last. **Same reasoning — role queries test accessibility as a side effect, and CSS-selector queries break the moment someone renames a class.**

```js
page.getByRole("button", { name: "Save" })     // ✓ survives restyling
page.locator(".btn-primary-2 > span")          // ✗ breaks on any markup change
```

## Web-first assertions retry; plain ones don't

**This distinction causes more flakiness than anything else, and it's easy to miss:**

```js
await expect(page.getByText("Saved")).toBeVisible();     // ✓ RETRIES until true or timeout
expect(await page.getByText("Saved").isVisible()).toBe(true);   // ✗ checks ONCE, immediately
```

**The first form polls.** The second takes a snapshot at one instant — and if the UI hasn't updated yet, it fails.

**The rule: `await expect(locator)…`, not `expect(await …)`.** The position of the `await` is the whole difference, and it's the single most useful thing to internalise about this tool.

## Structure: fixtures over `beforeEach`

**Playwright's fixture system is its best feature and the least used by beginners.**

```js
// fixtures.ts — define once
export const test = base.extend<{ authedPage: Page }>({
  authedPage: async ({ page }, use) => {
    await page.goto("/login");
    await page.getByLabel("Email").fill("test@example.com");
    await page.getByLabel("Password").fill("password");
    await page.getByRole("button", { name: "Log in" }).click();
    await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
    await use(page);          // ← the test runs here
    // teardown after
  },
});
```

```js
test("can create an order", async ({ authedPage }) => { … });   // just ask for it
```

**Why this beats `beforeEach`:** fixtures are **composable, lazy and typed.** A test that doesn't request `authedPage` doesn't pay for it — whereas `beforeEach` runs for every test in the file whether it's needed or not.

**Better still: don't log in through the UI at all.**

```js
// global setup — log in ONCE, save the cookies
await page.context().storageState({ path: "auth.json" });
// then: use: { storageState: "auth.json" }
```

**Logging in through the form in every test adds seconds per test and tests the login flow hundreds of times.** Test login *once*, properly; reuse the session everywhere else.

## Isolation is what keeps it non-flaky

**Every test gets a fresh browser context** — new cookies, new storage, new session. That's why Playwright tests can run in parallel by default.

**But your backend is shared**, and that's where isolation actually breaks:

- **Unique data per test.** `user-${Date.now()}@test.com`, not a hardcoded email — two parallel tests creating the same record collide
- **Don't depend on test order.** Each test sets up what it needs
- **Seed via the API, not the UI.** Creating a prerequisite order through fifteen clicks is slow and tests things this test isn't about
- **Clean up**, or reset the database between runs → [[backend/07-practices/02-testing-a-backend|test data isolation]]

**The shared-backend problem is the same one as [[backend/07-practices/02-testing-a-backend|backend testing]]**, and it's the reason "it passes alone but fails in the suite" happens.

## Debugging — the tools that make this bearable

```bash
npx playwright test --ui          # ← the UI mode. Start here. Time-travel through the run
npx playwright test --debug       # step through with Inspector
npx playwright codegen localhost:3000   # record actions → generated locators
npx playwright show-trace trace.zip
```

**The trace viewer is the answer to "it fails in CI and I can't reproduce it."** Enable `trace: "on-first-retry"` and a failed CI run gives you a DOM snapshot at every step, the network log, the console, and screenshots before and after each action. **You can inspect the page as it was at the moment of failure.**

**`codegen` is a genuinely good way to learn the API** — click through a flow and read the locators it produces. Then rewrite them, because generated locators are often more brittle than what you'd choose.

## What to E2E, and what not to

**A handful of critical journeys**, not coverage:

- Sign up → verify → first meaningful action
- Log in → the core workflow → log out
- The checkout or payment path
- Anything where failure costs money or data

**Not** every form validation message, every empty state, every permutation. **Those belong in component tests**, which run in milliseconds → [[frontend/07-practices/03-testing-a-frontend|note 03]].

**The economics: an E2E test costs seconds and can fail for reasons unrelated to your change** — a slow CI runner, a flaky dependency, a network hiccup. **A component test costs milliseconds and fails only when behaviour broke.** Push everything down the pyramid that will go.

## The extras worth knowing

- **Cross-browser** — Chromium, Firefox and WebKit from one config. **WebKit is how you catch Safari bugs without owning a Mac**
- **`--project=mobile-chrome`** — real device emulation, viewport and touch
- **`toHaveScreenshot()`** — visual regression, built in
- **API testing** — `request.post(...)` for seeding, or for testing the API directly
- **Network interception** — `page.route()` to stub or fail a specific request, which is how you test error states deterministically

## Related
- [[frontend/07-practices/03-testing-a-frontend|testing a frontend]] — the component layer
- [[backend/07-practices/02-testing-a-backend|testing a backend]] — the shared-database problem
- [[concepts/04-best-practices/04-testing-fundamentals|testing fundamentals]] — the pyramid
- [[devops/06-ci-cd/README|CI/CD]] — where these run

*Source: [reference] — from the Playwright documentation, Aug 2026.*
