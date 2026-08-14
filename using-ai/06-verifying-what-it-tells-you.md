# Verifying What It Tells You

**[Beginner, load-bearing]** — the most important note in this course. If you read one, read this one twice.

## The kid version first

The model sounds exactly as confident when it's right as when it's wrong. There is no tell. No hedge in the voice, no pause, no "I think." The fluency is constant because fluency is what it produces — accuracy is a side effect of the training text mostly being accurate.

So you cannot use *how it sounds* to judge *whether it's true*. That instinct — the one you use with people — is the thing you have to consciously switch off.

## Why fluency and truth come apart

From [[using-ai/02-how-llms-work-plainly|note 02]]: it predicts plausible next words. Plausible and true overlap heavily, which is what makes it useful — and what makes the gap so dangerous, because it's narrow and invisible.

The failure has a name, **hallucination**, which is a bad name: it suggests a rare glitch. It's not a glitch. It's the same process that produces correct answers, running on a question where the pattern doesn't happen to match reality. Fabricated content isn't produced differently from true content. That's why it's undetectable from the inside.

## The one question that decides everything

Before accepting any answer, ask:

> **Would I notice if this were wrong?**

- **Yes, immediately** — the code doesn't run, the joke isn't funny, the tone is off, the summary contradicts a document I have in front of me. → Low risk. Use it. You are the check.
- **Not until later** — the legal citation is fake, the dosage is wrong, the historical date is off, the statistic doesn't exist. → **Verify before acting.** Every time.

This single question does more work than any list of rules, because it scales with the stakes automatically.

## What to check hardest

Ranked roughly by how often models get them wrong *and* how badly it lands:

| Category | Why it's risky |
|---|---|
| **Citations, quotes, page numbers** | Perfectly-shaped and completely fabricated. The highest-frequency failure |
| **Statistics and figures** | Plausible magnitude, invented provenance |
| **Legal, medical, financial specifics** | Wrong is expensive, and varies by country in ways it'll flatten |
| **Anything recent** | Training cutoff; may not know it's out of date |
| **Names, dates, prices, versions** | Precise recall is its weakest mode |
| **"It says here that..."** about your own doc | It can misread or over-summarize; check the passage |

And what genuinely doesn't need this treatment: rewording your own text, brainstorming, explaining a concept you'll then test in practice, format conversion, first drafts you'll edit anyway. Verification is not a tax on every interaction — it's targeted at claims about the world.

## How to actually check

**Ask for the source, then open it.** Not "did you make that up?" — it can't reliably tell you. Ask for the specific source and go look. If a tool provides links, clicking them is the whole verification. A startling amount of "AI got it wrong" is really "nobody clicked."

Watch for the near-miss: real journal, real author, plausible title, paper doesn't exist. Or a real paper that says something adjacent to the claim rather than the claim.

**Ask in a fresh chat.** Same question, new conversation, no leading. Consistent answers aren't proof, but a different answer is a strong signal to stop trusting either. This works because there's no memory of having committed to the first answer — see [[using-ai/05-context-and-long-chats|note 05]].

**Ask a second model.** Different training, different failure modes. Disagreement is informative.

**Ask it to argue against itself.** *"What's the strongest case that this answer is wrong?"* Surfaces caveats it smoothed over. It's not introspection — it's generating counterargument text, which is a thing it's good at.

**Search normally.** For a checkable fact, a normal search is often faster than negotiating with a chatbot about whether it was sure.

## The specific traps

- **"Are you sure?"** doesn't verify anything. It makes concession-flavoured text likely. Models will "correct" right answers into wrong ones under mild pushback. Never treat capitulation as confirmation.
- **Confidence language is generated too.** "Definitely," "it's well established," "according to the 2019 study" — all just text. None of it reflects an internal certainty, because there isn't one.
- **Detail feels like evidence.** A fabrication with a page number, a date and a named author feels *more* credible than a vague truth. Specificity is free to generate.
- **Long output feels authoritative.** A 4,000-word research report earns the same scrutiny as a one-line answer. Volume is not verification.
- **It agrees with you.** These systems lean agreeable. If you sound like you want a particular answer, you raise the odds of getting it. State problems neutrally when you actually want the truth.
- **Your own expertise fades.** In your domain you catch errors instantly. Just outside it, you catch nothing — and that's exactly where you're most tempted to use it.

## Where the responsibility sits

If you send it, you said it. "The AI wrote it" has never once worked as a defence — not in court filings with invented cases, not in a report to your boss, not in a message to a client. The model is a drafting tool. Every output that leaves your hands is yours.

## Key insight

You cannot verify by asking the model. Confidence, detail, length, and apology are all generated text with no connection to truth. Verification means going outside the conversation — to a source, a second tool, a fresh chat, or your own knowledge. **Would I notice if this were wrong?** — and if the answer is no, go and check.

## Related
- [[using-ai/02-how-llms-work-plainly|How LLMs Work, Plainly]] — why confidence is uncorrelated with accuracy
- [[using-ai/05-context-and-long-chats|Context and Long Chats]] — grounding in real sources, the best prevention
- [[using-ai/08-living-with-it|Living With It]] — the habits that keep your own judgement sharp
- [[ai-ml/03-ai-engineer/12-evals|Evals]] — how builders verify at scale instead of one answer at a time
