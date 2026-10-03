# The AI engineer role

> **[Beginner]** · What an AI engineer does, how it differs from an ML engineer, and the decision every AI feature starts with: whether to use a model at all, and if so which kind. The worked example runs four features from this course through the decision, step by step. It's the frame for the rest of SWE 102, so it's short, and its practice task is about your own flagship.

## Before you start

You can already:

- Build and test an ordinary web feature, end to end.
- Explain in a sentence what a trained model is → [[ai-ml/00-foundations/02-what-is-a-model|what a model is]].

After this lesson you will be able to:

1. Say what an AI engineer builds, and how that differs from what an ML engineer builds.
2. Take a feature idea through the four-step decision: does it need a model, what kind, how capable, and hosted or self-run.
3. Name the cheaper option a model has to beat, before building with one.

**Study route.** Read it straight through, then do the practice task on your own flagship. It takes about half an hour.

## The kid version

Imagine you need a cake for a party. You could become a baker: buy ovens, learn recipes, practise for years. Or you could buy a very good cake from a shop and spend your effort on the party: the decorations, the candles, making sure it arrives on time and nobody's allergic. An ML engineer is the baker. An AI engineer buys the cake, which is a model someone else trained, and builds the party around it. And sometimes the right answer is that the party doesn't need a cake at all; biscuits would do.

**Where the analogy stops working.** A shop cake is the same every time. A model can give a different answer to the same question, and is sometimes confidently wrong, so most of the AI engineer's work is building around a cake that occasionally isn't what the box says.

## 1. Why this exists

Until recently, getting a program to read a support ticket and decide what it was about meant collecting thousands of labelled tickets, training a model and running it on your own servers. Today you send the ticket to an API and get a good answer back in a second. The hard part moved: from **building the model** to **building dependably around a model you don't control**, one that is non-deterministic, sometimes wrong and priced per token. That's a different discipline, and it's the one this course teaches.

## Terms used in this lesson

1. **Pre-trained model**: This is a model someone else has already trained on large amounts of data, which you use as it is, through an API or by downloading it.
2. **AI engineer**: This is someone who builds products and features on top of pre-trained models, mostly language models. The work is prompting, retrieval, tools, agents, evals, cost and safety: software engineering with a model as one component.
3. **ML engineer**: The letters stand for machine learning. This is someone who trains models, from data, and runs them in production. The work needs more statistics and maths, and different tooling.
4. **Baseline**: This is the simplest approach a model has to beat to be worth its cost, such as a few keyword rules ([[ai-ml/03-ai-engineer/12-evals/index|evals]]).
5. **Hosted model**: This is a model you reach through a provider's API. A **self-hosted** or **local** model runs on hardware you control.

## 2. AI engineer and ML engineer

| | ML engineer | AI engineer |
|---|---|---|
| Works with | models they train | pre-trained models, usually someone else's |
| Core skills | statistics, training, data pipelines, MLOps | prompting, retrieval, tools, agents, evals, product |
| The question | "how do I train a model that works?" | "how do I build a dependable product with existing models?" |
| Maths | a lot | enough to understand what the model does, not to derive it |

A chatbot, a search over your documents, an agent, or a language-model feature inside an app is AI engineering. Training a fraud model on transaction data, or fine-tuning a vision network for a factory line, is ML engineering. The line blurs at the edges (an AI engineer may fine-tune a small model; see [[ai-ml/03-ai-engineer/15-fine-tuning-applied|fine-tuning applied]]), but the default tools and the default question differ.

## 3. The decision every feature starts with

The most common mistake is reaching for the biggest model by default. Before building, take the feature through four questions, in order.

**Step 1 — does it need a model at all?** If the logic is well understood and doesn't vary, a hand-written rule beats any model: it's instant, free, predictable and easy to debug. Use a model when the pattern is too varied or fuzzy to write down. And write the rule anyway, as the **baseline**: in the evals lesson, eight lines of keyword rules scored 75% on the ticket set, which is the number a model has to beat to earn its cost.

**Step 2 — what kind of model?** The shape of the input and output narrows it quickly:

| Input → output | Reach for |
|---|---|
| rows of structured data → a number or a category | classic ML, such as gradient-boosted trees: an ML-engineer job |
| free text → text, a label or extracted fields | a language model |
| "find things similar to this" | an [[ai-ml/03-ai-engineer/06-rag-and-embeddings/index\|embedding model]] |
| image → description or label | a vision or multimodal model ([[ai-ml/03-ai-engineer/09-multimodal/index\|multimodal]]) |
| text → a new image or audio | a generation model |

**Step 3 — how much capability?** For a language task:

- **Narrow and high-volume** (classify, extract a field): a small, cheap model, or the rules from step 1.
- **Complex, ambiguous, multi-step reasoning**: a larger model earns its cost.
- **Needs to act, not just answer**: that's a question about tools and a loop ([[ai-ml/03-ai-engineer/08-agents/index|agents]]), not about a bigger model.
- **Needs to be current, or cite sources**: retrieval matters more than model size.

**Step 4 — hosted or self-run?** A hosted API is the usual default: the best models, no hardware. Run a model yourself when the data mustn't leave, when you must work offline, when volume makes per-token pricing dominate, or when you need to fine-tune on private data ([[ai-ml/03-ai-engineer/03-the-model-landscape|the model landscape]] and [[ai-ml/03-ai-engineer/16-local-and-open-models/index|local and open models]]).

## Worked example — four features through the decision

**1. Route support tickets to a team.**
Step 1: keyword rules get 75% on the golden set; good, but they miss tickets with no keywords and in other languages. A model is worth trying, against that baseline. Step 2: text in, one label out: a language model. Step 3: narrow and high-volume, so a small model, with a closed set of labels. Step 4: hosted, unless tickets contain data that mustn't leave; then a local model, at the cost of speed (see the landscape lesson). **Decision:** a small model, beating 75%, with the rules kept as the fallback ([[ai-ml/03-ai-engineer/13-reliability-and-plumbing/index|reliability and plumbing]]).

**2. Refund a customer when they ask.**
Step 1: whether a refund is allowed is a business rule — the order exists, isn't already refunded, the amount is within the total. That's code, not a model. The model's job, if any, is understanding the request and phrasing the reply. **Decision:** a fixed workflow where code decides and a person approves the payment; the model only writes the sentence ([[ai-ml/03-ai-engineer/08-agents/index|agents]]).

**3. Answer questions from the help centre.**
Step 1: the questions vary too much for rules. Step 2: "find the relevant articles" is an embedding search; "answer from them" is a language model. Step 3: must be grounded and cite sources, so retrieval matters more than size. **Decision:** retrieval plus a mid-sized model, with citations ([[ai-ml/03-ai-engineer/06-rag-and-embeddings/index|RAG]]).

**4. Predict which customers will cancel next month.**
Step 2: the input is rows of account data, the output a probability. That's a classic ML problem; a language model is the wrong tool, slower, costlier and worse on tabular data. **Decision:** hand it to ML engineering, or start with a gradient-boosted tree.

Notice that only one of the four ended with "use a big language model for the whole thing", and even that one needed retrieval to be trustworthy.

## Common pitfalls

1. **The biggest model by default.** Start from the cheapest option that could work, and move up only when the evals say so.
2. **No baseline.** Without the rules' score, "the model gets 80%" means nothing.
3. **A language model on tabular data.** Rows and columns are classic ML's home ground.
4. **An agent where a workflow would do.** If the steps are known, write them in code.
5. **Letting the model make business decisions.** Whether a refund is allowed is a rule, not a judgement.

## Check your understanding

1. What does an AI engineer build, and what question does an ML engineer start from instead?
2. Why write the keyword rules even when you're sure you'll use a model?
3. A feature must answer "what's our refund policy for annual plans?" from your help pages. Which steps of the decision matter most, and what do you build?
4. A team wants a language model to decide whether each refund is allowed. What would you suggest instead?
5. When would you run a model yourself instead of calling a hosted API?

<details>
<summary>Answers — after your attempt</summary>

1. Products and features on top of pre-trained models, with the engineering around them: prompts, retrieval, tools, evals, cost, safety. An ML engineer starts from "how do I train a model that works on this data?"
2. It's the baseline. Its score is what the model must beat to justify its cost and latency, and it doubles as the fallback when the model fails.
3. Step 3: it must be grounded in your pages and cite them, so retrieval matters more than model size. Build retrieval over the help pages plus a model that answers only from what was retrieved.
4. Write the rule in code — the order exists, isn't already refunded, the amount is within the total — and have a person approve the payment. The model can understand the request and write the reply, but not make the decision.
5. When the data mustn't leave your control, when you must work offline, when volume makes per-token pricing dominate, or when you need to fine-tune on private data.

</details>

## Practice — independent task

**Take your flagship through the decision.**

1. List the two or three places your flagship could use AI.
2. For each, write the four steps in one or two sentences each, as in the worked example, and end with a decision.
3. For the one you'll build, write the baseline you'll measure against: rules, a lookup, or "do nothing".

**Done when:** each candidate has a written decision with a reason at every step, and the feature you'll build has a named baseline. Keep it; it's the first section of week 6's write-up.

## Before moving on

You can say what an AI engineer does, take a feature through the four-step decision, and name the baseline it must beat.

**Recap.** An AI engineer builds dependable products around pre-trained models; an ML engineer trains them. For every feature: does it need a model (write the rule as the baseline either way), what kind, how capable, and hosted or self-run. Most features end up needing less model than you'd first think, and some need none.

**Next.** [[ai-ml/03-ai-engineer/02-how-llms-work/index|How LLMs work]] — what's actually inside the model you're building around.

## Related
- [[ai-ml/00-foundations/01-what-is-ai|What is AI]] — where AI, ML and deep learning sit
- [[ai-ml/02-ml-engineer/index|ML engineer path]] — the "train the model" sibling
- [[ai-ml/03-ai-engineer/03-the-model-landscape|The model landscape]] — the options step 2 and step 4 choose between
- [[ai-ml/03-ai-engineer/index|AI engineer track map]]

*Source: folds in the old "choosing the right AI tool" note; the AI-versus-ML distinction follows the roadmap.sh AI-engineer roadmap.*
