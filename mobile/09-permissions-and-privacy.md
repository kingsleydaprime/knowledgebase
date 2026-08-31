# Permissions and Privacy

**[Intermediate]** — the user can say no, the stores enforce rules, and both have teeth.

## The kid version first

Your app cannot read contacts, use the camera, or know where the user is **unless they agree**. They're asked, in a system dialog you don't control, and they can refuse — or grant it once, or grant a blurry version of it.

**Every permission-dependent feature needs a working "they said no" path.** That's not defensive programming; it's the common case.

## How to ask

**The single most effective technique: explain *before* you trigger the dialog.**

```
BAD:   app launches → 4 permission dialogs → user denies all → app is useless

GOOD:  user taps "Find nearby"
         → your own screen: "We use your location to show shops near you.
            We don't store it." [Not now] [Continue]
              → THEN the system dialog
```

**Why it matters so much:** on iOS, a denial is close to permanent — the dialog does not appear again, and recovery requires talking the user into Settings. **You get one ask.** Priming it with context routinely doubles acceptance.

**The rules:**
- **Ask in context, at the moment the feature needs it** — never in a launch sequence
- **Explain the benefit to them**, not the requirement on you
- **Handle denial gracefully.** Manual entry instead of location; upload instead of camera
- **Never nag.** Repeated prompting is a store violation, and users uninstall
- **If they've denied, deep-link to Settings** — and only when they ask for the feature again

## The permission tiers people miss

Both platforms have moved from yes/no to something more granular, and code written for the old model breaks:

- **"Only this once"** (both) — you get the permission for one session. **It will be revoked.** Re-check every time; never cache the answer
- **Approximate location** (Android 12+, iOS) — the user can grant *coarse* location. **Your "find nearby" feature must work with a ~2km radius**
- **Selected photos** (iOS 14+, Android 14+) — the user picks specific photos rather than granting the library. **Your gallery picker must handle a partial library**
- **Background location** is a **separate, later, harder** grant, requires the foreground one first, and gets extra store review scrutiny
- **Notifications require permission on both platforms now** (Android 13+ joined iOS). **Don't ask on first launch** — ask when there's something worth being notified about

## Privacy labels and declarations

Both stores require you to declare what you collect, and **being wrong is a rejection or a removal.**

- **Apple: Privacy Nutrition Labels** plus **privacy manifests** — and third-party SDKs must supply their own. **Apple also requires a declared reason for certain APIs** (file timestamps, disk space, `UserDefaults`) that were being abused for fingerprinting
- **Google: the Data Safety section**, similarly detailed

**The consequence that catches teams out: your SDKs collect data, and it's your declaration.** An analytics or ad SDK you added in an afternoon changes what you must declare. **Audit your dependencies** — an abandoned SDK quietly shipping data is both a compliance problem and a security one.

**Tracking:** Apple's **App Tracking Transparency** requires an explicit prompt before tracking across apps, and **the large majority of users decline.** Plan attribution around that rather than fighting it.

## Data minimisation

The rule that solves most of this:

> **Don't collect it and you don't have to declare it, secure it, or breach it.**

- **Ask what each field is for.** Most sign-up forms collect things nobody uses
- **Prefer on-device processing.** Both platforms have capable on-device ML — it's faster, works offline, and is a genuine privacy claim
- **Set a retention period** and honour it
- **Don't log personal data.** Crash reports and analytics leak more PII than most teams realise
- **Support deletion.** Both stores now **require an in-app account-deletion route** if you support account creation. This is enforced

## The legal layer

GDPR (EU/UK), CCPA (California), and a growing list elsewhere — including **Nigeria's NDPA** and similar regimes across Africa and Asia. The common obligations:

- **A lawful basis** for processing
- **Real consent** — freely given, specific, revocable. **Pre-ticked boxes and "consent" walls that offer no genuine choice do not qualify**
- **Access and deletion rights**
- **Breach notification**, usually within 72 hours
- **Children's data** is a stricter category — COPPA, and both stores' family policies. **If your app might attract under-13s, get advice**

**Not legal advice** — but "we're a small app" is not a defence, and the store policies enforce much of this regardless of jurisdiction.

## Key insight

**Permissions are a UX problem before they're a technical one.** The code is a few lines; whether users say yes depends entirely on whether you asked at a moment when the reason was obvious. And since a denial is close to permanent on iOS, **the priming screen you write before the system dialog is some of the highest-leverage UI in the app.**

## Related
- [[mobile/12-security-on-device|security on device]] — protecting what you did collect
- [[mobile/13-release-and-distribution|release]] — where declarations get checked
- [[cybersecurity/10-protecting-yourself/07-your-privacy-footprint|your privacy footprint]] — the user's side of this
- [[cybersecurity/08-governance-risk-and-compliance/README|governance and compliance]]

*Source: [reference] — Aug 2026. Not legal advice.*
