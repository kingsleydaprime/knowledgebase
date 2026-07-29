# strictenv — Learning Log

Building a zero-dependency TS micro-library that turns `process.env` into a typed, validated, auto-coercing boot-time check (see `PRD.md` / `plan.md` in the project repo: `/home/kingsleydaprime/code/spectroniq/projects/strictenv`). Each milestone entry follows: **Concept / What I built / What broke first / Key insight**.

---

## Milestone 1: Scaffold

**Concept:** Project/TS config for a **Node-only** package, contrasted with the sibling `json-healer` project's isomorphic setup. Dual-format (`CJS`+`ESM`) `package.json` `exports` map. Test runner + build tool wiring (`vitest`, `tsup`).

**What I built:**
- `package.json` with the same dual `exports` map shape as `json-healer` (`import` → `dist/index.js` + `dist/index.d.ts`, `require` → `dist/index.cjs` + `dist/index.d.cts`) and a `size-limit` entry targeting the PRD's literal **2 KB** gzip budget (not a relaxed one — we start at the real target and only loosen it later if a milestone genuinely can't fit, with a documented reason, same discipline as `json-healer`'s M10).
- `tsconfig.json`: unlike `json-healer` (which sets `"types": []` and avoids both DOM and Node lib types to stay isomorphic, since it's pure string transforms with no I/O), `strictenv` is explicitly Node-only per the PRD (`process.env`, `process.exit`, file reads for `.env` parsing) — so this project's `tsconfig.json` adds `"types": ["node"]` and a real `@types/node` devDependency. Still no `"DOM"` in `lib`, since there's no browser surface needed either. This is a deliberate, opposite choice from the sibling project, not an oversight — the isomorphic trick only makes sense when the code genuinely has no platform dependency.
- `tsup.config.ts` / `vitest.config.ts`: identical shape to `json-healer`'s (dual CJS/ESM build with bundled `.d.ts`, minified, ES2020 target; vitest picking up `tests/**/*.test.ts`).
- `src/index.ts` — just a version-string stub for now (no real API yet); `tests/index.test.ts` — one trivial test to prove the whole pipeline (`vitest` → transpile → run) actually works end-to-end before any real logic exists.

**What broke first:** Nothing — this milestone is pure config, verified by running `npm test`, `npm run typecheck`, and `npm run build` all successfully in sequence (test pipeline, type pipeline, and bundler pipeline are three separate tools that can each be individually misconfigured, so checking all three separately here — rather than assuming one working implies the others do — is the actual point of this milestone).

**Key insight:** "Zero dependencies" in the PRD refers to *runtime* dependencies only — `devDependencies` (`tsup`, `vitest`, `typescript`, `@types/node`, `size-limit`) are unrestricted, since none of them end up in the published bundle. This exact distinction between `dependencies` and `devDependencies` is what makes projects like this "zero-dep" *and* still use a modern toolchain, rather than needing to hand-roll a build/test system too.

---

## Milestone 2: Core type inference (`InferEnv`)

**Concept:** Discriminated unions vs. generic type parameters for correlating two fields of a config object at the type level; mapped-type key remapping (`as ... extends true ? K : never`) to conditionally split an object's keys into "required" vs. "optional" groups; a real TS quirk around type-only test tooling and unresolved intersections.

**What I built:**
- `src/types.ts` — `EnvFieldConfig` as a **flat discriminated union**, one member per `type` value (`"string"`/`"number"`/`"boolean"`), each with its own concretely-typed `default`. This was a deliberate choice over a generic `EnvField<T>` shape: a generic doesn't correlate `type` and `default` per object-literal property (a known TS inference gap — `{ type: "number", default: "oops" }` could silently type-check or the return-type inference could break), whereas contextual typing against a concrete union catches the mismatch as a compile error right where the literal is written. Verified with two `@ts-expect-error` test cases (`tests/types.test.ts`) — one for a string `default` on a `"number"` field, one for a string `default` on a `"boolean"` field.
- `IsGuaranteed<F>` — a field's value counts as "guaranteed present" (non-optional in the final result) if `required: true`, **or** if it has an actual `default` value. The subtle part: this has to check `F extends { default: FieldValue<F> }` (does the *value type* match), not `"default" extends keyof F` — because `default` is declared as an *optional* key (`default?: string`), so `"default" extends keyof F` is `true` even when the field never set one. Checking against the value type is what correctly distinguishes "declared as allowed" from "actually provided."
- `InferEnv<S>` — two mapped types (one for guaranteed keys, one for the rest, marked `?:`) combined with `&`. This two-mapped-types-intersected pattern is the standard idiom for "some keys required, some optional, decided per-key by a condition" — TS mapped-type optionality (`?:`) can't be made conditional *within* a single mapped type's modifier, so you build two separate objects (each only containing the keys that belong in that half, via `as ... extends true ? K : never` remapping) and intersect them.
- `Simplify<T>` — a small wrapper (`{ [K in keyof T]: T[K] }`) applied around the final `&` intersection.

**What broke first:** The type itself compiled fine, but `npm run typecheck` failed inside the *test file*, not `types.ts` — `expectTypeOf<InferEnv<S>>().toEqualTypeOf<{...}>()` reported `Expected 1 arguments, but got 0`, even though `expectTypeOf` has a documented zero-argument overload specifically for this use case. Bisected by writing a minimal repro from scratch and removing pieces one at a time: a single mapped type with `as` remapping worked fine; the same two mapped types *intersected with `&`* is what broke it — even after assigning the intersection to a `declare const value: M<...>` and passing that concrete value into the 1-argument overload instead, the failure just moved to the next call in the chain (`.toEqualTypeOf<...>()`). The fix was wrapping the whole intersection in `Simplify<T>` before handing it to `expectTypeOf` — once flattened into one plain object type (not left as an unresolved `&` of two deferred mapped types), the exact same test code worked with no other changes.

**Key insight:** An intersection of two *mapped types with conditional key remapping* is a fundamentally different animal from an intersection of two already-concrete object types (`{a:1} & {b:2}`, which works fine everywhere, including in `expect-type`'s own documented examples) — TypeScript can leave the former "unresolved"/deferred in a way that trips up tooling built on deep generic introspection (hover tooltips, `expectTypeOf`), even though normal *usage* of the type (assigning objects to it, structural checks via `extends`) works completely fine. `Simplify<T>` is the standard fix for this class of problem, and it's cheap enough (and improves IDE hover output, showing a flat object instead of `A & B`) that it's worth applying to `InferEnv`'s final output unconditionally, not just as a one-off test workaround.

---

## Milestone 3: Coercion + validation (`validateField`)

**Concept:** Deliberately encoding the PRD's success-metric edge cases (`""`, `"0"`, `"false"`) as the *design* of the coercion logic rather than as an afterthought; a plain-boolean helper function silently defeating TS control-flow narrowing.

**What I built:**
- `src/validate.ts` — `validateField(key, raw, config)` returns a small `FieldResult` discriminated union (`{ok:true, value} | {ok:false, error: EnvError}`), one field at a time (whole-schema aggregation is M4).
- The **"absent" check runs first**, before any type-specific coercion: `raw === undefined || raw === ""` are treated identically — both fall through to `default` (if set) or a `"missing"` error (if `required`) or plain `undefined` (optional, no default). This is the direct implementation of the PRD's named success metric: an empty string must never be reported as an *invalid* number/boolean, it's simply "not set."
- **Boolean coercion is a narrow allow-list** (`raw.toLowerCase() === "true"` / `"false"`, nothing else), not `Boolean(raw)` truthiness — `Boolean("false")` is `true` in plain JS, which is exactly the class of bug this whole library exists to prevent, so the allow-list approach isn't just stricter, it's the actual point of the type.
- **Number coercion** guards whitespace-only strings (`raw.trim() === ""`) before calling `Number()` at all, because `Number(" ")` evaluates to `0` in JavaScript — without this guard, a value like `PORT="   "` would silently validate as `0` instead of being reported as invalid. `"0"` itself, though, must validate successfully as `0` (checked via `Number.isNaN(Number(raw))`, not by checking falsiness of the *result*, which would wrongly reject a legitimate `0`).

**What broke first:** `npm run typecheck` (not `npm test` — this is exactly why the plan calls out that vitest's transpile-based test run and `tsc --noEmit` catch different classes of bugs). The first version pulled the absent-check into its own helper function, `isAbsent(raw): boolean`. That's a plain boolean return, not a type predicate (`raw is X`) — so even though the helper's logic was correct at runtime, TypeScript had no way to narrow `raw` from `string | undefined` down to `string` after `if (isAbsent(raw)) { return ... } ` and calling `raw.toLowerCase()` a few lines later still saw `raw` as possibly `undefined`. Fixed by inlining the `raw === undefined || raw === ""` check directly instead of hiding it behind a function call — TS's control-flow analysis narrows on literal equality checks written inline, but it does not "see through" an arbitrary function call to know that a `true` return means the checks it performed inside are now guaranteed by the caller.
- Note this could also have been fixed by writing `isAbsent` as a real type predicate (`raw is undefined`) — but that would have been actively wrong here, since the function returns `true` for both `raw === undefined` *and* `raw === ""`, and only the first case is actually typed `undefined`. A type predicate must describe what's actually true at runtime; using one just to satisfy the narrowing would have made `raw`'s type say `undefined` even in the `""` case, silently mislabeling the value that later gets stored in `EnvError.raw`.

**Key insight:** Extracting an early-return "is this thing absent" check into its own function feels like the obviously cleaner refactor, but it has a real cost here: it breaks TypeScript's control-flow narrowing unless deliberately restored via a type predicate — and a type predicate is only honest to write when it's actually describing a single, precise type transition, not a fuzzy "close enough" condition covering two different underlying values (`undefined` vs `""`). When a helper would need a "dishonest" predicate to make the types line up, that's a signal to just inline the check instead, not to force a predicate onto it.

---

## Milestone 4: Whole-schema validation + placeholder `defineEnv`

**Concept:** Composing many independent per-field checks into one aggregated result; the one deliberate, "trust me" type assertion needed to bridge a dynamically-built object into a statically-computed conditional type.

**What I built:**
- `validateSchema<S>(schema, merged)` in `src/validate.ts` — loops every key in the schema, calls `validateField` per key, and either collects every failure into `errors: EnvError[]` (not stopping at the first one — the table report in M7 needs the complete picture) or builds up a plain `Record<string, string|number|boolean>` of successful values.
- The one interesting line: `return { success: true, value: value as InferEnv<S> }`. `InferEnv<S>` is a *type-level* computation (conditional per-key optionality based on `required`/`default`) — there's no way for TypeScript to verify, at the point of building a plain mutable object in a loop, that it structurally matches that computed type, because the loop's logic (not the type checker) is what's actually enforcing "every guaranteed key got a value." This is a legitimate, deliberate type assertion, not a shortcut — the correctness guarantee comes from `validateField`'s per-field logic (only skipping assignment when `result.value === undefined`, which by construction only happens for genuinely-optional fields) rather than from anything TypeScript can check unassisted.
- `defineEnv(schema)` in `src/index.ts` — a placeholder version for now (no `.env` file loading yet, that's M5/M6; no color-coded report or `onError`, that's M7/M8): merges only real `process.env` (filtering out the `undefined`-typed entries `Object.entries(process.env)` can technically produce) and throws a plain `Error` listing every failing key on validation failure.

**What broke first:** Nothing broke — this milestone was straightforward composition of already-tested pieces (`validateField` from M3, `InferEnv` from M2). The only real design decision was *where* to put the type assertion (right at the `validateSchema` return, in one place) rather than scattering `as any`/`as InferEnv<S>` casts throughout `defineEnv` or the tests — keeping the "trust boundary" between dynamic and static typing in exactly one, well-commented spot.

**Key insight:** A generic-heavy public API can still need exactly one manual type assertion at its core — the goal isn't to eliminate every assertion (impossible when bridging a runtime loop into a compile-time-computed conditional type), it's to make sure there's only one, it's positioned at the actual trust boundary, and it's accompanied by a comment explaining *why* it's safe (what actually guarantees the shape matches) rather than just being an unexplained `as X` some future reader has to take on faith.

---

## Milestone 5: `.env` file parser (`dotenv.ts`)

**Concept:** Line-based parsing vs. a full character-level state machine — recognizing when the simpler tool actually fits the problem; escape-sequence processing, including a genuinely tricky regex-alternation-order edge case.

**What I built:**
- `parseEnvFile(content): Record<string,string>` — splits on `\r\n|\n|\r` and processes each physical line independently: skip blank/`#`-comment lines, split on the *first* `=`, trim the key, then classify the value as single-quoted (literal, no escapes), double-quoted (escape-processed), or unquoted (trailing-whitespace trimmed).
- The "multiline via `\n` escape" requirement turned out to need **no cross-line logic at all** — a value like `MULTI="line1\nline2"` is a literal two-character `\n` sequence sitting inside one physical line's quotes, which the escape processor already turns into a real newline character. This was worth confirming explicitly against the PRD wording before building anything, since "multiline" could easily have been misread as "a value spanning multiple physical lines" (the way some real dotenv-flow tools support triple-quoted multi-line blocks) — that's a materially different, harder feature the PRD doesn't actually ask for.
- Escape handling for double-quoted values: `\n`→newline, `\"`→`"`, `\\`→`\`, done via one regex (`/\\n|\\"|\\\\/g`) with a replacer function — anything else with a backslash passes through untouched (documented limitation, not silently wrong).

**What broke first:** Nothing broke in the sense of a failing test after the fact — the tricky part was reasoning through, *before* writing the test, what a regex alternation actually does with an ambiguous input like `a\\nb` (an *escaped backslash* immediately followed by a literal `n`, as opposed to the real `\n` newline escape). JS regex alternation (`A|B|C`) tries each branch **left-to-right at a given position and takes the first match, not the longest one** — so for the 2-char escape alternatives here, correctness depends on `\\` (escaped backslash) being checked as its own branch rather than assuming a leading backslash always belongs to a `\n`/`\"` escape. Traced through by hand: at the first backslash, the very next character is *also* a backslash, so the `\\` branch matches immediately (2 chars consumed, replaced with one real backslash) and the following `n` is left completely alone as a plain character — giving `a` + `\` + `n` + `b`, not a newline. Wrote this exact case as its own named test (`does not misinterpret an escaped backslash followed by a literal n`) rather than trusting the reasoning silently.

**Key insight:** "Multiline" and "multi-character-escape-inside-one-line" sound almost interchangeable when skimming a PRD line, but they imply completely different parser architectures (a real per-physical-line-spanning feature would need to track "am I still inside an open quote" *across* `content.split("\n")` boundaries, i.e. exactly the kind of cross-line state that would justify a heavier state machine). Reading the requirement literally — and checking it against the concrete example syntax — is what kept this milestone from accidentally over-building a feature that wasn't actually being asked for.

---

## Milestone 6: Multi-file loading + `process.env` precedence (`loadEnv.ts`)

**Concept:** Discriminating error codes (`ENOENT` vs. everything else) instead of blanket try/catch; precedence/merge-order reasoning across two different axes (file-vs-file, and files-vs-real-environment); defensive filtering against a type that's technically wider than what actually occurs at runtime.

**What I built:**
- `loadEnv(options)` — normalizes `path` (`string | string[] | undefined`) to an array, defaulting to `[".env"]` when unset.
- Reads each path **in order** with `readFileSync`, merging parsed results into one `fileEnv` object via `Object.assign` — later files in the array win on key collisions (so `path: [".env", ".env.local"]` lets `.env.local` override `.env`, matching the common convention from tools like `dotenv-flow`).
- **`ENOENT`-only silent skip**: `readFileIfExists` catches the exception from `readFileSync`, but only swallows it if `err.code === "ENOENT"` (file genuinely doesn't exist) — anything else (e.g. a permissions error on a file that *does* exist) is re-thrown. A blanket `catch { return undefined }` would have been the easy version, but it would silently hide a real, actionable problem (a broken file) behind the same "nothing to see here" behavior meant only for "this optional file wasn't there."
- **Two separate precedence questions, each with its own knob:** which *file* wins when multiple files define the same key (always: later array position, no config needed) vs. whether *file values* or *real `process.env`* wins (`override` option, defaulting to `false` = real environment wins) — these are conceptually different precedence axes and it was worth keeping them as two distinct, separately-tested behaviors rather than one blurred "merge order" concept.
- A defensive filter (`if (value !== undefined) realEnv[key] = value`) when copying from `process.env` — its TS type is `Record<string, string | undefined>` even though, in practice, Node never actually populates it with `undefined`-valued keys. Filtering explicitly here means the code's *runtime* behavior doesn't quietly depend on an assumption about Node internals that isn't enforced by the type system itself.

**What broke first:** Nothing broke — every test (fixture-file loading, multi-file override order, missing-file skip, both `override` directions) passed on the first run. The design work for this milestone was almost entirely in the planning stage (working out the two precedence axes and the `ENOENT`-specific catch) rather than in debugging after the fact.

**Key insight:** `try/catch` around I/O is often written as "catch anything, treat it as absence" — but that conflates two very different failure modes (expected absence vs. unexpected error) into one code path. Checking `err.code` (Node's `ErrnoException` convention) to distinguish them is a small amount of extra code that changes the failure behavior from "silently pretend nothing's wrong" to "only stay silent about the one specific thing you actually expected to sometimes not be there."

---

## Milestone 7: Terminal reporting (`colors.ts` + `report.ts`)

**Concept:** Hand-written ANSI escape codes as a zero-dependency alternative to `chalk`/`picocolors`; respecting the informal but real `NO_COLOR` ecosystem convention; padding-based table alignment; why testing "is this aligned" needs care when the padding itself is made of the same whitespace as the column separator.

**What I built:**
- `src/colors.ts` — `createColors(enabled)` returns wrapper functions (`red`, `bold`, `dim`, `cyan`) closing over a single `enabled` boolean, rather than each wrapper reading global state — keeps the module side-effect-free and the color decision threaded through explicitly instead of hidden behind a mutable flag.
- `shouldUseColor()` — checks `"NO_COLOR" in process.env` (key *presence*, not truthiness — the [no-color.org](https://no-color.org) convention says even `NO_COLOR=""` should disable color) and `process.stdout.isTTY` (so piped/CI output doesn't get raw escape codes dumped into logs). This wasn't explicitly demanded by the PRD, but it's a one-line, well-established nicety worth the small addition.
- `src/report.ts` — `renderErrorTable(errors)` computes each column's width as `max(header.length, ...allCellLengthsInThatColumn)`, then `padEnd`s every cell to that width *before* wrapping it in a color code — padding first matters because ANSI codes add invisible characters around the text; if you colored first and padded second, `padEnd` would count the escape-code characters as visible width and misalign the table.
- Default failure behavior: `reportFailure(errors)` → `console.error(renderErrorTable(errors))` then `process.exit(1)`, matching the PRD directly (the `onError` override arrives in M8).

**What broke first:** Not the implementation — my own **test**. I wrote a check for "the two data rows have equal first-column width" by splitting each rendered line on a `/\s{2,}/` (2-or-more-whitespace) regex and comparing the length of the first chunk. That failed with "12 vs 4" even though the actual table output was correctly aligned. The reason: the column separator between cells is also whitespace (2 spaces), and the *padding* added to a shorter cell is also whitespace — so for the shorter `"PORT"` row, the trailing pad spaces and the separator spaces are contiguous, and a `/\s{2,}/`-based split swallows them all as one delimiter, silently un-padding the very thing being measured. For the row that's already at the column's max width (`"DATABASE_URL"`, no padding needed), there's nothing to swallow, so it measured correctly by accident — which is what made the mismatch confusing at first rather than obviously a test bug. Fixed by asserting exact expected prefixes instead (`/^PORT {8} {2}/`) — computed by hand from the known column width — rather than trying to cleverly re-derive "where does column 1 end" from the same whitespace that's ambiguous by construction.

**Key insight:** When the thing you're testing *is* whitespace-based alignment, a whitespace-based test-detection method is the wrong tool — it can't distinguish "padding" from "separator" because, from a pure regex-on-characters point of view, there's no difference between them. The reliable way to verify padding/alignment is to assert an exact, hand-computed expected string (or offset), not to try to parse the rendered output back apart using the same kind of pattern that produced it.

---

## Milestone 8: Full `defineEnv(schema, options)` wiring

**Concept:** Composing independently-tested modules (M5's parser, M6's loader, M3/M4's validator, M7's reporter) into one public API; designing an escape-hatch callback option (`onError`) without silently breaking the function's own type contract; testing code whose default behavior is "terminate the process" without actually terminating the test runner.

**What I built:**
- `defineEnv(schema, options)` in `src/index.ts` now does the real thing end to end: `loadEnv({path, override})` (M6) → `validateSchema(schema, merged)` (M4) → on success, return the typed value; on failure, either call a user-supplied `onError(errors)` (receiving the structured `EnvError[]`, not a rendered string, so callers can format/log however they want) or fall through to the default `reportFailure(errors)` (M7: color-coded table + `process.exit(1)`).
- Documented, in JSDoc on the exported function (not just a code comment), the one real sharp edge: if a caller's `onError` doesn't itself `throw` or exit, `defineEnv` has nothing safe to return — it returns `undefined as unknown as InferEnv<S>`, so the "typed" result silently isn't trustworthy in that specific case. This is a real, honest limit of what static types can guarantee once a callback controls control flow, and it felt more useful to name plainly than to hide behind a runtime warning or paper over with extra machinery.
- `tests/index.test.ts` rewritten to test the *real* wiring instead of the M4 placeholder's plain-`Error`-throwing behavior: success path (full PRD example), file-loading via `path`/`override` options against the `fixtures/` files from M6, the default print-and-exit failure path, and the `onError` override path.

**What broke first:** Not a code bug — a test-design problem. The previous milestone's tests asserted `expect(() => defineEnv(...)).toThrow(...)` for the failure path, because the M4 placeholder threw a plain `Error`. Once M7's `reportFailure` (print + `process.exit(1)`) became the *real* default failure behavior, those same tests would have actually killed the vitest worker process if left unchanged — `process.exit()` really does terminate the process, test runner included, it doesn't respect try/catch. Fixed by using `vi.spyOn(process, "exit").mockImplementation(() => undefined as never)` (and similarly mocking `console.error` to keep test output clean) so the *call* to `process.exit(1)` is observed and asserted on without the mocked function actually doing what `process.exit` normally does.

**Key insight:** A function whose contract includes "may terminate the process" needs a fundamentally different testing strategy than one that throws — you can't wrap it in `expect(() => ...).toThrow()` and call it done, because by the time a real `process.exit` runs, there's no JS call stack left to catch anything in. Mocking the *specific side-effecting primitive itself* (`process.exit`, `console.error`) rather than trying to catch the effect after the fact is the general pattern for testing any "halt everything" code path.

---

## Milestone 9: PRD-traceable integration suite

**Concept:** Turning a PRD's numbered functional requirements directly into the *organization* of a test suite (one `describe` block per FR, not just "more tests somewhere") so "did we build what was asked" is answerable by reading test names, not by re-deriving it from memory.

**What I built:**
- Rewrote `tests/index.test.ts` so every `describe` block is explicitly labeled with the PRD requirement(s) it covers (`FR1/FR6`, `FR2`, `FR3/FR4`, `FR5`, `FR7`, `FR8`, `FR9/FR10`), plus one more block for the PRD's named success metric (no false-fails on `PORT="0"`, `DEBUG="false"`, an empty-string optional var).
- This surfaced one real gap: `fixtures/.env.quoted` (created back in M6 for potential future use) had never actually been exercised by a test until now — FR8 explicitly requires quoted values and the `\n` multiline escape, and nothing in the M5–M8 test suites had exercised that fixture end-to-end through the *real* `defineEnv` path (only through the lower-level `parseEnvFile` unit tests in M5). Added a dedicated FR8 test loading that exact fixture through `defineEnv({..., }, {path: "fixtures/.env.quoted"})` to close that gap.

**What broke first:** Nothing failed — but the FR-by-FR pass is exactly what caught the unused-fixture gap above. That's the actual value of this milestone's approach: mapping tests to requirements one-to-one turns "is this covered?" from a fuzzy judgment call into a checklist with a visibly empty checkbox.

**Key insight:** Fixture files created early (for a plausible future need) can quietly go unused if nothing later loops back to check "did every fixture actually get exercised by a test that matches why it was created." A requirements-to-tests mapping pass is a cheap, mechanical way to catch that class of drift — the same discipline `json-healer`'s benchmark suite applied at the *feature* level (20+ fixtures across categories, run as an executable spec) applied here at the *requirement* level instead.

---

## Milestone 10: Build, packaging, size-check, docs

**Concept:** Verifying a gzip size budget with the actual compression algorithm (not a proxy like raw byte count); confirming both halves of a dual-format package (CJS `require()`, ESM `import`) actually work post-build, not just that the build step didn't error.

**What I built:**
- `scripts/check-size.mjs` — reads `dist/index.js`, gzips it with Node's built-in `zlib.gzipSync` (no dependency needed for this), and compares against the PRD's literal 2048-byte (2KB) budget. Actual result: **2866 bytes raw, 1383 bytes gzipped** — well under budget, unlike `json-healer` which had to relax its own budget slightly (2.5KB) to fit its larger feature set. `strictenv`'s smaller surface area (no scanner/pipeline-style internals, mostly straight-line coercion/parsing logic) meant the real 2KB target was achievable without needing to negotiate it down.
- `size-limit` (already a devDependency from M1) configured in `package.json` against the same 2KB target, as the CI-facing version of the same check — confirms **1.37kB gzipped**, matching the manual script (small delta from `size-limit`'s own bundling step).
- `README.md` and `LICENSE` (MIT, Spectroniq Limited) — README covers install, the core `defineEnv` example straight from the PRD, `.env` file loading, the `onError` escape hatch, and the full type signatures, mirroring `json-healer`'s README structure (badges, a "why this exists" paragraph, usage, API, constraints).
- **Manual dual-format smoke test**: two standalone throwaway scripts (one `.cjs` using `require()`, one `.mjs` using `import`) — both load `dist/index.cjs` / `dist/index.js` directly (not through vitest's transform pipeline, which never touches the actual built output) and call `defineEnv` against the real `fixtures/.env.quoted` file, confirming both entry points work identically post-build.

**What broke first:** Nothing — every check (tests, typecheck, build, both size checks, both smoke-test scripts) passed cleanly on the first run of this milestone. That itself is worth noting as a signal, not just a non-event: it means the earlier milestones' discipline (typecheck-and-test after every change, never letting a red suite carry forward) paid off exactly where it's supposed to — at final integration, where compounding small mistakes from nine earlier milestones would otherwise surface all at once.

**Key insight:** `vitest` transpiles and runs your *source* (`src/*.ts`) directly — it never actually imports the bundled `dist/` output, so a passing test suite says nothing about whether `tsup`'s bundling, minification, or dual CJS/ESM output are actually correct. The manual `require()`/`import` smoke test against `dist/` is the only check in the whole pipeline that verifies the thing that actually gets published to npm is the thing that works — a distinction worth remembering before assuming "all green" means "ready to publish."

---

**Final state (all 10 milestones complete):** 65 passing tests across 7 suites, clean `tsc --noEmit`, dual CJS/ESM build via `tsup`, 1.37KB gzipped (well under the 2KB budget), README + LICENSE, and a verified working `require()`/`import` smoke test against the real built output.
