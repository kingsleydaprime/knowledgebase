# Experiment Tracking & Pipelines

**[reference]** — from the roadmap.sh `mlops` roadmap. The ML-specific tooling for reproducibility: tracking what you tried, versioning data and models, and automating the data → training flow.

## Experiment tracking — because ML is empirical

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

Git versions code but chokes on multi-GB datasets and model binaries. The ML-specific tools:

- **DVC (Data Version Control)** — Git-for-data: it version-controls datasets and model files by storing lightweight pointers in Git while the actual bytes live in cloud storage. This is what makes "reproduce the exact model from three months ago" possible — you check out the code *and* the matching data version.
- **Model registry** (MLflow, or cloud-native) — a versioned store of trained models with stages, so deployment pulls "the current production model" and rollback is selecting a previous version.

Tying **code + data + model + config** versions together is the core of MLOps reproducibility ([[ai-ml/02-ml-engineer/10-mlops/01-mlops-fundamentals|fundamentals]]).

## Feature stores

A recurring, expensive ML bug is **training-serving skew** — a feature computed one way in the training pipeline and slightly differently at serving time ([[ai-ml/02-ml-engineer/10-mlops/04-serving-and-monitoring|serving]]). A **feature store** (Feast, Tecton) solves it by computing features *once* and serving the identical values to both training (batch) and serving (low-latency online), while also letting teams share and reuse features. Worth knowing as the standard answer to skew and feature reuse at scale, though overkill for small projects.

## Data pipelines

Models need a reliable flow of data — ingested, cleaned, transformed, and delivered on a schedule. This is **data engineering**, and it overlaps ML heavily:

- **Orchestration** — **Airflow** (and Prefect, Dagster, Kubeflow Pipelines) schedule and manage multi-step pipelines as DAGs, with retries and dependencies. This is where a retraining pipeline actually lives.
- **Batch processing** — **Spark** for large-scale transformation.
- **Streaming** — **Kafka** (+ Flink) for real-time data flowing into features/predictions.
- **Storage** — data lakes (raw) and warehouses (structured, queried via SQL); increasingly "lakehouse" (Delta Lake).
- **Lineage** — tracking where data came from and how it was transformed, for debugging and compliance.

These are the same data-engineering concerns as any pipeline — the [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|batch-processing]] and [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|messaging]] notes cover the same ideas (throughput, backpressure, idempotency) in another domain — and the orchestration/scheduling overlaps [[devops/06-ci-cd/README|CI/CD]].

## Related
- [[ai-ml/02-ml-engineer/10-mlops/01-mlops-fundamentals|MLOps Fundamentals]] — why data/models need versioning
- [[ai-ml/02-ml-engineer/10-mlops/04-serving-and-monitoring|Serving & Operations]] — where training-serving skew bites
- [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Data Pipelines (Java)]] — the same data-engineering concerns
