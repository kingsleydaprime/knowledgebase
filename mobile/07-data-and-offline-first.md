# Data and Offline-First

**[Advanced]** — the architecture that makes an app usable on a train, and the sync problems it creates.

## The kid version first

**Online-first:** tap → spinner → wait for the server → show it. No network, no app.

**Offline-first:** the app reads from a database **on the phone**. It's always instant, always works. The network's job is to quietly keep that database fresh in the background.

**The user never waits for the network to see something they already have.**

## The single most important decision

> **The local database is the source of truth. The UI never reads from the network.**

```
UI ──observes──► Local DB ──────────────► always instant, always available
                    ▲
                    │ writes
              Sync layer ◄──── Network
```

The UI subscribes to a query. Sync updates the database. **The UI updates automatically** — it has no idea a network exists.

**Make this decision on day one.** Retrofitting it means rewriting every screen, and that's the most common expensive rewrite in mobile.

## The tools

| Platform | Database | Key-value |
|---|---|---|
| **Android** | **Room** (SQLite + compile-time checked queries) | DataStore |
| **iOS** | **SwiftData** (modern), Core Data (mature), GRDB (SQLite) | UserDefaults |
| **Cross-platform** | SQLDelight, Realm, WatermelonDB, Drift | — |
| **Sync-as-a-service** | PowerSync, ElectricSQL, Replicache, Firebase | — |

**SQLite underlies most of these**, and it's excellent — everything in [[databases/README|the databases course]] about indexes and query plans applies → [[databases/04-b-trees-and-indexes|indexes]].

**A note on the sync services:** offline sync is genuinely hard, and using a service that solves it is a legitimate engineering decision rather than a shortcut. Weigh it against the lock-in.

## Optimistic updates

The user taps "like". Do **not** wait for the server.

```
1. Write to the local DB immediately, marked pending
2. UI updates instantly — it's observing the DB
3. Queue the mutation
4. On success → clear pending
5. On failure → revert, and TELL THE USER
```

**Step 5 is where apps are dishonest.** Silently reverting is confusing; silently keeping a failed change is a lie. **Show a clear, non-blocking indication that something didn't save**, with a retry.

## The outbox

Queue mutations in a table, not in memory — **memory doesn't survive process death**:

```sql
CREATE TABLE outbox (
  id, operation, payload, created_at, attempts, last_error
);
```

Then:
- **Process in order** — a "create" must precede its "update"
- **Retry with exponential backoff and jitter**
- **Make it idempotent** — send a client-generated ID so a retry after a timeout doesn't create two records → [[backend/06-cross-cutting/README|idempotency]]
- **Give up eventually** and surface it. An item retrying forever is invisible data loss
- **Handle a dead item** — if a mutation can never succeed (deleted server-side), it must be removable

## Conflict resolution — the genuinely hard part

Two devices edit the same thing offline. Both come back. Now what?

| Strategy | Good for | Cost |
|---|---|---|
| **Last-write-wins** | Simple fields, low stakes | **Silent data loss** |
| **Server wins** | Server-authoritative data | Loses the user's offline work |
| **Client wins** | Personal, single-user data | Loses others' changes |
| **Field-level merge** | Structured records | Complex; can produce nonsense combinations |
| **CRDTs** | Collaborative text, sets, counters | **Converges automatically**, larger payloads → [[architecture/04-distributed-systems/06-crdts-and-conflict-resolution\|CRDTs]] |
| **Ask the user** | High-stakes, rare | Annoying if common |

**There is no universally correct answer** — it depends on what the data means. A counter can be merged; a paragraph of text cannot be merged safely by timestamp.

**Be honest about last-write-wins.** It's the default, it's usually fine, and **it silently destroys someone's work occasionally.** Choose it deliberately, and don't use it for anything a user spent effort on.

## Caching and freshness

```
Cache-first        show local, no fetch          static reference data
Stale-while-revalidate  show local, fetch, update  ← THE DEFAULT
Network-first      fetch, fall back to cache      prices, balances
```

**Stale-while-revalidate is right for most screens.** Instant render, quiet refresh.

**Tell the user what they're looking at.** A subtle "last updated 2 hours ago" or an offline indicator is the difference between trusted stale data and a confusing bug report.

## Sync mechanics

- **Delta sync, not full sync.** Send `?since=<cursor>` and get changes. Full sync on every launch burns battery and data
- **Server-driven cursors** beat client timestamps — **device clocks are wrong**, sometimes by hours
- **Paginate.** A user with 50,000 records shouldn't OOM on first sync
- **Sync on the right triggers:** app foreground, pull-to-refresh, connectivity regained, and a periodic background job → [[mobile/10-background-work-and-push|background work]]
- **Handle deletions** — soft-delete with tombstones, or the record lives forever on the client
- **Migrate schemas carefully.** Users skip versions; migrations must chain, and **a failed migration on launch is a crash loop that bricks the app** for that user

## Key insight

**Offline-first isn't a feature you add for people with bad signal — it's an architecture that makes the app instant for everyone**, because reading from local disk always beats a network round trip. The cost is that you've built a distributed system with a replica in every user's pocket, and **conflict resolution is the bill for that.**

## Related
- [[mobile/05-state-and-architecture|state and architecture]] — the repository this sits under
- [[mobile/08-networking-on-mobile|networking on mobile]]
- [[databases/README|databases]] — SQLite is a real database, treat it as one
- [[architecture/04-distributed-systems/README|distributed systems]] — because that's what you've built

*Source: [reference] — Aug 2026.*
