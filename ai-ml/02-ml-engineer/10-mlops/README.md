# 10 — MLOps

The operations half of the ML Engineer role: running models in production reliably. It's "DevOps for ML," so it **cross-links the [[devops/README|DevOps domain]]** for the shared infrastructure (Docker, Kubernetes, CI/CD, Terraform, Prometheus) and focuses here on what's *ML-specific*. Part of the [[ai-ml/02-ml-engineer/README|ML Engineer track]].

1. [[ai-ml/02-ml-engineer/10-mlops/01-mlops-fundamentals|MLOps Fundamentals]] — **[Advanced]** — the ML lifecycle, MLOps principles, and what ML adds beyond ordinary DevOps (data + models as versioned artifacts, not just code)
2. [[ai-ml/02-ml-engineer/10-mlops/02-experiment-tracking-and-pipelines|Experiment Tracking & Pipelines]] — **[Advanced]** — MLflow/DVC/W&B, model registries, feature stores, and data/training pipelines (Airflow, Kafka, Spark)
3. [[ai-ml/02-ml-engineer/10-mlops/03-monitoring-and-edge|Monitoring & Edge]] — **[Advanced]** — drift detection, model monitoring, and deploying to constrained/edge devices (TFLite, PyTorch Mobile, Jetson)
4. [[ai-ml/02-ml-engineer/10-mlops/04-serving-and-monitoring|Serving & Operations]] — **[Advanced]** — getting predictions out of a model: serving, versioning, A/B rollout, retraining pipelines, training-serving skew

## Related
- [[devops/README|DevOps]] — the shared infrastructure MLOps runs on
- [[devops/10-observability/README|Observability (DevOps)]] — monitoring, adapted for model drift
- [[devops/06-ci-cd/README|CI/CD (DevOps)]] — pipelines, extended to data + models
- [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Data pipelines (Java)]] — the same data-engineering concerns elsewhere
