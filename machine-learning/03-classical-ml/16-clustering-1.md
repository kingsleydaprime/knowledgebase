---
id: 2758d4f4-9c70-41d7-be93-224f3e61d63f
---

# Clustering 1: Grouping Data Without Labels

Clustering is an unsupervised machine learning technique that groups similar data points together into clusters (groups) based on their characteristics, without using any labeled data. The objective is to ensure that data points within the same cluster are more similar to each other than to those in different clusters, enabling the discovery of natural groupings and hidden patterns in complex datasets.

Earlier we saw that in unsupervised learning there are no known outputs, and one example was segmenting customers into groups. Clustering is the main technique for this.

## Before you start
<!-- bite: 67fee50c-8277-4232-98c6-13de63f37f6d -->

You should know what unsupervised learning is ([[machine-learning/01-foundations-of-ml/01-what-is-ml-and-types|What ML Is]]) and how distance is measured ([[machine-learning/03-classical-ml/03-distance-measures|Distance Measures]]).

After this lesson you will be able to:

- say what clustering is for and what it outputs;
- name the five types of clustering methods with one algorithm each;
- pick a suitable type for a dataset from its pros and cons.

## What clustering does
<!-- bite: 79dac438-d088-4983-88f2-269f49188bde -->

- **Goal:** Discover the natural grouping or structure in unlabeled data without predefined categories.
- **How:** Data points are assigned to clusters based on similarity or distance measure.
- **Similarity measures:** Can include Euclidean distance, cosine similarity or other metrics depending on data type and clustering method.
- **Output:** Each group is assigned a cluster ID, representing shared characteristics within the cluster.

For example, if we have customer purchase data, clustering can group customers with similar shopping habits. These clusters can then be used for targeted marketing, personalized recommendations or customer segmentation.

## Types of Clustering Methods
<!-- bite: b04d0e2f-e48d-4bab-95e3-ad1d2dc8a39a -->

Clustering methods can be classified on the basis of how they form clusters.

### 1. Centroid-based Clustering (Partitioning Methods)

Centroid-based clustering organizes data points around central prototypes called centroids, where each cluster is represented by the mean (or medoid) of its members. The number of clusters is specified in advance and the algorithm allocates points to the nearest centroid, making this technique efficient for spherical and similarly sized clusters but sensitive to outliers and initialization.

**Algorithms:**

- **K-means:** Iteratively assigns points to nearest centroid and recalculates centroids to minimize intra-cluster variance.
- **K-medoid:** Similar to K-means but uses actual data points (medoids) as centers, robust to outliers.

| Pros | Cons |
| --- | --- |
| Fast and scalable for large datasets | It requires pre-knowledge of K |
| Simple to implement and interpret | It is sensitive to initialization and outliers |
|  | It is not suitable for non-spherical clusters |

### 2. Density-based Clustering (Model-based Methods)

Density-based clustering defines clusters as contiguous regions of high data density separated by areas of lower density. This approach can identify clusters of arbitrary shapes, handles noise well and does not require predefining the number of clusters, though its effectiveness depends on chosen density parameters.

**Algorithms:**

- **DBSCAN** (Density Based Spatial Clustering of Application with Noise): Groups points with sufficient neighbors, labels sparse points as noise.
- **OPTICS** (Ordering Points To Identify Clustering Structure): Extends DBSCAN to handle varying densities.

| Pros | Cons |
| --- | --- |
| Handles clusters of varying shapes and sizes | Difficult to choose parameters like epsilon and min points |
| Effective on noisy datasets | Less effective for varying density clusters (except OPTICS) |
| Does not require cluster count upfront |  |

### 3. Connectivity-based Clustering (Hierarchical Clustering)

Connectivity-based clustering builds nested groupings of data by evaluating how data points are connected to their neighbors. It creates a **dendrogram**, a tree-like structure that reflects relationships at various granularity levels and does not require specifying clustering numbers in advance, but can be computationally intensive.

**Algorithms:**

- **Agglomerative (Hierarchical, bottom-up):** Start with each point as a cluster, iteratively merge closest clusters. It has no predict method.
- **Divisive (top-down):** Start with one cluster, iteratively split into smaller clusters.

A dendrogram is a visualization tool for hierarchical clustering that can handle multidimensional datasets.

| Pros | Cons |
| --- | --- |
| It provides a full hierarchy, easy to visualize | It is computationally intensive for large datasets |
| No need to specify number of clusters upfront | Merging/splitting decisions are irreversible |

### 4. Distribution-based Clustering

It assumes data is generated from a mixture of probability distributions such as Gaussian distributions and assigns points to clusters based on statistical likelihood. This method supports cluster with flexible shape and overlaps, but usually requires specifying the number of distributions.

**Algorithm:**

- **Gaussian Mixture Model (GMM):** Fits data as a weighted mixture of Gaussian distributions, assigns data points based on likelihood.

| Pros | Cons |
| --- | --- |
| Flexible cluster shapes | Requires specific number of components |
| Provides probabilistic membership | Computationally more expensive |
| Suitable for overlapping clusters | Sensitive to initialization |

### 5. Fuzzy Clustering

Fuzzy clustering extends traditional methods by allowing each data point to belong to multiple clusters with varying degrees of membership. This approach captures ambiguity and soft boundaries in data and is particularly useful when the clusters overlap or boundaries are not clear-cut.

**Algorithm:**

- **Fuzzy C-Means:** Similar to K-Means but with fuzzy memberships updated iteratively.

| Pros | Cons |
| --- | --- |
| Models data ambiguity explicitly | Choosing fuzziness parameter can be tricky |
| Useful for complex or imprecise data | Computational overhead compared to hard clustering |

## Applications of Clustering
<!-- bite: 62de6ce1-77ce-4328-b898-c4f0649a184a -->

- **Customer segmentation:** Grouping customers based on behaviour or demographics for targeted marketing and personalized services.
- **Anomaly detection:** Identifying outliers or fraudulent activities in finance, network security and sensor data.
- **Image segmentation:** Dividing images into meaningful parts for object detection, medical diagnostics or computer vision tasks.
- **Recommendation system:** Clustering user preferences to recommend movies, products or content tailored to different groups.
- **Market-basket analysis:** Discovering products frequently bought together to optimize store layouts and promotions.

## Check your understanding
<!-- bite: c0ad0a89-57fc-4f03-9f01-dac5ebbf320e -->

Try each one before you open the answer.

1. Which clustering type does not need the number of clusters upfront and labels sparse points as noise? Name an algorithm.

   <details><summary>Answer</summary>

   Density-based clustering, for example DBSCAN.

   </details>

2. What is the difference between K-means and K-medoid?

   <details><summary>Answer</summary>

   K-means uses the mean of the cluster's points as its centre. K-medoid uses an actual data point (a medoid) as the centre, which makes it more robust to outliers.

   </details>

3. In fuzzy clustering, how many clusters can one point belong to?

   <details><summary>Answer</summary>

   More than one, each with a degree of membership.

   </details>

## Before moving on
<!-- bite: cd8625fa-b005-4c6b-b9c5-ff8d4f6b26c9 -->

Clustering groups similar unlabelled points. Centroid-based (K-means), density-based (DBSCAN), connectivity-based (hierarchical), distribution-based (GMM) and fuzzy (Fuzzy C-Means) form clusters in different ways.

**Next:** [[machine-learning/03-classical-ml/17-clustering-2|Clustering 2]]. K-Means needs us to choose k first, and clustering has no correct answers to compare with. Next: how to choose k and check the result.

## About this lesson
<!-- bite: 441e31d0-0c0b-43e3-a3bc-09bd018307bd -->

**Level:** Intermediate. **Covers:** what clustering is, the five types of clustering methods with their pros and cons, and applications. Part 1 of 2 on clustering. **Source:** SSG 535 (Introduction to Machine Learning) class notes, 2025/2026 first semester. The wording is kept from the notes; only headings, links and the checks were added.
