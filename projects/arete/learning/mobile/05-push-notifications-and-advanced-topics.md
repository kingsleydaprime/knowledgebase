# Arete Mobile — Push Notifications & Advanced Topics

Split out from the original single-file `mobile-learning.md`. Covers the push notification flow,
deep links, the build-vs-OTA-update distinction, performance checklist, and resilience habits.

---

## Part 6 — Push Notifications & Deep Links

### Push flow (expo-notifications)

1. App asks permission, gets an **Expo push token**.
2. App sends it to the backend: `PATCH /users/push-token`.
3. Backend stores it on the User row and sends via Expo's push API (see `notification.service.ts`).
4. Local scheduled notifications handle the "your timer finished" case even if the app is backgrounded (`scheduleQuestTimerNotification` in `lib/notifications.ts`).

### Deep links and the scheme

`app.json` declares `"scheme": "com.spectroniq.arete"` — this is how password-reset emails open the app (`com.spectroniq.arete://reset-password?token=...`). Arete originally used the scheme `arete`, which risks collisions with other apps; reverse-DNS of your package name is the convention. **Changing the scheme requires a new native build** (EAS), not just an OTA update — scheme registration lives in the native shell.

---

## Part 7 — Advanced Topics

### What needs a new build vs what doesn't

| Change | Needs EAS build? |
|---|---|
| JS/TS code, styles, screens | No (OTA update possible) |
| App icon, splash, scheme, permissions | **Yes** |
| Adding a native module | **Yes** |
| Env var baked via `EXPO_PUBLIC_*` | Baked at build time — yes to change |

`EXPO_PUBLIC_API_URL` in Arete is read at build time. A "staging build" and "prod build" differ only by that variable (configured per-profile in `eas.json`).

### Performance checklist

- Long lists → `FlatList`/`FlashList`, never `.map()` inside `ScrollView` past ~30 items.
- Wrap list-item components in `React.memo` if parents re-render often (the per-second `tick` in quests.tsx makes this matter).
- `useCallback` for handlers passed to memoized children; `useMemo` for derived data (see `useMemo` for `currentIndex` in progression.tsx).
- Images: give explicit dimensions; use `expo-image` for caching.

### Resilience habits used in Arete

- Every fire-and-forget call ends in `.catch(() => null)` — a failed notification or suggestion fetch must never crash a screen.
- Idempotent server endpoints mean the app can retry freely (tapping "start" twice returns the same `startedAt`).
- Fields added to API responses are optional in `types.ts` until every shipped app version knows them.

### The path screen — deriving UI from math (progression.tsx)

The Duolingo-style path isn't stored anywhere. It's generated:

```ts
// nodes = each rank threshold + 3 checkpoints between ranks
const PATH_NODES = RANKS.flatMap(/* boss node + 25/50/75% checkpoints */);
// zigzag = a sine wave over the node index
const offsetFor = (i: number) => Math.round(Math.sin(i * 1.05) * 68);
// your position = first node with more XP than you
const currentIndex = PATH_NODES.findIndex((n) => n.xp > pillarXp);
```

Then `onLayout` captures the current node's `y` and `scrollTo({ y: y - 220 })` centers you on it. **Lesson: prefer computing UI from data over storing UI state.** Less state = fewer bugs.

---

