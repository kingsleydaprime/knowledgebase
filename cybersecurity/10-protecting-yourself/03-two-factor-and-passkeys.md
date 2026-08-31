# Two-Factor and Passkeys

**[Beginner]** — the layer that survives a stolen password, why the common kind is the weakest, and the backup step everyone skips.

## The kid version first

A password is something you **know**. If someone learns it, they're in.

Two-factor adds something you **have** — your phone, a little key on your keyring. Now knowing the password isn't enough; they'd need the thing in your pocket too.

**Not all second factors are equal.** The most common one — a code by text message — is the weakest, and it's weak in a way that has cost people everything.

## The four kinds, worst to best

| | How it works | Weakness |
|---|---|---|
| **SMS codes** | Texted to your number | **SIM swap.** Someone convinces your network to move your number to their SIM. Also interceptable |
| **Email codes** | Sent to your inbox | **Not a second factor** if the account being protected *is* that email, or shares its password |
| **Authenticator app (TOTP)** | A 6-digit code from an app, rotating every 30s | **Phishable** — a fake site asks for the code and relays it in real time |
| **Passkeys / hardware keys** | Cryptographic, tied to the real site's domain | **Phishing-proof.** The best available |

**SMS is still enormously better than nothing.** If a service offers only SMS, use it. But move your important accounts off it where you can.

## SIM swap, because it's the one that ruins people

Someone contacts your mobile network pretending to be you — armed with details from social media and old breaches — and asks to move your number to a new SIM. If they succeed:

```
your number now rings on their phone
        │
"forgot password" on your email → code texted → to them
        │
they own your email → then everything your email can reset
```

**Defences, and they're quick:**
- **Ask your network for a port-out PIN / account passcode.** Most offer one. This is the single most effective step
- **Move important accounts to an app or passkey** instead of SMS
- **Don't publicise your number**, especially alongside anything suggesting you hold crypto

## Authenticator apps

A shared secret on your device generates a code from the current time. No network needed, nothing to intercept.

**Use:** Aegis (Android), Raivo or the built-in Passwords app (iOS), 2FAS, Ente Auth, or your password manager's built-in TOTP.

**One trade-off worth understanding:** storing TOTP codes *inside* your password manager is convenient and puts both factors in one place. **For most people that's still a big net win** over no 2FA — but keep your email and bank codes somewhere separate if you want the factors genuinely separated.

**Avoid Google Authenticator's old versions** — historically it had no backup, so a lost phone meant losing every code. It syncs now, but the alternatives are better.

## Passkeys — the actual fix

A passkey is a **cryptographic key pair**. The private key never leaves your device; the site stores only the public half. You unlock it with your fingerprint, face or device PIN.

**Why it's categorically better, not incrementally:**

- **There is no shared secret.** Nothing to steal from the site's database, nothing to phish out of you
- **It's bound to the real domain.** A fake `g00gle.com` **cannot** trigger your Google passkey. The browser won't offer it. **This is the property that kills phishing** — and no code-based method has it
- **Nothing to type, so nothing to be tricked into reading aloud**

**Where they're at:** Google, Apple, Microsoft, Amazon, PayPal, GitHub and many banks support them. They sync through your platform account (iCloud Keychain, Google Password Manager) or your password manager.

**Turn them on where offered.** The common worry — "what if I lose my device?" — is handled by syncing, and you keep your old method as backup during the transition.

**Hardware keys** (YubiKey, Google Titan) are the same technology in physical form, not synced. Right for high-risk accounts and anyone genuinely targeted → [[cybersecurity/10-protecting-yourself/01-your-actual-threat-model|threat model]]. **Buy two and register both**, or losing one locks you out.

## Backup codes — the step everyone skips

When you enable 2FA, you're offered **backup/recovery codes**. Most people close that screen.

**Then they lose their phone and are permanently locked out** of an account customer support cannot restore. This is far more common than being hacked.

**Do this every time:**
1. **Save the codes into your password manager** as a secure note
2. For your most important accounts, **also print them** and keep them with your documents
3. **Register a second factor** where possible — a second key, a second device

## The one that isn't covered by any of this

**No second factor protects you if you read the code out to someone.**

The scam: a call from "your bank's fraud department", urgent, convincing. *"We're verifying your identity — I've sent a code, could you read it back?"* That code is the attacker's login attempt, happening live.

> **Nobody legitimate will ever ask for a code that was sent to you.** Not your bank, not the police, not support. **The code is for you to type into the site you opened yourself.**

Same for the notification that just appeared saying *"Approve sign-in?"* when you weren't signing in. **Deny it, then change that password** — someone has it → [[cybersecurity/10-protecting-yourself/04-phishing-and-scams|phishing]].

## Where to turn it on first

1. **Your primary email** — the master key
2. **Your password manager**
3. **Banking and payments**
4. **Your mobile network account** (this is what SIM swap attacks)
5. **Work accounts**
6. Social media — impersonation damages people around you, not just you

## Key insight

**The kind of 2FA matters more than having it.** SMS stops the automated attacks and loses to a phone call to your network. Codes stop stolen passwords and lose to a convincing fake site. **Only passkeys and hardware keys are bound to the real domain**, which is why they're the only kind that survives a person being fooled — and being fooled is the realistic scenario.

## Related
- [[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager|passwords]] — the first factor
- [[cybersecurity/10-protecting-yourself/04-phishing-and-scams|phishing and scams]] — what passkeys defeat
- [[cybersecurity/10-protecting-yourself/08-when-it-goes-wrong|when it goes wrong]]
- [[cybersecurity/05-cryptography/05-digital-signatures-and-pki|digital signatures]] — the cryptography a passkey uses
