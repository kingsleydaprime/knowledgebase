# NextVibe Frontend — State Management: Redux Toolkit & RTK Query

Split out from the original flat `frontend-learning.md` (moved to `learning/archive/`).
See also `learning/frontend/01-routing.md` (Server vs Client Components — the context this state
layer lives inside), `learning/frontend/03-auth.md` (the `baseQueryWithReauth` token-refresh queue),
`learning/frontend/06-realtime.md` (how Socket.IO events feed back into the RTK Query cache),
`learning/frontend/08-performance-debugging.md`, and the other `learning/frontend/*.md` files.

This file covers: Redux Toolkit slices for local UI state, RTK Query for server-state fetching
and caching (queries, mutations, lazy queries, the shared `baseQueryWithReauth`), and the general
scaling patterns used across the RTK Query API layer — splitting APIs by domain, centralising
error handling, environment variable rules, avoiding prop drilling, debouncing, and the
Socket.IO reconnection/re-join rule that also applies at the state layer.

---

## 9. State Management — Redux Toolkit

Redux Toolkit (RTK) is the official, modern way to use Redux. This project has two categories of Redux state:

### Slices — local UI state

Slices hold state that doesn't come from the API: who is logged in, the current event form values, canvas state, UI flags.

```ts
// src/app/provider/slices/user.ts
const authSlice = createSlice({
  name: "auth",
  initialState: { user: null, isAuthenticated: false },
  reducers: {
    setUser(state, action: PayloadAction<IUser | null>) {
      state.user = action.payload;  // Immer allows direct mutation
    },
    logout(state) {
      state.user = null;
      state.isAuthenticated = false;
    },
  },
});
```

**Slices in this project:**

| Slice | Purpose |
|---|---|
| `user` | Auth state: who is logged in, their role |
| `eventForm` | Multi-step event creation form values |
| `location` | User's selected location |
| `canvas` | Fabric.js canvas state for postcard editor |
| `ui` | UI flags like `hideHeader` |

### Using slice state in a component

```tsx
"use client";
import { useSelector, useDispatch } from "react-redux";
import { RootState } from "@/app/provider/store";
import { logout } from "@/app/provider/slices/user";

function ProfileButton() {
  const user = useSelector((state: RootState) => state.user.user);
  const dispatch = useDispatch();

  return (
    <div>
      <p>{user?.username}</p>
      <button onClick={() => dispatch(logout())}>Log out</button>
    </div>
  );
}
```

### The store — wiring everything together

```ts
// src/app/provider/store.ts
export const store = configureStore({
  reducer: {
    user: authReducer,
    eventForm: eventFormReducer,
    [authApi.reducerPath]: authApi.reducer,  // RTK Query APIs also go in the reducer
    // ... all other APIs
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(
      authApi.middleware,
      // ... all other API middlewares (required for caching, invalidation)
    ),
});
```

The store is provided to the app through `<Provider store={store}>` inside `ProviderWrapper`, which wraps the entire app in the root layout.

---

## 10. Data Fetching — RTK Query

RTK Query is a data fetching and caching layer built into Redux Toolkit. It replaces `useEffect + fetch + useState` for API calls.

### Defining an API

```ts
// src/app/provider/api/eventApi.ts
export const eventsApi = createApi({
  reducerPath: "eventsApi",       // key in the Redux store
  baseQuery: baseQueryWithReauth, // all requests go through this
  tagTypes: ["Events"],           // for cache invalidation
  endpoints: (builder) => ({

    // Query = GET — reads data, caches it
    getEvents: builder.query<EventsResponse, void>({
      query: () => "/v1/events",
      providesTags: ["Events"],
    }),

    // Mutation = POST/PUT/DELETE — writes data, can invalidate cache
    createEvent: builder.mutation<Event, CreateEventBody>({
      query: (body) => ({ url: "/v1/events", method: "POST", body }),
      invalidatesTags: ["Events"],  // clears the events cache after creating one
    }),
  }),
});

export const { useGetEventsQuery, useCreateEventMutation } = eventsApi;
```

### Using queries in components

```tsx
function EventList() {
  const { data, isLoading, isError, refetch } = useGetEventsQuery();

  if (isLoading) return <Spinner />;
  if (isError) return <ErrorMessage onRetry={refetch} />;

  return <ul>{data?.data.map(e => <EventCard key={e.id} event={e} />)}</ul>;
}
```

RTK Query automatically:
- Deduplicates identical requests (if 3 components call `useGetEventsQuery()`, only 1 HTTP request goes out)
- Caches results
- Refetches when the cache is invalidated
- Manages loading/error state

### Using mutations

```tsx
function CreateEventButton() {
  const [createEvent, { isLoading }] = useCreateEventMutation();

  const handleCreate = async () => {
    try {
      const newEvent = await createEvent({ name: "My Event" }).unwrap();
      toast.success("Created!");
    } catch (err: any) {
      toast.error(err?.data?.message ?? "Something went wrong");
    }
  };

  return <button onClick={handleCreate} disabled={isLoading}>Create</button>;
}
```

`.unwrap()` throws on error instead of returning it — lets you use `try/catch`. (See `learning/frontend/05-uploads-errors.md` for the universal `errorHandler()` function most `catch` blocks in this project actually call.)

### Lazy queries — fetch on demand

```tsx
const [verifyPayment, { isLoading }] = useLazyVerifyOrganizerPaymentQuery();

// Called imperatively, not on mount
const result = await verifyPayment(paymentId).unwrap();
```

Used in the payment verify page to poll manually instead of fetching on mount. (See `learning/frontend/07-payments-games.md` Part 13 for the full payment polling flow this lazy query is part of.)

### The `baseQueryWithReauth`

Every RTK Query API in this project uses a shared `baseQueryWithReauth` instead of a plain `fetchBaseQuery`. It adds:

1. **Token attachment** — reads `accessToken` from the cookie and adds `Authorization: Bearer <token>` to every request
2. **Token refresh** — on a 401, automatically calls `/v1/auth/refresh`, stores the new token, and retries the original request
3. **Queue pattern** — if multiple requests 401 at the same time, only one refresh happens; the rest wait

```
Request → prepareHeaders (attach token) → API → 401?
                                                  ↓
                                         isRefreshing?
                                           Yes → queue the request, wait
                                           No  → call /refresh, update cookie,
                                                 flush queue, retry all
```

(See `learning/frontend/03-auth.md` for the full mechanics of this refresh queue, plus the `PUBLIC_PATHS` allowlist that prevents it from redirecting anonymous users to login on public pages.)

---

## 19. Scaling Patterns

### Split RTK Query APIs by domain

Each API file in this project covers one domain (`eventApi.ts`, `paymentApi.ts`, `messagingApi.ts`). This keeps files manageable and allows independent cache invalidation. Never put everything in one giant `api.ts`.

### Centralise error handling

All API errors flow through `baseQueryWithReauth`. Add global error handling there instead of duplicating `try/catch` everywhere:

```ts
// In baseQueryWithReauth — handle 403 globally
if (result.error?.status === 403) {
  toast.error("You don't have permission to do that.");
}
```

### Environment variables

Next.js has two types:

| Variable | Accessible |
|---|---|
| `NEXT_PUBLIC_*` | Browser + server. Baked into the client bundle at build time. |
| Everything else | Server only. Never exposed to the browser. |

```ts
// Safe to use in browser code
const apiUrl = process.env.NEXT_PUBLIC_API_URL;

// Server-only (API routes, Server Components)
const secretKey = process.env.ERCASPAY_SECRET_KEY;
```

Never put secrets in `NEXT_PUBLIC_` variables — they'll appear in the compiled JavaScript. (See `learning/09-devops.md` Part 38 for the equivalent backend-side environment variable dev/prod split rule.)

### Avoid prop drilling with context or Redux

When state needs to travel more than 2-3 levels, put it in Redux or a React Context instead of threading it through props:

```tsx
// Instead of: <A eventId={eventId}><B eventId={eventId}><C eventId={eventId} /></B></A>
// Use: useSelector or useContext inside C directly
```

### Debounce user inputs

Heavy operations (search, map panning, canvas manipulation) should be debounced:

```tsx
import { useDebouncedCallback } from "use-debounce";

const handleSearch = useDebouncedCallback((value: string) => {
  setQuery(value);
}, 300);  // wait 300ms after user stops typing
```

This project includes `use-debounce` — use it anywhere you're calling APIs or doing expensive work on keystrokes.

### Socket.IO reconnection

When a user's network drops and reconnects, Socket.IO auto-reconnects the socket. But **room membership is not preserved** — you must re-join. Always put your `socket.emit("join:*", ...)` inside the effect that depends on `isConnected`, so it fires again after every reconnection. (See `learning/frontend/06-realtime.md` for the full, corrected event-driven version of this pattern — the naive `isConnected`-dependent effect described here has a real race condition that Part 36 there walks through and fixes.)

---

## Quick Reference

### Most-used RTK Query patterns

```ts
// Query (read)
const { data, isLoading, isError, refetch } = useGetSomethingQuery(arg);

// Lazy query (on demand)
const [trigger, { data, isLoading }] = useLazyGetSomethingQuery();
await trigger(arg).unwrap();

// Mutation (write)
const [mutate, { isLoading }] = useSomeMutation();
await mutate(body).unwrap();
```

### Most-used Redux patterns

```ts
const value = useSelector((state: RootState) => state.sliceName.field);
const dispatch = useDispatch();
dispatch(someAction(payload));
```
