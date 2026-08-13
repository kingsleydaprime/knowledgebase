# strictenv — Testing, Packaging & Project Story

Milestones 1, 8, 9, 10 — plus the behavioural questions wrapped around the project.

---

### Q1. [Advanced] 🔥 How do you test a function whose default behaviour is to call `process.exit(1)`?

**Strong answer covers:** you can't wrap it in `expect(() => ...).toThrow()` — `process.exit` really
terminates the process, test runner included, and doesn't respect try/catch. By the time it runs
there's no JS stack left to catch anything in. The fix is to mock the side-effecting primitive
itself: `vi.spyOn(process, "exit").mockImplementation(() => undefined as never)` (plus mocking
`console.error` to keep output clean), then assert the *call* was made with `1`.

**Real detail worth telling:** this bit for real. Earlier milestones tested the failure path with
`.toThrow()` because the placeholder implementation threw a plain `Error`. When the real
print-and-exit behaviour landed in M7/M8, those unchanged tests would have killed the vitest worker.

**Generalise it:** any "halt everything" code path is tested by mocking the specific primitive that
halts, not by catching the effect afterwards.

---

### Q2. [Intermediate] 🔥 You organised the integration suite one `describe` block per PRD requirement. What did that actually catch?

**Strong answer covers:** it turned "is this covered?" from a judgement call into a checklist with a
visibly empty box. Concretely: `fixtures/.env.quoted` had been created back in M6 for a plausible
future need and never exercised end-to-end — the quoted/escape behaviour was only covered by
low-level `parseEnvFile` unit tests, never through the real `defineEnv` path. The FR-by-FR pass
surfaced that gap immediately, and it closed with one test loading that exact fixture through the
public API.

**The insight:** fixtures created early for a future need quietly go unused unless something loops
back to check that every fixture is exercised by a test matching why it was created. A
requirements-to-tests mapping pass is a cheap mechanical way to catch that drift.

---

### Q3. [Advanced] 🔥 Your test suite was fully green. Why did you still write a manual `require()` / `import` smoke test?

**Strong answer covers:** vitest transpiles and runs your **source** — it never imports `dist/`. So a
green suite says nothing about whether tsup's bundling, minification, or dual CJS/ESM output are
correct. Two throwaway scripts — one `.cjs` doing `require("./dist/index.cjs")`, one `.mjs` doing
`import` from `dist/index.js` — calling `defineEnv` against a real fixture file are the *only* check
in the whole pipeline that verifies the artefact actually published to npm is the one that works.

This is a genuinely strong thing to volunteer: "all green" and "ready to publish" are different
claims, and most people conflate them.

---

### Q4. [Intermediate] How do you verify a gzip size budget, and why not just check raw byte count?

**Strong answer covers:** raw bytes are a proxy that can move in the wrong direction — minified code
with lots of repeated identifiers compresses very differently from code with lots of unique string
literals. The check gzips the real output with Node's built-in `zlib.gzipSync` (no dependency
needed) and compares against the literal budget. Actual numbers: **2866 bytes raw, 1383 gzipped**
against a 2048-byte budget; `size-limit` independently reports 1.37 kB, and the small delta is its
own bundling step. Two checks agreeing from different angles is the point.

**Comparison worth drawing:** the sibling `json-healer` had to relax its budget slightly for a
larger feature set (scanner + pipeline internals). strictenv's surface is mostly straight-line
coercion and parsing, so the real target was achievable without negotiating it down.

---

### Q5. [Intermediate] Why is this project Node-only when `json-healer` is deliberately isomorphic?

**Strong answer covers:** the requirement drives the config, not the other way round. strictenv
*is* `process.env`, `process.exit`, and file reads — there's no meaningful browser surface, so the
tsconfig adds `"types": ["node"]` and a real `@types/node` dev dependency. `json-healer` is pure
string transforms with no I/O, so it omits both DOM and Node types to make platform coupling a
compile error. Same author, same week, opposite decisions — because the isomorphic trick only makes
sense when the code genuinely has no platform dependency.

Being able to articulate a decision *and* the case where you made the opposite one is what makes it
read as judgement rather than habit.

---

### Q6. [Beginner] Where does this belong in an application's lifecycle, and what does that mean for how it's used?

**Strong answer covers:** the very top of the entry point, before any framework or server bootstraps
— that's the whole value proposition. The typed result is then imported everywhere else, so the rest
of the codebase never touches `process.env` directly. If code reads `process.env.PORT` in a request
handler, the library's guarantee is bypassed and you're back to `string | undefined` at runtime.
Worth mentioning: a lint rule banning direct `process.env` access outside the config module is how
you actually enforce it.

---

### Q7. [Intermediate] What happens in a serverless or edge environment?

**Strong answer covers:** honest limits. `process.exit(1)` in a serverless container kills the
invocation rather than the deploy, so the fail-fast guarantee is weaker — you want `onError` there
to throw so the platform surfaces it as an invocation error. File loading is largely irrelevant
since env comes from the platform. And edge runtimes may not have `process` at all, which is exactly
the platform coupling the tsconfig makes explicit. Say what doesn't work rather than claiming
universal fit.

---

### Q8. [Advanced] Nine of ten milestones had "nothing broke." Is that a sign of good work or of not pushing hard enough?

**Strong answer covers:** both readings deserve airtime. The defensible one: most milestones were
straight composition of already-tested pieces, and the design work happened *before* the code —
working out the two precedence axes, the `ENOENT`-specific catch, and the alternation-order
reasoning on paper meant those milestones had nothing left to discover at runtime. The final
milestone passing everything on the first run is the actual signal: compounding mistakes from nine
earlier milestones would otherwise all surface at integration.

The honest counterweight: the milestones that *did* break — the narrowing bug, the alignment test,
the `process.exit` test — were all discovered by a check that hadn't been run before (typecheck, a
new assertion style, a changed default). Absence of failure mostly measures the checks you're
running, so the useful question is what check *wasn't* in place.

---

### Q9. [Intermediate] What's still missing from this library?

**Strong answer covers:** pick real ones — no enum/union type (`NODE_ENV` as `"dev" | "prod"` is a
very common need and currently just `string`), no custom validator hook per field (URL format,
port range), no `.env.example` generation from the schema (the schema already contains everything
needed for it), and no way to mark a value secret so it's masked in the error table. Also worth
naming: nothing stops the rest of the codebase reading `process.env` directly.

---

### Q10. [Beginner] Why build this at all when `dotenv` exists?

**Strong answer covers:** they solve different halves. `dotenv` *loads* a file into `process.env`
and stops there — every value is still `string | undefined`, nothing is validated, and a missing
variable surfaces as `undefined` deep inside whatever code first needed it. strictenv covers
loading *plus* typing, coercion, required-checking, and boot-time failure with a full report. The
honest note: the loading half is a small part of the work, and the file parser here exists mainly
so the library has no runtime dependency at all.

---

### Q11. [Advanced] You built strictenv and json-healer back to back. What transferred, and what didn't?

**Strong answer covers:** transferred — the milestone discipline (test + typecheck after each
change, never carry a red suite forward), dual-format packaging and its `exports` map, the
"set the real budget on day one" rule, README structure. Didn't transfer — the tsconfig platform
decision (deliberately opposite), and the internal architecture: json-healer needed a shared scanner
because its steps all ask the same stateful question, while strictenv's per-field validation is
genuinely independent and composing it in a loop was the right shape. Reusing the *process* while
re-deriving the *architecture* per problem is the point.

---

### Q12. [Intermediate] Tell me about a time your first design was wrong and you changed it.

**Strong answer covers:** the `isAbsent` helper is the cleanest story — extracted for readability,
silently defeated TS narrowing, and the *obvious* fix (make it a type predicate) would have been
worse than the bug, because the predicate would have lied about the empty-string case. Ended up
inlining the check. Two-beat story: the fix that looked right, and why it wasn't. That structure
lands better than a straight "I made a mistake and fixed it."
