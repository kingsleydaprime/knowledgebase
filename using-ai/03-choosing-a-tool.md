# Choosing a Tool

**[Beginner]** — assumes notes 01–02. The one note here with a shelf life: **specific products and prices change every few months, the categories don't.** Learn the categories; check the current details yourself.

## The kid version first

"AI" isn't one product any more than "engine" is one vehicle. A chatbot, a research tool, an image generator and a coding assistant may all run on the same underlying model, but they're wrapped differently, and the wrapper is most of what you experience.

Pick by **what you're trying to produce**, not by which brand you've heard of most.

## The categories

| Category | Use it when | Watch out for |
|---|---|---|
| **General chat assistant** (ChatGPT, Claude, Gemini, Copilot) | Drafting, explaining, summarizing, thinking out loud — 80% of everyday use | Confident wrongness on facts; check whether it's searching the web or answering from memory |
| **Search-grounded answering** (Perplexity, the "search" toggle in most chat tools) | You need something current, or you want links to check | Cites real pages but can still misread them — click through |
| **Deep research** (a mode in most major assistants) | You want a long, sourced report and can wait 5–30 minutes | Long output feels authoritative; it's still worth spot-checking. Usually a paid feature |
| **Document / notebook tools** (NotebookLM and similar) | You have *your own* sources and want answers grounded only in them | Won't know anything outside what you gave it — that's the point |
| **Image generation** | Illustration, mockups, concept visuals | Text inside images, hands, precise layout; and the licensing question for commercial use |
| **Voice / realtime** | Hands-free, practising a language, transcription | Transcription errors compound silently into whatever comes next |
| **Coding assistants** (Cursor, Copilot, Claude Code) | Writing or changing code | A different course — see the hand-off at the end |
| **Automation platforms** (n8n, Zapier, Make) | The *same* AI task, repeatedly, without you present | Real engineering; see [[ai-automation/README\|ai-automation/]] |

## How to actually choose, in three questions

**1. Does the answer need to be current?**
If yes, you need a tool that searches — or you need to paste the source in yourself. A model answering from memory has a training cutoff and will not tell you when it's past it.

**2. Do you have the source material, or do you need it found?**
If you *have* it (a contract, a syllabus, ten PDFs), upload it and ask questions against it. Grounding the model in real text is the single biggest quality upgrade available to a beginner, and it costs nothing.
If you *need* it found, use a search-grounded tool and follow the links.

**3. Is this once, or every week?**
Once → a chat. Every week → save it as a reusable prompt or a project; if it's every day and unattended, it's an automation problem, not a chat problem.

## Free vs paid — what the money actually buys

Roughly, and consistently across providers:

- **A stronger default model.** The free tier usually runs a smaller, faster model, or downgrades you to one after a few messages. This is the real difference, and it's larger than most people assume — much "AI is overrated" experience is free-tier experience.
- **Higher limits.** More messages, bigger uploads, longer documents.
- **The advanced features.** Deep research, better voice, image generation, projects/memory, coding agents.

Two habits worth having regardless of tier: **notice which model you're actually talking to** (the switcher is usually one click, and tools quietly downgrade you when busy), and **try the same prompt in two different assistants** when something matters. They fail differently, and disagreement between them is a useful alarm.

## Don't over-commit early

You do not need a subscription to start. Free tiers of two or three assistants, used for a fortnight on real tasks, will tell you more about which one suits you than any comparison article — including this one. The models leapfrog each other every few months, so "which is best" is a question with a shelf life of about a quarter; "which one fits how I work" is more stable.

## Key insight

Match the tool to the *shape of the output* you want, then ask whether the answer needs to be current and whether you already hold the source material. Those three questions resolve almost every "which AI should I use" question without knowing a single benchmark score.

## Related
- [[using-ai/05-context-and-long-chats|Context and Long Chats]] — uploading your own sources, and why it helps so much
- [[using-ai/06-verifying-what-it-tells-you|Verifying What It Tells You]] — what to do with a sourced answer
- [[ai-ml/03-ai-engineer/03-the-model-landscape|The Model Landscape]] — the same landscape from the builder's side: providers, open vs closed, self-hosting
- [[ai-automation/README|AI Automation]] — when the task should run without you
