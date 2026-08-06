# Local & Open Models

**Source:** Part II of the AI-engineer track. [[ai-ml/03-ai-engineer/03-the-model-landscape|The model landscape]] introduced open-weight models and the self-hosted-vs-API tradeoff conceptually; this note is the practical toolkit — actually running a model on your own laptop or server, and when that's the right move. Code is illustrative shape.

## Why run a model yourself at all

The default for building is a hosted API — someone else runs the GPUs, you send tokens. Self-hosting an open-weight model ([[ai-ml/03-ai-engineer/03-the-model-landscape|landscape]]) is worth the extra effort when one of these dominates:
- **Privacy / data residency** — the data legally or contractually can't leave your infrastructure (health, legal, on-prem enterprise). This is the most common real reason.
- **Cost at high, steady volume** — past a certain sustained throughput, owning the hardware (or renting a fixed GPU) beats per-token pricing.
- **Control & no lock-in** — you pin the exact model version forever (hosted models get deprecated and retired out from under you), and you can fine-tune ([[ai-ml/03-ai-engineer/15-fine-tuning-applied|applied fine-tuning]]) freely.
- **Offline / edge** — no network, or latency requirements that a round-trip to a cloud can't meet.

Against all that: you now own the ops (GPUs, scaling, uptime, updates), and the best open models still trail the frontier closed models on the hardest tasks. Most teams should **prototype on an API and self-host only when a concrete driver above forces it** — the same "do you actually need it yet?" judgment as everywhere in this track.

## The two runtimes you'll actually use

### On your own machine — Ollama / LM Studio / llama.cpp
For local development, experimentation, and single-user apps, these make running a model a one-liner:
- **Ollama** — the pragmatic default. `ollama run <model>` pulls a quantized model and serves it behind a local API (often OpenAI-compatible, so your existing SDK code points at `localhost` by changing the base URL). Great for dev, offline work, and privacy-sensitive prototypes.
- **LM Studio** — a GUI over the same idea; nice for browsing/trying models without the terminal.
- **llama.cpp** — the C++ engine underneath much of the above; runs quantized models efficiently on CPU/Apple Silicon/consumer GPUs. Reach for it directly when you want maximum control or to embed inference in an app.

```bash
# The whole "run a real LLM locally" story, roughly:
ollama run llama-3-8b          # pull + serve a quantized model
# then point your app's base URL at http://localhost:11434 (OpenAI-compatible)
```

### On a server, at scale — vLLM / TGI
For production self-hosting that must serve many concurrent users, you need a real **inference server**, not a laptop runtime:
- **vLLM** — the common high-throughput choice. Its headline trick, **PagedAttention**, manages the attention KV-cache like OS virtual memory, packing far more concurrent requests onto a GPU. Also does **continuous batching** — slotting new requests into the batch as others finish instead of waiting for a full batch — which is what keeps a GPU busy and cost-per-token low.
- **TGI (Text Generation Inference)** — Hugging Face's production server, similar goals.

The mental model: *Ollama is for you; vLLM is for your users.*

## Quantization — the thing that makes local possible

A model's weights are numbers. Full precision stores each in 16 bits; a 70-billion-parameter model at 16-bit needs ~140 GB of memory — far beyond a laptop. **Quantization** compresses those numbers to fewer bits (8, 4, sometimes lower), shrinking the model **~2–4×** so it fits on consumer hardware and runs faster, at a **small, usually-acceptable quality cost**. It is the single technique that turns "impossible to run locally" into `ollama run`.

- **Formats you'll see:** **GGUF** (the llama.cpp/Ollama format, CPU-and-GPU friendly — what you download for local runtimes), **AWQ** / **GPTQ** (GPU-oriented quantization common with vLLM).
- **The dial:** lower bits → smaller/faster → more quality loss. **4-bit (Q4)** is the popular sweet spot — big size win, modest quality hit. Drop below 4-bit only when memory forces it.
- **Rule of thumb:** a well-quantized larger model usually beats a smaller full-precision one at the same memory budget — so quantization lets you run a *more capable* model than you otherwise could, not just a smaller one.

## Where to get the models

**Hugging Face** is the hub — the "GitHub of models." You'll find each open model in multiple formats and quantization levels, plus datasets and the libraries (`transformers`) to run them. Licenses vary and *matter*: "open weights" is not automatically "free for commercial use." Check the license before shipping — some restrict commercial use, redistribution, or specific applications.

## How this plugs into the rest of the track

The payoff of an OpenAI-compatible local endpoint is that **almost nothing else changes**: your [[ai-ml/03-ai-engineer/04-calling-models|calling-models]] code, [[ai-ml/03-ai-engineer/11-structured-output|structured output]], [[ai-ml/03-ai-engineer/07-tools-and-mcp|tool calling]], [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG]], and [[ai-ml/03-ai-engineer/12-evals|evals]] all work the same way — you point the base URL at your own server. That portability is exactly why an [[ai-ml/03-ai-engineer/13-reliability-and-plumbing|AI gateway]] and provider-neutral code pay off: swapping a hosted frontier model for a self-hosted open one becomes a config change, and you can even *fall back* between them. Self-hosting is also the prerequisite for running your own LoRA fine-tunes ([[ai-ml/03-ai-engineer/15-fine-tuning-applied|applied fine-tuning]]) with no per-token markup.

## Gotchas

- **Weights ≠ served model.** Downloading a model is step zero; you still need a runtime, enough VRAM, and (for production) a real inference server. "I have the weights" is not "I have an endpoint."
- **VRAM is the wall.** The model, its KV-cache, and concurrency all fight for GPU memory. Quantization buys headroom; underestimating VRAM is the classic first failure.
- **Over-quantizing tanks quality.** Below ~4-bit, degradation gets real and task-dependent. **Eval the quantized model on your actual task** ([[ai-ml/03-ai-engineer/12-evals|evals]]) — don't assume the benchmark numbers for the full-precision version carry over.
- **Licenses bite at ship time.** Confirm commercial-use terms *before* building on a model, not after.
- **Self-hosting is ops you now own.** Uptime, scaling, GPU failures, security patching — all yours. Factor the human cost, not just the GPU bill.

## Key insight

**Open-weight models plus quantization plus the right runtime make self-hosting genuinely practical — `ollama run` on your laptop, vLLM for your users — and an OpenAI-compatible endpoint means the rest of your stack doesn't change.** But self-host on purpose (privacy, steady high volume, control, offline), not by default: you trade the frontier's peak quality and someone-else's-ops for privacy, cost-at-scale, and freedom from lock-in. Quantization is the enabling trick; measuring the quantized model on *your* task is the discipline.

## Related
- [[ai-ml/03-ai-engineer/03-the-model-landscape|The Model Landscape]] — open vs. closed, self-hosted vs. API, in full
- [[ai-ml/03-ai-engineer/15-fine-tuning-applied|Fine-Tuning (Applied)]] — running your own LoRA on open weights
- [[ai-ml/03-ai-engineer/13-reliability-and-plumbing|Reliability & Plumbing]] — gateways make hosted↔self-hosted a config change
- [[ai-ml/03-ai-engineer/14-cost-caching-and-latency|Cost, Caching & Latency]] — when owning the hardware wins on cost
