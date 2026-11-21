# AI Engineering — Projects

_Building products on top of models others have trained. These need no maths and ship fast._

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

## Projects

_Your strongest applied area (AI SDK / MCP). These produce shippable, demoable products — high portfolio value._

- 🟢 ⭐ **RAG over this vault** — a chatbot that answers questions about _this knowledgebase_: chunk the markdown, embed it, store in [[ai-engineering/06-rag-and-embeddings/index|pgvector/Chroma]], retrieve + answer with citations. Dogfoods your own notes and is a perfect [[ai-engineering/06-rag-and-embeddings/index|RAG]] project.
- 🟡 **Build an MCP server** — wrap a real system (your notes, a database, an API) as an [[ai-engineering/07-tools-and-mcp/index|MCP server]] with tools + resources, and use it from an MCP host. You already _use_ MCP — building one closes the loop.
- 🟡 **An agent with real tools + an eval set** — an [[ai-engineering/08-agents/index|agent]] (via the AI SDK's agent loop) that does a multi-step task with 2–3 tools, plus an [[ai-engineering/10-safety-and-production/index|eval set]] measuring success rate as you change the prompt/model. The evals are what make it engineering, not a demo.
- 🟡 **Structured extraction pipeline** — feed scanned docs/receipts to a [[ai-engineering/09-multimodal/index|vision model]], extract typed JSON with [[ai-engineering/04-calling-models/index|structured output]], validate against a schema. A genuinely useful, sellable tool.
- 🟢 **Model bake-off via OpenRouter** — same prompt/eval set across 5 models through [[ai-engineering/03-the-model-landscape|OpenRouter]], compare quality/latency/cost. Cheap, fast, and teaches model selection.
- 🔴 **Prompt-injection red-team** — build a small agent, then try to break it (direct + indirect [[ai-engineering/10-safety-and-production/index|injection]]); document what worked and the mitigations. Rare, valuable security-adjacent signal.

## If you only do one

**RAG over this vault.** It dogfoods your own notes, it's the single most transferable AI-engineering pattern, and the retrieval quality problem it exposes is the real lesson.

**And if you want the layer underneath it:** [[build-your-own-shit/24-your-own-llm|build your own LLM]] — a transformer trained from scratch, the sequel to [[build-your-own-shit/10-your-own-neural-network|the neural network guide]]. Attention, tokenisation, temperature and the KV cache stop being API parameters.

## Related

- [[ai-engineering/index|AI Engineering]] · [[ai-engineering/interview/index|interview bank]]
- [[ai-engineering/19-practice-exercises|AI engineer exercises]]
- [[machine-learning/projects|Machine Learning projects]] · [[data-science/projects|Data Science projects]]
- [[project-ideas|Project Ideas]] — the vault-wide index
