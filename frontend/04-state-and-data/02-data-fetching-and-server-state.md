# Data Fetching and Server State

> **[Intermediate]** · Server state is a cache, not state — and treating it as state is the most expensive mistake in frontend architecture.

## The distinction that reorganises everything

**Client state** is yours. It exists only in the browser, you're the source of truth, it's synchronous. *Is the modal open, what's in this form, which tab is selected.*

**Server state** is **someone else's state, cached locally.** You're not the source of truth. It's asynchronous, it goes stale, other users change it, and it can fail to load.

**Putting server state in a client store — Redux, Zustand, a `useState` — means hand-writing:**

- loading, error, empty and stale flags per resource
- cache invalidation
- deduplication of concurrent identical requests
- background refetching
- retry with backoff
- **request cancellation**
- pagination cache coherence
- optimistic updates and rollback

**That's thousands of lines of the same code, and libraries exist because everyone wrote it badly.** → **TanStack Query**, **SWR**, **RTK Query**, or your framework's loader.

```jsx
const { data, isPending, error } = useQuery({
  queryKey: ["user", id],
  queryFn: ({ signal }) => fetch(`/api/users/${id}`, { signal }).then(r => r.json()),
});
```

**The genuine payoff of the split: once server state moves out, the amount of real *client* state in a typical app is tiny** — often a theme and a couple of toggles. Apps that still put everything in Redux are usually describing a problem they no longer have.

## The states everyone forgets

**Not loading and error. Five:**

**Loading** — first fetch, nothing to show.
**Error** — and *which* error: 404 is "not found", 500 is "try again", offline is different again.
**Empty** — succeeded, no results. **A blank screen where a list should be reads as broken.** This is the most-skipped state.
**Stale** — showing cached data while revalidating. Usually correct, and worth indicating.
**Refetching** — background update in progress; don't blank the screen.

**Showing cached data instantly then updating quietly beats a spinner** in nearly every case — that's stale-while-revalidate, and it's why the libraries default to it.

## The race condition

**The bug that hand-rolled fetching always has:**

```jsx
useEffect(() => {
  fetch(`/api/search?q=${query}`).then(r => r.json()).then(setResults);
}, [query]);
```

Type "react" quickly. Requests fire for `r`, `re`, `rea`, `reac`, `react`. **They can return out of order** — `rea` lands last and wins. **You now display results for a query the user isn't looking at, and it's intermittent, so it survives testing.**

```jsx
useEffect(() => {
  const controller = new AbortController();
  fetch(url, { signal: controller.signal })
    .then(r => r.json()).then(setResults)
    .catch(e => { if (e.name !== "AbortError") setError(e); });
  return () => controller.abort();          // ← cancel on change/unmount
}, [query]);
```

**`AbortController` is the answer**, and query libraries do it for you via the query key. **Note the `catch` must ignore `AbortError`** or every cancellation shows the user an error.

## Waterfalls

```
Page loads → fetch user → then fetch user's org → then fetch org's projects
```

**Three sequential round trips.** On a 200 ms connection that's 600 ms of nothing.

**Fixes, best first:**
- **Fetch in parallel** where there's no real dependency — `Promise.all`
- **Hoist the fetch** to a route loader that starts before components render
- **Prefetch on intent** — on hover or on focus, before the click
- **Fetch on the server**, where the round trips are datacentre-local → [[frontend/02-rendering/02-hydration-and-the-server-boundary|RSC]]

**Component-level fetching creates waterfalls by construction**, because a child can't fetch until its parent has rendered. That's the structural argument for route loaders.

## Mutations and optimistic updates

```jsx
const mutation = useMutation({
  mutationFn: updateTodo,
  onMutate: async (next) => {
    await queryClient.cancelQueries({ queryKey: ["todos"] });
    const previous = queryClient.getQueryData(["todos"]);
    queryClient.setQueryData(["todos"], optimistic(next));   // update immediately
    return { previous };                                     // keep for rollback
  },
  onError: (_e, _v, ctx) => queryClient.setQueryData(["todos"], ctx.previous),
  onSettled: () => queryClient.invalidateQueries({ queryKey: ["todos"] }),
});
```

**Optimistic updates make an app feel instant** — and **the rollback is not optional.** An optimistic update without one shows the user a lie when the request fails.

**Invalidate on settle, not on success.** After an error you still want the truth from the server.

## Where state actually belongs

| Kind | Home |
|---|---|
| Is this dropdown open | `useState`, local |
| Form field values | A form library, or local |
| **Filters, page, tab, search** | **The URL** |
| Theme, locale, current user | Context |
| The user, the product list | **A query library** |
| Genuinely global client state | A small store (Zustand, Jotai) |

**The URL row is the one people skip.** Filters in `useState` mean the page can't be shared, bookmarked, or back-buttoned correctly. **If a user would expect to send someone the link and have them see the same thing, it belongs in the URL** — and it's free persistence.

## Pagination cache coherence

**The cache key contains every argument — including the page number.** TanStack's `queryKey`, SWR's key, RTK Query's serialised args: all the same idea.

So `["postcards", eventId, 1]` and `["postcards", eventId, 2]` are **two separate cache entries**. A component asks for one and renders it.

**Which is why the naive "Load more" replaces the list instead of extending it:**

```jsx
<button onClick={() => setPage(p => p + 1)}>Load more</button>
const items = data?.items ?? [];        // ← page 2's items, not pages 1–2
```

Nothing is broken. "Give me page 2" is simply not the same request as "give me everything through page 2". The library did exactly what it was asked.

**Two ways out, and the choice is about who else uses the query.**

**1. Query-level — the library's built-in.** TanStack's `useInfiniteQuery`, RTK Query's `serializeQueryArgs` + `merge`, SWR's `useSWRInfinite`. All page-fetches collapse into one cache entry that grows. This is the better answer **when the query has one kind of consumer**.

**The catch:** it changes behaviour for *every* caller. If some other component uses the same query without a page argument — a count, a picker, a preview — it now reads the accumulated list instead of one page. Query-level config is global config.

**2. Component-level accumulation.** Keep the pages separate in the cache, stitch them together in the component that wants a growing list. Affects one caller.

### Three things that go wrong when you accumulate by hand

**Store pages keyed by page number, don't push onto an array.**

```js
{ 1: [...], 2: [...] }      // not  [...page1, ...page2]
```

Pushing duplicates everything the first time anything refetches — and refetches are routine, because creating an item invalidates the list. Keying by number is idempotent: receiving page 2 again overwrites slot 2.

**Reset inside the state updater, not in a separate effect.** A filter change and an in-flight page can land in the same tick, and the page will join the old list before a separate `useEffect(() => reset(), [filter])` runs. Compare the key inside the setter so it's one atomic step.

**Feed it the raw array and filter afterwards.** A cached array keeps a stable reference between renders; `(data ?? []).filter(...)` is a new array every render, so as an effect dependency it never stops firing.

### `isLoading` is true on every page

**`isLoading` means "no data for *these exact arguments* yet". `isFetching` means "a request is in flight".**

Change the page, change the arguments — `isLoading` is true again. So this blanks the list on every "Load more":

```jsx
{isLoading ? <Skeleton /> : <List items={items} />}
```

```jsx
{isLoading && items.length === 0 ? <Skeleton /> : <List items={items} />}
```

**For anything paginated or filtered, `isLoading` alone is almost always the wrong gate** — it's the "first fetch" flag, and every new filter value is a first fetch. This is the same mistake as blanking the screen on a background refetch, in the section above.

### Invalidation only works if something is labelled

Cache libraries invalidate by key or tag. **A mutation that invalidates `["events"]` does nothing if no query ever registered under it.**

Seen in the wild: `createEvent` invalidated `"Events"`, the main list provided `"Events"`, but "My Created Events" provided nothing at all. Creating an event refreshed one list and not the other, with no error anywhere — the second cache entry was still perfectly valid as far as the library knew.

**Worth auditing once per feature:** every query that renders a collection needs a tag or key that some mutation invalidates. One without is a list that can never refresh.

## Related
- [[frontend/04-state-and-data/01-state-management|state management]] — the client half
- [[frontend/02-rendering/02-hydration-and-the-server-boundary|the server boundary]]
- [[backend/06-cross-cutting/05-idempotency-and-retries|idempotency and retries]] — the other end of the same problem
- [[frontend/interview/03-state-data-and-architecture|the interview round]]
- [[projects/nextvibe/learning/frontend/12-rtk-query-and-api-slices|nextvibe — RTK Query & API slices]] — all of the above hit in one codebase

*Source: [reference] — written Aug 2026.*
