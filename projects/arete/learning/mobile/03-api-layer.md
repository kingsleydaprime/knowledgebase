# Arete Mobile — The API Layer

Split out from the original single-file `mobile-learning.md`. Covers the axios instance, the
refresh-token queue, and typed endpoint modules.

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

