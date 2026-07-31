# Monitoring & Edge

**[reference]** — from the roadmap.sh `mlops` roadmap. Two ML-specific production concerns: watching a model for silent decay, and running models on constrained devices.

## Monitoring — a model degrades without erroring

The defining difference from [[devops/10-observability/README|ordinary observability]]: traditional monitoring catches *errors and latency*; ML monitoring must also catch a model that keeps running fine while getting quietly **worse**. You watch two layers:

- **Operational** (same as any service — reuse [[devops/10-observability/README|DevOps observability]]): latency, throughput, error rate, resource use of the model service.
- **Model quality** (ML-specific): is the model still accurate?

### Drift — the core ML failure mode

- **Data drift** — the input distribution shifts from what the model trained on (new user behavior, a new product category, seasonality). The model is answering the same question, but the questions changed.
- **Concept drift** — the input→output *relationship* itself changes (fraud tactics evolve specifically to evade the model). What the model learned is no longer true.
- **Prediction drift** — the distribution of the model's *outputs* shifts, an early warning even before you know outcomes.

The hard part: **ground truth is delayed or missing.** You often don't learn whether a prediction was right until much later (did the flagged transaction turn out fraudulent?), or never. So monitoring leans on *proxy* signals — input distribution shifts, prediction distribution shifts, confidence drops — to raise an alarm before accuracy data confirms the damage.

Tools: **Evidently**, **WhyLabs**, **Arize**, or cloud-native model monitors compute drift metrics and dashboards; they feed the same alerting stack as [[devops/10-observability/README|DevOps observability]]. When drift crosses a threshold, it triggers investigation or an automated [[ai-ml/02-ml-engineer/10-mlops/04-serving-and-monitoring|retraining pipeline]].

## Edge AI — models off the server

Not every model runs in a datacenter. **Edge AI** runs models directly on phones, cameras, sensors, cars, and embedded devices — for **latency** (no network round-trip), **privacy** (data never leaves the device), **offline** operation, and **cost** (no per-inference server bill). The constraints are severe: limited compute, memory, and power.

Getting a model small and fast enough:

- **Quantization** — drop weight precision (32-bit float → 8-bit int), shrinking size and speeding inference at a small accuracy cost (the same idea as [[ai-ml/03-ai-engineer/03-the-model-landscape|LLM quantization]]).
- **Pruning** — remove weights/neurons that contribute little.
- **Distillation** — train a small "student" model to mimic a big "teacher," capturing much of its ability at a fraction of the size.

Runtimes/hardware:

- **TensorFlow Lite (LiteRT)** — the standard for on-device (mobile/embedded) inference.
- **PyTorch Mobile / ExecuTorch** — the PyTorch equivalent.
- **ONNX Runtime** — a portable format/runtime for deploying across many targets.
- **NVIDIA Jetson**, Coral, and mobile NPUs — hardware accelerators for edge inference.

Edge shifts the MLOps problem: updating a model means pushing it to thousands of devices, and monitoring means collecting signals back from them — a harder deployment/observability story than a central service.

## Related
- [[ai-ml/02-ml-engineer/10-mlops/04-serving-and-monitoring|Serving & Operations]] — retraining pipelines drift triggers
- [[devops/10-observability/README|Observability (DevOps)]] — the operational-monitoring foundation this extends
- [[ai-ml/03-ai-engineer/03-the-model-landscape|The Model Landscape]] — quantization for LLMs, the same idea
