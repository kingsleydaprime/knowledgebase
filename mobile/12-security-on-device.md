---
id: 5bf60d3c-f34c-4b3f-b362-845443b99cce
---

# Security on Device

Security on device is protecting the app and its data when the phone itself is in the hands of someone who may want to break in. Anyone can take an app apart, read its files and watch its network traffic. This lesson shows what an app can and can't keep secret, and where things like passwords and tokens should be stored.

## The kid version first
<!-- bite: e9346bfc-8ff8-4253-bd4b-22ea47a57b5e -->

Your server sits in a locked building you control. **Your app sits in the attacker's hand.**

They can read its files, decompile its code, watch its network traffic, run it on a rooted device, and change how it behaves. **Anything shipped inside the app is public** — it just takes them an afternoon.

So the rule is: **the app is untrusted. The server enforces everything that matters.**

## The rule that decides most questions
<!-- bite: 3f7ae5ba-ee80-4c9c-911b-d310690ac3af -->

> **Never trust the client. Enforce on the server.**

Every one of these is bypassable in minutes by someone with a modified app:

- ❌ Client-side price calculation
- ❌ Client-side permission checks ("hide the admin button")
- ❌ "Verified purchase" flags the client sends
- ❌ Rate limits enforced in the app
- ❌ Feature flags gating access to paid features

**Client-side checks are UX, not security.** Hide the admin button *and* reject the request server-side. **Receipt validation must happen server-to-server** with Apple/Google — validating in the app is trivially patched, and it's the single most common way apps get their paid features stolen.

## Secrets — there are none in your binary
<!-- bite: ab33b9d2-c7d5-42e5-b38f-f7503fb24475 -->

**Anything in your app is extractable.** Not "hard to find" — extractable, by tools that automate it.

- **API keys**, including ones in obfuscated strings or native libraries
- **Encryption keys** hardcoded anywhere
- **Certificates and private keys** bundled in resources

**What to do instead:**
- **Keep secrets on your server.** Proxy third-party APIs through your backend
- **If a key must be in the app** (many analytics SDKs), **restrict it server-side** — by bundle ID, by referrer, by scope — and treat it as public
- **Never commit secrets to the repo.** Scanners find them within minutes of a push → [[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager|key hygiene]]

## Storing data on the device
<!-- bite: 462b7ad4-dc1e-483a-8eab-ba63cb68d8ca -->

| Store | Use for |
|---|---|
| **Keychain** (iOS) / **Keystore** (Android) | **Tokens, credentials, encryption keys.** Hardware-backed where available |
| App-private files | Ordinary app data. Isolated by the OS, **readable on a rooted/jailbroken device** |
| `UserDefaults` / SharedPreferences | **Non-sensitive settings only.** Plain files, trivially readable |
| External/shared storage | **Nothing sensitive.** Other apps may read it |

**The Keystore/Keychain distinction matters:** keys can be hardware-backed (Secure Enclave, StrongBox) so they **never exist in extractable form**, and can require biometric authentication for use. **That's the one genuinely strong local protection available**, and it's what you should be using for auth tokens.

**Also:** databases can be encrypted (SQLCipher), full-disk encryption is on by default on modern devices, and **logs are not private** — don't log tokens or PII in release builds.

## Authentication on mobile
<!-- bite: 76991925-88ff-455a-b0ee-7d65cdcd67ee -->

- **OAuth via the system browser** (ASWebAuthenticationSession / Custom Tabs), **not a WebView.** A WebView lets the host app read the credentials — which is exactly what you're trying to prevent, and providers increasingly reject it
- **PKCE is mandatory** for mobile OAuth. Mobile apps are public clients and cannot hold a client secret → [[backend/05-auth/index|auth]]
- **Short-lived access tokens, refresh tokens in the Keychain/Keystore**, rotation on use
- **Biometrics unlock a local secret; they don't authenticate to your server.** The right pattern is: biometric unlocks a Keystore-held key, which is used to access the token. **A boolean "biometric succeeded" that the app checks is bypassable**
- **Handle biometric enrolment changes** — a new fingerprint added should invalidate the key, and the platforms support this

## Platform attack surface
<!-- bite: c5504e66-f80f-4c8c-98aa-dfceed17248a -->

**Deep links.** Custom schemes (`myapp://`) can be registered by **any** other app. **Use verified App Links / Universal Links** for anything sensitive, and validate every parameter — a deep link is untrusted input from an arbitrary source → [[mobile/06-navigation|navigation]].

**Exported Android components.** An `Activity`, `Service` or `BroadcastReceiver` marked exported is callable by any app on the device. **Set `android:exported="false"` unless you mean it**, and require a permission if you do.

**WebViews** — the largest single source of mobile vulnerabilities. Disable JavaScript if you don't need it, **never enable `addJavascriptInterface` with untrusted content** (it's remote code execution), don't load untrusted URLs, and never ignore certificate errors.

**Clipboard, screenshots and the app switcher.** The clipboard is readable by other apps and syncs across devices. The app-switcher snapshot can expose the last screen — both platforms let you obscure it (`FLAG_SECURE` on Android).

**Third-party SDKs run with your app's full permissions.** They have shipped malware, and it's your name on the store listing. **Audit what you add.**

## Root/jailbreak detection and obfuscation
<!-- bite: 311c1c78-7711-402d-b240-7289206e6f3c -->

**Be realistic about what these do.** Both are bypassable — Frida and Magisk exist and work. They **raise the cost** and stop casual tampering; they do not stop a determined attacker.

**Worth doing:** ProGuard/R8 minification (which you want anyway for size), certificate pinning **with a kill switch** → [[mobile/08-networking-on-mobile|networking]], and platform integrity attestation (Play Integrity, App Attest) as a *signal*.

**Not worth doing:** treating any of it as a security boundary, or refusing to run on rooted devices — which mostly annoys power users while the actual attackers bypass it.

## Key insight
<!-- bite: c0441176-44ed-4ede-be9c-7682e36958c9 -->

**Every security control in the app is advisory, because the attacker controls the runtime.** The device is genuinely useful for one thing — **hardware-backed key storage that can require biometrics** — and beyond that, the only real boundary is your server. Design as though your app's source and all its data are public, because for a motivated attacker they are.

## Related
<!-- bite: 3ddd26b8-9b22-485d-bfe8-e441a40306bd -->
- [[mobile/09-permissions-and-privacy|permissions and privacy]] — the data you shouldn't have collected
- [[backend/05-auth/index|auth]] — the server side of this
- [[cybersecurity/04-web-security/index|web security]] — much of it applies
- [[cybersecurity/05-cryptography/index|cryptography]] — what the Keystore is doing

## About this lesson
<!-- bite: a6b014ae-8af1-4f5c-a2a1-f0e30b1c1689 -->

**Level:** Advanced. **Covers:** the app is on hardware the attacker owns, and that changes what "secure" means.

*Source: [reference] — Aug 2026.*
