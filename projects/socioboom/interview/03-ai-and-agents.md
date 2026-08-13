# SocioBoom — AI & Agents

From [`../learning/backend/06-ai-and-agents.md`](../learning/backend/06-ai-and-agents.md) and
[`07-feature-case-studies.md`](../learning/backend/07-feature-case-studies.md).

**The strongest AI-engineering material in the vault.** If you're interviewing anywhere near LLM
products, know this file cold.

---

### Q1. [Intermediate] 🔥 Why is there a provider abstraction in front of the model?

**Strong answer covers:** the app needs to work against more than one provider — Anthropic directly
and OpenRouter as a fallback/breadth layer — so the calling code shouldn't know which is behind it.
The abstraction exposes two operations (free-text generation and *structured* generation) and hides
provider differences.

**The honest framing:** an abstraction is justified when varying the thing is a requirement, not when
it's conceivable. Here it is, and the reason is visible in Q3 — the structured-output *mechanism*
differs between providers, so without an abstraction that difference leaks into every caller.

---

### Q2. [Intermediate] 🔥 Single-shot prompts vs agents — how do you decide?

**Strong answer covers:** a **single-shot** prompt is right when the task is a transformation of
input you already have — draft this post, rewrite in this tone. It's cheap, predictable, one call,
and easy to evaluate. An **agent loop** is right when the model needs to *gather information it
doesn't have* and the number of steps isn't known in advance — pain-point discovery has to search,
read pages, and decide what to read next.

**The costs of the agent to name:** non-deterministic cost and latency (an unbounded loop is an
unbounded bill), harder evaluation, and a much larger blast radius — a tool-using model can reach the
network, which is why Q5 exists. The rule: **don't reach for an agent when the task is a
transformation; reach for one when it's a search.**

---

### Q3. [Advanced] 🔥🔥 You were extracting JSON from model output with a regex. What was wrong, and what replaced it?

**Strong answer covers the three silent failure modes of the old approach:**
```ts
const match = raw.match(/\[[\s\S]*\]/);   // find something array-shaped
if (!match) return [];                    // silently give up
const posts = JSON.parse(match[0]);       // hope
```
1. The model wraps JSON in prose or markdown fences → the regex may grab garbage.
2. The model apologises instead of answering → `return []` is indistinguishable from "no results."
3. The JSON parses but has the wrong **shape** → it crashes later, far from the cause.

**The fix — forced tool use.** Define a tool whose `input_schema` *is* your output schema, then force
the model to call it:
```ts
tools: [{ name: 'emit_result', input_schema: schema }],
tool_choice: { type: 'tool', name: 'emit_result' },   // ← the forcing
```
The model **physically cannot** reply with prose; the only legal output is arguments matching the
schema. The result arrives already parsed and already schema-shaped.

**The three gotchas — including these is what makes this an expert answer:**
1. **The schema root must be `type: "object"`.** For an array output, wrap it —
   `{ keywords: string[] }`, not `string[]`.
2. **Forced `tool_choice` is incompatible with extended thinking**, which only allows `auto`/`none`.
   So the structured path doesn't pass `thinking`, while the free-text path does.
3. **OpenRouter doesn't support the forcing across all models**, so the fallback is
   `response_format: { type: 'json_object' }` plus a *tolerant* parser. **Tolerance is the fallback,
   not the default** — that ordering is the whole point.

---

### Q4. [Advanced] 🔥🔥 Your agent invented a Reddit URL that passed validation. How did you fix it?

**The best AI-safety story in the vault.**

**Strong answer covers the flawed check:**
```ts
const isReal = url && (realUrls.has(url)
  || /reddit\.com\/r\/\w+\/comments\//.test(url)   // ← the hole
  || /twitter\.com|x\.com/.test(url));
```
A model that invents `https://reddit.com/r/startups/comments/abc123/fake_post/` produces a
**perfectly well-formed** URL — the regex passes it happily, and users click through to 404s.

**The one-line diagnosis:** *you cannot validate provenance with a format check.* Format tells you
whether a string looks like a URL; it can say nothing about whether the page exists or where the
model got it.

**The fix — an allowlist of URLs the system actually observed:** every search result and every
successfully fetched page registers its URL in a `Set` on the research context, and saving a finding
checks **exact membership**:
```ts
const urlVerified = !!postUrl && ctx.seenUrls.has(postUrl);
```
Unverified → the finding is saved with the URL dropped, and the agent is told so:
> `Saved, but the URL was dropped — it never appeared in your search results. Do not invent URLs.`

**The two properties that make it robust, and you should name both:**
1. The check is **exact set membership**, not pattern matching — there's no hole to slip through.
2. The agent gets **feedback when it misbehaves**, which corrects it *mid-run* rather than after the
   fact.

**The generalisation:** ground the model in what the *system* observed, not in what the model
claims. Same rule as `my-applicant`'s `verify()` — prompts shape behaviour, code guarantees it.

---

### Q5. [Advanced] 🔥 Your agent has a `fetch_page` tool. What's the SSRF risk and how do you contain it?

**Strong answer covers:** a tool that fetches an arbitrary URL is a **server-side request forgery
primitive** handed to a non-deterministic caller. The model can be steered — by a prompt injection in
a page it read — into fetching `http://169.254.169.254/` (cloud instance metadata, often including
credentials), internal service addresses, or `localhost` admin endpoints. Your server has network
access the attacker doesn't.

**Containment, layered:** an allowlist of permitted hosts rather than a denylist of bad ones; block
private and link-local address ranges **after DNS resolution** (a public hostname can resolve to
`127.0.0.1`, so checking the string isn't enough); refuse redirects to non-allowlisted hosts, because
a redirect bypasses the check you did on the original URL; enforce a timeout and a response-size cap;
and never forward the response's raw headers or cookies back into the model context.

**The point that ties it together:** the URL allowlist from Q4 and the SSRF defence are the *same*
mechanism serving two purposes — it constrains where the agent can go, and it's what makes the
provenance check possible.

---

### Q6. [Intermediate] Describe the pain-point discovery feature end to end.

**Strong answer covers:** the agent is given a topic and loops — `search_web` for relevant
discussions, `fetch_page` to read the promising ones properly, `save_pain_point` to record findings
with the source URL — until it has enough or hits its bound. Every URL it sees along the way lands in
`seenUrls`, which is what the save step validates against.

**The platform trick worth naming:** append **`.json`** to any Reddit thread URL and you get the post
*and* its comment tree as clean JSON — `data[0]` is the post, `data[1]` the comments — no HTML
scraping. And the comments are often better pain points than the post itself ("came here to say I
have this exact problem"), which is the sort of domain insight that only comes from actually reading
the output.

**Why the read step exists at all:** search snippets are ~150 characters. A pain point extracted from
a snippet is extracted from a headline.

---

### Q7. [Intermediate] 🔥 Describe the Review Poster feature and what makes it risky.

**Strong answer covers:** it drafts posts from source material and schedules them for publication.
The risk is structural: the output of a language model becomes a **public statement under the user's
name**, and publishing is irreversible. So the design constraints are the same family as
`my-applicant`'s — nothing auto-publishes that the user hasn't seen, generated content is drafted
into the scheduling flow rather than pushed straight to a platform, and the AI modules never call the
publishers directly.

**The single-path point:** keeping publishing behind one code path means the review/approval gate can
exist in one place instead of being a promise each feature makes separately.

---

### Q8. [Advanced] Why not use an LLM to check the LLM's output here?

**Strong answer covers:** for the URL problem, a judge model has exactly the same failure mode as the
generator and **no ground truth** — it can assess plausibility, and a plausible fabricated URL is
precisely the case that must be caught. The `seenUrls` set *is* ground truth, and set membership is
cheaper and strictly more reliable. LLM-as-judge earns its place for fuzzy criteria (is this post on
brand? is the tone right?) where no ground truth exists.

**The rule:** if you have ground truth, check against it mechanically. Only reach for a judge when you
genuinely don't.

---

### Q9. [Intermediate] How do you keep AI costs and latency under control?

**Strong answer covers:** bound the agent's steps and tool calls explicitly (an unbounded loop is an
unbounded bill); cap `max_tokens` per task type rather than setting one generous global default —
which is exactly the mistake that OOM-killed NextVibe; run long AI work as a **background job** so it
isn't holding an HTTP request open; cache anything repeatedly derived from stable input; and choose
the cheapest model per task, which is the concrete payoff of having a provider abstraction at all.

---

### Q10. [Advanced] 🔥 How would you know if the agent got *worse* after a model change?

**Strong answer covers — be honest that this is the weak point.** Available signals today are
mechanical: the rate of dropped (unverified) URLs, the number of tool calls per run, and how often a
run ends without findings. Those are cheap and already collected in effect. What's missing is an
**evaluation set** — a fixed list of topics with human-judged expected findings, run on every model
or prompt change, so "the new model is cheaper" can be weighed against "and it's worse at this."

**The framing:** without an eval set, every model upgrade is a bet you can't settle. Saying that
plainly is stronger than claiming a quality process you don't have.
