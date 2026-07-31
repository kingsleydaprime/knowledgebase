# 03 — AI Engineer

The applied-LLM path: **building products on top of pre-trained models** (mostly LLMs) via APIs — prompting, retrieval, tools, agents — without training models yourself. This is the deep-built track in the domain, and the one that maps to real applied-AI work (AI SDK, MCP, agents). Part of the [[ai-ml/README|AI/ML course]] — see it for how this differs from the [[ai-ml/01-data-scientist/README|Data Scientist]] and [[ai-ml/02-ml-engineer/README|ML Engineer]] paths.

Built by cross-referencing the [roadmap.sh ai-engineer](https://roadmap.sh/ai-engineer) roadmap and folding in the old `01-fundamentals/` notes (nothing dropped). The applied files (calling models, tools/MCP) are genuinely grounded in project work; the rest is a mix of grounded and reference.

## Reading order

1. [[ai-ml/03-ai-engineer/01-the-ai-engineer-role|The AI Engineer Role]] — **[Beginner]** — AI engineer vs ML engineer, the "build on pre-trained models" paradigm, and the choose-the-right-tool decision process
2. [[ai-ml/03-ai-engineer/02-how-llms-work|How LLMs Work]] — **[Beginner → Intermediate]** — tokens, context windows, transformers/attention, autoregression, and the sampling knobs (temperature, top-p/k, penalties) you set on every call
3. [[ai-ml/03-ai-engineer/03-the-model-landscape|The Model Landscape]] — **[Beginner]** — kinds of models, the LLM provider ecosystem, open vs closed/self-hosting, and the AI-tools categories
4. [[ai-ml/03-ai-engineer/04-calling-models|Calling Models]] — **[Intermediate]** — provider APIs, the messages format, SDKs (streaming, structured output, tool calling), and the discipline of a fast-moving toolchain
5. [[ai-ml/03-ai-engineer/05-prompt-engineering|Prompt Engineering]] — **[Beginner → Intermediate]** — system/user/roles, zero/few-shot, chain-of-thought, structured output, and context engineering
6. [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG & Embeddings]] — **[Intermediate → Advanced]** — embeddings, semantic search, the RAG pipeline, vector databases, and RAG vs fine-tuning
7. [[ai-ml/03-ai-engineer/07-tools-and-mcp|Tools & MCP]] — **[Intermediate]** — function/tool calling and the Model Context Protocol (servers, clients, hosts)
8. [[ai-ml/03-ai-engineer/08-agents|Agents]] — **[Advanced]** — the agentic (ReAct) loop, memory, multi-agent systems, frameworks, and observability
9. [[ai-ml/03-ai-engineer/09-multimodal|Multimodal AI]] — **[Intermediate]** — vision input, image generation, speech (STT/TTS), and video
10. [[ai-ml/03-ai-engineer/10-safety-and-production|Safety & Production]] — **[Advanced]** — prompt injection, guardrails, evals, cost, observability — turning a demo into a shipped product

## Practice, not just notes

Same honest caveat as every domain: reading this isn't reps. The reps here are *building* — a RAG system over your own docs, a small MCP server, an agent with real tools, an eval set for a feature. The applied work you already do (AI SDK, MCP) is where this becomes real; these notes are the map.

## Related
- [[ai-ml/README|AI/ML course map]] — the three paths
- [[ai-ml/00-foundations/README|Foundations]] — what a model is, and the (light) math this path needs
- [[ai-automation/README|ai-automation/]] — the no-code angle on applied AI
