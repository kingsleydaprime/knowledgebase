# AI/ML Interview — AI Engineering

From [[ai-ml/03-ai-engineer/README|03-ai-engineer]].

---

### Q1. [Intermediate] 🔥 How does a transformer LLM actually generate text?

**Strong answer covers:** text → **tokens** (subword units) → embeddings + positional information → N transformer blocks, each with **self-attention** (every token attends to every previous token, weighted by learned query/key/value projections) and a feed-forward network → a distribution over the vocabulary for the *next* token → sample → append → repeat.

**The properties that follow, which is what they're really asking:**
- **It's autoregressive**, one token at a time — so generation is inherently sequential and latency scales with output length. This is why time-to-first-token and tokens-per-second are separate metrics.
- **Attention is O(n²)** in sequence length, which is why long context is expensive and why the KV cache matters so much for inference.
- **It predicts plausible continuations**, not true statements. Hallucination isn't a bug to be patched; it's what the objective function optimises for. Systems must be designed around it.

**Sampling parameters worth knowing:** temperature (flattens/sharpens the distribution), top-p/nucleus (sample from the smallest set covering p of the mass). **Temperature 0 is not deterministic in practice** for hosted models — batching and floating-point non-associativity on GPUs mean identical inputs can differ. Knowing that saves you from writing tests that flake.

---

### Q2. [Intermediate] 🔥 Explain RAG. Where does it usually fail?

**Strong answer covers:** chunk documents → embed → store in a vector database → at query time embed the query, retrieve the top-k nearest chunks, and put them in the prompt as context. It grounds answers in your data without retraining, and gives you **citations**, which is often the actual business requirement.

**Where it fails — and this is the whole question, because everyone can describe the happy path:**
- **Retrieval, not generation.** If the right chunk isn't retrieved, no model can save you. Measure retrieval quality (recall@k) *separately* from answer quality, or you'll spend weeks tuning prompts to fix a retrieval bug.
- **Chunking destroys context.** Fixed-size chunks split tables and cut sentences mid-thought. Semantic or structure-aware chunking, plus overlap, plus including the document title/heading in each chunk.
- **Pure semantic search misses exact terms** — product codes, error codes, names. **Hybrid search** (BM25 + vector, fused with reciprocal rank fusion) is close to a default for a reason.
- **No reranking.** Embedding similarity is a cheap approximation; a cross-encoder reranker over the top ~50 dramatically improves precision at top-5.
- **Nothing handles "the answer isn't in the corpus."** The model will confabulate from irrelevant chunks unless you explicitly instruct and evaluate for "I don't know."

**A strong closer:** "and I'd build the eval set before the pipeline" — question/expected-answer pairs, so every change is measured rather than vibes. This is exactly the [[project-ideas|RAG-over-this-vault]] project.

---

### Q3. [Intermediate] 🔥 When do you fine-tune instead of prompting or RAG?

**Strong answer covers the decision order — prompting → RAG → fine-tuning — and the reason for it:**

- **Prompting** for behaviour changes. Free, instant, iterable.
- **RAG** for **knowledge** the model lacks. Cheap to update — new documents, no retraining. Gives citations.
- **Fine-tuning** for **form**, not facts: a consistent output format, a specific tone, a domain's idiom, or distilling a large model's behaviour into a smaller/cheaper one.

**The point that gets this right:** **fine-tuning is a bad way to add knowledge.** It's expensive, it goes stale, you can't cite sources, and it can degrade general capability. "Fine-tune it on our docs" is the most common wrong instinct in the field, and saying so clearly is a strong signal.

**Practical detail:** **LoRA/QLoRA** make it far cheaper — train small low-rank adapters instead of all weights, so you can fine-tune a useful model on one GPU and swap adapters per task.

---

### Q4. [Intermediate→Advanced] 🔥 How do you evaluate an LLM feature?

**The most important question in this file.** It's what separates engineers from demo-builders.

**Strong answer covers:**
- **Build the eval set first**, from real or realistic inputs. Even 50 examples beats none by an enormous margin.
- **Match the method to the task:** exact match/structural validation where there's a right answer; **LLM-as-judge** for open-ended output (with a rubric, and *validated against human labels* — an unvalidated judge is just a second unmeasured model); human review for the tail.
- **Test the failure modes deliberately**, not just the happy path: adversarial inputs, out-of-scope questions, prompt injection, ambiguity.
- **Track regressions in CI.** Changing a prompt is a code change and needs the same gate.
- **Measure cost and latency alongside quality** — they're real constraints and they trade against each other.

**The framing that lands:** *"an LLM feature without an eval set isn't an engineering artefact, it's a demo. You can't improve what you can't measure, and with a probabilistic system you can't even tell whether your last change helped."*

---

### Q5. [Intermediate] What is MCP and why does it exist?

**Strong answer covers:** the **Model Context Protocol** is an open standard for connecting models to tools, data, and prompts — a client/server protocol where a server exposes **tools** (callable functions), **resources** (readable data), and **prompts** (templates), and any compliant host can use them.

**Why it exists:** it's the **N×M problem**. Without a standard, every model host needs a bespoke integration with every tool — M hosts × N tools. With one, a tool is written once and works everywhere. It's USB-C for model integrations, and the analogy is fine because it's accurate.

**Say what you've done with it** — you *use* MCP servers; building one closes the loop and is a 🟡 in [[project-ideas|project-ideas]]. → [[ai-ml/03-ai-engineer/07-tools-and-mcp|tools & MCP]]

---

### Q6. [Intermediate→Advanced] 🔥 What makes an agent different from a chatbot, and why are agents hard?

**Strong answer covers:** an agent runs a **loop** — decide, call a tool, observe the result, decide again — until a goal is met. Chatbots respond; agents act, over multiple steps, with state.

**Why they're hard, which is the real question:**
- **Errors compound.** 95% per-step reliability over 10 steps is ~60% end-to-end. Long agent trajectories are unreliable *by arithmetic*, not by poor prompting.
- **They get stuck in loops** — retrying the same failing call. Need step budgets and loop detection.
- **Failure is silent.** The agent confidently reports success it didn't achieve, which is far worse than an exception.
- **Cost and latency are unbounded** without limits.
- **Tool design dominates.** A badly-described tool is used wrongly and no amount of prompt engineering fixes it. Descriptions, parameter names, and error messages *are* the interface the model reasons over — write them for a reader, not a compiler.

**The engineering answer:** constrain the space. Fewer, better tools; explicit step limits; validate outputs structurally; checkpoint so a failure doesn't restart everything; and **human-in-the-loop for irreversible actions**. Determinism where you can afford it, model judgement only where you can't.

---

### Q7. [Advanced] 🔥 What is prompt injection and can you fully prevent it?

**Strong answer covers:** instructions and data share one channel — the context window. If the model reads attacker-controlled text (a web page, an email, a document, a tool result), that text can carry instructions the model follows.

**Direct** injection is the user attacking their own session (mostly a policy problem). **Indirect** is far more dangerous: content the *system* retrieves carries the payload, so the attacker never touches your interface. An agent with tools and an injected instruction becomes a confused deputy — it has your credentials and follows their goals.

**The honest answer: no, you cannot fully prevent it.** It's the same class as [[cybersecurity/interview/01-appsec-crypto-and-defence|SQL injection]] — data interpreted as code — but **without the fix**. SQL has parameterised queries because SQL has a grammar that separates code from data. Natural language has no such separation, so there is no equivalent. Anyone claiming a complete solution is wrong.

**So you mitigate architecturally, not by prompting:**
- **Least privilege** — the agent's tools should have the *user's* permissions and no more.
- **Human confirmation for irreversible or outbound actions** — the single most effective control.
- **Treat all model output as untrusted** — never `eval` it, never pass it unvalidated to a shell or SQL.
- **Separate privileged planning from untrusted content processing** (dual-LLM patterns).
- **Constrain outputs structurally** — a model that can only emit a value from an enum can't emit an attack.
- **Log and monitor** tool calls for anomalies.

**The framing that scores:** *"design so that a successful injection is survivable, because you can't design so it's impossible."* → [[ai-ml/03-ai-engineer/10-safety-and-production|safety & production]]

---

### Q8. [Intermediate] How do you control cost and latency in an LLM application?

**Strong answer covers:**
- **Route by difficulty.** Most requests don't need your largest model. A cheap model with a fallback to an expensive one on low confidence is often a 10× cost reduction with negligible quality loss.
- **Prompt caching** — huge wins when a long system prompt or document is reused across requests.
- **Cache responses** for repeated queries (semantic caching where exact match is too strict).
- **Stream** — time-to-first-token is what users perceive, and streaming changes the felt latency far more than a faster model.
- **Shorten output.** Generation is sequential, so output tokens dominate latency. "Be concise" is a performance optimisation.
- **Batch** offline work.
- **Set token limits** and monitor spend per feature — an unbounded agent loop is an unbounded bill.

**Detail that shows real experience:** measure **cost per successful task**, not cost per call. A cheaper model that needs three retries is more expensive, and per-call pricing hides that completely.

---

### Q9. [Intermediate] How does vector search work, and what are the tradeoffs?

**Strong answer covers:** text → embedding vector; similarity is typically **cosine similarity**. Exact nearest-neighbour search is O(n), so production systems use **ANN** indexes — **HNSW** (a navigable small-world graph; fast queries, high memory, the common default) or **IVF** (cluster and search a subset; lower memory, needs training).

**The tradeoff to name:** ANN is **approximate** — you trade recall for speed, tunable via parameters (`ef_search` in HNSW). It's a real dial with a real cost, and a lot of "RAG isn't retrieving the right thing" is an untuned recall setting.

**Practical points:** dimensionality affects memory and speed (and Matryoshka embeddings let you truncate to trade quality for cost); metadata filtering plus vector search interacts badly with ANN indexes unless the store supports it properly (pre- vs post-filtering changes results); and **pgvector is usually enough** — a dedicated vector database is often premature infrastructure when you already run Postgres. → [[databases/interview/01-sql-modelling-and-internals|databases]]

---

### Q10. [Intermediate] What would you tell a team about to put an LLM feature in front of users?

An open judgement question. **A strong answer:**

- **Decide what happens when it's wrong**, before launch — because it will be. Is the failure mode embarrassing, expensive, or dangerous? That determines how much guardrail you need.
- **Never let it take irreversible action unsupervised.**
- **Show sources** where you can. It converts "trust me" into "check me," and it's the single biggest trust lever.
- **Make it easy to report a bad answer** — that's your eval set growing itself.
- **Set expectations in the UI.** Users forgive a system that says it might be wrong; they don't forgive one that was confidently wrong.
- **Log everything** (within privacy constraints) — you cannot debug a probabilistic system from a bug report alone.
- **Have a kill switch.** A feature flag that disables the feature without a deploy.

**The one-liner:** *"treat it as an unreliable component in a reliable system, not as a reliable component."*
