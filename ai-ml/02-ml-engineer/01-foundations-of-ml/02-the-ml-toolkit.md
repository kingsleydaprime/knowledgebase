# The ML Toolkit

**[reference]** — the Python stack every ML engineer works in. roadmap.sh lists these across both the `machine-learning` and `mlops` roadmaps; they're also the shared foundation the [[ai-ml/01-data-scientist/README|Data Scientist]] path needs (noted as a gap in [[ai-ml/00-foundations/README|00-foundations]]).

## Why Python

ML runs on Python — not because it's fast (it isn't), but because the heavy numeric work happens in optimized C/CUDA underneath (NumPy, PyTorch), and Python is the glue. The ecosystem, not the language, is the reason.

## The core stack

| Library | Role |
|---|---|
| **NumPy** | the foundation — n-dimensional arrays and vectorized math ([[ai-ml/00-foundations/03-mathematics/01-linear-algebra/README|linear algebra]] in code); nearly everything else is built on it |
| **pandas** | tabular data — the `DataFrame`, for loading, cleaning, and manipulating structured data ([[ai-ml/02-ml-engineer/02-working-with-data/README|working with data]]) |
| **Matplotlib / Seaborn** | visualization — plotting distributions, relationships, results (Seaborn is a higher-level layer on Matplotlib) |
| **scikit-learn** | classical ML — a consistent API for [[ai-ml/02-ml-engineer/03-classical-ml/README|regression, trees, SVMs, clustering, PCA]], plus preprocessing, metrics, and model selection. The workhorse for everything that isn't deep learning |
| **PyTorch** | deep learning — the research-and-increasingly-production standard; dynamic, Pythonic ([[ai-ml/02-ml-engineer/05-deep-learning/02-training-loop-in-pytorch|training loop]]) |
| **TensorFlow / Keras** | deep learning — Google's framework; Keras is its high-level API. Still common, especially in production/mobile ([[ai-ml/02-ml-engineer/10-mlops/03-monitoring-and-edge|edge]]) |

## The scikit-learn API — learn one, know them all

scikit-learn's real value is a *uniform* interface: every model is a class with `.fit()` (train) and `.predict()` (infer), so swapping algorithms is a one-line change. This is why it's the fastest way to try many models:

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

model = RandomForestClassifier()      # swap to LogisticRegression() — same interface
model.fit(X_train, y_train)           # train
preds = model.predict(X_test)         # infer
```

That `.fit()/.predict()` contract, plus `.transform()` for preprocessing, runs through the entire library — pipelines, cross-validation, and grid search ([[ai-ml/02-ml-engineer/04-model-evaluation/03-validation-and-tuning|validation & tuning]]) all compose on top of it.

## PyTorch vs TensorFlow — the short version

Both do deep learning; the practical differences have narrowed. PyTorch dominates research and is increasingly the production default (dynamic graphs, more Pythonic); TensorFlow retains strengths in mobile/edge deployment (TFLite) and some production tooling. For learning, **PyTorch** is the pragmatic pick, and this track uses it. Higher-level wrappers (PyTorch Lightning, Keras) cut boilerplate once you understand the [[ai-ml/02-ml-engineer/05-deep-learning/02-training-loop-in-pytorch|raw loop]].

## The environment

Real ML work lives in **Jupyter notebooks** for exploration (interactive, inline plots) and moves to plain `.py` modules for anything production-bound. `conda`/`venv` + `pip` manage dependencies; GPU work needs matching CUDA versions (a common setup headache). The [[ai-ml/02-ml-engineer/10-mlops/README|MLOps]] section covers taking this from a notebook to a reproducible pipeline.

## Related
- [[ai-ml/02-ml-engineer/01-foundations-of-ml/01-what-is-ml-and-types|What ML Is]] — what these tools are for
- [[ai-ml/02-ml-engineer/02-working-with-data/README|Working with Data]] — pandas/NumPy in anger
- [[ai-ml/00-foundations/03-mathematics/README|Mathematics]] — what NumPy computes
