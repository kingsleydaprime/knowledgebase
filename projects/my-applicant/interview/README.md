# my-applicant — Interview Questions

Questions an interviewer could realistically ask **about this project**, drawn from
[`../learning/`](../learning/). This project is unusually good interview material because it's an
*agentic* system that takes irreversible actions on your behalf — which is exactly the design
problem every company building with LLMs is currently arguing about internally.

## How to use this

- **Answer out loud, from memory, before reading the hint.**
- **Strong answer covers** = the checklist a good answer hits, not a script.
- **[Beginner] / [Intermediate] / [Advanced]** = how much project context the question assumes.
- 🔥 = most likely to be asked.

## Files

| File | Covers |
|---|---|
| [01-pipeline-and-system-design.md](01-pipeline-and-system-design.md) | Stage costs, idempotency, dedupe keys, autonomy tiering, degradation, retries |
| [02-ai-and-llm-engineering.md](02-ai-and-llm-engineering.md) | BYOK, provider abstraction, AI SDK v7, structured output, batching, `verify()` |
| [03-judgement-and-story.md](03-judgement-and-story.md) | The ethics question you *will* be asked, trade-offs, shell/tooling habits, behavioural |

---

## Before anything else: the 60-second pitch

> A pipeline that discovers jobs across multiple sources, filters and scores them, tailors a
> résumé per job, and then either submits or queues for review — designed to run unattended at 3am.
> It's bring-your-own-key: the config names an environment variable, never holds a secret, so it
> works against Claude, OpenAI, Google, OpenRouter or a local Ollama with a one-line change. The
> two design ideas I'd defend hardest: stages are ordered cheapest-first so free local filtering
> shrinks what the expensive model call ever sees, and anything the model generates gets
> **mechanically verified against my actual profile** before it can reach an application — because
> a prompt saying "don't invent skills" is a request, and a fabricated line on a résumé is
> something I'd have to defend in an interview.

The last clause is the whole pitch. Lead with the guardrail, not the automation.

---

## The one question to over-prepare

> *"You built a bot that applies to jobs for you. Isn't that spam?"*

You will get this. It is not hostile — it's a test of whether you thought about it. The answer
lives in [03-judgement-and-story.md](03-judgement-and-story.md), Q1. Do not improvise it.
