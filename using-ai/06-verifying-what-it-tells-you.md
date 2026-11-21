---
id: 139a33bb-44bc-4e88-b481-71bc1e5843e9
---

# Verifying What It Tells You

## The kid version first
<!-- bite: 8617eeb5-caeb-4535-8e96-c0c080de5a95 -->

The model sounds exactly as confident when it's right as when it's wrong. There is no tell. No hedge in the voice, no pause, no "I think." The fluency is constant because fluency is what it produces — accuracy is a side effect of the training text mostly being accurate.

So you cannot use *how it sounds* to judge *whether it's true*. That instinct — the one you use with people — is the thing you have to consciously switch off.

## Why fluency and truth come apart
<!-- bite: 50f835cd-709e-40bf-ae6f-916f4d717e3d -->

From [[using-ai/02-how-llms-work-plainly|note 02]]: it predicts plausible next words. Plausible and true overlap heavily, which is what makes it useful — and what makes the gap so dangerous, because it's narrow and invisible.

The failure has a name, **hallucination**, which is a bad name: it suggests a rare glitch. It's not a glitch. It's the same process that produces correct answers, running on a question where the pattern doesn't happen to match reality. Fabricated content isn't produced differently from true content. That's why it's undetectable from the inside.

## The one question that decides everything
<!-- bite: cf9d8e26-95ae-4dde-bcfe-be3ad9cc29da -->

Before accepting any answer, ask:

> **Would I notice if this were wrong?**

- **Yes, immediately** — the code doesn't run, the joke isn't funny, the tone is off, the summary contradicts a document I have in front of me. → Low risk. Use it. You are the check.
- **Not until later** — the legal citation is fake, the dosage is wrong, the historical date is off, the statistic doesn't exist. → **Verify before acting.** Every time.

This single question does more work than any list of rules, because it scales with the stakes automatically.

## What to check hardest
<!-- bite: 5a25d5b6-eae0-4939-9aa2-3f114a940c32 -->

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
<!-- bite: a4ba47c8-69f7-4a79-b56e-a37315242ab8 -->

**Ask for the source, then open it.** Not "did you make that up?" — it can't reliably tell you. Ask for the specific source and go look. If a tool provides links, clicking them is the whole verification. A startling amount of "AI got it wrong" is really "nobody clicked."

Watch for the near-miss: real journal, real author, plausible title, paper doesn't exist. Or a real paper that says something adjacent to the claim rather than the claim.

**Ask in a fresh chat.** Same question, new conversation, no leading. Consistent answers aren't proof, but a different answer is a strong signal to stop trusting either. This works because there's no memory of having committed to the first answer — see [[using-ai/05-context-and-long-chats|note 05]].

**Ask a second model.** Different training, different failure modes. Disagreement is informative.

**Ask it to argue against itself.** *"What's the strongest case that this answer is wrong?"* Surfaces caveats it smoothed over. It's not introspection — it's generating counterargument text, which is a thing it's good at.

**Search normally.** For a checkable fact, a normal search is often faster than negotiating with a chatbot about whether it was sure.

## The specific traps
<!-- bite: bdf934da-9c75-4857-8520-58212ddda900 -->

- **"Are you sure?"** doesn't verify anything. It makes concession-flavoured text likely. Models will "correct" right answers into wrong ones under mild pushback. Never treat capitulation as confirmation.
- **Confidence language is generated too.** "Definitely," "it's well established," "according to the 2019 study" — all just text. None of it reflects an internal certainty, because there isn't one.
- **Detail feels like evidence.** A fabrication with a page number, a date and a named author feels *more* credible than a vague truth. Specificity is free to generate.
- **Long output feels authoritative.** A 4,000-word research report earns the same scrutiny as a one-line answer. Volume is not verification.
- **It agrees with you.** These systems lean agreeable. If you sound like you want a particular answer, you raise the odds of getting it. State problems neutrally when you actually want the truth.
- **Your own expertise fades.** In your domain you catch errors instantly. Just outside it, you catch nothing — and that's exactly where you're most tempted to use it.

## Where the responsibility sits
<!-- bite: 93ad96dc-256c-4d41-af59-4bb4ed332276 -->

If you send it, you said it. "The AI wrote it" has never once worked as a defence — not in court filings with invented cases, not in a report to your boss, not in a message to a client. The model is a drafting tool. Every output that leaves your hands is yours.

## Key insight
<!-- bite: 38b1c431-6059-44c8-8d9e-48e2822d712b -->

You cannot verify by asking the model. Confidence, detail, length, and apology are all generated text with no connection to truth. Verification means going outside the conversation — to a source, a second tool, a fresh chat, or your own knowledge. **Would I notice if this were wrong?** — and if the answer is no, go and check.

## Related
<!-- bite: c269b313-74e3-4b79-bf59-0e6df536ceee -->
- [[using-ai/02-how-llms-work-plainly|How LLMs Work, Plainly]] — why confidence is uncorrelated with accuracy
- [[using-ai/05-context-and-long-chats|Context and Long Chats]] — grounding in real sources, the best prevention
- [[using-ai/08-living-with-it|Living With It]] — the habits that keep your own judgement sharp
- [[ai-ml/03-ai-engineer/12-evals/index|Evals]] — how builders verify at scale instead of one answer at a time

## About this lesson
<!-- bite: 3670ab05-b49e-4c36-843d-6dd04039b8c5 -->

**Level:** Beginner, load-bearing. **Covers:** the most important note in this course. If you read one, read this one twice.
