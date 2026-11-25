---
id: 3ec135b4-0a0a-4cfe-8153-336dd6139148
---

# Passwords, and the Manager

**A password manager makes and remembers a different strong password for every account — because the danger was never a weak password, but a reused one.**

## Before you start
<!-- bite: 2718618b-b636-4413-b9b5-05c3be4239af -->

You should have:

- Read the threat model, so you know credential stuffing is the attack this stops → [[cybersecurity/10-protecting-yourself/01-your-actual-threat-model|your actual threat model]].
- Nothing technical, and about an hour.

After this lesson you will be able to:

1. Explain why reuse, not weakness, is the whole problem.
2. Choose and set up a password manager with a strong master passphrase.
3. Answer the "all my eggs in one basket" objection honestly.
4. Fix your five most important accounts today without a miserable weekend.

**Study route.** Kid version and §1–3, then the practice task: set up a manager and fix your five key accounts.

## What a password manager is
<!-- bite: cbc965a4-8a7d-4539-ba2e-0d4bf336146e -->

This is thing number one on the list, and the single highest-value hour in the section. A password manager is an app that generates a unique, random password for each site, stores them all encrypted behind one master password, and fills them in for you. You remember exactly one password; it remembers the hundreds.

The reason it matters isn't that it makes passwords *stronger*. It's that it makes them *different* — and difference is what defeats the attack that actually reaches you. This lesson shows why reuse is the whole problem, which manager to pick, how to make the one password you must remember, and how to get there without changing 200 passwords in a weekend.

## The kid version
<!-- bite: 4042bfc3-7938-4f2d-8859-1e79e9ff115c -->

Imagine you have one key that opens your house, your car, your office and your safe. Convenient — until you drop it once, and now whoever finds it has everything. That's a reused password. The fix is obvious: a different key for each lock. But nobody can carry a hundred keys, so you get a single locked keyring that holds them all, and you only have to remember how to open the keyring.

A password manager is that keyring: one thing to remember, a different key for every lock inside.

**Where the analogy stops working.** A dropped keyring needs someone to physically find it. Your passwords get "dropped" when a company you used is breached and your password lands in a public file — then software tries it on every other site automatically, for free, worldwide. So the danger isn't losing one key in the street; it's that *one* reused key, leaked from one weak lock, is instantly tried against every lock you own.

## 1. Why reuse is the whole problem
<!-- bite: e95903ea-f9c4-450b-8637-bc4c32b42ca7 -->

Companies get breached constantly. When one you used is breached, your email and password end up in a file that gets passed around, and software tries that pair on hundreds of other sites:

![Credential stuffing in three steps: a shop you forgot about is breached and your email and password end up in a public dump, software replays that one pair against Gmail, your bank and your work login, and every site where you reused it is opened without anyone having to hack you.](../images/ps-credential-stuffing.svg)

**This is credential stuffing, the most common account compromise there is.** It requires no skill, costs nothing, and runs continuously. Nobody had to hack *you* — you were on a list.

## 1. Check your own exposure
<!-- bite: 8790eafc-8924-47fb-8f9f-c2af4374b67b -->

**Check your own exposure now:** [haveibeenpwned.com](https://haveibeenpwned.com) — enter your email. It's run by a well-known security researcher, it's free, and it doesn't store what you type. Most people find several breaches. That's normal, and it tells you which passwords to change first.

## 2. Use a password manager, and the master password
<!-- bite: b75e2c4c-a18a-4a31-a799-bfb7ea84ea4d -->

A manager generates a unique random password per site, stores them encrypted behind one master password, and fills them in. Any of these is fine:

1. **Bitwarden** — free tier is genuinely complete, open-source, works everywhere. The default recommendation.
2. **1Password** — paid, best polish and family sharing.
3. **Proton Pass** — good if you already use Proton.
4. **Built into your browser/OS** (Chrome, Apple Passwords, Firefox) — much better than reuse, weaker across ecosystems. **A real option** — the best manager is the one you'll actually use.

## 2. The master password
<!-- bite: 354ee3ef-923f-446b-8709-5bbd2665c7cb -->

The one password you memorise should be a **passphrase** — four or five random, unrelated words like `correct-horse-battery-staple-mango`. **Long beats complicated:** `Tr0ub4dor&3` is shorter, harder to remember, and easier to crack. Rules for this one password: used nowhere else ever; not derived from anything about you; write it down and keep it somewhere physically safe if that's what it takes (your realistic adversary is software, not a burglar in your filing cabinet); and **set up account recovery when you set up the manager** — losing the master password can mean losing everything.

## 3. "Isn't that all my eggs in one basket?"
<!-- bite: fbe16685-de47-473c-829c-b218ff68b80c -->

The most common objection, and it deserves a straight answer. **Yes. And it's still much better**, because:

1. **The alternative isn't many baskets** — it's one weak basket copied a hundred times. Reuse *is* a shared basket with a bad lock.
2. **The vault is encrypted on your device** before it's uploaded, so the provider can't read it. Even a full breach of the provider doesn't expose your passwords unless your master password is weak. LastPass's 2022 breach is the case study: vaults were stolen, and the accounts that suffered were those with weak master passwords.
3. **The basket is guarded by one strong password plus 2FA** → [[cybersecurity/10-protecting-yourself/03-two-factor-and-passkeys|two-factor]].

One concentrated, strong, encrypted basket beats a hundred copies of one weak one. That's the whole trade.

## Getting there without a miserable weekend
<!-- bite: a37fc83e-f867-4489-ab3f-c253114b8286 -->

**Don't try to change 200 passwords at once.** You'll stop after nine.

1. **Install it. Set a strong master password. Turn on 2FA for the manager itself.**
2. **Fix these five today:** your primary email, your bank, your phone-network account, your work login, and whichever service holds your card details. **Email first — it's the master key.**
3. **Let it fill in the rest as you go.** Each time you log into something over the coming months, let the manager save it and change the password if it was reused.
4. **Run its breach/reuse report** — every good manager has one — and work down the list slowly.

Also: turn on breach alerts, and **delete accounts you don't use** — a forgotten account is one you won't notice being breached.

## Security questions are passwords too
<!-- bite: bbc02653-64ea-492c-870f-c7d3da4d2810 -->

"Mother's maiden name", "first school" — these are **often discoverable** on social media or public records, and they bypass your strong password entirely. **Lie.** Put a random string in your password manager as the answer — `First school?` → `vault-orbit-clement-99`. Nothing requires the answer to be true. This is one of the highest-value five-minute habits in the section → [[cybersecurity/10-protecting-yourself/07-your-privacy-footprint|your privacy footprint]].

## Terms used in this lesson
<!-- bite: 50b09eef-200b-4094-912a-910ec87f57d1 -->

1. **Password reuse**: This is using the same password on more than one account — the single biggest cause of compromise, because one breach then opens all of them.
2. **Password manager**: This is an app that generates, stores (encrypted) and fills a unique password for every account, so you only remember one.
3. **Master password**: This is the one password you memorise to unlock the manager — made strong as a long passphrase, used nowhere else.
4. **Passphrase**: This is a password made of several random unrelated words; length makes it hard to crack while staying memorable.

## Terms used in this lesson: the vault
<!-- bite: 7e150885-0429-4478-b10e-dd213a346045 -->

5. **Credential stuffing**: This is software replaying a leaked email-and-password pair against many sites, opening every account where you reused it.
6. **Zero-knowledge / client-side encryption**: This is the manager encrypting your vault on your own device before upload, so the provider can't read it even if breached.
7. **Breach/reuse report**: This is the manager's built-in check that lists which of your passwords are weak, reused, or found in a known breach.
8. **Security question**: This is a "recovery" question (first school, pet's name) whose answer is often public — so you should store a random lie as the answer, not the truth.

## Check your understanding
<!-- bite: 0798289f-f30c-4234-98eb-281e164ebced -->

Try each one before you open the answer.

1. <!-- q: mcq id="bf79e421" -->
   You use one very strong password (20 random characters) on every site. Why is this still risky despite the strength?

   - [ ] Strong passwords are harder for *you* to type.
   - [x] If any one of those sites is breached, that single password opens all the others — reuse, not weakness, is the problem credential stuffing exploits.
   - [ ] Twenty characters is too short.
   - [ ] Websites reject long passwords.

   <details><summary>Answer</summary>

   Strength doesn't help against reuse. The attack that reaches you isn't someone *guessing* your password — it's your password being leaked from one breached site and replayed against every other. A strong password used in four places is more dangerous than a weak unique one on a site that stores passwords properly. The fix is difference: a unique password per site, which only a manager makes practical.

   </details>

2. <!-- q: gap id="d5f20716" answers="passphrase" -->
   The one password you must memorise (the master password) is best made as a ___ — four or five random unrelated words — because length makes it hard to crack while staying memorable, unlike a short string of symbols.

   <details><summary>Answer</summary>

   A passphrase (e.g. `correct-horse-battery-staple-mango`). Long beats complicated: it's both easier to remember and harder to crack than something like `Tr0ub4dor&3`. Length is what makes a password expensive to guess, and a passphrase gives you length you can actually remember.

   </details>

3. <!-- q: mcq id="1f0595b7" -->
   "A password manager puts all my eggs in one basket." What's the honest response?

   - [ ] True, so you shouldn't use one.
   - [x] True, but the alternative is one weak basket copied everywhere; the vault is encrypted on your device and guarded by a strong password plus 2FA, so it's a far better trade.
   - [ ] False — managers don't store your passwords.
   - [ ] True, and the provider can read all your passwords anyway.

   <details><summary>Answer</summary>

   It is one basket — but a strong, encrypted one, versus the reality of reuse, which is one *weak* basket copied a hundred times. The vault is encrypted on your device before upload (so even a provider breach doesn't expose it unless your master password is weak, per the LastPass case), and you protect it with a strong master password and 2FA. Concentrated and well-guarded beats scattered and weak.

   </details>

4. <!-- q: mcq id="3151f7a7" -->
   You're setting up a manager and don't want to spend a whole weekend. What's the recommended first move?

   - [ ] Change all 200 of your passwords immediately.
   - [x] Fix just five accounts today — email first, then bank, phone network, work, and your card-holding service — and let the manager save the rest as you log in over time.
   - [ ] Only store new passwords, never the old ones.
   - [ ] Memorise a unique password for each site.

   <details><summary>Answer</summary>

   Trying to change everything at once is how people give up after nine. Fix the five that matter most (email first, since it's the master key), then let the manager capture and upgrade the rest gradually as you use them. Small and done beats comprehensive and abandoned.

   </details>

5. <!-- q: mcq id="f1795ce5" -->
   A bank asks you to set a security question: "What was your first school?" What should you store as the answer?

   - [ ] Your actual first school, so you don't forget.
   - [x] A random string saved in your password manager — the true answer is often discoverable and bypasses your strong password.
   - [ ] Your mother's maiden name instead.
   - [ ] The same answer you use on every site.

   <details><summary>Answer</summary>

   Lie, and store the lie. Real answers to security questions (first school, pet, mother's maiden name) are often findable on social media or public records, and they let an attacker bypass your strong password entirely via "recovery". A random string like `vault-orbit-clement-99` in your manager removes that whole attack path, and nothing requires the answer to be true.

   </details>

6. <!-- q: open id="90878b10" -->
   A friend says "I don't need a password manager, my password is really strong and I can remember it." Explain, in plain terms, why that reasoning misses the actual threat.

   <details><summary>Answer</summary>

   Because the threat isn't someone sitting at a login screen trying to guess their password — strength would help against that, but that's not what happens. The real threat is that a company they signed up to years ago gets breached, and their email-and-password pair ends up in a public file that software automatically tries against hundreds of other sites (credential stuffing). If they remember one password, it's because they reuse it — and the moment any *one* of those sites is breached, that single password opens all the others, no matter how strong it is. A manager fixes this by making every password different and random, so a breach at one site exposes nothing anywhere else. The goal isn't an unguessable password; it's that no two sites share a password, which is impossible to do by memory and trivial with a manager.

   </details>

## Practice — set up a manager and fix your five
<!-- bite: 48f2d2c8-ef45-4e75-bed5-d318732f330f -->

**Task.** The highest-value hour in this section.

1. Install a password manager (Bitwarden if unsure), set a strong passphrase master password, and turn on 2FA for the manager itself.
2. Set up its account recovery (emergency access / recovery kit) *now*.
3. Change the passwords on your five key accounts to unique generated ones — email first.
4. Check [haveibeenpwned.com](https://haveibeenpwned.com) for your email and change any still-reused password it flags.

## Practice: when it's done
<!-- bite: 425b15f6-a4b8-4a4e-8b94-a1185939ec6b -->

Here's how you know the task is finished.

**Done when:** your five key accounts each have a unique generated password, your manager is protected by a strong passphrase + 2FA, and recovery is set up so you can't lock yourself out. The remaining accounts are fine to migrate gradually — the five that matter are done. You don't need to log this anywhere technical; the done-state is that your email no longer shares a password with anything.

## Before moving on
<!-- bite: fda8e5b4-059b-4489-a019-c1f4e62cac58 -->

You can now explain why reuse is the whole problem, set up a manager with a strong passphrase, answer the "one basket" objection, and fix your key accounts without burning a weekend.

**Recap for later lookup:** reuse, not weakness, is the problem — credential stuffing replays leaked pairs. Use a manager (Bitwarden is a fine default; the built-in one beats reuse); master password = a long passphrase, used nowhere else, with recovery set up. The "one basket" is encrypted on your device and guarded by a strong password + 2FA — far better than reuse. Fix five accounts first (email first), migrate the rest gradually. Lie on security questions and store the lie.

Next: [[cybersecurity/10-protecting-yourself/03-two-factor-and-passkeys|two-factor and passkeys]] — the layer that survives even a stolen password.

## Related
<!-- bite: 4d7a6d37-0331-40dc-ba7f-e9ae5d9aac0b -->

- [[cybersecurity/10-protecting-yourself/03-two-factor-and-passkeys|Two-factor and passkeys]] — the layer that survives a stolen password.
- [[cybersecurity/04-web-security/02-secure-authentication|Secure authentication]] — the builder's side: how sites *should* store these.
- [[cybersecurity/06-attacks-and-threats/04-password-malware-and-exploits|Password attacks]] — the professional treatment of what you're defending against.

## About this lesson
<!-- bite: 1f94c14d-ba19-4ba9-a0d9-6f02e6793d2b -->

**Level:** Beginner (no code). **Covers:** why reuse (not strength) is the whole problem, credential stuffing, choosing and setting up a password manager, the master passphrase, the "all eggs in one basket" objection, migrating without a miserable weekend, and lying on security questions, with a hands-on set-up-and-fix-five task. **Where it sits:** lesson 2 of the [[cybersecurity/10-protecting-yourself/index|Protecting Yourself]] section — thing number one, and load-bearing. **Sources:** the original vault note, rebuilt to the [[COURSE-STANDARD|course standard]] with quizzes and a personal task; written for the non-technical reader.
