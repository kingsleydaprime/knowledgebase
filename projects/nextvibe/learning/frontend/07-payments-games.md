# NextVibe Frontend — Payments & Games Feature

Split out from the original flat `frontend-learning.md` (moved to `learning/archive/`).
See also `learning/frontend/02-state-management.md` (RTK Query lazy queries used for payment
polling), `learning/frontend/03-auth.md` (the login flow anonymous play hooks into),
`learning/frontend/06-realtime.md`, `learning/frontend/08-performance-debugging.md`, and — for the
backend half of this feature area — `learning/backend/03-modules.md` (Payments, Pledges, Ercaspay
internals) and `learning/backend/04-games-ai.md` (AI generation + the anonymous play system this
file's frontend code drives).

This file covers: the Ercaspay redirect-based payment integration pattern (and the retry-button
`useEffect` bug it produced), discriminated AI response shapes per game type, a full audit of the
word-puzzle implementation against a design spec, dead code recognition and removal, the complete
anonymous/guest game play system (localStorage, RTK Query endpoints, the `PUBLIC_PATHS`
allowlist, stale-closure traps, the post-auth merge dialog), the already-played guard, the public
ticket-purchase confirmation page, a `correctAnswerIndex` vs `correctAnswer` bug, a `mapType`
enum-key mismatch, the THIS_OR_THAT → True/False pivot, and the word-puzzle serialization step in
the game creation wizard.

---

## 13. Payment Integration Pattern

### Why redirect-based, not widget-based

The original implementation used Juicyway's inline widget (a JS popup). Ercaspay uses a full redirect to a hosted payment page. The hosted approach is:
- More secure (card details never touch your app)
- PCI-compliant by default
- Works across all devices without JS compatibility issues

### The complete flow

```
1. User clicks "Pay & Publish"

2. POST /v1/organizer-payments/plan/initiate
   Body: { eventId, planType, couponCode? }
   Response: { paymentId, checkoutUrl, status, expiresAt }

3. Check status:
   - "COMPLETED" or checkoutUrl is null → coupon covered full cost, show success
   - "PENDING" → redirect: window.location.href = checkoutUrl

4. User pays on Ercaspay's page

5. Ercaspay redirects user back to:
   {FRONTEND_URL}/organizer/payment/verify?paymentId=<id>

6. Verify page polls GET /v1/organizer-payments/verify/:paymentId
   every 2 seconds, up to 10 attempts

7. Status:
   - "completed"  → show success, auto-redirect to /dashboard after 3s
   - "failed"     → show error, offer retry
   - "pending"    → keep polling
   - 10 attempts exhausted → show timeout message + "Check again" button
```

### The retry button bug (and the fix)

A subtle bug: when the polling times out and you click "Check again", the `useEffect` won't re-run because its dependency (`paymentId`) hasn't changed. Fix: add a `retryKey` state to the dependency array.

```tsx
const [retryKey, setRetryKey] = useState(0);

useEffect(() => {
  // polling logic
}, [paymentId, verifyPayment, retryKey]); // retryKey makes this re-trigger

// In the "Check again" button:
onClick={() => {
  attemptRef.current = 0;
  setPollState("polling");
  setRetryKey(k => k + 1);  // ← triggers the effect
}}
```

(See `learning/frontend/08-performance-debugging.md` Part 27 for the general "stale `useEffect` not re-triggering" lesson this bug is an instance of.)

### Free publish path

When a coupon covers 100% of the cost, the backend returns `{ status: "COMPLETED", checkoutUrl: null }` immediately. The frontend must handle this without redirecting:

```tsx
const { status, checkoutUrl } = res.data;
if (status === "COMPLETED" || !checkoutUrl) {
  toast.success("Event published!");
  return;
}
window.location.href = checkoutUrl;
```

(See `learning/backend/03-modules.md` Part 51 for the backend's Ercaspay internals — NGN vs kobo amounts and the webhook branching this frontend flow ultimately depends on.)

---

## 26. Discriminated AI Responses — Handling Type-Specific Shapes

### The problem with a single schema

The AI game generator returns different shapes depending on the game type. The old code used a single mapping and tried to find the correct answer by string-matching:

```ts
// Old approach — fragile
const correctIdx = options.findIndex(
  (o) => o.toLowerCase().trim() === correctAnswerStr.toLowerCase().trim()
);
```

If the AI phrased the answer slightly differently from the option text, the match failed silently and `correctIdx` defaulted to `0` — wrong answer selected.

### The new backend — per-type schemas

The backend now returns clean, type-specific shapes:

| Game type | `options` | `correctAnswerIndex` | `clue` | `correctAnswer` |
|---|---|---|---|---|
| `TRIVIA` | 4 items | 0–3 (the right answer) | — | — |
| `TWO_TRUTHS_ONE_LIE` | 3 items | index of the **lie** | — | — |
| `WORD_PUZZLE` | absent | absent | hint string | exact answer string |
| `THIS_OR_THAT` | 2 items | absent (opinion poll) | — | — |

### The correct mapping pattern — branch per type

```ts
if (gameType === "word-puzzle") {
  return {
    ...base,
    question: q.clue ?? q.text ?? "",
    clue: q.clue ?? q.text ?? "",
    correctAnswer: q.correctAnswer ?? q.answer ?? "",
    options: undefined,
    correctIndex: undefined,
  };
}

if (gameType === "two-truths") {
  const options: string[] = q.options ?? [];
  // Backend tells us exactly which index is the lie
  const lieIndex = q.correctAnswerIndex ??
    options.findIndex(o => o.toLowerCase() === (q.correctAnswer ?? "").toLowerCase());
  return {
    ...base,
    question: q.text ?? q.question ?? "",
    options,
    correctIndex: lieIndex >= 0 ? lieIndex : 0,
    correctAnswer: options[lieIndex >= 0 ? lieIndex : 0] ?? "",
  };
}

if (gameType === "this-or-that") {
  // Opinion poll — there is no correct answer
  return {
    ...base,
    question: q.text ?? q.question ?? "",
    options: q.options ?? [],
    correctIndex: undefined,
    correctAnswer: undefined,
  };
}

// TRIVIA — correctAnswerIndex is definitive
const options: string[] = q.options ?? [];
const correctIdx = q.correctAnswerIndex >= 0 ? q.correctAnswerIndex : 0;
return {
  ...base,
  question: q.text ?? q.question ?? "",
  options,
  correctIndex: correctIdx,
  correctAnswer: options[correctIdx] ?? "",
};
```

### Key lesson: prefer index over string matching

When a backend returns a numeric index (`correctAnswerIndex: 2`), use it directly. String matching is a fragile fallback — keep it only for backwards compatibility with old response shapes, and always prefer the index:

```ts
const correctIdx =
  q.correctAnswerIndex ??           // new backend: use directly
  options.findIndex(o => ...);      // old backend: fall back to string match
```

(This same "index over string match" lesson comes up again in Part 54 below — a real bug where the game play page read a field that doesn't exist in the config at all.)

---

## 49. Word Puzzle — Auditing an Implementation Against a Design Spec

### The exercise

A PDF spec was handed over describing how the word-puzzle game should work. The task: read the spec, check the code, and identify what's missing.

This is a real-world skill — product or backend teams often hand over requirements as documents rather than tickets. Knowing how to read a spec and map it against code methodically is as important as knowing how to write code.

### What the spec required

The PDF described five things:

1. **API response shape** — `{ grid: string[][], hiddenWords: [{word, clue, startCell, endCell, direction}], points }`
2. **2D grid render** — CSS Grid, dynamic column count, per-cell state (`isIdle`, `isHovered`, `isSelected`, `isPartofCorrectWord`)
3. **Pointer event listeners** — `onPointerDown`, `onPointerMove/Enter`, `onPointerUp` to track drag lines across letters
4. **Client-side word validation** — compare user's start/end cell coordinates against `hiddenWords`, no API call needed
5. **UI layout** — grid canvas, word/clue sidebar (strikethrough when found), score + timer panel

### How to audit systematically

Go through each requirement and find the corresponding code:

```
Requirement 1 — API shape
  → Search for where game data is consumed
  → Found: buildGridFromQuestions() in page.tsx and event-game-tab.tsx
  → Status: ✅ — server sends flat question objects with word/startCell/endCell;
    client builds the grid itself (smarter than spec's approach)

Requirement 2 — 2D grid render
  → Search for gridTemplateColumns
  → Found: style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}
  → Cell states: CellState = "idle" | "hovered" | "selected" | "correct" | "wrong-flash"
  → Status: ✅

Requirement 3 — Pointer events
  → Search for onPointerDown, onPointerMove, onPointerUp
  → Found: all three on the container div in WordPuzzleGrid
  → Also: setPointerCapture (spec didn't mention this but it's required for mobile)
  → Status: ✅ — better than spec

Requirement 4 — Client-side validation
  → Search for handleSelectionComplete
  → Found: coordinate matching with forward + reverse support
  → Status: ✅

Requirement 5 — Sidebar
  → Found: "Words to Find" section — shows hw.word
  → Spec said to show item.clue OR item.word
  → hw.clue is stored (q.text ?? q.clue ?? q.word) but never rendered
  → Status: ⚠️ — gap found

Score/timer panel
  → Found: countdown timer + progress bar in WordPuzzleRoundPlayer
  → Status: ✅
```

### The gap — sidebar showed word only, not clue

The spec said to show `item.clue` (hints like "King of the jungle") so finding the word is an actual puzzle. Showing "LION" in the word list makes it trivial — users just scan for each word they can read.

`hw.clue` was already stored in the data structure:

```ts
// In buildGridFromQuestions:
clue: q.text ?? q.clue ?? q.word,  // already there, just never rendered
```

### The fix — show both word and clue

The old sidebar was a flat flex-wrap pill list — too cramped to show two lines per item. Changed to a 2-column grid so each item has room for both:

```tsx
// ❌ Before — word only, pill layout
<div className="flex flex-wrap gap-1.5">
  {hiddenWords.map((hw, idx) => {
    const found = foundWords.has(hw.word.toUpperCase());
    return (
      <div key={`${hw.word}-${idx}`} className={cn(
        "flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium border",
        found ? "border-green-500/40 bg-green-500/10 text-green-700 line-through"
               : "border-border bg-muted text-muted-foreground"
      )}>
        {found && <CheckCircle2 className="h-3 w-3 shrink-0" />}
        {hw.word}
      </div>
    );
  })}
</div>
```

```tsx
// ✅ After — word + clue, 2-column grid layout
<div className="grid grid-cols-2 gap-1.5">
  {hiddenWords.map((hw, idx) => {
    const found = foundWords.has(hw.word.toUpperCase());
    // Only show clue if it's different from the word itself
    // (when no clue was provided, clue falls back to the word — no need to repeat it)
    const hasClue = hw.clue && hw.clue.toUpperCase() !== hw.word.toUpperCase();
    return (
      <div key={`${hw.word}-${idx}`} className={cn(
        "flex items-start gap-1.5 rounded-xl px-2.5 py-2 text-xs border transition-all",
        found ? "border-green-500/40 bg-green-500/10 text-green-700"
               : "border-border bg-muted/50 text-foreground"
      )}>
        <div className="shrink-0 mt-0.5">
          {found
            ? <CheckCircle2 className="h-3 w-3 text-green-600" />
            : <span className="block h-3 w-3 rounded-full border border-current opacity-40" />}
        </div>
        <div className="min-w-0">
          <p className={cn("font-bold leading-tight", found && "line-through")}>
            {hw.word}
          </p>
          {hasClue && (
            <p className={cn(
              "text-[10px] leading-tight mt-0.5 truncate",
              found ? "text-green-600/70" : "text-muted-foreground"
            )}>
              {hw.clue}
            </p>
          )}
        </div>
      </div>
    );
  })}
</div>
```

The `hasClue` check prevents redundancy: if no clue was authored (`clue` falls back to `word`), showing both would repeat the same text twice.

### How the game is played (mobile and laptop)

Understanding the interaction model is essential before auditing pointer event code.

**On mobile (touch):**
- Press and hold your finger on the starting letter
- Drag across the grid letters in a straight line
- Lift your finger on the last letter of the word
- If your start/end cells match a hidden word's coordinates, that word is found

**On laptop (mouse):**
- Click and hold on the starting letter
- Drag to the last letter
- Release

The cells highlight as you drag (`"hovered"` state). A correct match turns green (`"correct"`). A miss flashes red (`"wrong-flash"`) and clears after 500ms.

**Why `setPointerCapture` matters on mobile:** Without it, if your finger moves slightly off a cell edge, the browser treats it as leaving the element and `onPointerMove` stops firing mid-drag. `setPointerCapture` locks the pointer events to the grid container for the lifetime of the drag, no matter where the finger moves. The spec didn't mention this — it's a mobile-specific detail that the code handles correctly.

### Key lesson — specs describe what, code must handle how

The spec said "implement pointer event listeners." The code went further:
- Used container-level events (not per-cell) — essential for touch drag reliability
- Added `setPointerCapture` — handles finger drift
- Added `onPointerLeave` — commits the selection if the user drags off the grid edge

A spec describes the intended behaviour. Implementation must account for the real environment (mobile browsers, edge cases, timing).

(See `learning/backend/04-games-ai.md` Part 53 for the matching backend-side bug — a config-shape mismatch that silently zeroed every word-puzzle score — and Part 57 below for the wizard-side serialization step that produces the correct config shape.)

---

## 50. Dead Code — Recognising and Removing Unreachable Functions

### What dead code is

Dead code is any code that can never execute at runtime. It compiles, it looks correct, but no code path ever reaches it. It's harmless to behaviour but harmful to maintenance: future readers assume it matters, spend time understanding it, and may accidentally try to wire it up.

### The `handleWordSubmit` example

In `RoundPlayer` (inside both `page.tsx` and `event-game-tab.tsx`), there was a function:

```ts
const handleWordSubmit = () => {
  if (flash || !wordInput.trim()) return;
  const correctAnswer: string = q?.correctAnswer ?? q?.answer ?? "";
  const isCorrect = wordInput.trim().toLowerCase() === correctAnswer.trim().toLowerCase();
  const newAnswers = [...answers];
  newAnswers[currentQ] = wordInput;
  setAnswers(newAnswers);
  setFlash({ selected: wordInput, correct: correctAnswer, isCorrect });
  setTimeout(() => advance(wordInput, newAnswers), 800);
};
```

It looks reasonable — it handles submitting a typed word answer. But it was never called.

**Why it could never be called:** `RoundPlayer` handles multiple game types. When `gameType === "word-puzzle"`, the component exits early:

```ts
// ── Word Puzzle: delegate entirely to the grid player ──────────────────────
if (gameType === "word-puzzle") {
  if (finalScore !== null) {
    // fall through to score screen
  } else if (!waitingForResult) {
    return (
      <WordPuzzleRoundPlayer   // ← exits here — renders the grid player
        questions={questions}
        onAllComplete={async (wordAnswers) => { ... }}
      />
    );
  }
}
```

The execution path for word-puzzle never reaches the rest of `RoundPlayer`. There's no text input rendered. `handleWordSubmit` is wired to nothing. It's unreachable.

### How to identify dead code

**Signal 1 — TypeScript hints**

TypeScript reports `'handleWordSubmit' is declared but its value is never read` as a hint (code `6133`). This is TypeScript telling you directly that nothing references this identifier. Treat these hints seriously — they're almost always pointing at real dead code.

**Signal 2 — Early returns that bypass everything**

When a function has an early return that covers a whole case:

```ts
if (gameType === "word-puzzle") {
  return <WordPuzzleRoundPlayer ... />;  // exits here for ALL word-puzzle games
}

// Everything below here is never reached for word-puzzle
const handleWordSubmit = () => { ... };  // dead
```

Trace the control flow for each case. If a case exits early and a function is only relevant to that case, the function is dead.

**Signal 3 — Nothing calls it**

Search the file for the function name. If the only match is the declaration, it's dead.

```bash
grep -n "handleWordSubmit" event-game-tab.tsx
# 807:  const handleWordSubmit = () => {
# Only one result — the declaration. Nothing calls it.
```

### What to do about dead code

**Delete it.** Don't comment it out, don't add a `// TODO: use this later` comment, don't leave it "just in case." If it's unreachable now, it will stay unreachable — and if you genuinely need it later, git history has it.

The one exception: if there's a real, imminent plan to wire it up (e.g. "we're adding a text input mode for word puzzle next sprint"), keep it and add a comment explaining why. But "might be useful someday" is not a reason to keep dead code.

### Handling truly unused parameters

Sometimes a function signature must match a certain shape even when you don't use all the parameters. TypeScript's convention is to prefix unused parameters with `_`:

```ts
// ❌ Unused parameter — TypeScript reports hint 6133
const advance = async (selectedAnswer: number | string, allAnswers: (number | string)[]) => {
  // selectedAnswer is never used inside the function body
};

// ✅ Underscore prefix — tells TypeScript (and readers) "intentionally unused"
const advance = async (_selectedAnswer: number | string, allAnswers: (number | string)[]) => {
  // The _ prefix suppresses the hint and communicates intent
};
```

The underscore is a widely recognised convention across TypeScript, JavaScript, Python, Rust, and Go. It means "I know this parameter exists and I'm deliberately not using it."

**When to use `_` vs just removing the parameter:**
- Use `_` when the parameter is part of a required signature (callback shape, interface, event handler)
- Delete the parameter entirely when it's your own internal function and you can freely change the signature

In this project, `advance` is called via `setTimeout(() => advance(idx, newAnswers), 800)` and the first arg is passed even though `advance` doesn't use it. Changing the call site to `advance(newAnswers)` would also work, but the `_` approach is simpler and makes the intent obvious without restructuring the calls.

### Also cleaned up — inline event handlers

```tsx
// ❌ Unused event parameter
onPointerLeave={(e) => {
  if (isDrawing.current && startCell.current) { ... }
}}

// ✅ Remove unused param
onPointerLeave={() => {
  if (isDrawing.current && startCell.current) { ... }
}}
```

Same principle: if you're not using the event object, don't declare it. Keeps the code honest.

### Summary — dead code checklist

When reviewing code:

1. **Check TypeScript hints** — `'X' is declared but its value is never read` means dead code
2. **Trace early returns** — any function that "handles" a case already covered by an early return is dead
3. **Search for callers** — if nothing calls a function, it's dead
4. **Remove it** — don't leave "just in case" dead code; use git history if you ever need it back
5. **Prefix unused params** — `_paramName` instead of deleting when the signature must match a required shape

(See `learning/backend/04-games-ai.md` Part 48 for two more real dead-code examples found alongside this one — an unused `save-draft` backend endpoint and an entire unused frontend API file, `gameApi.ts`.)

---

## 51. Anonymous Game Play — Playing Without an Account

### The problem

Game rounds can be shared publicly via a `shareToken` link (`/game/<token>`). Users who aren't logged in should still be able to play — forcing login before play kills conversion for viral links. But anonymous play has to integrate with the authenticated leaderboard, rewards, and scoring system once the user does log in.

The solution has four moving parts:
1. A random guest ID stored in localStorage
2. Three backend anonymous endpoints (join, submit, merge)
3. A post-auth merge flow that converts anonymous scores to real account scores
4. UX guards and prompts at the score screen

(See `learning/backend/04-games-ai.md` Part 49 for the full backend side of this system — the Redis-backed guest session store and the three endpoints this file's frontend code calls.)

---

### The anonymous game library — `src/lib/anonymous-game.ts`

All localStorage interaction is centralised here so nothing reads/writes `localStorage` directly in components:

```typescript
const ANON_STORAGE_KEY = "nv_anon_game";

interface AnonGameData {
  anonymousId: string;
  sessions: AnonPendingSession[];
}

export interface AnonPendingSession {
  sessionId: string;
  eventId: string;
  eventName: string;
}

// Read the anonymous ID (returns null if no session exists)
export function getAnonymousId(): string | null {
  const raw = localStorage.getItem(ANON_STORAGE_KEY);
  if (!raw) return null;
  try { return JSON.parse(raw).anonymousId ?? null; } catch { return null; }
}

// Save after a successful anonymous join
export function saveAnonSession(
  anonymousId: string,
  session: AnonPendingSession
): void {
  const existing = getAllAnonData();
  const sessions = existing?.sessions ?? [];
  // dedup: don't add the same session twice
  if (!sessions.some(s => s.sessionId === session.sessionId)) {
    sessions.push(session);
  }
  localStorage.setItem(ANON_STORAGE_KEY, JSON.stringify({ anonymousId, sessions }));
}

// Get the list of pending sessions (for the merge dialog)
export function getPendingSessions(): AnonPendingSession[] {
  return getAllAnonData()?.sessions ?? [];
}

// Wipe everything after merge completes or user skips merge
export function clearAnonGameData(): void {
  localStorage.removeItem(ANON_STORAGE_KEY);
}
```

**Why localStorage, not a cookie?**

The anonymous ID must survive page reloads and browser closes (not just the session). Cookies could work, but localStorage is simpler here — anonymous game data has no security sensitivity and doesn't need to be sent to the server on every request (we send it explicitly in API call bodies).

---

### RTK Query endpoints — `eventApi.ts`

Three mutations handle the anonymous lifecycle:

```typescript
// Join a game session anonymously
anonymousJoinGame: builder.mutation<
  { data: { anonymousId: string; sessionId: string; eventId: string; eventName: string } },
  { token: string; anonymousId?: string }
>({
  query: ({ token, anonymousId }) => ({
    url: `/v1/games/anonymous/join/${token}`,
    method: "POST",
    body: anonymousId ? { anonymousId } : {},
  }),
}),

// Submit answers for a round as an anonymous player
anonymousSubmitRound: builder.mutation<
  { data: { score: number } },
  { roundId: string; answers: number[]; anonymousId: string }
>({
  query: ({ roundId, answers, anonymousId }) => ({
    url: `/v1/games/anonymous/rounds/${roundId}/submit`,
    method: "POST",
    body: { answers, anonymousId },
  }),
}),

// Merge anonymous scores into the now-authenticated user's account
mergeAnonymousSessions: builder.mutation<
  void,
  { anonymousId: string; confirmedEventIds: string[] }
>({
  query: ({ anonymousId, confirmedEventIds }) => ({
    url: `/v1/games/anonymous/merge`,
    method: "POST",
    body: { anonymousId, confirmedEventIds },
  }),
}),
```

Exported hooks: `useAnonymousJoinGameMutation`, `useAnonymousSubmitRoundMutation`, `useMergeAnonymousSessionsMutation`.

---

### `PUBLIC_PATHS` — preventing the 401 redirect loop

The `baseQueryWithReauth` in `src/app/provider/api/baseQuery.ts` redirects to `/auth/login?from=<current>` whenever an API call returns 401 and the user isn't logged in. This is correct for authenticated pages, but on a public game page an anonymous player will get 401 from authenticated endpoints (like `getGameSession`) — and should NOT be redirected to login.

The fix: a `PUBLIC_PATHS` allowlist checked before any 401 redirect:

```typescript
const PUBLIC_PATHS = [
  "/events",
  "/dashboard/events",
  "/postcards",
  "/postcard",
  "/dashboard/postcards",
  "/game",     // ← added for the public game share page
];

function isPublicPath(pathname: string): boolean {
  return PUBLIC_PATHS.some(
    (p) => pathname === p || pathname.startsWith(p + "/")
  );
}

// In the 401 handler:
if (!isPublicPath(window.location.pathname)) {
  clearSessionAndRedirect();
}
```

**Why `/game` specifically?** The public game page at `/game/<token>` calls `getGameSessionByToken` which is a protected endpoint — it returns 401 when called without a token. Without this guard, an anonymous user landing on `/game/abc` would get immediately redirected to login before they even see the game.

Note: this is different from `PUBLIC_ROUTES` in `src/proxy.ts` (server-side middleware, see `learning/frontend/01-routing.md` Part 23). The `PUBLIC_PATHS` check is purely client-side — it only prevents `baseQueryWithReauth` from redirecting to login on 401.

---

### Anonymous join on the event game tab

The event game tab (`event-game-tab.tsx`) handles two surfaces: authenticated and unauthenticated. The join flow detects which path to take:

```typescript
const [anonymousJoin] = useAnonymousJoinGameMutation();
const [anonId, setAnonId] = useState<string | null>(() => getAnonymousId());

// In handleJoin:
if (!isLoggedIn) {
  // Primary source: allSessions (from useGetGamesQuery) — always available synchronously
  const sessionFromList = allSessions.find((s: any) => s.id === sessionId);
  const shareToken: string | undefined =
    sessionFromList?.shareToken ?? sessionDataMap[sessionId]?.shareToken;

  if (shareToken) {
    try {
      const existingAnonId = getAnonymousId();
      const res = await anonymousJoin({
        token: shareToken,
        anonymousId: existingAnonId ?? undefined,
      }).unwrap();

      const payload = res?.data ?? res;
      saveAnonSession(payload.anonymousId, {
        sessionId: payload.sessionId,
        eventId: payload.eventId,
        eventName: payload.eventName,
      });
      setAnonId(payload.anonymousId);
    } catch { /* fall through — join locally only */ }
  }

  markSessionJoined(sessionId);
  setActiveSessionId(sessionId);
  toast.success("You're in! Sign in after to save your score.");
  return;
}

// Authenticated join path follows...
```

**The `sessionDataMap` race condition:**

`sessionDataMap` is populated by async `SessionFetcher` components. If the user clicks "Join" immediately after the page loads, those fetches may not have resolved yet — `sessionDataMap[sessionId]` would be `undefined`.

The fix: use `allSessions` (from `useGetGamesQuery`) as the primary source. `allSessions` comes from the top-level games list query that loaded before the user saw anything. `sessionDataMap` is only used as a fallback if for some reason `shareToken` isn't on the list entry:

```typescript
const shareToken: string | undefined =
  sessionFromList?.shareToken ??   // ← synchronous, always available
  sessionDataMap[sessionId]?.shareToken;  // ← async fallback
```

Why does `shareToken` appear on the list result? Because Prisma returns all scalar fields by default — `shareToken` is a scalar on `GameSession`, so it comes back in the list query without explicit `select`.

---

### Anonymous submit — and the stale closure trap

After the user answers a round, `handleSubmit` must decide whether to call the anonymous or authenticated endpoint:

```typescript
// Inside handleSubmit (event-game-tab.tsx):
const effectiveAnonId = anonId ?? getAnonymousId(); // ← read localStorage as fallback
const isLoggedIn = !!Cookies.get("accessToken");

if (!isLoggedIn && effectiveAnonId) {
  try {
    const res = await anonymousSubmit({
      roundId: playingRoundId,
      answers: submittedAnswers,
      anonymousId: effectiveAnonId,
    }).unwrap();
    const payload = res?.data ?? res;
    return { ok: true, score: payload.score ?? 0 };
  } catch {
    return { ok: false };
  }
}
```

**Why `anonId ?? getAnonymousId()`?**

React state (`anonId`) is captured at render time. `handleSubmit` is often called inside a `setTimeout` callback (e.g., 800ms after the user selects their final answer to show the result animation). If `setAnonId()` was called between render and the timeout firing, the closure still holds the old value.

Reading `getAnonymousId()` directly from localStorage breaks out of the closure — localStorage is always current. This pattern (`stateVar ?? readFromSource()`) is the general fix for stale closure problems where the source of truth is outside React. (See `learning/frontend/06-realtime.md` Part 48 for the general stale-closure concept this pattern is fixing.)

---

### Post-auth merge — `use-anon-merge.ts`

After a successful login (Google or email), the `handlePostAuth` function runs before redirecting the user:

```typescript
export function useAnonMerge() {
  async function handlePostAuth(onDone: () => void) {
    const hasPending = checkPending();  // checks localStorage for pending sessions
    if (!hasPending) { onDone(); return; }

    const sessions = getPendingSessions();
    const uniqueEventIds = [...new Set(sessions.map(s => s.eventId))];

    if (uniqueEventIds.length === 1) {
      // Single event — merge silently without asking
      await mergeAndClear(uniqueEventIds);
      onDone();
    } else {
      // Multiple events — show dialog so user can choose which to keep
      setShowDialog(true);
    }
  }

  async function mergeAndClear(confirmedEventIds: string[]) {
    const anonymousId = getAnonymousId();
    if (!anonymousId) { clearAnonGameData(); return; }

    try {
      await mergeSessions({ anonymousId, confirmedEventIds }).unwrap();
    } catch {
      // best-effort — if merge fails, don't block the user
    } finally {
      clearAnonGameData();  // ← ALWAYS clears, whether merge succeeded or failed
      setShowDialog(false);
    }
  }
}
```

**The `finally` block is critical.** It runs even if `mergeSessions` throws. This ensures:
- If merge succeeds → data is cleared ✓
- If merge fails (network, server error) → data is still cleared ✓
- After logout, the next anonymous play session starts fresh ✓

**Where `handlePostAuth` is called:**

Both the Google login button (`google-login-button.tsx`) and the email login form call `handlePostAuth` as the last step before `router.replace(destination)`. The call order is:

```
login succeeds → dispatch(setUser) → dispatch(setIsAuthenticated(true)) →
await handlePostAuth(() => router.replace(destination))
```

`handlePostAuth` either calls `onDone()` immediately (no pending sessions) or shows the `AnonymousMergeDialog` (multiple events to choose from). `onDone` is the redirect — so the user only navigates away after the merge completes.

---

### Login prompt on the score screen

After completing a round anonymously, the score screen shows a nudge to log in:

```tsx
// In RoundPlayer's score screen (both page.tsx and event-game-tab.tsx):
{isAnonymous && (() => {
  const from = encodeURIComponent(`/game/${token}`);
  return (
    <div className="w-full rounded-xl border border-[#5B1A57]/20 bg-[#5B1A57]/5 p-3 text-center space-y-1.5">
      <p className="text-xs text-muted-foreground font-medium">
        Log in to see the full leaderboard &amp; keep your score
      </p>
      <div className="flex gap-3 justify-center">
        <a href={`/auth/login?from=${from}`}
           className="text-xs font-semibold text-[#5B1A57] hover:underline">
          Log in
        </a>
        <span className="text-xs text-muted-foreground">·</span>
        <a href={`/auth/register?from=${from}`}
           className="text-xs font-semibold text-[#5B1A57] hover:underline">
          Sign up
        </a>
      </div>
    </div>
  );
})()}
```

**Why `<a>` not `<Link>`?** The `?from=` redirect must survive a full page navigation through the auth flow (login page → redirect back). `<a>` triggers a full navigation, which is correct here. `<Link>` does a client-side navigation within Next.js's router, which works fine here too — but `<a>` is slightly clearer for "navigating to a different section of the app." (See `learning/frontend/03-auth.md` Part 33 and 43 for everything that can go wrong in this `?from=` redirect flow.)

In `event-game-tab.tsx`, `isAnonymous` is detected via `!Cookies.get("accessToken")` since `isAuthenticated` (Redux state) may not reflect the cookie state during the brief window after a logout.

---

## 52. Already-Played Guard — Preventing Double Submissions

### The problem

A user completes a game round. If they then open the round URL again (directly, via back button, or by clicking a shared link), they would see the question list and could potentially submit again. The backend rejects duplicate submissions (`@@unique([gameRoundId, userId])`), but the UX should not even show the questions — it should show a "you already played this" screen.

### Two signals, one guard

The already-played state is detected from two sources:

```typescript
// Source 1: local React state (set immediately when user submits in this session)
const [playedRounds, setPlayedRounds] = useState<Set<string>>(new Set());

// Source 2: backend-persisted flag (loaded with the session data)
const roundAlreadyPlayed =
  playedRounds.has(playingRoundId) ||
  !!sessionDetail?.rounds?.find(r => r.id === playingRoundId)?.hasPlayed;
```

`playedRounds` is the fast path — it works immediately within the same browser session without a network round-trip. `hasPlayed` is the durable path — it persists across browser sessions and devices.

When `roundAlreadyPlayed` is true, the guard renders a completion screen instead of the questions:

```tsx
if (roundAlreadyPlayed) {
  return (
    <div className="flex flex-col items-center gap-4 py-10 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
        <CheckCircle2 className="h-9 w-9 text-green-600" />
      </div>
      <div>
        <h3 className="text-lg font-bold">Round already completed</h3>
        <p className="text-sm text-muted-foreground mt-1">
          You've already submitted your answers for this round.
        </p>
      </div>
      {myEntry?.score !== undefined && (
        <p className="text-sm">Your score: <strong>{myEntry.score}</strong></p>
      )}
      <Button onClick={() => setPlayingRoundId(null)}>Back to Lobby</Button>
    </div>
  );
}
```

### Where the guard lives

The guard appears in two places:
- **`/game/[token]/page.tsx`** — the public share link page, before rendering `PublicRoundPlayer`
- **`event-game-tab.tsx`** — the in-app event game tab, in the `if (playingRoundId)` block

Both use the same pattern. The `myEntry?.score` is only available on the public page (where the user's `GameEntry` is loaded from the session data) — on the event tab, only the "already played" message is shown without a score.

### Why check `sessionDetail?.rounds` rather than just `playedRounds`?

`playedRounds` is in-memory state. If the user:
1. Plays a round on their phone
2. Later opens the same round URL on their laptop

...their laptop's React state has no knowledge of what their phone played. `hasPlayed` is stored server-side and comes back with the session data, so it covers cross-device cases.

### Backend `hasPlayed` field

`hasPlayed` is a computed or stored field on `GameRound` that the backend returns as part of the session detail. It reflects whether the current authenticated user has a `GameEntry` row for that round. For anonymous users, this field is not present — the guard falls back to `playedRounds` only.

---

## 53. Ticket Purchase Confirmation — Public Summary Endpoint

### The endpoint

After Ercaspay redirects the user back from checkout, call:

```
GET /v1/payments/purchases/:purchaseId/summary
Auth: none required — public endpoint
```

No auth header needed. The purchase UUID is the access control: a 128-bit UUID (2^122 possible values) is computationally infeasible to guess. This lets the confirmation page work even if the user isn't logged in at that moment. (See `learning/backend/03-modules.md` Part 51 for the backend route-ordering detail that makes this endpoint work correctly alongside `GET /purchases/:id`.)

### Response shape

```json
{
  "purchaseId": "uuid",
  "paymentStatus": "COMPLETED",
  "paidAt": "2026-06-25T10:00:00.000Z",
  "totalAmount": 10000,
  "currency": "NGN",
  "customerName": "Kingsley Daprime",
  "event": {
    "id": "uuid",
    "name": "Make Music Lagos 2026",
    "startsAt": "2026-08-15T18:00:00.000Z",
    "endsAt": "2026-08-15T23:00:00.000Z",
    "locationName": "Eko Atlantic City, Lagos",
    "flierUrl": "https://...",
    "mode": "IN_PERSON"
  },
  "tickets": [
    { "ticketNumber": "NV-AB12CD34", "tierName": "VIP", "tierPrice": 5000, "status": "VALID", "qrCode": "data:image/png;base64,..." },
    { "ticketNumber": "NV-EF56GH78", "tierName": "VIP", "tierPrice": 5000, "status": "VALID", "qrCode": "data:image/png;base64,..." }
  ]
}
```

`totalAmount` is in NGN, full naira (not kobo) — display directly with `.toLocaleString()`.

### Getting `purchaseId` to the confirmation page

When initiating a purchase, the backend returns `purchaseId`. Pass it to Ercaspay's redirect URL:

```ts
// After initiatePurchase:
const { purchaseId, checkoutUrl } = result;
// Build your return URL:
const returnUrl = `${origin}/tickets/confirm?purchaseId=${purchaseId}`;
// Pass returnUrl to Ercaspay at checkout initiation
```

The confirmation page reads it:

```tsx
// Wrap in Suspense because useSearchParams() requires it
export default function ConfirmPage() {
  return (
    <Suspense fallback={<TicketSkeleton />}>
      <ConfirmPageInner />
    </Suspense>
  );
}

function ConfirmPageInner() {
  const searchParams = useSearchParams();
  const purchaseId = searchParams.get("purchaseId");
  // ...
}
```

(See `learning/frontend/01-routing.md` Part 25 for why this `<Suspense>` wrapper is a hard Next.js build requirement, not a style choice.)

### Polling for webhook delay

There's a race condition: Ercaspay redirects the user before the webhook fires. The confirmation page may arrive when `paymentStatus` is still `PENDING`. Poll until `COMPLETED`:

```ts
const [attempts, setAttempts] = useState(0);
const { data, refetch } = useGetPurchaseSummaryQuery(purchaseId ?? "", {
  skip: !purchaseId,
});

const status = data?.data?.paymentStatus;
const isPending = status === "PENDING" || !status;

useEffect(() => {
  if (!isPending || attempts >= 10) return;
  const timer = setTimeout(() => {
    refetch();
    setAttempts((a) => a + 1);
  }, 2000); // check every 2s, up to 10 attempts (~20s total)
  return () => clearTimeout(timer);
}, [isPending, attempts, refetch]);
```

After 10 attempts, show a "payment still processing" message and a manual refresh button rather than spinning forever.

### Displaying individual tickets

Each ticket in the response has its own `ticketNumber` and `qrCode` (base64 data URL). Render them in a list:

```tsx
{summary.tickets.map((ticket) => (
  <div key={ticket.ticketNumber} className="rounded-xl border p-4 space-y-2">
    <div className="flex justify-between items-center">
      <div>
        <p className="font-semibold">{ticket.tierName}</p>
        <p className="text-xs text-muted-foreground font-mono">{ticket.ticketNumber}</p>
      </div>
      <p className="font-medium">₦{ticket.tierPrice.toLocaleString()}</p>
    </div>
    {ticket.qrCode && (
      <img src={ticket.qrCode} alt={`QR for ${ticket.ticketNumber}`}
           className="w-32 h-32 mx-auto" />
    )}
  </div>
))}
```

---

## 54. Game Play Page — `correctAnswerIndex` vs `correctAnswer`

### The Bug

In the game play page (`/game/[token]/page.tsx`), the flash-feedback after a player selects an option always highlighted option A (index 0), regardless of which option was actually correct. This applied to both trivia and true/false questions.

**Root cause:** The game config stores answers as a numeric index under `correctAnswerIndex`. The page was reading:

```typescript
// Old — broken:
const correctIdx: number | string = q?.correctAnswer ?? q?.correct ?? q?.answer ?? 0;
```

`q.correctAnswer` is not a field in the config — the config stores `q.correctAnswerIndex`. None of the fallbacks (`correct`, `answer`) exist either. The entire chain resolved to `0`, so the flash always highlighted option A.

**The fix:**

```typescript
// New — correct:
const correctIdx: number = q?.correctAnswerIndex ?? 0;
```

Read `correctAnswerIndex` directly. The `?? 0` fallback is safe: if a question has no correct answer defined (shouldn't happen, but defensive), option A is highlighted — the same old behavior, just not for wrong reasons.

### The Rule

When working with game round config in the frontend:
- **Answers are stored as `correctAnswerIndex` (number 0-3)** — the zero-based index of the correct option in the `options` array
- **Never read `q.correctAnswer`** — that string field does not exist in the config JSON the backend stores
- **Never read `q.correct` or `q.answer`** — also absent from the config

The only exception: `q.correctAnswer` is set as a computed convenience field on the frontend wizard's local `Question` state — but that state is for the creation UI, not for the game play page which reads from the backend config.

---

## 55. mapType Enum Keys Must Match Backend Exactly

### The Bug

The game play page (`page.tsx`) maps backend game type strings to frontend display types:

```typescript
// Old — broken:
const mapType: Record<string, string> = {
  TRIVIA: "trivia",
  WORD_PUZZLE: "word-puzzle",
  TWO_TRUTHS: "two-truths",       // ← wrong
  THIS_OR_THAT: "this-or-that",
};
```

The backend enum value for two-truths is `TWO_TRUTHS_ONE_LIE`. The map had `TWO_TRUTHS`. When the backend returned `"TWO_TRUTHS_ONE_LIE"`, the map lookup found no key and fell through to the trivia renderer. Every two-truths round rendered as trivia.

**The fix:**

```typescript
// Correct:
const mapType: Record<string, string> = {
  TRIVIA: "trivia",
  WORD_PUZZLE: "word-puzzle",
  TWO_TRUTHS_ONE_LIE: "two-truths",   // matches backend enum
  THIS_OR_THAT: "this-or-that",
};
```

### The Rule

Any frontend map from backend enum values to display types must use the exact backend enum string as the key. The backend enum is the source of truth. Check `backend/prisma/schema/games.prisma` → `enum GameType` for the canonical values.

Current `GameType` enum:
```prisma
enum GameType {
  TRIVIA
  WORD_PUZZLE
  THIS_OR_THAT
  TWO_TRUTHS_ONE_LIE
}
```

**How bugs like this hide:** The fallback renderer (trivia) is functional — players can still answer questions. The wrong rendering just shows a different layout. No error is thrown, no network failure, no console warning. The only signal is visual: "why does my two-truths round look like trivia?"

---

## 56. True/False Pivot — Renaming THIS_OR_THAT and Adding Real Scoring

### The Decision

`THIS_OR_THAT` in its original form was an opinion poll: "Do you prefer X or Y?" Players picked an option and everyone got points regardless of choice. There was no correct answer.

The pivot: rename the concept to **True or False** and make it a knowledge game. Each question is a factual statement that is definitively true or false. Players who identify it correctly get points; those who get it wrong get nothing.

The backend enum stays `THIS_OR_THAT` — no database migration needed. The display label changes to "True or False" and the mechanics change. (See `learning/backend/04-games-ai.md` Part 53 for the corresponding backend scoring change.)

### Config Shape After the Pivot

```json
{
  "text": "The Great Wall of China is visible from space.",
  "options": ["True", "False"],
  "correctAnswerIndex": 1,
  "points": 5
}
```

- `options` is always `["True", "False"]` — locked, not editable
- `correctAnswerIndex` is 0 if the statement is TRUE, 1 if FALSE
- The backend scores by comparing `userAnswer` (submitted as option index) to `correctAnswerIndex`

### UI Changes in the Wizard

**Step 4 (question review/edit):**

The edit mode for `this-or-that` questions was changed from generic text input + correct-answer selector to a locked True/False toggle:

```tsx
{gameType === "this-or-that" ? (
  <>
    <Label>Is the statement true or false? — tap to mark</Label>
    <div className="flex gap-2">
      {["True", "False"].map((label, optIdx) => (
        <button
          key={label}
          type="button"
          onClick={() => handleQuestionEdit(q.id, "correctAnswerIndex", optIdx)}
          className={cn(
            "flex-1 h-9 rounded-lg border text-sm font-medium transition-colors",
            q.correctAnswerIndex === optIdx
              ? "bg-emerald-500 border-emerald-500 text-white"
              : "border-border bg-muted text-muted-foreground"
          )}
        >
          {label}
        </button>
      ))}
    </div>
  </>
) : /* trivia/two-truths: editable text inputs */ }
```

The options themselves are not text inputs — True and False are fixed. The organizer only controls which is correct.

**View mode** shows the correct option highlighted green (same as trivia).

**`addQuestion` template for this-or-that:**
```typescript
{ id: newId, question: "", options: ["True", "False"], correctAnswerIndex: 0, correctAnswer: "True", timeLimitSecs: 15, points: 5 }
```

**AI response mapping (in `handleComplete` of the wizard):**

AI-generated questions for `this-or-that` must be mapped to ensure `correctAnswerIndex` is always a defined number:

```typescript
if (gameType === "this-or-that") {
  const tfOptions = ["True", "False"];
  const correctIdx = q.correctAnswerIndex ?? 0;
  return {
    ...base,
    question: q.text ?? q.question ?? "",
    options: tfOptions,
    correctAnswerIndex: correctIdx,
    correctAnswer: tfOptions[correctIdx],
  };
}
```

The fallback `?? 0` (defaulting to True) is acceptable — the organizer reviews every AI-generated question before saving and can correct it with the toggle.

### AI Prompt for THIS_OR_THAT

The AI is instructed to produce True/False questions:

- `"options"`: exactly `["True", "False"]` — always these two words
- `"correctAnswerIndex"`: 0 if the statement is TRUE, 1 if the statement is FALSE
- The statement in `"text"` must be definitively factual — not subjective or debatable

The AI schema example uses:
```json
{
  "text": "A factual statement that is either true or false",
  "options": ["True", "False"],
  "correctAnswerIndex": 0,
  "points": 5
}
```

(See `learning/backend/04-games-ai.md` Part 48 for the OpenRouter/Gemini AI generation service that produces these questions.)

---

## 57. Word Puzzle Serialization in the Game Creation Wizard

### How the Wizard Stores Word Puzzle Questions

The wizard's internal `Question` state for word puzzles stores each hidden word as a separate question entry:

```typescript
// Internal wizard state — one entry per hidden word:
[
  { id: "q-1", wordPuzzleMeta: { grid: [[...]], word: "CAT", startCell: [0,0], endCell: [0,2], direction: "HORIZONTAL" }, points: 10 },
  { id: "q-2", wordPuzzleMeta: { word: "DOG", startCell: [1,0], endCell: [1,2], direction: "HORIZONTAL" }, points: 10 },
]
```

This is a UI convenience — it lets the organizer manage each word as an individual item in the list.

### How the Backend Expects the Config

The backend reads `config.questions[0].hiddenWords[]`. All hidden words must be grouped under a single `questions[0]` object. The grid is shared — all words are in the same grid.

### The Serialization Step (in `handleComplete`)

When the wizard submits, it must transform the one-word-per-question internal state into the one-question-with-all-words format the backend expects:

```typescript
if (r.gameType === "word-puzzle") {
  const grid = r.questions[0]?.wordPuzzleMeta?.grid ?? [];
  const totalPoints = r.questions.reduce((sum, q) => sum + (q.points ?? 10), 0);
  const hiddenWords = r.questions
    .filter((q) => q.wordPuzzleMeta?.word)
    .map((q) => ({
      word: q.wordPuzzleMeta!.word,
      startCell: q.wordPuzzleMeta!.startCell,
      endCell: q.wordPuzzleMeta!.endCell,
      direction: q.wordPuzzleMeta!.direction,
    }));
  return {
    ...roundBase,
    config: { questions: [{ grid, hiddenWords, points: totalPoints }] },
  };
}
```

Key details:
- The grid is taken from the first question entry (all entries share the same grid)
- `totalPoints` sums all per-word points — the backend awards them all as one when the player finds any word? No — the backend awards `question.points` when a hidden word is found, reading from the single question's `points`. Use total points to avoid the player getting zero points for finding words beyond the first.
- Only entries with a `wordPuzzleMeta.word` are included (filters out empty template entries)

### Why the Mismatch Exists

The wizard's step-four UI renders each word as an editable "question card" — this matches the trivia UX where each question is independent. The word puzzle concept doesn't map cleanly to this UI, so the internal representation is adapted for the UI and then serialized correctly at save time. The serialization step is the critical translation layer between UI state and backend config.

(See `learning/backend/04-games-ai.md` Part 53 for the exact backend config shape this serialization step must match, and the real bug that occurred when an earlier version of this wizard didn't group hidden words correctly.)

---

## `touch-action: none` makes overflow unrecoverable (2026-08-21)

A player reported the word puzzle "not swiping" on his phone. It worked fine on
a laptop. The cause was a layout bug that only exists below a certain viewport
width, and it's a combination worth recognising because each half looks correct
on its own.

**Half one — fixed cell sizes inside a scroll container:**

```jsx
<div className="overflow-x-auto">
  <div className="inline-grid gap-0.5" style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
    <div className="h-8 w-8 ..." />   {/* fixed size */}
```

`overflow-x-auto` looks like the responsible thing to do — "if it's too wide,
let them scroll." Do the arithmetic though: 12 columns x 32px + 11 gaps x 2px =
406px, against roughly 343px of usable width on a 375px phone.

**Half two — the drag handler disables panning:**

```jsx
className="... touch-none"   // touch-action: none
```

That's *correct* for a drag-to-select grid: without it the browser treats the
drag as a scroll and `pointermove` never fires. But `touch-action: none` also
means the finger can no longer pan the `overflow-x-auto` parent. So the content
overflows, and the one affordance provided for reaching it is disabled by the
very property that makes the interaction work.

The result: columns exist off-screen, are unreachable, and a drag toward them
does nothing — indistinguishable from "swiping is broken".

**The fix is to stop overflowing rather than to scroll:**

```jsx
<div className="w-full max-w-sm mx-auto">
  <div className="grid w-full gap-0.5 touch-none"
       style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}>
    <div className="aspect-square ..." />   {/* sized by the grid */}
```

`minmax(0, 1fr)` rather than `1fr` matters: `1fr` is shorthand for
`minmax(auto, 1fr)`, and the `auto` minimum refuses to shrink below the content's
intrinsic size — which is what lets grid and flex children blow out their
container. `minmax(0, 1fr)` allows genuine shrinking. This is the single most
common reason a CSS grid or flex row overflows despite `w-full`.

`aspect-square` then keeps the cells square at whatever width they land on, so
one rule handles every column count on every screen.

### The general lessons

- **A scroll container is not a fix for overflow** when something else on the
  element disables scrolling. `touch-action`, `pointer-events`, and
  `overscroll-behavior` all interact with scroll affordances in ways that are
  invisible on a mouse-driven desktop.
- **Desktop-only testing hides an entire class of bug.** Nothing here was wrong
  at a laptop width; the layout only failed below roughly 400px. Checking a
  narrow viewport (devtools device toolbar is enough to catch this one) costs
  seconds.
- **A generator change can surface a latent UI bug.** The grid was previously
  always 10x10 because the AI prompt demanded it, which fits. Moving placement
  into code let grids be 11-14 wide — the layout bug was always there, the
  content just never triggered it. When changing what a system *produces*, check
  what consumes it against the new range of outputs, not just the old one.

---

## Reading a bug out of a screen recording (2026-08-21)

A player reported the word puzzle "not swiping" on his iPhone. It worked on the
organiser's iPhone. Three rounds of theorising got nowhere; a 15-second screen
recording settled it in one pass.

### The technique

Video can't be watched directly, but frames can be read as images. `ffmpeg`
samples them and tiles them into numbered contact sheets:

```bash
ffprobe -v error -show_entries format=duration -show_entries stream=width,height "clip.mp4"

# numbered contact sheets: 3 frames/sec, 24 per sheet
ffmpeg -i clip.mp4 -vf "fps=3,scale=176:-1,\
drawtext=text='%{n}':x=4:y=4:fontsize=16:fontcolor=yellow:box=1:boxcolor=black,\
tile=6x4" sheet_%d.png
```

- `fps=3` resamples — 3 frames per second of video, not every frame.
- `drawtext=text='%{n}'` stamps the frame number, so a frame of interest can be
  re-extracted at full resolution.
- `tile=6x4` packs 24 frames into one image: a whole interaction seen at once,
  which is what makes the *pattern* visible rather than any single moment.

Chaining filters with commas builds a pipeline — resample, scale, label, tile —
each stage feeding the next.

### What it showed

Across 44 frames, **never more than one cell was highlighted.** Always a single
cell, which then flashed red. The countdown ran 50s → 36s, so the app was alive;
roughly a dozen attempts all failed identically.

That single observation eliminated nearly every hypothesis at once. Tap feedback
appearing proves `pointerdown`, `touch-action: none`, and cell identification all
work. The selection never growing proves the failure is between down and up. And
the red flash proves the selection *completed* — with `start === end`.

**Evidence narrows faster than reasoning does.** Overflowing grids,
`-webkit-user-select`, `touch-callout`, Tailwind not compiling `touch-none` — all
plausible, all wrong, and all of them cost more time than the recording did.
When a bug can't be reproduced locally, get an artefact rather than another
hypothesis.

### The actual defect

```ts
const cellFromPoint = (clientX, clientY) => {
  const el = document.elementFromPoint(clientX, clientY);
  if (!el) return null;
  if (el.dataset.row === undefined) return null;   // ← silently discards the move
  ...
```

Two WebKit-specific problems, both producing exactly one highlighted cell:

1. **Hit-testing under pointer capture.** `onPointerDown` calls
   `setPointerCapture`. While a pointer is captured, WebKit can return the
   *capture target* from a hit test rather than the element under the finger. The
   capture target is the grid, which has no `data-row`, so every `pointermove`
   hit `return null` and was dropped.
2. **`onPointerLeave` committing the selection.** With capture taken, move and up
   still arrive even outside the element — so leaving is *not* the end of a drag.
   If WebKit fires `pointerleave` when capture is taken, the handler committed a
   one-cell selection instantly, ending the drag before the finger moved.

**Fix: don't hit-test, do arithmetic.**

```ts
const rect = gridRef.current.getBoundingClientRect();
const col = clamp(Math.floor(((clientX - rect.left) / rect.width) * cols), 0, cols - 1);
const row = clamp(Math.floor(((clientY - rect.top) / rect.height) * rows), 0, rows - 1);
```

A uniform grid's geometry already determines which cell a point falls in. Asking
the DOM was doing work that could be computed — and taking on the DOM's
browser-specific edge cases for free. It's also faster (no hit test per move) and
clamping means a finger straying past the edge keeps dragging instead of
dropping the selection. `onPointerLeave` was removed entirely; capture already
guarantees delivery.

**The general principle: prefer computing over querying when the answer is
already determined by data you hold.** A hit test asks "what is under this
point?" — a question with browser-, overlay-, and capture-dependent answers. The
arithmetic asks "which cell contains this point?", which has exactly one answer
everywhere.

### The caveat worth keeping

Why it worked on one iPhone and not another was never established — most likely
an iOS version difference in hit-testing under capture. The fix removes the
dependency entirely rather than explaining the divergence, so it holds either
way. **Note the difference between fixing a bug and understanding it**; this was
the former, and saying so is more useful than implying the latter.

---

## "Still shows submitted after switching accounts" — caches that outlive an identity (2026-08-31)

The report: play a game, sign in as a **different account**, and the round still
shows as submitted. Clearing browser history didn't help.

That last clause is the diagnostic gift. **Browsing history and `localStorage`
are different stores.** Chrome's "Clear browsing history" checkbox clears the
visited-URL list; site data (localStorage, IndexedDB, cache) is a *separate*
checkbox that most people never tick. So "I cleared history and it persisted"
doesn't mean "it isn't client-side" — it points straight at localStorage.

### Cause 1 — the cache key named the event but not the player

```typescript
// before
const playedRoundsKey = `playedRounds:${eventProp?.id}`;
```

The comment above it even said *"Key is scoped to the event so different events
don't collide"* — which is true, and incomplete. Two things vary here, not one:
which event, and **which person**. Scoping to only one of them makes "already
submitted" a property of the browser.

```typescript
// after
const identityKey = isLoggedIn
  ? currentUserId ? `u:${currentUserId}` : null   // null = /users/me still in flight
  : `anon:${anonId ?? "guest"}`;

const playedRoundsKey =
  identityKey && eventProp?.id ? `playedRounds:${eventProp.id}:${identityKey}` : null;
```

Three details in that snippet that matter more than the renaming:

- **`null` for "not resolved yet"** is a third state, distinct from logged-out.
  Logged in but `/users/me` hasn't returned means we don't yet know whose bucket
  to use — so we neither read nor write. Defaulting to a "guest" bucket instead
  would have quietly filed one account's plays under another's key.
- **Reload on identity change, don't merge.** An effect keyed on
  `[eventId, joinedSessionsKey, playedRoundsKey]` *replaces* both sets from the
  new key. Merging would have preserved the exact leak being fixed.
- **Purge the old unscoped keys.** Shipping the new key layout fixes new writes;
  every existing user is still carrying a poisoned `playedRounds:<eventId>`
  entry. A one-line `removeItem` of the legacy keys in the same effect is the
  migration. *A key-format change needs a cleanup pass for data already on disk.*

### Cause 2 — sign-out did a client-side navigation

```typescript
// before
router.push("/auth/login");
```

`router.push` is a **client-side** transition: React unmounts components, but the
Redux store — and with it every RTK Query response cached under the outgoing
account — survives. The next person to sign in on that tab inherits the previous
account's `game-sessions/:id` payload, `rounds[].hasPlayed` included.

```typescript
// after
window.location.href = "/auth/login";
```

A hard navigation tears down the JS heap. You *can* instead dispatch
`api.util.resetApiState()` for each API slice, but that's a list someone has to
remember to extend every time a new slice is added — the reload can't be
forgotten. **Sign-out is the one place where a full page load is the feature.**
(The marketing navbar's logout already did this; only the settings screen
didn't, which is why the bug depended on *which* sign-out button you used.)

### The pattern under both

Neither cause was a wrong calculation — the server was right the whole time.
`GET /v1/game-sessions/:id` returns per-user `rounds[].hasPlayed` derived from a
`@@unique([gameRoundId, userId])` row. Both bugs were **client-side caches whose
lifetime was longer than the identity they described.**

The question to ask of any client cache: *what invalidates this?* If the honest
answer is "nothing, until the tab closes", then anything user-specific in it is
a cross-account leak waiting for someone to share a device. Two mitigations,
and you generally want both:

1. Put the identity **in the key**, so a switch reads a different bucket rather
   than needing a correct eviction.
2. Make sign-out destroy the whole cache, so anything you forgot to key still
   can't survive.

### Where it *wasn't*

The share-link game page (`/game/[token]`) has its own `playedRounds`, but as
plain React state with no persistence — so it was never affected. Worth
confirming rather than assuming: two components with the same variable name had
materially different exposure.
