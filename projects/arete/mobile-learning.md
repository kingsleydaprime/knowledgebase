# Mobile Engineering — Beginner to Advanced
### Everything used in the Arete mobile app (Expo SDK 54 + React Native), and why

---

## Part 1 — Absolute Beginner

### What React Native actually is

React Native (RN) lets you write UI in JavaScript/TypeScript, but it does **not** render HTML in a webview. Your `<View>` becomes a real Android `ViewGroup` / iOS `UIView`. That's why RN apps feel native — they are native views, driven by JS.

**Expo** is a toolchain on top of RN: it gives you the build system (EAS), a standard library of native modules (`expo-haptics`, `expo-notifications`, `expo-router`), and removes the need to touch Xcode/Android Studio for most work.

### The three primitives you'll use 95% of the time

```tsx
import { View, Text, StyleSheet } from 'react-native';

export default function Hello() {
  return (
    <View style={styles.card}>
      <Text style={styles.title}>ARETE</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: { padding: 16, backgroundColor: '#12121A', borderRadius: 8 },
  title: { color: '#FFF', fontSize: 20, fontWeight: '800' },
});
```

Key differences from web:
- There is no `div`/`span`/`p`. `View` = container, `Text` = ALL text (text outside `<Text>` crashes), `Image`, `ScrollView`, `TextInput`, `TouchableOpacity` (a pressable).
- Styles are JS objects, not CSS. No cascading, no classes, no units (numbers are density-independent pixels).
- **Everything is flexbox by default**, and `flexDirection` defaults to `column` (web defaults to `row`).

### Flexbox mental model (used everywhere in Arete)

```tsx
// A row with an icon left, text filling the middle, button right:
<View style={{ flexDirection: 'row', alignItems: 'center', gap: 12 }}>
  <Text>🔥</Text>
  <View style={{ flex: 1 }}>            {/* flex: 1 = "take remaining space" */}
    <Text>Spiritual</Text>
  </View>
  <TouchableOpacity>...</TouchableOpacity>
</View>
```

This exact pattern is the `shieldRow` in `streaks.tsx`. Learn `flexDirection`, `alignItems` (cross-axis), `justifyContent` (main axis), `flex: 1`, and `gap` — that's 90% of layout.

### State and effects — the two hooks that run everything

```tsx
const [count, setCount] = useState(0);        // component-local state

useEffect(() => {
  fetchData();                                 // runs after mount
  return () => cleanup();                      // runs on unmount
}, []);                                        // [] = run once
```

Rules that save hours of debugging:
- State updates are async — never read `count` right after `setCount(count + 1)`. Use the function form: `setCount(c => c + 1)` (see `setTick((t) => t + 1)` in the quest timer).
- The dependency array decides when an effect re-runs. `[]` = mount only. `[activeTab]` = whenever `activeTab` changes (this is how the HISTORY tab lazy-loads in `quests.tsx`).

---

## Part 2 — Project Structure & Navigation

### File-based routing with expo-router

In Arete, **the folder structure IS the navigation**:

```
mobile/app/
  index.tsx              → the "/" route (entry redirect)
  _layout.tsx            → root layout (providers, auth gate)
  (auth)/                → route group: login, register
  (onboarding)/          → route group: setup, assessment
  (app)/                 → route group: the real app
    _layout.tsx          → tab bar layout
    quests.tsx           → /quests
    progression.tsx      → /progression
    streaks.tsx          → /streaks
  components/            → shared UI (not routes)
  lib/                   → api client, types, notifications
  store/                 → zustand stores
  constants/             → theme, ranks, pillars
```

Things to know:
- Parentheses `(app)` create a **group** — it organizes files and gets its own `_layout.tsx`, but doesn't appear in the URL.
- `_layout.tsx` wraps every screen below it. The root layout is where auth redirects live ("no token? → `(auth)/login`").
- Navigate with `router.push('/quests')` or declaratively with `<Link>`.

### Passing data between screens: params vs global state

**Arete's documented decision:** transient onboarding data (faith, equipment) flows through **route params**, not a global store.

```tsx
// setup.tsx — send
router.push({ pathname: '/(onboarding)/assessment', params: { faith, equipment } });

// assessment.tsx — receive
const { faith, equipment } = useLocalSearchParams<{ faith: string; equipment: string }>();
```

**Why:** the data is only needed for the next screen and then submitted to the API. Putting it in a global store means you must remember to clear it, it survives app restarts confusingly, and it hides the data flow. Rule of thumb: *params for hand-offs, stores for data many screens read*.

---

## Part 3 — State Management with Zustand

Arete uses [zustand](https://github.com/pmndrs/zustand) — three small stores (`auth.store`, `quests.store`, `progression.store`) instead of Redux.

```ts
// The shape of a zustand store
import { create } from 'zustand';

interface QuestsState {
  todayData: TodayQuestsResponse | null;
  isLoading: boolean;
  fetchToday: () => Promise<void>;
  completeQuest: (questId: string) => Promise<CompleteQuestResponse>;
}

export const useQuestsStore = create<QuestsState>((set, get) => ({
  todayData: null,
  isLoading: false,
  fetchToday: async () => {
    set({ isLoading: true });
    const data = await questsApi.getToday();
    set({ todayData: data, isLoading: false });
  },
  completeQuest: async (questId) => {
    const result = await questsApi.complete(questId);
    // ...update todayData optimistically...
    return result;
  },
}));
```

Usage in any component — it's just a hook:

```tsx
const { todayData, isLoading, fetchToday } = useQuestsStore();
```

**Why zustand over Redux/Context:**
- No providers, no boilerplate, no action types. A store is ~30 lines.
- Reading outside React works: `useAuthStore.getState().accessToken` — this is exactly how the axios interceptor grabs the token without being a component.
- Context re-renders every consumer on any change; zustand components only re-render when the slice they read changes.

**When you'd outgrow it:** heavy server-cache needs (pagination, background refetch, cache invalidation) → add TanStack Query and keep zustand for client-only state.

---

## Part 4 — The API Layer (the most reusable file in the app)

`lib/api.ts` is a pattern worth memorizing. Three layers:

### 4.1 One axios instance with an auth interceptor

```ts
const client = axios.create({ baseURL: BASE_URL });

client.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
```

Every request gets the JWT automatically. No screen ever thinks about auth headers.

### 4.2 The refresh-token queue (advanced, and worth understanding deeply)

Problem: your access token expires (15 min in Arete). Five requests fire at once, all get 401. Naive code refreshes the token five times, and four refreshes may invalidate each other.

Solution — refresh once, queue the rest:

```ts
let isRefreshing = false;
let refreshQueue: Array<(token: string) => void> = [];

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;                    // never retry twice

      if (isRefreshing) {
        // someone else is already refreshing — park this request
        return new Promise((resolve) => {
          refreshQueue.push((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            resolve(client(originalRequest));           // replay when token arrives
          });
        });
      }

      isRefreshing = true;
      try {
        const { accessToken } = await refreshCall();
        refreshQueue.forEach((cb) => cb(accessToken));  // release the parked requests
        refreshQueue = [];
        return client(originalRequest);                 // replay the original
      } catch {
        clearAuth();                                    // refresh failed → log out
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  },
);
```

The moving parts: `_retry` flag prevents infinite loops, `isRefreshing` makes refresh a singleton, and the queue of callbacks replays every parked request with the new token. This is interview-question material — know it cold.

### 4.3 Typed endpoint modules

```ts
export const questsApi = {
  getToday: () => client.get<TodayQuestsResponse>('/quests/today').then((r) => r.data),
  complete: (questId: string) =>
    client.patch<CompleteQuestResponse>(`/quests/${questId}/complete`).then((r) => r.data),
};
```

All response shapes live in one `lib/types.ts` that mirrors the backend. When the backend adds a field (like `perfectDay`), you add it as **optional** (`perfectDay?: ...`) so old app versions in the wild don't break — servers and apps never update in lockstep.

---

## Part 5 — Real Patterns from Arete's Screens

### 5.1 Timers that survive backgrounding (quests.tsx)

**Wrong way:** count seconds with `setInterval(() => setElapsed(e => e + 1), 1000)`. The OS pauses JS timers when the app backgrounds — your timer silently drifts.

**Arete's way:** the server's `startedAt` timestamp is the source of truth; the interval only forces re-renders:

```tsx
const [tick, setTick] = useState(0);              // exists only to trigger re-render
useEffect(() => {
  const id = setInterval(() => setTick((t) => t + 1), 1000);
  return () => clearInterval(id);
}, []);

// elapsed is DERIVED from wall-clock time, every render:
const rawElapsedMs = Date.now() - new Date(quest.startedAt).getTime();
const elapsed = Math.floor((rawElapsedMs - quest.totalPausedMs - currentPauseMs) / 1000);
```

Kill the app, reopen it an hour later — elapsed is still correct, because it's computed from timestamps, not accumulated. **General principle: derive state from durable facts; never accumulate state you can compute.**

Pause handling stacks three buckets: server-committed pause time (`totalPausedMs`), pauses finished this session (`pausedMsRef`), and the currently-running pause (`Date.now() - pauseStart`). Same principle — each bucket is derived from timestamps.

### 5.2 Optimistic updates

When you tap "complete", the UI marks it complete *immediately*, then the API call confirms. If it fails, you roll back (or in Arete's case, a refetch corrects it). Users perceive the app as instant.

```tsx
const handleComplete = async (questId: string) => {
  markCompletedLocally(questId);        // instant UI
  try {
    const result = await completeQuest(questId);
  } catch {
    // silent — next fetch reconciles
  }
};
```

### 5.3 Server-driven display text (the variant system)

When we added specific daily missions ("Read John 3", "20 pushups, 30 squats"), the mobile app needed **zero changes** — because the backend substitutes the variant text into `task.name` before responding. The app just renders what it's told.

**Lesson for mobile architecture:** every string the server can own, the server should own. App store review takes days; a server deploy takes minutes. Content, copy, and configuration belong on the server.

### 5.4 Animations — two libraries, and when each is right

Arete uses **both** RN's built-in `Animated` and `react-native-reanimated`, deliberately:

```tsx
// Reanimated — runs on the UI thread, buttery for transforms/opacity:
const checkScale = useSharedValue(0);
checkScale.value = withSpring(1, { damping: 10, stiffness: 200 });
const style = useAnimatedStyle(() => ({ transform: [{ scale: checkScale.value }] }));

// Entry animations in one line:
<Animated.View entering={FadeInDown.delay(index * 60)}>
```

But `AnimatedBar` (the XP bar) uses the old `Animated` API. **Why:** the native driver can only animate `transform` and `opacity`. A progress bar animates `width: '43%'` — a layout property — which must run on the JS thread anyway, so Reanimated buys nothing there.

**Rule: transforms/opacity → Reanimated with native driver. Layout properties (width/height/padding) → JS-driven animation, keep them rare.**

### 5.5 Juice: haptics and celebrations

```tsx
import * as Haptics from 'expo-haptics';
Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
```

Cheap, and it makes completion feel physical. Pair with a celebration modal (`QuestCelebration.tsx`) for milestone moments. Retention lives in these details.

### 5.6 Pull-to-refresh (every list screen)

```tsx
<ScrollView
  refreshControl={
    <RefreshControl refreshing={refreshing} onRefresh={handleRefresh}
      tintColor={colors.accent} colors={[colors.accent]} />
  }
>
```

`tintColor` is iOS, `colors` is Android — set both or one platform looks broken.

### 5.7 Design tokens, not magic numbers

Every screen imports from one `constants/theme.ts`:

```ts
export const colors = { bg: '#0A0A0F', surface: '#12121A', accent: '#6C63FF', ... } as const;
export const spacing = { xs: 4, sm: 8, md: 16, lg: 24, xl: 32 } as const;
```

Changing the brand color is a one-line diff. Also note the alpha trick used everywhere: `color + '22'` appends a hex alpha to any color for translucent backgrounds (`#6C63FF22`).

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

## Part 9 — Study Path

1. **Weeks 1–2:** Components, props, state, flexbox. Rebuild the streaks calendar grid from scratch.
2. **Weeks 3–4:** expo-router navigation, zustand, axios. Rebuild the login → tabs flow.
3. **Month 2:** The refresh-queue interceptor, optimistic updates, timestamp-derived timers. These three patterns separate juniors from mid-levels.
4. **Month 3+:** Reanimated, push notifications end-to-end, EAS build profiles, performance profiling with React DevTools.
5. **Advanced:** read the RN "New Architecture" docs (Fabric/TurboModules), learn native modules basics, offline-first sync patterns.
