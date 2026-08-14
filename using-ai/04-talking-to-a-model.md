# Talking to a Model

**[Beginner]** — assumes [[using-ai/02-how-llms-work-plainly|note 02]]. This is "prompt engineering," minus the mystique. You have a text box, not an API — everything here works in one.

## The kid version first

Imagine briefing a talented freelancer who starts work the instant you stop talking, never asks a clarifying question, and cannot see your screen, your company, or your last email.

They'll do *something* regardless of how vague you were. The quality of what you get back is mostly the quality of the brief.

That's it. Prompting isn't magic words. It's briefing.

## The four things a good brief contains

Most weak prompts are missing one of these. Most strong prompts are just an ordinary sentence with all four.

| Element | The question it answers | Example |
|---|---|---|
| **Task** | What do you want done? | "Rewrite this email" |
| **Context** | What do you need to know first? | "It's to a client who missed two deadlines; I want to keep the relationship" |
| **Format** | What should the output look like? | "Under 150 words, no bullet points, warm but direct" |
| **Audience** | Who reads it? | "She's technical, senior, and dislikes padding" |

Compare:

> *Make this email better.*

> *Rewrite this email to a client who's missed two deadlines. I want to be direct about the impact without damaging the relationship — we want to keep working with them. Under 150 words, plain prose, no bullet points. She's senior and dislikes padding.*

Same effort, roughly. Wildly different output. Nothing clever happened — the second one simply removed the guessing.

## The techniques worth knowing (there are only about six)

**Show an example.** Describing a format abstractly is harder than demonstrating it. Paste one instance of the output you want — one summarized meeting note, one rewritten headline — and say "like this." Pattern-matching is what the machine is built for, so this is disproportionately effective.

**Ask for reasoning on hard things.** "Work through it step by step before giving the answer." As [[using-ai/02-how-llms-work-plainly|note 02]] explains, its own words are its scratch paper. Skip this on simple tasks — it just makes them longer.

**Give it a role, lightly.** "You're an experienced GP explaining this to a worried patient" shifts vocabulary and framing usefully. Don't overinvest: it changes *tone and register*, it does not install expertise. A role prompt cannot make a model know something it doesn't.

**Ask it to interview you.** Genuinely underused and the best single tip for a beginner:

> *Before you write anything, ask me the five questions you most need answered to do this well.*

It flips the dynamic from "guess what I want" to a briefing conversation. Particularly good for writing tasks, planning, and anything personal to your situation.

**Iterate instead of restarting.** Your first prompt is a first draft. Say what's wrong — "too formal," "you invented a detail in paragraph two, drop it," "keep the structure but halve the length." Steering beats rewriting the whole prompt from scratch.

**Ask for options.** "Give me three versions with different tones" costs you one message and gives you something to react to. Reacting is much easier than specifying.

## What doesn't work

- **Politeness as leverage.** Please and thank you are fine — they're not doing any work. (Being *specific* is doing all of it.)
- **Threats, urgency, fake stakes.** "This is critical for my career" is folklore. Skip it.
- **Insisting harder.** If it can't do something — current events without search, reliable arithmetic, knowledge of your private files — no phrasing fixes it. That's a wrong-tool problem ([[using-ai/03-choosing-a-tool|note 03]]).
- **"Are you sure?"** as a check. It tests nothing; it just makes a concession more likely. To really test an answer, ask it to redo the work, or ask again in a fresh chat.
- **One giant prompt with fifteen requirements.** Long stuffed instructions reliably drop several. Break it into steps.

## Failure modes → the actual fix

| What happened | Why | Fix |
|---|---|---|
| Bland, generic output | Nothing to condition on | Add context and audience; give an example |
| Ignored half your instructions | Too many at once | Split into two messages |
| Confidently wrong facts | It's guessing from memory | Give it the source, or use a searching tool |
| Wrong tone | You didn't specify one | Name the tone, or paste something in the voice you want |
| Weirdly formal, lots of "Certainly!" | Default assistant register | "Drop the preamble, answer directly" |
| It agreed with something you know is wrong | Agreement is the likeliest next text | Ask it to argue the opposite case |

That last row is worth internalising. These systems lean agreeable. If you want a real critique, you have to ask for one explicitly — *"what's the strongest objection to this?"* — because "this is great" is always available as plausible text.

## Key insight

Every prompting technique is the same technique: reduce what the model has to guess. Context, examples, format, audience, and reasoning room are five ways of doing that. If output is bad, ask "what did I make it guess?" before reaching for a cleverer phrasing.

## Related
- [[using-ai/02-how-llms-work-plainly|How LLMs Work, Plainly]] — why removing guesswork is the whole game
- [[using-ai/05-context-and-long-chats|Context and Long Chats]] — the other half of a good brief: what's in the window
- [[using-ai/06-verifying-what-it-tells-you|Verifying What It Tells You]] — a well-briefed answer still isn't a checked answer
- [[ai-ml/03-ai-engineer/05-prompt-engineering|Prompt Engineering]] — the builder's version: system prompts, chaining, evals, optimization
