# my-applicant — AI & LLM Engineering

From [`../learning/02-ai-sdk-and-byok.md`](../learning/02-ai-sdk-and-byok.md). This is the file to
know cold if you're interviewing for anything AI-adjacent.

---

### Q1. [Intermediate] 🔥 Why put an SDK abstraction in front of the model instead of calling Anthropic directly?

**Strong answer covers:** because **provider choice is the product**. The pitch is "your key, your
model", and that only holds if switching provider is a config line rather than a rewrite. The
Vercel AI SDK gives one `generateText` interface over Anthropic, OpenAI, Google, OpenRouter, Ollama
and anything OpenAI-compatible, so the whole provider layer collapses to a switch returning a
`LanguageModel`, and everything downstream — scoring, tailoring, parsing — is provider-agnostic.

**The part that makes this a senior answer:** *"If the tool only ever talked to Claude, the
Anthropic SDK would be simpler and better."* Add an abstraction when **varying the thing is a
requirement**, not because varying it is conceivable. Here it was the requirement. Most of the time
it isn't, and the abstraction is a cost. Interviewers hear a lot of reflexive abstraction; hearing
the condition stated correctly stands out.

---

### Q2. [Intermediate] 🔥 You say you never write this SDK from memory. Why not, and what do you do instead?

**Strong answer covers:** the SDK changes across majors and training data goes stale — two APIs
that "obviously" existed did not:

| Remembered (v5-era) | Actual (v7) |
|---|---|
| `system: '...'` | `instructions: '...'` |
| `generateObject({ schema })` | `generateText({ output: Output.object({ schema }) })` |

Both would have compiled as plausible-looking wrong code and failed at runtime — the worst kind of
error, because it looks right in review. The fix: the package **ships its own version-matched
docs** inside `node_modules` (`node_modules/ai/docs/...`, `node_modules/@ai-sdk/anthropic/docs/...`).
Reading those beats any web search, because they cannot be out of sync with what's installed.

**Generalise it:** when a library ships docs or `.d.ts` files in `node_modules`, that's the
authoritative source — on disk, version-matched, faster than searching.

---

### Q3. [Beginner] 🔥 Explain BYOK as you implemented it. Where does the key live?

**Strong answer covers:** the config file names the *environment variable*, never the value:
`llm: { apiKeyEnv: ANTHROPIC_API_KEY }`. Consequences — `config.yaml` is safe to read over
someone's shoulder, the key lives only in the process environment, and `git push` on the repo can
never leak one. (`.gitignore` still excludes the config anyway, because `profile.yaml` beside it
holds personal data — belt and braces.)

**The pattern in one line:** config names the secret, the environment holds it.

---

### Q4. [Advanced] 🔥 Your provider validation has a set of providers that require a key — and Ollama isn't in it. Why does that matter?

**Strong answer covers:** Ollama runs on `127.0.0.1` and authenticates against nothing. Demanding a
key would be an **invented requirement** — and local models are the main reason to want BYOK at
all, so the check would have silently blocked the offline use case. Hence
`PROVIDERS_REQUIRING_KEY` as an explicit allow-set with `ollama` and `custom` deliberately absent.

**The general lesson:** "an API needs a key" is true often enough to feel universal. When you write
a required-field check, ask **which legitimate configuration it makes impossible**. That question
catches a whole class of over-validation.

---

### Q5. [Advanced] 🔥 Your tailoring prompt says "do not invent skills." Why isn't that sufficient?

**Strong answer covers:** because it's a **request**, not a guarantee. The model usually complies.
Usually isn't good enough when the failure mode is a fabricated line on a résumé you have to defend
in an interview. So after generation, `verify()` checks every claim against the profile and strips
what doesn't match — canonical skill lookup against a known set, with anything unmatched recorded as
a violation.

**The three properties worth naming:**
1. **The check is mechanical** — a set membership test, no judgement, no second model.
2. **Violations are surfaced, not swallowed** — a model that keeps inventing is information, about
   the model *or* about a too-sparse profile.
3. **Violations change the routing** — any violation forces the application into the review queue
   even in auto mode, because a model that fabricated one thing may have fabricated another the
   checker can't see.

**The one-liner to land:** when an LLM output feeds an irreversible action, validate it against
ground truth you control. **Prompts shape behaviour; code guarantees it.**

---

### Q6. [Advanced] Why not use a second LLM call to check the first one's output?

**Strong answer covers:** an LLM judge has the same failure mode as the generator and no ground
truth — it can only assess plausibility, and a fabricated-but-plausible skill is exactly the case
that must be caught. The profile *is* the ground truth and it's a finite set, so a set-membership
check is both cheaper and strictly more reliable. LLM-as-judge earns its place for fuzzy criteria
(tone, relevance) where no ground truth exists; it's the wrong tool when you have one.

---

### Q7. [Intermediate] How do you get structured output, and what changes if a provider doesn't support it?

**Strong answer covers:** structured output via the SDK's `Output.object({ schema })` on
`generateText` (not the remembered `generateObject`) — the schema is defined once and reused for
parsing and for downstream types. Providers differ in support: OpenAI-compatible endpoints and local
models may not honour a schema, so the code has to **degrade** — fall back to prompted JSON plus
parsing, and treat a parse failure as a normal, handled outcome rather than a crash. Given the BYOK
premise, "assume every provider supports structured output" is not a safe assumption.

---

### Q8. [Intermediate] Why is scoring a *batched* model call while tailoring is per-job?

**Strong answer covers:** the work is comparative. Scoring asks "how does this job rank against my
profile," and sending many jobs in one call is both cheaper (one prompt overhead, not N) and
*better*, because the model can calibrate across the set instead of scoring each in isolation with a
drifting internal scale. Tailoring is genuinely per-job — the output is a bespoke document — so
there's nothing to share.

**The rule:** batch when the work is comparative; don't batch when each output is independent and
large.

---

### Q9. [Advanced] What are the costs of batching, and where does it break?

**Strong answer covers:** context limits (a batch that's too large gets truncated, silently
degrading the tail), correlated failure (one malformed response loses the whole batch, so batch size
is a blast-radius decision), and position bias — models can weight earlier items differently, which
matters when the output is a ranking. Mitigations: bounded batch size, per-item IDs in the response
so a partial parse is still usable, and treating batch results as needing the same verification pass
as anything else.

---

### Q10. [Intermediate] "Schema-once, use-everywhere" — what does that mean here?

**Strong answer covers:** the same schema definition drives the model's structured output *and* the
TypeScript type the rest of the pipeline consumes. One definition means the parsing code and the
consuming code cannot drift apart — if the schema changes, the type changes, and every consumer
fails to compile rather than failing at runtime on a missing field. It's the same instinct as
generating DB types from the schema rather than hand-writing them.

---

### Q11. [Beginner] How would you evaluate whether the tailoring is actually any good?

**Strong answer covers:** be honest that this is the weakest measured part. Available signals:
violation rate from `verify()` (mechanical, already collected), review-queue outcomes — if a human
edits every queued application heavily, tailoring is poor — and downstream response rate, which is
the real metric but is slow, noisy, and confounded by everything else. A defensible answer names a
small hand-labelled evaluation set as the thing you'd build if this mattered commercially, rather
than claiming the current system measures quality.
