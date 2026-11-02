# NextVibe — Thinking Patterns

Specific instances from NextVibe sessions. The cross-project patterns live in
[[problem-solving/thinking-patterns|problem-solving/thinking-patterns]]. This file is the evidence.

---

## 2026-11-02 — Wishlist and spin-the-wheel design session

### Strength: product reasoning that beat the technical recommendation, twice

**Overfunding.** The AI recommended auto-closing a wishlist item once its confirmed total reached
the price. His answer was to keep items open until the organizer closes them, *"because the idea is
also to give… in such events, people wanna give."* That was right, and for a reason the AI had
missed: every contribution lands in one bank account, so per-item totals are only labels, and
overfunding costs nobody anything. Blocking a giver is the real failure.

**Where spin the wheel lives.** The AI proposed a standalone module. He said *"it's supposed to be a
GAME, so part of the gamification"*, then sharpened his own point: *"A wheel could be a game round
in a game session."* Both corrections were right. The AI had compared the wheel only against the
inside of a round. He was thinking about the whole system: plan quota, scheduling, the rewards
queue.

**What made it work:** he asked *"what do you think"* instead of simply overriding, which brought
out the reasoning on both sides. And his domain knowledge (how guests at Nigerian weddings
actually behave, and what "a game" means to an organizer) was evidence the AI didn't have.

### Strength: fast, clean decisions

About fifteen design questions were answered in one sitting, mostly with a letter and sometimes a
short reason. Examples: guest identity (name required, email optional), contributor visibility,
odds by rarity with visible labels, checked-in attendees only, claim codes now and QR later. When
he asked *"can't we have both limited and non-limited?"*, he turned an either/or question into a
better option.

### Watch: a new feature arriving before the last one is verified

One message held three asks: finish the wishlist extras, a postcard bug, and a **new game idea**.
At that point the wishlist had been built but never run end to end. Spin the wheel was then
designed and fully built the same day. The idea was good and the design was solid. The pattern is
the one `finish-line` exists for: in-flight work gets lighter verification when new work is
already starting. **What better looks like:** "smoke-test the wishlist, then design the wheel."

### Watch: handing over the keyboard vs the stated goal

*"You just write it please. I'm short on time"*, then *"You build it"* for the spin endpoint, even
after it was offered as a good one to write himself. Time pressure is real, and handing over is a
legitimate choice. But his stated goal is to *"understand it, implement it on my own, be able to
answer it in an interview."* Interview answers about code you didn't write are weaker under
follow-up questions. **A cheap fix:** re-implement `spin()` from the notes, without looking: the
row lock, derived stock, weighted pick and retry rule. It takes about an hour, and it turns
"we built" into "I built".
