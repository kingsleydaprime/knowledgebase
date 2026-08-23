# Frontend Interview — JavaScript & TypeScript

The language round. **Every frontend and full-stack interview has one**, and it's the round most candidates under-prepare because they've been writing framework code rather than language code.

From [[frontend/README|frontend]], [[backend/frameworks/javascript/01-node-runtime/README|the Node runtime]], and [[foundations/programming-fundamentals/README|programming fundamentals]].

---

### Q1. [Beginner→Intermediate] 🔥 Explain the event loop.

**Strong answer covers:** JavaScript has **one** thread for your code. The runtime keeps a **call stack**; when the stack empties, the event loop pulls work from queues and pushes it on. Async APIs (timers, network, I/O) are handled *outside* the JS thread — by the browser or by libuv in Node — and their callbacks are queued when ready.

**Details that matter:**
- **Two queues, not one.** **Microtasks** (promise callbacks, `queueMicrotask`, `MutationObserver`) drain **completely** after each macrotask. **Macrotasks** (timers, I/O, events) run one per tick. So a promise chain always resolves before a `setTimeout(…, 0)` queued earlier.
- **A microtask that queues another microtask starves the macrotask queue** — an infinite promise loop freezes the page in a way an infinite `setTimeout` doesn't.
- **`setTimeout(fn, 0)` is not "immediately"** — it's "after the current stack unwinds, and no sooner than the clamped minimum" (~4ms for nested timers in browsers).
- **Blocking is blocking.** A 500ms synchronous loop freezes rendering, input and everything else. That's what Web Workers exist for.

**The senior point:** *asynchronous* is not *parallel*. One thread, interleaved. Which is why a CPU-bound task needs a Worker (browser) or a worker thread / separate process (Node), and why `Promise.all` doesn't make anything faster unless the work was already off-thread — it just stops you awaiting sequentially → [[languages/06-python/12-concurrency-and-the-gil|the same argument in Python]].

---

### Q2. [Intermediate] 🔥 What's a closure, and where have you actually used one?

**Strong answer covers:** a function bundled with the scope it was created in, keeping those variables alive after the enclosing function returns.

```js
function counter() {
  let n = 0;                 // captured
  return () => ++n;
}
```

**Where they genuinely show up** — and having a real example is what separates a memorised answer:
- **Module privacy** — variables reachable only through the returned functions
- **Event handlers and callbacks** capturing the props/state of the render that created them
- **`useState`** — React's hook state lives in a closure over the fibre, which is *why* hooks can't be called conditionally
- **Debounce and throttle** — the pending timer id lives in the closure

**The trap to raise unprompted — stale closures:**
```js
useEffect(() => {
  const id = setInterval(() => setCount(count + 1), 1000);   // ✗ always 0 + 1
  return () => clearInterval(id);
}, []);                                                       // captured the FIRST count
```
Fix with the updater form `setCount(c => c + 1)`, or add the dep. **This is the single most common React bug caused by a language feature**, and it's the same late-binding trap as [[languages/06-python/04-functions-and-scope|Python's loop closures]].

---

### Q3. [Intermediate] 🔥 `==` vs `===`, and what actually surprises people.

**Strong answer covers:** `===` compares without coercion; `==` coerces first via a documented but unintuitive algorithm. **Use `===`**, with the one idiomatic exception below.

**Details that matter:**
- `null == undefined` is **true**; `null === undefined` is false. So `if (x == null)` is the idiomatic "null or undefined" check, and it's the one legitimate use of `==`
- `NaN !== NaN`. Test with `Number.isNaN`, and note `isNaN("foo")` is `true` because it coerces — `Number.isNaN` doesn't
- `0 == "0"` true, `0 == []` true, `"0" == []` **false** — three coercions, no transitivity
- `typeof null === "object"` — a bug from 1995, unfixable for compatibility
- **Objects compare by reference.** `{} === {}` is false → [[foundations/programming-fundamentals/05-variables-and-types|reference vs value]]

**The senior point:** this is trivia *unless* you can say why it matters — coercion bugs surface at boundaries where data arrives as strings (query params, form inputs, env vars, JSON). **Parse at the boundary**, then the rest of your code never faces the question.

---

### Q4. [Intermediate] What is `this`, and how do the rules resolve?

**Strong answer covers:** in a normal function, `this` is determined by **how the function is called**, not where it's defined. Four rules, in precedence order: `new` binding → explicit (`call`/`apply`/`bind`) → method call (the object before the dot) → default (`undefined` in strict mode/modules, `globalThis` otherwise).

**Arrow functions have no `this` of their own** — they close over the enclosing lexical scope, which is why they're correct for callbacks and wrong as object methods or constructors.

**The classic failure:**
```js
const obj = { name: "x", greet() { setTimeout(function () { console.log(this.name); }, 0); } };
// undefined — the timer calls it with no receiver
```
Fix: arrow function, or `.bind(this)`.

**The senior point:** modern code largely sidesteps this by using arrows and modules. Being able to *read* it still matters — you'll meet it in older codebases and library internals.

---

### Q5. [Intermediate] 🔥 What does TypeScript actually give you, and what doesn't it?

**Strong answer covers:** compile-time structural type checking that **erases entirely** at runtime. It catches type errors before execution and drives editor tooling. It does **not** validate data at runtime.

**The consequence that matters most:**
```ts
const user: User = await res.json();   // ✗ a lie — `any` cast to User
```
**Nothing checked that.** If the API changed, you have a `User`-shaped hole and a crash somewhere unrelated. **Validate at the boundary** with `zod`/`valibot`, then the type is earned rather than asserted → [[backend/frameworks/python/01-fastapi/README|the same argument for Pydantic]].

**Details that matter:**
- **Structural, not nominal** — anything with the right shape satisfies the type. Two unrelated interfaces with identical members are interchangeable
- **`any` disables checking and spreads.** Prefer `unknown`, which forces you to narrow
- **Narrowing** via `typeof`, `instanceof`, `in`, and custom type guards (`x is Foo`)
- **Generics** for relating input and output types; `keyof`, mapped and conditional types for the library-level work
- **`strict` is worth the cost**, especially `strictNullChecks` — that flag alone eliminates a whole bug class

**The senior point:** TypeScript's value is proportional to how much it's told. A codebase full of `any` and `as` casts has the build cost and none of the benefit.

---

### Q6. [Intermediate] Explain promises, `async/await`, and how you handle concurrent work.

**Strong answer covers:** a promise is an object representing a future value in one of three states. `async/await` is syntax over the same machinery — `await` suspends the function and yields to the event loop.

```js
const [a, b] = await Promise.all([fetchA(), fetchB()]);   // concurrent
const a = await fetchA(); const b = await fetchB();       // sequential — 2x slower
```

**Details that matter:**
- **`Promise.all` rejects on the first failure** and the others keep running unawaited. `Promise.allSettled` when you want every result
- `Promise.race` (first to settle) vs `Promise.any` (first to *fulfil*)
- **An unhandled rejection crashes a Node process** by default in modern versions
- `await` in a `for` loop is sequential. `.map` + `Promise.all` is concurrent — **and needs a concurrency cap** for large arrays, or you open 10,000 sockets
- **Every network call needs a timeout** — `AbortController` in the browser and Node

**The senior point:** this is the same set of mistakes as [[languages/06-python/17-asyncio-in-depth|asyncio]] — sequential awaits masquerading as concurrency, and unbounded fan-out. **Recognising that they're the same bug in two languages is what a strong answer sounds like.**

---

### Q7. [Advanced] How does JavaScript manage memory, and how do you leak?

**Strong answer covers:** a tracing garbage collector, generational, with a fast nursery for short-lived objects. Anything **reachable** from a root is retained.

**The leaks that actually happen in frontend code:**
- **Listeners not removed** on unmount — the handler's closure retains the whole component scope
- **Timers/intervals not cleared**
- **Detached DOM nodes** still referenced by JS
- **Unbounded caches and module-level arrays** that only grow
- **Closures capturing more than intended** — one small callback pinning a large object

**How you'd find one:** Chrome DevTools → Memory → heap snapshots at three points, compare retained size, look for detached nodes. The Performance panel's memory line going up-and-to-the-right across repeated interactions is the signal.

**The senior point:** the cleanup function in `useEffect` exists for precisely this, and StrictMode's double-invoke in development is designed to expose a missing one.

---

## Related
- [[frontend/interview/01-react-rendering-and-performance|React, rendering & performance]]
- [[frontend/interview/03-state-data-and-architecture|State, data & architecture]]
- [[backend/frameworks/javascript/01-node-runtime/README|the Node runtime]] — the event loop, server-side
- [[backend/interview/02-node-runtime-and-api|Node interview prep]]

*Source: [reference] — the language round, assembled Aug 2026.*
