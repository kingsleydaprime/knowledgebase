---
id: a15b7eb1-6bdb-4285-b8a3-7a394322526f
---

# The Work Breakdown Structure

A work breakdown structure (WBS) is a big project split into smaller and smaller pieces until each piece is a job you can estimate, schedule and give to someone.

## Before you start
<!-- bite: 209ab0b6-450e-4fb7-bab8-0b5361b14039 -->

You should have read [[planning-and-scheduling/05-pmbok-2|05 — PMBOK 2]].

After this lesson you will be able to:

1. explain why a WBS comes before any schedule;
2. break a small project into a WBS down to activity level;
3. say what a WBS dictionary is and what it holds.

## What a work breakdown structure is
<!-- bite: 68f838bb-99c8-4640-9ce8-4e2c863f588f -->

You can't schedule what you haven't listed. Ask someone "how long will the fence take?" and they guess. Ask them "how long to dig the holes? to buy the wood? to paint?" and the answers get much better, because small jobs are easier to picture than big ones.

That is the whole idea of a WBS. A major cause of project failure is wrong estimates of time and cost, and the WBS is the best tool to fix that. You keep splitting a big, complicated task into smaller tasks until you reach a level that can't sensibly be split any further. Those lowest-level pieces are the **activities** that go into the network diagrams of part 3.

## The fence and gate, broken down
<!-- bite: 0a5db9ad-0a39-4b1a-b951-4f82bd1c6a0a -->

Here is the fence and gate as a WBS. The whole project is at the top. The next level splits it by what is being produced: the fence, the gate, the paint job. The level under that holds the activities.

![A work breakdown structure tree: the Fence and gate project at the top splits into Fence, Gate and Painting; Fence holds A Dig holes, B Buy wood and D Erect fence; Gate holds C Buy gate and F Erect gate; Painting holds E Buy paint, G Paint fence and H Paint gate](images/ps-wbs-fence.svg)

## What each level of the tree does
<!-- bite: ee5db258-44ea-4c09-8744-f73be057dd7c -->

Each level of the fence's WBS has its own job.

Look at what each level does:

1. **Level 1** is the whole project. Nobody can estimate it well in one go.
2. **Level 2** is the major parts, the deliverables: fence, gate, painting.
3. **Level 3** is the activities: eight jobs, each with a person and a time. These are the eight lettered activities A to H that we'll schedule for the rest of the subject.

Every activity you later draw, estimate, crash or level starts its life as a box at the bottom of this tree.

## Terms used in the WBS
<!-- bite: 0cd64f2f-a12c-425a-8d9d-2e34d7f0a2ff -->

1. **Deliverable**: This is a product or result the project must hand over, such as the gate.
2. **Work package**: This is the lowest level of the WBS that is managed as one unit, with its own cost and owner. In a small project the work packages are the activities themselves.
3. **Decomposition**: This is the technique of splitting a piece of work into smaller pieces. Building a WBS is decomposition.
4. **WBS dictionary**: This is the document that explains every element of the WBS, so a vague box name can't be misread.

## The WBS dictionary
<!-- bite: db56341f-7193-43c7-818a-d1cd3e382204 -->

A box that says "Painting" can mean many things. Which colour? How many coats? Does it include the gate? The WBS dictionary answers that for every element.

It describes each element's milestones, deliverables, activities and scope, and sometimes its dates, resources, cost and quality requirements. PMI's definition:

A one-sentence version for an exam: the WBS dictionary is a document that provides detailed deliverable, activity and scheduling information about each component in the work breakdown structure.

For "G Paint fence" an entry might say: two coats of white exterior paint on all 40 metres; starts after the gate is up; two days; one painter; done when the owner signs off the finish.

## Why estimating at the bottom works
<!-- bite: 38b8e350-e267-4149-b99a-fd467d370f11 -->

Estimating at the lowest level is what makes durations and costs believable. There are three reasons.

1. **Small jobs are easier to picture.** "Dig 20 holes" is a thing you can imagine doing; "build a fence" isn't.
2. **Nothing is forgotten.** Splitting forces you to ask "what else does this need?", and that is how "buy paint" gets onto the list.
3. **Totals roll up.** Add the costs of the boxes under "Gate" and you have the gate's cost; add everything and you have the project's.

The WBS works well when the whole project can be seen clearly at the start. When the far end of a project is still foggy, you plan it differently, and that's rolling wave planning in the next lesson.

## Common pitfalls
<!-- bite: 72f5224d-572f-471b-bd53-b774f38d1ad3 -->

1. **Listing activities with no hierarchy.** A WBS is a tree, split level by level, not one long to-do list.
2. **Stopping too high.** "Build gate" is still too big to estimate well. Keep going until each box has one owner and one clear duration.
3. **Putting order into the WBS.** The WBS says *what*, not *in which order*. The order comes in the network diagram.
4. **Skipping the dictionary.** Vague box names cause arguments later about what was included.

## Check your understanding
<!-- bite: a16b1a7d-361d-483e-8361-f2701f445eb5 -->

Try each one before you open the answer.

1. <!-- q: mcq id="8f3c2a61" -->
   What is the main reason for building a WBS before estimating a project?

   - [ ] It shows which activities must come first
   - [x] Small pieces of work can be estimated far more accurately than the whole
   - [ ] It replaces the need for a schedule
   - [ ] It shows the critical path

   <details><summary>Answer</summary>

   Small, well-defined pieces are easier to estimate, and splitting makes sure nothing is left out. Order and the critical path come later, from the network.

   </details>

2. <!-- q: gap id="1d74e0b9" answers="decomposition" -->
   The technique of splitting work into smaller and smaller pieces to build a WBS is called ___.

   <details><summary>Answer</summary>

   Decomposition.

   </details>

3. <!-- q: mcq id="b5e09d3f" -->
   A WBS box reads only "Electrical". Which document should explain exactly what that covers?

   - [ ] The Gantt chart
   - [ ] The network diagram
   - [x] The WBS dictionary
   - [ ] The risk register

   <details><summary>Answer</summary>

   The WBS dictionary gives each element's scope, deliverables and other details.

   </details>

4. <!-- q: sketch id="3a96e7c4" -->
   Draw a three-level WBS for "hold a birthday party", with at least three level-2 parts and at least two activities under each.

   <details><summary>Answer</summary>

   One possible answer: level 1 "Birthday party"; level 2 "Venue", "Food", "Guests"; level 3 under Venue: book hall, decorate hall; under Food: order cake, buy drinks; under Guests: write guest list, send invitations.

   What to check:
   - one box at the top for the whole project;
   - level 2 split by part or deliverable, not by date;
   - every level-3 box is one job you could give a time to;
   - no arrows showing order: a WBS is a tree, not a network.

   </details>

5. <!-- q: open id="c20e8f5a" -->
   Explain why a WBS reduces the risk of wrong cost estimates.

   <details><summary>Answer</summary>

   Wrong estimates are a major cause of project failure. A WBS splits the project until each piece is small enough to picture and price, so each estimate is more accurate; the splitting also brings out jobs that would otherwise be forgotten; and the total is built by adding up those pieces rather than guessed in one go.

   </details>

## Before moving on
<!-- bite: 1b108feb-b86e-4b93-9092-30bd6e7717f5 -->

You can break a project into a WBS and explain the WBS dictionary. **Next:** [[planning-and-scheduling/07-rolling-wave-planning-and-reserves|07 — Rolling Wave Planning and Reserves]].

## Related
<!-- bite: 921c7849-a030-4cd3-aa61-7a614262f4e7 -->

- [[planning-and-scheduling/index|Planning and scheduling map]]
- [[systems-engineering/index|Systems Engineering]]: breaking down whole systems, not just the work.

## About this lesson
<!-- bite: e7211d66-db75-4a28-91d8-de487d13f2b8 -->

**Level:** Beginner. **Covers:** why the WBS comes first, the fence and gate broken down, work packages, decomposition, the WBS dictionary and why bottom-up estimating works.

**Where it sits:** lesson 6 of 35, in part 2 (breaking down the work).

**Source:** the author's own SSG 513 study notes, section 2. The fence's grouping into fence, gate and painting is added for this lesson; the eight activities are Class Exercise 2. The tree comes from `scripts/diagrams/planning_scheduling.py`.
