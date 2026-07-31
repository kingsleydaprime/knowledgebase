# Multimodal AI

**Source:** new for the track, from the [roadmap.sh ai-engineer](https://roadmap.sh/ai-engineer) multimodal branch. **[reference]**

"Multimodal" means working with more than text — images, audio, video — either as input a model understands or as output a model generates. For an AI engineer these are mostly more API calls in the same shape as [[ai-ml/03-ai-engineer/04-calling-models|text calls]], so this is a capability map more than a deep dive.

## Vision — images as input

Modern frontier LLMs are **vision-capable**: you send an image alongside text and the model reasons over both — describe a photo, extract text/data from a screenshot or document (OCR-plus-understanding), answer questions about a chart, debug a UI from a screenshot. Practically it's the same [[ai-ml/03-ai-engineer/04-calling-models|messages call]] with an image part in the content. Extremely useful for document/data extraction pipelines where the source is a PDF or scan rather than clean text.

## Image generation — images as output

Driven by **diffusion models** ([[ai-ml/03-ai-engineer/03-the-model-landscape|the model landscape]]): text prompt → generated image, by starting from noise and repeatedly denoising toward something matching the prompt.

- **Hosted**: DALL·E, Google Imagen, Midjourney — API or product, no infrastructure.
- **Open**: Stable Diffusion / Flux — run locally, fully customizable (LoRAs, ControlNet for pose/layout control), the open-weights [[ai-ml/03-ai-engineer/03-the-model-landscape|self-host vs API]] tradeoff again.

Evaluation criteria differ entirely from text — aesthetic quality, prompt adherence, consistency across edits — and prompting images is its own skill.

## Audio

- **Speech-to-text (ASR)** — audio in, transcript out. **Whisper** (OpenAI, open-weight) is the well-known one; the backbone of transcription, voice interfaces, and meeting/podcast pipelines.
- **Text-to-speech (TTS)** — text in, synthesized (increasingly natural, voice-cloneable) speech out.
- Together they enable **voice agents** — STT → [[ai-ml/03-ai-engineer/08-agents|LLM/agent]] → TTS — a full spoken loop.

## Video

The newest, fastest-moving frontier: text/image → generated video (Sora-style), and video *understanding* (reasoning over frames). Powerful but less mature; treat capabilities and limits as a moving target and verify current state before relying on it.

## The practical framing

For most AI-engineering work, multimodal = **pick a model that supports the modality and call it like any other model** ([[ai-ml/03-ai-engineer/04-calling-models|calling models]]). The engineering interest is usually in the *pipeline* around it — feed a scanned document to a vision model, extract structured data ([[ai-ml/03-ai-engineer/04-calling-models|structured output]]), act on it — rather than the model internals. The same [[ai-ml/03-ai-engineer/10-safety-and-production|safety]] and cost concerns apply, sometimes more sharply (image/video generation raises extra content-moderation and provenance/deepfake questions).

## Related
- [[ai-ml/03-ai-engineer/03-the-model-landscape|The Model Landscape]] — diffusion and speech models as types
- [[ai-ml/03-ai-engineer/04-calling-models|Calling Models]] — multimodal is the same call shape with more content types
- [[ai-ml/02-ml-engineer/06-computer-vision/README|Computer Vision (ML-engineer)]] — the training-side view of vision models
