# SocioBoom Frontend — TanStack Query, Polling & Payload Discipline

Split out from the original flat `frontend-learning.md` (moved to `learning/archive/`). See also
`learning/frontend/07-pitfalls-and-honest-ui.md` (the "only offer what the backend can do" rule that
grew out of these lessons), `learning/backend/05-queues-and-jobs.md` (the background jobs being
polled), and `learning/frontend/06-feature-walkthroughs.md` (these patterns in real screens).

This file covers: TanStack Query v5 patterns — queries, mutations, cache keys and invalidation —
polling a long-running background agent and the async job UX that goes with it (pending states,
progress feedback, terminal states), and the "send what you collect" lesson: the payload bugs that
happen when the form gathers a field the request body never actually carries.

---

## 10. Tanstack Query v5 Patterns

Tanstack Query (formerly React Query) manages server state — data that comes from an API. It handles caching, background refetching, loading states, and error states, removing the need to manually manage these with `useState` + `useEffect`.

### Setup

The `QueryClient` is configured in `src/shared/providers/index.tsx`:

```typescript
"use client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient();

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
```

This wraps the application so every component can use Tanstack Query hooks.

Note: The `queryClient` is defined outside the component. This is intentional — it should not be re-created on every render. In a Next.js app with multiple users, you would create it inside the component with a `useState` to ensure each user gets their own instance, but for a client-side app this pattern is fine.

### `useQuery` for Fetching Data

```typescript
import { useQuery } from "@tanstack/react-query";
import axios from "axios";

function PostsList() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["posts"],        // cache key — must be unique per query
    queryFn: async () => {
      const response = await axios.get("/api/v1/posts");
      return response.data;
    },
  });

  if (isLoading) return <Skeleton />;
  if (isError) return <div>Error: {error.message}</div>;

  return (
    <ul>
      {data.posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

The `queryKey` is how TQ identifies and caches queries. Include any dynamic values that affect the result:

```typescript
// This query re-fetches when businessName changes
const { data } = useQuery({
  queryKey: ["reviews", businessName],
  queryFn: () => fetchReviews(businessName),
  enabled: !!businessName,  // don't run if businessName is empty
});
```

### `useMutation` for Creating/Updating/Deleting

```typescript
import { useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { toast } from "sonner";

function CreatePost() {
  const queryClient = useQueryClient();

  const { mutate, isPending } = useMutation({
    mutationFn: async (postData: CreatePostDTO) => {
      const response = await axios.post("/api/v1/posts", postData);
      return response.data;
    },
    onSuccess: () => {
      toast.success("Post scheduled!");
      // Invalidate the posts list so it re-fetches with the new post
      queryClient.invalidateQueries({ queryKey: ["posts"] });
    },
    onError: (error) => {
      toast.error("Failed to schedule post.");
    },
  });

  return (
    <Button
      disabled={isPending}
      onClick={() => mutate({ content: "Hello world", platforms: ["twitter"] })}
    >
      {isPending ? "Scheduling..." : "Schedule Post"}
    </Button>
  );
}
```

### v5 API Changes from v4

Tanstack Query v5 changed the API slightly from v4:

```typescript
// v4 (old)
const { isLoading } = useQuery(["key"], fetchFn);

// v5 (current in SocioBoom)
const { isLoading } = useQuery({
  queryKey: ["key"],
  queryFn: fetchFn,
});

// isPending replaces isLoading for mutations in v5
const { isPending } = useMutation({ mutationFn: ... });
```

### Why Not `useEffect` + `fetch`?

You could write this manually:

```typescript
const [data, setData] = useState(null);
const [isLoading, setIsLoading] = useState(true);

useEffect(() => {
  fetch("/api/posts")
    .then(r => r.json())
    .then(d => { setData(d); setIsLoading(false); });
}, []);
```

But this misses: caching (re-fetch every render), background updates, deduplication (two components fetching the same endpoint make two requests), error handling, stale-while-revalidate, and more. Tanstack Query handles all of this automatically.

---


## 19. Polling a Background Agent: Async Job UX

When Pain-Point Discovery became a background agent (1–3 minute runs), the frontend contract changed completely. The old flow was one awaited request:

```ts
const { data } = await axios.post(`${API}/discovery/search`, {...});
setPainPoints(data.painPoints);   // everything arrives at once, or times out
```

The new flow is **kickoff + poll**:

```ts
// 1. Kickoff — returns immediately with 202 and a session in status "running"
const { data } = await axios.post(`${API}/discovery/search`, { appDescription, platforms, searchProvider });
const sessionId: number = data.session.id;

// 2. Poll — results GROW while the agent works, because it saves incrementally
for (let i = 0; i < MAX_POLLS && activeSearch.current === searchToken; i++) {
  await new Promise((r) => setTimeout(r, POLL_INTERVAL_MS));
  const { data: snap } = await axios.get(`${API}/discovery/${sessionId}`);
  setPainPoints(snap.painPoints ?? []);           // streaming feel, no WebSockets
  if (snap.session.status !== "running") {        // completed | failed
    setAgentSummary(snap.session.summary ?? null);
    break;
  }
}
```

### The cancellation token pattern

The subtle bug in any polling loop: the user starts a search, gets bored, starts *another* search — now two loops are alive, and the old one keeps overwriting state with stale results. Or the user navigates away and the loop calls `setState` on an unmounted component.

The fix is a **ref token**:

```ts
const activeSearch = React.useRef(0);

// on unmount, invalidate whatever loop is running
useEffect(() => () => { activeSearch.current = -1; }, []);

const search = async () => {
  const searchToken = Date.now();
  activeSearch.current = searchToken;      // claiming the "current search" slot
  ...
  // inside the loop AND after it:
  if (activeSearch.current !== searchToken) return;   // someone superseded us — stop silently
  ...
  finally {
    if (activeSearch.current === searchToken) setSearching(false);
  }
};
```

Why a **ref** and not state? Because the check happens *inside an async closure*. State captured in a closure is frozen at the moment the closure was created; a ref is a live pointer — reading `.current` always gives the latest value. This is the canonical fix for "stale closure" bugs in async React code.

### Status-driven UX decisions

- Poll interval **4 s**: fast enough to feel live, slow enough that a 3-minute run costs ~45 requests against the backend's 200-per-15-min rate limit. Polling frequency is a rate-limit budget decision, not a taste decision.
- One **combined endpoint** (`{ session, painPoints }`) instead of two — halves request volume.
- Cap the loop (`MAX_POLLS`) and handle the timeout case explicitly ("still working — check Saved Sessions") instead of spinning forever.
- Distinguish all three endings with different toasts: `failed` (check API keys), `completed` with results, `completed` empty (refine the description). Every terminal state the backend can produce needs a UI sentence.
- Show partial results *while* `searching` — the render gate changed from `searched && painPoints.length > 0` to `(searching || searched) && painPoints.length > 0`. The whole point of incremental saves is lost if the UI hides them until the end.

---

## 20. Send What You Collect: Payload Lessons

A bug worth studying because it produced **zero errors**: the AI panel generated per-platform post variants and stored them in state —

```ts
const [platformContent, setPlatformContent] = useState<Record<string, string>>({});
// filled by AIGeneratePanel's onGenerate callback, shown in PostPreview…
```

— and then the schedule request sent only `content: postContent`. The variants were collected, previewed… and thrown away. Every platform received the same text, silently contradicting the product's whole pitch ("never the same post twice"). No console error, no failed request. The only way to catch this class of bug is to **read the request payload and ask: is everything the user built actually in here?**

The fix, and the pattern for conditional payloads:

```ts
// Only send variants for platforms actually selected, and only non-empty ones
const buildContentByPlatform = () => {
  const map: Record<string, string> = {};
  for (const p of selectedPlatforms) {
    if (platformContent[p]?.trim()) map[p] = platformContent[p];
  }
  return Object.keys(map).length ? map : undefined;   // undefined = key omitted from JSON
};

const body = {
  content: postContent,                      // fallback for platforms without a variant
  contentByPlatform: buildContentByPlatform(),
  subreddit: subreddit.trim() || undefined,  // "" would fail backend validation; undefined won't
  ...
};
```

Two idioms to keep:
- **`undefined` means "omit"** — `JSON.stringify` drops `undefined` values, so optional fields stay clean instead of arriving as `""` or `{}` and confusing backend validation.
- **Round-trip symmetry**: whatever you send on create, you must restore on edit. The edit loader gained `setPlatformContent(post.contentByPlatform ?? {})` and `setSubreddit(post.subreddit ?? "")` — forgetting this half means editing a post silently discards its variants.

---


