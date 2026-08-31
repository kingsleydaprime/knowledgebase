# Release and Distribution

**[Intermediate]** — the gatekeepers, and why mobile release engineering is cautious by necessity.

## The kid version first

You can't just deploy. **You submit a build, someone reviews it, and then users decide whether to install it.**

So a bug can be live for days before a fix reaches anyone — and **old versions live on phones for years.** Every release decision in mobile follows from those two facts.

## The pipeline

```
build → sign → upload → REVIEW → staged rollout → monitor → (halt or continue)
```

**Signing** is where iOS newcomers lose days. Certificates, provisioning profiles, capabilities and identifiers must all agree. **Xcode's automatic signing works; use it**, and use **fastlane match** for teams so certificates aren't passed around manually.

Android is simpler: **one upload key, and Play App Signing holds the real key.** Turn that on — losing your signing key without it means **you can never update your app again** and must publish a new listing.

## Review

| | Apple | Google |
|---|---|---|
| **Time** | Hours to a few days | Usually hours |
| **Strictness** | **High**, and human | Lower, more automated |
| **First submission** | Slowest, most scrutiny | Slower than updates |

**What actually gets rejected:**
- **Crashes on the reviewer's device** — the most common cause, and usually avoidable
- **A login wall with no way in.** **Provide a demo account** in review notes, always
- **Broken or missing features** relative to your description
- **Payments outside the store's system** for digital goods — the rule with the most litigation attached, and still enforced
- **Privacy declarations that don't match behaviour** → [[mobile/09-permissions-and-privacy|privacy]]
- **Missing account deletion** if you support account creation
- **Permissions requested without a clear purpose string**

**When rejected:** read the actual guideline cited, fix it, and reply in Resolution Center. **You can appeal, and appeals do succeed** — reviewers make mistakes. Don't resubmit unchanged.

**Budget for review.** Never promise a launch date that assumes same-day approval.

## Staged rollout — the most important habit

**Never release to 100% at once.**

```
1% → watch crash-free rate → 5% → 20% → 50% → 100%
```

**Google Play** supports this natively and lets you **halt** a rollout. **Apple's phased release** rolls out over 7 days and can be paused.

**Watch crash-free users and ANR rate at each step.** A regression caught at 1% affects a hundredth of the damage. **This is the closest thing mobile has to a rollback**, because there isn't one — you can only halt and ship a fix.

## The two switches you need before you need them

**1. Feature flags / remote config.** The only way to turn off a broken feature without a release. **Set this up before launch** — Firebase Remote Config or equivalent. It converts "emergency release, three days" into "toggle, thirty seconds."

**2. Forced update.** An endpoint returning a minimum supported version, and a blocking screen below it. **You will need this** — a security fix, a breaking API change, a broken build. **Retrofitting it is impossible**, because the users you need to reach are on the version that lacks it.

**Use it sparingly.** Blocking users is hostile; a "recommended update" prompt should be the default.

## Versioning and API compatibility

**Old versions never die.** A meaningful share of users won't update for months, some never.

- **Never break your API for old clients.** Add fields, don't remove them → [[mobile/08-networking-on-mobile|networking]]
- **Clients must ignore unknown fields**
- **Know your actual version distribution** — both consoles show it, and it's usually worse than you'd guess
- **Database migrations must chain** across skipped versions. **A failed migration on launch is a crash loop that permanently bricks the app for that user** — test upgrades from several old versions, not just the last

## CI/CD

Automate it — mobile release is too error-prone by hand:

- **Fastlane** is the standard for both platforms: build, sign, screenshot, upload, release notes
- **CI:** GitHub Actions, Bitrise, Codemagic. **iOS builds need macOS runners**, which is a real cost
- **Distribute test builds** — TestFlight (iOS), Play Internal Testing / Firebase App Distribution
- **On every PR:** build, unit test, lint. **On main:** upload to internal testing automatically
- **Automate version bumps** and changelogs → [[devops/06-ci-cd/README|CI/CD]]

## Monitoring — the part that's easy to skip

You cannot SSH into a user's phone. **Instrumentation is all you get:**

- **Crash reporting** — Crashlytics or Sentry, **with symbol upload in the release pipeline** or your stack traces are unreadable
- **The metric to watch: crash-free users.** Both stores rank on it, and it's the clearest health signal
- **ANRs (Android)** — the app frozen more than 5s. Tracked by Play and penalised
- **Android Vitals / Xcode Organizer** — real-device data on startup, battery and rendering → [[mobile/11-performance-and-battery|performance]]
- **Alert on crash-rate regressions** per version, and **halt the rollout automatically** if you can

## Store listing

The part engineers ignore and that determines whether anyone installs:

- **Screenshots are the main conversion lever** — far more than the description
- **The first two lines of the description** are what's read
- **Ratings prompts:** use the native API, and ask **after a moment of success**, never on launch or after an error
- **Respond to reviews.** It measurably improves ratings, and it's where you find bugs nobody reported
- **Localise** the listing at minimum, before the app itself

## Key insight

**Mobile has no rollback**, so the entire discipline shifts to prevention and containment: staged rollouts to limit blast radius, feature flags to disable without shipping, forced update as the last resort, and never breaking an API that old clients depend on. **Set up the flags and the version endpoint before your first release** — they're the two things you cannot add later, exactly when you need them.

## Related
- [[mobile/09-permissions-and-privacy|permissions and privacy]] — declarations checked at review
- [[mobile/11-performance-and-battery|performance]] — the metrics the stores rank on
- [[devops/06-ci-cd/README|CI/CD]] — the general discipline
- [[devops/11-delivery-and-advanced/README|delivery]] — staged rollout in the wider sense

*Source: [reference] — Aug 2026.*
