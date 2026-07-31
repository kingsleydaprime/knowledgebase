# Clustering & PCA

**[reference]** — from the roadmap.sh `machine-learning` roadmap. The two workhorses of **unsupervised** learning — finding structure in data that has no labels.

## Clustering — grouping without labels

Clustering partitions data into groups of similar points, with no target to predict. Used for customer segmentation, topic discovery, anomaly detection, and exploration.

### K-means

The most common clustering algorithm: you pick `k` (the number of clusters), and it iteratively assigns each point to the nearest cluster center, then moves each center to the mean of its points, until it stabilizes.

```python
from sklearn.cluster import KMeans
km = KMeans(n_clusters=4).fit(X)
km.labels_          # cluster assignment per point
km.cluster_centers_
```

- Fast and scalable, the default first thing to try.
- **You must choose `k`** — the awkward part, since you usually don't know it. The *elbow method* (plot within-cluster variance vs `k`, look for the bend) and *silhouette score* help estimate it.
- Assumes roughly spherical, similarly-sized clusters, and it's sensitive to feature scaling and to initialization (run several times). Struggles with elongated or nested shapes.

### Hierarchical clustering

Builds a tree of clusters (a *dendrogram*) by repeatedly merging the closest pair of clusters (agglomerative). You don't pre-specify `k` — you cut the tree at whatever level gives the granularity you want. Slower than k-means (poor for huge data) but reveals nested structure and doesn't need `k` up front. **DBSCAN** is another alternative worth knowing — it finds arbitrarily-shaped clusters by density and labels outliers as noise, without needing `k`.

## PCA — dimensionality reduction

**Principal Component Analysis** compresses many features into fewer, keeping as much of the variation as possible. It finds the directions (principal components) along which the data varies most — mathematically, the [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/README|eigenvectors]] of the data's covariance — and projects the data onto the top few:

```python
from sklearn.decomposition import PCA
X_reduced = PCA(n_components=2).fit_transform(X)   # e.g. 100 features → 2, for plotting
```

Why reduce dimensions:

- **Visualization** — squash high-dimensional data to 2D/3D to actually see it.
- **Speed & the curse of dimensionality** — fewer features means faster training and less overfitting; many algorithms (like [[ai-ml/02-ml-engineer/03-classical-ml/03-svm-knn-naive-bayes|KNN]]) degrade badly in high dimensions.
- **Denoising** — dropping low-variance components discards noise.

The cost: the new components are **linear combinations** of original features, so interpretability is lost (a component isn't "age" anymore, it's a blend). For non-linear structure, **t-SNE** and **UMAP** are the go-to visualization alternatives (great for seeing clusters, but for plotting only, not as features).

## Where these fit

Unsupervised methods are often a *step* in a pipeline rather than the end: cluster to create segment labels, or PCA to compress features before feeding a supervised model. They're also central to the [[ai-ml/01-data-scientist/README|Data Scientist]] path's exploratory analysis. And the "compress to a meaningful lower-dimensional representation" idea reappears, learned rather than linear, in [[ai-ml/02-ml-engineer/08-other-architectures/01-autoencoders-and-gans|autoencoders]] and in [[ai-ml/03-ai-engineer/06-rag-and-embeddings|embeddings]].

## Related
- [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/README|Linear Algebra]] — eigenvectors, the basis of PCA
- [[ai-ml/02-ml-engineer/08-other-architectures/01-autoencoders-and-gans|Autoencoders]] — the neural, non-linear version of dimensionality reduction
- [[ai-ml/02-ml-engineer/02-working-with-data/02-feature-engineering-and-scaling|Feature Scaling]] — required before distance-based clustering
