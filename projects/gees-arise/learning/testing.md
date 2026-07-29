# Testing (Playwright) — Gees Arise

You asked to learn Playwright properly after seeing it drive the sign-up flow in a real browser during the auth-flow build. This file explains what it actually is and does, then walks through the real test file in this project (`e2e/auth.spec.ts`) line by line.

---

## What Playwright actually is

Playwright is a library that **remote-controls a real browser** — it launches an actual Chromium/Firefox/WebKit engine and drives it the way a human would: open a URL, click things, type into fields, read what's on screen. This is different in kind from things like `tsc --noEmit` (which only checks that code is *structurally valid*) or unit tests (which call a function directly and check its return value) — Playwright is the only one of the three that catches "does this actually work when a real browser loads it and a user clicks through it."

Two separate pieces, easy to conflate:
- **The `playwright`/`@playwright/test` npm package** — the JavaScript API you write test code against (`page.goto(...)`, `page.click(...)`, etc.).
- **The actual browser binary** (`npx playwright install chromium`) — a real Chromium build Playwright downloads and drives. The npm package alone can't do anything without a browser binary to control.

**Headless vs. headed:** by default Playwright runs "headless" — the browser genuinely runs, renders pages, executes JS, but with no visible window (no GPU/display needed, which is why it works fine in a terminal-only environment). You can run "headed" (`headless: false` in config, or `--headed` on the CLI) to actually *watch* the browser window while a test runs — much easier when you're debugging why a test isn't finding an element.

## Two ways to use Playwright, and why this project uses the second one

**1. Raw scripts** (what got used to test the auth flow live, in a throwaway tmp file): plain JS, `chromium.launch()`, manual `try/catch`, `console.log` to report results. Fine for a one-off "does this work right now" check, but nothing about it persists — hence you not finding it in the repo afterward. Every run has to be re-driven by hand.

**2. `@playwright/test`** (what's actually in this repo now, `e2e/auth.spec.ts`): a real **test framework** built on top of the same browser-automation engine. It adds:
- `test(name, async ({ page }) => {...})` — declares a named, individually runnable test. `page` is provided automatically (a "fixture") — you don't manually launch/close a browser yourself.
- `expect(...)` — assertions that fail the test with a clear message and automatically **retry for a few seconds** before giving up (crucial for web UIs: a redirect or a rendered error message doesn't appear instantly, so a naive `if (url !== expected) throw` would be flaky; `expect(page).toHaveURL(...)` keeps checking until it's true or times out).
- A config file (`playwright.config.ts`) — one place for base URL, which browsers to test in, and (see below) auto-starting the dev server.
- An HTML report (`reporter: "html"` in the config) — after a run, `npx playwright show-report` opens a browsable report of what passed/failed, with screenshots/traces on failure.

## Reading `playwright.config.ts`

```ts
export default defineConfig({
  testDir: "./e2e",
  use: { baseURL: "http://localhost:3000", trace: "on-first-retry" },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000",
    reuseExistingServer: true,
    timeout: 60_000,
  },
});
```
- `testDir: "./e2e"` — where test files live. Kept separate from a future unit-test setup (e.g. Vitest for pure functions) since browser tests are a different *kind* of test (slow, need a real server) from unit tests (fast, no server needed).
- `baseURL` — lets tests write `page.goto("/login")` instead of the full `http://localhost:3000/login` every time.
- `trace: "on-first-retry"` — if a test fails and retries, Playwright records a full trace (network, DOM snapshots, console) you can replay afterward with `npx playwright show-trace`.
- **`webServer`** is the important one: it tells Playwright to run `npm run dev` *itself* before the tests start, and wait until `http://localhost:3000` responds. `reuseExistingServer: true` means if you already have `npm run dev` running in another terminal, Playwright detects that and uses it instead of starting a second one. Net effect: **`npx playwright test` alone is enough** — no need to manually start the dev server first (though you still can, especially while actively developing and watching output).

## Reading `e2e/auth.spec.ts`

```ts
test("unauthenticated visitors are redirected to /login", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/\/login$/);
});
```
Navigates to the root, then asserts the *final* URL matches `/login` — this is testing `proxy.ts`'s redirect logic (see `learning/sys-design.md` and `learning/supabase.md` §1) without needing to read a single line of that file; it's checking the observable behavior.

```ts
test("can navigate between /login and /signup", async ({ page }) => {
  await page.goto("/login");
  await page.getByRole("link", { name: "Sign up" }).click();
  await expect(page).toHaveURL(/\/signup$/);
  ...
```
`getByRole("link", { name: "Sign up" })` is Playwright's **preferred way to find elements** — by their accessible role and visible text, the same way a screen reader or a real user would identify them, rather than by CSS selectors like `.some-class-name` or `#some-id` (those break the moment styling changes; accessible roles/labels are far more stable and also nudge you toward writing more accessible markup in the first place). Compare this to the original scratch script, which used raw CSS selectors like `input[name="email"]` — that works, but `getByLabel("Email")` (used further down) is more robust since it survives the input's `name` attribute changing.

```ts
test("signing up with an undeliverable email domain shows an error", async ({ page }) => {
  ...
  await expect(page.getByText(/invalid/i)).toBeVisible();
});
```
This is the exact scenario that happened live during testing: Supabase's Auth API rejects `@example.com` as non-deliverable, and the app is supposed to surface that error in the UI (via the `state?.error` rendering in `login/page.tsx`/`signup/page.tsx` — see `learning/frontend.md`). Turning what was a one-off manual finding into a permanent test means this behavior stays checked automatically from now on, instead of only being true "as of the day someone happened to test it by hand."

```ts
// Not run by default...
test("full signup reaches the check-email page", async ({ page }) => {
```
Left in the file, but documented as something to run deliberately (`npx playwright test --grep "full signup"`) rather than every time, because Supabase's built-in email sender has a real rate limit (see `learning/supabase.md`) — running this on every test run would start failing for a reason that has nothing to do with whether the code is broken. **This is a real, common testing tradeoff**: a test that's *accurate* but *expensive/rate-limited* to run often ends up run selectively rather than on every single execution, unlike cheap, side-effect-free tests which should just always run.

## How to actually run these

```bash
npx playwright test              # runs every test except explicitly-skipped ones, headless
npx playwright test --headed     # same, but you can watch the browser window
npx playwright test --grep "full signup"   # run just that one test
npx playwright show-report       # open the HTML report from the last run
```

## To cover as we build more of the app

- [ ] Writing a test for the *authenticated* path (signing in as a real user, then interacting with circle/task UI) — needs a way to get a logged-in session into a test without hitting the real rate-limited signup flow every time (likely: seed a confirmed test user directly via Supabase, or use `storageState` to reuse a saved login session across tests)
- [ ] CI — running these on every push/PR once there's a CI pipeline, rather than only ever running locally
