# strictenv — The TypeScript Type System

The hardest part of this project, and the part worth the most in an interview. Milestones 2–4.

---

### Q1. [Intermediate] 🔥 Your schema config is a flat discriminated union, one member per `type`. Why not a generic `EnvField<T>`?

**Strong answer covers:** the goal is to correlate two fields of the same object literal — `type`
and `default` — so `{ type: "number", default: "oops" }` is a compile error. A generic
`EnvField<T>` doesn't reliably do that per-property inside an object literal: TS has a known
inference gap there, so the mismatch either type-checks silently or wrecks the return-type
inference. Contextually typing the literal against a concrete union means TS picks the member by
`type` and checks `default` against *that member's* concrete type, flagging the error exactly where
it was written.

**Follow-up:** *"How did you prove it works?"* — `@ts-expect-error` test cases in
`tests/types.test.ts`, one per wrong-default combination. A type-level guarantee needs a
type-level test; a runtime test can't observe it at all.

---

### Q2. [Advanced] 🔥 `IsGuaranteed<F>` checks `F extends { default: FieldValue<F> }` rather than `"default" extends keyof F`. Why does that distinction matter?

**Strong answer covers:** `default` is declared as an *optional* key (`default?: string`), so
`"default" extends keyof F` is `true` for every field — even one that never supplied a default.
That check answers "is this key declared as allowed?", not "was a value actually provided."
Checking against the *value type* is what distinguishes the two. Get it wrong and every optional
field with no default gets typed as guaranteed-present, which is the exact failure the library is
supposed to prevent.

---

### Q3. [Advanced] 🔥 Explain how `InferEnv<S>` makes some keys required and others optional.

**Strong answer covers:** TypeScript's mapped-type optionality modifier (`?:`) is fixed for the
whole mapped type — you cannot make it conditional per key inside one. So you build **two** mapped
types: one containing only the guaranteed keys (via `as ... extends true ? K : never` key
remapping to filter the rest out) with no modifier, and one containing only the rest, marked `?:`.
Then intersect them with `&`. The two-mapped-types-intersected pattern is the standard idiom for
"optionality decided per key by a condition."

**Follow-up:** *"What does `as ... : never` do in a mapped type?"* — key remapping; a key mapped to
`never` is dropped from the resulting type entirely. That's the filtering mechanism.

---

### Q4. [Advanced] What is `Simplify<T>` and what real problem did it solve for you?

**Strong answer covers:** `{ [K in keyof T]: T[K] }` — it flattens a type into one plain object
instead of leaving it as a deferred intersection. The concrete problem: `expectTypeOf<InferEnv<S>>()`
failed with "Expected 1 arguments, but got 0" even though the zero-arg overload exists. Bisected
from a minimal repro: a single mapped type with `as` remapping worked; **two** such mapped types
intersected with `&` broke it. TypeScript can leave that kind of intersection *unresolved* in a way
that trips tooling built on deep generic introspection — hover tooltips, `expectTypeOf` — even
though ordinary usage (assigning objects, `extends` checks) works fine. Wrapping in `Simplify`
resolved it, and as a bonus IDE hover now shows a flat object instead of `A & B`.

**What makes this a strong answer:** the debugging method. Minimal repro, remove one piece at a
time, notice the failure moves rather than disappears. That's more interesting to an interviewer
than the fix.

---

### Q5. [Intermediate] You have exactly one type assertion in the library — `value as InferEnv<S>`. Defend it.

**Strong answer covers:** `validateSchema` builds a plain object in a loop; `InferEnv<S>` is a
compile-time conditional computation. TypeScript cannot verify that runtime loop logic satisfies a
computed conditional type — nothing can, unassisted. So an assertion is genuinely required. What
matters is the discipline around it: **one** assertion, placed exactly at the trust boundary
between dynamic and static typing, with a comment explaining *what actually guarantees* the shape
holds (per-field logic only skips assignment when the value is `undefined`, which by construction
only happens for genuinely optional fields). The failure mode isn't having an assertion — it's
scattering `as any` through the call sites so the boundary becomes unfindable.

---

### Q6. [Intermediate] 🔥 You extracted an `isAbsent(raw)` helper and it broke type-checking. What happened?

**Strong answer covers:** `isAbsent(raw): boolean` returns a plain boolean, not a type predicate.
TS's control-flow analysis narrows on literal equality checks written **inline** (`raw === undefined`),
but it does not see through an arbitrary function call — so after `if (isAbsent(raw)) return;`,
`raw` was still `string | undefined` and `raw.toLowerCase()` failed. Fixed by inlining the check.

**The follow-up that separates good from great:** *"Why not just write it as a type predicate?"* —
because that would have been actively **wrong**. The function returns `true` for both
`raw === undefined` *and* `raw === ""`, and only the first is typed `undefined`. A predicate
`raw is undefined` would make TS believe the empty-string case was `undefined`, mislabelling a
value that later gets stored in the error record. A type predicate must describe what's actually
true at runtime — using one to silence a narrowing complaint is how you get a lie in the type
system.

---

### Q7. [Intermediate] What's the difference between what `npm test` catches and what `npm run typecheck` catches here?

**Strong answer covers:** vitest transpiles and runs — it strips types without checking them, so it
catches wrong behaviour and misses type contract violations. `tsc --noEmit` catches the contract
errors in paths no test exercises. In this project the split was concrete: the `isAbsent` narrowing
bug failed typecheck while every test passed. Both run separately in CI, on purpose.

---

### Q8. [Advanced] Someone calls `defineEnv` with an `onError` that neither throws nor exits. What does your function return, and is that acceptable?

**Strong answer covers:** it returns `undefined as unknown as InferEnv<S>` — the "typed" result is
not trustworthy in that specific case. That's an honest limit: once a caller-supplied callback
controls control flow, no static type can guarantee the function's own return contract. The
decision was to **document it in JSDoc on the exported function** rather than paper over it with
runtime warnings or extra machinery. Naming a sharp edge in the public API docs is better
engineering than pretending it doesn't exist, and an interviewer will read the willingness to say
so as a good sign.

**Follow-up:** *"Could you have designed it away?"* — yes: type `onError` as returning `never`, so
TS forces it to throw or exit. Worth mentioning as the alternative, along with why it's a stricter
contract than some callers want (an `onError` that just logs and lets a caller handle the rest).

---

### Q9. [Beginner] Why is `FieldResult` a discriminated union instead of returning `null` on failure?

**Strong answer covers:** `{ ok: true, value } | { ok: false, error: EnvError }` carries *why* it
failed, structurally — which key, what the raw value was, which rule broke. That structure is what
the M7 table renderer consumes and what a user's `onError` receives. Returning `null` would force
the caller to reconstruct the reason, and a coerced `0` or `false` is a legitimate value that
`null`-based signalling would be tempted to conflate with failure.

---

### Q10. [Advanced] How does this compare to using Zod for env validation?

**Strong answer covers:** Zod is a general-purpose runtime schema validator — far more capable, and
a dependency with real bundle weight. strictenv is deliberately narrow: env values are always
strings, so the coercion rules are fixed and small, the failure mode is always "die at boot with a
table", and the whole thing fits in under 2KB gzipped with zero runtime deps. The honest framing:
if a project already has Zod, `z.coerce` plus a `safeParse` at boot covers most of this. strictenv
earns its place when you want no dependency, boot-time enforcement as the default behaviour rather
than something you wire up, and coercion semantics chosen specifically for env-var edge cases
(`""`, `"0"`, `"false"`).
