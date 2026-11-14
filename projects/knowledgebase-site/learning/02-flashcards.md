# 02 — Flashcards: every "Answer" toggle becomes a card

Follows [[01-study-ui|the study UI]]. Added on 2026-11-14. The vault already held thousands of questions with hidden answers. This turns them into flashcards you can practise, with no new content written.

## What you get

- **Practise button** on every folder page and at the end of every note that has answers. It shows the card count, or "Review 3 due cards" (pulsing) when some are waiting. Underneath: "12 of 24 learned".
- **Practice screen:** one card at a time.
  1. Read the question and say the answer out loud.
  2. Tap the card (or Space) to flip it.
  3. Press **Got it** or **Again**. On a phone you can swipe right or left; on a laptop, `2`/`→` or `1`/`←`.
- **Missed cards come back** three cards later in the same session, with a red top edge.
- **In the note itself**, every answer gets small "↺ Again / ✓ Got it" buttons. A learned card's 👀 becomes ✅, and a due one shows 🔁.
- **Home page:** "Review N due cards" in the banner gathers due cards from every subject into one session.

## Where the cards come from

Notes write checks in three ways. All three are recognised, in `extractCards()` in `quartz/quartz/plugins/transformers/studyNav.ts`:

| Pattern | Looks like | The question is |
|---|---|---|
| 1. Paragraph then toggle | `**1. What is Big-O?**` then `<details><summary>Answer</summary>…` | the element just before the toggle |
| 2. Inside a list item | `1. **Question?**` with `<details>` indented under it | everything in the list item before the toggle |
| 3. Numbered list, one "Answers" toggle | five numbered questions, then `<details><summary>Answers</summary>` with five numbered answers | question *n* pairs with answer *n*, only when the counts match |

The extractor works on the HTML tree after Quartz has rendered the markdown, not on the raw text. That way code highlighting, maths, abbreviations and links in a card look the same as in the note.

Toggles whose summary doesn't start with "Answer" ("Hints", "After your prediction") are left alone, since they aren't question-and-answer pairs.

## Card ids

Each card's id is a short hash of *the note it's in and the question's text*. So:
- reordering questions, or editing an answer, keeps your progress;
- editing a question's wording, or moving the note, makes it a new card (you start that one again).

Two identical questions on one page get `-1`, `-2` added.

## The files, and why there are two kinds

The first version wrote one deck per folder with all its cards inside. DSA alone has **2,134 cards**, so its deck was **2 MB**, downloaded by every DSA folder page just to show a count. That's the slow-sidebar mistake again.

So the `StudyDecks` emitter writes two kinds of file:

| File | Holds | Size (DSA) |
|---|---|---|
| `static/decks/<folder>.json` | only the card ids, in reading order, and which note each is in | tens of KB |
| `static/cards/<note>.json` | one note's cards, with their HTML | one note's worth |

A folder page loads its deck to count. Pressing Practise picks 20 ids and loads only the notes those 20 come from, usually one to three small files. The deck also stores each note's path once, with cards pointing to it by number, instead of repeating the path 2,134 times.

**Why an emitter:** a transformer sees one note at a time, and a folder page can be processed before the notes inside it. An *emitter* runs after every note has been processed, so it can see all the cards at once. The transformer saves each note's cards in `file.data.studyCards`, and the emitter collects them.

**But the button is on the page**, and pages are rendered before other emitters run. So the page can't know the folder's card count at build time. It knows only whether a folder *has* cards, from a quick text check (`<summary>Answer`) done when the note tree is built. The browser fills in the count after loading the deck.

## Remembering what you know: the Leitner system

Each card sits in a **box** from 0 to 5, stored in localStorage under `kb_cards_v1` as `{ b: box, d: due date, n: note }`.

| Box | Comes back after |
|---|---|
| 0 | now (you pressed Again) |
| 1 | 1 day |
| 2 | 3 days |
| 3 | 7 days |
| 4 | 16 days |
| 5 | 35 days |

- **Got it** moves a card up one box. **Again** sends it to box 0.
- A card you missed earlier in the same session only reaches box 1 when you get it right. You didn't really know it.
- Pressing Got it on a card that isn't due yet does nothing. Clicking it ten times in a row can't fake mastery.
- **A session** is 20 cards: due ones first (most overdue first), then new ones in reading order. When nothing is due and nothing is new, it gives you the 20 coming up soonest.
- **"Learned"** means box 1 or higher.

This is a simple version of what Anki does. The spacing works because you recall a card just as you're about to forget it, which is the "practice over reading" idea from your learning system.

## Small things worth knowing

- **Links inside cards** were written relative to their own note (`../02-arrays`). A card shown on another page would break them, so the script resolves every `href` and `src` against the card's own note first.
- **Following a link** from a card closes the practice screen, and Quartz navigates as usual.
- **Keys:** while the practice screen is open, it catches key presses first (`stopPropagation`), so `j`/`k` don't flip pages behind it.
- **Deleted cards:** when a note's cards load, records for cards no longer in that note are removed. Otherwise they'd stay "due" forever.

## Try it yourself

1. Open `dsa/01-loops-and-what-they-cost-qb`, press Practise, and do a session. Then look at `kb_cards_v1` in DevTools → Application → Local Storage.
2. In DevTools, set one card's `d` to `0` and reload the home page: "Review 1 due card" appears.
3. **Exercise:** add a "Shuffle" option to the practice screen. Hint: `pickSession()` returns ids in reading order. Shuffling them before `hydrate()` is enough, but think about whether due cards should still come first.
