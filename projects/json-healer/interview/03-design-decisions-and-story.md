# json-healer — Design Decisions & Project Story

Scope, trade-offs, and the behavioural questions that come wrapped around a side project.

---

### Q1. [Beginner] 🔥 Why does this library need to exist? Why not just prompt the model better?

**Strong answer covers:** prompting reduces the rate, it doesn't eliminate it — and the failure is
*at the boundary of your system*, where you have no control and a retry costs a full model call.
Streaming makes it structural rather than probabilistic: a truncated stream is malformed by
definition, no matter how good the prompt. A repair step is cheap, deterministic, and local; a
re-prompt is expensive, slow, and may fail the same way again.

---

### Q2. [Intermediate] Why not use an existing lenient parser — JSON5, `json5-parse`, a hand-rolled recursive descent parser?

**Strong answer covers:** JSON5 solves a *different* problem — it parses a permissive **grammar**
(comments, unquoted keys, trailing commas) from a source you control. It does not handle markdown
fences, surrounding prose, or a payload truncated mid-token, which are the actual LLM failure
modes. And a full recursive-descent parser means you own a second implementation of JSON semantics
that can drift from `JSON.parse`. Repairing text and then handing it to the platform's own parser
means the parse result is always exactly what the runtime would produce.

---

### Q3. [Intermediate] What's explicitly out of scope, and how did you decide?

**Strong answer covers:** schema validation. `healJson<T>()` gives a type, not a guarantee — Zod
and friends own runtime shape checking, and duplicating it would balloon the bundle past the size
budget for capability that's better composed than absorbed. Also out of scope: rewriting semantic
content (guessing at missing values), because a repair library that invents data is worse than one
that fails loudly.

**Follow-up:** *"How do you decide something is out of scope?"* — if getting it wrong produces
*plausible but incorrect* output rather than a clear failure, it doesn't belong in a repair tool.

---

### Q4. [Advanced] 🔥 What's the worst thing this library could do to a user?

**Strong answer covers:** silently return a *different* object than the model intended — most
plausibly via quote fixing on an ambiguous apostrophe, or bracket balancing closing a truncated
structure in a way that produces a valid object missing half its data. Failing to heal is a
non-event; the user retries. Healing incorrectly is a data-integrity bug that surfaces three layers
downstream. That asymmetry is why the risky steps are conservative and why the pipeline prefers
"fail with a clear message" over "try harder".

---

### Q5. [Intermediate] How would you know if a truncated payload was healed into something wrong?

**Strong answer covers:** you often can't from inside the library — which is the argument for
surfacing *what was done*. Practical answers: return the applied-step list alongside the result so
callers can treat "bracket-balanced a truncated stream" as lower-confidence; validate downstream
with a schema (the composition point from Q3); and for a streaming caller, prefer waiting for the
stream to finish over healing an in-flight prefix.

---

### Q6. [Intermediate] The project has a benchmark suite and a size budget but is a small utility. Isn't that over-engineering?

**Strong answer covers:** both exist because the library's *promise* is "cheap and safe to put in
your hot path." A size budget and a fast-path benchmark are how that promise gets checked
mechanically rather than asserted in a README. The honest framing: for a published package
consumed by other people, the discipline is proportionate; for an internal helper, it wouldn't be.
Being able to say where the line is matters more than defending the choice absolutely.

---

### Q7. [Beginner] Walk me through a milestone. What did you build, what broke, what did you learn?

**Strong answer covers:** pick M3 or M4, not M1. The strongest narrative is: hand-rolled bracket
matching in M3 → hit the "`}` inside a string" wall → that wall is *why* M4 is a shared scanner
rather than another regex. It shows a design being forced by evidence rather than chosen up front,
which is what the question is actually testing.

---

### Q8. [Intermediate] If I gave you one week on this, what would you build next?

**Strong answer covers:** pick something the notes actually justify —
- returning the applied-step list in the success result (turns "healed" into "healed, how"),
- a fuzz/property test that generates valid JSON, corrupts it in a known way, and asserts the heal
  round-trips to the original object — the one test class that could catch silent-wrong-output,
- streaming-aware entry point that knows a payload is a prefix and refuses the riskiest steps.

Naming the fuzz test is the strongest answer, because it targets the worst failure mode from Q4.

---

### Q9. [Advanced] How would you scope this if it had to handle a format that isn't JSON — say YAML or XML?

**Strong answer covers:** the architecture generalises but the risk profile doesn't. The
shape — fast path, extraction, format-aware scanner, ordered repair steps, parse-retry pipeline —
is reusable. But YAML's significant whitespace means truncation and indentation errors are far more
ambiguous, so the "silently wrong" risk goes up sharply. The right answer is a shared pipeline
skeleton with a per-format scanner and step set, not one universal healer.

---

### Q10. [Beginner] You showcased this on two Next.js sites. Why does that matter for a library?

**Strong answer covers:** it's the first time the package is consumed the way a stranger consumes
it — installed from the registry, resolved through the `exports` map, bundled by someone else's
toolchain. Packaging bugs (wrong types resolved, CJS/ESM interop, missing files in the published
tarball) are invisible from inside the repo and obvious the first time you install it elsewhere.

---

### Q11. [Intermediate] What would you do differently if you started over?

**Strong answer covers:** the honest one — build the scanner first. M2 and M3 were built with
regex/manual matching and then partly re-founded on scanner state; the wall in M3 was predictable
from the problem statement ("is this character inside a string?" is *the* question in text
repair). Counterpoint worth voicing: hitting the wall produced a much clearer understanding of why
the scanner's interface needed to be what it is, so it wasn't wasted — just longer than necessary.

---

### Q12. [Advanced] A user reports json-healer produced valid JSON with the wrong values. How do you debug it?

**Strong answer covers:** a real process, in order — (1) get the exact raw input, since the bug is
input-dependent and unreproducible without it; (2) run the pipeline step by step and diff the
string after each, which localises the corrupting step immediately; (3) once identified, add the
input as a regression fixture *before* fixing; (4) fix by making that step more conservative, not
by special-casing the input; (5) check whether the same ambiguity class affects the other steps.
Mentioning "add the fixture first" is what separates this from a guess-and-patch answer.
