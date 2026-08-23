# Testing a Frontend

> **[Intermediate]** · Test what the user does, not what the component is — and the one rule that makes frontend tests survive a refactor.

**The pyramid and TDD are in [[concepts/04-best-practices/04-testing-fundamentals|testing fundamentals]]; the server side is in [[backend/07-practices/02-testing-a-backend|testing a backend]].** This is what's different about the browser.

## What makes frontend testing distinctive

**Three things, and each one shapes the tooling:**

**The DOM is the output.** You're not asserting on a return value — you're asserting on a rendered tree, which means queries and text matching rather than equality.

**Everything is async.** Data arrives, animations run, state settles. **Most flaky frontend tests are a missing wait**, and the fix is almost never `sleep`.

**Implementation churns constantly.** Refactor a component, rename a prop, swap a state library — **and the behaviour is unchanged.** A test coupled to implementation now fails for no user-visible reason, which trains people to delete tests.

## The rule

> **The more your tests resemble the way your software is used, the more confidence they can give you.** — Kent C. Dodds

**In practice: query the DOM the way a user finds things, and assert what a user would observe.**

```jsx
// ✗ coupled to implementation — breaks on any refactor
expect(wrapper.find("SubmitButton").props().disabled).toBe(true);
expect(component.state.isLoading).toBe(true);

// ✓ coupled to behaviour — survives the refactor
expect(screen.getByRole("button", { name: /submit/i })).toBeDisabled();
```

**The second version also happens to test accessibility**, because `getByRole` only finds the button if it's exposed correctly to assistive technology. **That's the quiet reason to prefer role queries: a test that can't find your button is telling you a screen reader can't either** → [[frontend/06-cross-cutting/01-accessibility|accessibility]].

## The query priority

Testing Library orders queries deliberately, and following the order is most of the value:

1. **`getByRole`** — accessible role + name. **The default; use this**
2. **`getByLabelText`** — form fields
3. **`getByPlaceholderText`** · **`getByText`** · **`getByDisplayValue`**
4. **`getByAltText`** · **`getByTitle`**
5. **`getByTestId`** — **the escape hatch**, not the default

**`data-testid` is not forbidden — it's last.** A test id says "there is no user-perceivable way to find this", which is occasionally true (a chart container, a layout wrapper) and usually means the markup is missing a role or a label.

**The three prefixes matter and get confused:**

| | Returns | Use for |
|---|---|---|
| `getBy…` | Element, **throws if absent** | It should be there **now** |
| `queryBy…` | Element or **null** | Asserting **absence** |
| `findBy…` | **Promise**, retries | It will appear **after** something async |

```jsx
expect(screen.queryByText("Error")).not.toBeInTheDocument();   // ✓ absence
expect(await screen.findByText("Saved")).toBeVisible();         // ✓ appears later
```

**Using `getBy` to assert absence throws instead of failing cleanly**, and using it for async content is the single most common source of "works locally, fails in CI".

## Waiting properly

```jsx
await screen.findByText("Loaded");                    // ✓ retries until it appears
await waitFor(() => expect(mockFn).toHaveBeenCalled()); // ✓ for non-DOM assertions
await waitForElementToBeRemoved(() => screen.queryByText("Loading"));

await new Promise(r => setTimeout(r, 1000));          // ✗ never
```

**A fixed sleep is either too short (flaky) or too long (slow), and it's usually both across different machines.** Every waiting helper here polls until a condition holds or a timeout expires — that's what makes them stable.

**Use `userEvent`, not `fireEvent`:**

```jsx
await userEvent.type(screen.getByLabelText("Email"), "a@b.com");
await userEvent.click(screen.getByRole("button", { name: /save/i }));
```

`fireEvent.click` dispatches one synthetic event. **`userEvent.click` does what a browser does** — pointer events, focus, mouse down/up, then click. Which matters, because a component that only breaks on real focus behaviour will pass a `fireEvent` test.

## Mock the network, not your modules

**The most valuable single change to most frontend test suites.**

```jsx
// ✗ mocking your own module — asserts your assumptions, not behaviour
jest.mock("./api", () => ({ fetchUser: () => Promise.resolve({ name: "Ada" }) }));

// ✓ MSW — intercept at the network layer
const server = setupServer(
  http.get("/api/users/:id", () => HttpResponse.json({ id: 1, name: "Ada" }))
);
```

**Why it's better:** your real fetch code, your real query library, your real error handling and retries all execute. **You've replaced the server, not your application.** And the same handlers work in tests, in Storybook, and in local development.

**It also makes failure testing trivial**, which is the part people skip:

```jsx
server.use(http.get("/api/users/:id", () => new HttpResponse(null, { status: 500 })));
```

**Test the error state, the empty state and the slow state** — those are the states users actually hit and the ones that never get built properly → [[frontend/04-state-and-data/02-data-fetching-and-server-state|the five states]].

## What to test, and what not to

**Worth testing:**
- **Business logic and derived values** — highest value, cheapest to test
- **Conditional rendering** — what appears for an admin vs a guest
- **Forms** — validation, error display, submission, the disabled-while-submitting state
- **Async states** — loading, error, empty, success
- **Custom hooks** with real logic
- **Accessibility** — `jest-axe` in a component test is nearly free

**Not worth testing:**
- **That the framework works.** `useState` updates. The router routes
- **Implementation details** — internal state, private handlers, "did this re-render"
- **Exact markup or class names.** `toMatchSnapshot()` on a whole component produces a test nobody reads and everybody re-baselines → [[concepts/interview/02-patterns-code-quality-and-review|testing theatre]]
- **Styling.** Use visual regression tooling for that, not assertions

## The tools

| | |
|---|---|
| **Vitest** | The default for new projects — fast, Vite-native, Jest-compatible API |
| **Jest** | Still everywhere; fine |
| **Testing Library** | The queries. Framework-specific packages for React/Vue/Svelte |
| **MSW** | Network mocking |
| **jest-axe / axe-core** | Automated accessibility assertions |
| **Storybook + play functions** | Component testing with a visual harness |
| **Playwright** | → [[frontend/07-practices/04-end-to-end-with-playwright\|note 04]] |

**jsdom is not a browser.** It has no layout engine, so anything depending on real geometry — `getBoundingClientRect`, `IntersectionObserver`, scroll position — returns zeros or needs stubbing. **When a test needs real rendering, that's a signal to move it to Playwright**, which runs in an actual browser.

## Related
- [[frontend/07-practices/04-end-to-end-with-playwright|end-to-end with Playwright]]
- [[concepts/04-best-practices/04-testing-fundamentals|testing fundamentals]] — the pyramid, TDD
- [[backend/07-practices/02-testing-a-backend|testing a backend]] — the other half
- [[frontend/06-cross-cutting/01-accessibility|accessibility]] — why role queries pay twice

*Source: [reference] — from the Testing Library and MSW documentation, Aug 2026.*
