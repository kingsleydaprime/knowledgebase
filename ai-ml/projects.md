# AI & ML — Projects

*Three career paths over a shared foundation, so three ladders. **Pick the path first** — the AI-engineer projects need no maths and ship fast; the ML-engineer and data-scientist ones need a dataset and patience.*

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

## AI Engineer
*Your strongest applied area (AI SDK / MCP). These produce shippable, demoable products — high portfolio value.*

- 🟢 ⭐ **RAG over this vault** — a chatbot that answers questions about *this knowledgebase*: chunk the markdown, embed it, store in [[ai-ml/03-ai-engineer/06-rag-and-embeddings|pgvector/Chroma]], retrieve + answer with citations. Dogfoods your own notes and is a perfect [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG]] project.
- 🟡 **Build an MCP server** — wrap a real system (your notes, a database, an API) as an [[ai-ml/03-ai-engineer/07-tools-and-mcp|MCP server]] with tools + resources, and use it from an MCP host. You already *use* MCP — building one closes the loop.
- 🟡 **An agent with real tools + an eval set** — an [[ai-ml/03-ai-engineer/08-agents|agent]] (via the AI SDK's agent loop) that does a multi-step task with 2–3 tools, plus an [[ai-ml/03-ai-engineer/10-safety-and-production|eval set]] measuring success rate as you change the prompt/model. The evals are what make it engineering, not a demo.
- 🟡 **Structured extraction pipeline** — feed scanned docs/receipts to a [[ai-ml/03-ai-engineer/09-multimodal|vision model]], extract typed JSON with [[ai-ml/03-ai-engineer/04-calling-models|structured output]], validate against a schema. A genuinely useful, sellable tool.
- 🟢 **Model bake-off via OpenRouter** — same prompt/eval set across 5 models through [[ai-ml/03-ai-engineer/03-the-model-landscape|OpenRouter]], compare quality/latency/cost. Cheap, fast, and teaches model selection.
- 🔴 **Prompt-injection red-team** — build a small agent, then try to break it (direct + indirect [[ai-ml/03-ai-engineer/10-safety-and-production|injection]]); document what worked and the mitigations. Rare, valuable security-adjacent signal.


## ML Engineer
*The modeling half — needs a dataset and patience. Kaggle is the fastest source of real data.*

- 🟢 **Tabular ML done right** — take a Kaggle tabular dataset, do [[ai-ml/01-data-scientist/04-exploratory-data-analysis|EDA]], train [[ai-ml/02-ml-engineer/03-classical-ml/02-trees-and-ensembles|gradient boosting]] vs [[ai-ml/02-ml-engineer/03-classical-ml/01-regression|logistic regression]], with proper [[ai-ml/02-ml-engineer/04-model-evaluation/03-validation-and-tuning|cross-validation + tuning]]. Prove the boosting-beats-deep-learning-on-tabular point yourself.
- 🟢 **Implement it from scratch in NumPy** — write linear regression (gradient descent) and k-means using *only* [[ai-ml/00-foundations/04-python-and-data-tools/02-numpy|NumPy]], no scikit-learn. The fastest way to make [[ai-ml/00-foundations/03-mathematics/README|the math]] and vectorization click.
- 🟡 **Image classifier with transfer learning** — fine-tune a pretrained CNN ([[ai-ml/02-ml-engineer/06-computer-vision/03-transfer-learning|transfer learning]]) on a custom image set. Small, satisfying, and teaches the [[ai-ml/02-ml-engineer/05-deep-learning/02-training-loop-in-pytorch|PyTorch loop]].
- 🟡 **Fine-tune a small open model** — LoRA-fine-tune a small model from [[ai-ml/03-ai-engineer/03-the-model-landscape|Hugging Face]] on a narrow task, and honestly compare it to just prompting a bigger model (the [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG vs fine-tuning]] decision, tested).
- 🔴 ⭐ **End-to-end MLOps project** — train a model, track experiments with [[ai-ml/02-ml-engineer/10-mlops/02-experiment-tracking-and-pipelines|MLflow]], [[ai-ml/02-ml-engineer/10-mlops/04-serving-and-monitoring|serve it]] behind a FastAPI endpoint in a container, and add [[ai-ml/02-ml-engineer/10-mlops/03-monitoring-and-edge|drift monitoring]]. This is the whole *engineer* half of ML engineering, and it reuses your DevOps skills.


## Data Scientist
*The analysis/inference half — the deliverable is a trustworthy answer, well communicated.*

- 🟢 **A real EDA + statistical report** — take a dataset you care about, do a full [[ai-ml/01-data-scientist/04-exploratory-data-analysis|EDA]], compute [[ai-ml/01-data-scientist/02-descriptive-statistics|descriptive stats]], and write up findings with honest [[ai-ml/01-data-scientist/05-data-visualization|visualizations]]. Practice the "numbers + a picture + a takeaway" discipline.
- 🟡 ⭐ **A/B test analysis, done rigorously** — take (or simulate) experiment data and analyze it properly: [[ai-ml/01-data-scientist/03-inferential-statistics|hypothesis test]], effect size *and* confidence interval, check for the [[ai-ml/01-data-scientist/06-experimentation-and-ab-testing|pitfalls]] (SRM, peeking, Simpson's paradox). The core data-scientist skill.
- 🟡 **Causal case study** — pick a question where correlation ≠ causation and attempt a [[ai-ml/01-data-scientist/07-causal-inference-and-econometrics|difference-in-differences or regression-discontinuity]] analysis, stating your assumptions honestly. Rare, high-value reasoning.
- 🟢 **Power analysis calculator** — a small tool that computes required sample size for an A/B test given a minimum detectable effect. Cements [[ai-ml/01-data-scientist/03-inferential-statistics|power/significance]].
- 🟡 **A stakeholder dashboard** — turn an analysis into a clean, honest dashboard (a BI tool or a notebook), tuned for a decision-maker, not a data person. Communication reps.


## The foundation rep, whichever path

- 🔴 ⭐ **Build your own neural network** — the guide: [[build-your-own-shit/10-your-own-neural-network|10-your-own-neural-network]]. Forward pass → loss → **backprop by hand** → gradient checking → a tiny autodiff engine. **Done when:** `loss.backward()` stops being magic. This is the guide [[ai-ml/README|ai-ml's]] ~98 notes never had.


## If you only do one

**RAG over this vault.** It dogfoods your own notes, it's the single most transferable AI-engineering pattern, and the retrieval quality problem it exposes is the real lesson.


## Related

- [[ai-ml/README|the ai-ml curriculum map]] · [[ai-ml/interview/README|interview bank]]
- [[ai-ml/03-ai-engineer/19-practice-exercises|AI engineer exercises]]
- [[project-ideas|Project Ideas]] — the vault-wide index
