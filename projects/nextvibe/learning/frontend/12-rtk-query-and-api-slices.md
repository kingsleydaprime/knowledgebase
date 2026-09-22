# 12 — RTK Query, Cache Tags, and Splitting a Big API File

*Written 2026-09-21, from splitting nextvibe's 1,039-line eventApi.*

Plain-English version. The concepts here tripped me up, so this explains them
from scratch rather than assuming the vocabulary.

See also: [[projects/nextvibe/learning/frontend/02-state-management|02 — State Management]],
[[projects/nextvibe/learning/frontend/10-typed-api-contracts|10 — Typed API Contracts]]

---

## 1. What an "API slice" actually is

I used to read `eventApi.ts` as "the file with my fetch calls in it". That is
wrong, and the wrong picture is what makes everything else confusing.

An RTK Query API slice is **three things bundled together**:

1. **A place to store downloaded data** (a cache)
2. **A set of React hooks** you call in components
3. **A reducer** — a real part of the Redux store

That third one is the surprise. Look at `store/store.ts`:

```ts
reducer: {
  user: authReducer,                                   // normal state
  ui:   uiReducer,                                     // normal state
  [eventsApi.reducerPath]: eventsApi.reducer,          // ← the API slice
}
```

`eventsApi.reducer` sits in the same list as `uiReducer`. It is not a helper
that lives next to the store. **It is part of the store.**

That is why the folder is `store/api/` and not `services/`. If these were plain
`fetch` functions with no Redux involved, `services/` would be right. It is
RTK Query specifically that makes them state.

---

## 2. Why caching needs "tags"

Say a component calls:

```ts
const { data } = useGetEventDetailsQuery(eventId);
```

RTK Query fetches the event once, stores the result, and hands the same stored
copy to every other component that asks. Good — one network request instead of
ten.

Now you create a game for that event. The event's data has changed on the
server. But RTK Query does not know that. It still has the old copy and will
keep handing it out.

**Tags are how you tell it what to throw away.**

Think of a sticky label on each cached response:

```ts
getEventDetails: builder.query({
  query: (eventId) => `/v1/events/${eventId}`,
  providesTags: (result, error, eventId) => [{ type: "Event", id: eventId }],
})
```

That says: *"the thing I just cached is labelled Event #42."*

Then the mutation says which labels to bin:

```ts
createGame: builder.mutation({
  query: ({ eventId, body }) => ({ url: `/v1/events/${eventId}/game-sessions`, method: "POST", body }),
  invalidatesTags: (result, error, { eventId }) => [
    "Games",
    { type: "Event", id: eventId },
  ],
})
```

*"I changed things. Bin anything labelled Games, and anything labelled
Event #42."* RTK Query throws those cached entries away, and any component
currently showing them refetches automatically.

Two words to know, because the docs use them constantly:

- **`providesTags`** — "here is the label for what I fetched"
- **`invalidatesTags`** — "bin everything with these labels"

And **"invalidate"** just means "mark as out of date so it gets fetched again".
It does not mean delete-and-leave-empty.

---

## 3. The part that nearly bit me: tags only work inside one slice

Here is the thing no tutorial mentions, and it is the whole reason this
refactor was done a particular way.

**A tag is only understood by the slice it was created in.**

`eventApi` declares which labels exist:

```ts
export const baseApi = createApi({
  tagTypes: ["Events", "Event", "Gallery", "Messages", "Games", "PublishPreview", "Withdrawals"],
  …
})
```

If I had made a *separate* `createApi` for games, and its `createGame` said
`invalidatesTags: [{ type: "Event", id: eventId }]`, then:

- gameApi bins its own `Event #42` entry — which does not exist, it never
  fetched one
- eventApi's real `Event #42` entry is **untouched**

Two slices, two separate noticeboards. Same word on a label, different
noticeboard. Nothing crosses.

**And nothing errors.** No warning, no red console text. It just quietly
stops refreshing.

In this codebase that would have been five broken refreshes:

```
createGame            → invalidates "Event", "PublishPreview"
updateGameSession     → invalidates "Event", "Event:game-status-<id>"
getActiveGameStatus   → provides   "Event"
```

Real symptom: an organizer creates a game, and the event page keeps showing the
old price on the publish-preview panel. No error. Weeks later someone reports
"the price is sometimes wrong" and nobody links it to a folder reorganisation.

> **The rule:** two endpoints that need to invalidate each other's cache must
> live in the same `createApi` instance. This is a *correctness* constraint, not
> a style preference.

---

## 4. `injectEndpoints` — file split without slice split

So: I wanted `eventApi.ts` (1,039 lines, five different subjects) split into
smaller files, but I could **not** split it into separate slices.

`injectEndpoints` does exactly this. One slice, many files.

**Step 1** — a base file holding the configuration and no endpoints:

```ts
// store/api/baseApi.ts
export const baseApi = createApi({
  reducerPath: "eventsApi",
  baseQuery: baseQueryWithReauth,
  tagTypes: ["Events", "Event", "Gallery", "Messages", "Games", "PublishPreview", "Withdrawals"],
  keepUnusedDataFor: 300,
  endpoints: () => ({}),          // deliberately empty
});
```

**Step 2** — each subject adds its endpoints to that same slice:

```ts
// store/api/endpoints/games.ts
import { baseApi } from "../baseApi";

export const gameEndpoints = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    createGame: builder.mutation({ … }),
    joinGameSession: builder.mutation({ … }),
    // 24 more
  }),
});

export const { useCreateGameMutation, useJoinGameSessionMutation, … } = gameEndpoints;
```

Result: three files, but **one** reducer, **one** cache, **one** set of labels.
`createGame` in `games.ts` can still bin `Event #42` cached by `eventApi.ts`,
because they are the same slice underneath.

Things worth knowing about it:

- **All `tagTypes` must be declared on the base.** `injectEndpoints` cannot add
  new label names. Forget one and you get a runtime warning.
- **Keep `reducerPath` the same** as the old slice had. It is the key the data
  sits under in the store, so leaving it alone means `store.ts` does not change.
- **Injection happens when the file is first imported.** A component importing
  `useCreateGameMutation` causes `games.ts` to load, which injects. This is the
  same mechanism used for lazy-loading API code in big apps.
- **Do not define the same endpoint name twice** across files. RTK warns in dev
  and keeps the first.

---

## 5. How I actually did the move

Not interesting theory, but the bits that saved time.

**Step A — convert in place, change nothing else.** First commit just moved the
`createApi` config into `baseApi.ts` and made `eventApi.ts` say
`baseApi.injectEndpoints({ …the same 78 endpoints… })`. Same exports, same
hooks, zero behaviour change, `tsc` clean. Nothing could break, and now files
could be carved off one at a time.

Doing the enabling step as its own commit is the trick. If something *had*
broken, I would know it was the conversion and not one of the moves.

**Step B — carve off one subject at a time.** Games first, then postcards. Each
is its own commit, so a problem is easy to bisect.

**Find the ranges with text markers, not line numbers.** The endpoints were not
in one block — games came in three clusters with event endpoints in between. I
first wrote down line numbers, then deleted a dead endpoint, and every number
below it shifted by 14. Section dividers already in the file survive edits:

```python
end = find(lambda l: l.strip().startswith('// ── Event Tags'))
```

**Watch out for doc comments.** A `/** … */` block sits *above* the endpoint it
describes. Slice a range by "the line the next endpoint starts on" and you drag
the next endpoint's comment along with you. Walk backwards from the endpoint
line over comment lines to find the real start.

**Assert before writing.** Every extraction script checked its own work before
touching a file:

```python
assert len(moved) == 26, f'expected 26 endpoints, got {len(moved)}'
for name in moved:
    assert not re.search(rf'^    {name}: builder\.', rest, re.M), f'{name} still in eventApi'
```

A bad regex then fails loudly instead of silently writing half a file.

**Let the compiler find the callers.** After moving 26 endpoints, `tsc` reported
26 errors naming every file that imported a hook from the old place. I did not
have to grep for them — I fixed exactly the list it printed.

**This only worked because `ignoreBuildErrors` was off.** Earlier the same day
`next.config.ts` had `typescript: { ignoreBuildErrors: true }`. With that on,
this refactor would have built green and shipped six files importing hooks that
no longer existed — a blank game tab in production and nothing in the logs.

---

## 6. One more trap: inheriting the shared client's defaults

Separate from the split, but the same lesson about moving code into shared
infrastructure.

A wizard was calling the AI endpoint with raw `fetch`:

```ts
const accessToken = Cookies.get("accessToken");   // read once, at render
…
fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/games/ai/generate-draft`, {
  headers: { Authorization: `Bearer ${accessToken}` },
})
```

Two bugs. There is no token refresh, so an expired token just fails. And the
token is captured when the component renders, so even if something else
refreshed it, this component keeps sending the stale one. On the slowest call in
the app.

Moving it into an RTK Query mutation fixes both, because `baseQuery` reads the
cookie per request and has a refresh queue.

**But `baseQuery` also sets `timeout: 15000`, and the raw fetch had no timeout
at all.** Moving the call over unchanged would have swapped a token bug for a
"generation dies after 15 seconds" bug — on an endpoint that waits for an LLM.
`fetchBaseQuery` accepts a per-request override:

```ts
generateGameDraft: builder.mutation({
  query: (body) => ({ url: "/v1/games/ai/generate-draft", method: "POST", body, timeout: 60000 }),
})
```

And errors change shape. `.unwrap()` rejects with `{ status, data }`, not an
`Error`. So `err.message` is `undefined` and every failure shows the generic
fallback, hiding the server's real message:

```ts
toast.error(err?.data?.message ?? err?.message ?? "AI generation failed.");
```

> **General lesson:** when you move a call from a bespoke client into a shared
> one, you inherit the shared one's defaults — timeouts, headers, retries, error
> shape. Check each. The bespoke version had no defaults, so every default is a
> change.

---

## 7. Short version

- An API slice is a **reducer**, not a fetch helper. That is why it lives in `store/`.
- **Tags** are labels on cached data. `providesTags` labels it, `invalidatesTags` bins it.
- **Tags only work inside one `createApi`.** Splitting a slice silently breaks cross-subject refreshes.
- **`injectEndpoints`** splits the files while keeping one slice, one cache, one set of tags.
- Do the **conversion** as its own no-op commit, then carve off one subject per commit.
- **Text markers beat line numbers** for finding ranges; line numbers go stale mid-edit.
- Let **`tsc`** find the callers — which requires not ignoring build errors.
