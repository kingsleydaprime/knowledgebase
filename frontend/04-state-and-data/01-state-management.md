# State Management — Local, Global, Server State

"State" is just data that changes over time and affects what's rendered. The actual design question in frontend work isn't "how do I manage state" in the abstract — it's "where should *this specific piece* of state live," and the three categories below need genuinely different tools because they behave differently.

## Local state — owned by a single component

Data that only one component (and maybe its direct children) cares about — whether a dropdown is open, the current value of a text input before it's submitted.

```javascript
function SearchBox() {
  const [query, setQuery] = useState("");   // React — lives and dies with this component
  return <input value={query} onChange={(e) => setQuery(e.target.value)} />;
}
```

The default choice, and the right one far more often than it initially seems — reaching for global state before confirming a piece of data genuinely needs to be shared across distant components is a common, avoidable source of unnecessary complexity.

## Global (client) state — shared across many components

Data that many, often distant, parts of the app need — the current logged-in user, a shopping cart, a UI theme setting. Passing this down through props at every intermediate level ("prop drilling") gets unwieldy fast as an app grows, which is exactly the problem dedicated global state tools solve.

```javascript
// Redux/Zustand-style shape, conceptually
const useCartStore = create((set) => ({
  items: [],
  addItem: (item) => set((state) => ({ items: [...state.items, item] })),
}));

// any component, anywhere in the tree, can read/update this directly:
const { items, addItem } = useCartStore();
```

React's Context API solves the prop-drilling problem for simpler cases; dedicated libraries (Redux, Zustand, and similar) add more structure, tooling, and performance optimization for larger apps with frequent, complex state updates across many components.

## Server state — data that lives somewhere else entirely

Data fetched from an API — a list of posts, a user's profile, search results. This is a genuinely different category from local/global client state, because it comes with problems client state doesn't have: it can be stale (the server's copy may have changed since you fetched it), it needs loading/error states, and it often benefits from caching so the same data isn't re-fetched unnecessarily on every render.

```javascript
// React Query / TanStack Query — purpose-built for exactly this category
const { data, isLoading, error } = useQuery({
  queryKey: ["posts", postId],
  queryFn: () => fetchPost(postId),
});
```

Treating server state as if it were just more global client state (dumping fetched data into Redux and manually managing loading flags, cache invalidation, and refetching by hand) is exactly the pattern that dedicated server-state libraries (React Query, SWR) exist to eliminate — they provide caching, background refetching, and stale-data handling out of the box, purpose-built for data that lives outside the client entirely.

## Why conflating these three categories causes real problems

Treating server state as global client state means manually reinventing caching/staleness logic that a purpose-built tool already solves well. Treating local state as global state means every unrelated component re-renders when state that only mattered to one small part of the UI changes, hurting performance for no benefit. The practical skill in this area is mostly about **correctly categorizing** a given piece of state, more than mastering any single tool — most real-world "state management is a mess" complaints trace back to this categorization never having been done deliberately.

## URL state — a fourth category worth naming separately

Some state genuinely belongs in the URL, not in a JS state store at all — the current page number, active filters, a search query — specifically because it should be shareable (someone can send a link and land on the same filtered view), bookmarkable, and preserved correctly on browser back/forward navigation, none of which a JS-only state store provides for free.

```
/products?category=shoes&sort=price&page=2
```

## Gotchas

- Reaching for a global state library before confirming the data actually needs to be shared broadly is a common form of premature complexity — start local, lift state up only when a genuine sharing need appears.
- Storing server data in global client state without a caching strategy leads to duplicated, potentially inconsistent copies of the same data across the app, along with manually-written (and easily buggy) refetch/invalidation logic that a dedicated server-state library already solves.
- Forgetting that server state can go stale — displaying data fetched minutes ago as if it's still current, without a refetch/invalidation strategy, is a common source of confusing "why does this look wrong" bugs.

## Related
- [[frontend/02-rendering/01-rendering-strategies|rendering strategies]]
- [[frontend/07-practices/01-frontend-best-practices|frontend-best-practices]]
