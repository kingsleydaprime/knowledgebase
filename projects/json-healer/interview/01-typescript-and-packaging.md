# json-healer — TypeScript, Types & Packaging

Everything from Milestone 1 and Milestone 10: config, type design, build tooling, publishing.

---

### Q1. [Beginner] Your `package.json` has an `exports` map with separate `import` and `require` entries. Why isn't one entry point enough?

**Strong answer covers:** a published package is consumed by both ESM (`import`) and CJS
(`require()`) callers, and they need physically different files — `dist/index.js` vs
`dist/index.cjs`. Each also needs its *own* type declaration (`.d.ts` vs `.d.cts`), because
TypeScript resolves types per module format; shipping one `.d.ts` for both is the classic reason
a package "has no types" under `moduleResolution: node16`. The consumer never has to know which
one they got.

**Follow-up they'll push on:** *"What's the dual-package hazard?"* — two copies of the module
loaded in one process, so `instanceof` across the boundary fails and module-level state diverges.
It doesn't bite json-healer because the library is stateless pure functions, but say that
explicitly rather than pretending the hazard doesn't exist.

---

### Q2. [Intermediate] 🔥 Your `tsconfig.json` deliberately includes neither `"DOM"` nor Node types. What does that buy you, and what does it cost?

**Strong answer covers:** the PRD requires the library to run in Node *and* the browser. Rather
than enforcing that by discipline ("remember not to use `window`"), omitting both type libs makes
it a **compile error** to touch `window`, `document`, `Buffer` or `process`. The constraint is
enforced structurally by the type system instead of by code review. Cost: you can't use any
platform API even where it would be convenient, and you need a deliberate escape hatch if that
ever changes.

**Follow-up:** *"When would that be the wrong call?"* — the sibling project `strictenv` is the
counter-example: it's Node-only by design (`process.env`, file reads), so it adds
`"types": ["node"]`. The isomorphic trick only makes sense when the code genuinely has no
platform dependency. Being able to name the opposite decision and why is the whole answer.

---

### Q3. [Intermediate] What does `noUncheckedIndexedAccess: true` change, and why did this project in particular want it?

**Strong answer covers:** `str[i]` becomes `string | undefined` rather than `string`. In a library
whose entire middle section is a character-by-character scanner walking string boundaries,
off-by-one at the end of input is the dominant bug class — the flag turns "I read one past the
end" from a silent `undefined` at runtime into a compile error at the point of the read.

---

### Q4. [Intermediate] You wrote `class HealError extends Error` and had to add `Object.setPrototypeOf(this, HealError.prototype)`. Explain that.

**Strong answer covers:** when TS downlevels `class X extends Error` to an older ES target, the
built-in `Error` constructor returns a fresh object and the prototype chain isn't restored, so
`err instanceof HealError` silently returns `false`. The manual `setPrototypeOf` in the
constructor repairs the chain. It's a general gotcha for subclassing *any* built-in (`Error`,
`Array`, `Map`), not something specific to this library.

**Follow-up:** *"How would you have caught this if you didn't already know it?"* — a test that
asserts `expect(() => healJson('garbage')).toThrow(HealError)`, not just `.toThrow()`.

---

### Q5. [Intermediate] 🔥 `healJson<T>()` is generic. Does it validate that the parsed JSON matches `T`?

**Strong answer covers:** **No.** The generic is a *type-level* convenience — it tells TypeScript
what shape to assume downstream and does zero runtime checking. If the JSON doesn't match `T`,
nothing in the library catches it. That's a deliberate non-goal in the PRD (runtime validation is
Zod's job); the risk is that callers assume `healJson<MyType>()` validates, so it belongs in the
README, not just in the code.

This is a great question to *volunteer* — knowing the limits of your own API reads as senior.

---

### Q6. [Beginner] What is `HealResult<T>` and why a discriminated union instead of `{ data?, error? }`?

**Strong answer covers:** `{ success: true; data: T } | { success: false; error: string }`.
TypeScript narrows on `success`, so `result.data` is only reachable in the success branch — no
non-null assertions, no "I know it's there" comments. The optional-fields version would let you
read `data` on a failure and get `undefined` with no complaint.

**Follow-up:** *"Why does `healJson` throw while `tryHealJson` returns a result?"* — two audiences.
`tryHealJson` does the real work; `healJson` is a thin wrapper that adapts its output by throwing.
The important part is that the wrapper never grows its own duplicate logic, even once the pipeline
got complex.

---

### Q7. [Intermediate] Why tsup? Why not Vite, Rollup, or just `tsc`?

**Strong answer covers:** the deliverable is a *library*, not an app. `tsc` alone emits JS but
won't produce a bundled `.d.ts` or a dual CJS/ESM output. Vite is app/dev-server-oriented (and
"vitest" being Vite-based is a genuinely easy mix-up to explain away). Rollup does the job but
needs a plugin stack. tsup wraps esbuild with the exact library defaults needed — dual format,
bundled types, minify, target — in about ten lines of config.

---

### Q8. [Advanced] You enforce a gzip size budget with `size-limit`. Why is that a build-time gate rather than a note in the README?

**Strong answer covers:** a size target that isn't checked in CI is a wish. Setting the budget at
the *real* PRD number from milestone 1 — not a comfortable one — means every subsequent milestone
either fits or forces an explicit, documented decision to loosen it. Budgets set generously and
tightened later never actually get tightened.

**Follow-up:** *"What actually drives bundle size in a zero-dep library?"* — mostly the code you
wrote, so the trade-off lands on things like regex tables and error-message strings, not on
transitive dependencies.

---

### Q9. [Beginner] "Zero dependencies" — but your `devDependencies` list is long. Is that dishonest?

**Strong answer covers:** no — the claim is about *runtime* dependencies, the ones that end up in
a consumer's `node_modules` and their supply-chain surface. `tsup`, `vitest`, `typescript`,
`size-limit` never ship. That distinction is precisely what lets a project be genuinely zero-dep
*and* use a modern toolchain instead of hand-rolling a build system.

---

### Q10. [Intermediate] Walk me through publishing this to npm, including moving it under a scoped org.

**Strong answer covers:** the shipping loop — version bump, build, `npm publish` (with
`--access public` for a scoped package, since scoped defaults to restricted), tags and release
notes on GitHub. Moving to a company-owned scope means publishing under the new name and
**deprecating** the old one with a message pointing at the replacement, rather than unpublishing —
unpublish breaks every existing install. Mention that npm surfaces alarming-looking errors during
scope moves that are usually permission/access-flag issues rather than anything destructive.

---

### Q11. [Beginner] How do you test a library like this, and what did you test first?

**Strong answer covers:** vitest, tests written per milestone against the *behaviour* (malformed
string in → parsed object out), not against internals. First tests were the two ends of the range:
valid JSON on the fast path, and unrecoverable garbage producing a `HealError` / failure result.
Fixing the contract at both extremes before filling in heal steps means every later milestone is
adding capability inside a known boundary.

---

### Q12. [Advanced] Where would type-checking catch a bug that your tests wouldn't, and vice versa?

**Strong answer covers:** they're different passes. vitest transpiles and runs — it catches wrong
*behaviour* but happily runs code `tsc` would reject, because transpilation strips types without
checking them. `tsc --noEmit` catches contract errors (a nullable value used as non-null, a
narrowing that doesn't hold) in code paths no test exercises. Running both separately in CI is the
point; treating a passing test suite as proof the types are sound is the mistake.
