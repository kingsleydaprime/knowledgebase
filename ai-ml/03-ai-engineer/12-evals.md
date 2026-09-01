# Evals

**Source:** Part II of the AI-engineer track, and the biggest gap the original ten notes left — evals had been *one paragraph* inside [[ai-ml/03-ai-engineer/10-safety-and-production|safety & production]]. It's actually the core skill of applied AI: the discipline that turns "seems better?" into a number. If you take one thing from this whole track into real work, it's this.

## Why LLM features can't use ordinary tests

A unit test asserts `add(2, 2) === 4`. It works because the function is **deterministic** — same input, same output, exact match. LLM output is **nondeterministic and open-ended**: the same prompt can produce different-but-equally-good answers, and "good" is often a judgment ("is this summary faithful?", "is this tone right?") that no `===` can check. So the question "did my prompt change help?" has no built-in answer. Without evals, you're tuning by vibes — you change a prompt, eyeball three outputs, and ship on a feeling. Evals replace the feeling with a measurement.

**An eval is: a set of representative inputs + a way to score each output + a number you track as you change things.** Prompts, models, retrieval, temperature — every change gets re-scored against the same set, so "better" becomes provable.

## The eval set (your golden dataset)

The dataset *is* the eval — a scoring method is worthless against unrepresentative inputs.

- **Draw from reality.** Seed it from real user queries (or realistic ones), not made-up easy cases. Production logs and support tickets are gold.
- **Cover the hard and the weird.** Include edge cases, adversarial inputs, empty/ambiguous queries, the long tail where things actually break — not just the happy path.
- **Label the expected outcome** where one exists: the correct answer, the required fields, the acceptable range. For open-ended tasks, label a *rubric* instead (see LLM-as-judge).
- **Start tiny, grow deliberately.** 20 well-chosen cases beat 500 random ones. Every time a bug reaches production, add the case that would have caught it — the eval set becomes a **regression suite** that compounds in value.
- **Freeze it.** A moving eval set can't measure progress. Version it; add cases in reviewed batches.

## Scoring methods, cheapest to most flexible

Reach for the cheapest one that fits — most tasks mix several.

| Method | How | Best for | Cost / caveat |
|---|---|---|---|
| **Exact / structural** | `===`, schema-valid, regex, "contains X" | classification, extraction, [[ai-ml/03-ai-engineer/11-structured-output\|structured output]], tool-arg correctness | free, deterministic, but only for checkable outputs |
| **Programmatic metrics** | code compiles/tests pass; JSON parses; number in range; string-similarity (BLEU/ROUGE — weak) | code-gen, data extraction, bounded numeric answers | cheap, but similarity metrics correlate poorly with quality |
| **LLM-as-judge** | a second model scores the output against a rubric | open-ended quality (summaries, chat, tone, helpfulness) | flexible and scalable, but has biases — see below |
| **Human review** | a person grades | the hardest / highest-stakes cases; calibrating the judge | the gold standard, and the bottleneck — reserve it |

**Prefer exact/structural whenever you can shape the task to allow it.** Ask for a classification label instead of a paragraph, extract fields instead of prose — you trade a little flexibility for a free, reliable, deterministic score. A huge amount of eval skill is *designing the task* so it's cheaply checkable.

## LLM-as-judge — the workhorse, and its traps

For open-ended quality you can't check with code, have a model grade the output against an explicit rubric. It scales (score thousands of outputs for cents) and correlates surprisingly well with human judgment *when done carefully*. The care is the whole game:

- **Write an explicit, gradeable rubric.** Not "is it good?" but per-criterion checks: "Does the answer cite a source for every factual claim? Is it under 150 words? Does it avoid speculation?" Vague rubrics produce noisy scores.
- **Prefer a small scale or pairwise.** Absolute 1–10 scores drift and cluster; **binary pass/fail per criterion** or **"which of A/B is better?"** are far more stable.
- **Know the biases and design around them:**
  - **Position bias** — judges favor whichever answer comes first in A/B. Fix: run both orderings and average, or randomize.
  - **Verbosity/self bias** — judges over-reward longer answers and outputs from their own model family. Fix: rubric-anchor on substance; consider a different judge model than the one under test.
  - **Leniency** — judges drift toward "pass." Fix: calibrate the judge against a human-labeled subset and check agreement.
- **Validate the judge itself.** Have a human grade a sample, measure judge-vs-human agreement, and only trust the judge on the axes where they agree. An uncalibrated judge is just another vibe with a number attached.

## Offline vs. online

- **Offline (pre-ship):** run the eval set in CI on every prompt/model/retrieval change. This is your regression gate — a change that drops the score doesn't merge. Fast feedback, controlled inputs.
- **Online (post-ship):** measure the live system — thumbs up/down, task-completion, escalation-to-human rate, downstream conversion, and sampled human review of real traffic. This catches what the offline set didn't anticipate, and the failures you find here become new offline cases. The loop: **offline gate → ship → online signal → new offline cases → tighter gate.**

## Evaluating the sub-systems

Whole-pipeline evals hide *where* a failure came from. Score the parts:
- **RAG** ([[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG & embeddings]]) splits into **retrieval** and **generation**. Retrieval metrics: did the right chunk get fetched (context precision/recall)? Generation metrics: is the answer **faithful** to the retrieved context (no facts beyond it), and does it actually **answer** the question (answer relevance)? A bad RAG answer is usually a retrieval miss wearing a generation costume — measure retrieval first.
- **Agents** ([[ai-ml/03-ai-engineer/08-agents|agents]]): score the *trajectory*, not just the final answer — did it pick the right tools, in a sane order, without looping? Plus end-to-end task success.

## Gotchas

- **Overfitting to the eval set.** If you tune relentlessly against a frozen set, you optimize for *that set*, not reality. Keep a held-out slice and refresh from production periodically.
- **A number with no baseline is noise.** Always compare against the previous version and, ideally, a trivial baseline (keyword match, "return the most common label") — if you can't beat the baseline, the LLM isn't earning its cost.
- **Small sets have wide error bars.** A jump from 82% to 85% on 20 cases may be luck. Grow the set before trusting small deltas.
- **The judge is a model, so it drifts too.** Re-validate judge-vs-human agreement when you change the judge model.

## Key insight

**You can't ship what you can't measure, and LLM quality is invisible without an eval set.** The craft is: build a small, realistic, versioned dataset; score with the cheapest method the task allows (shape tasks to be checkable); use a carefully-rubriced, bias-corrected LLM judge for the open-ended rest; gate changes offline and mine production online for new cases. This is the AI-engineering equivalent of a [[languages/01-java/03-tooling/04-testing|test suite]] — and the thing that most separates a demo from a product.

## Related
- [[ai-ml/03-ai-engineer/10-safety-and-production|Safety & Production]] — evals are one pillar of shipping safely
- [[ai-ml/03-ai-engineer/05-prompt-engineering|Prompt Engineering]] — evals are how you know a prompt change helped
- [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG & Embeddings]] — retrieval vs. generation metrics
- [[ai-ml/03-ai-engineer/11-structured-output|Structured Output]] — structural checks are the cheapest eval
- [[ai-ml/02-ml-engineer/04-model-evaluation/01-evaluation-metrics|ML Evaluation Metrics]] — the classical-ML sibling of this discipline
