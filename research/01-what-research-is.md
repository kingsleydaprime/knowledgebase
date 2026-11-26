---
id: d88eaf6d-6639-44b2-a264-88260dcfda88
---

# What Research Is

Research is finding out something nobody knew yet, and explaining it so carefully that other people can check it and build on it.

## Before you start
<!-- bite: 57091cff-fcf0-4e99-bae8-08949372b9c7 -->

You don't need anything else for this lesson: it's the starting point for the whole subject.

After this lesson you will be able to:

1. say what makes research different from a report;
2. name a paper's contribution in one sentence, and say what kind of contribution it is;
3. tell the four kinds of research apart by how each one knows something is true;
4. judge research on the four things reviewers look for: novel, valid, significant and reproducible;
5. trace the research lifecycle that the rest of this subject follows.

## What research is
<!-- bite: 0ae8ea38-5290-47e7-b296-d045d174c351 -->

When most people say "do research", they mean: read what others have found and write it up. That's useful, but it's a **report**. You gathered knowledge; you didn't add any.

**Research** is different in two ways. You produce a small piece of **new** knowledge, something nobody knew before. And you explain how you found it so precisely that anyone can follow your steps and check it. "Trust me" isn't research; "here's exactly what I did, try it yourself" is.

So research has two jobs: **create new knowledge, and make it checkable.** Everything else in this subject serves those two jobs. This lesson covers what counts as new knowledge, the kinds of research, what makes research good, and the cycle every project goes through.

## The kid version
<!-- bite: c82ae68d-ea64-4ed5-b0f5-54347d5dbbdd -->

Your teacher says "do research on volcanoes". You read some books and write down what they say in your own words. That's a report: everything in it was already known.

Now imagine you notice that the hot spring behind your school bubbles more after it rains, and nobody has ever written that down. You measure the bubbling every day for a month, write down the rainfall too, and show your notebook to your teacher so she can see exactly what you did. That's research. You found out something new, and you showed your steps so anyone can check them, like a detective who explains every clue.

**Where the analogy stops working.** A month of notes on one spring is a start, but real research has to rule out other explanations (maybe the bubbling follows the temperature, not the rain) and compare its result with what's already known. The later lessons in part A are about doing exactly that.

## Seeing the difference
<!-- bite: ab4cba4b-bb36-4fad-b4bf-e095ac9dda19 -->

Picture everything people already know as a region, with an edge at the limit of what anyone knows. A report gathers things from inside the region. Research pushes the edge out, a tiny bit:

![Report versus research. The blue region is everything people already know, and its curved edge is the limit of what anyone knows. A report (the dot inside) gathers and summarises knowledge that is already inside the region. Research pushes the edge out: the small orange bump is a contribution, a piece of new knowledge that was not inside before](images/rs-knowledge-edge.svg)

Notice how small the bump is. Research is incremental: you add one brick, not the whole building. That's normal, and it's why the next lesson starts with reading what's already inside the region.

## The contribution
<!-- bite: 99c7cb53-c01e-4b63-8f6e-27edc9ae53f2 -->

That small bump has a name: the paper's **contribution**, the one new thing it adds to what people know. Every research paper exists to deliver one clear contribution.

Here's the test. Finish this sentence: *"Before this work, nobody knew, or could do, ___; now they can."* If you can't fill the blank in one sentence, you don't have a paper yet. Naming your contribution is the most important step in any project, and beginners skip it more than any other.

## Kinds of contribution
<!-- bite: 97c9ad4f-dcc2-4d2c-a1f9-a32aaed6ba17 -->

Contributions come in a few kinds, and the kind decides what evidence you need and how you'll write the paper:

1. **A new method or technique**: "here's a better way to do X", such as a faster algorithm or a new model design.
2. **An empirical finding**: "here's something true about the world that we measured", such as "model A beats model B on task T".
3. **A theory or proof**: "here's something we can prove must be true", such as a bound or an impossibility result.
4. **A system or artifact**: "we built a thing that works; here's the design and the evidence", such as a robot controller or a chip.

## Kinds of contribution, continued
<!-- bite: bf51f319-cef5-4509-869e-9b729de154c6 -->

Three more kinds are less common, but you'll meet them in every field:

1. **A dataset or benchmark**: "here's a new way to measure progress", such as a labelled dataset.
2. **A survey**: "here's a whole field organised so you can understand it".
3. **A new problem**: "here's a question worth asking that nobody had framed".

As a systems engineering student, you'll most often make empirical and system contributions, and sometimes theoretical ones. Each has its own writing style, covered in Paper Types and Writing Styles (lesson 11, being written).

## How each kind of research knows things
<!-- bite: fa26d97c-79fa-4f50-ae7c-4cf73c6d88bb -->

Fields differ in what counts as *proof*. There are four main kinds of research:

1. **Empirical** research learns by **measuring** the world: run experiments, collect data, compare against a baseline. Most of machine learning, robotics and physical engineering. Truth is the evidence.
2. **Theoretical** research learns by **proving**: start from assumptions and derive results with maths or logic. Truth is a valid proof.
3. **Systems or engineering** research learns by **building something and evaluating it**: the artifact is the contribution, and benchmarks or case studies show it works. Truth is a working, measured system.
4. **Qualitative** research learns by **observing and interpreting**: interviews, case studies, careful observation, as in the social sciences and design. Truth is a careful, well-argued interpretation.

Most real projects mix them: build a system, run experiments on it, and prove a small bound. Knowing which mode you're in tells you what counts as evidence.

## The research mindset
<!-- bite: e52fdf65-7aea-4470-85f8-c0bd972736b9 -->

Five habits separate research from opinion:

1. **Curiosity and doubt together.** Chase interesting questions, but distrust your own results most of all. "Is there a boring explanation for this?" should be your reflex.
2. **Precision.** A vague claim can't be checked. "It's faster" is opinion; "23% lower latency on dataset D" is a claim someone can test.
3. **Honesty.** Report what actually happened, including failures, limitations and results that hurt your story. The whole system runs on trust; see [[research/07-research-ethics-and-integrity|Research Ethics and Integrity]].
4. **Building on others.** You're adding one brick, so you must know the bricks already there; see [[research/03-finding-a-problem-and-literature-review|Finding a Problem and the Literature Review]].
5. **Being comfortable wrong.** Most experiments fail and most ideas don't work out. A negative result, honestly reported, is still real knowledge.

## What makes research good
<!-- bite: f5932b09-c68a-4940-a4b2-df163e87c9b8 -->

Reviewers and readers judge research on four things. Aim for all four:

1. **Novel**: it's genuinely new, not a rehash. The literature review is how you show this.
2. **Valid**: the method really supports the claim, with no fatal flaw. That's the job of [[research/05-methodology-and-experiment-design|Methodology and Experiment Design]].
3. **Significant**: it matters; someone can use it or build on it. New but trivial gets rejected.
4. **Reproducible**: someone else can repeat it and get the same result. This is what makes it science rather than a story.

## The research lifecycle
<!-- bite: 2fab0fd9-87fe-4af6-87e4-82d9a060526c -->

Every project goes round the same loop. Here it is, coloured by the part of this subject that covers it:

![The research lifecycle as a loop: curiosity leads to a question; you read the literature and sharpen it into a question or hypothesis; design a method; run experiments or build; analyse honestly (part A of the course, blue); write it up (part B, green); go through peer review, publish, and others build on it (part C, yellow), which raises new questions and starts the loop again](images/rs-lifecycle.svg)

Part A of this subject (blue) is doing the research. Part B (green) is writing it up. Part C (yellow) is getting it out, where others build on it. The orange arrow is why the loop never really ends: every answer raises new questions.

## Your project: a real study, start to finish
<!-- bite: c562eb0e-0f78-48bf-b62d-3f2cdd13d970 -->

This subject isn't something you only read. By the end of it you'll have **done a small piece of research and written it up as a short paper**. Every lesson moves your study one step forward.

The lessons follow one default study you can do yourself: **"How accurate are free weather apps for Lagos?"** You'll record what two or three free apps forecast, record what the weather actually did, measure each app's errors over a few weeks, compare them fairly, and write it up. It needs only a phone and a notebook, and as far as we know, nobody has published that exact comparison. If you'd rather study your own question, use it instead; it just needs something you can measure, build or compare in a few weeks.

## Step 1: start your research journal
<!-- bite: 997d048a-707b-4c11-b2e0-1636e2ed43a5 -->

Make a folder called `my-study`, and in it a file `journal.md`. Researchers keep a dated journal of every decision and result, because you will forget why you did things. Write today's date and one line: "Started."

## Step 2: list your curiosities
<!-- bite: 9c660f38-4c2e-4c2b-b550-4d477867a00d -->

In the journal, write **five questions you're genuinely curious about** that nobody has handed you an answer to. Small and local is good: "Do bus fares in Yaba follow fuel prices?", "Is my phone's battery estimate honest?", "Which weather app is right most often in Lagos?"

## Step 3: pick your study and draft its contribution
<!-- bite: 6e682479-11ab-4117-bb19-f5e61202264c -->

Pick one question: the weather apps, or one of yours. Then write a **draft contribution** in the shape from earlier: *"Before this study, nobody knew ___; now we know ___."* It will change as you read, so don't polish it; just write it down.

## Your project so far
<!-- bite: 8833c005-897d-46f9-8f08-dbedfc3505fc -->

```text
my-study/
└── journal.md   ← today's date, five questions, your chosen study, a draft contribution
```

**Done when** your journal has the date, five real questions, the one you chose, and a draft contribution sentence with its kind of contribution named (for the weather apps: an empirical finding).

## Terms used in this lesson
<!-- bite: a866d496-898b-4035-a580-c99bc9bc5eb1 -->

1. **Research** is producing a small piece of new knowledge and explaining it so others can check it and build on it.
2. A **report** gathers and summarises knowledge that already exists.
3. A **contribution** is the one new thing a piece of research adds to what people know.
4. **Empirical** research learns by measuring the world; **theoretical** research by proving; **systems** research by building and evaluating; **qualitative** research by observing and interpreting.
5. Research is **reproducible** when someone else can repeat it and get the same result.
6. A **negative result** is finding that something doesn't work or doesn't hold; honestly reported, it still counts as knowledge.

## Common pitfalls and traps
<!-- bite: ba911b44-90e1-48f4-ac99-1918fcd968fd -->

1. **Calling a summary research.** A literature review on its own is a report (or a survey paper, if it organises a whole field). Research adds something new.
2. **No one-sentence contribution.** If you can't finish "before this, nobody knew ___", stop and find it before you write anything.
3. **Vague claims.** "Better", "faster" and "more efficient" mean nothing until you say by how much, on what, compared with what.
4. **Hiding failures.** Dropping the experiments that didn't work makes the rest untrustworthy. Report them.

## Check your understanding
<!-- bite: 4f97633e-d729-410d-9172-7e75c0b4aa0f -->

Try each one before you open the answer.

1. <!-- q: mcq id="7c2e91a4" -->
   A student reads ten articles on solar panels in Nigeria and writes a 20-page summary of what they say. What is this?

   - [ ] Empirical research
   - [x] A report
   - [ ] Theoretical research
   - [ ] A new contribution

   <details><summary>Answer</summary>

   A report. Everything in it was already known; the student gathered and summarised it. It would become research if they measured, built or proved something new, such as testing how dust affects panel output on their own roof.

   </details>

2. <!-- q: mcq id="3a8d5f60" -->
   A paper says: "We built a low-cost robot arm controller and show it tracks a target within 2 mm in 50 trials." What kind of contribution is this mainly?

   - [ ] A theory or proof
   - [x] A system or artifact
   - [ ] A survey
   - [ ] A dataset

   <details><summary>Answer</summary>

   A system or artifact: the controller is the new thing, and the 50 trials are the evidence that it works. (The trials are empirical, which is normal: systems papers usually back the system with measurements.)

   </details>

3. <!-- q: gap id="b41f0c72" answers="measuring;proving;building" -->
   Fill in how each kind of research knows things.

   Empirical research learns by ___ the world. Theoretical research learns by ___. Systems research learns by ___ something and evaluating it.

   <details><summary>Answer</summary>

   Measuring, proving, building. Empirical truth is evidence; theoretical truth is a valid proof; systems truth is a working, measured system.

   </details>

4. <!-- q: mcq id="e5096d1b" -->
   Which one is a **checkable** claim?

   - [ ] "Our app is much faster."
   - [ ] "Our method is more efficient than older ones."
   - [x] "Our app loads in 1.2 s on a Tecno Spark 10, against 3.4 s for the old version."
   - [ ] "Users will love the new design."

   <details><summary>Answer</summary>

   The third: it says what was measured, on what, and compared with what, so anyone can test it. The others are opinions until they're made precise.

   </details>

5. <!-- q: mcq id="5f27a8c3" -->
   Another lab repeats your experiment exactly and gets the same result. Which property of good research does this show?

   - [ ] Novel
   - [ ] Significant
   - [x] Reproducible
   - [ ] Qualitative

   <details><summary>Answer</summary>

   Reproducible. It's the property that turns a result from a story into science.

   </details>

6. <!-- q: open id="9d63b2e8" -->
   Write a one-sentence contribution for this project: "I compared three ways of detecting cassava disease from leaf photos on a cheap phone, and found that a small neural network was most accurate while still running offline." Then say which kind of contribution it is.

   <details><summary>Answer</summary>

   For example: "Before this work, nobody had compared cassava disease detectors on a low-cost phone; we show that a small neural network is the most accurate of three methods while still running offline." It's mainly an **empirical finding** (a measured comparison). If the main point were the app itself, it would be a system contribution.

   </details>

## Before moving on
<!-- bite: 3d56f0b3-e513-417f-accd-aeb4dde12156 -->

You're done when you can tell a report from research, write any project's contribution in one sentence and name its kind, say how the four kinds of research know things, and judge a piece of research as novel, valid, significant and reproducible.

Recap: research creates a small piece of new knowledge and makes it checkable. Its heart is one nameable contribution. Fields prove things differently (measuring, proving, building, interpreting), good research is novel, valid, significant and reproducible, and every project goes round the same lifecycle. You learn it by doing it.

Next: [[research/02-reading-papers|Reading Papers]], the first real skill, because you can only push the edge out once you know where it is.

## Related
<!-- bite: cab5f308-452b-4520-a6a6-24da5eb1acc1 -->

- [[research/02-reading-papers|Reading Papers]]: absorbing what's already known.
- [[research/03-finding-a-problem-and-literature-review|Finding a Problem and the Literature Review]]: turning curiosity into a real, novel question.
- [[research/07-research-ethics-and-integrity|Research Ethics and Integrity]]: why honesty holds the whole thing up.

## About this lesson
<!-- bite: 46285ad3-b7cb-4804-a9a4-054dec3a3ae9 -->

**Level:** beginner. Lesson 01 of the research subject, part A (doing the research). It covers what research is, contributions and their kinds, the four kinds of research, the research mindset, what makes research good, and the research lifecycle.

**Source:** *The Craft of Research* (Booth, Colomb and Williams) and standard scientific-method guidance. Rewritten to the course standard on 2026-11-26; the pictures come from `scripts/diagrams/research.py`.
