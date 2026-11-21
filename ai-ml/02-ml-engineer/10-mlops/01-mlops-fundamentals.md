---
id: d5d13d48-d48b-491f-a3c7-f74edc03f3b2
---

# MLOps Fundamentals

**[reference]** — from the roadmap.sh `mlops` roadmap. What MLOps is, and — the key framing — what it adds *beyond* the [[devops/index|DevOps]] you already know.

## What MLOps is
<!-- bite: b8bb1bab-c9a2-4e64-b984-d31c1b02da0c -->

MLOps is the discipline of reliably building, deploying, and maintaining ML models in production. It's **DevOps applied to ML**, and it borrows most of DevOps wholesale — CI/CD, containers, infrastructure-as-code, monitoring. So rather than re-explain those, this section **cross-links the [[devops/index|DevOps domain]]** for the shared parts and focuses on what's genuinely ML-specific.

## What ML adds beyond ordinary DevOps
<!-- bite: 55bb27fb-f2cc-40c6-8fa6-5b9fc20b5f55 -->

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
<!-- bite: 317cb37c-5298-4e81-a8f8-1616924ff553 -->

MLOps automates and monitors this loop, rather than treating training as a one-time event:

```
data collection → data validation → feature engineering → training
   → evaluation → model validation → deployment → monitoring
   → (drift detected) → retrain → redeploy ...
```

The goal is **reproducibility** (rebuild any model from versioned data+code+config), **automation** (retrain/deploy via pipelines, not by hand), and **continuous monitoring** (catch degradation before it hurts).

## MLOps maturity
<!-- bite: 9d6c74df-d7ad-45ed-b819-947b935bbc19 -->

A useful way to place a team: from **manual** (notebooks, hand-deployed models, no monitoring — where most start) → **automated training pipelines** (retrain on a trigger) → **full CI/CD for ML** (automated retraining, validation, deployment, and monitoring closing the loop). You don't need the top rung on day one; match the investment to how much the model matters and how fast its world changes.

## What maps to DevOps (cross-links, not re-explained)
<!-- bite: eb069612-5f86-4ea2-8136-6b057224e8c5 -->

| MLOps needs | Lives in DevOps |
|---|---|
| Containerizing a model service | [[devops/03-docker/index\|Docker]] / [[devops/10-orchestration/index\|Kubernetes]] |
| Automated pipelines | [[devops/05-ci-cd/index\|CI/CD]] |
| Provisioning training/serving infra | [[devops/09-infrastructure-as-code/index\|Terraform/IaC]] |
| Metrics/logs/dashboards | [[devops/07-observability/index\|Observability]] |

MLOps = these + data/model versioning + experiment tracking + drift monitoring + retraining. The next notes cover that ML-specific delta.

## Related
<!-- bite: 9d82528e-f213-49c1-93a7-c827d20cb2d3 -->
- [[ai-ml/02-ml-engineer/10-mlops/02-experiment-tracking-and-pipelines|Experiment Tracking & Pipelines]] — versioning data/models/experiments
- [[ai-ml/02-ml-engineer/10-mlops/03-monitoring-and-edge|Monitoring & Edge]] — drift and edge deployment
- [[devops/index|DevOps]] — the shared foundation MLOps extends
