# Risk and Failure Analysis

> **[Intermediate]** · FMEA, fault trees, and the systematic search for what you didn't think of.

Verification proves the system meets its requirements. **This is the separate activity that asks what happens when things go wrong in ways nobody wrote a requirement about** — and it's the part of the discipline that transfers most directly into software.

## Risk

**Risk = likelihood × consequence.** Both estimated, usually on 1–5 scales, and plotted on a matrix:

```
         │ Catastrophic  Major  Moderate  Minor
─────────┼──────────────────────────────────────
Frequent │   ███████     █████    ███       ░
Likely   │   ██████      ████     ██        ░
Possible │   █████       ███      ░         ░
Unlikely │   ███         ░        ░         ░
Rare     │   ░           ░        ░         ░
```

The four responses: **avoid** (change the design so it can't happen), **mitigate** (reduce likelihood or consequence), **transfer** (insure, or contract it out), **accept** (record it, and say so out loud).

**Accepting a risk is a legitimate decision. Accepting it silently is not** — the difference is whether anyone can be held to it later.

**The systematic error worth knowing:** people are poor at low-likelihood/high-consequence estimates. Rare events get rounded to "won't happen" — until an organisation has normalised the anomaly, which is [Diane Vaughan's](https://en.wikipedia.org/wiki/Normalization_of_deviance) reading of *Challenger*: the O-ring erosion was observed repeatedly, survived each time, and each survival made the next flight feel safer rather than less safe.

**The software version is entirely familiar:** the alert that fires every week and is always fine, the disk at 85% for months, the flaky test everyone re-runs. **Each survival is treated as evidence of safety rather than as a warning you got away with.**

## FMEA — bottom-up

**Failure Mode and Effects Analysis.** For every component, ask: how can this fail, what happens, how bad, how likely, would we detect it?

| Component | Failure mode | Effect | S | O | D | RPN |
|---|---|---|---|---|---|---|
| Temp sensor | Reads high | Overcooling, wasted energy | 4 | 3 | 2 | 24 |
| Temp sensor | **Reads low** | **Overheating, fire** | **9** | 3 | **7** | **189** |
| Temp sensor | No output | System detects, safe shutdown | 5 | 2 | 1 | 10 |

**RPN = Severity × Occurrence × Detection**, each 1–10, with detection scored *high when detection is poor*. Sort descending; work the top.

**The detection column is the one people underuse and the one that most often changes a design.** Row 2 and row 3 are the same sensor failing. Row 3 is fine — the system knows and shuts down safely. Row 2 is a fire, entirely because the failure is *silent*.

**So the cheapest fix is frequently not "make it fail less" but "make it fail loudly"** — a range check, a plausibility check against a second sensor, a heartbeat. That's the same instinct as ECC memory in [[devops/00-the-physical-layer/01-servers-and-what-makes-them-servers|servers]] and checksums in [[foundations/networking/02-the-link-layer|the link layer]]: **convert silent failure into loud failure.**

**RPN is a flawed number** — it multiplies ordinal scales, so 9×3×7 and 3×9×7 rank equally despite one being catastrophic. Use it to sort, then judge; never treat it as a threshold.

**The software FMEA is worth doing and almost nobody does it.** Take each dependency — database, cache, third-party API, queue, DNS — and ask: what if it's slow? Unavailable? Returns wrong data? Returns *stale* data? Silently succeeds but does nothing? **"Slow" is the mode most often missed**, and it's usually worse than "down", because a down dependency fails fast while a slow one exhausts your connection pool and takes the whole service with it → [[architecture/04-distributed-systems/README|distributed systems]].

## Fault Tree Analysis — top-down

FMEA starts at components. **FTA starts at the disaster and works backwards.**

```
              [ Total power loss ]
                       │
                    ── AND ──
                   │          │
        [Main supply fails] [Backup fails]
                │                  │
             ── OR ──           ── OR ──
            │        │         │        │
        [Grid]   [Breaker]  [No fuel] [Start fail]
```

**AND gates are your redundancy; OR gates are your single points of failure.**

Its distinctive value is finding **common-cause failures** — one event that defeats several branches at once. Two independent power supplies on the same circuit breaker aren't independent. Two availability zones in the same building aren't independent → [[devops/00-the-physical-layer/03-data-centres|data centres]]. Two services in different regions that both call the same auth provider aren't independent.

**Redundancy only helps against failures that are actually independent**, and the whole point of FTA is that independence is an assumption you must check rather than assert.

## Hazard analysis and safety

Where failures can hurt people, the process is formalised and legally required — DO-178C (aircraft), ISO 26262 (automotive), IEC 62304 (medical), IEC 61508 (industrial).

The concepts worth carrying regardless of domain:

**Fail-safe** — on failure, go to a state that's safe. A signal fails to red. A press retracts.

**Defence in depth** — several independent barriers, so no single failure is sufficient. James Reason's *Swiss cheese model*: every layer has holes; accidents happen when they line up.

**Safety integrity levels** — how much rigour a function requires, scaled to how bad its failure is. Not everything gets the same treatment, and pretending otherwise wastes the budget that should go to the critical parts.

**The rule that shows up everywhere:** where a hazard can be removed by design, do that instead of adding a control. A guard can be defeated; a mechanism that cannot reach the operator cannot be defeated.

## The cognitive part

Formal methods exist because informal judgement fails predictably:

- **Availability bias** — we overweight what we can easily imagine, so *novel* failures are systematically underestimated
- **Confirmation bias** — we test to confirm rather than to break
- **Normalisation of deviance** — as above
- **Groupthink** — the concern raised and not pursued. *Challenger* again

**FMEA and FTA are structured precisely so that they don't depend on someone happening to think of the right thing.** That's their real value: exhaustiveness over inspiration.

**And the same reasoning is why [[devops/12-sre-and-platform-engineering/02-site-reliability-engineering|blameless postmortems]] and [[foundations/systems-engineering/06-verification-and-validation|independent V&V]] exist.** All three are mechanisms for surfacing what the people closest to the work cannot see.

## Related
- [[foundations/systems-engineering/06-verification-and-validation|verification and validation]] — proving what you did specify
- [[devops/12-sre-and-platform-engineering/02-site-reliability-engineering|SRE]] — incident response and postmortems
- [[architecture/01-system-design-fundamentals/03-availability-and-reliability|availability and reliability]] — the numbers
- [[cybersecurity/06-attacks-and-threats/README|threat modelling]] — FMEA with an adversary

*Source: [reference] — from IEC 60812 (FMEA), IEC 61025 (FTA), the NASA SE Handbook, and Vaughan's *The Challenger Launch Decision*.*
