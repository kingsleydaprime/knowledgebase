# Background Work and Push

**[Advanced]** — what you can do when you're not on screen, which is much less than you think.

## The kid version first

Your app is not on screen. **You are essentially not running.**

You don't get to poll a server every minute. You don't get to keep a socket open. The OS batches, delays and refuses your background work to protect the battery — and if you fight it, it restricts you harder.

**The two things that do work:** ask the OS to run a job *eventually* under conditions you specify, or have your **server** wake you with a push notification.

## The mental model

> **You cannot decide when to run. You can only describe work and let the OS schedule it.**

**"Every 15 minutes" means "not more often than every 15 minutes, and probably much less."** Both platforms learn usage patterns and deprioritise apps the user rarely opens.

## The APIs

**Android — WorkManager for essentially everything deferrable:**

```kotlin
val work = PeriodicWorkRequestBuilder<SyncWorker>(6, TimeUnit.HOURS)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.UNMETERED)   // Wi-Fi only
            .setRequiresCharging(true)
            .build()
    ).build()
```

It survives reboots, handles retries and backoff, and respects Doze. **Minimum period is 15 minutes** — and treat that as a floor, not a schedule.

For work the user is actively waiting on and can see (a download, a workout), use a **foreground service** with a visible notification. **Android 14+ requires you to declare a specific service type**, and mismatching it is a rejection.

**iOS — narrower and stricter:**
- `BGAppRefreshTask` — short, opportunistic refresh
- `BGProcessingTask` — longer, typically overnight while charging
- Background URLSession — downloads continue after your app is suspended
- Silent push — asks the system to wake you. **It may be throttled or dropped entirely**, and is unreliable if the user force-quit the app

**iOS gives you less. Design for it, and treat any successful background run as a bonus rather than a guarantee.**

## The Android fragmentation tax

This is the one that costs real days. **Manufacturer battery managers kill background work in ways that violate documented Android behaviour** — Xiaomi, Huawei, Oppo, Vivo, OnePlus and Samsung have all shipped versions of this.

[dontkillmyapp.com](https://dontkillmyapp.com) catalogues it per manufacturer.

**What to do:**
- **Never rely on background work for correctness.** Sync opportunistically, and always sync on foreground
- **Detect it** — if a periodic job hasn't run in far too long, you know
- For genuinely critical cases, **guide the user to whitelist your app** — but only if the feature justifies asking

## Push notifications

**The reliable way to have something happen while your app is closed** — because it originates from your server.

```
your server → FCM (Android) / APNs (iOS) → device → your app
```

**Firebase Cloud Messaging handles both platforms**, and is the standard path.

**Two kinds, and the distinction matters:**
- **Notification/alert push** — the OS displays it. Works even if your app is asleep. **Delivery is best-effort, never guaranteed**
- **Data/silent push** — wakes your app to do something. **Heavily throttled on iOS**, and dropped if the user force-quit

**Never assume delivery.** Push is a *hint* to sync, not a transport for data. **The payload should say "something changed" and your app should then fetch the truth** — which also avoids putting sensitive data in a notification.

## Notifications as a UX problem

**Permission is required on both platforms now, and users are ruthless.** Notifications are the fastest route to an uninstall.

- **Don't ask on first launch.** Ask when there's a specific thing worth being told about
- **Send fewer.** Every notification should be worth interrupting someone
- **Use Android's notification channels** properly — users can disable *categories* rather than everything, which saves the ones that matter
- **Deep link correctly**, from a cold start → [[mobile/06-navigation|navigation]]
- **Group and summarise.** Twelve separate notifications is a bad experience
- **Respect quiet hours and time zones.** A 3am marketing push is an uninstall
- **Nothing sensitive in the preview** — lock screens are visible to whoever's nearby

## What genuinely can't be done

Say this out loud when someone asks:

- ❌ Run continuously in the background
- ❌ Poll a server every minute
- ❌ Guarantee a task runs at an exact time
- ❌ Guarantee push delivery
- ❌ Restart yourself after being force-quit (iOS)
- ❌ Track location continuously without a persistent, visible indicator

**These are policy, not gaps.** Frameworks and hacks claiming otherwise are fragile, drain battery, and get apps rejected.

## Key insight

**Both platforms decided the battery matters more than your app's convenience, and they enforce it.** So the correct architecture is opportunistic: sync when foregrounded, sync when the OS offers you a window, let push *hint* that something changed — and **never let correctness depend on background execution**, because on a meaningful share of Android devices it simply will not happen.

## Related
- [[mobile/07-data-and-offline-first|offline-first]] — what the sync job actually does
- [[mobile/11-performance-and-battery|performance and battery]] — why the OS is like this
- [[mobile/06-navigation|navigation]] — handling a notification tap from cold
- [[foundations/os/03-scheduling|scheduling]] — the OS side

*Source: [reference] — Aug 2026.*
