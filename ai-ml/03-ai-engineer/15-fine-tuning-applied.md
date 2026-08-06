# Fine-Tuning (Applied)

**Source:** Part II of the AI-engineer track. [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG & embeddings]] covered *when* to fine-tune vs. retrieve; this note is the applied *how* — from the perspective of someone building on pre-trained models, not training from scratch. The deep mechanics (backprop, the training loop, RLHF) live in the ML-engineer track's [[ai-ml/02-ml-engineer/09-building-and-fine-tuning/03-fine-tuning|fine-tuning note]]; this is the API-side, decision-and-recipe view.

## First: are you sure you need it?

Fine-tuning is the tool most reached for and least often correct. Before you touch it, exhaust the cheaper levers, because they solve most problems fine-tuning is blamed for:
1. **Better prompting + few-shot examples** ([[ai-ml/03-ai-engineer/05-prompt-engineering|prompt engineering]]) — often closes the gap alone.
2. **RAG** — if the problem is "the model doesn't *know* our facts," that's a knowledge gap, and retrieval fixes it instantly and updatably. Fine-tuning is a bad and expensive way to inject knowledge.
3. **A more capable model** — sometimes the fix is just a bigger base model, no training at all.

**The dividing line:** RAG (and prompting) add **knowledge**; fine-tuning changes **behavior** — consistent tone/format/style, a narrow specialized skill, or reliably following a house convention that no prompt seems to pin down. If you can express the requirement as "know this," don't fine-tune. If it's "*behave* like this, every time, without a paragraph of instructions," fine-tuning earns its place.

Concrete cases where it's the right call: locking a rigid output format or persona, a high-volume narrow task where a fine-tuned **small** model matches a prompted **large** one at a fraction of the cost/latency, teaching a domain style (legal, medical, brand voice), or distilling a big model's behavior into a cheap one.

## What "fine-tuning" means at the applied layer

You take an already-trained base model and continue training it a little on **your** examples, nudging its weights toward your task. Two things make this practical without a GPU cluster:

- **You rarely update all the weights.** **Parameter-efficient fine-tuning (PEFT)**, most commonly **LoRA** (Low-Rank Adaptation), freezes the giant base model and trains a tiny set of small "adapter" matrices bolted onto it. You end up training well under 1% of the parameters — cheap, fast, and you can keep many small adapters for one base model. This is what "fine-tuning" almost always means in practice today.
- **Hosted providers hide even that.** The closed-API path is: upload a dataset of examples → the provider runs the training → you call a new model ID. No infrastructure, no PEFT knobs — you supply data and get an endpoint. Open-weight models ([[ai-ml/03-ai-engineer/16-local-and-open-models|local & open models]]) let you run LoRA yourself for more control and no per-token markup.

### Two flavors, by what your data looks like
- **Supervised fine-tuning (SFT)** — the common one. Your dataset is `(input, ideal_output)` pairs; the model learns to produce the ideal output. This is how you teach format, tone, and narrow tasks.
- **Preference tuning (DPO / RLHF-family)** — your data is *comparisons* (`output A is better than output B`) rather than single gold answers, used to align the model toward preferred behavior. **DPO** (Direct Preference Optimization) is the simpler, now-common way to do this without the full reinforcement-learning machinery of classic RLHF. Reach for it when "better" is a judgment you can only express by ranking, not by writing one perfect answer.

## The recipe (hosted path)

1. **Build the dataset.** This *is* the project — quality and consistency matter far more than volume. A few hundred *clean, consistent* examples usually beat thousands of noisy ones. Every example must model exactly the behavior you want; one inconsistent label teaches the model to be inconsistent.
2. **Split off a held-out eval set** *before* training. You need [[ai-ml/03-ai-engineer/12-evals|evals]] to answer "did it actually get better?" — and to catch overfitting.
3. **Train** — upload, kick off the job, keep it a small nudge (few epochs). Over-training makes the model **overfit**: brilliant on your examples, brittle and forgetful on everything else (it can even lose general capability — "catastrophic forgetting").
4. **Evaluate against the base model** on the held-out set *and* on a general set. If the fine-tune doesn't clearly beat well-prompted base on your task — or if it regressed on general ability — it wasn't worth it.
5. **Iterate on the data, not the hyperparameters.** At this layer, almost every quality gain comes from cleaning, balancing, and expanding the dataset — not from knob-twiddling.

## The honest cost/benefit

- **Upfront cost:** curating a good dataset (real work), the training run, and an eval harness.
- **Ongoing cost:** fine-tuned models are a **frozen snapshot** — to teach new facts or behavior you retrain. Knowledge that changes weekly should be RAG, not a fine-tune you re-bake constantly.
- **The payoff, when it fits:** a smaller, cheaper, faster model that *reliably* does your narrow task, with a short prompt instead of a giant one — lower per-call cost and latency ([[ai-ml/03-ai-engineer/14-cost-caching-and-latency|cost, caching & latency]]) at scale.

You can also **combine** RAG and fine-tuning: fine-tune for *how to behave* (format, tone, how to use retrieved context) and use RAG for *what to know*. That's often the strongest setup for a specialized production assistant.

## Gotchas

- **Fine-tuning to inject facts.** The classic mistake — expensive, doesn't update, and the model still hallucinates around the edges. Use RAG for knowledge.
- **Overfitting on a tiny or repetitive set.** Great on your examples, worse in the wild. Train lightly, hold out an eval set, watch for regressions on general tasks.
- **Dirty data.** The model faithfully learns your inconsistencies. Garbage examples → a garbage fine-tune; data cleaning is most of the work.
- **No baseline comparison.** If you never measured well-prompted base on the same eval set, you can't claim the fine-tune helped.
- **A frozen model drifts from reality.** Anything time-sensitive baked into weights goes stale silently. Prefer RAG for the moving parts.

## Key insight

**Fine-tuning changes *behavior*; RAG and prompting supply *knowledge* — reach for a fine-tune only after the cheaper levers are exhausted, and only when you need consistent style/format/skill that no prompt reliably pins down.** In practice it's PEFT/LoRA on a hosted or open model, and the whole game is a small, clean, consistent dataset plus an [[ai-ml/03-ai-engineer/12-evals|eval set]] that proves it beat well-prompted base without regressing. The strongest specialized systems often fine-tune for behavior *and* retrieve for knowledge.

## Related
- [[ai-ml/02-ml-engineer/09-building-and-fine-tuning/03-fine-tuning|ML Engineer: Fine-Tuning]] — the deep mechanics (loss, epochs, RLHF, transfer learning)
- [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG & Embeddings]] — the RAG-vs-fine-tuning decision in full
- [[ai-ml/03-ai-engineer/16-local-and-open-models|Local & Open Models]] — running your own LoRA on open weights
- [[ai-ml/03-ai-engineer/12-evals|Evals]] — how you prove the fine-tune was worth it
