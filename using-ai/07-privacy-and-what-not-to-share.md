# Privacy and What Not to Share

**[Beginner]** — assumes nothing technical. Practical, not paranoid: what actually happens to what you type, and the small number of rules worth following.

## The kid version first

Typing into a chatbot feels like typing into a private notebook. It isn't. It's closer to **sending an email to a company** — one that may be stored, may be read by a human reviewer, and may be used to improve future products.

That's not a reason to avoid these tools. It's a reason to know which conversations belong in them.

## What actually happens to what you type

Details differ by provider and change over time, but the shape is consistent:

1. **It's sent to a server.** Almost always someone else's, often in another country. (Local models on your own machine are the exception — a niche but real option.)
2. **It's usually stored.** Your chat history is a feature; that means retention.
3. **It may train future models — depending on your tier and settings.** This is the one people get wrong. Broadly: consumer/free tiers often use conversations for improvement by default, business and enterprise tiers usually don't, and most consumer products offer a setting to opt out. **Go and look at yours.** It's typically under Settings → Data controls, and takes a minute.
4. **A human may read a sample.** For safety review and quality work, providers sample conversations. Rare for any given chat, but not zero.
5. **Deleting a chat isn't always deleting the data.** Retention windows for safety and legal purposes often outlive the visible history.

None of this is sinister — it's roughly how every cloud service works. The mistake is assuming a conversational interface implies a private one.

## The rules

**Don't paste:**

- Passwords, API keys, card numbers, one-time codes
- Other people's personal data — customer records, patient details, an employee's medical situation, a friend's private message thread
- Anything under an NDA or a confidentiality clause
- Unreleased financials, unfiled legal strategy, unannounced deals
- Government or client data your employer hasn't cleared for third-party AI tools

**Fine to paste:**

- Your own work, your own writing, your own questions
- Public documents
- Anything you'd be comfortable emailing to a competent vendor
- Sensitive-*shaped* material with the identifying details swapped out

**The redaction habit** is the one that makes this workable. You rarely need the real names. "Review this contract between Acme Ltd and my company" works just as well as the version with real parties, and "a 34-year-old with these symptoms" gets the same answer as one with a name attached. Strip identifiers, keep the substance — you lose almost nothing.

## Work and clients

The single most common way people get into trouble: pasting employer or client material into a personal free-tier account. Even where the content is harmless, it often breaches a policy or a client contract.

- **Find out if your employer has a policy.** Many now do, and many provide an approved tool with a proper data agreement. Use that one.
- **A client contract may prohibit it** regardless of your employer's view — confidentiality clauses written before 2023 usually cover "disclosure to third parties" without mentioning AI, and a chatbot is a third party.
- **In regulated work** — health, legal, finance, education, government — assume the answer is no until someone tells you which tool is approved.

## The other direction: what comes out

Two things worth flagging:

- **Output isn't automatically yours to use freely.** For most text, in most places, using it is fine — but generated images can resemble existing work, and generated code can carry licence implications. If it's going into something commercial, that's worth a real check rather than an assumption.
- **Never paste secrets *out* of a conversation into somewhere public** — people share screenshots of chats without noticing the system prompt, the file contents, or the email address in the corner.

## A note on the anxiety

It's easy to read all this and conclude the safe move is not to use these tools. That's usually the wrong conclusion. The realistic risk for most people, most of the time, is *low* — and it's almost entirely eliminated by two habits: **check your data-training setting once**, and **redact identifying details before pasting**. Do those two things and the remaining risk is comparable to using any other cloud service you already trust.

## Key insight

Treat a chatbot as a competent external vendor, not a private notebook. That single framing gets you to the right answer on nearly every "should I paste this?" question — and the redaction habit means the answer is usually "yes, just not with the real names in it."

## Related
- [[using-ai/05-context-and-long-chats|Context and Long Chats]] — memory and projects persist more than a single chat does
- [[using-ai/08-living-with-it|Living With It]] — disclosure, and where responsibility sits
- [[ai-ml/03-ai-engineer/10-safety-and-production|Safety & Production]] — the builder's side: prompt injection, guardrails, data handling
- [[cybersecurity/README|Cybersecurity]] — the wider discipline this borrows from
