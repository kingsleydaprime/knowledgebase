# How LLMs Work, Plainly

**[Beginner]** — assumes [[using-ai/01-what-this-thing-is|note 01]]. No maths. The goal is that the model's behaviour stops feeling random and starts feeling *predictable* — because once you can predict it, you can work with it.

## The kid version first

The model plays one game, over and over: **given everything written so far, what word comes next?**

It writes that word down, then reads the whole thing again — including the word it just added — and asks the same question. Again. Again. Until it decides to stop.

That's the whole trick. There is no plan, no outline it's working from, no sentence it's building toward. Every answer you've ever received from an LLM was assembled one guess at a time, left to right, with no ability to go back and revise.

Almost every strength and every weakness in this note falls out of that.

## Why this explains so much

**Why it can't count the letters in a word.** It doesn't see letters. Text gets chopped into chunks called **tokens** — roughly 4 characters each, often a word or a piece of one. "Strawberry" might reach the model as `straw` + `berry`. Asking how many R's are in it is like asking someone to count the letters in a word you spelled out in interpretive dance. Modern models often get it right now, but by working around the problem, not because they can see letters.

**Why the answer gets better when you ask it to explain its reasoning.** Each word it writes becomes part of what it reads for the next word. Reasoning out loud literally gives it more to work with — it's using its own output as scratch paper. "Think it through step by step before answering" is not flattery; it's giving the model room to compute.

**Why it never says "I don't know."** Well — it does, sometimes, when the training text contained people saying that in similar situations. But it has no internal signal that reads *low confidence*. Not knowing feels, mechanically, exactly like knowing. This is the root of the whole verification problem in [[using-ai/06-verifying-what-it-tells-you|note 06]].

**Why you get a different answer the second time.** At each step there isn't one next word, there's a *ranked list* of candidates with probabilities. The model usually picks somewhat randomly among the top ones, because always taking the single likeliest word produces flat, repetitive text. Ask the same question twice, get two different answers — both legitimate. Nothing is broken.

**Why it makes up sources.** A citation is text. A plausible-looking citation is plausible-looking text. Authors, journal names, years, and DOIs all have very learnable shapes, and the model can produce a perfectly-shaped reference to a paper that does not exist. It isn't lying — lying requires knowing the truth.

## The context window — its entire working memory

The model can only look at a fixed amount of text at once. Everything it can see — your instructions, the conversation so far, any file you attached, its own replies — has to fit in that budget, called the **context window**.

Two consequences people constantly trip on:

1. **Anything outside the window doesn't exist to it.** Not "forgotten" — never seen. A fresh chat knows nothing about your last one unless the product deliberately carries something over.
2. **It has no memory of the world after its training finished.** There's a cutoff date. Ask about something recent and you'll get either a refusal, a stale answer, or a confident fabrication — unless the tool searches the web, which some do and some don't. Knowing which one you're using matters.

The window is large in modern tools (a whole book's worth), but "large" isn't "unlimited," and a stuffed window degrades quality — details in the middle get less attention than things at the start or end. [[using-ai/05-context-and-long-chats|Note 05]] is about living with this.

## What it's genuinely good at vs genuinely bad at

The pattern is clearer than people expect. It's strong where *many valid answers exist* and weak where *exactly one answer is correct and must be derived*.

| Genuinely good | Genuinely bad |
|---|---|
| Rephrasing, summarizing, changing tone | Arithmetic on numbers it hasn't seen |
| Drafting from a blank page | Counting things, tracking totals |
| Explaining a concept five different ways | Precise recall of facts, dates, quotes, prices |
| Translating, and explaining the translation | Anything after its training cutoff |
| Structuring messy notes | Knowing what it doesn't know |
| Brainstorming, naming, first-pass ideas | Reasoning about *itself* ("are you sure?") |

That last one deserves a warning. Asking "are you sure?" does not run a check. It just makes agreement-flavoured or apology-flavoured text more likely next. Models will often cave and "correct" a right answer to a wrong one, because a challenge is followed by a concession in most text ever written. To actually test an answer, ask it to *redo* the work, or ask in a fresh chat.

## Key insight

It is a next-word guesser with a fixed-size window and no self-knowledge. Every quirk in this note — the fabricated citation, the changed answer, the miscounted letters, the false apology — is that same machine behaving exactly as designed. None of it is a malfunction, so none of it will be fixed by complaining to it.

## Related
- [[using-ai/01-what-this-thing-is|What This Thing Actually Is]] — the vocabulary
- [[using-ai/04-talking-to-a-model|Talking to a Model]] — turning this mechanism into better prompts
- [[using-ai/05-context-and-long-chats|Context and Long Chats]] — living inside the window
- [[using-ai/06-verifying-what-it-tells-you|Verifying What It Tells You]] — the discipline this note argues for
- [[ai-ml/03-ai-engineer/02-how-llms-work|How LLMs Work]] — the same mechanism with the maths and the API controls, for builders
