# Using AI

**A course for someone who has never seriously used an LLM — and doesn't write code.** Eight notes, readable in an evening, about *using* these tools well: what they are, why they behave as they do, how to brief them, how to check them, and what not to hand them.

This is the on-ramp to the rest of the vault's AI material. Everything under [[ai-ml/README|ai-ml/]] assumes you're going to **build** with models — APIs, retrieval, agents, evals. This folder assumes you're going to **use** them, from a text box, for real work. No maths, no code, no jargon that isn't defined on the spot.

If you already program and want to build AI features, skip this and start at [[ai-ml/03-ai-engineer/README|03-ai-engineer/]].

## Reading order

Read 01–06 in order — each leans on the one before. 07 and 08 can be read any time and probably should be read early if you're using these tools at work.

1. [[using-ai/01-what-this-thing-is|What This Thing Actually Is]] — **[Beginner]** — AI vs machine learning vs deep learning, what a "model" is, training vs use, and why "narrow AI" is all that exists
2. [[using-ai/02-how-llms-work-plainly|How LLMs Work, Plainly]] — **[Beginner]** — next-word prediction, tokens, the context window, and why that explains the miscounting, the made-up citations, and the different answer every time
3. [[using-ai/03-choosing-a-tool|Choosing a Tool]] — **[Beginner]** — chat vs search-grounded vs deep research vs document tools vs image vs voice; free vs paid; the three questions that pick one
4. [[using-ai/04-talking-to-a-model|Talking to a Model]] — **[Beginner]** — prompting as briefing: task, context, format, audience. The six techniques that matter, and the folklore that doesn't
5. [[using-ai/05-context-and-long-chats|Context and Long Chats]] — **[Beginner]** — attach the source instead of asking from memory; why long chats degrade; memory and projects; when to start fresh
6. [[using-ai/06-verifying-what-it-tells-you|Verifying What It Tells You]] — **[Beginner, load-bearing]** — the most important note here. Why confidence tells you nothing, what to check hardest, and why "are you sure?" isn't a check
7. [[using-ai/07-privacy-and-what-not-to-share|Privacy and What Not to Share]] — **[Beginner]** — what happens to what you type, the redaction habit, and the work/client rules
8. [[using-ai/08-living-with-it|Living With It]] — **[Beginner]** — where it earns its place, skill atrophy, disclosure norms, and where to go next

## If you only take three things

1. **It's a next-word guesser, not a knower.** Every quirk follows from that ([[using-ai/02-how-llms-work-plainly|02]]).
2. **Give it the source material.** Attaching your document beats asking from its memory, every time ([[using-ai/05-context-and-long-chats|05]]).
3. **Ask "would I notice if this were wrong?"** — and if not, go and check outside the chat ([[using-ai/06-verifying-what-it-tells-you|06]]).

## Practice, not just notes

Same caveat as every course here: reading isn't reps. The reps are using it on something real — a document you actually need summarized, a letter you actually need to write, a topic you actually want explained. Do that for a fortnight and re-read note 06; it'll land differently once you've been confidently misled once.

## Planned

A parallel track for **technical users who don't yet build with AI** — coding assistants and agentic editors, AI-assisted debugging and code review, what to let an agent touch, and reviewing generated code you didn't write. Not written yet; it slots between this folder and [[ai-ml/03-ai-engineer/README|03-ai-engineer/]].

## Related
- [[ai-ml/README|AI & ML]] — the three builder paths (data scientist, ML engineer, AI engineer)
- [[ai-ml/03-ai-engineer/README|AI Engineer track]] — the direct next step for anyone who writes code
- [[ai-automation/README|AI Automation]] — when the task should run on a schedule without you
- [[README|Vault index]]
