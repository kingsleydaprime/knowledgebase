# Arete Mobile — The Home Trail (a Full Feature, Dissected)

Split out from the original single-file `mobile-learning.md`. A compact case study in deriving UI
from data: the home trail feature end to end.

---

## Part 8 — The Home Trail (a full feature, dissected)

The home screen became a Duolingo-style trail of **days**. It's a compact masterclass in deriving UI from data, so it earns its own section.

### 8.1 Micro vs macro — one metaphor, two screens

Design decision worth internalizing: the **home trail's nodes are days** (past days colored by outcome, today as the big tappable node, next week locked ahead), while the **Progression path's nodes are XP thresholds** (F→SSSS). Same visual language, two different questions: "how is my week going?" vs "where am I in the long game?" When a metaphor works, don't cram both time scales into one screen — split by the question the user is asking.

### 8.2 Deriving the trail (zero new backend)

Everything is computed from data that already existed:

```ts
// Past days: the history endpoint (counts per day) → status colors
const status = day.completed === day.total ? 'complete' : day.completed > 0 ? 'partial' : 'missed';

// Today: live todayData (fresher than history) → big node with completion %

// Future milestones: pure math from the current streak —
const prospectiveStreak = maxStreak + (allDone ? 0 : 1) + d + 1;
const isMilestone = STREAK_MILESTONES.has(prospectiveStreak);  // 🔥 DAY 7 flag, 3 nodes ahead
```

That last one is the retention trick: the user *sees* day 7 sitting on their path before they've earned it. Anticipation rendered from arithmetic — no server support needed.

### 8.3 Empty states are the first thing new users see

**The bug:** a brand-new user saw 13 gray "empty" nodes above their first day, because the history endpoint returns an entry for every calendar day in range — including days before the account existed.

**The fix:** trim the *leading* run of empty days, keep gaps after the first active day (once the journey starts, a blank day is part of the story):

```ts
const firstActiveIdx = rawPast.findIndex((d) => d.total > 0);
const pastDays = firstActiveIdx === -1 ? [] : rawPast.slice(firstActiveIdx);
```

**Lesson:** always render your screens as a day-0 user. List UIs designed against a rich test account almost always have a broken first-run experience.

### 8.4 Tap-to-preview with a client-side cache

Future nodes open a forecast modal (`GET /quests/preview?date=`). Two small patterns:

```ts
const previewCache = useRef<Map<string, DayPreviewResponse>>(new Map());
// useRef, not useState: caching a Map shouldn't trigger re-renders.
// Repeat taps on the same day are instant and free.

<Modal visible={preview !== null} transparent animationType="fade">
  <TouchableOpacity style={backdrop} activeOpacity={1} onPress={close}>
    <TouchableOpacity activeOpacity={1} onPress={() => {}}>   {/* swallow taps inside card */}
```

The nested-touchable trick is the standard "tap outside to dismiss, tap inside does nothing" modal recipe in RN.

### 8.5 Two small war stories

- **The orphaned route:** the Progression screen existed at `/(app)/progression` as a hidden tab (`href: null`)… and *nothing in the app linked to it*. File-based routing means a screen can exist and be unreachable. After adding a route, grep for who links to it — a screen with zero inbound links is dead code with a URL.
- **Null-hardening `worldRank`:** when the backend started returning `worldRank: null` for users not yet on the leaderboard, two screens would have rendered `#null`. The fix is the same habit as always: type it `number | null`, render `#{rank ?? '—'}`. Every field that can be absent must have a display fallback.

