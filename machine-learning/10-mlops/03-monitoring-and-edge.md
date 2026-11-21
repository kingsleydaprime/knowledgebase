---
id: f193314d-6aba-408e-9d70-86ed03436fb0
---

# Monitoring & Edge

Monitoring a model means watching it after launch to catch it getting worse, even when nothing has crashed. Edge AI means running a model on the device itself, like a phone or a camera, instead of on a faraway server. Face unlock on your phone works without the internet because the model runs right there on the phone.

## Monitoring — a model degrades without erroring
<!-- bite: a142927b-2a1c-4242-aad3-66e524231cd8 -->

The defining difference from [[devops/07-observability/index|ordinary observability]]: traditional monitoring catches _errors and latency_; ML monitoring must also catch a model that keeps running fine while getting quietly **worse**. You watch two layers:

- **Operational** (same as any service — reuse [[devops/07-observability/index|DevOps observability]]): latency, throughput, error rate, resource use of the model service.
- **Model quality** (ML-specific): is the model still accurate?

### Drift — the core ML failure mode

- **Data drift** — the input distribution shifts from what the model trained on (new user behavior, a new product category, seasonality). The model is answering the same question, but the questions changed.
- **Concept drift** — the input→output _relationship_ itself changes (fraud tactics evolve specifically to evade the model). What the model learned is no longer true.
- **Prediction drift** — the distribution of the model's _outputs_ shifts, an early warning even before you know outcomes.

The hard part: **ground truth is delayed or missing.** You often don't learn whether a prediction was right until much later (did the flagged transaction turn out fraudulent?), or never. So monitoring leans on _proxy_ signals — input distribution shifts, prediction distribution shifts, confidence drops — to raise an alarm before accuracy data confirms the damage.

Tools: **Evidently**, **WhyLabs**, **Arize**, or cloud-native model monitors compute drift metrics and dashboards; they feed the same alerting stack as [[devops/07-observability/index|DevOps observability]]. When drift crosses a threshold, it triggers investigation or an automated [[machine-learning/10-mlops/04-serving-and-monitoring|retraining pipeline]].

## Edge AI — models off the server
<!-- bite: 705cd000-f330-44cc-b45f-66a347f4d7e3 -->

Not every model runs in a datacenter. **Edge AI** runs models directly on phones, cameras, sensors, cars, and embedded devices — for **latency** (no network round-trip), **privacy** (data never leaves the device), **offline** operation, and **cost** (no per-inference server bill). The constraints are severe: limited compute, memory, and power.

Getting a model small and fast enough:

- **Quantization** — drop weight precision (32-bit float → 8-bit int), shrinking size and speeding inference at a small accuracy cost (the same idea as [[ai-engineering/03-the-model-landscape|LLM quantization]]).
- **Pruning** — remove weights/neurons that contribute little.
- **Distillation** — train a small "student" model to mimic a big "teacher," capturing much of its ability at a fraction of the size.

Runtimes/hardware:

- **TensorFlow Lite (LiteRT)** — the standard for on-device (mobile/embedded) inference.
- **PyTorch Mobile / ExecuTorch** — the PyTorch equivalent.
- **ONNX Runtime** — a portable format/runtime for deploying across many targets.
- **NVIDIA Jetson**, Coral, and mobile NPUs — hardware accelerators for edge inference.

Edge shifts the MLOps problem: updating a model means pushing it to thousands of devices, and monitoring means collecting signals back from them — a harder deployment/observability story than a central service.

## Related
<!-- bite: 8ff071e3-e664-4813-ae72-5e8798d39af5 -->

- [[machine-learning/10-mlops/04-serving-and-monitoring|Serving & Operations]] — retraining pipelines drift triggers
- [[devops/07-observability/index|Observability (DevOps)]] — the operational-monitoring foundation this extends
- [[ai-engineering/03-the-model-landscape|The Model Landscape]] — quantization for LLMs, the same idea

## About this lesson
<!-- bite: e7b8c0c7-e828-45ab-ae9b-218482c8fede -->

**Level:** reference. **Covers:** from the roadmap.sh `mlops` roadmap. Two ML-specific production concerns: watching a model for silent decay, and running models on constrained devices.
