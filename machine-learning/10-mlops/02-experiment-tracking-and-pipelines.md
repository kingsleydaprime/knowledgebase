---
id: 758dc736-b7b9-4278-b152-be8d8adef4e4
---

# Experiment Tracking & Pipelines

Experiment tracking records every training run; a pipeline repeats the same steps every time.

## What experiment tracking and pipelines are
<!-- bite: 228b7e72-40e0-4854-b8ea-06d4072caf4f -->

Experiment tracking is keeping a record of every model you train, with the settings and results of each run. A pipeline is a set of steps that runs in order, such as fetching data, cleaning it and training the model, so it can be repeated the same way every time. Without these, nobody can say which run produced the good model or how to make it again.

Next: experiment tracking, then versioning data and models.

## Experiment tracking — because ML is empirical
<!-- bite: 99e8f607-9b26-48dd-9672-be39c764d335 -->

ML development is a huge number of experiments: different features, architectures, hyperparameters. Without tracking, "which run produced the good model, and with what settings?" becomes unanswerable. **Experiment tracking** logs every run's parameters, metrics, and artifacts:

- **MLflow** — the popular open standard: log params/metrics/models per run, compare runs in a UI, and a **model registry** to version and stage models (staging → production).
- **Weights & Biases (W&B)** — polished hosted tracking + visualization, popular in research.
- **Neptune, Comet** — similar alternatives.

```python
import mlflow
with mlflow.start_run():
    mlflow.log_param("max_depth", 5)
    mlflow.log_metric("val_auc", 0.91)
    mlflow.sklearn.log_model(model, "model")
```

The payoff: every result is reproducible and comparable, and the best model is registered with a clear lineage back to its params.

## Versioning data and models
<!-- bite: 80a476a5-9463-4ca5-a381-5a20e0aa8256 -->

Git versions code but chokes on multi-GB datasets and model binaries. The ML-specific tools:

- **DVC (Data Version Control)** — Git-for-data: it version-controls datasets and model files by storing lightweight pointers in Git while the actual bytes live in cloud storage. This is what makes "reproduce the exact model from three months ago" possible — you check out the code *and* the matching data version.
- **Model registry** (MLflow, or cloud-native) — a versioned store of trained models with stages, so deployment pulls "the current production model" and rollback is selecting a previous version.

Tying **code + data + model + config** versions together is the core of MLOps reproducibility ([[machine-learning/10-mlops/01-mlops-fundamentals|fundamentals]]).

## Feature stores
<!-- bite: 773a399b-08ae-482d-ac1f-bcb75021177f -->

A recurring, expensive ML bug is **training-serving skew** — a feature computed one way in the training pipeline and slightly differently at serving time ([[machine-learning/10-mlops/04-serving-and-monitoring|serving]]). A **feature store** (Feast, Tecton) solves it by computing features *once* and serving the identical values to both training (batch) and serving (low-latency online), while also letting teams share and reuse features. Worth knowing as the standard answer to skew and feature reuse at scale, though overkill for small projects.

## Data pipelines
<!-- bite: cb70ec5a-9464-4392-93e1-28ea7cb9dab1 -->

Models need a reliable flow of data — ingested, cleaned, transformed, and delivered on a schedule. This is **data engineering**, and it overlaps ML heavily:

- **Orchestration** — **Airflow** (and Prefect, Dagster, Kubeflow Pipelines) schedule and manage multi-step pipelines as DAGs, with retries and dependencies. This is where a retraining pipeline actually lives.
- **Batch processing** — **Spark** for large-scale transformation.
- **Streaming** — **Kafka** (+ Flink) for real-time data flowing into features/predictions.
- **Storage** — data lakes (raw) and warehouses (structured, queried via SQL); increasingly "lakehouse" (Delta Lake).
- **Lineage** — tracking where data came from and how it was transformed, for debugging and compliance.

These are the same data-engineering concerns as any pipeline — the [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|batch-processing]] and [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|messaging]] notes cover the same ideas (throughput, backpressure, idempotency) in another domain — and the orchestration/scheduling overlaps [[devops/05-ci-cd/index|CI/CD]].

## Related
<!-- bite: 9ea873df-ae19-491b-8dad-cabcab950128 -->
- [[machine-learning/10-mlops/01-mlops-fundamentals|MLOps Fundamentals]] — why data/models need versioning
- [[machine-learning/10-mlops/04-serving-and-monitoring|Serving & Operations]] — where training-serving skew bites
- [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Data Pipelines (Java)]] — the same data-engineering concerns

## About this lesson
<!-- bite: 1dc0d62e-9fb4-4539-b4c8-13d78bd46843 -->

**Level:** reference. **Covers:** from the roadmap.sh `mlops` roadmap. The ML-specific tooling for reproducibility: tracking what you tried, versioning data and models, and automating the data → training flow.
