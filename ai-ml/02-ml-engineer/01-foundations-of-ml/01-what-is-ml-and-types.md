# What ML Is, and the Types of Learning

**[reference]** — from the roadmap.sh `machine-learning` roadmap. Orientation for the whole modeling half.

## What machine learning is

Machine learning is getting a computer to learn a task from **data** instead of from **hand-written rules**. Rather than a programmer specifying "if the email contains X and Y, mark it spam," you show the system thousands of labeled emails and it *infers* the rule — a function mapping input to output — by adjusting internal parameters ([[ai-ml/00-foundations/02-what-is-a-model|what a model is]]). Reach for ML when the pattern is too complex, variable, or poorly-understood to hand-specify; a plain rule beats a model whenever the logic is actually known ([[ai-ml/03-ai-engineer/01-the-ai-engineer-role|choosing the right tool]]).

The whole modeling half of this track is variations on one loop: **guess → measure error (loss) → adjust parameters to reduce it → repeat** ([[ai-ml/00-foundations/03-mathematics/04-optimization|optimization]]), with the real goal being **generalization** — performing well on data never seen during training, not memorizing the training set.

## The types of learning

The single most useful first classification of any ML problem — it determines which algorithms even apply:

### Supervised learning — learning from labeled examples

You have inputs **and** their correct outputs (labels), and the model learns to predict the output for new inputs. The dominant paradigm in practice. Two sub-types by output shape:

- **Classification** — predict a category (spam/not-spam, which digit, which disease). Output is discrete.
- **Regression** — predict a continuous number (house price, temperature, demand). Output is a quantity.

This is the world of [[ai-ml/02-ml-engineer/03-classical-ml/01-regression|regression]], [[ai-ml/02-ml-engineer/03-classical-ml/02-trees-and-ensembles|trees]], and most of [[ai-ml/02-ml-engineer/05-deep-learning/README|deep learning]].

### Unsupervised learning — finding structure without labels

You have inputs but **no** labels; the model finds structure on its own:

- **Clustering** — group similar points (customer segments, topic discovery) — [[ai-ml/02-ml-engineer/03-classical-ml/04-unsupervised-clustering-and-pca|k-means]].
- **Dimensionality reduction** — compress many features into fewer while keeping the signal ([[ai-ml/02-ml-engineer/03-classical-ml/04-unsupervised-clustering-and-pca|PCA]]).

### Self-supervised learning — labels from the data itself

A hugely important modern middle ground: the model generates its *own* labels from unlabeled data by hiding part of the input and predicting it. **This is how LLMs are pretrained** — "predict the next token" is a label the text provides for free ([[ai-ml/03-ai-engineer/02-how-llms-work|how LLMs work]]). It unlocked training on internet-scale unlabeled data. **Semi-supervised** learning (a little labeled data + a lot of unlabeled) is the related cousin.

### Reinforcement learning — learning from reward

No fixed dataset of answers at all — an agent takes actions in an environment and receives a reward signal, adjusting behavior to maximize cumulative reward over time. Fundamentally different from the above. Game-playing (AlphaGo), robotics, and — notably — the RLHF step that makes LLMs follow instructions. Covered in [[ai-ml/02-ml-engineer/08-other-architectures/03-reinforcement-learning|reinforcement learning]].

## The ML workflow

Whatever the type, real ML work follows a loop that's mostly *not* modeling:

```
frame the problem → get & clean data → engineer features → split data
   → train a model → evaluate honestly → tune → deploy → monitor → (retrain)
```

The unglamorous truth: **most of the effort is data** ([[ai-ml/02-ml-engineer/02-working-with-data/README|working with data]]) and **honest evaluation** ([[ai-ml/02-ml-engineer/04-model-evaluation/README|model evaluation]]), not picking a clever algorithm. And the last two steps — deploy and monitor — are the [[ai-ml/02-ml-engineer/10-mlops/README|MLOps]] half that distinguishes an ML *engineer* from someone training models in a notebook.

## Related
- [[ai-ml/00-foundations/02-what-is-a-model|What is a Model]] — the shared concept
- [[ai-ml/02-ml-engineer/01-foundations-of-ml/02-the-ml-toolkit|The ML Toolkit]] — the libraries you'll use
- [[ai-ml/02-ml-engineer/03-classical-ml/README|Classical ML]] — the supervised/unsupervised algorithms
