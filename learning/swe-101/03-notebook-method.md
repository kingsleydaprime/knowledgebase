# The Notebook Method

> How the physical book works, and the rule that stops it duplicating 1,150 notes that already exist.

---

## The 8-part structure

Yours, kept verbatim. For every topic:

1. **Concept** — what is it?
2. **Why** — why does it exist?
3. **How** — how does it work?
4. **Example** — one concrete example.
5. **Trade-offs** — when is it useful, when isn't it?
6. **Connection** — what does this connect to?
7. **Practice** — do something with it.
8. **Explain** — close the book and explain it from memory.

**Step 8 is the whole thing.** If you can't explain it without looking, you don't own it yet.

Steps 2 and 5 are what make this a *engineering* notebook rather than a summary. "What problem does this solve?" was the right question to build the habit around.

---

## The rule that matters most here

**You already wrote the library.**

Your own loop, from [[learning/02-the-learning-loop|02]]:

> Board = arena · Notebook = workbench · **Laptop = library**

The laptop half is *done* — 1,150 notes covering almost every phase of this curriculum. So the notebook must not become a hand-copied second vault. That would be transcription wearing the costume of study, and it's the most plausible way this course quietly fails: months of beautiful pages, no reps.

**The division:**

| Surface | Job in SWE 101 |
|---|---|
| **The vault** | The source. Read it at step 1. Check against it at step 5. |
| **The notebook** | Steps 2, 5, 7 — the *why*, the trade-offs, and worked problems. In your own words, from memory. |
| **The board** | Step 8. Reconstruct, derive, solve, erase, retry. |

**Concretely: read the vault note, close the laptop, then write.** If a notebook page could have been produced with the note open, it did nothing.

## What earns a notebook entry

Not everything. A page per topic in a 15-phase curriculum is hundreds of pages of overhead.

Write a page when **one** of these is true:

- You got it wrong first, and the page records why
- You can now explain something you couldn't last week
- It's a DSA pattern (these all get pages — pattern, tell, template, problems solved cold)
- It's a trade-off you'd have to justify in an interview
- The vault note and your understanding *disagreed*

Skip the page when you already knew it. Skipping is a legitimate outcome of the audit, not a shortcut.

## The DSA page format

One per pattern, and this is the part that becomes the interview prep:

```
PATTERN: sliding window
THE TELL: contiguous subarray/substring + "longest/shortest/max/min"
THE TEMPLATE: [from memory, not copied]
WHY IT'S O(n): [in your own words]
WHERE IT BREAKS: [when it doesn't apply]

PROBLEMS
  #  name              cold?  time   what I missed
  1  ...               Y      12m    off-by-one on shrink
```

The problems table is the visible progress — the equivalent of the JAMB board. It's also, by week 20, the honest answer to "how much DSA have you actually done."

## The Sunday session

One hour, end of week. Everything closed.

Teach the week out loud from memory — to the board, to nobody. Where it falls apart is next week's Monday.

This is step 3 of the loop and it is the step that gets skipped. Protecting it is the difference between this working and this being reading.

---

**Related:** [[learning/02-the-learning-loop|The Learning Loop]] · [[learning/06-ai-as-sparring-partner|AI as Sparring Partner]] — during SWE 101, sparring mode is the default. Hints and quizzes, not worked solutions, unless you've attempted it first.
