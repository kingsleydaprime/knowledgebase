---
id: 8319f0be-2752-4d28-90a1-58959ba63a0d
---

# Your Privacy Footprint

**Your privacy footprint is everything already out there about you — and those facts are the raw material an attacker uses to seem legitimate.**

## Before you start
<!-- bite: 51238bbc-8e4b-46f2-8ee9-8f12ebc9eaf6 -->

You should have:

- Met the "lie on security questions" habit → [[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager|passwords and the manager]].
- Met how this data gets used in scams → [[cybersecurity/10-protecting-yourself/04-phishing-and-scams|phishing and scams]].

After this lesson you will be able to:

1. Explain why privacy is a security problem, not a separate topic.
2. Name where your data already is, and accept what can't be undone.
3. Apply the highest-value habits — severing the link between public facts and account access.
4. Tell what's worth doing from what's sold to you.

**Study route.** Kid version and §1–2, then the practice task: the privacy habits that remove an attack path.

## What your privacy footprint is
<!-- bite: b7133877-3392-47c0-9af7-c681368df88a -->

This is the quieter of the six-plus topics, and it connects two things people treat as separate. Privacy and security sound like different concerns — until you notice the mechanism joining them: **the things people know about you are the raw material for convincing you they're legitimate.**

Your birthday, first school, mother's maiden name, pet, employer, street — those aren't just personal details. They're the *answers to security questions*, and the ingredients of a phone call that sounds like it's really from your bank. This lesson covers where your data already is (and what can't come back), the practical fix (not hiding your life, but severing the link between public facts and account access), and an honest split of what's worth doing from what's sold to you.

## The kid version
<!-- bite: 8bc9c3e9-01c8-4125-8e72-15b777b91829 -->

Imagine a con artist who, before knocking on your door, reads everything about you from a notice board in the town square: your name, your dog, where you went to school, when your birthday is. Now when they knock, they can say *"Hi, it's about Rex, and I know it's nearly your birthday"* — and you believe them, because how would a stranger know that? The facts themselves are harmless. The danger is that they make the *next lie* believable.

Your privacy footprint is that town-square notice board. You can't take most of it down. But you can make sure none of your locks open just because someone read the board.

**Where the analogy stops working.** A town notice board is small and local. Yours is global and permanent — breach dumps, data brokers, social media, public records — and it's searched by software, not a single con artist. So the realistic goal isn't scrubbing the board clean (impossible); it's making the facts on it *useless* by ensuring no account access depends on anything a stranger could look up.

## 1. Where your data is, and the security consequence
<!-- bite: 3bf54d15-91d2-43f1-9493-492e0742e313 -->

Be realistic — some of it is out and won't come back: **breach dumps** (check [haveibeenpwned.com](https://haveibeenpwned.com) — most people find several), **data brokers** who aggregate and sell profiles you never meaningfully agreed to, **social media** (yours and other people's posts about you), **public records**, and **your phone's apps** selling location and usage data.

## 1. The security consequence
<!-- bite: e72c94c0-51f5-411a-8588-d2c4fbb8bf19 -->

The security consequence is a chain:

![How a privacy footprint becomes a breach, in three steps: an attacker reads public facts from your social media such as your dog's name, school and birthday; those facts answer your bank's security questions; and the account is reset, or a phone call using the details sounds completely real.](../images/ps-privacy-to-breach.svg)

Or the softer version: a call that opens with your full name, address and last four card digits — those details make you believe the rest, and that belief is the actual attack. **So the fix isn't hiding your life. It's severing the link between public facts and account access.**

## 2. The highest-value habits
<!-- bite: 327e1272-8f0a-4014-9949-98f4c8396782 -->

1. **Lie on security questions.** Random strings in your manager. Your mother's maiden name is discoverable; `vault-orbit-clement-99` is not. Five minutes per account, and it removes an entire attack path.
2. **Use email aliases.** A different address per service, so a breach at one doesn't link the others and you can see who leaked or sold your address (Apple's Hide My Email, Firefox Relay, SimpleLogin). Also lets you cut spam off at the source.
3. **Protect your phone number like a password.** It's a recovery method and the SIM-swap target — ask your network for a port-out PIN; consider a separate number for shops and sign-ups.
4. **Audit what's public.** Search your own name, email and number; look at your profiles while logged out. You'll find something you forgot.
5. **Lock down old accounts.** The 2011 forum has your details and no security team. Delete accounts you don't use ([JustDeleteMe](https://justdeleteme.xyz) lists how).
6. **Review app permissions twice a year.** Revoke generously — you can re-grant.

## 3. What's worth it, and what isn't
<!-- bite: a655001f-6841-4e41-93e3-765d40febacc -->

**Worth doing:**

1. **A privacy-respecting browser setup** — Firefox or Safari, plus **uBlock Origin**. Ad networks are a genuine malware vector ("malvertising"), so **this is a security measure, not just privacy**.
2. **A search engine that doesn't profile you** — DuckDuckGo, Brave.
3. **Encrypted messaging** for private conversations — Signal.
4. **Opting out of the big data brokers** (tedious; in the EU/UK, GDPR gives a legal right to erasure that generally works).

**Mostly not worth it:** deleting all social media (the cost is usually social, the benefit smaller than the six basics); trying to be truly anonymous (enormously hard, not what your threat model needs); paid "remove your data from the internet" services (incomplete, forever, for a subscription); and a VPN "for privacy from advertisers" (tracking is by cookies and fingerprinting, not IP).

## What not to post
<!-- bite: 7d75e805-6a58-42d9-8fd8-e63dd07c36c4 -->

Not paranoia — these specific things get used: your **full date of birth** alongside your name and place of birth; **boarding passes and tickets** (the barcode holds your booking reference and surname); your **address** or photos identifying it; **real-time holiday posts** (post afterwards); **children in school uniform**; **crypto holdings** (targeted phishing *and* physical risk); and **anything you'd answer as a security question**.

And an easy one people miss: those social quizzes — *"your stripper name is your first pet and the street you grew up on"* — are collecting security-question answers, by design or by accident.

## Terms used in this lesson
<!-- bite: 00ede24e-1af0-440c-a92a-961f82f8c71e -->

1. **Privacy footprint**: This is the total of what's already known or findable about you — breach data, broker profiles, social media, public records.
2. **Data broker**: This is a company that aggregates public records, purchases and app data into profiles it sells, without your meaningful consent.
3. **Email alias**: This is a disposable, per-service email address that forwards to your real one, so a breach at one service doesn't link to the others.
4. **Malvertising**: This is malware delivered through online ads, which is why an ad blocker like uBlock Origin is a security tool, not just a convenience.

## Terms used in this lesson: the fix
<!-- bite: 1f0c5f8d-dc92-4513-81ba-5245d9ec7a61 -->

5. **Security question**: This is a recovery question whose true answer (first school, pet) is often public — so you store a random lie instead.
6. **Right to erasure**: This is the legal right (under GDPR in the EU/UK) to make a company delete your data, which generally works against data brokers.
7. **Fingerprinting**: This is tracking you by the unique combination of your browser and device settings, rather than by IP — which is why a VPN doesn't stop advertiser tracking.
8. **Doxxing**: This is publishing someone's private identifying information to harass them — part of why what you post about your address and routine matters.

## Check your understanding
<!-- bite: e44b9542-cdb4-4c2f-93fc-79c76944afb8 -->

Try each one before you open the answer.

1. <!-- q: mcq id="42da7a7e" -->
   Why is privacy treated as a *security* problem in this section, rather than a separate concern?

   - [ ] Because privacy laws require security measures.
   - [x] Because public facts about you (birthday, school, pet) are the answers to security questions and the ingredients that make a scam call sound legitimate.
   - [ ] Because privacy settings also encrypt your files.
   - [ ] They aren't related; it's just convenient to group them.

   <details><summary>Answer</summary>

   The link is one mechanism: the things people know about you are the raw material for convincing you — or your bank — that an attacker is legitimate. Your details answer "recovery" questions and make a phone call believable. So reducing how much of your life is usable as account-access material is directly a security act.

   </details>

2. <!-- q: mcq id="9a866abd" -->
   The lesson says the practical fix "isn't hiding your life, it's severing the link between public facts and account access." What does that mean in practice?

   - [ ] Delete all your social media immediately.
   - [x] Make the public facts useless — e.g. store random lies as security-question answers — so no account can be accessed using something a stranger could look up.
   - [ ] Move to a different country.
   - [ ] Stop using the internet.

   <details><summary>Answer</summary>

   You can't retract what's already public, and trying to scrub it all is impractical. The high-leverage move is to ensure none of your account access *depends* on those facts: lie on security questions (and store the lie), so "mother's maiden name" being discoverable no longer unlocks anything. The facts stay public but become useless to an attacker.

   </details>

3. <!-- q: gap id="acbe45c3" answers="aliases|alias|email aliases" -->
   Using a different email ___ per service (via Hide My Email, Firefox Relay, or SimpleLogin) means a breach at one site doesn't link to your others, and lets you see who leaked or sold your address — and shut that one off.

   <details><summary>Answer</summary>

   Email aliases. Each service gets its own forwarding address, so breaches don't correlate across services, and if one alias starts getting spam you know exactly who leaked it and can disable just that one. It's a privacy *and* security habit, and it also kills spam at the source.

   </details>

4. <!-- q: mcq id="776d5716" -->
   Which of these is described as genuinely *worth doing* — and as a security measure, not just a privacy one?

   - [ ] A paid "remove your data from the internet" subscription service.
   - [x] A browser with uBlock Origin, because ad networks are a real malware vector (malvertising).
   - [ ] A VPN to stop advertiser tracking.
   - [ ] Deleting all your social media.

   <details><summary>Answer</summary>

   An ad blocker like uBlock Origin blocks malvertising — malware delivered through ad networks — so it's a security control, not just a privacy nicety. The others are oversold or ineffective: paid removal services are incomplete and endless, a VPN doesn't stop tracking (which uses cookies and fingerprinting, not IP), and deleting social media costs more socially than it gains over the six basics.

   </details>

5. <!-- q: mcq id="f39d60be" -->
   A fun social-media quiz asks "your stripper name is your first pet plus the street you grew up on." Why is answering it a bad idea?

   - [ ] It's embarrassing.
   - [x] It's harvesting common security-question answers (first pet, childhood street) that can be used to reset your accounts.
   - [ ] It uses too much data.
   - [ ] It's copyrighted.

   <details><summary>Answer</summary>

   Those quizzes collect exactly the facts used as security-question answers — first pet, childhood street, mother's maiden name — whether by deliberate design or just by accident of what they ask. Posting the answers publicly hands attackers the material to reset accounts. (And it's another reason to store random lies as your actual security-question answers.)

   </details>

6. <!-- q: open id="1f5cb008" -->
   "Your privacy footprint is your attacker's research budget." Explain this idea, and why it means you can defend yourself even though you can't delete what's already public.

   <details><summary>Answer</summary>

   The idea is that every public fact about you lowers the effort an attacker needs to be convincing: your birthday, pet, school, employer and address are free research that makes the next phone call sound real ("it's about Rex, and happy birthday for Thursday") and makes security questions answerable. The more that's out there, the richer the attacker's "budget" for impersonation and account recovery. You can't retract what's already public — breach dumps, broker profiles, old posts and public records are out and won't come back — but you don't have to. You defend yourself by making those facts *useless*: ensure no account access depends on anything a stranger could look up. Concretely, store random lies as security-question answers, protect your phone number with a port-out PIN, use email aliases so breaches don't link up, and lock down or delete old accounts. The facts stay public, but they no longer open anything — so the attacker's research budget buys them nothing.

   </details>

## Practice — the privacy habits that remove an attack path
<!-- bite: 42e889b5-1aab-4e40-90d7-886720cd4b6e -->

**Task.** Sever the link between public facts and your accounts.

1. On your most important accounts, replace any real security-question answers with random strings stored in your manager.
2. Set up email aliases for new sign-ups (Hide My Email / Firefox Relay / SimpleLogin).
3. Search your own name, email and phone number, and look at your social profiles logged out — note what's exposed.
4. Delete two old accounts you no longer use, and install uBlock Origin in your browser.

## Practice: when it's done
<!-- bite: c3ac00e6-fb8e-4729-bc61-a435f2107b72 -->

Here's how you know the task is finished.

**Done when:** your key accounts' security answers are random (not real), new sign-ups use aliases, you've seen what's public about you, and you've pruned at least two dead accounts. The test: could someone who read everything public about you reset any of your accounts? If the answer is no, the footprint is still there but it's been made useless.

## Before moving on
<!-- bite: 5654431f-7f1d-43e6-8604-0f0193cc5316 -->

You can now explain why privacy is a security problem, name where your data already is, apply the habits that sever facts from access, and tell what's worth doing from what's sold to you.

**Recap for later lookup:** your public facts are the answers to security questions and the ingredients of a convincing scam — privacy is security. You can't delete what's out (breach dumps, brokers, records), so make it useless: lie on security questions, use email aliases, port-out PIN your number, delete old accounts, review permissions. Worth it: uBlock Origin (malvertising), non-profiling search, Signal, GDPR erasure. Not worth it: deleting all social media, true anonymity, paid removal services, a VPN "for privacy". Don't post your DOB, address, boarding passes, real-time holidays, kids' uniforms, crypto holdings, or security-question answers.

Next: [[cybersecurity/10-protecting-yourself/08-when-it-goes-wrong|when it goes wrong]] — the ordered checklist for the moment something has already happened.

## Related
<!-- bite: 0cbc8060-cdcf-4ac2-a943-c4c2a0208902 -->

- [[cybersecurity/10-protecting-yourself/04-phishing-and-scams|Phishing and scams]] — where this data gets used.
- [[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager|Passwords]] — the security-question fix.
- [[cybersecurity/02-ethical-hacking/03-reconnaissance|Reconnaissance]] — the professional side: how this is gathered deliberately.

## About this lesson
<!-- bite: e2d9840a-8410-4660-b29a-c97c45aa0efa -->

**Level:** Beginner (no code). **Covers:** why privacy is a security problem, where your data already is, the habits that sever public facts from account access (lie on security questions, email aliases, port-out PIN, prune old accounts), and an honest split of what's worth doing from what's sold, with a sever-the-link task. **Where it sits:** lesson 7 of the [[cybersecurity/10-protecting-yourself/index|Protecting Yourself]] section. **Sources:** the original vault note, rebuilt to the [[COURSE-STANDARD|course standard]] with quizzes and a personal task; written for the non-technical reader.
