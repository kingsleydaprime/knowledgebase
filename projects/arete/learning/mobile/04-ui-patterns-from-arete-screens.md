# Arete Mobile — UI Patterns from Arete's Screens

Split out from the original single-file `mobile-learning.md`. Covers backgrounding-safe timers,
optimistic updates, server-driven display text, animation library choice, haptics, pull-to-refresh,
and design tokens.

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

