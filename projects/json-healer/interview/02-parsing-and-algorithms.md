# json-healer — Parsing & Algorithms

The core of the library, and the part an interviewer will actually dig into. Milestones 2–9.

---

### Q1. [Intermediate] 🔥 Where exactly is regex the right tool in this project, and where does it stop working?

**Strong answer covers:** regex is right when the problem is about **structural boundaries** —
markdown fence markers always sit on their own line, delimited by a literal ` ``` `. It stops
working the moment the question becomes *semantic*: "is this comma inside a string value?" A regex
has no notion of parser state, so it cannot distinguish a trailing comma from a comma inside
`"a, b"`. That wall is exactly what motivated building a real scanner in M4 — fence-stripping and
block-extraction get to stay regex-only precisely because they run *before* any reasoning about
JSON string semantics.

Being able to name the boundary — not "regex is bad" but "regex is correct up to here" — is the
answer they're looking for.

---

### Q2. [Intermediate] Your closed-fence pattern is non-greedy. What breaks if it's greedy?

**Strong answer covers:** a greedy `[\s\S]*` spans from the *first* opening fence to the *last*
closing fence in the input, swallowing every intervening block into one match. With two fenced
blocks — an example followed by the real payload — you'd extract the concatenation of both plus
the prose between them. Non-greedy (`[\s\S]*?`) stops at the first closer.

---

### Q3. [Intermediate] The model returns two fenced blocks: a code example, then the real JSON. How do you pick the right one?

**Strong answer covers:** don't take the first fence in document order. Use `matchAll` to collect
*all* closed fences, then prefer the first whose trimmed content starts with `{` or `[`. The
selection is content-based, not position-based. Same principle guards the inline-backtick case —
a stray `` `verbose` `` in a sentence is only treated as a fence if what's inside looks
JSON-shaped.

---

### Q4. [Advanced] 🔥 You initially built fence-stripping as "delete the markers." Why was that wrong, and what did you change it to?

**Strong answer covers:** deleting markers leaves the surrounding chatter in the string —
`"Here is your data:\n```json\n{...}\n```\nLet me know!"` becomes two sentences wrapped around
valid JSON, which still doesn't parse. The fix was to make the step **extract** the chosen fence's
content and discard everything outside it. The deeper point: when a fence is present it's the most
reliable signal available for where the payload lives, so it's correct — good, even — for this
step to lean on it fully, and let block-extraction handle only the no-fence case.

---

### Q5. [Intermediate] How does block extraction find the end of the JSON when there's no fence?

**Strong answer covers:** find the first `{` or `[` (`input.search(/[{[]/)`), then walk forward
with a depth counter — openers increment, closers decrement — and stop when depth returns to zero.
If you run off the end of the input before that happens, the payload is truncated: take everything
from the opening bracket to end-of-string and let bracket-balancing (M7) close it.

**Follow-up they'll definitely ask:** *"What breaks in that depth counter?"* — a `}` inside a
string value (`{"note": "use } carefully"}`) decrements depth and terminates the block early.
That's the exact failure that forced the shared scanner.

---

### Q6. [Advanced] 🔥 Describe the shared scanner. What state does it track and why does everything downstream depend on it?

**Strong answer covers:** a single left-to-right character walk that maintains parser state —
whether the cursor is currently **inside a string**, and whether the previous character was an
**escape** (`\`), so an escaped quote doesn't toggle string state. With that state available, every
later step asks a question it couldn't ask before: trailing-comma removal only considers commas
seen *outside* a string; bracket balancing only counts brackets outside strings; quote fixing knows
which quotes are structural. Building it once and sharing it means these steps agree with each
other by construction rather than each re-deriving string state slightly differently.

**Follow-up:** *"Isn't that just writing a JSON parser?"* — it's the tokenizer half, deliberately
without the grammar half. It needs to know where strings are; it never needs to build a value tree,
because `JSON.parse` does that once the text is repaired.

---

### Q7. [Intermediate] Trailing commas: what makes them hard, given a scanner?

**Strong answer covers:** with scanner state the hard part is gone — you only inspect commas
outside strings, then look ahead past whitespace for a `}` or `]`. Without it, `{"a": "x,"}` and
`{"a": 1,}` look the same to a regex. Worth saying that the *detection* is easy and the *ordering*
matters: this step must run after extraction (so you're not scanning prose) and before parse
retry.

---

### Q8. [Advanced] Quote fixing is the riskiest step. Why?

**Strong answer covers:** it's the one step that can turn *recoverable* input into *wrong* output.
Converting single quotes to double quotes is only safe for quotes acting as structural delimiters;
an apostrophe inside a value (`{'note': 'it's fine'}`) is genuinely ambiguous — there's no
information in the string that tells you which `'` was meant as a delimiter. So the step has to be
conservative and anchored on scanner state and position (key position, value start) rather than
blanket-replacing. A heal library's worst outcome isn't failing to fix something; it's silently
producing a *different* object than the model meant.

---

### Q9. [Intermediate] Bracket balancing has to close a truncated payload. In what order do you close, and how do you know?

**Strong answer covers:** the scanner gives you a stack of *unclosed* openers in the order they
were opened; you close them in reverse (LIFO) — innermost first. You also have to handle a stream
cut mid-string: close the string before closing the containers, otherwise the appended `}` lands
inside the string literal. And a stream cut mid-key or after a dangling comma needs that fragment
dropped before closing, or you produce syntactically valid JSON with a garbage key.

---

### Q10. [Intermediate] 🔥 Describe the pipeline. Why not just run every heal step every time?

**Strong answer covers:** the fast path is `JSON.parse` in a try/catch — valid input costs one
parse and nothing else. On failure, steps run in a fixed order (fences → block → commas → quotes →
brackets), each returning `{ output, changed }`. The `changed` flag lets the pipeline skip
redundant re-parses (nothing changed, so retrying `JSON.parse` on identical text is pure waste) and
lets the final error message report *what was actually attempted*. Running everything unconditionally
is both slower and more dangerous — every step is an opportunity to corrupt input that a later,
gentler step would have fixed.

---

### Q11. [Intermediate] Why does the order of the steps matter? Give a concrete pair.

**Strong answer covers:** fence-stripping must precede block extraction, because a fence is a
stronger signal than bracket-scanning and the fence content may contain prose-looking brackets.
Bracket balancing must come last, because it's the only step that *adds* characters — running it
before comma removal could balance a structure that still contains a trailing comma, producing
valid-looking-but-unparseable text and a worse error message.

---

### Q12. [Advanced] When the input is unrecoverable, what does the error message say?

**Strong answer covers:** not just "invalid JSON". The pipeline knows which steps ran and which
reported `changed: true`, so the failure can report the sequence attempted and the underlying
`JSON.parse` error from the final attempt. For a library whose users are debugging a *model's*
output, "I stripped a fence and extracted a block, then parse still failed at position 412" is the
difference between a usable library and a black box.

---

### Q13. [Intermediate] You built a benchmark suite. What did you measure, and what would make a benchmark here misleading?

**Strong answer covers:** the two paths have completely different cost profiles, so measure them
separately — already-valid input (one `JSON.parse`, the case that must stay near-free) versus each
class of malformed input. A benchmark that averages the two hides a regression in either. Also
measure against *realistic* payload sizes, since scanner cost is linear in input length and a
100-byte fixture tells you nothing about a 200 KB model response.

---

### Q14. [Advanced] What's the algorithmic complexity, and where's the worst case?

**Strong answer covers:** each step is a single linear pass, and there's a bounded number of steps,
so it's O(n) per attempt with a small constant — but the pipeline may re-parse between steps, so
the real bound is O(k·n) for k steps. The pathological input is one that is *almost* valid in a way
that triggers every step and still fails, paying full price for no result. That's an argument for
the `changed` flag doing real work, not just improving error messages.
