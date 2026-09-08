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

The strongest patterns in [[foundations/dsa/04-data-structures/01-arrays|arrays]], [[foundations/dsa/04-data-structures/02-dynamic-arrays|dynamic arrays]], and [[foundations/dsa/04-data-structures/03-hash-maps|hash maps]] are:

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

### 2. Begin with a problem worth solving

Use one concrete situation and show why the simpler approach is insufficient. An analogy can provide intuition, but explain where it stops matching the real mechanism.

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

## A flexible lesson outline

Use meaningful topic-specific headings. This is a scaffold, not a requirement to paste identical sections into every note.

```markdown
# Topic

[Difficulty and source/experience status]

## Before you start

Prerequisites, outcomes, artifact, study route.

## The problem

Concrete motivation and the simpler approach's limitation.

## How it works

Terms, diagram, state-by-state example, prediction, reasoning.

## Worked example

Complete setup, implementation or derivation, expected results.

## Try it yourself

Reconstruction, guided change, independent task and checks.

## Hints and answers — after your attempt

Progressive help and explanations, or links to existing solutions.

## Tradeoffs and extensions

Assumptions, failure modes, real-world connections, optional depth.

## Before moving on

Demonstrable completion criteria, recap, next lesson.

## Related and sources

Focused links and references for technical claims.
```

For a mathematics lesson, substitute a worked derivation and an independent proof/problem for runnable code. For hardware, use a safe setup, wiring diagram, predicted measurement, uncertainty, and a bounded experiment. The learning sequence stays the same; Python is not a universal requirement.

## The course around the lessons

A course index should specify the starting knowledge, dependency-aware reading order, practical stopping points, and a cumulative project or assessment. Distinguish core lessons from optional depth. Numbered filenames alone do not establish prerequisites.

Revision should preserve useful existing detail, links, and file locations. Fix inaccurate explanations while rewriting, but do not expand the task into unrelated topics. If a lesson becomes unwieldy, separate core and extension reading before splitting files and breaking links.

## Review checklist

- [ ] The prerequisites and outcomes are explicit and realistic.
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
