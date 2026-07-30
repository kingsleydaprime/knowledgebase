# Arete Mobile — Navigation & State Management

Split out from the original single-file `mobile-learning.md`. Covers expo-router file-based
routing and zustand state management. See also `01-react-native-fundamentals.md`.

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

