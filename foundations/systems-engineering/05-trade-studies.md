# Trade Studies

> **[Intermediate]** · Choosing between options defensibly — and the ways a weighted-scoring matrix lies to you.

A **trade study** (trade-off analysis) is the formal method for choosing between design alternatives. It's what turns "we went with Kubernetes" into a decision with a recorded reason.

## The method

1. **State the decision and the constraints** — what's being chosen, and what's non-negotiable
2. **Generate alternatives** — including "do nothing" and at least one you don't like
3. **Define criteria** from the requirements — measurable ones
4. **Weight the criteria** — *before* scoring
5. **Score each alternative**, with evidence
6. **Analyse sensitivity** — does the answer survive plausible changes?
7. **Record the decision and the reasoning**

**Steps 4 and 7 are where the value is.** Weighting before scoring stops you reverse-engineering weights to justify the answer you wanted. Recording the reasoning means that in two years, when circumstances change, you can tell whether the decision is still valid — instead of re-litigating from scratch.

## The matrix

| Criterion | Weight | Battery A | Battery B | Battery C |
|---|---|---|---|---|
| Energy density | 0.30 | 8 (2.4) | 6 (1.8) | 9 (2.7) |
| Cost | 0.25 | 6 (1.5) | 9 (2.25) | 4 (1.0) |
| Cycle life | 0.20 | 7 (1.4) | 7 (1.4) | 8 (1.6) |
| Safety | 0.15 | 9 (1.35) | 8 (1.2) | 5 (0.75) |
| Supply risk | 0.10 | 5 (0.5) | 8 (0.8) | 3 (0.3) |
| **Total** | | **7.15** | **7.45** | **6.35** |

B wins. **Now be suspicious of it**, because this table has four well-known ways of being wrong.

## How the matrix lies

**1. The weights carry the answer.** Nudge cost from 0.25 to 0.30 and take it from energy density, and A wins. Whoever sets the weights has effectively made the decision, and weights are usually chosen with far less rigour than scores.

*Defence: sensitivity analysis.* Vary each weight ±20% and see if the ranking holds. **If the winner changes under small perturbations, your study says the options are equivalent — not that B is best.** That's a real and useful finding, and it means you should decide on something the matrix isn't capturing.

**2. Scores are ordinal, dressed as ratio.** "8" for energy density and "8" for safety are not the same kind of number, and multiplying them by weights and adding assumes they are. A 9-vs-8 gap may be 1% or 50% in reality.

*Defence:* use real units where you can, normalise explicitly, and state what each point means.

**3. It hides a disqualifier.** C scores 5 on safety. If 5 means "fails a mandatory certification", C isn't a lower-scoring option — **it's not an option**, and its 6.35 total is meaningless.

*Defence:* apply **constraints first, as a filter**, before scoring anything. Requirements are pass/fail; only preferences get scored.

**4. It launders a decision already made.** The most common real-world failure. Someone has chosen, and the matrix is built to produce that answer — usually visible in the alternatives, which are the favourite plus two obviously weak ones.

*Defence:* generate alternatives before criteria, and include one a *critic* would propose.

## Sensitivity analysis, concretely

The thing that separates a real trade study from a decorated opinion:

- **Vary the weights** — does the ranking survive?
- **Vary uncertain scores** — score C's supply risk 3 or 6; does it matter?
- **Find the break-even** — *"A wins if energy density is worth more than 34% of the decision."* That's a far more useful output than a total, because it's a statement a stakeholder can actually rule on

**Report the break-even, not just the winner.** It converts an engineering result into a decision someone can own.

## Where costs actually live

**Purchase price is rarely the number that matters.** Total cost of ownership:

```
TCO = acquisition + operating + maintenance + downtime + disposal
      − residual value
```

A cheaper component with a shorter service life and a harder replacement procedure is routinely more expensive over ten years.

**In software this is the entire "build vs buy" argument, and it's usually done badly.** The managed service costs $2,000/month and self-hosting is "free" — except the engineer-days to build it, the on-call burden, the upgrade work, the security patching, and the fact that the person who built it will leave. **Engineer time is the dominant term and the one most often excluded.**

## Recording it

**A trade study nobody can find is a trade study that gets redone.** The software-native form is an **Architecture Decision Record** — one short file per nontrivial decision:

```markdown
# ADR-012: Use PostgreSQL for the primary datastore

## Status
Accepted — 2026-08-22

## Context
Need transactional integrity, relational queries, ~10k writes/s at peak.
Team has Postgres experience; no dedicated DBA.

## Decision
PostgreSQL, managed (RDS).

## Alternatives considered
- **MongoDB** — rejected: our access patterns are relational; joins in
  application code were the failure mode last time
- **DynamoDB** — rejected: access patterns not yet stable enough to
  commit to a partition key
- **Self-hosted Postgres** — rejected: no DBA; TCO higher once on-call
  is counted

## Consequences
+ Mature tooling, team knows it, strong consistency
− Vertical scaling ceiling; sharding later would be a project
− Vendor coupling to RDS-specific operations
```

**The "alternatives considered" section is the one that pays.** In eighteen months someone will ask "why didn't we use Dynamo?" — and this answers it in ten seconds instead of a three-day re-investigation.

This is exactly the `DECISIONS.md` habit in [[foundations/software-engineering/01-what-software-engineering-is|the engineering habits]], and it's the same instinct as [[concepts/04-best-practices/03-documentation-practices|documentation practices]].

## When not to run one

**The method costs more than the decision is worth, most of the time.** Reserve it for decisions that are expensive to reverse, and use judgement for the rest.

The useful test is **reversibility**: a decision you can undo in an afternoon should be made in an afternoon. A decision that commits a supplier, a schema, a public API or a factory tool deserves the full method. Amazon's *one-way vs two-way doors* is the same idea, and the common failure is treating two-way doors as one-way — deliberating for a fortnight over something you could have tried.

## Related
- [[foundations/systems-engineering/04-architecture-and-interfaces|architecture and interfaces]] — what you're choosing between
- [[foundations/systems-engineering/08-risk-and-failure-analysis|risk and failure analysis]] — quantifying the downside
- [[concepts/04-best-practices/03-documentation-practices|documentation practices]] — ADRs
- [[architecture/01-system-design-fundamentals/README|system design]] — trade-offs as the core skill

*Source: [reference] — from the INCOSE handbook, NASA SE Handbook, and the ADR literature (Nygard).*
