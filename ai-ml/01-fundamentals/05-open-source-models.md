# Using Open-Source Models

"Open-source model" usually means the trained weights are published for anyone to download and run — as opposed to a closed model (like most frontier LLMs) that you can only access through an API. This note is about what that choice actually involves practically: where to get them, how to run them, and what you give up or gain versus an API.

## Where open-weight models live

**Hugging Face** is the de facto hub — a combination of GitHub and a package registry for models, datasets, and the libraries (`transformers`, `datasets`) to use them. Almost every notable open-weight model family (Llama, Mistral, Qwen, Gemma, Whisper, Stable Diffusion, and many others) publishes there, along with a model card describing size, license, training data, and intended use.

## Running a model locally

Two very different levels of effort:

- **Ollama** — the easiest on-ramp. `ollama run llama3` downloads and runs a model with one command, exposing a local API compatible with a chat-style interface. Handles quantization and hardware details for you. Good for experimentation and for building things that need a local, private LLM without touching infrastructure.
- **llama.cpp** (and its many wrappers) — a lower-level, highly optimized C/C++ inference engine, the thing Ollama itself is often built on top of. Gives more control over exact settings (context size, quantization level, batching) at the cost of more manual setup.
- **`transformers` (Python library)** — the standard way to load and run a Hugging Face model directly in Python code, useful when you need to integrate a model into a custom pipeline rather than just chat with it.

## Quantization — making big models runnable on normal hardware

A model's weights are normally stored as 16 or 32-bit floating point numbers. Quantization reduces that precision (commonly to 8-bit or 4-bit integers), shrinking the model's memory footprint and speeding up inference, at a small cost to output quality. A 4-bit quantized version of a model can often run on a consumer GPU (or even CPU) where the full-precision version would need many times more memory. This is why you'll see model files named things like `Q4_K_M` or `int8` — a naming convention for which quantization scheme was used, trading off size against fidelity.

## Self-hosting vs API — the actual tradeoff

| | Self-hosted open model | Hosted API (Claude, GPT, etc.) |
|---|---|---|
| Cost model | Upfront hardware/electricity, ~free marginal cost per request | Pay per token, no hardware needed |
| Data privacy | Data never leaves your machine/infra | Data sent to a third party (subject to their policies) |
| Capability | Generally behind the best closed frontier models | Access to the most capable models available |
| Latency/scaling | You manage it — can be a real engineering problem at scale | Handled by the provider |
| Customization | Full control — fine-tune, modify, run offline | Limited to what the API exposes (system prompts, fine-tuning endpoints if offered) |

The practical rule of thumb: reach for a self-hosted open model when data privacy/offline operation is a hard requirement, when request volume is high enough that per-token API cost would dominate, or when you specifically need to fine-tune on private data. Reach for a hosted API when you want the best available capability with no infrastructure to manage — which is the common case for most products, especially early on.

## Fine-tuning open models

Because the weights are yours to modify, open models can be further trained on your own data (see [[04-optimization|optimization]] for the mechanism) to specialize them — a support-ticket classifier fine-tuned on a company's actual tickets, for instance. Full fine-tuning of a large model is expensive; **LoRA** (Low-Rank Adaptation) and similar parameter-efficient methods have become the practical default, training a small number of additional parameters instead of the whole model, making fine-tuning feasible on much more modest hardware.

## Gotchas

- **Licenses vary and matter** — "open-weight" doesn't always mean "open-source" in the traditional sense, and some licenses restrict commercial use or require attribution above a certain scale. Check the specific model's license before shipping a product on it.
- Local models are usually smaller than the frontier closed models for hardware reasons, which shows up as weaker performance on complex reasoning even if they're fine for narrower, well-defined tasks — match model size/capability to the actual task rather than assuming "open-source" implies "as good."
- Quantization quality loss is usually small but not zero — worth actually evaluating output quality at your chosen quantization level rather than assuming it's a free lunch.

## Related
- [[03-llms|llms]]
- [[09-choosing-the-right-ai-tool|choosing-the-right-ai-tool]]
- [[04-optimization|optimization]]
