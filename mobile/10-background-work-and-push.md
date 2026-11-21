---
id: 4d933963-5364-47df-8a76-b5fc92026d2d
---

# Background Work and Push

Background work is anything an app does while it is not on screen, and a push notification is a message a server sends to wake the phone and show an alert. The phone limits background work heavily to save battery. This lesson shows how apps still sync data and send alerts, like a bank app telling you money just came in.

## The kid version first
<!-- bite: f7003dd0-488e-4643-b5bd-18b42eba50f9 -->

Your app is not on screen. **You are essentially not running.**

You don't get to poll a server every minute. You don't get to keep a socket open. The OS batches, delays and refuses your background work to protect the battery — and if you fight it, it restricts you harder.

**The two things that do work:** ask the OS to run a job *eventually* under conditions you specify, or have your **server** wake you with a push notification.

## The mental model
<!-- bite: a5eb186c-241b-4129-b6b9-47b87e17ad3e -->

> **You cannot decide when to run. You can only describe work and let the OS schedule it.**

**"Every 15 minutes" means "not more often than every 15 minutes, and probably much less."** Both platforms learn usage patterns and deprioritise apps the user rarely opens.

## The APIs
<!-- bite: 91e688ce-987b-45cc-90d6-74875a05c624 -->

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
<!-- bite: a92cd51c-d15c-48b9-82c6-2ee90a222769 -->

This is the one that costs real days. **Manufacturer battery managers kill background work in ways that violate documented Android behaviour** — Xiaomi, Huawei, Oppo, Vivo, OnePlus and Samsung have all shipped versions of this.

[dontkillmyapp.com](https://dontkillmyapp.com) catalogues it per manufacturer.

**What to do:**
- **Never rely on background work for correctness.** Sync opportunistically, and always sync on foreground
- **Detect it** — if a periodic job hasn't run in far too long, you know
- For genuinely critical cases, **guide the user to whitelist your app** — but only if the feature justifies asking

## Push notifications
<!-- bite: ffef3ebc-1be3-43e8-85d3-9878c8d2db93 -->

**The reliable way to have something happen while your app is closed** — because it originates from your server.

```text
your server → FCM (Android) / APNs (iOS) → device → your app
```

**Firebase Cloud Messaging handles both platforms**, and is the standard path.

**Two kinds, and the distinction matters:**
- **Notification/alert push** — the OS displays it. Works even if your app is asleep. **Delivery is best-effort, never guaranteed**
- **Data/silent push** — wakes your app to do something. **Heavily throttled on iOS**, and dropped if the user force-quit

**Never assume delivery.** Push is a *hint* to sync, not a transport for data. **The payload should say "something changed" and your app should then fetch the truth** — which also avoids putting sensitive data in a notification.

## Notifications as a UX problem
<!-- bite: b2133a48-b04d-4886-b51c-394cd75731a0 -->

**Permission is required on both platforms now, and users are ruthless.** Notifications are the fastest route to an uninstall.

- **Don't ask on first launch.** Ask when there's a specific thing worth being told about
- **Send fewer.** Every notification should be worth interrupting someone
- **Use Android's notification channels** properly — users can disable *categories* rather than everything, which saves the ones that matter
- **Deep link correctly**, from a cold start → [[mobile/06-navigation|navigation]]
- **Group and summarise.** Twelve separate notifications is a bad experience
- **Respect quiet hours and time zones.** A 3am marketing push is an uninstall
- **Nothing sensitive in the preview** — lock screens are visible to whoever's nearby

## What genuinely can't be done
<!-- bite: 121dc940-0d24-489f-b6aa-5a7cf0f05142 -->

Say this out loud when someone asks:

- ❌ Run continuously in the background
- ❌ Poll a server every minute
- ❌ Guarantee a task runs at an exact time
- ❌ Guarantee push delivery
- ❌ Restart yourself after being force-quit (iOS)
- ❌ Track location continuously without a persistent, visible indicator

**These are policy, not gaps.** Frameworks and hacks claiming otherwise are fragile, drain battery, and get apps rejected.

## Key insight
<!-- bite: 7af0ac9c-65a0-41d4-aa29-ec0d0eeaeb79 -->

**Both platforms decided the battery matters more than your app's convenience, and they enforce it.** So the correct architecture is opportunistic: sync when foregrounded, sync when the OS offers you a window, let push *hint* that something changed — and **never let correctness depend on background execution**, because on a meaningful share of Android devices it simply will not happen.

## Related
<!-- bite: 69271e79-838a-434d-8c09-901b35fb40ae -->
- [[mobile/07-data-and-offline-first|offline-first]] — what the sync job actually does
- [[mobile/11-performance-and-battery|performance and battery]] — why the OS is like this
- [[mobile/06-navigation|navigation]] — handling a notification tap from cold
- [[os/03-scheduling|scheduling]] — the OS side

## About this lesson
<!-- bite: 975a46c0-985d-4006-8fbe-779192a31426 -->

**Level:** Advanced. **Covers:** what you can do when you're not on screen, which is much less than you think.

*Source: [reference] — Aug 2026.*
