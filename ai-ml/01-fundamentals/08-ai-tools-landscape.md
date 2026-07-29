# The AI Tools Landscape

A map of the current categories of AI-powered tools, since "AI tool" spans wildly different things under one label. This is about recognizing categories, not endorsing specific products — the specific best-in-class tool in any category changes fast; the categories themselves are more stable.

## Chat assistants (general-purpose)

Conversational interfaces to a general LLM (Claude, ChatGPT, Gemini, and similar) — for open-ended questions, writing, explanation, brainstorming, analysis of pasted text/documents. The common thread: no persistent tool access by default beyond what the specific product bolts on (web search, file upload, code execution sandboxes are increasingly built in, blurring the line with agents — see [[06-agents|agents]]).

## Coding assistants / agentic coding tools

Tools built specifically around a codebase: autocomplete-style inline suggestion (GitHub Copilot's original form), chat-in-the-IDE, or full agentic tools that can read/write files, run commands, and iterate on a task across many steps (Claude Code being one of these — the tool you're using right now is itself in this category). The meaningful axis to evaluate these on is **how much autonomy and tool access they have** — pure autocomplete vs. an agent that can run your test suite and fix its own mistakes are very different tools wearing a similar label.

## Image/video/audio generation

Diffusion-model-based tools (see [[04-other-model-types|other-model-types]]) for generating or editing images, video, and audio/music from text descriptions or reference inputs. Distinct category from chat/coding tools entirely — different underlying architecture, different evaluation criteria (aesthetic quality, prompt adherence, consistency across frames/edits).

## Search / retrieval-augmented tools

Products that combine an LLM with live web search or a private document store, so answers are grounded in retrieved, current sources rather than relying purely on training data — directly addressing the hallucination risk covered in [[03-llms|llms]]. Worth reaching for specifically when currency (news, recent events, prices) or citing a source matters more than pure reasoning ability.

## Embedding/search infrastructure

Not consumer-facing products but the building blocks behind semantic search, recommendation, and RAG systems (see [[04-other-model-types|other-model-types]]) — vector databases and embedding APIs that most people interact with indirectly, through a product built on top of them, rather than directly.

## MLOps / model-serving platforms

Infrastructure for training, deploying, monitoring, and serving models at scale — a different audience (ML engineers building systems) from the consumer-facing categories above. Worth knowing this category exists as a marker for "the practitioner side of AI," separate from "using AI tools as a consumer of them."

## No-code / low-code AI builders

Tools that let non-engineers assemble an agent or automation by connecting an LLM to triggers and actions through a visual interface, rather than writing code — trading flexibility for accessibility. Useful for straightforward automations; tends to hit a ceiling fast for anything requiring custom logic, which is where the coding-assistant category above takes over.

## Why this map matters

Most "which AI tool should I use" confusion comes from comparing across categories that aren't actually competing — a chat assistant and an agentic coding tool solve different problems even though both are "powered by an LLM." Identify the category the task actually falls into first (see [[09-choosing-the-right-ai-tool|choosing-the-right-ai-tool]] for turning this into a decision process), then compare options within that category.

## Related
- [[09-choosing-the-right-ai-tool|choosing-the-right-ai-tool]]
- [[06-agents|agents]]
- [[04-other-model-types|other-model-types]]
