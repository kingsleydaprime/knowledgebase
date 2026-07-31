# 02 — ML Engineer

The ML Engineer **builds, trains, and ships models as production software**. roadmap.sh splits this role's body of knowledge across two roadmaps, and this track covers both — they're genuinely different disciplines under one role:

- **ML / modeling** ([`machine-learning`](https://roadmap.sh/machine-learning)) — the models themselves: the algorithm zoo, deep learning, evaluation. Sections 01–09.
- **MLOps / operations** ([`mlops`](https://roadmap.sh/mlops)) — running models in production: deployment, monitoring, pipelines, retraining. Essentially "DevOps for ML." Section 10.

Contrast the siblings: the [[ai-ml/01-data-scientist/README|Data Scientist]] uses models to *find answers* (and may touch neither production nor operations); the [[ai-ml/03-ai-engineer/README|AI Engineer]] builds on *pre-trained* models without training their own. The ML Engineer owns the model **and** ships it. Part of the [[ai-ml/README|AI/ML course]].

## Reading order

**Modeling half:**

1. [[ai-ml/02-ml-engineer/01-foundations-of-ml/README|01-foundations-of-ml/]] — **[Beginner]** — what ML is, the types of learning (supervised/unsupervised/RL), and the Python/scikit-learn/PyTorch toolkit
2. [[ai-ml/02-ml-engineer/02-working-with-data/README|02-working-with-data/]] — **[Intermediate]** — cleaning, feature engineering & scaling, train/val/test splits (data is where most ML work actually happens)
3. [[ai-ml/02-ml-engineer/03-classical-ml/README|03-classical-ml/]] — **[Intermediate]** — the algorithm zoo: regression & regularization, trees & ensembles, SVM/KNN/naive Bayes, clustering & PCA
4. [[ai-ml/02-ml-engineer/04-model-evaluation/README|04-model-evaluation/]] — **[Intermediate]** — metrics, overfitting/regularization, cross-validation, model selection, hyperparameter tuning
5. [[ai-ml/02-ml-engineer/05-deep-learning/README|05-deep-learning/]] — **[Intermediate → Advanced]** — neural network fundamentals (perceptron/MLP, backprop, activations, losses) and a real PyTorch training loop
6. [[ai-ml/02-ml-engineer/06-computer-vision/README|06-computer-vision/]] — **[Intermediate]** — CNNs, image data/augmentation, transfer learning
7. [[ai-ml/02-ml-engineer/07-sequence-models-and-nlp/README|07-sequence-models-and-nlp/]] — **[Advanced]** — RNN/LSTM/GRU, transformers & attention, NLP & embeddings
8. [[ai-ml/02-ml-engineer/08-other-architectures/README|08-other-architectures/]] — **[Advanced]** — autoencoders & GANs, recommendation systems, reinforcement learning
9. [[ai-ml/02-ml-engineer/09-building-and-fine-tuning/README|09-building-and-fine-tuning/]] — **[Advanced]** — designing an architecture, training from scratch vs fine-tuning, and explainability (SHAP/LIME)

**Operations half:**

10. [[ai-ml/02-ml-engineer/10-mlops/README|10-mlops/]] — **[Advanced]** — the ML lifecycle in production: experiment tracking, data pipelines, serving, drift monitoring, edge AI — cross-linking the [[devops/README|DevOps domain]] for the shared infrastructure

## Where the content comes from

The original flat `ml-engineering`/`computer-vision`/`building-your-own-models` content was re-homed into this reading order (nothing dropped), and the roadmap.sh gaps filled in this pass. It's mostly `[reference]` — solid conceptual coverage with real scikit-learn/PyTorch code, but the reps are *doing*: train the models, run the experiments, ship one. Where MLOps meets infrastructure, it cross-links [[devops/README|DevOps]] rather than re-explaining Docker/k8s/CI/CD/Terraform/Prometheus.

## Related
- [[ai-ml/00-foundations/03-mathematics/README|Mathematics]] — the linear algebra/calculus/probability these models are built on
- [[devops/README|DevOps]] — the operational tooling the MLOps section builds on
- [[ai-ml/README|AI/ML course map]] — the three paths
