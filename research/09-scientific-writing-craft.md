# Scientific Writing Craft

**[reference]** — from Zobel's *Writing for Computer Science*, Williams' *Style: Lessons in Clarity and Grace*, and Strunk & White. [[research/08-anatomy-of-a-paper|Anatomy]] gave you the skeleton and where each section goes; this is the **craft** of the sentences and paragraphs that fill it — turning a correct-but-impenetrable draft into something a reader glides through.

## The kid version first

Good scientific writing is **not** about big fancy words that make you sound smart. It's the opposite: it's about making a **hard idea feel easy to follow** — like a patient friend explaining something so clearly you barely notice you're learning.

Here's the mindset that changes everything: **if the reader has to read a sentence twice to understand it, *you* failed — not them.** Their confusion is your bug, not their fault. Their time and attention are precious and limited, and your job is to spend as little of it as possible getting your idea into their head. Clear writing is an act of *respect* for the reader.

So the whole craft is: **be understood with the least effort from the reader.** Not impressive — *clear*.

## Clarity over cleverness

The purpose of a research paper is to **transfer an idea**, not to showcase vocabulary. Big words, long sentences, and dense jargon *feel* scholarly and *are* barriers. Every time a reader stumbles — an undefined term, a tangled sentence, a missing connection — you risk losing them. Write for a smart reader who is **not** a specialist in your exact sub-problem and is reading quickly. When in doubt, choose the plainer word and the shorter sentence.

## Structure at every scale: point first

The [[research/08-anatomy-of-a-paper|reverse-pyramid]] habit, applied down to the paragraph:
- **One idea per paragraph**, and the **first sentence states it** (the topic sentence). The rest of the paragraph defends or develops that one idea. A reader skimming *only* first sentences should still follow your argument.
- If a paragraph has two ideas, split it. If you can't write its topic sentence, you don't yet know what it's about.

## Precision

Vague claims aren't just weak — they're unverifiable:
- **Concrete over vague** — "reduces error by 12%" not "greatly improves"; "runs in 3 ms" not "is fast." ([[research/06-analyzing-and-interpreting-results|The narrowest true claim.]])
- **Define terms once, then use them consistently** — don't call the same thing "the model," "the network," and "our approach" in three paragraphs; pick one name. Inconsistent terminology makes readers wonder if you mean different things.
- **Consistent notation** — a symbol means one thing throughout; introduce it before you use it.

## Sentence-level craft

- **Prefer active voice and strong verbs** — "we measured X" over "X was measured"; "the model *predicts*" over "the model is able to make a prediction of." Active voice is clearer and shorter. *(Some fields still lean passive in Methods — [[research/11-paper-types-and-writing-styles|know your venue]] — but default to active.)*
- **Cut hedging and filler** — "it is worth noting that," "in order to," "due to the fact that," "very," "quite," "somewhat." They add words and subtract confidence. "In order to" → "to." "Due to the fact that" → "because."
- **Short sentences for hard ideas** — when the *content* is complex, keep the *syntax* simple. Long sentence + hard idea = lost reader.
- **Parallel structure** — items in a list share grammatical form ("we collect data, train the model, and evaluate results" — not "…and evaluation of results").
- **One point per sentence** — if a sentence has three clauses doing three jobs, it's probably three sentences.

## Flow and cohesion — make it *connect*

Clarity isn't just clear sentences; it's clear *links* between them:
- **Old information before new** — start a sentence with something the reader already knows (from the previous sentence), then introduce the new. This "given → new" chaining is what makes prose feel like it *flows* instead of lurching. It's the single most powerful cohesion technique and the hardest to notice when it's missing.
- **Signpost the logic** — use transitions that name the *relationship*: "However" (contrast), "Therefore" (consequence), "For example" (instance), "In contrast" (comparison). Don't make the reader infer how two sentences relate.
- **Forecast and summarize** at section boundaries so readers never feel lost.

## The common mistakes (that reviewers groan at)

- **Burying the contribution** — the reader can't find what's new.
- **Undefined jargon / acronyms** — define on first use; don't assume.
- **Passive fog** — endless "it was found that…" hiding who did what.
- **Throat-clearing intros** — three paragraphs of generic background before anything specific ("Since the dawn of computing…"). Get to the point.
- **Results with no interpretation** — a table dumped with no "what this shows."
- **Inconsistent terms/notation** — the same thing under three names.
- **Overclaiming** — writing checks the [[research/06-analyzing-and-interpreting-results|evidence]] can't cash.

## Writing = rewriting

Nobody writes a good first draft — **the first draft's only job is to exist.** Good writing is made in revision:
- **Get it all down badly first**, then fix. Don't polish sentence 1 before sentence 2 exists.
- **Read it aloud** — your ear catches clunky sentences your eye skims past.
- **Cut ~10% on every pass** — almost every draft is too long; brevity is clarity.
- **Reverse-outline** — after drafting, write the topic sentence of each paragraph in a list; if that list isn't a clean argument, your structure is broken (fix it before polishing prose).
- **Get feedback early** — a confused reader shows you exactly where the writing fails; you're too close to see it.

## A note for non-native English writers

Most of the world's researchers write in a second language, and clear scientific English is a **learnable skill, not a talent.** Practical tactics: favor **short, simple sentences** (they're clearer *and* harder to get wrong), **imitate the phrasing** of well-written papers in your area (keep a file of good sentence patterns), use grammar tools and (disclosed, per [[research/07-research-ethics-and-integrity|ethics]]) AI editing to polish — but **you own every claim**, and ask a fluent colleague for a read. Clarity of *thinking* translates to clarity of writing in any language; a well-organized simple-English paper beats a fancy tangled one every time.

## Key insight

**Good scientific writing makes a hard idea easy to follow — if the reader has to read a sentence twice, you failed, not them.** Choose clarity over cleverness (plainer word, shorter sentence), **lead with the point** at every scale (one idea per paragraph, topic sentence first), be **precise** (concrete numbers, consistent terms and notation), and write tight sentences (**active voice, strong verbs, cut the hedging and filler**). Make prose *flow* with **old-info-before-new** chaining and explicit transitions. And accept that **writing is rewriting** — draft badly, then revise ruthlessly (read aloud, cut 10%, reverse-outline, get early feedback). It's a craft you build by doing, and it's an act of respect for the reader's time.

## Related
- [[research/08-anatomy-of-a-paper|Anatomy of a Paper]] — the structure this prose fills
- [[research/10-figures-tables-and-presenting-data|Figures & Tables]] — the visual half of communicating results
- [[research/11-paper-types-and-writing-styles|Paper Types & Writing Styles]] — how tone/voice shift by field
- [[research/06-analyzing-and-interpreting-results|Analyzing & Interpreting Results]] — precise, non-overclaiming statements
