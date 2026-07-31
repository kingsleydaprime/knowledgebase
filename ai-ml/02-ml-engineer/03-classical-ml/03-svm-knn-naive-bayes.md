# SVM, KNN & Naive Bayes

**[reference]** — from the roadmap.sh `machine-learning` roadmap. Three more classic supervised algorithms, each with a distinct idea worth knowing and a niche where it shines.

## Support Vector Machines (SVM)

An SVM finds the decision boundary that **maximizes the margin** — the widest possible gap between the two classes. The points sitting on the edge of that gap (the "support vectors") are the only ones that matter; the rest don't affect the boundary.

Its superpower is the **kernel trick**: by implicitly mapping data into a higher-dimensional space, an SVM can find a linear boundary there that corresponds to a complex non-linear boundary in the original space — without ever computing the high-dimensional coordinates.

```python
from sklearn.svm import SVC
SVC(kernel="rbf", C=1.0).fit(X_train, y_train)   # rbf = the common non-linear kernel
```

Strong on **small-to-medium datasets with clear margins** and high-dimensional data (text classification historically). The catch: **doesn't scale** to very large datasets (training is roughly quadratic), needs feature scaling, and the kernel/`C`/`gamma` choices need tuning. Largely superseded by gradient boosting for tabular and by deep learning for text/images, but conceptually important and still useful on the right small problem.

## K-Nearest Neighbors (KNN)

The laziest algorithm, and the most intuitive: to classify a new point, find its `k` nearest points in the training data and take the majority vote (or average, for regression). There's **no training** — it just stores the data and does all the work at prediction time.

```python
from sklearn.neighbors import KNeighborsClassifier
KNeighborsClassifier(n_neighbors=5).fit(X_train, y_train)
```

- Simple, no assumptions about the data's shape, naturally handles multi-class.
- **Prediction is slow** (must compare to all training points) and it degrades in high dimensions (the "curse of dimensionality" — distances become meaningless when there are many features). Needs scaling, since it's distance-based.
- `k` is the key hyperparameter: small `k` overfits (noisy), large `k` oversmooths.

The *idea* — "similar inputs have similar outputs, measured by distance" — is exactly the intuition behind [[ai-ml/03-ai-engineer/06-rag-and-embeddings|semantic search over embeddings]], which is essentially KNN in a learned vector space.

## Naive Bayes

Applies [[ai-ml/00-foundations/03-mathematics/03-probability-and-statistics/03-bayes-theorem|Bayes' theorem]] with a "naive" assumption: that all features are independent given the class. That assumption is almost always false, yet the model works surprisingly well anyway — especially for **text classification** (spam filtering, sentiment):

```python
from sklearn.naive_bayes import MultinomialNB
MultinomialNB().fit(X_train, y_train)   # great for word-count / TF-IDF text features
```

Extremely fast to train and predict, works with little data, and a strong baseline for text. Its probability estimates are poorly calibrated (the independence assumption), so trust the *ranking* more than the exact probabilities.

## Choosing among them

| Algorithm | Shines when | Avoid when |
|---|---|---|
| **SVM** | small/medium data, clear margins, high-dim | large datasets |
| **KNN** | small data, low dimensions, simple baseline | large data, many features |
| **Naive Bayes** | text, high-dim sparse features, tiny data | features are strongly dependent and you need calibrated probabilities |

All three are worth recognizing, but for most tabular problems [[ai-ml/02-ml-engineer/03-classical-ml/02-trees-and-ensembles|gradient boosting]] will beat them — these earn their place on specific data shapes (SVM on clean small margins, Naive Bayes on text, KNN as a dead-simple baseline).

## Related
- [[ai-ml/02-ml-engineer/03-classical-ml/02-trees-and-ensembles|Trees & Ensembles]] — the usual stronger default
- [[ai-ml/00-foundations/03-mathematics/03-probability-and-statistics/03-bayes-theorem|Bayes' Theorem]] — the basis for Naive Bayes
- [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG & Embeddings]] — KNN's idea applied at scale
