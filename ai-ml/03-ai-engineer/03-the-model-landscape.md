# The Model Landscape

**Source:** folds three old `01-fundamentals/` notes — `04-other-model-types`, `05-open-source-models`, and `08-ai-tools-landscape` — into one landscape, plus the current LLM-provider map ([roadmap.sh ai-engineer](https://roadmap.sh/ai-engineer)). An AI engineer's core skill here is *choosing a model*, so the landscape matters more than any one product.

## The wider tree — kinds of models

LLMs dominate the conversation but are one branch. Recognizing what *kind* of model a problem needs is the first filter ([[ai-ml/03-ai-engineer/01-the-ai-engineer-role|the decision process]]):

- **LLMs** — text in, text out. The AI engineer's main tool.
- **Embedding models** — input → a vector capturing *meaning*, so similar inputs get similar vectors. Not for generating; for **comparison and search** — the engine behind semantic search and [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG]].
- **Diffusion / generation models** — text → new image/video/audio (Stable Diffusion, Midjourney, Sora-style). Different architecture from LLMs entirely (denoising, not next-token) — covered under [[ai-ml/03-ai-engineer/09-multimodal|multimodal]].
- **Speech models** — speech-to-text (Whisper) and text-to-speech.
- **Vision models** — image classification/detection/segmentation.
- **Classic ML / RL** — regression, trees, clustering, reinforcement learning. Mostly [[ai-ml/02-ml-engineer/README|ML-engineer]] territory, but worth recognizing (a gradient-boosted tree often beats an LLM on structured/tabular data, cheaper and faster).

## LLM providers — closed (API) models

The frontier closed models, accessed only via API:

| Provider | Models | Notes |
|---|---|---|
| **Anthropic** | Claude | strong reasoning, long context, tool use, coding |
| **OpenAI** | GPT / o-series | broad ecosystem, function calling, the reference API shape |
| **Google** | Gemini | strong multimodal, huge context |
| **others** | Cohere, Mistral (also open), DeepSeek, xAI Grok | varied strengths/pricing |

Closed models give you the **best available capability with zero infrastructure** — the common default. You trade control and data-locality for that.

**Gateways / aggregators** — rather than integrate each provider separately, a gateway fronts many of them behind **one API and one key**, so you reach dozens of models (open *and* closed) with a `provider/model` string and can swap or fall back between them:

- **OpenRouter** — the popular independent aggregator: one API keying into hundreds of models across all major providers (and many open ones), with unified billing and automatic fallback/routing. The fastest way to try many models, compare them, or avoid lock-in to a single provider's SDK.
- **Vercel AI Gateway** — the same idea, tightly integrated with the AI SDK ([[ai-ml/03-ai-engineer/04-calling-models|calling models]]).

Gateways add a small latency/markup hop but massively simplify multi-model work — genuinely useful early on and for model comparison.

## Open-weight models

"Open" usually means the trained **weights are published** to download and run yourself — as opposed to API-only closed models.

- **Where they live:** **Hugging Face** is the de-facto hub — GitHub-plus-registry for models, datasets, and the `transformers`/`datasets` libraries. Llama, Mistral, Qwen, Gemma, Whisper, Stable Diffusion all publish there, each with a model card (size, license, training data, intended use).
- **Running one locally:** **Ollama** (`ollama run llama3` — the easiest on-ramp, handles quantization/hardware, exposes a local API), **llama.cpp** (the lower-level optimized engine Ollama often sits on), **LM Studio** (a GUI), or the **`transformers`** Python library for custom pipelines. For **serving open models at scale** (high-throughput, multi-user, GPU), **vLLM** is the standard inference server — far faster than Ollama for concurrent load, and it exposes an OpenAI-compatible API so app code barely changes.
- **Quantization** — weights are normally 16/32-bit floats; quantization drops precision (8-bit, 4-bit) to shrink memory and speed inference at a small quality cost. A 4-bit model can run on a consumer GPU/CPU where full precision couldn't — hence filenames like `Q4_K_M`. Evaluate quality at your chosen level rather than assuming it's free.
- **Fine-tuning** — since the weights are yours, you can specialize an open model on your data. Full fine-tuning is expensive; **LoRA** and parameter-efficient methods (train a small number of extra parameters) are the practical default.

## Self-hosted vs API — the tradeoff

| | Self-hosted open model | Hosted API |
|---|---|---|
| Cost | upfront hardware, ~free per request | pay per token, no hardware |
| Data privacy | never leaves your infra | sent to a third party |
| Capability | usually behind frontier closed models | best available |
| Ops | you manage scaling/latency | provider handles it |
| Customization | full — fine-tune, modify, run offline | limited to what the API exposes |

Rule of thumb: **self-host when privacy/offline is a hard requirement, volume makes per-token cost dominate, or you must fine-tune on private data; use an API otherwise** — which is most products, especially early.

**Licenses matter:** "open-weight" ≠ "open-source." Some licenses restrict commercial use or require attribution above a scale. Check before shipping.

## The AI-tools landscape (products, not models)

"AI tool" spans wildly different categories that aren't actually competing — identify the category before comparing options within it:

- **Chat assistants** (Claude, ChatGPT, Gemini) — general conversational LLM access.
- **Coding assistants / agentic coding tools** (Copilot, Cursor, Claude Code) — evaluate on *how much autonomy/tool access* they have, from autocomplete to a full [[ai-ml/03-ai-engineer/08-agents|agent]] that runs your tests.
- **Image/video/audio generation** — diffusion-based, different evaluation criteria entirely.
- **Search/RAG tools** — LLM + live search or a document store, grounding answers in sources.
- **Embedding/vector infrastructure** — the building blocks behind semantic search and RAG (usually used indirectly).
- **MLOps/serving platforms** — the practitioner side ([[ai-ml/02-ml-engineer/README|ML engineer]] audience).
- **No-code/low-code AI builders** — visual agent/automation assembly ([[ai-automation/README|ai-automation]]); accessible, hits a ceiling fast for custom logic.

## Related
- [[ai-ml/03-ai-engineer/01-the-ai-engineer-role|The AI Engineer Role]] — the decision process for picking from this landscape
- [[ai-ml/03-ai-engineer/04-calling-models|Calling Models]] — actually invoking these via APIs/SDKs
- [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG & Embeddings]] — where embedding models earn their place
