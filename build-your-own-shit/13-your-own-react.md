# Build Your Own React

> **[Intermediate]** · ~500 lines, and **the hook rules stop being rules and become consequences.**

## What you're building

**A working React clone** — JSX, a virtual DOM, reconciliation with keys, function components, and `useState`/`useEffect` — that renders and updates a real app in the browser.

**And what you're deliberately not:** Suspense, Server Components, concurrent features, portals, error boundaries, or the event system. **The goal is that `useState` stops being magic**, not a production framework.

**Why it belongs here:** it's the frontend equivalent of [[build-your-own-shit/04-your-own-language|your own language]] — a tool you use every day whose internals feel like magic until you've built the smallest version of one.

## What you need first

- **JavaScript, comfortably** — closures especially → [[frontend/interview/02-javascript-and-typescript|JS & TS]]
- **The DOM** — `createElement`, `appendChild`, `removeChild` → [[frontend/01-foundations/02-the-browser-and-the-dom|the browser and the DOM]]
- **The React model** — what you're reimplementing → [[frontend/frameworks/react/01-the-react-model|the React model]]

**JavaScript, in the browser.** No build tooling beyond something that transpiles JSX — or skip JSX entirely and call `createElement` directly for the first few steps.

## The build order

**1. `createElement` — JSX is just function calls.**
```jsx
<div id="a">hello</div>
// ↓ Babel transpiles to
createElement("div", { id: "a" }, "hello")
// ↓ which returns
{ type: "div", props: { id: "a", children: [{ type: "TEXT", props: { nodeValue: "hello" }}] } }
```
Write `createElement` returning that object. **Wrap text children in their own element objects** so everything downstream handles one shape.
*Works when:* `console.log(<div>hi</div>)` prints your object tree. **JSX stops being syntax and becomes data.**

**2. `render` — object tree to DOM.**
Recursively create DOM nodes, assign props, append children.
*Works when:* a static element tree appears on the page. **You now have a working (if useless) framework.**

**3. Break the recursion into a work loop.**
Step 2 recurses until the whole tree is built — and **cannot be interrupted**, so a large tree blocks the main thread and the page janks → [[frontend/01-foundations/01-what-a-frontend-is|one thread does everything]].

Restructure into units of work processed in a loop, yielding via `requestIdleCallback` (or `MessageChannel`, which is what React actually uses).
*Works when:* rendering a large tree no longer freezes the page. **This is the entire motivation for React Fiber**, discovered by hitting the problem yourself.

**4. Fibers — a tree you can pause in.**
To resume, you need to know where you were. A recursive call stack can't be saved; **a linked structure can.**

Give each unit `child`, `sibling` and `parent` pointers. Traversal becomes: child first, then sibling, then walk up to the parent's sibling.
*Works when:* you can process one fiber, return, and continue correctly later. **The awkwardness of that traversal is why fibers exist** — it's the price of interruptibility.

**5. Split render and commit.**
Mutating the DOM as you go means a user can see a **half-built tree** if you yield mid-render.

So: build the whole fiber tree first (**render phase**, interruptible), then apply every DOM change at once (**commit phase**, uninterruptible).
*Works when:* nothing partial ever appears on screen.

**This is why render must be pure** → [[frontend/frameworks/react/01-the-react-model|the React model]]. The render phase can be paused, restarted, or thrown away — so a side effect there might run twice or never. **StrictMode's double-invocation exists to surface exactly this**, and now you know why.

**6. Reconciliation — diffing and keys.**
Compare the new tree to the previous one, fiber by fiber:
- **Same type** → keep the DOM node, update changed props
- **Different type** → delete the old node, create a new one
- **Removed** → delete

*Works when:* updating text doesn't recreate the whole tree — verify in DevTools by watching which nodes flash.

**Then add keys.** Without them, matching is positional: insert an item at the front of a list and every subsequent element is treated as "changed", so **state moves to the wrong row**. With keys, you match by identity.
*Works when:* you've **reproduced the index-as-key bug** — a checked checkbox jumping to a different item after an unshift — and then fixed it with stable keys. **Do this deliberately; it's the most valuable ten minutes in the project.**

**7. Function components.**
Their fiber has no DOM node of its own — you *call* the function to get children.
*Works when:* `<App />` renders, and nested components work.

**8. `useState` — and the reason for the rules.**
Store hooks in an **array on the fiber**, with a cursor that increments on each hook call.

```js
let wipFiber = null, hookIndex = null;

function useState(initial) {
  const old = wipFiber.alternate?.hooks?.[hookIndex];
  const hook = { state: old ? old.state : initial, queue: [] };
  (old?.queue ?? []).forEach(action => { hook.state = action(hook.state); });
  const setState = action => { hook.queue.push(action); scheduleRerender(); };
  wipFiber.hooks.push(hook);
  hookIndex++;
  return [hook.state, setState];
}
```

*Works when:* a counter increments and re-renders.

**Now put a hook inside an `if` and watch state attach to the wrong hook.** The cursor shifts, slot 1 becomes slot 0, and the values swap. **"Only call hooks at the top level" is not a style rule — it's the only thing keeping that array aligned** → [[frontend/frameworks/react/01-the-react-model|the hook rules]].

**9. `useEffect`.**
Collect effects during render, run them **after commit**, and run the previous cleanup first. Compare dependency arrays to decide whether to re-run.
*Works when:* an effect runs on mount, cleanup runs on unmount, and a changed dep re-runs it.

**10. Optional: signals instead.**
Rebuild the same app with **fine-grained reactivity** — a `signal()` that tracks which computations read it and re-runs only those, with no virtual DOM and no diffing.

*Works when:* updating one value re-runs one computation rather than a component function. **~100 lines, and it makes the [[frontend/frameworks/README|React vs Solid/Svelte comparison]] something you've felt** rather than read.

## The parts that will bite you

**Text nodes.** Strings and numbers aren't objects. Normalise them into `TEXT_ELEMENT` fibers in step 1 or every later step needs a special case.

**`children` is both a prop and a structural field.** Decide early whether it lives in `props` (React's choice) and be consistent.

**The `alternate` pointer.** Each fiber links to its counterpart from the previous render — that's how you diff. Forget to set it and every update looks like a fresh mount.

**Event handlers.** Props starting with `on` need `addEventListener`, not `setAttribute` — **and old listeners must be removed on update** or they accumulate silently.

**`requestIdleCallback` isn't in Safari.** Use `MessageChannel`, or a `setTimeout` shim.

**Infinite re-render loops** when `setState` is called during render. Yours will do it; React errors on it deliberately.

## How to know it works

1. **Static tree renders**
2. **A large tree doesn't freeze the page** (step 3)
3. **Updating text doesn't recreate the DOM** — watch the flashing in DevTools
4. **You reproduced the index-key bug, then fixed it**
5. **A counter works**, and **a conditional hook breaks it in the way you can now explain**
6. **Effects run and clean up in order**
7. **A small real app** — a to-do list with add, toggle and delete

## Where to stop

**Stop after `useEffect` and the to-do list.** Synthetic events, Suspense, concurrent scheduling and Server Components are each large and teach much less per hour once the core is yours.

**You will have learned:** that JSX is function calls, that the virtual DOM is an optimisation rather than a virtue, **why fibers exist**, why render must be pure, why keys matter, and why the hook rules are mechanical rather than stylistic.

**The reference implementation:** Rodrigo Pombo's [Build Your Own React](https://pomb.us/build-your-own-react/) — a genuinely excellent walkthrough of exactly this, and the best companion to this guide.

## Related
- [[frontend/frameworks/react/01-the-react-model|the React model]] — what you're reimplementing
- [[frontend/frameworks/README|frameworks/]] — the reactivity-model comparison step 10 illuminates
- [[build-your-own-shit/04-your-own-language|your own language]] — the same premise, other end of the stack
- [[foundations/compilers/README|compilers]] — JSX transpilation

*Source: [reference] — build guide, Aug 2026.*
