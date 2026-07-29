# Deployment & MLOps

A trained model sitting in a notebook isn't useful to anyone yet — deployment is turning it into something that serves real predictions to real requests, reliably, and MLOps is the discipline of operating that in production the way DevOps operates regular software (see [[devops-reference]] for the non-ML version of many of these same concerns).

## Serving — getting predictions out of a trained model

At minimum, serving means wrapping a trained model in something that accepts a request, runs [[01-training-loop-in-pytorch|inference]] (not training — see [[02-what-is-a-model|what-is-a-model]] for why these are separate concerns), and returns a response.

```python
from fastapi import FastAPI
import torch

app = FastAPI()
model = torch.load("model.pt")
model.eval()

@app.post("/predict")
def predict(features: list[float]):
    with torch.no_grad():
        input_tensor = torch.tensor(features).unsqueeze(0)
        output = model(input_tensor)
    return {"prediction": output.item()}
```

For higher-throughput or latency-sensitive needs, dedicated model-serving frameworks (TorchServe, Triton Inference Server, or a managed cloud equivalent) handle batching, GPU scheduling, and scaling that a hand-rolled API wrapper like the one above doesn't.

## Monitoring — a deployed model can degrade silently

Unlike traditional software, a model can keep running without errors while quietly getting *worse* — this is called **model drift**, and it comes in two flavors:
- **Data drift** — the real-world input distribution shifts away from what the model was trained on (user behavior changes, a new product category appears) — the model is still answering the same question, but the questions being asked have changed.
- **Concept drift** — the actual relationship between inputs and the correct output changes (fraud patterns evolve specifically to evade a fraud model) — the underlying pattern the model learned is no longer accurate.

Both require monitoring prediction quality *after* deployment, not just once at training time — tracking prediction distributions, and where possible, actual outcomes, to catch degradation before it causes real damage.

## Versioning — models change, and you need to track how

A production ML system needs to track which exact model version served which prediction, alongside the data and code version that produced it — critical for debugging a bad prediction after the fact and for being able to roll back to a previous model version if a new one underperforms in production despite looking better in offline evaluation.

## A/B testing and gradual rollout

Rather than replacing a production model with a new version all at once, route a small percentage of real traffic to the new model and compare its real-world performance against the current one before a full rollout — offline validation metrics (see [[02-evaluation-metrics|evaluation-metrics]]) don't always predict real-world performance perfectly, and gradual rollout limits the damage if they diverge.

## Retraining pipelines

Models don't stay accurate forever, especially under data/concept drift — production ML systems typically need an automated or semi-automated pipeline to retrain on fresh data periodically, evaluate the new version against the current one, and promote it only if it's genuinely better, rather than a one-time training event that's assumed to stay valid indefinitely.

## Gotchas

- **Training-serving skew** — if the data preprocessing at serving time doesn't exactly match what was used during training (a different scaling formula, a different feature computed slightly differently), the model silently receives different-looking inputs than it was trained on, degrading performance in a way that's easy to miss without specifically checking for it.
- Deploying a model without any monitoring is the equivalent of shipping code with no logging or alerting — the first sign of a problem ends up being a business outcome (poor recommendations, missed fraud) rather than a metric you caught early.
- Offline evaluation metrics (see [[02-evaluation-metrics|evaluation-metrics]]) being strong doesn't guarantee production performance will match — the real input distribution and downstream effects of a model's decisions (a recommendation changing what a user does next, which changes future training data) can differ from a static offline test set in ways that only show up after deployment.

## Related
- [[02-training-from-scratch-vs-fine-tuning|training-from-scratch-vs-fine-tuning]]
- [[02-evaluation-metrics|evaluation-metrics]]
- [[devops-reference]] — the non-ML operational disciplines this borrows heavily from
