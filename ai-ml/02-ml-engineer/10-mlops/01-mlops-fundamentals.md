# MLOps Fundamentals

**[reference]** — from the roadmap.sh `mlops` roadmap. What MLOps is, and — the key framing — what it adds *beyond* the [[devops/README|DevOps]] you already know.

## What MLOps is

MLOps is the discipline of reliably building, deploying, and maintaining ML models in production. It's **DevOps applied to ML**, and it borrows most of DevOps wholesale — CI/CD, containers, infrastructure-as-code, monitoring. So rather than re-explain those, this section **cross-links the [[devops/README|DevOps domain]]** for the shared parts and focuses on what's genuinely ML-specific.

## What ML adds beyond ordinary DevOps

Traditional software has one thing that changes: **code**. ML systems have **three** things that change and interact — and that's the entire source of MLOps's extra complexity:

```
Traditional:   code → build → test → deploy → monitor
ML:            code + DATA + MODEL → ... → deploy → monitor for DRIFT → retrain
```

- **Data is a versioned artifact.** The same code trained on different data produces a different model. You must version *data*, not just code ([[ai-ml/02-ml-engineer/10-mlops/02-experiment-tracking-and-pipelines|DVC, feature stores]]). Git doesn't handle multi-GB datasets.
- **The model is a versioned artifact** — a trained binary that must be tracked, registered, and rollback-able, tied to the exact data + code that produced it ([[ai-ml/02-ml-engineer/10-mlops/02-experiment-tracking-and-pipelines|model registry]]).
- **"Correct" isn't binary and it decays.** Software is right or has a bug; a model is *accurate enough* until the world shifts and it silently degrades ([[ai-ml/02-ml-engineer/10-mlops/03-monitoring-and-edge|drift]]). It needs **retraining**, not just patching.
- **Testing is different.** You can't unit-test "is this prediction correct." You test data quality, validate model performance against thresholds, and check for training-serving skew ([[ai-ml/02-ml-engineer/10-mlops/04-serving-and-monitoring|serving]]).

## The ML lifecycle

MLOps automates and monitors this loop, rather than treating training as a one-time event:

```
data collection → data validation → feature engineering → training
   → evaluation → model validation → deployment → monitoring
   → (drift detected) → retrain → redeploy ...
```

The goal is **reproducibility** (rebuild any model from versioned data+code+config), **automation** (retrain/deploy via pipelines, not by hand), and **continuous monitoring** (catch degradation before it hurts).

## MLOps maturity

A useful way to place a team: from **manual** (notebooks, hand-deployed models, no monitoring — where most start) → **automated training pipelines** (retrain on a trigger) → **full CI/CD for ML** (automated retraining, validation, deployment, and monitoring closing the loop). You don't need the top rung on day one; match the investment to how much the model matters and how fast its world changes.

## What maps to DevOps (cross-links, not re-explained)

| MLOps needs | Lives in DevOps |
|---|---|
| Containerizing a model service | [[devops/02-docker/README|Docker]] / [[devops/05-orchestration/README|Kubernetes]] |
| Automated pipelines | [[devops/06-ci-cd/README|CI/CD]] |
| Provisioning training/serving infra | [[devops/07-infrastructure-as-code/README|Terraform/IaC]] |
| Metrics/logs/dashboards | [[devops/10-observability/README|Observability]] |

MLOps = these + data/model versioning + experiment tracking + drift monitoring + retraining. The next notes cover that ML-specific delta.

## Related
- [[ai-ml/02-ml-engineer/10-mlops/02-experiment-tracking-and-pipelines|Experiment Tracking & Pipelines]] — versioning data/models/experiments
- [[ai-ml/02-ml-engineer/10-mlops/03-monitoring-and-edge|Monitoring & Edge]] — drift and edge deployment
- [[devops/README|DevOps]] — the shared foundation MLOps extends
