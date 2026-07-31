# Serving & Operations

**Source:** the original project's deployment note, re-homed into the MLOps section and trimmed so drift/monitoring depth lives in its own note ([[ai-ml/02-ml-engineer/10-mlops/03-monitoring-and-edge|monitoring & edge]]). Getting a trained model out of a notebook and operating it: serving predictions, versioning, safe rollout, and retraining. The infra underneath is [[devops/README|DevOps]] ([[devops/02-docker/README|Docker]]/[[devops/05-orchestration/README|k8s]]/[[devops/10-observability/README|observability]]) — this is the ML-specific layer on top.

## Serving — getting predictions out of a model

At minimum, serving wraps a trained model in something that accepts a request, runs **inference** (not training — see [[ai-ml/00-foundations/02-what-is-a-model|why these are separate]]), and returns a response:

```python
from fastapi import FastAPI
import torch

app = FastAPI()
model = torch.load("model.pt")
model.eval()

@app.post("/predict")
def predict(features: list[float]):
    with torch.no_grad():
        output = model(torch.tensor(features).unsqueeze(0))
    return {"prediction": output.item()}
```

For higher throughput or latency-sensitive needs, dedicated serving frameworks (**TorchServe**, **NVIDIA Triton**, BentoML, or a managed cloud endpoint) handle request **batching**, GPU scheduling, and autoscaling that a hand-rolled wrapper doesn't. **Batch** (offline, score a big dataset on a schedule) vs **online/real-time** (low-latency per-request) serving are different problems — pick per use case.

## Versioning — track what served what

A production ML system must record which exact **model version** served which prediction, tied to the data and code version that produced it ([[ai-ml/02-ml-engineer/10-mlops/02-experiment-tracking-and-pipelines|model registry]]) — essential for debugging a bad prediction after the fact and for **rollback** when a new model underperforms in production despite looking better offline.

## A/B testing and gradual rollout

Don't swap the whole production model at once. Route a small % of real traffic to the new version and compare *real-world* performance before full rollout — the same canary/blue-green ideas as [[devops/06-ci-cd/01-ci-cd-concepts|CI/CD deployment strategies]]. This matters more in ML than in ordinary software because offline metrics ([[ai-ml/02-ml-engineer/04-model-evaluation/01-evaluation-metrics|evaluation]]) don't perfectly predict live performance, and a model's decisions change user behavior in ways only visible on live traffic ([[ai-ml/02-ml-engineer/08-other-architectures/02-recommendation-systems|feedback loops]]).

## Retraining pipelines

Models decay under [[ai-ml/02-ml-engineer/10-mlops/03-monitoring-and-edge|drift]], so production ML needs a pipeline to retrain on fresh data, evaluate the new model against the current one, and **promote only if genuinely better** — rather than a one-time training event assumed valid forever. This closes the MLOps loop ([[ai-ml/02-ml-engineer/10-mlops/01-mlops-fundamentals|fundamentals]]); orchestration lives in [[ai-ml/02-ml-engineer/10-mlops/02-experiment-tracking-and-pipelines|data pipelines]].

## The gotcha: training-serving skew

The classic silent killer — if serving-time preprocessing doesn't *exactly* match training-time (a different scaling formula, a feature computed slightly differently), the model receives different-looking inputs than it trained on and degrades in a way that's easy to miss. The standard defense is a [[ai-ml/02-ml-engineer/10-mlops/02-experiment-tracking-and-pipelines|feature store]] computing features once for both paths. And deploying with no [[ai-ml/02-ml-engineer/10-mlops/03-monitoring-and-edge|monitoring]] at all means the first sign of a problem is a business outcome (missed fraud, bad recommendations), not a metric you caught early.

## Related
- [[ai-ml/02-ml-engineer/10-mlops/03-monitoring-and-edge|Monitoring & Edge]] — catching the drift that triggers retraining
- [[ai-ml/02-ml-engineer/10-mlops/02-experiment-tracking-and-pipelines|Experiment Tracking & Pipelines]] — model registry, feature stores, orchestration
- [[ai-ml/02-ml-engineer/09-building-and-fine-tuning/02-training-from-scratch-vs-fine-tuning|Training From Scratch vs Fine-Tuning]] — what produced the model being served
- [[devops/README|DevOps]] — the operational disciplines this borrows from
