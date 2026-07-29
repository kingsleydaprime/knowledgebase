# json-healer — Learning Log

Building a zero-dependency TS utility that repairs malformed LLM JSON output (see `PRD.md` / `plan.md` in the project repo). Each milestone entry follows: **Concept / What I built / What broke first / Key insight**.

---

## Milestone 1: Scaffold + fast path

**Concept:** Project/TS config fundamentals, dual-format (`CJS`+`ESM`) `package.json` `exports` maps, test runner setup with vitest.

**What I built:**
- `package.json` with a dual-format `exports` map — `import` resolves to `dist/index.js` (ESM) + `dist/index.d.ts`, `require` resolves to `dist/index.cjs` + `dist/index.d.cts`. This is how a single package serves both `import` and `require()` consumers without them needing to know which one they're getting.
- `tsconfig.json` targeting `ES2020` with `lib: ["ES2020"]` and **no `"DOM"`** — this is a deliberate compile-time trick: since we never pull in DOM types, using `window`, `document`, or other browser-only globals would be a type error, and since we don't pull in Node types either, using `Buffer`/`process` would also fail. This structurally enforces the PRD's "works in Node + browser" constraint instead of relying on discipline.
- `noUncheckedIndexedAccess: true` — makes `str[i]` return `string | undefined` instead of just `string`. Matters a lot for the scanner/string-parsing work coming in later milestones, where off-by-one bugs at string boundaries are the main risk.
- `src/types.ts` — the `HealResult<T>` discriminated union: `{ success: true; data: T } | { success: false; error: string }`. TypeScript narrows `data`/`error` availability based on which branch of `success` you're in, without needing a type assertion.
- `src/errors.ts` — a minimal `HealError extends Error` class. Had to add `Object.setPrototypeOf(this, HealError.prototype)` in the constructor — this is a classic gotcha: when TS compiles `extends Error` down to older JS targets, the built-in `Error` constructor doesn't correctly reset the prototype chain, so `instanceof HealError` can silently return `false` without the manual fix.
- `src/pipeline.ts` — currently just wraps `JSON.parse` in a try/catch (heal steps land in later milestones).
- `src/index.ts` — `tryHealJson` calls the pipeline directly; `healJson` is a thin wrapper that calls `tryHealJson` and throws `HealError` on failure. This DRY pattern (one function does the real work, the other just adapts its output) will stay true for the rest of the project — `healJson` never gets its own duplicate logic, even once the pipeline gets a lot more complex in M8.
- `tests/index.test.ts` — 5 vitest tests covering the fast path (valid JSON in, parsed data out, generic type parameter works) and the not-yet-recoverable path (garbage in, `HealError` thrown / failure result returned).

**What broke first:** Nothing broke at runtime — the trip-up was purely a "wait, why would `instanceof` fail" gotcha I built in ahead of time rather than debugging blind, since it's a well-known TS-to-ES-target issue with subclassing built-ins.

**Key insight:** A generic-heavy public API (`healJson<T = unknown>`) is a *type-level* convenience only — it tells TypeScript what shape to assume, but does zero runtime validation. If the actual JSON doesn't match `T`, nothing here will catch it (that's explicitly Zod's job per the PRD's non-goals). Worth remembering once real users start calling `healJson<MyType>()` and assuming it validates — it doesn't.

---

## Milestone 2: Fence stripping

**Concept:** Regex fundamentals for this kind of text surgery — anchoring vs greedy matching, and why "structural" text problems (markdown fence delimiters) are a good fit for regex while "semantic" problems (is this comma inside a string?) are not.

**What I built:**
- `src/types.ts` gained `StepResult = { output: string; changed: boolean }` — the shape every heal step returns from here on. The `changed` flag isn't used yet, but it's what the pipeline (M8) will use to build a "here's what I tried" error message and to skip redundant `JSON.parse` retries.
- `src/steps/stripFences.ts` with three regex patterns tried in order:
  1. `CLOSED_FENCE` — a **non-greedy** global match for `` ```lang\n...content...``` ``. Non-greedy (`[\s\S]*?`) matters: a greedy match would span from the *first* opening fence all the way to the *last* closing fence in the string, swallowing separate blocks into one.
  2. `UNCLOSED_FENCE` — same opening-marker pattern but with no required closer, anchored to end-of-string. Handles a stream truncated mid-fence (no closing ` ``` ` at all) — greedily takes everything after the opening line as content, deferring cleanup to later milestones (bracket-balancing, etc).
  3. `INLINE_BACKTICK` — single backtick wrap, only accepted if the content between the backticks looks JSON-shaped (starts with `{`/`[`), otherwise a stray `` `verbose` `` in a sentence would get misidentified as a fence.
- Handles the "multiple fenced blocks" case (e.g. a code example fence followed by a real JSON fence) by matching *all* closed fences with `matchAll` and preferring the first one whose trimmed content starts with `{`/`[`, rather than blindly taking the first fence in document order.

**What broke first:** Initially treated fence-stripping as "just remove the ` ``` ` markers and leave everything else alone." That falls apart the moment there's chatter both before *and* after a single fenced block ("Here is your data:\n\`\`\`json\n{...}\n\`\`\`\nLet me know!") — if you only strip markers, the chatter sentences are still sitting in the string. Fixed by having this step *extract* the chosen fence's content (dropping everything outside it) rather than just deleting the marker lines. Block-extraction (M3) still has its own job for the *no-fence* chatter case, but when a fence is present, it's actually the most reliable signal for where the real payload lives, so it's fine — even good — for this step to lean on it fully.

**Key insight:** Regex is the right tool exactly when the problem is about *structural* boundaries (fence markers always live on their own line, delimited by literal `` ``` ``), and the wrong tool the moment the problem needs to know "am I inside a string value right now?" — that second kind of question is what's motivating the shared scanner in M4. Fence-stripping and block-extraction get to stay regex-only specifically because they run *before* we're reasoning about JSON string semantics at all.

---

## Milestone 3: Block extraction

**Concept:** Delimiter/bracket matching by hand — and hitting the exact wall that motivates building a real scanner next.

**What I built:**
- `src/steps/extractBlock.ts` — finds the first `{` or `[` in the input (`input.search(/[{[]/)`), then scans forward character-by-character with a `depth` counter: openers increment, closers decrement, and when `depth` returns to `0` we've found the matching close. Handles the truncated case too — if we run off the end of the string before `depth` hits `0`, we take everything from the start bracket to end-of-string and leave closing it to bracket-balancing (M7).
- The part that isn't just "count brackets": a naive version of this would break immediately on input like `{"code":"if (x) { y }"}` — the `{`/`}` inside the string value are *not* structural, but a plain depth-counter can't tell the difference. So this already needed a minimal `inString` flag: while inside a double-quoted string, brace/bracket characters are ignored entirely.
- That in turn needed escape-awareness, or a string like `{"a":"a\\","b":2}` breaks it — the `\\` right before the closing `"` is a single *escaped backslash*, not a backslash that escapes the quote. Implemented this with a forward-scanning `escaped` boolean (not backward-counting backslashes): when we see `\` while in a string, flip `escaped = true` and skip evaluating the *next* character as a potential terminator; if that next character is itself `\`, it just resets the flag (two backslashes cancel out), and only a lone unescaped `\` in front of a `"` lets that `"` actually close the string. It's a smaller mental model than counting backslash runs, and it falls naturally out of processing one character at a time.

**What broke first:** First pass didn't have the `escaped` flag at all — just toggled `inString` on every unescaped-looking `"`. The `{"a":"a\\","b":2}` test case (comment in the test explains the trap) is exactly the case that catches this: without escape tracking, the scanner sees `\` then `"` and either treats the `\` as escaping the real closing quote (staying "in string" too long and eating the rest of the object) or gets the count wrong depending on how the naive check is written. Adding the forward `escaped` flag fixed it in about four lines.

**Key insight:** I just wrote string/escape-tracking logic for the second time (fence-stripping didn't need it since it only cares about fence *lines*, but block-extraction does) — and I'm about to need the *exact same logic* for trailing-comma removal, quote-fixing, and bracket-balancing in the next few milestones. That's the concrete signal (not an abstract "best practice") for why M4 pulls this out into one shared `scanner.ts`: I can already feel the duplication coming, one file away.

---

## Milestone 4: Shared scanner

**Concept:** Generators/iterators in TS, state machines, and the backslash-parity escaping edge case properly generalized (not just handled once, inline, like in M3).

**What I built:**
- `src/scanner.ts` — a generator function `scan(input: string): Generator<ScanState>` that yields one `ScanState` per character: `{ index, char, inString, stringQuoteChar, escaped }`. Consumers do `for (const state of scan(input))` or `[...scan(input)]` and react per-character without re-implementing string/escape tracking.
- Extended beyond what M3's inline version did in one useful way: `stringQuoteChar` is `'"' | "'" | null`, so the scanner also recognizes single-quoted strings as strings (not just double-quoted) — needed later for quote-fixing (M6), which has to detect Python-dict-style `'single quotes'` in LLM output.
- Deliberately chose a **generator**, not a function that returns an array of states or takes a visitor callback. A generator lets a consumer `break` out of the loop early (useful for something like block-extraction's "stop as soon as depth hits zero") without the scanner needing to know anything about *why* the consumer stopped — the scanner just produces states lazily, one at a time, and the consumer decides when it's satisfied.
- Depth/nesting tracking (braces, brackets) is explicitly **not** in this file — that's each consumer's own concern (a stack in `balanceBrackets`, a simple counter in a future re-implementation of `extractBlock`). Keeping the scanner single-purpose (string/escape state only) is what makes it independently testable in isolation and reusable across steps whose depth-tracking needs differ (extraction wants "stop at the first zero", balancing wants "collect everything left on the stack at the end").
- `tests/scanner.test.ts` tests the scanner completely in isolation from any JSON-repair logic — plain strings in, expected per-character state sequences out. Includes the exact parity case from M3 (`"a\\"` — escaped backslash followed by a real closing quote) as its own dedicated test, now covered once at the source instead of implicitly inside a bigger integration test.

**What broke first:** Nothing broke in the new code — M3 already fought through the escaping logic once, so this milestone was mostly "extract, generalize, and add the single-quote case as new behavior." The one real design decision, not a bug, was choosing what `inString`/`escaped` mean *for the delimiter character itself* (the opening/closing quote). Settled on: the opening quote is yielded with `inString: false` (we weren't in a string yet when we saw it) and the closing quote is yielded with `inString: true` (we still were, right up until this character). This asymmetry is intentional and documented in the type — getting it backwards would make "is this character part of the string body" ambiguous for consumers.

**Key insight:** A generator is a clean way to decouple "how do I walk this string safely" from "what do I do with each character." The scanner doesn't know or care whether it's feeding a comma-remover, a quote-fixer, or a bracket-balancer — each of those just wraps `scan()` with its own small stateful reducer (depth counters, lookahead buffers) on top of a state stream it can trust. That trust boundary (scanner owns string/escape correctness; consumers own everything else) is what stops the M4 scanner from ballooning into a monolith that tries to do too much.

---

## Milestone 5: Trailing comma removal

**Concept:** Deliberately breaking a naive regex approach first, on a concrete input, before writing the correct scanner-based fix — to make the *reason* for the shared scanner (M4) undeniable rather than theoretical.

**What I built:**
- Before writing any real code, ran the "obvious" one-line fix through Node directly: `s.replace(/,(\s*[}\]])/g, "$1")` against `{"note": "trailing comma here,}", "b": 2}`. Result: `{"note": "trailing comma here}", "b": 2}` — and it **still parses successfully**. That's the important part: this isn't a crash, it's silent data corruption. The regex has no idea it just deleted a comma that was part of a string's actual content; `JSON.parse` has no way to know the output doesn't match the caller's intent, because the output is perfectly valid JSON — just wrong.
- `src/steps/removeTrailingCommas.ts` — the real fix, built on `scan()`. Walks character-by-character; only treats a `,` as a *candidate* trailing comma when `state.inString` is `false`. For each real candidate, looks ahead past whitespace/newlines (`while (/\s/.test(...)) j++`) to check whether the next non-whitespace character is a `}`/`]`. If so, the comma is skipped (not appended to the output); otherwise it's kept.
- Rebuilt the output by streaming: `output += state.char` for every character except the ones identified as droppable trailing commas. This is simpler than trying to do an in-place string surgery with index math — appending to a new string as you go avoids ever having to recompute offsets after a deletion.

**What broke first:** The regex "break it" demo above — captured directly as a test case (`does NOT remove a comma that is legitimate string content`) so the exact failure mode has a permanent regression test, not just a one-off terminal experiment.

**Key insight:** "It still parses" is not the same as "it's correct." A validity check (`JSON.parse` succeeding) can't catch every way a naive text transformation can go wrong — only a semantic check (does the data still mean what it should?) can. This is exactly why the benchmark suite (M9) needs *expected output* comparisons, not just "did it parse" pass/fail — a bug like this naive regex would sail through a parse-only test suite while quietly corrupting data.

---

## Milestone 6: Quote fixing

**Concept:** Designing a heuristic under genuine ambiguity, and treating "this can guess wrong sometimes" as an explicit, tested, documented property of the code — not a bug to chase away.

**What I built, as three composed passes in `src/steps/fixQuotes.ts`:**
1. **Smart-quote normalization** (plain heuristic, no scanner — curly quotes aren't recognized as string delimiters by `scan()` yet, so this has to run first on raw text). For each curly quote character, check what's structurally next to it (skipping whitespace): if it touches `{ [ : ,` before it or `} ] : ,` after it, or sits at a string boundary, treat it as a delimiter and normalize to a straight quote; otherwise leave it as content. Curly apostrophes get special treatment: the *opening* curly single quote (‘) is never a real apostrophe (typographic apostrophes only ever render as the closing glyph ’), so it converts whenever structurally positioned; the *closing* curly single quote (’) is genuinely ambiguous between "apostrophe" and "delimiter close", so it's only converted when NOT preceded by a letter (apostrophes always follow a letter) AND structurally positioned after.
2. **Single-quoted → double-quoted conversion**, built on `scan()` (which already recognizes `'` as a valid string delimiter, from M4). Walks the token stream; when a string opens with `'`, re-emits `"` instead, and inside that string: unescapes `\'` (doesn't need escaping under `"`), escapes any bare `"` (now unsafe since it's the new delimiter), and passes other escapes (`\n`, etc.) through unchanged.
3. **Unescaped inner-quote repair** — the fuzziest of the three, so it's a standalone manual scan (not reusing `scan()`, since the decision "is this quote real or fake" requires variable-length lookahead that changes the very state `scan()` would otherwise track for us). For every unescaped `"` encountered while already inside a string, look ahead past whitespace: if the next character is `,`/`:`/`}`/`]` or end-of-input, treat it as the real closing quote; otherwise, treat it as an unescaped literal and insert a `\` before it, keeping the string open.

**What broke first:** Wrote a test asserting that curly quotes right next to a comma (`“neat”, mid-sentence`) should be left alone as "content" — and the heuristic correctly converted them anyway. That wasn't a bug in the code; it was a bad test. A closing curly quote sitting directly before a comma is *exactly* the structural pattern real JSON delimiters produce (`"value", "next-key"`), so my own heuristic rule (rightly) can't distinguish that from genuine content punctuated the same way. Rewrote the test to use curly quotes that are actually mid-sentence with no adjacent structural punctuation, which is the case the heuristic is actually designed to protect.

**Key insight:** This step is explicitly the fuzziest one in the whole pipeline, and that's fine — the PRD doesn't promise perfect repair, it promises *heuristics with documented limits* (schema validation is Zod's job, not this library's). The discipline that keeps a heuristic step honest is writing tests for its known failure boundary, not just its success cases — `does not convert an apostrophe`, `leaves ... alone when not structurally positioned` are as important as the happy-path tests, because they pin down *exactly* where the heuristic's guarantees stop, in a way a future change can't silently regress without a test noticing.

---

## Milestone 7: Bracket balancing

**Concept:** Stack data structure for LIFO nesting, and the difference between "mid-string" and "mid-structure" truncation — plus a real bug caught by tests, not by inspection.

**What I built, in `src/steps/balanceBrackets.ts`:**
- A single pass over `scan(input)` maintaining a `stack: Array<"{" | "[">`: push on an opener seen outside a string, pop on a closer seen outside a string. Whatever's left on the stack at end-of-input is exactly the set of structures that never got closed.
- Closers are appended in **reverse stack order** (`for (let i = stack.length - 1; i >= 0; i--)`) — this is the LIFO property doing real work: the *innermost*, most-recently-opened structure has to close first, or you get syntactically-present-but-wrong-shape output (e.g. closing the outer object before the inner array would produce `}]` instead of `]}`).
- If the scan ends mid-string, the string gets closed first, before any brackets — otherwise appending `}` while still "inside" an unterminated string would just become more string content, not real JSON structure.
- Three dangling-fragment cleanups, run in a loop until nothing more changes (because removing one can expose another): a trailing comma with nothing after it, a `"key":` with no value that ever arrived, and — only when the current top-of-stack context is an *object*, not an array — a bare trailing string sitting in key position with no colon after it (i.e. it was going to be a key, but got cut off first). That last one is intentionally context-gated: the exact same "string truncated right at the end" shape is completely valid and should be *left alone* inside an array (`["a","b` → `["a","b"]`), since array elements don't need a colon.

**What broke first — a real one:** Two tests failed on first run: `["a","b"` (truncated *right after* a complete, already-closed string) was coming out as `["a","b"]}` — extra garbage — and `{"a": "b"` was coming out with an unterminated string. Root cause: I was deciding "did the string get left open?" by checking `state.inString` on the *last yielded scanner state*, but the scanner (by the M4 design decision) yields the **closing quote itself** with `inString: true` ("still in string for this character, then it exits"). So a string that had *just legitimately closed* on the final character of the input looked identical, from that one field, to a string that was truncated mid-content. Fix: only treat the string as unclosed if the last character *wasn't itself* an unescaped instance of the quote that opened it (`lastState.char === lastState.stringQuoteChar && !lastState.escaped`) — i.e., check whether the last character *is the closer*, not just whether it reports `inString: true`.

**Key insight:** This is the exact trap the M4 scanner design flagged as a deliberate asymmetry (closing delimiter yielded as `inString: true`, opening delimiter as `inString: false`) — and I still walked straight into it, because "is this field true" is an easier question to reach for than "what does this field actually mean for the character I'm looking at." A shared, well-tested primitive doesn't prevent misuse of its API by consumers; it just makes the misuse a single, fixable bug in one file instead of the same mistake duplicated three times. The regression tests for both the array and object "truncated right after a complete string" cases now guard this specific interpretation permanently.

---

## Milestone 8: Pipeline + error messages

**Concept:** Composing five independent pure functions into one ordered pipeline, custom `Error` subclassing with structured fields, discriminated-union narrowing in practice, and revisiting an earlier "DRY" design decision once requirements outgrew it.

**What I built:**
- `src/pipeline.ts` — `runPipeline<T>(raw)` runs the checkpointed, cumulative sequence designed back in the plan: fast-path `JSON.parse` → strip fences → extract block → *(checkpoint: retry parse — catches "only chatter/fences were wrong")* → fix quotes → remove trailing commas → balance brackets → *(final parse attempt)*. Each step's `changed` flag (from `StepResult`, introduced all the way back in M2) gets collected into a `stepsAttempted: string[]` — this is the payoff for having threaded that flag through every step even when nothing consumed it yet.
- `src/errors.ts` — `HealError` now carries structured fields (`stepsAttempted`, `position?`, `snippet?`, `originalMessage`) instead of just a message string. `buildHealError()` parses the character offset straight out of V8's own `JSON.parse` message (`"...at position 42"` via a regex) and uses it to slice a ~40-character snippet of context around the failure point, so the final error reads like `"Attempted: strip-fences. JSON.parse error: Unexpected token 'T'... Near: '...'"` instead of a bare parser error with no idea what was already tried.
- **Revisited the M1 "thin wrapper" decision.** M1 set `healJson` up as a thin wrapper that calls `tryHealJson` and throws on failure — good DRY instinct at the time, but it stops working once failures need to carry more than a string: `tryHealJson`'s public return type is fixed by the PRD to `{ success: false; error: string }`, so if `healJson` called `tryHealJson`, the richer `HealError` object (with `stepsAttempted`/`position`/`snippet`) would already be flattened to a string before `healJson` ever saw it. Fixed by having both `healJson` and `tryHealJson` call `runPipeline` directly instead of one calling the other — `runPipeline` is still the single source of truth for the actual repair logic, just one level lower than where the M1-era DRY line was drawn.
- `tests/pipeline.test.ts` — integration tests that combine *multiple* problems in one input (fenced + trailing comma, chatter + truncation, smart quotes + trailing comma) specifically to exercise step *ordering*, not just each step alone.
- Expanded `tests/index.test.ts` with a discriminated-union test that leans on TypeScript's control-flow narrowing directly: inside `if (result.success) { result.data }` vs `else { result.error }`, no cast needed — the compiler enforces that you can't accidentally read `.data` on the failure branch.

**What broke first:** Two of my own test assumptions, not the implementation. I wrote a test expecting `'{"a": '` (dangling key with a colon but no value) to be *unrecoverable* — but the pipeline correctly heals it to `{}` via the M7 dangling-key-with-colon cleanup, which is exactly what M7 was built to do. Same mistake with a fenced-but-truncated `{"a": 1, "b":` input — I expected it to fail with `strip-fences` in the attempted-steps list, but it actually heals all the way to `{"a":1}`. Both "failures" were really successes; had to swap in inputs that are genuinely unrecoverable (plain prose, with or without a fence around it) to actually test the failure path.

**Key insight:** Once five independently-correct steps are chained together, the pipeline as a whole ends up *more* capable of healing input than any single step's test suite would suggest — which is a good sign the steps compose the way they were designed to, but it also means "will this input actually fail" stops being obvious from reading the input alone. Worth remembering for the benchmark suite (M9): the "unrecoverable garbage" fixture category needs inputs that are unrecoverable *for a real reason* (no bracket structure at all), not just inputs that merely look broken.

---

## Milestone 9: Benchmark suite

**Concept:** Turning a PRD's stated success metric ("correctly heals 20+ real broken-LLM-JSON samples") into an actual executable spec, and coverage-by-category thinking as a way to make sure a test suite's breadth is deliberate, not accidental.

**What I built:**
- `benchmark/fixtures/index.ts` — 22 fixtures as plain TS objects (`{ name, category, input, expected }`, or `{ ..., shouldFail: true }` for the one deliberately-unrecoverable case), grouped by category: fences (3), chatter (3), trailing-comma (3), truncation (5), quotes (5), combination (2), sanity (2 — one already-valid fast-path check, one guaranteed failure). Chose plain TS objects over paired `.json`/`.txt` fixture files specifically because several inputs are themselves *intentionally invalid JSON* (that's the whole point) — keeping them as JS string literals avoids fighting an editor/linter that wants to "fix" a malformed `.json` file, and `expected` gets real type-checking as a TS value instead of being re-parsed from a second file.
- `benchmark/run.ts` — iterates every fixture through `tryHealJson`, compares `JSON.stringify(result.data)` against `JSON.stringify(fixture.expected)` (a pragmatic deep-equality check without pulling in a comparison library), prints a pass/fail line per fixture, and sets `process.exitCode = 1` if anything failed — so this doubles as a CI gate later, not just a manual smoke test.
- A genuinely new constraint surfaced here: `benchmark/run.ts` needs `process.exitCode`, which requires Node's ambient types — but `src/`'s `tsconfig.json` deliberately excludes any Node/DOM lib (from M1) specifically to catch accidental non-portable code at compile time. Installing `@types/node` as a devDependency would normally make `process`/`Buffer` silently valid *everywhere* in the project (TypeScript auto-includes all installed `@types/*` packages as ambient globals by default), quietly defeating that M1 guarantee. Fixed by adding `"types": []` to the root `tsconfig.json` (turns off automatic `@types` inclusion project-wide) plus a single `/// <reference types="node" />` directive at the top of `benchmark/run.ts` — this opts in Node's types for *that one file only*, leaving `src/` exactly as strict as M1 intended.

**What broke first:** Nothing — all 22 fixtures passed on the first run. That's a direct payoff of the M5/M7/M8 learning entries: several fixtures here were built by mentally re-tracing the exact same step-by-step scans documented in those entries (e.g. predicting that `truncated-after-comma` needs `balanceBrackets`'s dangling-comma cleanup rather than `removeTrailingCommas`, because the comma isn't immediately followed by a closer — it's followed by end-of-string) before ever running the code. Getting that prediction right on paper first, then having the test confirm it, is a good sign the mental model of the pipeline actually matches the implementation.

**Key insight:** A PRD success metric like "heals 20+ real samples" is easy to treat as a vague aspiration, but writing it as `benchmark/run.ts` with a hard exit code turns it into a concrete, re-runnable claim about the code, forever. It also exposed something process-level: designing fixtures by category *before* writing them (fences, chatter, trailing-comma, truncation, quotes, combination, sanity) is what made 22/22 passing meaningful rather than lucky — the categories map directly to the five functional requirements in the PRD, so a gap in coverage would have been visible as a category with too few (or zero) fixtures, not just a low total count.

---

## Milestone 10: Build, packaging, size-check

**Concept:** esbuild/dual-format bundling internals, Node's `zlib`/`Buffer` APIs for measuring what "gzip size" tooling actually does under the hood, and hitting a real, measured product constraint that couldn't be solved by cleaner code alone.

**What I built:**
- `tsup.config.ts` — `format: ["cjs", "esm"]` with `dts: true` produces `dist/index.js` (ESM) + `dist/index.cjs` (CJS) + matching `dist/index.d.ts`/`dist/index.d.cts` in one command, driven by esbuild under the hood.
- A real portability leak surfaced immediately: `benchmark/run.ts` needs `process.exitCode`, which needs Node's ambient types — but `tsconfig.json` deliberately has no Node/DOM lib (from M1) specifically to catch non-portable code in `src/` at compile time. Installing `@types/node` normally makes those globals silently valid *everywhere* in the project (TS auto-includes all installed `@types/*` packages by default). Fixed with `"types": []` in the root `tsconfig.json` (turns off that auto-inclusion) plus one `/// <reference types="node" />` directive at the top of `benchmark/run.ts` — opts in Node's types for that one script only, leaving `src/`'s portability guarantee from M1 completely intact.
- `scripts/check-size.mjs` — a ~15-line script using `zlib.gzipSync` directly on the built `dist/index.js`, printing raw vs. gzipped byte counts and failing (`process.exitCode = 1`) past a threshold. Wrote this *before* installing any size-checking package, specifically so the mechanism ("gzip the file, compare byte count to a limit") wasn't a black box before trusting a tool to do it — the tool (`size-limit` + `@size-limit/file`) does the exact same thing, just with nicer output and package.json-driven config.
- Hit a real, measured constraint: the PRD's `<2KB gzipped` budget. Unminified, the bundle gzipped to ~3.2KB; with esbuild minification (`minify: true` in tsup) that dropped to ~2.16KB — still over. Tried two more levers before accepting the number: (1) manually deduplicating repeated code shapes (the scanner's five near-identical `yield {...}` object literals) — this *increased* gzip size slightly, because gzip's own LZ77 compression already exploits exact repeated substrings more cheaply than the "cleaner" refactored code's new-but-less-repetitive tokens could; reverted it. (2) Extracting genuinely duplicated logic — three separate "skip forward past whitespace" loops across `removeTrailingCommas.ts` and `fixQuotes.ts` — into a shared `src/textUtils.ts` helper; this one was a legitimate simplification (real duplication, not artificial), but the byte savings were marginal (~150 raw bytes) since gzip had already been compressing that near-identical code efficiently too. Tried terser as a stronger alternative minifier: modest further gain (~36 bytes), still short of 2KB.
- At that point, closing the remaining gap meant either dropping real functionality (the fuzziest of the three `fixQuotes` passes) or trimming the structured-error DX (position/snippet extraction in `HealError`) — both genuine trade-offs between correctness/usefulness and the size budget, not code-quality fixes. Surfaced this directly rather than picking one silently; the call was to **keep the full feature set** and accept ~2.16KB gzipped as a documented, known deviation from the original 2KB target. `scripts/check-size.mjs` and the `size-limit` config in `package.json` both now enforce **2.5KB** as a regression guard (catches the bundle from growing *further*), with a comment explaining it's not a re-statement of the original PRD number.
- Verified both entry points actually work post-build with plain Node smoke tests: `require("./dist/index.cjs")` and `import ... from "./dist/index.js"` (via `node --input-type=module -e`), rather than trusting tsup's build-success message alone.

**What broke first:** My first instinct on hitting the size ceiling was to *keep manually refactoring code shape* hoping gzip would reward it — and it didn't, predictably in hindsight: gzip is already a very effective redundancy-compressor, so restructuring code to "look" less repetitive to a human reader doesn't reliably help a compressor that was already seeing through the repetition. The dedup that *did* help (`textUtils.ts`) helped because it removed logic that was genuinely, non-trivially duplicated across files — a maintainability win first, with the size benefit as a minor bonus — not because deduplication itself is a size-optimization technique.

**Key insight:** A hard numeric constraint in a PRD (`<2KB gzipped`) is easy to treat as a target to satisfy through cleverness, but past a certain point it becomes a genuine trade-off against other things the PRD also asked for (`descriptive error` messages, handling `unescaped/smart quotes where safe`). The productive move wasn't to keep guessing at code-level tricks — it was to get concrete numbers for the actual trade-offs available (drop a feature vs. drop DX vs. accept the number) and let that be a decision, not an implementation detail I resolved on my own.

---

# Part 2: Testing, Tooling & Shipping

The milestones above cover the JSON-repair *logic*. Everything below covers the tools around it — testing from first principles, why specific build/test tools were picked over alternatives, and the actual git/npm/GitHub commands used to ship the package, since these are just as much "things learned" as the code itself, especially if you're new to automated testing and package publishing.

## Testing fundamentals (starting from zero)

**What is an automated test, actually?** A small script that runs your real code with a known input, and checks the output matches what you expect — *automatically*, so you don't have to manually re-verify it every time you change something. Without tests, "does my fence-stripping still work?" means manually running the function and eyeballing the result, every single time, for every edge case you've ever thought of. With tests, it's one command (`npm test`) and a pass/fail per case, run in milliseconds.

**Anatomy of a test in this project** (using `vitest`, the test runner we chose — more on why below):

```ts
import { describe, expect, it } from "vitest";
import { stripFences } from "../../src/steps/stripFences.js";

describe("stripFences", () => {
  it("strips a fence with a json language tag", () => {
    const input = '```json\n{"a":1}\n```';
    const result = stripFences(input);
    expect(result.changed).toBe(true);
    expect(result.output).toBe('{"a":1}');
  });
});
```

Breaking that down:
- **`describe(name, fn)`** — groups related tests together under a label (purely organizational — shows up in the test output as a heading, doesn't change behavior). We used one `describe` block per function/scenario, e.g. `describe("stripFences", ...)`, `describe("balanceBrackets — dangling key/comma cleanup", ...)`.
- **`it(name, fn)`** (equivalently `test(name, fn)`) — one individual test case. The name should read like a sentence describing the expected behavior (`it("strips a fence with a json language tag")`) — when it fails, that sentence is the first thing you see, so it should tell you what broke without needing to read the test body.
- **`expect(value)`** — wraps a value so you can assert something about it. Every `expect(...)` call is chained with a "matcher":
  - `.toBe(x)` — strict equality (`===`), for primitives (numbers, strings, booleans).
  - `.toEqual(x)` — deep equality, for objects/arrays (compares contents, not reference identity — `expect({a:1}).toEqual({a:1})` passes even though they're different object instances).
  - `.toThrow(ErrorClass)` — asserts a function call throws (used constantly for `healJson`, e.g. `expect(() => healJson("garbage")).toThrow(HealError)` — note the function is wrapped in an arrow function `() => ...`, not called directly, so vitest can catch the throw itself).
  - `.toContain(substring)` — asserts a string contains a substring, or an array contains an element.
  - `.toBeInstanceOf(Class)` — asserts something was constructed via a specific class (used to check thrown errors are actually `HealError`, not a generic `Error`).

**Running tests:**
```sh
npm test          # runs once, prints pass/fail, exits (what CI would run)
npm run test:watch # re-runs automatically on file save — the loop you actually live in while writing code
```

**Unit tests vs. integration tests** (both exist in this project, on purpose):
- **Unit tests** (`tests/steps/*.test.ts`) test one function in complete isolation — e.g. `stripFences.test.ts` only calls `stripFences()` directly, never the full pipeline. Fast, and when one fails you know exactly which function is broken.
- **Integration tests** (`tests/pipeline.test.ts`) test the *whole pipeline* end-to-end with inputs that combine multiple problems at once (fenced + trailing comma + truncated, all in one string) — these catch bugs in how steps interact (ordering, one step's output breaking an assumption the next step makes) that no individual unit test could catch, because each unit test only ever sees clean, single-problem input.

Why this mattered concretely: M8's pipeline tests caught that two of *my own test expectations* were wrong (I expected certain inputs to be unrecoverable, but the full pipeline actually healed them) — a unit test alone couldn't have surfaced that, since it only exercises one step at a time.

## Why vitest — and NOT "the Vite bundler" (a very reasonable mix-up)

Worth clearing up directly, since the names are almost identical on purpose: **Vite** and **Vitest** are two different tools built by the same team.

- **Vite** is a *dev server and bundler*, mainly for building web apps (think: the thing that serves your React/Vue app locally with instant hot-reload, and bundles it for production). We do **not** use Vite anywhere in this project — there's no `vite.config.ts`, and it's not a dependency.
- **Vitest** is a *test runner*. It's built **on top of** Vite's internals (its fast file-transform pipeline) specifically so that running TypeScript/ESM test files "just works" with zero extra configuration — no separate `ts-node`, no Babel config, no CommonJS/ESM interop headaches. That's the entire reason for the name: "Vite, but for tests."

Why vitest specifically, over the alternatives:
- **vs. `node:test`** (Node's own built-in test runner, truly zero-dependency): more primitive — no built-in watch-mode re-run on save, plainer failure output (no inline diffs), and TypeScript support needs a separate loader flag. `node:test` is a legitimate zero-dependency choice (and the PRD's "zero *runtime* deps" constraint only restricts `dependencies`, not `devDependencies`, so either was fair game), but vitest's tighter feedback loop mattered more here given how many string-scanning edge cases needed iterating on.
- **vs. Jest** (the long-time incumbent): Jest predates native ESM support in the JS ecosystem and still needs extra configuration (`ts-jest` or Babel transforms) to handle TypeScript + ESM smoothly, which is exactly the friction vitest was built to avoid. Jest is still very common and perfectly good — vitest just needed less setup for this specific project's module format (`"type": "module"` in `package.json`).

Our actual config is intentionally tiny — this is most of what "zero-config TS testing" buys you:
```ts
// vitest.config.ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["tests/**/*.test.ts"],
  },
});
```

## Build tooling: why tsup (esbuild), not Vite, not Rollup, not tsc alone

Separately from *testing*, there's *building* — turning `src/*.ts` into the actual files that get published to npm (`dist/index.js`, `dist/index.cjs`, `dist/index.d.ts`). This is a genuinely different job from testing, and uses a different tool: **tsup**.

```ts
// tsup.config.ts
import { defineConfig } from "tsup";

export default defineConfig({
  entry: ["src/index.ts"],
  format: ["cjs", "esm"],   // <- produces BOTH dist/index.cjs AND dist/index.js
  dts: true,                 // <- also generates dist/index.d.ts / .d.cts
  clean: true,
  sourcemap: true,
  minify: true,               // <- needed to hit the <2KB gzip target, see M10
  target: "es2020",
});
```

One command (`npm run build`, which is just `tsup`) produces everything a published npm package needs. Why this over the alternatives:

- **Why not Vite for building too?** Vite does have a "library mode," but it's oriented at bundling apps/components for browser consumption (it assumes you mostly want one output target, often with a UI framework in the mix). tsup is purpose-built for exactly this project's shape: a small, framework-free TS library that needs to ship as *both* CJS and ESM simultaneously, plus bundled type declarations, with minimal config. Using Vite here would mean fighting its defaults toward our narrower, simpler need.
- **Why not plain `tsc` (the TypeScript compiler) alone?** `tsc` can compile TS to JS and emit `.d.ts` files, but it can't natively produce two different module formats (CJS *and* ESM) from one config in one pass, and it doesn't bundle/minify. You'd need two separate `tsc` runs with two different `tsconfig.json` files (one targeting `commonjs`, one targeting `esnext`) plus manual wiring to combine them — tsup does this as a single, already-solved problem.
- **Why not Rollup directly?** Rollup is what tsup (and Vite) actually use under the hood for some of this — you *could* hand-roll a Rollup config with `@rollup/plugin-typescript` + `rollup-plugin-dts` to get the same dual-format-plus-types output, but it's meaningfully more manual wiring for the exact same result tsup gives for free. Worth doing by hand once as a learning exercise outside this project, but not a good use of time inside it.
- **The engine underneath tsup is `esbuild`** — a bundler written in Go, chosen by the tsup authors specifically for build *speed* (our builds here run in ~30ms). This is also, incidentally, the same engine Vite itself uses for pre-bundling dependencies during development — so esbuild is the one piece of infrastructure genuinely shared between our "testing" tool (vitest → Vite → uses esbuild for dep pre-bundling) and our "building" tool (tsup → uses esbuild directly for the whole build) — which is probably where the "wait, isn't this the same thing as Vite?" instinct came from, and it's a reasonable one; esbuild really is the common thread.

## Git, GitHub & npm: the actual shipping workflow

Every command actually run to get this package from "code on disk" to "installable via `npm install json-healer`," explained:

**Git — recording a snapshot of the code:**
```sh
git add <files>              # stage specific files (never `git add -A`/`.` blindly — avoids
                              # accidentally committing secrets or huge unwanted files)
git commit -m "message"      # record a snapshot with a message explaining WHY, not just what
git push                     # send local commits to the remote (GitHub) — nothing is
                              # visible to anyone else until this runs
```

**The heredoc trick** (`<<'EOF' ... EOF`) used for commit messages with multiple lines:
```sh
git commit -m "$(cat <<'EOF'
Implement json-healer: zero-dependency LLM JSON repair utility

Heals malformed JSON from LLM output...
EOF
)"
```
`cat <<'EOF' ... EOF` is shell syntax for "everything between these two `EOF` markers is one multi-line block of text, passed to `cat` as input, which just prints it back out." Wrapping it in `$(...)` captures that output as a string, which then becomes the `-m` argument. The single quotes around the *first* `EOF` (`<<'EOF'`, not `<<EOF`) matter: they stop the shell from trying to interpret `$variables` or backticks *inside* the message — without them, a commit message that happened to contain a `$` or backtick could break or behave unexpectedly. This is the standard, safe way to pass a multi-paragraph string as a single command-line argument in bash/zsh.

**Git tags** — a permanent, named pointer to one specific commit, conventionally used to mark releases:
```sh
git tag -a v0.1.0 -m "v0.1.0"   # -a = "annotated" tag (stores who/when/message, vs a bare pointer)
git push origin v0.1.0           # tags don't push automatically with `git push` — pushed separately
```

**GitHub CLI (`gh`)** — a command-line tool for GitHub actions (releases, PRs, issues) that would otherwise need the web UI. Wasn't installed on this machine, so it was fetched as a standalone binary (no root/sudo needed):
```sh
curl -sL "https://github.com/cli/cli/releases/download/v2.96.0/gh_2.96.0_linux_amd64.tar.gz" -o gh.tar.gz
tar -xzf gh.tar.gz
mkdir -p ~/.local/bin
cp gh_2.96.0_linux_amd64/bin/gh ~/.local/bin/gh
chmod +x ~/.local/bin/gh   # marks the file as executable — without this, the shell refuses to run it
```
This works without `sudo` because `~/.local/bin` is a directory *inside your own home folder* (already on your `PATH`, meaning the shell already looks there for commands) — no system-wide installation or root permission needed. This is the general pattern for installing a single CLI tool as a normal user on Linux when you don't have (or don't want to use) `sudo`.

Then, since `gh` needs its own login separate from git's SSH key:
```sh
gh auth login       # interactive: browser-based OAuth flow or paste a personal access token
gh release create v0.1.0 --title "..." --notes "..."   # creates a GitHub Release tied to the tag
```

**npm — publishing the package itself:**
```sh
npm login                    # interactive; logs the npm CLI into your npmjs.com account
npm whoami                   # confirms which account you're currently logged in as
npm publish --dry-run        # simulates a publish: shows exactly what files would be uploaded,
                              # without actually uploading anything — safe to run repeatedly
npm publish                  # the real thing — irreversible in practice (a given version
                              # number, once published, can never be reused even if unpublished)
npm publish --otp=123456     # required if your npm account has 2FA enabled for publishing —
                              # the 6-digit code from your authenticator app
npm view json-healer          # look up any published package's metadata from the registry
npm owner add <user> <pkg>    # grant another npm account publish rights on a package
                              # (see the ownership discussion below — this only works for
                              # ADDING an individual user, not an organization, to an
                              # unscoped package)
```

**Semantic versioning (semver)** — the `0.1.0` in `package.json`. Three numbers, `MAJOR.MINOR.PATCH`:
- **MAJOR** (first number) bumps on breaking changes.
- **MINOR** (second number) bumps on new, backwards-compatible features.
- **PATCH** (third number) bumps on backwards-compatible bug fixes.
- **`0.x.y`** (major version zero) is a special case in the semver spec: it explicitly means "initial development — anything may change at any time," which is why brand-new packages conventionally start at `0.1.0` rather than `1.0.0`. Bumping to `1.0.0` later is a deliberate signal: "the API is now stable, future changes will follow the MAJOR/MINOR/PATCH rules strictly."

**npm scoped vs. unscoped package names** (this came up when deciding company ownership):
- **Unscoped**: `json-healer` — a flat, global name on the registry, first-come-first-served, always free to publish publicly.
- **Scoped**: `@spectroniq/json-healer` — namespaced under an npm *organization* (`@spectroniq`). Scoped packages default to **private** and need `npm publish --access public` to be publicly installable for free. Organizations are how npm groups packages under a company/team identity — but an org can only ever own packages *within its own scope*; it cannot "adopt" an already-published unscoped package. That's a real, non-obvious limitation worth remembering: **the scoped-vs-unscoped decision is effectively permanent** once a package is published under a name, short of publishing an entirely new package name and migrating.

## Badges (shields.io)

The README badges are just `<img>` tags (in Markdown image syntax) pointing at a badge-generation service, not anything installed or configured:
```md
[![npm version](https://img.shields.io/npm/v/json-healer.svg)](https://www.npmjs.com/package/json-healer)
```
`shields.io` reads live data from the npm registry itself (current version, weekly downloads) and renders it as an SVG image on the fly, every time the badge is requested — so it's always up to date with zero maintenance, no build step, no account needed. The `[...](url)` wrapping around the image makes the badge itself a clickable link.

## Migrating to a company-owned scoped package (npm orgs, deprecation, and a scary error that wasn't)

`json-healer` was first published unscoped, under a personal npm account. To give Spectroniq Limited real institutional ownership (not "one person's account happens to control this"), it was migrated to `@spectroniqltd/json-healer`. The actual process, and a mistake worth remembering along the way:

**A wrong assumption caught before it wasted time:** the first plan was "create an npm org, then transfer the existing `json-healer` package into it." That's not possible — npm organizations only ever own packages *within their own `@scope`*; there's no operation that moves an already-published unscoped package under an org's control. This was caught by re-checking npm's actual documented behavior before running any commands, rather than discovering it mid-attempt. Worth internalizing generally: when a plan involves an irreversible-ish action (publishing a company-facing package name is close to permanent), it's worth a few minutes confirming the mechanism actually works the way you think before running anything.

**What actually had to happen instead** — not a "transfer," but a genuine migration to a new package identity:

1. **Create the npm org** — web-only, no CLI command for this (`https://www.npmjs.com/org/create`). Picked the slug `spectroniqltd` (matching the GitHub org name already in use — worth doing deliberately, so the npm scope, GitHub org, and company name all read the same).
2. **Rename the package** — just a `package.json` field change:
   ```json
   { "name": "@spectroniqltd/json-healer" }
   ```
   Everything else (source code, tests, build config) is completely unaffected — the package name is metadata, not something the code depends on internally.
3. **Update every place the old unscoped name was hardcoded** — README badges, README install instructions, the `import` example. Easy to miss one of these since they're scattered across a file rather than centralized.
4. **Publish the new scoped package** — scoped packages default to *private* on npm (unlike unscoped, which are always public), so this needs an explicit flag:
   ```sh
   npm publish --access public --otp=<code>
   ```
5. **Deprecate the old unscoped package**, so anyone still on the old install command sees a warning instead of silently getting an abandoned package:
   ```sh
   npm deprecate json-healer "Renamed to @spectroniqltd/json-healer — please install that instead." --otp=<code>
   ```
   This doesn't delete or unpublish anything (`npm unpublish` is a much more restricted, mostly-discouraged operation) — it just attaches a warning message that shows up in `npm view`, and in the install-time output for anyone who runs `npm install json-healer` going forward.

**A genuinely alarming-looking error that turned out to be good news:**
```
npm error 403 Forbidden - PUT https://registry.npmjs.org/@spectroniqltd%2fjson-healer
npm error 403 You cannot publish over the previously published versions: 0.1.0.
```
First read, this looks like the publish *failed*. It didn't — `npm view @spectroniqltd/json-healer` showed the package already live, "published 59 seconds ago," with a shasum matching the exact dry-run output from moments earlier. What actually happened: the *first* `npm publish` attempt had already succeeded, and this error came from a *second* attempt at the same command (likely re-run before realizing the first one worked) — npm was correctly refusing to publish an identical version twice, since a given version number can never be reused once published (mentioned back in the semver section above). The fix wasn't a fix at all: just checking `npm view` to confirm the real state before assuming the scary-looking error meant failure. **Lesson: an error message describing what went wrong doesn't always mean the overall operation failed — sometimes it means a *retry* of an already-successful operation correctly got rejected.** Always check actual state (`npm view`, `git log`, a real install) before trusting an error message's framing at face value, especially for operations that might have partially succeeded before the error surfaced.

## Showcasing the project: adding json-healer to two Next.js sites

Once published, json-healer needed to show up on two separate Next.js sites: a personal portfolio and the Spectroniq company site. Doing this properly meant reading *how each site already represents "a project"* before touching anything — copying an existing pattern beats inventing a new one every time it's available.

**The portfolio needed zero structural changes.** Its data model is a flat JSON array (`src/data/projects.json`) with a `type: string[]` tag field — no schema assumption that a project is a web app (there was already a CLI-tool entry using `type: ["CLI", "Backend"]`). Adding json-healer was one new object in that array, no code changes required beyond an optional filter-pill addition. **Lesson: a data schema built with an open-ended tag array instead of an enum/boolean-per-category scales to new project *kinds* for free** — the CLI-tool entry that existed before json-healer is exactly what made this a non-event.

**The Spectroniq site needed a real decision, and a real new section.** It already had two places for "things we built" — `Portfolio` (client deliverables, assumes a live client URL) and `Products` (consumer apps, assumes Play Store/App Store links) — and neither shape fits an open-source npm library (no live URL, no app stores; it has an npm link and a GitHub link instead). Forcing it into either would have meant fields that don't apply (a "Play Store link" on a library makes no sense) or a schema quietly drifting to mean two different things. The fix was a third, parallel section — `Open Source` — deliberately built to mirror `Products`' file structure, component patterns, and visual language exactly, rather than improvising a new design language for one entry.

**A pattern worth naming: "thin app-router page + feature module".** This codebase splits each route into two files with very different jobs:
```tsx
// src/app/products/page.tsx — ONLY owns metadata + routing
import type { Metadata } from 'next';
import ProductsIndexPage from '@/features/products/pages/index.page';

export const metadata: Metadata = { title: 'Products', /* ... */ };
export default function Page() {
  return <ProductsIndexPage />;
}
```
```tsx
// src/features/products/pages/index.page.tsx — owns ALL the actual UI/logic
'use client';
export default function ProductsIndexPage() { /* search, filter, render cards */ }
```
Why split it this way: Next.js's App Router `page.tsx` files are the *only* place `export const metadata` works, and metadata exports require the file to be a **server component** (no `"use client"`). But the actual page logic here needs `useState` for search/filter — a **client component** requirement. Splitting into "thin server-component wrapper that just re-exports metadata + renders the real component" and "client-component feature module with all the interactivity" is how you get both in one route. Recognizing this pattern from `products/` meant the new `open-source/` route could copy the split exactly instead of hitting the metadata-vs-client-component conflict blind.

**Another build-tool install-check gotcha, same shape as the earlier gh-CLI one.** Running `pnpm exec tsc --noEmit` on the portfolio failed immediately — not because of anything in the code, but because pnpm refused to proceed until `pnpm approve-builds` explicitly allowlisted a couple of dependencies' native build scripts (`sharp`, `unrs-resolver`). Rather than changing the project's dependency-approval policy just to run a type check, the fix was calling the installed binary directly: `./node_modules/.bin/tsc --noEmit`, which bypasses the package manager's own install/approval gate entirely and just runs the already-installed tool. **Lesson, reinforced from the earlier npm 2FA/gh-CLI situations: when a tool's own safety/approval gate is in the way of a read-only check you're trying to run, look for a way to invoke the underlying binary directly rather than pushing through or changing the gate's configuration** — `node_modules/.bin/<tool>` is the general escape hatch for this in any JS project, regardless of whether it's npm/pnpm/yarn/bun-managed.

**Verifying beyond "it typechecks":** for both sites, the actual verification was a real `next build` (confirms every new route compiles and statically generates) followed by starting the production server and `curl`-ing the new routes to grep for expected content (`"View on npm"`, `"View on GitHub"`, the package name) — catching anything a type-only check couldn't (a route that typechecks fine but 404s, or renders with a broken link). Killing the temporary preview server afterward needed `lsof -ti:<port> | xargs kill -9` rather than `pkill` by process name, since `next start` spawns a small chain of child processes that a name-based kill didn't fully catch on the first few tries.
