---
id: 0962e8de-43c6-4f93-ab35-3f58b16555f8
---

# Choosing a Tool

Choosing a tool means picking the right kind of AI product for the job you have, such as a chatbot, a research tool, an image maker or a coding helper. Many of them run on the same model underneath but are built for different jobs. Specific products and prices change often, so this lesson teaches the kinds of tool.

## The kid version first
<!-- bite: 34047b57-b2f4-48c7-bcdc-426828463d2c -->

"AI" isn't one product any more than "engine" is one vehicle. A chatbot, a research tool, an image generator and a coding assistant may all run on the same underlying model, but they're wrapped differently, and the wrapper is most of what you experience.

Pick by **what you're trying to produce**, not by which brand you've heard of most.

## The categories
<!-- bite: b21e9802-9cc0-4a3a-b90c-925fb9a4742e -->

| Category | Use it when | Watch out for |
|---|---|---|
| **General chat assistant** (ChatGPT, Claude, Gemini, Copilot) | Drafting, explaining, summarizing, thinking out loud — 80% of everyday use | Confident wrongness on facts; check whether it's searching the web or answering from memory |
| **Search-grounded answering** (Perplexity, the "search" toggle in most chat tools) | You need something current, or you want links to check | Cites real pages but can still misread them — click through |
| **Deep research** (a mode in most major assistants) | You want a long, sourced report and can wait 5–30 minutes | Long output feels authoritative; it's still worth spot-checking. Usually a paid feature |
| **Document / notebook tools** (NotebookLM and similar) | You have *your own* sources and want answers grounded only in them | Won't know anything outside what you gave it — that's the point |
| **Image generation** | Illustration, mockups, concept visuals | Text inside images, hands, precise layout; and the licensing question for commercial use |
| **Voice / realtime** | Hands-free, practising a language, transcription | Transcription errors compound silently into whatever comes next |
| **Coding assistants** (Cursor, Copilot, Claude Code) | Writing or changing code | A different course — see the hand-off at the end |
| **Automation platforms** (n8n, Zapier, Make) | The *same* AI task, repeatedly, without you present | Real engineering; see [[ai-automation/index\|ai-automation/]] |

## How to actually choose, in three questions
<!-- bite: cbdede8e-d70d-409c-b8f9-807065420f91 -->

**1. Does the answer need to be current?**
If yes, you need a tool that searches — or you need to paste the source in yourself. A model answering from memory has a training cutoff and will not tell you when it's past it.

**2. Do you have the source material, or do you need it found?**
If you *have* it (a contract, a syllabus, ten PDFs), upload it and ask questions against it. Grounding the model in real text is the single biggest quality upgrade available to a beginner, and it costs nothing.
If you *need* it found, use a search-grounded tool and follow the links.

**3. Is this once, or every week?**
Once → a chat. Every week → save it as a reusable prompt or a project; if it's every day and unattended, it's an automation problem, not a chat problem.

## Free vs paid — what the money actually buys
<!-- bite: 467a9c58-23e1-4165-a68b-8d3049dbe780 -->

Roughly, and consistently across providers:

- **A stronger default model.** The free tier usually runs a smaller, faster model, or downgrades you to one after a few messages. This is the real difference, and it's larger than most people assume — much "AI is overrated" experience is free-tier experience.
- **Higher limits.** More messages, bigger uploads, longer documents.
- **The advanced features.** Deep research, better voice, image generation, projects/memory, coding agents.

Two habits worth having regardless of tier: **notice which model you're actually talking to** (the switcher is usually one click, and tools quietly downgrade you when busy), and **try the same prompt in two different assistants** when something matters. They fail differently, and disagreement between them is a useful alarm.

## Don't over-commit early
<!-- bite: d52b63bf-dc89-4c1a-b386-18852e6260d0 -->

You do not need a subscription to start. Free tiers of two or three assistants, used for a fortnight on real tasks, will tell you more about which one suits you than any comparison article — including this one. The models leapfrog each other every few months, so "which is best" is a question with a shelf life of about a quarter; "which one fits how I work" is more stable.

## Key insight
<!-- bite: 9ccd6b90-9432-4f90-b233-1558acf0f19f -->

Match the tool to the *shape of the output* you want, then ask whether the answer needs to be current and whether you already hold the source material. Those three questions resolve almost every "which AI should I use" question without knowing a single benchmark score.

## Related
<!-- bite: 9088d87a-b06a-4e54-992b-63ab7cac9a10 -->
- [[using-ai/05-context-and-long-chats|Context and Long Chats]] — uploading your own sources, and why it helps so much
- [[using-ai/06-verifying-what-it-tells-you|Verifying What It Tells You]] — what to do with a sourced answer
- [[ai-ml/03-ai-engineer/03-the-model-landscape|The Model Landscape]] — the same landscape from the builder's side: providers, open vs closed, self-hosting
- [[ai-automation/index|AI Automation]] — when the task should run without you

## About this lesson
<!-- bite: 434f5692-7593-4929-b131-eb8498570672 -->

**Level:** Beginner. **Covers:** assumes notes 01–02. The one note here with a shelf life: **specific products and prices change every few months, the categories don't.** Learn the categories; check the current details yourself.
