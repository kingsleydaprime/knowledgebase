# Research Questions & Hypotheses

**[reference]** — from *The Craft of Research* and standard scientific-method guidance. The hinge between "an area I'm curious about" and "an experiment I can actually run." [[research/03-finding-a-problem-and-literature-review|Finding a problem]] got you a candidate gap; this note sharpens it into something **precise and testable**.

## The kid version first

"I want to know about drones" is a **wish**, not a question you can answer. You can't tell when you're *done*, and you don't know what to *measure*. Research needs you to grind the fuzzy wish down to a **sharp question you could actually check** — like turning *"are dogs smart?"* into *"can my dog learn to sit in fewer tries than my cat?"*

Look what the sharp version gives you for free:
- **What to measure** — number of tries to learn "sit."
- **What to change** — dog vs cat.
- **When you're done** — when you've counted the tries for both.
- **A clear answer** — either the dog took fewer tries, or it didn't.

The whole job of this note is that grind: **fuzzy topic → sharp question → (often) a hypothesis you could prove wrong.** Get this right and the experiment designs *itself*; get it wrong and no amount of clever work saves you, because you never defined what "answering it" means.

## The funnel: topic → question → hypothesis

- **Topic** — a broad area ("drone landing," "LLM reasoning"). Too big to answer; it's a *direction*, not a target.
- **Question** — a specific, answerable thing about that topic ("does controller X reduce landing error vs standard PID in wind?").
- **Hypothesis** — a *predicted answer* you can test and that could turn out false ("controller X reduces landing error by ≥20% at wind >5 m/s").

Not every project needs the third step (see exploratory research below), but every project needs the second. Beginners stall at the topic stage and call it a research plan.

## Operationalizing — turning fuzzy words into measurements

The critical move, and the one people skip: **every vague concept in your question must become something you can actually measure.** A concept you can't measure isn't a research question yet.

| Vague word | Operationalized as… |
|---|---|
| "better" | +X% accuracy on dataset D / −Y ms p95 latency |
| "robust" | performance degradation under noise level N |
| "efficient" | energy per operation / FLOPs / cost per 1k requests |
| "learns faster" | epochs (or samples) to reach threshold accuracy |

This is called defining your **metric**, and it's a *choice with consequences* — "better" measured by accuracy vs. by latency can give opposite answers. Pick the metric that actually reflects what you care about, name it explicitly, and justify it. A huge fraction of weak papers are weak because "better" was never pinned to a number.

## Variables — name the four kinds

Any experiment is really "change one thing, measure another, hold the rest still." The vocabulary:
- **Independent variable** — what *you deliberately change* (the controller: X vs PID). The cause you're probing.
- **Dependent variable** — what *you measure* (landing error). The effect.
- **Controlled variables** — what you *hold constant* so they can't interfere (same drone, same payload, same test area).
- **Confounding variables** — the sneaky ones: something that varies *along with* your independent variable and could be the *real* cause of the effect. (If you tested controller X only on calm days and PID only on windy days, "weather" is a confound — you can't tell if X won or the weather did.) **Hunting confounds is the heart of valid [[research/05-methodology-and-experiment-design|experiment design]].**

## Hypotheses & falsifiability

A real hypothesis makes a **risky, specific prediction that could turn out false.** This is Popper's **falsifiability**: a claim is scientific only if there's some result that would *disprove* it. "Our method works well" is unfalsifiable fluff (what result would count as *not* working?). "Our method achieves ≥90% accuracy on benchmark B" is falsifiable — run it and find out.

The formal framing (used with statistics — [[research/06-analyzing-and-interpreting-results|analysis]]):
- **Null hypothesis (H₀)** — the boring default: "no effect / no difference" (controller X is *no better* than PID).
- **Alternative hypothesis (H₁)** — what you suspect: "there is an effect" (X *is* better).
- You design the study to see whether the evidence lets you **reject the null**. You never "prove" H₁ — you show the null is implausible given the data. (Subtle but important: absence of evidence isn't proof of no effect.)

## Three flavors of question (increasingly demanding)

The *kind* of question sets how hard the design must be:
- **Descriptive** — "what / how much / how often?" (What's the average landing error of PID in wind?) Easiest — just measure carefully.
- **Relational / comparative** — "does A relate to / differ from B?" (Does X differ from PID?) Needs a fair comparison + statistics.
- **Causal** — "does A *cause* B?" (Does switching to X *cause* lower error?) **The hardest by far** — correlation isn't causation, and establishing cause demands controlled experiments or careful [[ai-ml/01-data-scientist/07-causal-inference-and-econometrics|causal-inference]] methods to rule out confounds. Be honest about whether your design supports a causal claim or only a correlational one; over-claiming causation from correlation is the classic sin.

## When you *don't* have a hypothesis (and that's fine)

Not all good research is hypothesis-testing:
- **Exploratory research** — you're mapping unknown territory ("what happens if we scale this up? what patterns are in this data?"). The output is *new questions/hypotheses*, not a confirmed one. Legitimate — but don't dress it up as confirmatory afterward ([[research/06-analyzing-and-interpreting-results|HARKing]] — inventing the hypothesis *after* seeing the results — is a real integrity problem).
- **Systems / engineering research** — the question is often "*can* we build a system that does X, and how well?" The hypothesis is implicit ("this design achieves the goal"); the evaluation is the proof.

The honesty move: **know and state whether you're doing confirmatory (testing a pre-stated hypothesis) or exploratory (discovering) work.** Pre-registration — publicly stating your hypothesis and analysis *before* collecting data — is the strongest way to keep the two honest, increasingly expected in empirical fields.

## A good research question, checklist

- **Specific** — one clear thing, not a bundle.
- **Measurable** — every key term operationalized into a metric.
- **Answerable in scope** — finishable with your time/resources ([[research/03-finding-a-problem-and-literature-review|FINER feasibility]]).
- **Connected to the gap** — answering it fills the hole your [[research/03-finding-a-problem-and-literature-review|literature review]] found.
- **Honest about type** — descriptive/relational/causal, confirmatory/exploratory.

## Key insight

**A fuzzy topic can't be researched — you must grind it into a sharp, measurable question, and (for confirmatory work) a falsifiable hypothesis that some result could prove wrong.** The core skill is **operationalizing**: turning vague words like "better" and "robust" into named metrics, then framing the study as "change the *independent* variable, measure the *dependent* one, hold controls constant, and hunt the *confounds* that could fool you." Match the design's rigor to the question type (descriptive < relational < **causal**, the hardest), and stay honest about whether you're *confirming* a pre-stated hypothesis or *exploring* — pre-registration is what keeps that line clean.

## Related
- [[research/03-finding-a-problem-and-literature-review|Finding a Problem]] — where the question comes from
- [[research/05-methodology-and-experiment-design|Methodology & Experiment Design]] — how you answer it soundly
- [[research/06-analyzing-and-interpreting-results|Analyzing & Interpreting Results]] — H₀/H₁ and honest conclusions
- [[ai-ml/01-data-scientist/06-experimentation-and-ab-testing|Experimentation & A/B Testing]] — variables & hypotheses in practice
- [[ai-ml/01-data-scientist/07-causal-inference-and-econometrics|Causal Inference]] — when the question is causal
