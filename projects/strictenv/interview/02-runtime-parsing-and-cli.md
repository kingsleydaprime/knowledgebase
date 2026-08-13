# strictenv — Runtime Behaviour: Coercion, Parsing, Loading, Output

Milestones 3, 5, 6 and 7 — the parts that actually run.

---

### Q1. [Beginner] 🔥 Why is `Boolean(raw)` wrong for coercing a boolean env var?

**Strong answer covers:** `Boolean("false")` is `true` in JavaScript — every non-empty string is
truthy. `DEBUG=false` would enable debug mode. So boolean coercion is a **narrow allow-list**:
`raw.toLowerCase()` must be exactly `"true"` or `"false"`, anything else is an error. This isn't
just "stricter" — preventing this exact class of bug is the reason the library exists.

---

### Q2. [Intermediate] What does `Number(" ")` evaluate to, and how does that affect your number coercion?

**Strong answer covers:** `0`. So `PORT="   "` would silently validate as port zero. The coercion
guards `raw.trim() === ""` before calling `Number()` at all. The mirrored trap: you must check
`Number.isNaN(Number(raw))`, **not** the falsiness of the result — checking falsiness would reject
a legitimate `"0"`.

---

### Q3. [Intermediate] 🔥 How do you treat an empty string, and why does the order of checks matter?

**Strong answer covers:** the "absent" check runs **first**, before any type-specific coercion, and
treats `raw === undefined` and `raw === ""` identically — both fall through to the default if one
exists, then to a "missing" error if required, then to plain `undefined` if optional. That ordering
is a direct implementation of the PRD's named success metric: an empty string must never be
reported as an *invalid* number or boolean; it's simply not set. If coercion ran first, `PORT=""`
would produce "invalid number" and send the user hunting for a typo that isn't there.

**The three cases worth naming unprompted:** `PORT="0"` must succeed as `0`, `DEBUG="false"` must
succeed as `false`, and `OPTIONAL=""` must be treated as unset. Each of those is a place a naive
implementation reports a false failure.

---

### Q4. [Intermediate] Why does whole-schema validation collect every error instead of returning on the first one?

**Strong answer covers:** the failure output is a **table** of everything wrong at once. Fail-fast
means a misconfigured deploy is a sequence of five restart-and-rediscover cycles instead of one.
The cost is trivial (validation is pure and cheap); the benefit is the entire user experience of the
library.

---

### Q5. [Intermediate] Your `.env` parser is line-based, not a character state machine. When would that be the wrong choice?

**Strong answer covers:** it's right here because the PRD's "multiline" requirement turned out to
mean a literal `\n` **escape inside one physical line's quotes** (`MULTI="line1\nline2"`), which the
escape processor handles with no cross-line logic at all. It would be wrong if the requirement were
values *spanning* physical lines (triple-quoted blocks, as some dotenv-flow tools support) — that
needs "am I still inside an open quote" tracked across `split("\n")` boundaries, i.e. exactly the
cross-line state a real state machine exists for.

**The point to land:** those two readings of "multiline" sound interchangeable when skimming a
requirement and imply completely different parser architectures. Checking the literal wording
against the example syntax before building is what avoided over-building.

---

### Q6. [Advanced] 🔥 Walk me through `a\\nb` in your escape handling. What should it produce and why?

**Strong answer covers:** that's an *escaped backslash* followed by a literal `n` — the result must
be `a` `\` `n` `b`, **not** a newline. It works because JS regex alternation (`\\n|\\"|\\\\`) tries
branches left-to-right at each position and takes the **first match, not the longest** — so at the
first backslash, the `\\\\` (escaped-backslash) branch matches, consumes both characters, emits one
real backslash, and the following `n` is never considered part of an escape. Correctness therefore
depends on `\\` being its own branch rather than assuming a leading backslash always belongs to a
`\n`/`\"` escape.

**Say this too:** it was traced by hand *before* writing the test, then written as its own named
test rather than trusted silently. Interviewers care that ambiguous regex behaviour got pinned down
by a test, not by confidence.

---

### Q7. [Intermediate] 🔥 You have two different precedence questions in `loadEnv`. Name them.

**Strong answer covers:** they're separate axes, deliberately kept separate and separately tested —
1. **File vs file:** when multiple paths define the same key, later array position wins
   (`[".env", ".env.local"]` → `.env.local` overrides). No config, matches the dotenv-flow
   convention.
2. **Files vs the real environment:** controlled by the `override` option, defaulting to `false`
   so real `process.env` wins.

Blurring them into one "merge order" concept is how you end up with a library whose behaviour
nobody can predict in CI, where the real environment is the thing that matters most.

---

### Q8. [Intermediate] 🔥 Why does your file read catch only `ENOENT` and rethrow everything else?

**Strong answer covers:** a blanket `catch { return undefined }` conflates two completely different
failure modes — *expected absence* (an optional `.env.local` that isn't there) and *unexpected
error* (a permissions problem on a file that does exist, a directory where a file was expected).
Checking `err.code === "ENOENT"` (Node's `ErrnoException` convention) keeps the silence scoped to
the one thing you actually expected to sometimes be missing. Otherwise a broken, unreadable env file
looks exactly like no env file, and the user gets "missing DATABASE_URL" instead of "permission
denied".

---

### Q9. [Beginner] `process.env` is typed `Record<string, string | undefined>` but Node never actually stores `undefined` values. You filter anyway. Why?

**Strong answer covers:** the filter (`if (value !== undefined)`) means the runtime behaviour doesn't
quietly depend on an assumption about Node internals that nothing enforces. It costs one line and
removes a "this works because of something the type system explicitly says isn't guaranteed"
footnote.

---

### Q10. [Intermediate] You hand-wrote ANSI colour codes instead of using chalk or picocolors. Justify that in a library, and how do you decide when *not* to emit colour?

**Strong answer covers:** the zero-runtime-dependency constraint plus a 2KB budget — four wrappers
(`red`, `bold`, `dim`, `cyan`) are a handful of string templates. `createColors(enabled)` returns
functions closing over one boolean rather than each reading global state, so the module stays
side-effect-free and the colour decision is threaded explicitly. Colour is disabled when
`"NO_COLOR" in process.env` — key **presence**, not truthiness, because the no-color.org convention
says even `NO_COLOR=""` disables — and when `process.stdout.isTTY` is false, so piped/CI logs don't
get raw escape codes dumped into them.

---

### Q11. [Advanced] Your table renderer pads cells *before* applying colour. Why does the order matter?

**Strong answer covers:** ANSI escape codes are invisible characters that still count toward
`String.length`. If you colour first and pad second, `padEnd` counts the escape sequence as visible
width and under-pads by exactly the length of the codes, so the table misaligns — and it misaligns
*only* for coloured cells, which makes it look like a data problem rather than a rendering one.
Pad against the raw text, then wrap.

---

### Q12. [Advanced] 🔥 You wrote a test for column alignment and the test was wrong, not the code. What happened?

**Strong answer covers:** the test split each rendered line on `/\s{2,}/` and compared first-chunk
lengths — reporting "12 vs 4" on a table that was actually aligned correctly. The reason: the column
*separator* is whitespace and the *padding* is whitespace, and for a short cell they're contiguous,
so a whitespace-based split swallows both as one delimiter and un-pads the very thing being
measured. The row already at max width has no padding to swallow, so it measured correctly by
accident — which is what made the mismatch confusing rather than obviously a test bug. Fixed by
asserting an exact hand-computed prefix (`/^PORT {8} {2}/`).

**The generalisable insight:** when the thing under test *is* whitespace alignment, a
whitespace-based detection method can't work — from a pure character view there's no difference
between padding and separator. Assert an exact expected string or offset instead of re-parsing the
rendered output with the same kind of pattern that produced it.

---

### Q13. [Intermediate] Why does the default failure path call `process.exit(1)` rather than throw?

**Strong answer covers:** the library's whole premise is *fail at boot, loudly, before anything
else runs*. A thrown error can be caught by a well-meaning top-level handler and downgraded to a
log line, at which point the process continues with a broken config — the exact scenario the library
exists to prevent. Exiting with a non-zero code is also what a process supervisor, a container
orchestrator, or CI actually reads. The `onError` option exists as the deliberate escape hatch for
callers who need different behaviour.
