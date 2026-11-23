---
id: 078cce39-23cd-46de-9c1a-8ea1b31a6cfc
---

# Serving & Operations

Serving is getting a trained model out of a notebook and answering real requests with it.

## What serving and operations are
<!-- bite: 6b5162bb-fa36-4ed6-9b35-5e5d73386d82 -->

Getting a trained model out of a notebook and operating it: serving predictions, versioning, safe rollout, and retraining. The infra underneath is [[devops/index|DevOps]] ([[devops/03-docker/index|Docker]]/[[devops/10-orchestration/index|k8s]]/[[devops/07-observability/index|observability]]) — this is the ML-specific layer on top.

Next: serving itself, then versioning, safe rollout and retraining.

## Serving — getting predictions out of a model
<!-- bite: e5c52d7b-79f9-43cc-b427-95570cd27519 -->

At minimum, serving wraps a trained model in something that accepts a request, runs **inference** (not training — see [[machine-learning/00-foundations/02-what-is-a-model|why these are separate]]), and returns a response:

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
<!-- bite: 743369e5-8e00-4553-ba35-70379fe56a25 -->

A production ML system must record which exact **model version** served which prediction, tied to the data and code version that produced it ([[machine-learning/10-mlops/02-experiment-tracking-and-pipelines|model registry]]) — essential for debugging a bad prediction after the fact and for **rollback** when a new model underperforms in production despite looking better offline.

## A/B testing and gradual rollout
<!-- bite: f3d763df-fea8-4bc6-8100-fff8c7da219c -->

Don't swap the whole production model at once. Route a small % of real traffic to the new version and compare *real-world* performance before full rollout — the same canary/blue-green ideas as [[devops/05-ci-cd/01-ci-cd-concepts|CI/CD deployment strategies]]. This matters more in ML than in ordinary software because offline metrics ([[machine-learning/04-model-evaluation/01-evaluation-metrics-1|evaluation]]) don't perfectly predict live performance, and a model's decisions change user behavior in ways only visible on live traffic ([[machine-learning/08-other-architectures/02-recommendation-systems|feedback loops]]).

## Retraining pipelines
<!-- bite: 2de2a59f-d940-4df4-82ef-0457d8ca5ea3 -->

Models decay under [[machine-learning/10-mlops/03-monitoring-and-edge|drift]], so production ML needs a pipeline to retrain on fresh data, evaluate the new model against the current one, and **promote only if genuinely better** — rather than a one-time training event assumed valid forever. This closes the MLOps loop ([[machine-learning/10-mlops/01-mlops-fundamentals|fundamentals]]); orchestration lives in [[machine-learning/10-mlops/02-experiment-tracking-and-pipelines|data pipelines]].

## The gotcha: training-serving skew
<!-- bite: bdd0d860-b317-4457-b6fc-f9c88323ede6 -->

The classic silent killer — if serving-time preprocessing doesn't *exactly* match training-time (a different scaling formula, a feature computed slightly differently), the model receives different-looking inputs than it trained on and degrades in a way that's easy to miss. The standard defense is a [[machine-learning/10-mlops/02-experiment-tracking-and-pipelines|feature store]] computing features once for both paths. And deploying with no [[machine-learning/10-mlops/03-monitoring-and-edge|monitoring]] at all means the first sign of a problem is a business outcome (missed fraud, bad recommendations), not a metric you caught early.

## Check your understanding
<!-- bite: d960e253-73ae-4df7-9427-45722aa97471 -->

Try each one before you open the answer.

1. <!-- q: mcq id="c0851c52" -->
   Scoring a big dataset every night is which kind of serving?

   - [x] Batch (offline)
   - [ ] Online (real-time)

   <details><summary>Answer</summary>

   Batch. Online serving answers each request with low latency. They are different problems, so pick one per use case.

   </details>

2. <!-- q: mcq id="b61f7f88" -->
   Why route only a small share of live traffic to a new model first?

   - [ ] To save GPU memory
   - [x] Offline metrics don't perfectly predict live performance, so you compare on real traffic before full rollout
   - [ ] Because the new model is always worse

   <details><summary>Answer</summary>

   Offline metrics aren't the whole story, and a model's decisions change user behaviour in ways only live traffic shows.

   </details>

3. <!-- q: gap id="2ae9c507" answers="better" -->
   Fill in the gap. A retraining pipeline should promote the new model only if it is genuinely ___ than the current one.

   <details><summary>Answer</summary>

   Better. Retrain on fresh data, evaluate against the current model, and promote only if it wins.

   </details>

4. <!-- q: mcq id="79b5b083" -->
   In the FastAPI example, why does the code call `model.eval()` and use `torch.no_grad()`?

   - [x] Serving is inference: no training happens, so use inference behaviour and skip gradients
   - [ ] To retrain the model on each request
   - [ ] To make the model larger

   <details><summary>Answer</summary>

   Serving runs inference, not training. `eval()` switches layers like dropout to inference mode, and `no_grad()` skips the gradients you don't need.

   </details>

5. <!-- q: open id="6e286505" -->
   Why must a production system record which model version served each prediction?

   <details><summary>Answer</summary>

   So you can debug a bad prediction after the fact by tracing it to the exact model, data and code. It also lets you roll back when a new model underperforms in production.

   </details>

## Related
<!-- bite: 92052cde-4217-492c-b781-2dc1359c118b -->
- [[machine-learning/10-mlops/03-monitoring-and-edge|Monitoring & Edge]] — catching the drift that triggers retraining
- [[machine-learning/10-mlops/02-experiment-tracking-and-pipelines|Experiment Tracking & Pipelines]] — model registry, feature stores, orchestration
- [[machine-learning/09-building-and-fine-tuning/02-training-from-scratch-vs-fine-tuning|Training From Scratch vs Fine-Tuning]] — what produced the model being served
- [[devops/index|DevOps]] — the operational disciplines this borrows from

## About this lesson
<!-- bite: 4e5bad55-a70d-4e8c-a255-422ea721bd8e -->

**Source:** the original project's deployment note, re-homed into the MLOps section and trimmed so drift/monitoring depth lives in its own note ([[machine-learning/10-mlops/03-monitoring-and-edge|monitoring & edge]]).
