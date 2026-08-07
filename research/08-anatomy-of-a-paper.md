# The Anatomy of a Paper

**[reference]** — built around Simon Peyton Jones' "How to Write a Great Research Paper," *The Craft of Research*, and Zobel's *Writing for Computer Science*. Opens Part B (writing). The standard sections of a paper, what each one must *do*, **and the argument that runs underneath them** — because a paper is not a lab diary, it's a **persuasive case for one claim.**

## The kid version first

A research paper is **not** a diary of *"here's everything I did all summer, in order."* It's much more like a **lawyer making one argument to a jury**:
> *"Here's my claim. Here's why you should care. Here's my evidence. Therefore, believe me."*

Everything in the paper serves that one argument. The lawyer doesn't tell the jury about the dead ends, the coffee breaks, or the three weeks fixing a bug — only what builds the case. And courtrooms have a **standard order** (opening statement, evidence, closing) so everyone knows what's coming; papers do too (abstract, intro, method, results, conclusion) so any reader knows exactly where to look for what they need.

So two ideas run this whole note: **(1) a paper is an *argument*, not a chronology, and (2) it has a *standard structure* where each section has one job.** Master both and writing gets dramatically easier, because you stop asking "what do I say next?" and start asking "what does *this section* need to do for my argument?"

## The paper is an argument, not a chronology

The single most important mental shift for a new writer: **you are not reporting your journey; you are convincing a skeptical expert of one contribution.** Peyton Jones' framing — *"don't describe your work, sell your idea."* This means:
- **The structure follows the *logic of the argument*, not the *timeline of the work*.** You might present your method cleanly even though you actually stumbled into it backwards.
- **Everything that doesn't serve the argument gets cut** — the failed approaches (unless instructive), the incidental details, the ego.
- **One paper, one contribution.** If you have three ideas, that's often three papers. A paper trying to argue three things argues none of them well.

Nail down your **one-sentence storyline** first — *"We show that [X]"* — and let every section serve it.

## Section by section — and each one's job

The conventional structure (with variations by [[research/11-paper-types-and-writing-styles|field/type]]). What each must accomplish:

### Title
Findable and honest — it should say what the paper is *actually* about (the contribution), using terms people will search for. Not clickbait, not cryptically clever.

### Abstract (~150–250 words) — a mini-paper
**The most-read part of your paper by far** — many people read *only* this and decide whether to go further. It's a compressed version of the whole argument: **problem → gap → what you did → key result → why it matters.** Every sentence earns its place; no filler, no "in this paper we will discuss." Write it to stand completely alone.

### Introduction — the most important section
If the abstract earns a read, the **intro** earns the *rest of the paper*. Peyton Jones is emphatic: **state your contributions explicitly, early, and concretely.** The reliable structure — a funnel:
1. **The problem** — what's the setting, in accessible terms.
2. **Why it matters** — the stakes; why a reader should care.
3. **The gap** — what's missing in what exists ([[research/03-finding-a-problem-and-literature-review|lit review]] in miniature): "but no one has…".
4. **"In this paper, we…"** — your approach in a sentence or two.
5. **Contributions** — often an explicit **bulleted list** ("Our contributions are: (1)…, (2)…"). This is a gift to reviewers — it tells them exactly what to evaluate.
6. **Roadmap** — a one-line "the rest of the paper is organized as…".

A reader should finish page 1 **understanding what you did and why it matters.** If they don't, nothing else you write can rescue the paper.

### Related Work — situate, don't list
Show you know the field *and* how you differ. Organize by **theme**, synthesize (not "Smith did X, Jones did Y…" — that's the [[research/03-finding-a-problem-and-literature-review|book-report smell]]). It's often placed **after** the intro (or even near the end) so a wall of citations doesn't block the reader's momentum before they even understand your idea. Its job: position your contribution in the landscape and make your novelty undeniable.

### Method / Approach — precisely, reproducibly
*What you did*, in enough detail that a competent reader could **[[research/05-methodology-and-experiment-design|reproduce]]** it. Define notation once and use it consistently. Present it in the *clear* logical order, not the messy order you discovered it. Diagrams help enormously here.

### Experiments / Results — the evidence
First the **setup** (datasets, baselines, metrics, protocol — enough to trust and repeat), then the **findings**. The [[research/10-figures-tables-and-presenting-data|figures and tables]] carry the story — a reader should get the headline result from a glance at your main figure. Explicitly **answer the questions** you posed in the intro, and report results honestly ([[research/06-analyzing-and-interpreting-results|variance, not just means]]).

### Discussion — what it means
Interpret: *why* did it come out this way, what does it imply, and — crucially — **limitations and threats to validity.** Stating your own limitations reads as **strength and honesty**, not weakness; it also pre-empts the reviewer who'd otherwise raise them.

### Conclusion — recap the contribution (not a summary)
Restate what you *contributed* (not "in this paper we discussed…" — remind them what you *showed*), and point to **future work** (open questions — a gift to future-you and to others). Short.

### References
Complete, correctly formatted, original sources ([[research/12-citations-referencing-and-tools|citations & tools]]).

## Write it in a *non-linear* order

You do **not** write top-to-bottom. A common, effective order:
1. **Figures/tables and results first** — they're the skeleton of the evidence.
2. **Method** — you know what you did.
3. **Related work** — while it's fresh.
4. **Introduction** — now that you know the paper's real story.
5. **Abstract and title *last*** — you can't summarize a paper you haven't written.

The abstract and intro are the hardest and most important, so writing them *last* (when you actually know what the paper says) is far easier than agonizing over them first.

## Point-first, everywhere (the reverse pyramid)

At every scale — the paper, each section, each paragraph — **lead with the point, then support it.** Abstract states the result up front; each section opens by saying what it'll establish; each paragraph's first sentence is its claim. Readers are busy and skim; if they read only the first sentence of each paragraph, they should still get your argument. This one habit does more for readability than any other ([[research/09-scientific-writing-craft|writing craft]]).

## Key insight

**A paper is a lawyer's argument for one contribution, not a diary of your summer — structure follows the *logic of the case*, not the timeline of the work, and everything that doesn't serve the argument gets cut.** Each section has a job: the **abstract** is a stand-alone mini-paper (the most-read part), the **introduction** must make the reader understand-and-care by the end of page 1 and **state contributions explicitly** (bulleted), **related work** situates by theme, **method** enables reproduction, **results** present evidence via figures, **discussion** interprets and owns limitations, and the **conclusion** recaps the contribution. Write it **non-linearly** (results → method → intro → abstract *last*), and **lead with the point** at every scale.

## Related
- [[research/09-scientific-writing-craft|Scientific Writing Craft]] — sentence- and paragraph-level clarity
- [[research/11-paper-types-and-writing-styles|Paper Types & Writing Styles]] — how this structure flexes by field/type
- [[research/03-finding-a-problem-and-literature-review|Literature Review]] — the discipline behind Related Work
- [[research/10-figures-tables-and-presenting-data|Figures & Tables]] — the evidence that carries Results
