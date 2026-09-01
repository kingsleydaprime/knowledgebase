# Communicating Analysis

**[Intermediate]** — the half of the job that isn't technical, and the reason good analyses get ignored while worse ones drive decisions.

## The kid version first

You did the analysis, found the answer, and it's correct. **You're only halfway done.** If you communicate it as a wall of numbers, or bury the finding on slide 14, or answer a question nobody asked, it changes nothing — and an analysis that changes nothing has failed, however correct it was. **The best analysts are the ones whose findings actually get acted on**, and that's a communication skill as much as a technical one.

This is the note the whole track has been pointing at: [[data-analysis/01-what-data-analysis-is|the deliverable is a decision]], and communication is how the analysis *becomes* one.

## Why this is half the job

A technically brilliant analysis communicated badly loses to a mediocre analysis communicated well — because **decisions are made by people, and people act on what they understand and remember, not on what's most rigorous.** The analyst who can make a finding *land* — clear, memorable, tied to an action — has more impact than the one with better statistics and worse slides. This isn't a knock on rigour; it's that rigour is *necessary and not sufficient*. The [[ai-ml/01-data-scientist/README|data-scientist track]] opens with the same lesson, because it's the one both disciplines most underweight early.

## Lead with the answer

**The single most important habit: start with the conclusion, not the journey.**

Analysts love to walk through their process — the data, the caveats, the method, and *then* the finding. **Stakeholders want the opposite:** the answer first, then the support if they want it. This is the "**BLUF**" principle — Bottom Line Up Front:

```
   BAD:   "So I pulled the orders table, joined it to users, filtered out test
           accounts, segmented by device, and after checking for seasonality... "
           → the exec has stopped listening

   GOOD:  "Mobile checkout is broken in Germany — it's costing us ~£40k/week,
           and it started with Tuesday's release. Here's the evidence."
           → now they're leaning in
```

**The pyramid principle:** answer → key reasons → supporting detail. Anyone can stop reading at any level and still have the thing that matters. **Put the "so what" in the first sentence, the subject line, the slide title** — not at the end.

## The "so what" — the test every finding must pass

Before communicating anything, ask: **"so what?"** — what should someone *do* differently because of this?

- *"Conversion is 3%."* → So what? (nothing) → **not worth reporting**
- *"Conversion dropped to 1% on mobile after Tuesday's release, costing £40k/week."* → So what: fix the release → **worth reporting, and it names the action**

**A finding without a "so what" is trivia.** If you can't articulate what changes because of it, either dig until you can or don't send it. This single question filters most of what analysts are tempted to report → [[data-analysis/03-metrics-and-kpis|actionable over interesting]].

## Data storytelling

A finding is more memorable and persuasive as a *narrative* than a table:

- **A story has structure** — setup (here's the situation), tension (here's what's wrong / what changed), resolution (here's what to do). It's how humans process and remember information
- **One chart, one message** — each visual makes a single point, with the point *stated in the title* ("Mobile conversion halved after the release," not "Conversion by device over time"). The reader shouldn't have to interpret; you interpret *for* them → [[data-analysis/07-dashboards-and-bi|dashboard design]]
- **Tailor to the audience** — an executive wants the decision and its size; a product manager wants the specific broken step; an engineer wants the exact error. **Same finding, different framing.** Sending the exec the engineer's version (or vice versa) fails both
- **Anticipate the next question** — "why?", "how big?", "are you sure?", "what do we do?" — and have the answer ready

## Honesty and avoiding misleading

The analyst has a duty to be *honest*, including about their own uncertainty — and it's tempting not to be, because a confident, clean story is more persuasive than a caveated one:

- **State uncertainty and limitations** — the sample size, the assumptions, what you *couldn't* determine. **A finding presented as more certain than it is will eventually blow up**, and it takes your credibility with it
- **Don't mislead with visuals** — truncated y-axes that exaggerate, cherry-picked date ranges, dual axes implying a relationship, 3D pie charts. **The same chart can tell the truth or a lie**; choose truth even when the lie is more compelling → [[ai-ml/01-data-scientist/05-data-visualization|misleading visualisations]]
- **Say "associated," not "caused," unless you've earned it** → [[data-analysis/04-exploratory-and-diagnostic-analysis|correlation ≠ causation]]
- **Present the finding, not the one you (or the stakeholder) wanted** — resisting pressure to make the data say what someone hoped is the core of analyst integrity

**Credibility is the analyst's real currency.** It's built slowly through honest, reliable findings and destroyed instantly by one confident answer that was wrong — after which nobody trusts your dashboards.

## From insight to action — closing the loop

The finding isn't the end; the *decision and its outcome* are:

- **Make a recommendation**, don't just present data. Stakeholders often want the analyst's judgement — "based on this, I'd recommend X" — not a neutral data dump they have to interpret. (Offer the recommendation *and* the evidence, so they can disagree with the reasoning.)
- **Follow up** — did the decision get made? Did it work? Closing the loop is how you learn whether your analysis was *useful*, not just correct, and it's how you build the track record that makes the next finding trusted
- **The relationship matters** — an analyst embedded with and trusted by a team drives more decisions than a better analyst treated as a report-vending machine

## Key insight

**Communication is half the analyst's job, because a correct finding that isn't understood or acted on has failed — so lead with the answer (bottom line up front), make every finding pass the "so what" test (what changes because of this?), and tell it as a tailored story where each chart states its own message.** Honesty is the constraint: state your uncertainty, never mislead with a truncated axis or an unearned causal claim, and present the finding rather than the one someone wanted — because credibility is the analyst's currency, built slowly and destroyed by a single confident wrong answer. The loop closes not at the finding but at the decision and its outcome.

## Related
- [[data-analysis/01-what-data-analysis-is|the deliverable is a decision]] — the framing this note delivers on
- [[data-analysis/07-dashboards-and-bi|dashboards and BI]] — dashboards vs reports as communication
- [[ai-ml/01-data-scientist/05-data-visualization|data visualization]] — charts that inform rather than mislead
- [[data-analysis/03-metrics-and-kpis|metrics and KPIs]] — actionable over vanity

*Source: [reference] — Sep 2026.*
