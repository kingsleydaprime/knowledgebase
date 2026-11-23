# Course Standard — From Reading to Independent Work

The goal is not to make notes sound academic. It is to make them teach: **explain the idea, show how it works, then help the learner do it without copying.** A sequence of topic summaries is not yet a self-study course.

This is the standard for new and revised **teaching lessons**, not a claim that the whole vault already meets it. Lookup references, interview banks, project journals, and personal reflections keep their own shapes. `[reference]` still means read-from-sources rather than learned through the author's own production experience; a tested example does not erase that distinction.

## University / high-school course feel

A good course note — whether university or high school — does not just list facts. It gives **definitions, comprehensive explanations, worked examples, and the reason something is defined that way.** The reader should finish a section able to explain the concept in their own words and apply it to a new problem, not just recognise the heading.

- Define terms before using them, and keep the definition local to the section where it first matters.
- Explain the _why_ behind each definition or rule, not just the _what_. If a definition has a common alternative, say why this one is chosen and when the alternative appears.
- Use one or two comprehensive worked examples that trace the full mechanism step by step, not three superficial name-drops.
- Separate the core idea from advanced applications; advanced material belongs in an optional extension, not the entry path.
- Acknowledge limitations, edge cases, and common mistakes explicitly rather than burying them in a short "gotchas" line.

This does not mean every note becomes a textbook chapter. A 10-minute pattern note can still be complete if it motivates the pattern, defines the terms, walks through one full example, and gives the learner a task they cannot complete by skimming.

## What to borrow from data structures

The strongest patterns in [[dsa/02-data-structures/01-arrays|arrays]], [[dsa/02-data-structures/02-dynamic-arrays|dynamic arrays]], and [[dsa/02-data-structures/03-hash-maps|hash maps]] are:

- Motivation before machinery: what problem does this solve?
- Plain-English definitions before a wall of terminology.
- Small diagrams with concrete values, not only abstractions.
- Operations broken into visible steps.
- Tradeoffs and questions that expose misunderstandings.

Borrow the teaching moves, not every heading or claim. The source lessons are inspiration, not a correctness oracle. Constant-time work is not literally instantaneous; memory layout depends on the language and representation; average-case behaviour needs assumptions.

The next improvement is **independent implementation**. A learner should not have to invent the setup, inputs, expected behaviour, and practice task after reading the explanation.

## The learning sequence

### 1. Set a clear starting point

State the prerequisites as things the learner can already do, with a small number of direct links. Define unfamiliar terms locally; do not send the reader through six other notes to understand the opening paragraph.

Give two to four observable outcomes. “Understand BFS” is vague. “Trace its queue, implement it, and explain why the returned path uses the fewest edges” is testable.

Name the artifact: a working function, a proof, a circuit measurement, a query plan, a design with justified tradeoffs. State tools and versions where relevant. Do not promise “zero prior background” for an intermediate lesson.

### 2. Open with the kid version, then a problem worth solving

Every lesson opens with **a kid version**: the whole idea explained in a few sentences a twelve-year-old could follow, using an everyday picture (a toolbox, a queue at a shop, a library card index). It comes before the definitions and before any code. Then say where the picture stops matching the real mechanism — an analogy left unchecked teaches the wrong edge cases. See [Writing conventions](#the-kid-version-comes-first).

After the kid version, use one concrete situation and show why the simpler approach is insufficient.

A short motivating example is enough. Three production name-drops are not a substitute for a problem the reader can work through.

### 3. Build the mechanism one step at a time

Introduce terms when they become necessary. Use a small glossary when several new terms arrive together; do not force a glossary onto a lesson with no new vocabulary.

Use one running example where possible:

1. Show its initial state.
2. Perform one operation.
3. Show what changed and what stayed true.
4. Explain why the next step follows.
5. Pause for a prediction before revealing the result.

Define symbols before equations. For code, explain decisions, boundaries, and state transitions rather than commenting `i += 1` as “increment i”. Include the invariant or correctness argument at the level the lesson requires.

### 4. Give one complete worked example

Clearly distinguish **runnable example**, **fragment**, **pseudocode**, and **exercise checks**.

A runnable example includes:

- All imports and definitions, a small input fixture, and any required dependencies.
- A filename and exact command, with the working directory explained.
- Expected output or assertions; describe nondeterminism rather than promising an exact order.
- Error and boundary cases relevant to the mechanism.
- Safety boundaries and cleanup for files, databases, cloud resources, or hardware.

Prefer local, bounded experiments without paid services or credentials. Never require destructive operations on a live system. Label simplified teaching models and state what they deliberately omit.

### 5. Gradually remove the help

Use this progression rather than providing only worked solutions:

| Stage       | What the learner does                             | What the note supplies                               |
| ----------- | ------------------------------------------------- | ---------------------------------------------------- |
| Predict     | Trace the next state or output before running     | A small input and a place to compare the result      |
| Reconstruct | Rebuild the core idea with the worked code closed | A contract or diagram, not another full solution     |
| Modify      | Make one guided change                            | A focused hint and an expected observation           |
| Apply       | Implement a new variation independently           | Inputs, outputs, constraints, edge cases, and checks |
| Explain     | Justify correctness and diagnose a failure        | Questions and a completion checklist                 |

Keep hints and answers **after the attempt**, under a clearly labelled heading or in the existing solutions note. Give conceptual explanations and enough debugging guidance for a stuck learner; withholding the finished exercise implementation is not a reason to withhold feedback.

Do not duplicate a course's existing exercise bank. Link the relevant exercise at the point the learner is ready for it. If the existing exercise jumps too far ahead, add a smaller bridge inside the lesson.

### 6. Explain limits without interrupting the first pass

Connect the mechanism to actual use after the core model is clear. Keep advanced applications and operational tuning in an explicitly optional section when they are not needed for the first implementation.

Discuss complexity where it is useful, with the input size and assumptions defined. Do not force best/average/worst Big-O tables into a history, design, or hardware lesson. For those topics, cost, evidence, constraints, measurement error, and failure modes may be more appropriate.

Separate illustrative values from measured results. A claimed speedup needs the workload, environment, method, and result; otherwise describe what to measure, not what result the learner must obtain.

### 7. End with a demonstrable finish line

A lesson is finished when the learner can explain the idea, trace an unfamiliar input, produce the artifact independently, and check it against the contract. Reading to the bottom is not the finish line.

Point to the next lesson and explain the dependency. Keep a short recap suitable for later lookup so the expanded teaching material remains useful as a knowledge base.

## Writing conventions

These are not stylistic preferences; each one exists because its absence made a
lesson harder to read.

### Write it the way the author writes

This one comes first because it matters most. The model is the author's own
university notes, [[computer-graphics/01-introduction-to-computer-graphics|Introduction to Computer Graphics]],
which he wrote himself. Lessons written by AI have been too technical and too
disconnected; his are easy to read because of how one idea leads to the next.
Read that lesson before writing or rewriting any other.

1. **Say what it is, straight away.** The first line after the title is a plain
   definition: "Computer graphics is the field of making a computer create, store,
   change and display pictures on a screen, using programming." Level, contents and
   course position go at the end, in "About this lesson".
2. **Each idea hands off to the next.** End a part by saying why the next part is
   needed: "And this is why graphics cares so much about speed. If the picture cannot
   be redrawn fast enough, the loop breaks… That is what leads us into display
   hardware and refresh rate." Open the next part by recalling the earlier one:
   "Remember the feedback loop from lesson 1? The screen is the computer's half of it."
   A reader should never wonder why a section is there.
3. **Carry one example all the way through.** The architect appears for visual
   problem solving (comprehend, conceive, communicate) and comes back for command-based
   versus interactive computing ("move wall 2 meters left"). One example the reader
   already knows beats three new ones.
4. **Describe the idea first, then give its name.** "The computer does not just carry
   out your orders. It extends what you can do… Augmentation is the name for what
   interactive computing does."
5. **Talk to the reader.** Short sentences, everyday examples (dragging a window,
   typing a command in a terminal) before any hardware or maths, and the author's
   Nigerian English warmth where it fits: "it can make you go like ehn? But it's not
   that deep sha…", "Okay!!!!!", "Remember this one:".
6. **Keep the exam line separate.** When a formal definition matters for an exam,
   give it as its own line, after the plain explanation: "A one-sentence version for
   an exam: …"
7. **Aim lower than feels natural.** If a sentence needs a term the reader hasn't met,
   the sentence is too early. Lists and comparison tables are for things to memorise,
   after the idea is understood.
8. **When the author gives his own text, use his exact words.** Only add `##`
   headings (taken from his own phrases, so the platform can cut bites) and fix
   clear typos.

### The kid version comes first

*Optional when the lesson already opens the way the rule above describes: a lesson
written like Graphics Systems and Display Hardware doesn't need one.*

Before the terms, before the mechanism, explain the whole idea as if to a
twelve-year-old: three to six sentences, one everyday picture, no jargon. It gives
the reader a hook to hang every later detail on, and it is a test for the writer —
if you cannot write the kid version, you do not yet understand the topic well
enough to teach it.

End it with **where the analogy stops working**, in one or two sentences. That
sentence is not optional: it is where the reader learns the real mechanism's
edge, instead of carrying the analogy's.

> **The kid version.** You're organising a toolbox. By type: all screwdrivers in
> one drawer, all wrenches in another. By job: a "bike box" holding everything
> for the bike. To fix the bike you open four drawers, or grab one box...
>
> **Where the analogy stops working.** A box on a shelf does nothing until you
> plug it in — in software, every feature must be registered with the app somewhere.

Call the section "The kid version" (or "The kid version first") so it is easy to
find and skip on a re-read.

### Definitions are a numbered list in plain English

Not a table. A table forces definitions into fragments, and a fragment reads as
though the reader already knows the term. Give each one a full sentence, and give
a synonym its own sentence:

> 1. **Vertex**: This is also known as a **node**. This is a point in a graph
>    that can be connected to other points by edges.

Use a heading that says what it is — "Terms used in graphs" — rather than
"Terminology".

### State a result in words before you write the formula

The sentence comes first, the symbols second. The formula is a compression of the
sentence, and a reader who has not yet got the sentence cannot decompress it:

> The handshaking lemma states that in any undirected graph, the sum of all the
> vertex degrees is exactly twice the total number of edges. It is a fundamental
> principle because each edge connects exactly two vertices.
>
> $$\sum_{v \in V} \deg(v) = 2\lvert E\rvert$$

### Every acronym carries its full meaning, on every use

A reader arriving mid-page from a search, or returning weeks later, must be able
to find out what an acronym means without scrolling back. An expansion given once
at the top of a lesson does not serve them.

**You do not write the expansion by hand.** Write the bare acronym in the
markdown, and the `abbreviations` plugin wraps every occurrence in `<abbr>` at
build time, so hovering shows the full meaning. Writing `API (application
programming interface)` at all ~3,100 acronym occurrences in this vault would add
roughly 167 KB of markup and make the notes unpleasant to edit.

**Your one job is to keep the list current — and a script checks it.** If you use an
acronym that is not in `quartz-plugins/abbreviations/glossary.json`, add it. One entry
makes it work everywhere at once, and it appears on the published [[glossary]] page too.
**This covers notation as well as acronyms**: `p50`, `p95`, `p99` and the like are in the
glossary for the same reason. Before a lesson counts as converted, this must report nothing:

```bash
python3 quartz-plugins/abbreviations/check.py path/to/lesson.md
```

Run with no arguments, it checks every lesson the SWE courses link to, and their companions.

**Two places still spell it out in the prose:**

1. **The definition-list entry** that introduces the term, because there the
   expansion *is* the definition: "**DAG (directed acyclic graph)**: The letters
   stand for those three words. It is a directed graph with no directed cycle..."
2. **Anywhere the expansion carries the argument**, where the words themselves are
   doing explanatory work rather than just naming the thing.

**Where the tooltips do and don't appear.** The plugin runs when the site is built, so the
tooltips exist on the **published site** only. Three places don't get them:

- **Headings** — skipped on purpose, because a tooltip inside a heading breaks the table of contents. Avoid acronyms in headings, or spell them out there.
- **Obsidian, and the raw markdown** — no build step, so `SLO` is just "SLO". `glossary.json` is the lookup.
- **Touch devices** — no hover, which is why the [[glossary]] page exists.

A local AI study partner reading the raw files has the same gap; point it at `glossary.json` (the [[tools/openclaw-study-partner/index|study-partner setup]] does).

### The abstract data type comes before the implementation

For any data structure, describe **what it does** before showing **how it is
built**. List the operations with a plain-English line each, saying what the
operation is for and what it costs:

> `adjacent(v, u)` — Returns `true` if there is an edge between `v` and `u`.
> Use it when you have two specific vertices and want to know whether they are
> joined. Cost depends on the representation: $O(1)$ for an adjacency matrix,
> $O(\deg v)$ for an adjacency list.

Code answers "how". The reader needs "what" and "why" first, and cannot reliably
reconstruct either by reading an implementation.

## The lesson shape

Two folders in this vault reached university quality by slightly different routes, and the standard is the union of both, not a choice between them.

`dsa/02-data-structures/` contributes the **visual teaching**: a physical analogy up front, a plain-English terminology table before any jargon is used, ASCII diagrams carrying real numbers rather than abstract letters, an explicit pitfalls list, and self-assessment questions whose answers are hidden behind `<details>` so the reader must attempt first.

`dsa/04-patterns/` contributes the **bridge to independent work**: a difficulty tag, prerequisites stated as things the reader can already do, observable outcomes, a complete runnable artifact with its exact command and expected output, an independent task with a "done when" condition, and answers placed after the attempt.

A lesson meeting this standard has both halves. Explanation without the bridge produces a reader who recognises the heading; the bridge without the explanation produces a reader who cannot start.

Use meaningful topic-specific headings and drop sections that a given topic genuinely does not need. This is a scaffold, not a form to fill in.

```markdown
# Module N: Topic (the one-phrase hook)

**One plain sentence saying what the thing is.** Then one or two everyday sentences on
where the reader has already met it. No level tag, contents summary, course position
or source up here: a reader opening the lesson wants to know what it is first.

## Before you start

Prerequisites as things you can already do, each with one direct link.
"After this lesson you will be able to:" — two to four observable outcomes.
Study route: which sections to read, where to stop and attempt.

## The kid version

The whole idea in three to six sentences a twelve-year-old could follow, with one
everyday picture. Then: where the analogy stops working.

## 1. Why this exists (real-world motivation)

One concrete situation. Show why the simpler approach is insufficient.

## Terms used in <topic>

A **numbered list**, not a table. One entry per term, written in full sentences
and plain English. Give the synonym its own sentence. Define every term before
the section that uses it, and never define a term using two other undefined ones.

1. **Term**: This is also known as a **synonym**. This is <what it is, in words a
   beginner already has>. <A concrete example.>

## The abstract data type

Before any code: the operations the structure supports, what each one is *for*,
and what it costs. One line of explanation per operation, in plain English.

## 3..N. How it works — step by step

One running example. Show initial state, perform one operation, show what
changed and what stayed true, explain why the next step follows.
Diagrams carry concrete values. Define symbols before equations.
Pause for a prediction before revealing a result.

## Worked example

Complete setup, exact command and working directory, expected output or
measurement, boundary cases, and any safety limits.

## Common pitfalls and traps

The mistakes this topic actually produces, named explicitly.

## Check your understanding

Every lesson ends with this. 3 to 6 questions, each tagged
<!-- q: TYPE id="…" --> so EruditeMe can make it interactive.
See "End-of-lesson questions" below for the format.

## Practice — independent task

Inputs, expected behaviour, edge cases, and an explicit "Done when".
Link the course's existing exercise bank instead of duplicating it.

## Tradeoffs, limits and extensions

Assumptions, failure modes, and optional depth kept out of the entry path.

## Before moving on

Demonstrable completion criteria, a short recap for later lookup, and the
next lesson with the dependency named.

## Related

## About this lesson

**Level**, what the lesson covers, where it sits in the course and what to read in
which order, and its sources. Bookkeeping goes last, as in a subject index.
```

For a mathematics lesson, substitute a worked derivation and an independent proof or problem for the runnable code. For hardware and physics, substitute a safe bounded setup, a diagram, a predicted measurement with its uncertainty, and what a disagreeing result would mean. The learning sequence stays the same; Python is not a universal requirement.

## End-of-lesson questions

Every lesson ends with questions you answer, not just read. The section is `## Check your understanding`, placed just before `## Before moving on`. EruditeMe turns it into an interactive quiz, showing one question per screen. On the Quartz site it stays a normal numbered list with hidden answers.

There are seven kinds of question:

1. **Multiple choice (`mcq`).** You pick from 2 to 6 options. If more than one option is right, the app says "choose all that apply".
2. **Fixed answer (`exact`).** You type a number or a word, and it is marked right or wrong straight away.
3. **Fill in the gaps (`gap`).** A sentence with one or more blanks written `___`. You type a word into each blank.
4. **Theory (`open`).** You write your answer in your own words, then compare it with the model answer.
5. **Draw on paper (`sketch`).** You draw the graph or shape on paper, then compare it with the answer picture and a short "What to check" list, and mark yourself.
6. **Pixel grid (`grid`).** You click the cells a raster algorithm would light, such as a Bresenham line, a circle octant or the pixels that survive clipping, and the app checks the set.
7. **Points on axes (`points`).** You tap to place points on numbered axes, such as a transformed triangle's corners, clipped end points or de Casteljau points, and each must land within a small distance of the right spot.

Each question is one numbered item. Its first line starts with a marker after `N. `. The question follows, indented, and it can run over several lines, with code or maths in it. The `<details>` block always comes last. It holds the explanation, and for an `open` question it is the model answer.

```markdown
## Check your understanding
<!-- bite: … -->

Try each one before you open the answer.

1. <!-- q: mcq id="3f9a1c27" -->
   K = 3. The three nearest neighbours are setosa, versicolor, versicolor. What does KNN predict?

   - [ ] setosa
   - [x] versicolor
   - [ ] virginica

   <details><summary>Answer</summary>

   Versicolor. Classification is a majority vote, and two of the three are versicolor.

   </details>

2. <!-- q: exact id="b2e04d91" answer="0.5" accept="1/2|half" tolerance="0.01" -->
   …

3. <!-- q: open id="7c1d5e08" -->
   Why is KNN called a lazy learner?

   <details><summary>Answer</summary>

   Model answer…

   </details>
```

The rules:

- **`id`** is 8 hex characters, unique within the lesson. Never change it once the lesson is published, because your saved answers hang on it. Generate one with `python3 -c "import secrets; print(secrets.token_hex(4))"`.
- **`mcq` options** are one task list (`- [ ]` / `- [x]`) between the question and `<details>`. Each option fits on one line. Several `[x]` make the question multi-select.
- **`exact`** compares your answer without caring about capitals, spaces, a full stop at the end, or `−` versus `-`. So `(3, 2)` matches `(3,2)`, and you don't need spacing variants in `accept=`. If both sides are numbers, they are compared as numbers, so 10 and 10.0 match. The app does no maths on fractions or percentages, so list forms like `3/4` or `75%` in `accept=`. `accept="a|b"` lists other answers that also count.
- **Rounded answers use `sigfigs`.** Engineering answers are often given to different numbers of decimal places or significant figures, so for any answer that isn't a whole number or an exact short decimal, write `answer=` at full precision and add `sigfigs="N"`, the fewest significant figures the learner must give. A number is accepted when it has at least N significant figures and is correctly rounded, meaning it is within half a unit of its own last digit from the true value. For example, with `answer="0.909091" sigfigs="2"`, the answers 0.91, 0.909 and 0.9091 pass. 0.9 fails because it has too few figures, and 0.90 fails because it is rounded wrong. Leading zeros don't count as significant figures. Trailing zeros in a whole number can be read either way, so "120" counts as 2 or 3 figures, and it passes if either reading passes. `sigfigs` is a whole number from 1 to 15. On a `gap` it applies to every numeric blank. An answer typed exactly as listed in `answer=` or `accept=` always passes, so `-0.5` in `accept=` passes even with `sigfigs="2"`. The app tells the learner how many figures to give, so don't put that in the question.
- **`tolerance="0.01"`** allows a fixed error instead. If both `sigfigs` and `tolerance` are set, passing either is enough. With neither, a number must be exactly equal, which is right for whole-number answers like 50 or 256.
- **`gap`** writes each blank as `___` (three underscores) in the question. `answers=` gives one answer per blank, in order, separated by `;`. Use `|` inside one blank for other answers that also count: `answers="binary;multiclass|multi-class"`. Each blank is marked like an `exact` answer.
- **`sketch`** has no answer attribute. Its `<details>` holds the answer picture (`![…](images/name.svg)`) and a "What to check" list of the things a correct drawing must show.
- **`grid`** takes `cols` and `rows` (keep cols at 14 or fewer so it fits a phone), `answer` as space-separated `x,y` cells with the origin at the bottom-left, optional `given` cells that start lit and are locked (they must be in `answer`), optional `line="x0,y0 x1,y1"` for a faint guide, and `axes="true"` to number the rows and columns. The lit set must equal `answer` exactly. Compute `answer` with the same code that draws the lesson's diagrams, never by hand.
- **`points`** takes `xmin`, `xmax`, `ymin`, `ymax` (both axes use the same scale, so keep the ranges close to the shape), `step` for grid lines (at most 50 per axis), optional `snap`, `answer` as space-separated `x,y` points (1 to 12, all inside the axes), optional `labels="A',B',C'"` to make the points be placed and marked in that order, `tolerance` in data units (default half the step), optional `ghost` points drawn faintly for reference (such as the shape before a transform), and `polygon="true"` to join the points into a closed shape. If `snap` is set, every answer point must be within `tolerance` of a snap point. Compute the answers with code.
- **Attribute values** always go in double quotes.
- **A question with no marker** counts as `open`, so older lessons still work.
- **A question the app can't mark** also becomes `open`, and EruditeMe shows an author warning. That covers an `mcq` with no `[x]` or outside 2 to 6 options, an `exact` with no `answer=`, a `gap` whose blank count doesn't match its answers, and a missing or duplicate `id`. A blank is exactly three underscores; four or more is not a blank.
- **Every question stands on its own.** EruditeMe shows one question per screen, so a question can't lean on the lesson's tables, an earlier question ("Same data…"), or memory of a worked example. Put every value the learner needs in the question itself: a small markdown table for a dataset, the numbers for a calculation, or the picture (`![…](…svg)`) for "use this tree". Prefer fresh numbers to the lesson's own example, so the learner applies the method instead of recalling the answer.
- **Mix the kinds.** Use `mcq`, `exact` and `gap` for facts, terms and calculations, and `open` for "why" and "explain" questions.
- **More than 6 questions** get split into two `##` sections, each with its own bite marker, so each quiz takes about 3 to 4 minutes. The second heading is `## Check your understanding:` followed by a subtitle, for example `## Check your understanding: worked problems` for the calculation set in maths-heavy lessons. The colon matters: "Check your understanding of X" is not read as a quiz.
- **Pick `sigfigs` so a wrong value can't round to a right-looking one.** For 0.985 at 2 figures, "1.0" would pass, so ask for 3.

## Diagrams

A picture is worth adding where the reader would otherwise draw it themselves: pixel grids, trees, curves, regions, before-and-after transforms. Keep the vault light and the pictures exact:

- **Generate them from code, never by hand or with an image model.** Each subject's diagrams come from one script, `scripts/diagrams/<subject>.py`, which runs the same algorithm the lesson teaches, so a picture can never disagree with the worked example. Rerun the script after changing it.
- **No drawings made of text characters.** A picture typed with `│ ─ ╱ ■ →` inside a code block shows as code in the app and on phones. Draw it in the subject's diagram script instead. Pipelines and flows become Graphviz flowcharts (`flowchart()` in `scripts/diagrams/svgkit.py`). Pseudocode and formulas stay as code.
- **SVG, not PNG.** A diagram is a few kilobytes of text and stays sharp at any size. Each one draws its own light background, so it reads in dark mode too.
- **Store them in `<subject>/images/`** and embed them with plain markdown on their own line: `![Alt text that says what the picture shows](images/name.svg)`. The alt text is a full sentence describing the picture, for screen readers and for anyone the image fails to load for.
- **Inside the bite, or its own bite, depending on fit.** If the picture explains that bite and the bite still fits on one screen with it, put it inside, with a sentence saying what to look at. If adding it would make the bite scroll (for example after a full worked table), give it its own small `##` bite right after, such as "Seeing the shallow line on the grid". One picture per bite either way.

## Companion lessons in other languages

A lesson teaches in **one** language — TypeScript for software-engineering topics, Python for data and maths, C for operating systems — so it stays readable. Its **companion** shows the same idea in the vault's other languages: TypeScript/JavaScript, Python, Go, Java, Rust, C, C++ and C#. [[LANGUAGE-COVERAGE|Language coverage]] tracks which lessons have one.

- **Name and place.** A lesson with labs or a companion is a **folder**: its text in `index.md`, the companion in `in-other-languages.md` beside it, and its labs in `labs/<language>/` — for example `backend/03-structuring-a-backend/03-dependency-injection-and-wiring/`. A lesson with neither stays a single file. The companion's first lines say `A companion to [[<lesson path>/index|…]]` — that's how the tracker finds it.
- **One section per language, the same shape each time:** the idiomatic way to do it, what the language *changes* about the idea, and one verified example. Write what's different, not a line-by-line translation — if a section would only translate syntax, keep it to a few sentences.
- **Only where the language makes sense.** C and C++ get a section when the idea exists there (memory, concurrency, boundaries, error handling). A web-framework idea in C, or pandas in Rust, gets one sentence saying what's used instead, or nothing.
- **Every example runs.** Each language's code lives in a lab beside the lesson (`<lesson folder>/labs/<language>/`) and is checked by `python3 labs/run.py`. Lab folders aren't published on the site, so link the lab's path to its folder on GitHub: [`<lesson folder>/labs/<language>/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/<lesson folder>/labs/<language>). C# labs run in the .NET SDK container.
- **The full lesson shape still applies** — a short kid version, terms, checks and a practice task — but the main lesson holds the explanation; the companion assumes it's been read.

## Subjects, lessons, bites, courses and study plans

The vault and the EruditeMe platform use these five words, and each one means one thing.

1. **Subject**: A subject is a top-level folder such as `backend/` or `computer-graphics/`. It holds everything about one field, deep and complete, in reading order. It is never on a clock. A **subject group** is a folder whose `index.md` has `subject_group: true` in its frontmatter, such as `languages/`, `backend/frameworks/` or `frontend/frameworks/`. It is not a subject itself, and each folder inside it with its own `index.md` is a subject, numbered or not (`languages/01-java/` is the subject "Java", `frontend/frameworks/gsap/` is "GSAP"). A group can sit inside a subject; the outer subject (Frontend, Backend) then leaves out the lessons that belong to the inner ones. `subject: false` in a child's frontmatter holds it back, for example until it has at least three lessons. A subject about a tool is **named after the tool**, with the language in brackets: "Spring Boot (Java Backend)", not "Java Backend". Each tool gets its own subject ("FastAPI (Python Backend)", "Django (Python Backend)"), and each one teaches the whole of its parent subject in that tool's own way rather than sharing a folder with its rivals. Nothing moves on disk.
2. **Lesson**: A lesson is one file or folder inside a subject, such as `computer-graphics/03-line-drawing-and-antialiasing.md`. It takes 10–15 minutes and follows the lesson shape above. Lessons are only ever edited in the vault. A file counts as a lesson when its name (or, for a folder lesson, its folder's name) starts with a two-digit number and it holds no numbered files of its own. Section indexes, companions, labs, interview banks, question banks and solutions don't count, and `lesson: false` in the frontmatter leaves out anything else. `scripts/lesson-ids.py` applies this rule and gives every lesson an `id`.
3. **Bite**: A bite is a 3–4 minute piece of a lesson, usually one `##` section with its quiz questions. The platform cuts lessons into bites when it builds, so bites exist only on the platform. A finished bite is what counts towards a streak. A bite should fit on one screen without scrolling. Only go longer when the idea really can't be understood in less. When a `##` section runs past a screen, split it into more `##` sections (for example, one per example pair, one per sub-type), and open each new section with a sentence that says what it is. Text above a lesson's first `##` and anything under "Before you start" never reaches the app as a bite, so content the learner must see (like a list of the types) needs its own `##` section. The first bite is the intro: a `## What <thing> is` section (right after "Before you start") that says in plain words what the lesson's thing is and what's coming, before any detail. The line under the `# Title` is one sentence at most, because the app shows it on top of the first bite. Run `python3 scripts/long-bites.py <subject>` to list bites that probably scroll and lessons without an intro bite. In a subject or section index, each lesson link shows the lesson's file number, like `[[backend/frameworks/net-http/02-routing|02 — Routing]]`, because EruditeMe takes the lesson title it shows from that link text. Number only links to this subject's own lessons, not links to other subjects.
4. **Course**: A course is a short, ordered list of lessons picked from any subjects, with one promise: "after this, you can do X". It holds no lessons of its own, only links to them, so one lesson can sit in many courses. For example, "Structure a Backend Properly" links six lessons from `backend/` and `concepts/`. A course has no dates and no owner.
5. **Study plan**: A study plan is one person putting one or more courses on their own calendar, with a pace, start date and reason. For example, "4 bites a day, weekdays, from Monday, to explain backend structure in interviews". Study plans are personal: in the vault they live in `learning/`, and on the platform they are a per-user setting.

Older text in the vault says "course index" where it means a **subject** index, and SWE 101–103 are study plans with their courses built in. Both get renamed as files are revised.

## When a topic is too big for one lesson

This is a rule for the whole vault. A topic usually makes one lesson, but when a topic is too big to learn in one 10–15 minute sitting, split it into numbered parts: **Regression 1, Regression 2, Regression 3**. Don't squeeze it into one long lesson, and don't cut the explanation to make it fit.

1. **When to split.** Split when a lesson runs well past 15 minutes: roughly 1,500 words of prose, or a worked example long enough to need its own sitting. A hand calculation with many steps counts as long even when the word count is small. Split before you write if you can already see the topic is that big.
2. **Where to cut.** Cut where the topic naturally pauses, so each part has one job a learner can finish. A long worked example can be its own part ("Decision Trees 2: Play Tennis, Choosing the Root Node", then "Decision Trees 3: Play Tennis, Growing the Branches"). Never cut a derivation or a worked example in the middle of a step.
3. **How to name it.** The topic name, the part number, then a colon and what this part does: `# Decision Trees 4: Gini Impurity and the Weekend Decision`. Files follow the folder's numbering with the part in the name: `08-decision-trees-4.md`. Every part is a full lesson with its own id, "Before you start", checks and "About this lesson", which says "Part 4 of 6 on decision trees".
4. **How the parts connect.** Each part's "Before you start" names the part before it, and its "Before moving on" hands off to the next with the reason it is needed, the same way each idea hands off to the next inside a lesson. The subject or section index lists every part, with one plain line each.
5. **Keep ids and links.** When an existing lesson is split, the old lesson's `id` goes to the part that keeps most of its content, its sections keep their bite ids, and every link to the old path is updated across the vault in the same change.

[[machine-learning/03-classical-ml/index|Classical ML]] is the first section built this way: KNN 1–2, Decision Trees 1–6, Bayesian Networks 1–2 and Clustering 1–2.

## The course around the lessons

A course index should specify the starting knowledge, dependency-aware reading order, practical stopping points, and a cumulative project or assessment. Distinguish core lessons from optional depth. Numbered filenames alone do not establish prerequisites.

### A course index opens with what the subject is

Someone opening a course for the first time has to know what the subject *is* before anything else. Write the index for that reader, not for someone who already knows the field.

1. **Start with one plain sentence that says what the subject is,** in words a beginner already knows. "Computer graphics is drawing pictures on a computer screen with the help of programming." Then two or three sentences on where the reader has already met it in everyday life.
2. **No unexplained terms above the reading list.** "Rasterisation, shading and ray tracing" means nothing yet. Say what the reader will be able to *do*, in plain words, and let the lessons introduce the names.
3. **Each lesson in the reading list gets one plain line** saying what it teaches. Keep jargon out of the line, or explain it there.
4. **Beginner material comes first** in the list, even if it was written later. Say clearly where to start.
5. **Bold sparingly.** When half the page is bold, nothing stands out.
6. **Bookkeeping goes in an "About this course" section at the very end:** word counts, when it was written or extended, the source it was built from, and what's missing. A reader studying the subject doesn't need it first.
7. **Leave out why the course was chosen or how it fits the vault's plans.** "The weakest fit of the five domains in this batch" is a note to the author, not to a learner. Links to related courses go in a short "Related" list, with one plain line each.

The SSG 511 study notes are the model for tone: plain definitions, everyday examples, one idea at a time. [[computer-graphics/index|Computer Graphics]] is the first index rewritten this way.

Revision should preserve useful existing detail, links, and file locations. Fix inaccurate explanations while rewriting, but do not expand the task into unrelated topics. If a lesson becomes too big for one sitting, split it into numbered parts (see [When a topic is too big for one lesson](#when-a-topic-is-too-big-for-one-lesson)) and update every link to it.

## Review checklist

- [ ] The prerequisites and outcomes are explicit and realistic.
- [ ] The lesson fits one 10–15 minute sitting; a bigger topic is split into numbered parts (Topic 1, Topic 2…) that each hand off to the next.
- [ ] A course index opens with a plain sentence saying what the subject is, and keeps word counts and build history at the end.
- [ ] The lesson reads like the author's own notes ("Write it the way the author writes"): each part ends by leading into the next, one example runs through, ideas come before their names.
- [ ] A lesson opens with a plain sentence saying what the thing is. Its level, contents summary, course position and sources are in "About this lesson" at the end.
- [ ] A kid version opens the lesson, and says where its analogy stops working.
- [ ] Definitions are a numbered list in plain full sentences, not a table.
- [ ] Every result is stated in words before its formula appears.
- [ ] Every acronym and notation such as `p99` is in `glossary.json` — `check.py` reports nothing for the lesson.
- [ ] For a data structure, the abstract data type and its operations come before any code.
- [ ] The running example teaches the steps between intuition and formalism.
- [ ] The learner can execute the worked example without guessing missing setup.
- [ ] At least one task requires prediction and one requires independent work.
- [ ] Checks cover meaningful boundaries and explain what success means.
- [ ] Hints/answers are separate from the attempt; existing practice is linked locally.
- [ ] Claims distinguish the model, implementation details, assumptions, and evidence.
- [ ] Experiments are safe, bounded, and labelled with any unverified requirements.
- [ ] Core and advanced material have a clear reading route.
- [ ] Existing useful links still resolve; runnable examples were checked where possible.

**Validation is not the same as learning success.** Executed examples establish that the supplied artifacts behave as checked. A real closed-book study attempt establishes whether the explanation provides enough support. Record where the learner gets stuck before repeating the format across a whole domain.

## First pilots and rollout

- [[languages/06-python/06-iterators-generators-and-comprehensions|Python iterators and generators]] — tracing suspended state, then implementing a lazy variation.
- [[databases/03-storage-and-page-layout|Database page layout]] — tracing byte offsets, then implementing compaction with stable slots.

These are revised pilots, not a declaration that either full course is converted. [[BUILD-PLAN|The build plan]] tracks the remaining work.
