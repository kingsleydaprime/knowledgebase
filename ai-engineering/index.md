# AI Engineering

## What AI engineering is

**AI engineering is building apps on top of AI models that someone else has already trained, like Claude or GPT.** You don't train the model. You call it from your code, give it the right instructions and information, let it use tools, and check that its answers are good enough to ship.

This subject is **building products on top of pre-trained models** (mostly LLMs) via APIs — prompting, retrieval, tools, agents — without training models yourself. This is the deep-built track in the domain, and the one that maps to real applied-AI work (AI SDK, MCP, agents).

Built by cross-referencing the [roadmap.sh ai-engineer](https://roadmap.sh/ai-engineer) roadmap and folding in the old `01-fundamentals/` notes (nothing dropped). The applied files (calling models, tools/MCP) are genuinely grounded in project work; the rest is a mix of grounded and reference.

## Three subjects, three jobs

Data science, machine learning and AI engineering used to be one subject called "AI & ML". They are three jobs that share some basics, so each is its own subject now.

| Subject | The question it answers | What you produce | Do you train models? |
|---|---|---|---|
| [[data-science/index\|Data Science]] | "What does the data tell us?" | an answer or insight, often a report | sometimes, mostly simpler models |
| [[machine-learning/index\|Machine Learning]] | "How do we build a model and run it reliably in a real product?" | a trained model running as software | **yes** |
| [[ai-engineering/index\|AI Engineering]] | "How do we build a product on top of models others have trained?" | an app that uses models like Claude or GPT | **no**, you use existing ones |

## Reading order

The track is in two parts. **Part I (1–10)** is the core path — everything you need to build an AI feature end to end. **Part II (11–17)** goes deeper on the topics that separate a demo from a shipped product: the reliable-component techniques, the production plumbing, and the depth topics (fine-tuning, self-hosting, voice). Read Part I in order; dip into Part II as you need it.

### Part I — Building

1. [[ai-engineering/01-the-ai-engineer-role|The AI Engineer Role]] — **[Beginner]** — AI engineer vs ML engineer, the "build on pre-trained models" paradigm, and the choose-the-right-tool decision process
2. [[ai-engineering/02-how-llms-work/index|How LLMs Work]] — **[Beginner → Intermediate]** — tokens, context windows, transformers/attention, autoregression, and the sampling knobs (temperature, top-p/k, penalties) you set on every call
3. [[ai-engineering/03-the-model-landscape|The Model Landscape]] — **[Beginner]** — kinds of models, the LLM provider ecosystem, open vs closed/self-hosting, and the AI-tools categories
4. [[ai-engineering/04-calling-models/index|Calling Models]] — **[Intermediate]** — provider APIs, the messages format, SDKs (streaming, structured output, tool calling), and the discipline of a fast-moving toolchain
5. [[ai-engineering/05-prompt-engineering/index|Prompt Engineering]] — **[Beginner → Intermediate]** — system/user/roles, zero/few-shot, chain-of-thought, structured output, and context engineering
6. [[ai-engineering/06-rag-and-embeddings/index|RAG & Embeddings]] — **[Intermediate → Advanced]** — embeddings, semantic search, the RAG pipeline, vector databases, and RAG vs fine-tuning
7. [[ai-engineering/07-tools-and-mcp/index|Tools & MCP]] — **[Intermediate]** — function/tool calling and the Model Context Protocol (servers, clients, hosts)
8. [[ai-engineering/08-agents/index|Agents]] — **[Advanced]** — the agentic (ReAct) loop, memory, multi-agent systems, frameworks, and observability
9. [[ai-engineering/09-multimodal/index|Multimodal AI]] — **[Intermediate]** — vision input, image generation, speech (STT/TTS), and video
10. [[ai-engineering/10-safety-and-production/index|Safety & Production]] — **[Advanced]** — prompt injection, guardrails, evals, cost, observability — turning a demo into a shipped product

### Part II — Depth & Production

11. [[ai-engineering/11-structured-output/index|Structured Output]] — **[Intermediate]** — JSON mode, schema-constrained decoding, and the discipline that turns an LLM into a reliable *function*
12. [[ai-engineering/12-evals/index|Evals]] — **[Intermediate → Advanced]** — the core applied-AI skill: golden datasets, LLM-as-judge (and its biases), offline gates vs online signal, evaluating RAG and agents
13. [[ai-engineering/13-reliability-and-plumbing/index|Reliability & Plumbing]] — **[Intermediate]** — retries/backoff, timeouts, rate limits, fallbacks, and AI gateways: making a flaky network call dependable
14. [[ai-engineering/14-cost-caching-and-latency/index|Cost, Caching & Latency]] — **[Intermediate]** — model routing/cascading, prompt caching (freeze the front), streaming for perceived latency, trimming tokens
15. [[ai-engineering/15-fine-tuning-applied|Fine-Tuning (Applied)]] — **[Advanced]** — when (rarely) to fine-tune, LoRA/PEFT, SFT vs DPO, the dataset-is-the-project reality
16. [[ai-engineering/16-local-and-open-models/index|Local & Open Models]] — **[Intermediate]** — Ollama/vLLM, quantization (GGUF/AWQ), and when self-hosting an open model beats an API
17. [[ai-engineering/17-voice-and-realtime|Voice & Realtime]] — **[Advanced]** — STT→LLM→TTS pipelines vs speech-native models, and the sub-second-latency constraint (streaming, turn-taking, barge-in)

### Part III — Reps

Reading this track isn't reps. The reps are *building*, so the builds are now in the folder rather than left as an exhortation:

18. [[ai-engineering/18-lab-setup|Lab Setup]] — **[Beginner]** — the environment the exercises assume: one key with a spending cap, a cheap model, `usage` printed on every call, and the habit of checking the SDK's version-matched docs instead of your memory
19. [[ai-engineering/19-practice-exercises|Practice Exercises]] — **[Beginner → Advanced]** — fifteen exercises over the whole track, each naming the note it exercises and what "done" looks like. The load-bearing four: build an eval set, build a RAG over your own notes, diagnose its failures as retrieval vs generation, and prompt-inject it
20. [[ai-engineering/20-practice-exercises-solutions|Solutions]] — **[Beginner → Advanced]** — worked answers with code, and the reasoning behind each

Same pattern as [[cybersecurity/02-ethical-hacking/12-practice-exercises|ethical hacking]] and the [[devops/01-linux/15-rhcsa/15-practice-exercises|RHCSA track]]: lab, exercises, solutions. The applied work you already do (AI SDK, MCP) is where this becomes real; these notes are the map, and Part III is the terrain.

## Related
- [[using-ai/index|Using AI]] — the prior course for non-programmers: using LLMs as a *user*. Note 1 below assumes you've either read it or absorbed it by osmosis
- [[machine-learning/index|Machine Learning]] · [[data-science/index|Data Science]] — the two sibling subjects
- [[ai-engineering/projects|Projects]] · [[ai-engineering/interview/index|Interview prep]]
- [[machine-learning/00-foundations/index|Foundations]] — what a model is, and the (light) math this path needs
- [[ai-automation/index|ai-automation/]] — the no-code angle on applied AI
