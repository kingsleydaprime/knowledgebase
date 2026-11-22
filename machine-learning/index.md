# Machine Learning

## What machine learning is

**Machine learning is getting a computer to learn a task from examples instead of following rules a programmer wrote by hand.** To spot spam the old way, you write rules like "if it says 'you've won', it's spam", and spammers learn to dodge them. With machine learning, you show the computer thousands of emails already labelled spam or not spam, and it works out the patterns itself. What it learns is called a **model**.

This subject teaches you to **build, train and ship models as production software**, which is the ML engineer's job. roadmap.sh splits this role's body of knowledge across two roadmaps, and this track covers both — they're genuinely different disciplines under one role:

- **ML / modeling** ([`machine-learning`](https://roadmap.sh/machine-learning)) — the models themselves: the algorithm zoo, deep learning, evaluation. Sections 01–09.
- **MLOps / operations** ([`mlops`](https://roadmap.sh/mlops)) — running models in production: deployment, monitoring, pipelines, retraining. Essentially "DevOps for ML." Section 10.

Contrast the siblings: the [[data-science/index|Data Scientist]] uses models to *find answers* (and may touch neither production nor operations); the [[ai-engineering/index|AI Engineer]] builds on *pre-trained* models without training their own. The ML Engineer owns the model **and** ships it.

## Three subjects, three jobs

Data science, machine learning and AI engineering used to be one subject called "AI & ML". They are three jobs that share some basics, so each is its own subject now.

| Subject | The question it answers | What you produce | Do you train models? |
|---|---|---|---|
| [[data-science/index\|Data Science]] | "What does the data tell us?" | an answer or insight, often a report | sometimes, mostly simpler models |
| [[machine-learning/index\|Machine Learning]] | "How do we build a model and run it reliably in a real product?" | a trained model running as software | **yes** |
| [[ai-engineering/index\|AI Engineering]] | "How do we build a product on top of models others have trained?" | an app that uses models like Claude or GPT | **no**, you use existing ones |

## Reading order

**Start with [[machine-learning/00-foundations/index|00 — Foundations]]:** what AI and a model are, the maths, and Python's data tools.

**Modeling half:**

1. [[machine-learning/01-foundations-of-ml/index|01-foundations-of-ml/]] — **[Beginner]** — what ML is, the types of learning (supervised/unsupervised/RL), and the Python/scikit-learn/PyTorch toolkit
2. [[machine-learning/02-working-with-data/index|02-working-with-data/]] — **[Intermediate]** — cleaning, feature engineering & scaling, train/val/test splits (data is where most ML work actually happens)
3. [[machine-learning/03-classical-ml/index|03-classical-ml/]] — **[Intermediate]** — the classic models, one topic at a time: KNN, distance measures, LVQ, decision trees (in six parts), naive Bayes, Bayesian networks, linear models, kernel machines, clustering, PCA and inductive logic programming
4. [[machine-learning/04-model-evaluation/index|04-model-evaluation/]] — **[Intermediate]** — the confusion matrix and classification metrics, regression metrics, overfitting, cross-validation and tuning
5. [[machine-learning/05-deep-learning/index|05-deep-learning/]] — **[Intermediate → Advanced]** — neural network fundamentals (perceptron/MLP, backprop, activations, losses) and a real PyTorch training loop
6. [[machine-learning/06-computer-vision/index|06-computer-vision/]] — **[Intermediate]** — CNNs, image data/augmentation, transfer learning
7. [[machine-learning/07-sequence-models-and-nlp/index|07-sequence-models-and-nlp/]] — **[Advanced]** — RNN/LSTM/GRU, transformers & attention, NLP & embeddings
8. [[machine-learning/08-other-architectures/index|08-other-architectures/]] — **[Advanced]** — autoencoders & GANs, recommendation systems, reinforcement learning
9. [[machine-learning/09-building-and-fine-tuning/index|09-building-and-fine-tuning/]] — **[Advanced]** — designing an architecture, training from scratch vs fine-tuning, and explainability (SHAP/LIME)

**Operations half:**

10. [[machine-learning/10-mlops/index|10-mlops/]] — **[Advanced]** — the ML lifecycle in production: experiment tracking, data pipelines, serving, drift monitoring, edge AI — cross-linking the [[devops/index|DevOps domain]] for the shared infrastructure

## Where the content comes from

The original flat `ml-engineering`/`computer-vision`/`building-your-own-models` content was re-homed into this reading order (nothing dropped), and the roadmap.sh gaps filled in this pass. It's mostly `[reference]` — solid conceptual coverage with real scikit-learn/PyTorch code, but the reps are *doing*: train the models, run the experiments, ship one. Where MLOps meets infrastructure, it cross-links [[devops/index|DevOps]] rather than re-explaining Docker/k8s/CI/CD/Terraform/Prometheus.

## Related
- [[machine-learning/00-foundations/03-mathematics/index|Mathematics]] — the linear algebra/calculus/probability these models are built on
- [[devops/index|DevOps]] — the operational tooling the MLOps section builds on
- [[data-science/index|Data Science]] · [[ai-engineering/index|AI Engineering]] — the two sibling subjects
- [[machine-learning/projects|Projects]] · [[machine-learning/interview/index|Interview prep]]
- [[machine-learning/ssg-535-question-bank|SSG 535 question bank]] — every practice and past exam question from the class, with hidden solutions
