# Context and Long Chats

**[Beginner]** — assumes [[using-ai/02-how-llms-work-plainly|note 02]]'s context window. This note is about the habits that follow from it: attachments, memory, projects, and when to walk away from a conversation.

## The kid version first

Picture a whiteboard. Everything the model can see — your instructions, the whole conversation, any file you attached, its own replies — is written on that whiteboard. Nothing else exists to it.

The whiteboard is big, but finite. When it fills, things start falling off the edge or getting crowded out. And when you open a new chat, you get a **blank whiteboard** — not the same assistant with a memory of yesterday.

Most confusing LLM behaviour is really whiteboard behaviour.

## Give it the source material

The highest-leverage habit in this entire course: **stop asking from memory, start asking from documents.**

Instead of "what does UK employment law say about notice periods," attach your actual contract and ask what *it* says. Instead of "summarize the arguments about X," paste the three articles you care about.

Why it works so well:

- It removes the fabrication problem at the root. The model isn't recalling, it's reading.
- It can quote, and you can check the quote against the text in front of you.
- It's the same mechanism serious AI products are built on (they call it retrieval — see [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG]]), except you're doing the retrieval by hand, which for a handful of documents is better anyway.

Caveats worth knowing: scanned PDFs may come through garbled or not at all; very long documents may be read in pieces, so "summarize this 300-page report" is weaker than asking about specific sections; and spreadsheets are read as text, so it can misread numbers it "sees" perfectly well.

## Why long chats get worse

A conversation that's been running for two hours tends to drift — vaguer answers, forgotten instructions, repeated suggestions, contradictions with things it said earlier. This is not fatigue. It's crowding:

- Early instructions are now buried under thousands of words of transcript.
- Its own earlier answers are now context, so mistakes get reinforced — it read them and treats them as established.
- Once the window is genuinely full, the oldest turns are dropped or compressed. It isn't ignoring your original brief; the brief is gone.

**The fix is almost always a new chat.** Start fresh, paste in only the bit that mattered — the final version of the document, the three decisions you've made — and continue. This feels wasteful the first few times. It isn't. A clean whiteboard with 200 good words on it beats a crowded one with 20,000 mediocre ones.

Rule of thumb: **when it starts repeating itself or losing the thread, that's the signal.** Don't fight it for another twenty messages.

## One chat, one job

Related habit: keep separate topics in separate conversations. A thread where you've been debugging a spreadsheet, planning a holiday, and drafting a resignation letter has all three sitting in the window, competing. Answers bleed between them in ways that are hard to spot.

## Memory and projects

Most assistants now offer two things that survive across chats. Worth understanding the difference:

| Feature | What it is | Use it for |
|---|---|---|
| **Memory** | The tool saves facts about you and quietly injects them into future chats | Standing preferences: your job, how you like answers formatted |
| **Projects / custom instructions** | A named space with its own files and standing instructions | An ongoing piece of work with its own documents and rules |

Both are genuinely useful, and both are worth auditing occasionally. Memory in particular accumulates: a stray comment becomes a permanent belief about you, and then it's quietly shaping answers months later. Every tool that has memory has a screen where you can read and delete what it stored. Look at it once in a while — people are routinely surprised.

Memory is also a privacy surface, since you're choosing to persist things. That's [[using-ai/07-privacy-and-what-not-to-share|note 07]].

## The habits, compressed

- Attach the source rather than asking from memory.
- One conversation per topic.
- When it drifts, start fresh and carry over a summary.
- Keep your own good prompts somewhere — a note file is fine. You'll reuse them more than you expect.
- Save the *output* you care about outside the chat. Chat histories get lost, cleared, and reorganised by product updates.

## Key insight

You are not talking to something that remembers you. You're filling a whiteboard, and you control what's on it. Nearly every complaint about an assistant "getting worse" or "forgetting" is a whiteboard that needed wiping.

## Related
- [[using-ai/02-how-llms-work-plainly|How LLMs Work, Plainly]] — where the context window comes from
- [[using-ai/04-talking-to-a-model|Talking to a Model]] — what to put on the whiteboard
- [[using-ai/07-privacy-and-what-not-to-share|Privacy and What Not to Share]] — the flip side of uploading everything
- [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG & Embeddings]] — automating "give it the source material," for builders
