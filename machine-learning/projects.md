# Machine Learning — Projects

_Training models and running them in production. You need a dataset and patience._

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

## Projects

_The modeling half — needs a dataset and patience. Kaggle is the fastest source of real data._

- 🟢 **Tabular ML done right** — take a Kaggle tabular dataset, do [[data-science/04-exploratory-data-analysis|EDA]], train [[machine-learning/03-classical-ml/10-decision-trees-6|gradient boosting]] vs [[machine-learning/03-classical-ml/14-linear-models-and-regression|logistic regression]], with proper [[machine-learning/04-model-evaluation/05-validation-and-tuning|cross-validation + tuning]]. Prove the boosting-beats-deep-learning-on-tabular point yourself.
- 🟢 **Implement it from scratch in NumPy** — write linear regression (gradient descent) and k-means using _only_ [[machine-learning/00-foundations/04-python-and-data-tools/02-numpy|NumPy]], no scikit-learn. The fastest way to make [[machine-learning/00-foundations/03-mathematics/index|the math]] and vectorization click.
- 🟡 **Image classifier with transfer learning** — fine-tune a pretrained CNN ([[machine-learning/06-computer-vision/03-transfer-learning|transfer learning]]) on a custom image set. Small, satisfying, and teaches the [[machine-learning/05-deep-learning/02-training-loop-in-pytorch|PyTorch loop]].
- 🟡 **Fine-tune a small open model** — LoRA-fine-tune a small model from [[ai-engineering/03-the-model-landscape|Hugging Face]] on a narrow task, and honestly compare it to just prompting a bigger model (the [[ai-engineering/06-rag-and-embeddings/index|RAG vs fine-tuning]] decision, tested).
- 🔴 ⭐ **End-to-end MLOps project** — train a model, track experiments with [[machine-learning/10-mlops/02-experiment-tracking-and-pipelines|MLflow]], [[machine-learning/10-mlops/04-serving-and-monitoring|serve it]] behind a FastAPI endpoint in a container, and add [[machine-learning/10-mlops/03-monitoring-and-edge|drift monitoring]]. This is the whole _engineer_ half of ML engineering, and it reuses your DevOps skills.

## The foundation rep

- 🔴 ⭐ **Build your own neural network** — the guide: [[build-your-own-shit/10-your-own-neural-network|10-your-own-neural-network]]. Forward pass → loss → **backprop by hand** → gradient checking → a tiny autodiff engine. **Done when:** `loss.backward()` stops being magic.

## Related

- [[machine-learning/index|Machine Learning]] · [[machine-learning/interview/index|interview bank]]
- [[data-science/projects|Data Science projects]] · [[ai-engineering/projects|AI Engineering projects]]
- [[project-ideas|Project Ideas]] — the vault-wide index
