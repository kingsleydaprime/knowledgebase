# Finding a Problem & the Literature Review

**[reference]** — from *The Craft of Research* and standard lit-review methodology. The hardest, most underrated part of research: **choosing what to work on.** A well-chosen question is half the paper; a badly chosen one wastes months no matter how well you execute. This note is how to find a good problem and how the literature review *proves* it's worth doing.

## The kid version first

Everyone thinks the hard part of research is *answering* the question. It's not — it's **finding a good question in the first place.** A good research question is like a spot to dig for treasure that is all three of these at once:
- **Nobody has dug there yet** (it's *novel* — not already answered),
- **There's probably treasure** (it *matters* — someone will care about the answer), and
- **Your shovel can actually reach it** (it's *feasible* — you can tackle it with your time, skills, and equipment).

Digging where someone already dug = you rediscover their treasure (not novel). Digging where there's no treasure = wasted effort (not significant). Digging toward the Earth's core with a plastic spade = impossible (not feasible). Most bad projects fail one of these three *before any work is done.* And the map that tells you where people have already dug is the **literature review.**

## Good questions are the scarce resource

You will have no shortage of *energy* to do research and a chronic shortage of *good questions* to point it at. Experienced researchers are valuable largely because they have a *taste* for good problems. That taste is learnable — it comes from reading a lot ([[research/02-reading-papers|reading papers]]) and knowing where questions hide.

## Where good research questions come from

Questions rarely arrive as lightning bolts; you *mine* them:
- **The "Limitations" and "Future Work" sections** — authors literally list what their paper *doesn't* solve. This is the single richest vein: they've handed you open problems.
- **"Does it still hold if…?"** — take a result and change one thing: a different dataset, a harsher condition, a bigger scale, a real-world setting instead of a lab one. *Replication under new conditions* is real, publishable research (and often reveals the original was overclaimed).
- **Cross-pollination** — apply a method from field A to a problem in field B ("this technique from NLP might help this robotics control problem"). Much innovation is transfer, not invention.
- **Where papers disagree** — two papers claim opposite things; *why?* Resolving a contradiction is a great contribution.
- **Where a method breaks** — you notice (in a [[research/02-reading-papers|Pass-3 deep read]]) a hidden assumption; what happens when it's violated?
- **Your own itch** — a real problem you hit while building something. Systems/engineering research often starts here: "I needed X, nothing did it well, so I built and evaluated it."

For a **systems-engineering** student researching across AI/ML, robotics, and chips, the richest sources will usually be *"does this ML method work on my real physical/hardware system?"* and *"I built a system to do X, here's the design and evaluation."*

## The literature review — what it's really for

Beginners think a literature review is "a summary of everything written on my topic." It's not. **A literature review is an *argument* that (a) establishes what's already known, and (b) reveals the specific *gap* your work fills.** It exists to prove your question is **novel** (nobody dug here) and to **situate** your contribution (which existing bricks you build on).

How to do one well:
1. **Search systematically** — start from a survey + seminal papers, follow the [[research/02-reading-papers|citation map]] backward and forward. Search multiple term variations (fields use different words for the same idea).
2. **Organize by *theme*, not chronology** — group papers by *approach* or *sub-problem* ("methods that do X vs methods that do Y"), not "Smith 2019 did… then Jones 2020 did…". A chronological list is a red flag; a thematic synthesis shows understanding.
3. **Synthesize, don't enumerate** — say what the body of work *collectively* shows and where it agrees/disagrees, citing groups of papers together. You're drawing a map, not writing book reports.
4. **Name the gap explicitly** — end with the sentence the whole review was building toward: *"However, no prior work has addressed ___ — which is what this paper does."* That gap **is** your contribution's justification.

A **gap** is a *known unknown* — something the field would benefit from knowing but doesn't yet. Not every gap is worth filling (some are boring); the good ones are gaps whose answer *matters*.

## Scoping the question — the Goldilocks zone

Once you have a candidate question, **right-size it.** The classic checklist is **FINER**:
- **F**easible — can you actually do it with your time, skills, data, and equipment? *(the one students most overestimate)*
- **I**nteresting — will anyone care about the answer?
- **N**ovel — not already answered (this is what the lit review checks).
- **E**thical — can it be done responsibly? ([[research/07-research-ethics-and-integrity|ethics]])
- **R**elevant — does it advance the field / matter to someone?

And apply two blunt tests:
- **The Goldilocks test** — *too broad* ("solve robot navigation") is a career, not a paper; *too narrow* ("tune this one hyperparameter") is trivial. Aim for a question you can answer convincingly in one focused piece of work.
- **The "so what?" test** — imagine you've finished and gotten a clean answer. Say the answer out loud. Does anyone care? If "so what?" has no good reply, re-scope before you start.

Converting a fuzzy *topic* ("I'm interested in drones") into a sharp *question* ("does controller X reduce landing error vs the standard PID under wind gusts >5 m/s?") is most of the battle — the sharp version is [[research/05-methodology-and-experiment-design|testable]] and finishable.

## Staying current (an ongoing habit, not a one-time task)

The frontier moves; keep up cheaply: **arXiv subject alerts**, **Google Scholar alerts** (for a topic or when a key paper gets cited), **follow the key researchers/labs** (their new work + who they cite), and skim the **accepted-papers lists** of the field's top venues each cycle. Fifteen minutes a week keeps your map current and often surfaces your next question.

## Common traps (all avoidable before you start)

- **Reinventing the wheel** — you skipped/rushed the lit review and built something that already exists. The most demoralizing and most preventable failure.
- **Too broad** — you'll never finish; nothing gets a convincing answer.
- **Not actually novel** — "new to me" ≠ "new to the field." Only the literature can tell you.
- **Not feasible** — the experiment needs data/compute/equipment/time you don't have. *Check feasibility before committing.*
- **No "so what?"** — technically fine, but nobody cares.

## Key insight

**The scarce resource in research is a *good question*, and finding one is half the work.** A good problem is simultaneously **novel** (nobody's answered it), **significant** (the answer matters), and **feasible** (you can actually do it) — questions hide in papers' Limitations/Future-Work sections, in replication-under-new-conditions, in cross-field transfer, and in your own build-it pain. The **literature review** is not a summary but an **argument that reveals the gap you'll fill** — organized by theme, synthesized (not enumerated), ending in the explicit "no prior work has done ___" sentence. Scope with **FINER** and the "so what?" test, and turn a fuzzy topic into one sharp, testable question before you invest a single day of real work.

## Related
- [[research/02-reading-papers|Reading Papers]] — the citation-mapping that powers the lit review
- [[research/04-research-questions-and-hypotheses|Research Questions & Hypotheses]] — sharpening the question into something testable
- [[research/05-methodology-and-experiment-design|Methodology & Experiment Design]] — how you'll actually answer it
- [[research/01-what-research-is|What Research Is]] — novelty & significance as quality axes
