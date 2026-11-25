---
id: 748fdc11-9137-4803-bf27-ce52294e981b
---

# Two-Factor and Passkeys

**Two-factor login means needing two things to get in — your password and something you have — and the kind matters more than having it.**

## Before you start
<!-- bite: 8d0423bd-c9ce-40e9-8989-e21f7caefe18 -->

You should have:

- Set up a password manager, the first factor this builds on → [[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager|passwords and the manager]].
- Nothing technical, and your phone to hand.

After this lesson you will be able to:

1. Rank the four kinds of second factor from worst to best, and say why.
2. Explain SIM swap and the quick step that defends against it.
3. Explain why passkeys are categorically better, not incrementally.
4. Save the backup codes everyone skips, and spot the "read me the code" scam.

**Study route.** Kid version and §1–4, then the practice task: turn on real 2FA on your email and save the backup codes.

## What two-factor is
<!-- bite: 835e6e66-dd60-4c50-9feb-f3d00b8638bb -->

This is thing number two: the layer that survives even a stolen password. A password is something you *know*; if someone learns it, they're in. Two-factor adds something you *have* — your phone, a little key — so knowing the password isn't enough.

But not all second factors are equal, and the gap between them is the whole point of this lesson. The most common kind, a code by text message, is the weakest, and it's weak in a way that has cost people everything. By the end you'll know which kind to turn on where, why passkeys end phishing in a way codes never can, and how not to lock yourself out doing it.

## The kid version
<!-- bite: 128a52aa-a911-4e15-b6e1-719ad32b8ac7 -->

Imagine your front door needs both a key *and* a fingerprint. Losing the key isn't enough for a burglar — they'd need your finger too. That's two-factor: a second lock of a different kind, so stealing one doesn't open the door.

But some "second locks" are better than others. A code texted to your phone is like a spare key hidden under a mat that a smooth-talker can convince the locksmith to hand over. A passkey is like a lock that physically only your own finger fits — it can't be handed to anyone, copied, or talked out of you.

**Where the analogy stops working.** A real second lock just has to be present. Online, the attacker's best move is to get *you* to open the lock for them — a fake site or a phone call that tricks you into typing or reading out the code. So the thing that matters most isn't whether the second lock exists; it's whether it can be *fooled by fooling you*. That's the line between codes (foolable) and passkeys (not).

## 1. The four kinds, worst to best
<!-- bite: 7b79d388-d3f1-4429-b8e2-896f43721278 -->

| Kind | How it works | Weakness |
|---|---|---|
| **SMS codes** | Texted to your number | **SIM swap** — someone moves your number to their SIM. Also interceptable |
| **Email codes** | Sent to your inbox | **Not a second factor** if the account being protected *is* that email |
| **Authenticator app (TOTP)** | A 6-digit code rotating every 30s | **Phishable** — a fake site asks for the code and relays it live |
| **Passkeys / hardware keys** | Cryptographic, tied to the real site's domain | **Phishing-proof.** The best available |

**SMS is still enormously better than nothing.** If a service offers only SMS, use it — but move your important accounts off it where you can.

## 2. SIM swap — the one that ruins people
<!-- bite: 0812726c-78c0-46f0-bcab-2aefb58aef33 -->

Someone contacts your mobile network pretending to be you — armed with details from social media and old breaches — and asks to move your number to a new SIM. If they succeed:

![A SIM swap in four steps: the attacker convinces your mobile network to move your number to their SIM, your number now rings on their phone, a forgot-password on your email texts the reset code to them, and they then own your email and everything it can reset.](../images/ps-sim-swap.svg)

**Defences, and they're quick:**

1. **Ask your network for a port-out PIN / account passcode.** Most offer one. This is the single most effective step.
2. **Move important accounts to an app or passkey** instead of SMS.
3. **Don't publicise your number**, especially alongside anything suggesting you hold crypto.

## 3. Authenticator apps, and passkeys — the actual fix
<!-- bite: e523ecfd-ca64-435a-a75a-92d342f71266 -->

An **authenticator app** holds a shared secret on your device and generates a code from the current time — no network, nothing to intercept. Use Aegis (Android), the built-in Passwords app (iOS), 2FAS, Ente Auth, or your password manager's built-in codes. (Storing codes *inside* your manager is convenient and still a big net win over no 2FA; keep email and bank codes separate if you want the factors genuinely apart.)

## 3. Passkeys — the actual fix
<!-- bite: 3a3490d3-8dcd-4df9-8130-08a4c3394a85 -->

A **passkey** is a cryptographic key pair. The private half never leaves your device; the site stores only the public half; you unlock it with your fingerprint, face or PIN. **Why it's categorically better, not incrementally:**

1. **There's no shared secret** — nothing to steal from the site's database, nothing to phish out of you.
2. **It's bound to the real domain.** A fake `g00gle.com` *cannot* trigger your Google passkey — the browser won't offer it. **This is the property that kills phishing**, and no code-based method has it.
3. **Nothing to type, so nothing to be tricked into reading aloud.**

Google, Apple, Microsoft, Amazon, PayPal, GitHub and many banks support them, synced through your platform or password manager. **Turn them on where offered.** Hardware keys (YubiKey, Titan) are the same technology in physical form — right for high-risk accounts; **buy two and register both**, or losing one locks you out.

## 4. Backup codes — the step everyone skips
<!-- bite: a042683d-c2c4-4c38-a5a0-a280c6c33dbd -->

When you enable 2FA, you're offered **backup/recovery codes**. Most people close that screen — then lose their phone and are permanently locked out of an account customer support cannot restore. This is far more common than being hacked. Do this every time:

1. **Save the codes into your password manager** as a secure note.
2. For your most important accounts, **also print them** and keep them with your documents.
3. **Register a second factor** where possible — a second key, a second device.

## The one that isn't covered by any of this
<!-- bite: 820c3e94-da26-4dcb-9859-f30bf0bed7c7 -->

**No second factor protects you if you read the code out to someone.** The scam: a call from "your bank's fraud department", urgent and convincing — *"we're verifying your identity, I've sent a code, could you read it back?"* That code is the attacker's login attempt, happening live.

> **Nobody legitimate will ever ask for a code that was sent to you.** Not your bank, not the police, not support. The code is for you to type into the site you opened yourself.

Same for a surprise *"Approve sign-in?"* notification when you weren't signing in: **deny it, then change that password** — someone has it → [[cybersecurity/10-protecting-yourself/04-phishing-and-scams|phishing]].

## Where to turn it on first
<!-- bite: 07681419-4d0c-4ef0-9403-6d92ba9dfd5f -->

1. **Your primary email** — the master key.
2. **Your password manager.**
3. **Banking and payments.**
4. **Your mobile network account** (this is what SIM swap attacks).
5. **Work accounts.**
6. Social media — impersonation damages people around you.

## Terms used in this lesson
<!-- bite: 803ca057-2aa7-4d6c-80a3-2d97b7a86b7d -->

1. **Two-factor authentication (2FA)**: This is requiring two different kinds of proof to log in — something you know (password) plus something you have (phone, key).
2. **SMS code**: This is a one-time code texted to your number — the weakest second factor, because your number can be stolen by SIM swap.
3. **Authenticator app (TOTP)**: This is an app that generates a rotating code from a shared secret and the current time, with nothing sent over the network to intercept.
4. **Passkey**: This is a cryptographic key pair tied to the real site's domain; the private half never leaves your device, which makes it phishing-proof.

## Terms used in this lesson: the traps and the backups
<!-- bite: e6c4e961-f9c3-4394-bc8e-5d27b2c14090 -->

5. **SIM swap**: This is an attacker moving your phone number to their SIM, so your SMS codes and resets go to them. A port-out PIN defends against it.
6. **Phishing-proof / domain-bound**: This describes a factor (passkey, hardware key) that only works on the genuine site, so a fake lookalike site can't use it.
7. **Backup/recovery codes**: These are one-time codes you save when enabling 2FA, to get back in if you lose your device — the step most people skip and later need.
8. **Hardware key**: This is a physical passkey device (YubiKey, Titan); buy two and register both so losing one doesn't lock you out.

## Check your understanding
<!-- bite: 7787358c-ff6e-490d-ba36-66dff74c028a -->

Try each one before you open the answer.

1. <!-- q: mcq id="41489cc3" -->
   Why is a code sent by SMS the *weakest* kind of two-factor authentication?

   - [ ] Text messages cost money to send.
   - [x] Your phone number can be stolen via a SIM swap (and SMS can be intercepted), so an attacker can receive your codes without your phone.
   - [ ] SMS codes are too short to be secure.
   - [ ] Phones can't receive texts reliably.

   <details><summary>Answer</summary>

   SMS depends on your phone *number*, and a SIM swap moves that number to the attacker's SIM — after which your codes text to them. It can also be intercepted. It's still far better than nothing (use it if it's all a service offers), but move important accounts to an app or, better, a passkey. The weakness is that the factor isn't really tied to a device you hold.

   </details>

2. <!-- q: mcq id="9b4c054c" -->
   What makes a passkey "categorically" better than an authenticator-app code, rather than just a bit better?

   - [ ] It generates longer codes.
   - [x] It's bound to the real site's domain, so a fake lookalike site can't trigger it — which eliminates phishing, something no code-based method can do.
   - [ ] It works without a device.
   - [ ] It never expires.

   <details><summary>Answer</summary>

   A passkey only works on the genuine domain — the browser won't offer your Google passkey to `g00gle.com`. An authenticator code can still be phished: a fake site asks for it and relays it to the real one in real time. Because the passkey can't be used on the wrong site and there's nothing to type or read aloud, phishing simply doesn't apply. That's a different category, not an increment.

   </details>

3. <!-- q: gap id="48f66d91" answers="port-out PIN|port out PIN|account passcode|PIN" -->
   The single most effective defence against a SIM swap is to ask your mobile network to set a ___ on your account, so your number can't be moved to another SIM without it.

   <details><summary>Answer</summary>

   A port-out PIN (or account passcode). Most networks offer one, and it stops someone armed with your personal details from talking the network into transferring your number. Combined with moving important accounts off SMS, it closes the SIM-swap path that otherwise unlocks everything your number can reset.

   </details>

4. <!-- q: mcq id="f008af1b" -->
   You get a call from "your bank's fraud team" saying they've sent a verification code and asking you to read it back. What's happening?

   - [ ] A routine security check — read it to them.
   - [x] A scam: that code is the attacker's own login attempt, and reading it out hands them your account. No legitimate party asks for a code sent to you.
   - [ ] The bank verifying your phone works.
   - [ ] A test of your 2FA setup.

   <details><summary>Answer</summary>

   The code was generated because *they* are trying to log in as you right now; reading it back completes their login. No bank, police force, or support line will ever ask for a code that was sent to you — it's for you to type into a site you opened yourself. The same applies to an unexpected "approve sign-in?" prompt: deny it, then change that password, because someone already has it.

   </details>

5. <!-- q: mcq id="21972ec9" -->
   You enable 2FA on an important account and it shows you ten backup codes. What should you do?

   - [ ] Close the screen — you have your phone, so you won't need them.
   - [x] Save them in your password manager (and print them for your most important accounts), because losing your device otherwise locks you out permanently.
   - [ ] Email them to yourself.
   - [ ] Memorise them.

   <details><summary>Answer</summary>

   Being locked out after losing a phone is far more common than being hacked, and support often can't restore the account. Save the backup codes into your manager as a secure note, print them for your most critical accounts, and register a second factor where you can. Skipping this is the mistake that turns a lost phone into a lost account.

   </details>

6. <!-- q: open id="cdfac3e4" -->
   Two people both have "2FA turned on". One uses SMS codes, the other uses a passkey. A convincing fake login page tricks each of them. Explain why one is compromised and the other isn't.

   <details><summary>Answer</summary>

   The SMS user is compromised; the passkey user isn't. With SMS (or any code), the fake site collects both the password *and* the code the victim types in, and relays them to the real site in real time — the code is just a number, and the victim handed it over, so the second factor adds nothing against a convincing fake. With a passkey, there's nothing to type or hand over, and crucially the passkey is bound to the real domain: the browser simply won't offer the victim's passkey to the fake lookalike site, so there's no secret for the fake page to capture and relay. The passkey's protection doesn't depend on the user spotting the fake — it fails safe even when the person is fooled, which is the realistic scenario. That domain-binding is why passkeys end phishing and codes don't.

   </details>

## Practice — turn on real 2FA where it counts
<!-- bite: 14b227c2-7f96-4746-a425-21e110427860 -->

**Task.** Add a strong second factor to the accounts that matter.

1. On your primary email, turn on 2FA with an authenticator app or (better) a passkey — not SMS if you can avoid it.
2. **Save the backup codes** into your password manager, and print them.
3. Do the same for your password manager and your bank.
4. Ask your mobile network to set a port-out PIN on your account.

## Practice: when it's done
<!-- bite: de48daf0-4474-40a2-8c6e-37fcfa98e3d2 -->

Here's how you know the task is finished.

**Done when:** your email, manager and bank each have app-or-passkey 2FA with backup codes saved (and printed for email), and your phone number has a port-out PIN. The test: if you lost your phone tomorrow, your backup codes would get you back in — and if a fake site fooled you, your email's passkey wouldn't help it.

## Before moving on
<!-- bite: 1259cf03-1ff0-4a32-b90d-a307cfa5cc00 -->

You can now rank the four second factors, explain and defend against SIM swap, say why passkeys are categorically better, and save the backup codes and spot the "read me the code" scam.

**Recap for later lookup:** 2FA = something you know + something you have. Worst to best: SMS (SIM swap), email codes, authenticator app (phishable), passkeys/hardware keys (phishing-proof, domain-bound). SIM-swap defence = port-out PIN + move off SMS. Passkeys are categorically better because they're bound to the real domain, so a fake site can't use them. Always save backup codes. Nobody legitimate asks for a code sent to you.

Next: [[cybersecurity/10-protecting-yourself/04-phishing-and-scams|phishing and scams]] — the attacks these factors defend against, and the two habits that stop nearly all of them.

## Related
<!-- bite: 7f724fdc-ae88-45d4-88a0-1c88a7247b3d -->

- [[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager|Passwords]] — the first factor.
- [[cybersecurity/10-protecting-yourself/04-phishing-and-scams|Phishing and scams]] — what passkeys defeat.
- [[cybersecurity/05-cryptography/05-digital-signatures-and-pki|Digital signatures]] — the cryptography a passkey uses.

## About this lesson
<!-- bite: 6467ab64-af01-4a19-93d9-6bee98364403 -->

**Level:** Beginner (no code). **Covers:** the four kinds of second factor worst-to-best, SIM swap and the port-out PIN, why passkeys are phishing-proof (domain-bound), authenticator apps, backup codes, and the "read me the code" scam, with a hands-on turn-on-2FA task. **Where it sits:** lesson 3 of the [[cybersecurity/10-protecting-yourself/index|Protecting Yourself]] section. **Sources:** the original vault note, rebuilt to the [[COURSE-STANDARD|course standard]] with quizzes and a personal task; written for the non-technical reader.
