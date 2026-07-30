# NextVibe — Backend Games: AI Generation & Anonymous Play

Split out from the original flat `learning.md` (moved to `learning/archive/`). See also
`learning/backend/03-modules.md` Part 10 for the core Games Module (payment gate, viral share
tokens, score calculation, reward distribution) that this file builds on top of, and
`learning/09-devops.md` Part 55 for the production out-of-memory incident that this AI generation
service caused. For the frontend consumption of this system (word puzzle audits, the True/False
pivot, anonymous play UX, dead code cleanup), see `learning/frontend/07-payments-games.md`.

This file covers: OpenRouter as a unified AI model gateway (and why it was added alongside
direct Gemini calls), the full anonymous/guest game-play system (Redis-backed guest sessions,
the join/submit/merge endpoint trio, the guest-to-user merge pattern), the word-puzzle
config-shape serialization bug that silently zeroed every score, and the `EventPlan` null-guard
bug where a free event's session could be created without payment being properly gated.

---

## Part 48 — OpenRouter: One API for Every AI Model

### What OpenRouter Is

OpenRouter is a routing layer that sits in front of dozens of AI model providers (OpenAI, Anthropic, Google, Mistral, Perplexity, Meta, etc.) and exposes them all through a single, unified API. Instead of managing separate API keys and SDKs for each provider, you have one key and one endpoint.

```
Your app
    │
    ▼
OpenRouter  (https://openrouter.ai/api/v1)
    │
    ├── OpenAI         (gpt-4o, o3, o1)
    ├── Anthropic      (claude-3.5-sonnet, claude-3-haiku)
    ├── Google         (gemini-2.5-flash, gemini-2.5-pro)
    ├── Perplexity     (sonar-pro, sonar-reasoning)
    ├── Meta           (llama-3.3-70b, llama-4-scout)
    ├── Mistral        (mistral-large, codestral)
    └── ...50+ more
```

### Why Use It Instead of Direct Provider APIs

- **One key to manage** — single `OPENROUTER_API_KEY`, not separate keys for OpenAI + Anthropic + Google
- **Easy model switching** — change one string (`"gpt-4o"` → `"claude-3.5-sonnet"`) to compare models or fall back if one is down
- **Fallbacks and load balancing** — OpenRouter can automatically fall back to another model if your primary is rate-limited
- **Unified billing** — one invoice, one dashboard for all usage across providers
- **Cost visibility** — see exactly what each model costs per token before you commit

### The OpenAI SDK as a Universal AI Client

OpenRouter uses the same request/response format as OpenAI's Chat Completions API. This means you can use the `openai` npm package to talk to OpenRouter — just change the `baseURL` and `apiKey`:

```typescript
import OpenAI from 'openai';

// OpenAI directly
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// OpenRouter — same SDK, different URL + key
const openRouter = new OpenAI({
  apiKey: process.env.OPENROUTER_API_KEY,
  baseURL: 'https://openrouter.ai/api/v1',
  defaultHeaders: {
    'HTTP-Referer': 'https://yourapp.com',   // identifies your app to OpenRouter
    'X-Title': 'Your App Name',              // shown in OpenRouter dashboard
  },
});

// Calling either one is identical
const response = await openRouter.chat.completions.create({
  model: 'anthropic/claude-3.5-sonnet',
  messages: [{ role: 'user', content: 'Hello' }],
});
```

This is the OpenAI-compatible API pattern — many providers (Mistral, Together AI, Groq, Ollama for local models) expose the same interface. One SDK, many providers.

### Web Search in AI: Online Models

Some AI models can search the web in real time before generating a response. This solves the fundamental LLM problem: training data has a cutoff date. A model trained on data from 2024 doesn't know about an event that happened last week.

For game generation, web search means:
- "Generate trivia about the FIFA 2026 World Cup" → model can search for actual recent results, correct scores, real players
- "Generate questions about [artist]'s latest album" → model searches for the actual track list instead of hallucinating
- "Create a word puzzle about Nigerian fintech news" → model pulls current companies and events, not outdated training data

**Perplexity Sonar** is the primary web-search AI provider. Their models always search the web — it's not optional. `perplexity/sonar-pro` is their most capable search-augmented model.

**The `:online` suffix** — on OpenRouter, any model can have web search added by appending `:online`:
```
google/gemini-2.5-flash          ← no web search
google/gemini-2.5-flash:online   ← web search enabled
openai/gpt-4o:online             ← GPT-4o with web search
```

OpenRouter handles the search plumbing — the model gets web results injected into its context automatically.

### Structured JSON Output on OpenRouter

Gemini enforces JSON via a `responseSchema` object in its generation config. OpenRouter uses the OpenAI standard:

```typescript
response_format: { type: 'json_object' }
```

This tells the model to always return valid JSON — no markdown fences, no explanation text, just the JSON object. Not all models honour this (especially smaller open-source ones), but all major commercial models do.

For even stricter control, OpenAI-compatible APIs also support JSON Schema via:
```typescript
response_format: {
  type: 'json_schema',
  json_schema: { name: 'game_draft', schema: yourSchemaObject }
}
```

### The Model ID Format on OpenRouter

```
{provider}/{model-name}:{variant}

anthropic/claude-3.5-sonnet
google/gemini-2.5-flash
openai/gpt-4o
perplexity/sonar-pro
meta-llama/llama-3.3-70b-instruct
openai/gpt-4o:online              ← with web search
google/gemini-2.5-flash:online    ← Gemini with web search
```

Browse available models and their costs at `openrouter.ai/models`.

### In This Codebase

`generateGameDraftViaOpenRouter()` is the new method. It uses `perplexity/sonar-pro` for web-grounded game generation. The `generateGameDraft()` method (Gemini) is kept as-is. To switch which one the games controller calls, change one method name in the game generation controller.

The `HTTP-Referer` and `X-Title` headers are required by OpenRouter — they appear in your usage dashboard and help OpenRouter attribute traffic to your app. If omitted, some models may reject the request.

(See `learning/09-devops.md` Part 55 for the production OOM incident this same `AiGeneratorService` caused on a 512MB Render instance, and the per-game-type token-cap fix.)

---

## Part 49 — Anonymous Game Play and the Guest-to-User Merge Pattern

### Why anonymous play?

Game rounds are shared via a `shareToken` link. The link is meant to go viral — shared outside the platform to people who don't have accounts. If login is required to even see the game, virality dies. Anonymous play lets anyone click the link, play immediately, and be nudged to create an account after they see their score.

This is a **conversion funnel pattern**: friction-free first experience → hook them with a score → offer account creation to persist the score.

---

### The three anonymous endpoints

All three are `@Public()` — no `JwtAuthGuard` required:

```typescript
// 1. Join a game session — creates/retrieves a Redis guest session
POST /v1/games/anonymous/join/:token
Body: { anonymousId?: string }     // send existing ID to resume a session; omit to create new
Response: { anonymousId, sessionId, eventId, eventName }

// 2. Submit answers for a round
POST /v1/games/anonymous/rounds/:roundId/submit
Body: { answers: number[], anonymousId: string }
Response: { score: number, correct: number, total: number }

// 3. Merge all anonymous scores into the now-authenticated user's account
POST /v1/games/anonymous/merge
Body: { anonymousId: string, confirmedEventIds: string[] }
Auth: JwtAuthGuard (this one IS protected — user must be logged in to merge)
Response: { merged: number }
```

(See `learning/backend/02-auth.md` Part 46 for the `@Public()` guard pattern these first two endpoints rely on.)

---

### Redis as the anonymous session store

Anonymous game data lives in Redis, not PostgreSQL. The Redis key format:

```
anon:game:<anonymousId>
```

The value is a JSON object:

```typescript
interface AnonymousGameData {
  anonymousId: string;
  sessions: {
    sessionId: string;
    eventId: string;
    eventName: string;
    rounds: {
      roundId: string;
      answers: number[];
      score: number;
    }[];
  }[];
}
```

**Why Redis, not PostgreSQL?**

1. **Anonymous data is temporary.** If a guest never creates an account, their data shouldn't clutter the database. Redis keys can have a TTL (e.g., 7 days) so the data auto-expires.
2. **Speed.** Anonymous game submissions need to respond fast. Redis is in-memory and can handle this without a database write on every answer.
3. **No schema coupling.** The anonymous session doesn't need to satisfy foreign key constraints (e.g., `GameEntry` requires a real `userId`). Storing in Redis sidesteps this entirely.

(See `learning/00-sys-design.md` for the general Redis-vs-PostgreSQL decision framework this design follows.)

---

### The anonymous ID — security model

```typescript
const anonymousId = existingAnonId ?? nanoid(21);
```

The anonymous ID is a random `nanoid(21)` — 21 characters from a URL-safe alphabet, generating ~10 septillion possible values. It's:
- **Non-guessable** — brute-forcing another user's anonymous session is computationally infeasible
- **Not tied to identity** — it's just a random token, not linked to an IP or device fingerprint

The ID is generated by the backend on the first join call, or re-used if the frontend passes back its stored ID. This allows a user to re-open the same game (e.g., browser refresh) and continue from their existing anonymous session.

**Stored in:** `localStorage` on the client (`nv_anon_game` key), `Redis` on the server.

---

### The join endpoint — finding the session by token

```typescript
async joinSessionAnonymously(token: string, existingAnonId?: string) {
  // Find the session by share token
  const session = await this.prisma.gameSession.findUnique({
    where: { shareToken: token },
    include: { event: true },
  });
  if (!session) throw new NotFoundException('Session not found');

  const anonymousId = existingAnonId ?? nanoid(21);

  // Load or create the Redis record for this anonymous user
  const existing = await this.redis.get(`anon:game:${anonymousId}`);
  const data: AnonymousGameData = existing ? JSON.parse(existing) : {
    anonymousId,
    sessions: [],
  };

  // Add this session if not already tracked
  if (!data.sessions.some(s => s.sessionId === session.id)) {
    data.sessions.push({
      sessionId: session.id,
      eventId: session.eventId,
      eventName: session.event.name,
      rounds: [],
    });
  }

  await this.redis.setex(
    `anon:game:${anonymousId}`,
    60 * 60 * 24 * 7,    // 7-day TTL — expires if no account is created
    JSON.stringify(data)
  );

  return { anonymousId, sessionId: session.id, eventId: session.eventId, eventName: session.event.name };
}
```

The `shareToken` field on `GameSession` is a `@unique` scalar — Prisma returns it in all `findUnique` and `findMany` results by default (no `select` needed), which is why it appears on the list endpoint response used by the frontend.

---

### The submit endpoint — scoring without a user row

```typescript
async submitRoundAnonymously(roundId: string, answers: number[], anonymousId: string) {
  const round = await this.prisma.gameRound.findUnique({
    where: { id: roundId },
    include: { session: true },
  });

  const score = this.calculateScore(round.session.gameType, round.config, { answers });

  // Update the Redis record with the submitted round
  const raw = await this.redis.get(`anon:game:${anonymousId}`);
  if (!raw) throw new BadRequestException('Anonymous session expired or not found');

  const data: AnonymousGameData = JSON.parse(raw);
  const sessionRecord = data.sessions.find(s => s.sessionId === round.sessionId);
  if (!sessionRecord) throw new BadRequestException('Session not found in anonymous record');

  // Idempotency: only record once per round
  if (!sessionRecord.rounds.some(r => r.roundId === roundId)) {
    sessionRecord.rounds.push({ roundId, answers, score });
  }

  await this.redis.setex(`anon:game:${anonymousId}`, 60 * 60 * 24 * 7, JSON.stringify(data));
  return { score };
}
```

Note the **idempotency check** (`!sessionRecord.rounds.some(r => r.roundId === roundId)`). The backend never lets an anonymous player submit the same round twice — same as the `@@unique([gameRoundId, userId])` constraint for authenticated players.

---

### The merge endpoint — converting guest scores to real scores

When the user logs in after anonymous play, the frontend calls merge with:
- `anonymousId` — from localStorage
- `confirmedEventIds` — which events' scores to move (chosen by the user in the `AnonymousMergeDialog`)

```typescript
async mergeAnonymousSessions(userId: string, anonymousId: string, confirmedEventIds: string[]) {
  const raw = await this.redis.get(`anon:game:${anonymousId}`);
  if (!raw) return { merged: 0 };

  const data: AnonymousGameData = JSON.parse(raw);

  // Filter to only the sessions the user confirmed
  const sessionsToMerge = data.sessions.filter(s =>
    confirmedEventIds.includes(s.eventId)
  );

  let merged = 0;
  for (const session of sessionsToMerge) {
    for (const roundRecord of session.rounds) {
      // Skip if user already has a real GameEntry for this round
      const exists = await this.prisma.gameEntry.findUnique({
        where: { gameRoundId_userId: { gameRoundId: roundRecord.roundId, userId } },
      });
      if (exists) continue;

      // Create the real GameEntry with the anonymous score
      await this.prisma.gameEntry.create({
        data: {
          gameRoundId: roundRecord.roundId,
          userId,
          answers: roundRecord.answers,
          score: roundRecord.score,
          completedAt: new Date(),
        },
      });
      merged++;
    }

    // Also ensure the user has a GameSessionEntry (for the overall leaderboard)
    await this.prisma.gameSessionEntry.upsert({
      where: { gameSessionId_userId: { gameSessionId: session.sessionId, userId } },
      create: { gameSessionId: session.sessionId, userId, totalScore: 0 },
      update: {},
    });
  }

  // Recalculate totalScore for each merged session
  for (const session of sessionsToMerge) {
    await this.recalculateSessionScore(session.sessionId, userId);
  }

  // The Redis key is NOT deleted here — the frontend deletes localStorage
  // and never calls merge again, making the Redis key effectively dead (expires via TTL)
  return { merged };
}
```

**Why not delete the Redis key after merging?**

The frontend is responsible for clearing `localStorage` after merge (via `clearAnonGameData()` in the `finally` block). The Redis key will expire via its 7-day TTL. Deleting it from the backend would require a round-trip for no practical benefit — the key is inaccessible once the frontend has cleared the anonymous ID from localStorage.

---

### The `AnonymousMergeDialog` — multi-event UX

When a guest played rounds across multiple events (e.g., joined two different friends' events as a guest), the merge dialog asks which events to keep scores for:

```tsx
<AnonymousMergeDialog
  sessions={pendingSessions}        // AnonPendingSession[]
  isLoading={isMerging}
  onConfirm={(ids) => confirmMerge(ids, () => router.replace(destination))}
  onSkip={() => skipMerge(() => router.replace(destination))}
/>
```

The dialog shows event names from `pendingSessions`. The user picks which events' scores to merge. Unchecked events are simply not sent in `confirmedEventIds` — their anonymous scores are abandoned.

When there is only a single event, the dialog is skipped and merge happens silently.

(See `learning/frontend/07-payments-games.md` Part 51 for the full frontend implementation of this dialog, the `PUBLIC_PATHS` allowlist that prevents a 401 redirect loop on the public game page, and the stale-closure trap in the submit handler.)

---

### Data lifecycle summary

```
1. User clicks share link                    → no localStorage data
2. Anonymous join                            → anonymousId stored in localStorage + Redis
3. Play rounds                               → Redis updated per round
4. See score screen → login link shown       → user clicks "Log in"
5. Login completes                           → handlePostAuth runs
6. If single event: merge silently           → GameEntry rows created in PostgreSQL
7. If multiple events: show dialog           → user picks, then merge
8. Finally block runs                        → clearAnonGameData() wipes localStorage
9. Redirect to destination                   → user sees real leaderboard with their score
10. Redis key expires in 7 days             → anonymous data gone forever
```

---

### Pattern: best-effort with `finally` cleanup

The merge uses a try/catch/finally in `useAnonMerge`:

```typescript
try {
  await mergeSessions({ anonymousId, confirmedEventIds }).unwrap();
} catch {
  // don't block the user if merge fails — they can still use the app
} finally {
  clearAnonGameData();   // always clears
  setShowDialog(false);
}
```

This is the right pattern for "cleanup that must happen regardless of success or failure." If the merge API call throws (network down, server error), the user isn't stuck — they land on the app without their anonymous scores being merged, which is better than being stuck on a loading spinner. The anonymous data in localStorage is also cleared so they don't see stale merge prompts on future logins.

---

## Part 53 — Game Session Config Structure: The Word Puzzle Serialization Bug

### The Config Shape the Backend Expects

`GameRound.config` is a JSON column. The exact shape the backend reads for each game type is hardcoded in `games.service.ts → calculateScore`. Get this shape wrong and scoring silently returns 0.

**WORD_PUZZLE config — the backend reads `questions[0].hiddenWords[]`:**

```json
{
  "questions": [
    {
      "grid": [["C","A","T",...], ...],
      "hiddenWords": [
        { "word": "CAT", "startCell": [0,0], "endCell": [0,2], "direction": "HORIZONTAL" },
        { "word": "DOG", "startCell": [1,0], "endCell": [1,2], "direction": "HORIZONTAL" }
      ],
      "points": 20
    }
  ]
}
```

All hidden words live inside a single `questions[0]` object. `questions.length` is always 1 for word puzzle.

**What the wizard was doing wrong (the bug):**

The wizard had been creating one question entry per hidden word:

```json
{
  "questions": [
    { "word": "CAT", "startCell": [0,0], "endCell": [0,2], "direction": "HORIZONTAL", "points": 10 },
    { "word": "DOG", "startCell": [1,0], "endCell": [1,2], "direction": "HORIZONTAL", "points": 10 }
  ]
}
```

The backend's `calculateScore` reads `config.questions[0].hiddenWords` and finds it undefined — scoring returns 0 every time. The game played, players submitted answers, but all scores were 0. No error was thrown.

**The fix (in the wizard's `handleComplete`):**

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

**The lesson:** when a backend service reads structured JSON from a database column, there is only one valid shape. The code that writes that JSON must produce the exact same shape the reader expects. When they're in different files (wizard vs games.service.ts), drift is easy to miss and silent to fail.

(See `learning/frontend/07-payments-games.md` Part 57 for the full frontend serialization step in the wizard's `handleComplete`, including why the wizard's internal per-word `Question` state needed this translation layer at all.)

### THIS_OR_THAT Scoring: Changed from Participation to Correct-Answer

The original `calculateScore` for `THIS_OR_THAT` gave points to everyone regardless of answer — it was a participation game. After the pivot to True/False (where there is a definitive correct answer), the scoring changed:

```typescript
// Old — participation:
case 'THIS_OR_THAT':
  totalScore += question.points || 5;
  break;

// New — correct answer required:
case 'THIS_OR_THAT':
  if (Number(userAnswer) === question.correctAnswerIndex) {
    totalScore += question.points || 5;
  }
  break;
```

`userAnswer` is a string (submitted by the frontend as the option index). `Number()` converts it to a number before comparing. `correctAnswerIndex` is 0 for True, 1 for False. The answer stored in the config is `correctAnswerIndex`, not the option text.

(See `learning/frontend/07-payments-games.md` Part 56 for the full frontend side of this True/False pivot, including the wizard UI changes and the AI prompt update.)

---

## Part 54 — EventPlan Null Guard: The paymentRequired Disagreement Bug

### How EventPlan is Created

`EventPlan` has exactly one creator in the entire codebase: `activatePayment()` in `organizer-payments.service.ts`. It uses `eventPlan.upsert()`. It is called:

1. When an organizer pays for a plan (Ercaspay webhook fires `activatePayment()`)
2. When a coupon covers 100% of the cost (free payment path — `activatePayment()` is called immediately)
3. As a fallback in `verifyPayment()` — if the webhook was missed, the frontend can trigger verification which calls `activatePayment()` if the payment reference is confirmed

**Free events never get an EventPlan.** Creating an event is free. Publishing a free event (no tickets, no games, no VibeTags) costs nothing and bypasses the billing flow entirely. A free event's `EventPlan` is always `null`.

### The Bug

`createSession` had this logic:

```typescript
// Old — broken:
let paymentRequired = false;
if (plan) {
  if (plan.gamesUsed >= plan.gamesIncluded) {
    paymentRequired = true;
  }
}
// If plan is null → paymentRequired stays false
// The session is created with paymentRequired: false
```

Then if the organizer tried to activate the session (`updateStatus` to `ACTIVE`), the service threw:

```
400 Bad Request: No active event plan found for this event
```

The `createSession` response told the organizer "no payment required" but `updateStatus` refused to activate. Contradiction. The organizer would see a game in PENDING state that appeared free but couldn't be activated.

**The fix:**

```typescript
const paymentRequired = !plan || plan.gamesUsed >= plan.gamesIncluded;
```

Now a null plan correctly signals `paymentRequired: true`. The organizer is told upfront they need to purchase a plan. The wizard can show a payment flow before creating the session.

### The Mental Model

EventPlan is a gate, not a side effect. Before running any game session, the system must confirm:
- A plan exists (organizer has purchased)
- The plan has remaining quota (`gamesUsed < gamesIncluded`)

Both conditions must be true. The old code only checked the second condition when the plan existed, treating "no plan" as "no gate." The new code treats "no plan" as a failed gate.

(See `learning/00-sys-design.md` Domain 6 — Billing for the `EventPlan` model's role in the schema, and `learning/backend/03-modules.md` Part 10 for the game session status-lifecycle state machine this gate feeds into.)
