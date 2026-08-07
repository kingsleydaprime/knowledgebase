# Reading Papers

**[reference]** — built around S. Keshav's "How to Read a Paper" (the three-pass method), plus standard advice on literature mapping. The first real research skill: you can't add a brick until you know which bricks exist, and that means reading papers — *efficiently*, because there are far too many to read them all properly.

## The kid version first

Trying to read a research paper like a storybook — first word to last, understanding every line — is **torture, and a waste of time.** Papers are dense, written by experts for experts, and *most of any given paper you don't need.*

Read like a **scout exploring from a plane** instead of a hiker walking every trail:
1. **First, a quick flyover** — is there even anything here worth landing for? (5 minutes.)
2. **If yes, a walk-through** — get the lay of the land, understand the main idea. (An hour.)
3. **Only for the few that really matter, a deep dive** — climb into every detail, maybe even redo it yourself. (Hours.)

You'll "read" a hundred papers with the flyover, actually walk through ten, and deeply climb three. That's not lazy — that's how researchers survive an ocean of papers. The method has a name: **the three-pass approach.**

## Why papers are hard on purpose

Papers are **dense by design**: strict page limits, an expert audience, and a convention of packing years of work into 8 pages. They assume you know the background, they front-load the contribution and hide the caveats, and they are absolutely **not** meant to be read linearly. Fighting that is the beginner's mistake. Once you accept "I will read the *right parts* in the *right order for my goal*," reading gets far faster.

## The three-pass method

### Pass 1 — the flyover (~5–10 minutes): *should I read this at all?*
Read only: **title → abstract → introduction → section/subsection headings → conclusion**, then glance at the figures and skim the references (do you recognize the big ones?). That's it. Afterward you should be able to answer the **five C's**:
- **Category** — what kind of paper is it? (new method, measurement study, survey…)
- **Context** — what other work is it related to; what foundations does it build on?
- **Correctness** — do the assumptions seem valid, on the face of it?
- **Contributions** — what does it claim to add? (the one sentence)
- **Clarity** — is it well written?

Then **decide**: read further, or stop. Most papers you'll stop here — and that's the point. Pass 1 is a filter, and being ruthless with it is what lets you cover a field.

### Pass 2 — the walk-through (~1 hour): *what did they actually do?*
Read the whole paper, but **skip the heavy machinery** — the proofs, the deep math derivations. **Look hard at the figures, tables, and graphs** (in a good paper these carry the story — can you read the key result off a chart?). Note terms you don't understand and references worth chasing. Afterward you should be able to **summarize the paper's main thrust to someone else, with evidence** — the contribution, the method in broad strokes, and what the results show. If you can't, either the paper is badly written or the topic needs background you should go get. This is the depth you need for most papers you cite.

### Pass 3 — the deep dive (several hours): *could I have done this? is it right?*
For the handful of papers you'll **build on, reproduce, or review**. Here you **virtually re-implement the paper** — mentally (or actually) re-derive every result, re-run the logic, challenge every assumption. You try to reconstruct exactly what the authors did and ask "would *I* have made these same choices? what did they *not* test? where would this break?" This is how you find a paper's hidden limitations — the gaps that become *your* next research question. It's slow and you do it rarely, but it's where real understanding (and new ideas) come from.

## Reading critically, not passively

At Pass 2 and 3, don't just absorb — **interrogate**:
- **What exactly is the claim?** (State it in one sentence — often narrower than the title suggests.)
- **Does the evidence actually support *that* claim?** Or does it support something weaker? (Over-claiming is the most common flaw.)
- **What did they *not* compare against?** Missing baselines and cherry-picked datasets hide here.
- **What are the limitations they downplayed?** Every method has them; the honest ones are stated, the rest you infer.
- **What would break it?** The condition under which it fails is often your opportunity.

Reading critically is the same muscle as [[research/14-peer-review-and-rebuttals|peer review]] — you're just reviewing for yourself.

## Mapping a whole field (not just one paper)

To get into a *new* area, don't read random papers — **build the map**:
1. **Start from a recent survey** (a review paper) or a well-cited recent paper in the area — it gives you the vocabulary and the landmarks.
2. **Follow citations *backward*** — the papers it cites are the foundations; the ones cited by *everybody* are the **seminal** papers you must know.
3. **Follow citations *forward*** — who cited *this* paper? (Google Scholar's "Cited by," Semantic Scholar, Connected Papers) — that shows you what came *after* and where the frontier is now.
4. **Notice the names** — the same few authors/groups recur; they're the people driving the area.

A few hours of this and you'll have a mental graph of "the 10 papers that matter and how they connect" — worth more than 50 papers read in random order.

## Note-taking & reference management (do this from day one)

You *will* forget why a paper mattered. Keep a **one-paragraph note per paper**: its contribution, method in a line, key result, limitations, and **how it relates to your work**. Store PDFs + metadata in a **reference manager** (**Zotero** is the free standard; Mendeley, Notion also work) — it also generates your [[research/12-citations-referencing-and-tools|citations/BibTeX]] later, so set it up early. A searchable pile of your own summaries is one of a researcher's most valuable assets.

**Where to find papers:** **arXiv** (preprints, especially CS/ML/physics — often free and months ahead of publication), **Google Scholar** and **Semantic Scholar** (search + citation graph), the **proceedings** of the field's main conferences/journals, and **Connected Papers** (visual citation maps).

## Key insight

**Don't read papers linearly — read like a scout, in three passes**: a 5-minute flyover (the five C's) to decide if it's worth more, a 1-hour walk-through (skip the heavy math, mine the figures) to grasp and summarize it, and a multi-hour deep dive (virtually re-implement it, challenge every assumption) only for the few you'll build on or review. Read **critically** — pin the exact claim, check the evidence really supports *it*, hunt the missing baselines and hidden limitations (those gaps are your next question). And to enter a field, **build its citation map** (survey → backward to foundations → forward to the frontier) rather than reading at random — keeping a one-paragraph note per paper in a reference manager from day one.

## Related
- [[research/01-what-research-is|What Research Is]] — why the "contribution" is what you read *for*
- [[research/03-finding-a-problem-and-literature-review|Finding a Problem & Literature Review]] — turning wide reading into a gap you can attack
- [[research/14-peer-review-and-rebuttals|Peer Review & Rebuttals]] — critical reading, formalized
- [[research/12-citations-referencing-and-tools|Citations & Tools]] — Zotero/BibTeX for managing what you read
