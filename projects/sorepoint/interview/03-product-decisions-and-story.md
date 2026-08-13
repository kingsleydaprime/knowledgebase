# Sorepoint — Product Decisions, Frontend & Story

The design and judgement questions. Draws on
[`../learning/frontend.md`](../learning/frontend.md) and the SPEC/DECISIONS reasoning captured
across the learning notes.

---

### Q1. [Intermediate] 🔥🔥 You scan businesses that didn't ask to be scanned, then mail them a fix. Isn't that cold outreach at best and creepy at worst?

**Prepare this one properly — it's the product's central question, not a gotcha.**

**Strong answer covers, in order:**
1. **Concede the real concern.** Unsolicited outreach at volume is spam, and "I built a tool that
   does it faster" is not a defence.
2. **What makes this different in design.** It's not a blast — each business gets *one* finding,
   chosen as the single worst *fixable* flaw, with the fix already built. The unit of outreach is a
   deliverable, not a pitch.
3. **The honesty machinery is the ethical machinery.** A signal that couldn't be determined is
   `null`, not `false`; a site that blocked the crawler is recorded as evidence about *us* and
   marked `unscanned`, never reported as their flaw. That's what stops the product from mailing
   someone an accusation it can't support.
4. **Where the line is.** Volume caps, respecting opt-outs, and never claiming a finding derived
   from a heuristic (`<meta viewport>`) as a definitive audit result.

**What not to do:** don't lean on "everyone does cold email." The interesting answer is that data
integrity and ethics are the same constraint here — being wrong in public about someone's business
is the failure mode.

---

### Q2. [Advanced] 🔥 Six agents compete and one wins. How should that ranking work, and why "evidence-weighted"?

**Strong answer covers:** the winner isn't "highest severity" — it's the finding best supported by
what was actually observed. An agent whose inputs were `null`/`unscanned` cannot win, however severe
its category would be, because there's no evidence behind it. So ranking has to weight (a) how
confident the signal is (a hard `dns` failure vs a `<meta viewport>` heuristic), (b) how fixable the
flaw is — the product ships the fix, so an unfixable flaw is worthless — and (c) severity last.

**The framing to state:** a ranking over findings of *different confidence levels* is not a
comparison of numbers; treating a heuristic and a definite observation as commensurable is exactly
how you mail someone a wrong claim.

---

### Q3. [Intermediate] 🔥 "Honest coverage UI" — what does that mean concretely?

**Strong answer covers:** the dashboard must distinguish **"we checked and it's fine"** from **"we
couldn't check"**. That's why `unscanned` exists as a first-class state all the way from the
crawler through to the UI, rather than collapsing into a pass. A UI that renders unknown as green is
lying to the operator, and the operator is the person deciding whether to send an email.

**The connective tissue worth pointing out:** the `null`-not-`false` rule in the crawler exists
*because* of this UI requirement. The data model was chosen to make an honest interface possible;
if the crawler defaulted to `false`, no amount of UI work could recover the distinction.

---

### Q4. [Intermediate] Your frontend notes say "this is NOT the Next.js you know — read the bundled docs first." Explain.

**Strong answer covers:** the version installed by `create-next-app` moves faster than anyone's
memory of it, and writing from a two-versions-ago mental model produces code that looks right and
behaves differently. The habit is to read the docs shipped with the installed version rather than
recalling patterns or searching the web, which returns answers for whatever version was popular when
the article was written.

**Same instinct, different project:** the AI SDK v7 lesson in `my-applicant` — check what's actually
installed, not what you remember. Naming that as a general habit rather than a one-off is the
stronger answer.

---

### Q5. [Intermediate] Tailwind v4 is CSS-first with no `tailwind.config.js`. What actually changed?

**Strong answer covers:** configuration moved into CSS — theme tokens are declared with `@theme` in
the stylesheet and the config file is gone, so the source of truth for design tokens is the CSS
itself rather than a JS object consumed at build time. Practically: half the Tailwind answers online
tell you to edit a file that doesn't exist in this project, which is the same
read-the-installed-docs point as Q4.

---

### Q6. [Advanced] Why does `unscanned` need to be a state rather than just a missing row?

**Strong answer covers:** absence is ambiguous — "we never looked" and "we looked and found nothing"
are the same absence, and only one of them justifies re-running work or suppressing a finding.
Making it explicit means the ranking layer can exclude unsupported agents, the UI can show honest
coverage, and the pipeline can distinguish "retry this" from "this is done." Same principle as
recording a `skipped` decision in `my-applicant`: **record the negative outcome, don't leave a hole
where it was.**

---

### Q7. [Intermediate] The project name was chosen after checking npm and the web for collisions. Why bother?

**Strong answer covers:** it's cheap and the downside is expensive — discovering a name collision
after a domain, a package, and a repo history exist means renaming across all three, or living with
a confusing one. Practically it's a few `npm view` / search commands before committing to anything.
Small, but it's the kind of thing an interviewer reads as "thinks a step ahead."

---

### Q8. [Advanced] What's the biggest technical risk in the product as designed?

**Strong answer covers:** pick one and commit —
- **Signal quality.** Every finding rests on cheap heuristics from a single fetch. `<meta viewport>`
  is a proxy for mobile-readiness and TTFB-to-headers is a proxy for slowness; a business whose site
  is fine can be flagged, and there's no feedback loop that would tell you.
- **Data coverage.** OSM coverage varies enormously by region and category (0 dentists in Lagos), so
  the addressable market is uneven in a way that isn't visible until you query.
- **The irreversibility of sending.** Once an email goes out with a wrong finding, no code change
  takes it back — which is the same asymmetry that drives `my-applicant`'s autonomy tiering, and
  argues for a human review step before send.

---

### Q9. [Intermediate] If the pipeline had to run for a thousand cities, what breaks first?

**Strong answer covers:** the free external services. Nominatim and Overpass are fair-use, one
request per scan is fine, and a thousand scans is a different relationship with those services
entirely — you'd need caching of geocodes (a city's bounding box is static), scheduling/rate
budgeting, and probably a paid or self-hosted Overpass. The worker architecture itself scales
fine — it's already resumable and cache-first — so the honest answer is that the bottleneck is
someone else's goodwill, not your code.

---

### Q10. [Beginner] What would you build next, and why that?

**Strong answer covers:** the answer that shows product judgement is a **review-before-send step**
plus outcome tracking, not more agents. More agents increase the surface for a wrong claim; a review
gate and a record of what happened after each send are what would tell you whether any of the six
agents is actually finding things worth fixing. Volunteering "not more features, more feedback" is
the point.
