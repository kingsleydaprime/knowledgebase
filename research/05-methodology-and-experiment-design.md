# Methodology & Experiment Design

**[reference]** — from *The Craft of Research*, Zobel's *Writing for Computer Science*, and standard experimental-design methodology. The engine room: designing a study whose results **actually support the claim**, with no fatal flaw a sharp reviewer — or reality — can puncture. This is where most weak papers are weak, and where a great question goes to die if you're careless.

## The kid version first

You built a new paper-airplane design and you think it flies farther. How do you find out **fairly**? Here's how *not* to: throw the new plane really hard, indoors, with no wind — and throw the old plane gently, outside, into a breeze. If the new one wins, *you learned nothing*, because you can't tell whether the **design** won or the **conditions** did.

The fair way: throw **both planes the same way, from the same spot, on the same day, many times each**, and compare the average distances. Now the *only* thing different is the design — so if the new one wins, it's the design that did it.

That's the entire secret of experiment design: **change only the one thing you're testing, keep everything else the same, and compare against something.** Everything below is "how to keep it fair when it gets complicated" — and the sneaky ways fairness quietly breaks.

## The core logic: fair comparison

An experiment tests a claim by **isolating one variable**: change the [[research/04-research-questions-and-hypotheses|independent variable]], hold the **controls** constant, measure the effect. The instant something *other* than your change also differs between conditions (a [[research/04-research-questions-and-hypotheses|confound]]), your result is ambiguous. So the discipline is: **make the conditions identical in every way except the one you're studying.** Where you can't hold something constant, **randomize** it (assign trials randomly) so it can't systematically favor one side.

## Baselines — a number without a comparison means nothing

"Our method got 85% accuracy." **Is that good?** You have no idea — 85% could be *terrible* (if a coin-flip gets 84%) or *great* (if the best prior work got 70%). A result is only meaningful **relative to a baseline.** You need two kinds:
- **Prior-work baselines** — the current best methods for this problem. Beating these is what makes you *novel and significant*.
- **Simple / sanity baselines** — the dumbest thing that could work: random guessing, always-predict-the-majority-class, a linear model, "do nothing." These catch the embarrassing case where your fancy method barely beats trivial — a shockingly common and *career-saving* check.

**Reviewers reject papers with missing or weak baselines more than almost anything else.** If you can't compare, you can't claim.

## Ablations — proving each piece earns its place

Your method has parts (a new loss + a new architecture + a new training trick). An **ablation study** removes each part one at a time and re-measures, to show *which* parts actually matter. If removing your "key innovation" barely changes the result, then it wasn't the innovation doing the work — better to find that out yourself than have a reviewer find it. Ablations are the standard evidence that your contribution is *real* and not riding on some incidental detail.

## The cheating trap (usually unconscious)

The most common way papers mislead isn't fraud — it's **unfair effort**: you lovingly tune *your* method (sweep hyperparameters, pick the best run, use the best data split) while running the **baselines at their defaults**, out of the box. Of course yours wins — you tried harder for it. This is *the* pervasive, mostly-unconscious sin of empirical research. The fixes: give every method the **same tuning budget**, the **same data and compute**, re-run baselines yourself when you can (don't just cite their best-ever number obtained under different conditions), and report *how* you tuned everything.

## Validity — the four ways a study can be wrong

A formal checklist for "is this result trustworthy?" — run your design against all four:
- **Internal validity** — did *your change* cause the effect, or a **confound**? (Controls, randomization, holding conditions equal.) *The most important one* — a broken internal validity means your central claim is unsupported.
- **External validity** — does it **generalize** beyond your exact setup? A result on one dataset, one robot, one seed may not hold elsewhere. Test on **multiple datasets/conditions**; be explicit about the scope you've actually shown.
- **Construct validity** — are you **measuring what you think**? Does your [[research/04-research-questions-and-hypotheses|metric]] actually capture the concept ("did accuracy really measure *usefulness*?").
- **Statistical-conclusion validity** — enough samples, the right test, not fooled by **noise** ([[research/06-analyzing-and-interpreting-results|analysis]]). One lucky run is not a finding.

Good papers explicitly discuss **threats to validity** — naming the ways their own study could be wrong. It reads as *strength*, not weakness.

## Sound protocol (the checklist that saves you)

- **Train / validation / test separation** — tune on validation, report on a test set touched **only once** ([[ai-ml/02-ml-engineer/02-working-with-data/03-train-val-test-splits|splits]]). This is [[research/04-research-questions-and-hypotheses|confirmatory]] discipline.
- **Avoid data leakage** — the silent killer: any way test information sneaks into training (features computed over the whole dataset, duplicate samples across splits, tuning on the test set). Leakage inflates results and evaporates in the real world — audit for it ruthlessly.
- **Repeat and report variance** — run multiple seeds/trials; report **mean ± std / error bars**, not a single number. A single run tells you nothing about whether the difference is real.
- **Enough samples (statistical power)** — too few trials and you can't distinguish a real effect from luck. Estimate how many you need *before* running.
- **Fix and record seeds, versions, configs, hardware** — so the run is repeatable.

## Reproducibility — the property that makes it science

A result no one can reproduce is an anecdote. The **reproducibility crisis** (large fractions of published results failing to replicate, across ML, psychology, and beyond) has made this a first-class concern. Your obligations:
- **Release code, data, and exact configs** (seeds, hyperparameters, environment/versions) — for ML, this is [[ai-ml/02-ml-engineer/10-mlops/01-mlops-fundamentals|MLOps]] discipline (experiment tracking, pinned dependencies).
- **Document the environment** precisely (a reader on different hardware should get the same answer).
- **Pre-register** where the field supports it (state hypothesis + analysis before collecting data) — the gold standard against unconscious fishing.

"Could a competent stranger reproduce my result from what I've published?" is the question to keep asking.

## Field-specific design notes (relevant to your fields)

- **ML / empirical** — controlled experiments, multiple datasets, proper splits, significance testing, ablations, released code.
- **Systems / engineering benchmarking** — measure **steady-state** (discard warm-up), report **percentiles** (p50/p95/p99) not just averages, control for noisy neighbors, repeat runs, state the hardware exactly.
- **Robotics / physical** — **calibrate instruments**, run many physical trials (the world is noisy), and be explicit about the **sim-to-real gap** if you validated in simulation.
- **Chips / hardware** — process/corner variation, measurement setup, and what's simulated vs fabricated-and-measured.

## Key insight

**A great question dies here if the design isn't fair — so change only the thing you're testing, hold everything else constant (or randomize it), and always compare against baselines** (both prior work *and* dumb sanity baselines — a number alone means nothing). Prove each component earns its place with **ablations**, and beware the near-universal unconscious cheat of tuning your method while baselines sit at defaults. Check all four **validities** (internal = did *your* change cause it; external = does it generalize; construct = are you measuring the right thing; statistical = is it real or noise), run a clean protocol (proper splits, **no data leakage**, repeated runs with variance reported), and make it **reproducible** — because a result no one can repeat isn't a finding, it's a story.

## Related
- [[research/04-research-questions-and-hypotheses|Research Questions & Hypotheses]] — the variables and hypothesis this tests
- [[research/06-analyzing-and-interpreting-results|Analyzing & Interpreting Results]] — turning the measurements into honest conclusions
- [[research/07-research-ethics-and-integrity|Ethics & Integrity]] — leakage, cherry-picking, and the line into misconduct
- [[ai-ml/01-data-scientist/06-experimentation-and-ab-testing|Experimentation & A/B Testing]] — controlled experiments in practice
- [[ai-ml/02-ml-engineer/04-model-evaluation/03-validation-and-tuning|Validation & Tuning]] · [[ai-ml/02-ml-engineer/02-working-with-data/03-train-val-test-splits|Train/Val/Test Splits]]
