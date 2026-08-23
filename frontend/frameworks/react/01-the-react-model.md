# The React Model

> **[Intermediate]** · UI as a function of state, what a re-render actually costs, and the hook rules that aren't arbitrary.

## The one idea

$$\text{UI} = f(\text{state})$$

**You don't mutate the DOM. You describe what it should look like given the current state**, and React works out the minimum set of DOM operations to get there.

**Two consequences:**
- **To change the screen, change state.** Reaching for `document.querySelector` in React code means you've left the model
- **Your component function may run many times.** It must be a pure function of props and state — same inputs, same output, no side effects during render → [[foundations/programming-fundamentals/14-programming-paradigms|purity]]

## Render is not the DOM

**The distinction that clears up most React performance confusion.**

```
state changes
  → React calls your component function again      ← "render"
  → produces a new element tree
  → diffs against the previous tree                ← "reconciliation"
  → applies the minimum DOM mutations              ← "commit"
```

**A re-render that produces identical output costs CPU and touches no DOM.** So "it re-rendered" is not automatically a problem — the cost is your function running plus the diff, which for a small component is negligible.

**Which is why premature `memo` is usually a loss:** you've added a props comparison to avoid work that was cheaper than the comparison.

**Keys drive reconciliation.** Using an array index as a key means React matches the wrong elements when a list reorders — and **state moves to the wrong row**, which is the classic "the checkbox jumped" bug. Use a stable id.

## Hooks, and why the rules exist

**Only call hooks at the top level, and only from React functions.**

Not style — mechanics. **React tracks hooks by call order**, not by name. It keeps an array per component and matches the first `useState` to slot 0, the second to slot 1.

```jsx
if (loggedIn) { const [name] = useState("");  }   // ✗ shifts every later hook by one
```

**Conditional hooks make the slots misalign**, so state silently belongs to the wrong hook. That's why the linter rule is an error, not a warning.

## `useState` and `useEffect`

```jsx
const [count, setCount] = useState(0);
setCount(c => c + 1);        // updater form — use when the new value depends on the old
```

**State updates are asynchronous with respect to the current scope.** Reading `count` right after `setCount` gives the old value — you're reading the variable captured by *this* render's closure → [[frontend/interview/02-javascript-and-typescript|stale closures]].

**`useEffect` is for synchronising with something outside React** — a subscription, a timer, a WebSocket, an imperative library, the document title.

**Most `useEffect` calls are unnecessary**, and this is the single most useful thing to internalise:

| Instead of an effect | Do this |
|---|---|
| Deriving state from props | **Calculate during render** |
| Transforming data for display | Calculate during render, `useMemo` if genuinely costly |
| Responding to a user event | **Put it in the event handler** |
| Resetting state when a prop changes | **Change the `key`** to remount |
| Fetching data | **A query library** → [[frontend/04-state-and-data/02-data-fetching-and-server-state\|note 02]] |

**"Why does my effect run twice?"** — StrictMode in development double-invokes effects deliberately, to surface missing cleanup. **It's a feature**: if double-mounting breaks your component, there's a real bug (an unremoved listener, an uncancelled fetch). It doesn't happen in production.

**"Why does my effect loop forever?"** — a dependency is recreated every render (an inline object, array or function). Each render makes a new reference, the effect reruns, sets state, renders again.

## The rest of the hooks

```jsx
useMemo(() => expensive(a, b), [a, b]);        // cache a VALUE
useCallback(fn, [deps]);                       // cache a FUNCTION identity
useRef(initial);                               // mutable box that doesn't trigger renders
useReducer(reducer, init);                     // when next state depends on the last, complexly
useContext(Ctx);                               // read ambient value
useId();                                       // SSR-safe unique id — for label/input pairs
useSyncExternalStore(...);                     // subscribe to a non-React store, correctly
```

**`useRef` for anything that shouldn't cause a render** — a DOM node, a timer id, a previous value, a mutable flag.

**`useMemo`/`useCallback` after profiling.** They cost memory and a dependency comparison. **React Compiler (19+) does this automatically**, which is a good reason not to litter your code with it now.

## What React 19 changed

- **Actions and `useActionState`** — form submission with pending and error state built in
- **`use()`** — read a promise or context, integrating with Suspense
- **Server Components / Server Actions** → [[frontend/frameworks/next/README|Next.js]] · [[frontend/02-rendering/02-hydration-and-the-server-boundary|the server boundary]]
- **React Compiler** — automatic memoisation
- `forwardRef` largely unnecessary — `ref` is a normal prop now

## Where React is weak, honestly

**It's a library, not a framework.** Routing, data fetching, forms and build tooling are all your choice — flexible, and it means every React codebase is assembled differently.

**The mental model has grown.** Server Components, Suspense, transitions and the compiler are real complexity on top of what was once a small idea.

**Re-render behaviour surprises people** far more than in signal-based frameworks (Solid, Svelte 5, Vue), which track dependencies at a finer grain and re-run less by construction.

## Related
- [[frontend/frameworks/react/README|React]] · [[frontend/frameworks/next/README|Next.js]]
- [[frontend/03-structuring-a-frontend/01-components-and-composition|components and composition]]
- [[frontend/interview/01-react-rendering-and-performance|the interview round]]

*Source: [reference] — from the React documentation, Aug 2026.*
