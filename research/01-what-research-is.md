# What Research Actually Is

**[reference]** — from *The Craft of Research* (Booth et al.) and standard scientific-method guidance. Before *how* to do research, it helps to be clear on *what it is* — because most people (and most school assignments) mean something much smaller by "research." This note sets the mindset the rest of the course builds on.

## The kid version first

When your teacher says "do research for your report on volcanoes," you go read what other people already figured out and write it up in your own words. That's a **report** — useful, but you didn't discover anything; you *summarized*.

**Real research is different: you find out something that *nobody knew yet*, and you tell the world in a way they can *check*.** It's less like writing a report and more like being a **detective**: you notice a question no one has answered, you hunt for a new clue, and then — this is the crucial part — you **show everyone exactly how you found the clue**, so they can follow your steps and trust it (or catch your mistake). "Trust me" isn't research. "Here's precisely what I did, try it yourself" is.

So research = **create a small piece of new knowledge + explain it carefully enough that others can verify it and build on it.** Everything else in this course serves those two jobs.

## The heart of it: a "contribution"

Every research paper exists to deliver **one clear contribution** — the single new thing it adds to human knowledge. If you can't finish the sentence *"Before this paper, nobody knew / could / had ___; now they do,"* you don't yet have a paper. Naming your contribution in one sentence is the most important thing you'll do, and beginners consistently skip it.

Contributions come in a few flavors — knowing which kind you're making shapes the whole paper:

| Kind of contribution | You're claiming… | Example |
|---|---|---|
| **New method / technique** | "here's a better way to do X" | a faster algorithm, a new model architecture |
| **Empirical finding** | "here's something true about the world we measured" | "model A beats B on task T," "this material fatigues under condition C" |
| **Theory / proof** | "here's something we can *prove* must be true" | a bound, a theorem, an impossibility result ([[architecture/04-distributed-systems/02-theoretical-limits|like FLP]]) |
| **System / artifact** | "we built a thing that works, here's the design + evidence" | a new robot controller, a chip design, a software system |
| **Dataset / benchmark** | "here's a new way to *measure* progress" | a labeled dataset, an evaluation suite |
| **Survey / synthesis** | "here's the whole field organized so you understand it" | a review paper mapping an area |
| **New problem / formulation** | "here's a question worth asking that nobody framed" | defining a new task |

As a **systems-engineering** student, you'll most often make **empirical**, **systems/artifact**, and sometimes **theory** contributions — and each has its own writing style ([[research/11-paper-types-and-writing-styles|paper types & writing styles]]).

## The kinds of research (and how they *know* things)

Different fields answer questions differently — the method of "proof" changes:
- **Empirical** — learn by *measuring the world*: run experiments, collect data, compare against baselines. Most of ML, robotics, physical engineering. Truth = evidence.
- **Theoretical** — learn by *proving*: start from assumptions, derive results with math/logic. Truth = a valid proof.
- **Systems / engineering** — *build something and evaluate it*: the artifact is the contribution, and you show it works (benchmarks, case studies). Truth = a working, measured system.
- **Qualitative** — *observe and interpret*: interviews, ethnography, case analysis (social sciences, HCI, design). Truth = careful, well-argued interpretation.

Most real work mixes them (build a system *and* run empirical experiments *and* prove a small bound). Knowing which mode you're in tells you what counts as evidence.

## The research mindset

The habits that separate research from opinion:
- **Curiosity + skepticism together** — chase interesting questions, but *distrust your own results* hardest. "Is there a boring explanation for this?" is the researcher's reflex.
- **Precision** — vague claims aren't checkable. "It's faster" is opinion; "23% lower latency at p95 on dataset D" is a claim.
- **Radical honesty** — report what actually happened, including failures, limitations, and results that hurt your story. The whole enterprise runs on trust; one faked result poisons it ([[research/07-research-ethics-and-integrity|ethics]]).
- **Standing on shoulders** — research is *incremental*. You're adding one brick, not building the cathedral alone — which is why knowing the existing bricks ([[research/03-finding-a-problem-and-literature-review|literature review]]) is non-negotiable.
- **Comfort with being wrong** — most experiments fail, most ideas don't pan out, and a *negative* result honestly reported is still real knowledge.

## What makes research *good*

Reviewers and readers judge work on roughly four axes — internalize them and aim for all four:
- **Novel** — genuinely new, not a rehash (this is what the [[research/03-finding-a-problem-and-literature-review|literature review]] establishes).
- **Valid / correct** — the method actually supports the claim; no fatal flaw ([[research/05-methodology-and-experiment-design|methodology]]).
- **Significant** — it *matters*; someone can use or build on it. (Novel-but-trivial gets rejected.)
- **Reproducible** — others can repeat it and get the same result — the property that makes it *science* rather than an anecdote.

## The research lifecycle (the map for this course)

```
curiosity → a QUESTION → read the LITERATURE → sharpen into a HYPOTHESIS/question
   → design a METHOD → run EXPERIMENTS / build → ANALYZE honestly
   → WRITE it up → PEER REVIEW → PUBLISH → others build on it → new questions
```

Part A of this course is the left half (doing the research), Part B is writing it up, Part C is getting it out and into the loop where others extend it. The cycle never really ends — every answer spawns new questions.

## Key insight

**Research is not summarizing what's known — it's producing a small piece of *new* knowledge and explaining it so precisely that others can verify and build on it.** The core of every paper is one nameable **contribution** ("before this, nobody knew/could ___"), which comes in flavors (method, empirical finding, theory, system, dataset, survey, new problem) — and the flavor plus the *kind* of research (empirical / theoretical / systems / qualitative) determines what counts as evidence and how you'll write it. Good research is **novel, valid, significant, and reproducible**, and it runs entirely on **honesty**. You learn it by *doing* it, not reading about it.

## Related
- [[research/02-reading-papers|Reading Papers]] — the first real skill: absorbing what's already known
- [[research/03-finding-a-problem-and-literature-review|Finding a Problem]] — turning curiosity into a real, novel question
- [[research/11-paper-types-and-writing-styles|Paper Types & Writing Styles]] — how the contribution-kind shapes the paper
- [[research/07-research-ethics-and-integrity|Ethics & Integrity]] — why honesty is the load-bearing value
