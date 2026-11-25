---
id: eb807345-f26f-478b-9545-ed43010c3ac8
---

# Your Actual Threat Model

**Your threat model is an honest answer to three questions — what you have worth taking, who would try to take it, and what it would cost you.**

## Before you start
<!-- bite: 364a5b8f-ef9e-46bc-b884-ea90fd5b1469 -->

You should have:

- Nothing technical. This whole section assumes no code and no security background.
- An email account and a phone — the two things it turns out matter most.

After this lesson you will be able to:

1. Write a three-question threat model for yourself.
2. Say who is realistically after ordinary people, and who genuinely is targeted.
3. Rank what's actually worth protecting, starting with your email.
4. Name the six highest-value things to do — and the popular advice that isn't worth your time.

**Study route.** Kid version and the three questions, then the practice task: writing your own threat model and checking your exposure.

## What a threat model is
<!-- bite: 6f50fca3-952a-426b-b6b7-eed16dd52368 -->

Security advice usually arrives as an enormous list, all of it urgent, none of it ranked. So people either do nothing, or exhaust themselves on the wrong things. A threat model cuts through that: it's the small, honest answer that tells you *which* advice is for you.

It's three questions — what do I have that's worth taking, who would plausibly take it, and what would it cost me? Answer those and the enormous list shrinks to about six things. This lesson walks through them for the ordinary person (who is almost never personally targeted), flags the people who genuinely are, and ends with the ranked six. The rest of the section is those six, one at a time.

## The kid version
<!-- bite: 232bdac7-4266-45fa-8d59-01f10adf84b9 -->

Imagine everyone in your town is told to fortify their house against burglars. Most people don't need a vault and armed guards — there's no master thief after *them* specifically. What actually happens is someone walks down the street at night trying every door handle, and walks into the houses left unlocked. So the useful move isn't becoming a fortress; it's locking your door, so the handle-rattler moves to the next house.

A threat model is working out which kind of danger you actually face. For nearly everyone, it's the handle-rattler — automated, aimed at everybody, stopped by locking a few doors.

**Where the analogy stops working.** A burglar has to be physically on your street. Your real "handle-rattler" is software trying millions of doors a second across the whole internet, using keys stolen from *other* break-ins (passwords from old breaches). So the few doors worth locking are specific — your email, your phone number — and locking them is a setting, not a wall.

## 1. You are almost certainly not being targeted
<!-- bite: 4e0d6b4a-8033-4af2-9198-2100d51b5443 -->

This is the most freeing thing in the section. **Nearly all harm that reaches ordinary people is opportunistic, not targeted.** Nobody chose you; a system chose everybody, and you were on the list. What that looks like:

1. **Credential stuffing.** A company you used was breached; your email and password are in a file with millions of others, replayed automatically against every major site. **If you reused that password, that account is already open.**
2. **Phishing at scale.** Ten million identical messages — it only needs to fool 0.1%.
3. **SIM swap.** Someone moves your number to their SIM, then resets every account that texts you a code.
4. **Device theft.** Usually the threat is the *data*, not the hardware.
5. **Investment and romance fraud.** Months of grooming, a fake platform — often run by organised crime, not a lone scammer.

**What's *not* on that list:** someone cracking your strong password, breaking your encryption, or surveilling you personally. Those are what people worry about, and the least likely.

## 2. But "not targeted" isn't universal
<!-- bite: 3e4bb49e-dabe-4716-aa1e-de29fa118f39 -->

Some people **are** targeted, and the advice changes. Be honest about whether you're one:

| If you are | The added risk |
|---|---|
| **A journalist or activist** | State-level actors, device seizure, targeted malware |
| **A business owner or finance staff** | **Business email compromise** — the invoice that isn't real |
| **Someone with visible crypto holdings** | Targeted phishing, and physical risk. **Don't publicise holdings** |
| **A public figure** | Impersonation, doxxing, coordinated harassment |
| **Leaving an abusive relationship** | **The most dangerous case here** — the adversary knows your birthday, your pet's name, your recovery answers, and may have had physical access to your devices |

**That last row deserves saying plainly.** If someone who knows you intimately may have access to your accounts or devices, changing a password can *alert* them and escalate things. Domestic-violence support organisations have specialists for exactly this, and the right move is to talk to them **before** changing anything. A general guide is not adequate there.

## 3. What's actually worth protecting
<!-- bite: f344796c-3b8d-4da9-9166-9fd4e9541465 -->

Rank yours. Most people's list looks like this:

1. **Your primary email.** **The master key** — password resets for everything land there. Someone with your email has, given twenty minutes, everything else. Protect it more than your bank.
2. **Your phone number.** The second master key, because so many services use it for recovery. This is what makes SIM swap so effective.
3. **Money** — banking, payment apps, anything holding crypto.
4. **Identity documents** — enough to open accounts in your name.
5. **Private material** — photos, messages, health records. Low financial value, high personal cost.
6. **Work access** — where your mistake becomes your employer's incident.

**If you protect your email and your phone number well and do nothing else, you've done most of the available good.**

## The six things, ranked
<!-- bite: 46c98173-c9b9-4b59-a778-9d20e255cf5d -->

The whole section in one list, ordered by harm prevented per hour spent:

| # | Do this | Why it's here | Lesson |
|---|---|---|---|
| 1 | **A password manager, stop reusing** | Kills credential stuffing entirely | [[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager\|02]] |
| 2 | **Real 2FA on email and banking** | Kills stolen-password attacks | [[cybersecurity/10-protecting-yourself/03-two-factor-and-passkeys\|03]] |
| 3 | **Turn on automatic updates** | Kills most malware. One click | [[cybersecurity/10-protecting-yourself/05-your-devices-and-networks\|05]] |
| 4 | **Learn the phishing tells** | The commonest way people lose money | [[cybersecurity/10-protecting-yourself/04-phishing-and-scams\|04]] |
| 5 | **A backup you have tested** | The only defence against ransomware and loss | [[cybersecurity/10-protecting-yourself/06-backups-and-your-data\|06]] |
| 6 | **Lock your phone, encrypt your laptop** | Turns theft into a hardware loss | [[cybersecurity/10-protecting-yourself/05-your-devices-and-networks\|05]] |

**That's a weekend, once, then almost nothing ongoing.**

## What isn't worth your time
<!-- bite: aeb164c5-deba-42a3-9b5f-c98da0cbfc42 -->

Being honest about this matters, because bad advice crowds out good:

1. **Changing passwords every 90 days.** Counterproductive — it produces `Summer2024!` → `Autumn2024!`. Even NIST now recommends against forced rotation. Change a password when there's a *reason* to.
2. **A consumer VPN "for security".** Oversold. It moves who can see your traffic; it doesn't stop phishing, malware or breaches → [[cybersecurity/10-protecting-yourself/05-your-devices-and-networks|05]].
3. **Antivirus beyond what's built in.** Windows Defender is good now; third-party suites are mostly upsell.
4. **Covering your webcam.** Harmless, and far down the list.
5. **Worrying about encryption being broken.** It won't be. The attacker goes *around* it, through you.

## Terms used in this lesson
<!-- bite: 46b32298-6e5a-4be9-a8c8-d52367b1a237 -->

1. **Threat model**: This is your honest answer to what you have worth taking, who would take it, and what it would cost — used to decide which security steps are worth your time.
2. **Opportunistic attack**: This is an attack aimed at everybody, not you specifically — automated, cheap, and stopped by being a slightly harder target than average.
3. **Targeted attack**: This is an attack aimed at you personally, by someone willing to spend effort — rare for ordinary people, but real for journalists, the wealthy, and those with a hostile ex.
4. **Credential stuffing**: This is software replaying your email-and-password pair (leaked from one breach) against every other site, opening any account where you reused it.

## Terms used in this lesson: the master keys
<!-- bite: 073a0e7c-8226-44f3-ac54-f43715b4c3fb -->

5. **Primary email**: This is the account most of your others reset *through*, which makes it the master key — protect it above everything.
6. **SIM swap**: This is an attacker moving your phone number to their SIM so they receive your reset codes — which is why your number is the second master key.
7. **Business email compromise (BEC)**: This is a scam where a real-looking email (often from a hacked account) asks you to pay or change bank details — the main targeted risk for finance staff.
8. **Blast radius (personal version)**: This is how much damage one compromise causes — which is why your email, resetting everything, matters most.

## Check your understanding
<!-- bite: 04e62e75-2144-45f6-bc81-0decb00bdef8 -->

Try each one before you open the answer.

1. <!-- q: mcq id="8c9a0fd6" -->
   For an ordinary person (not a journalist, activist, or someone with a hostile ex), what kind of attack is almost all real-world harm?

   - [ ] A skilled hacker personally cracking their strong password.
   - [x] Opportunistic and automated — aimed at everybody, like credential stuffing and mass phishing, not at them specifically.
   - [ ] Government surveillance of them personally.
   - [ ] Someone breaking their encryption.

   <details><summary>Answer</summary>

   Nearly all harm to ordinary people is opportunistic: a system chose everybody and they were on the list. The things people worry about (cracked passwords, broken encryption, personal surveillance) are the least likely. This is freeing, because the defence isn't being unbreakable — it's being a slightly harder target so the automation moves on.

   </details>

2. <!-- q: mcq id="3983ee94" -->
   Of everything in your digital life, which single account should you protect *most* carefully, and why?

   - [ ] Your bank, because it holds money directly.
   - [x] Your primary email, because password resets for everything else land there — it's the master key.
   - [ ] Your social media, because it has the most followers.
   - [ ] Your work login, because your employer requires it.

   <details><summary>Answer</summary>

   Your primary email is the master key: whoever controls it can click "forgot password" on your bank, your social media and nearly everything else and have the reset code delivered to them. Protect it more carefully than your bank. Your phone number is the second master key for the same reason (recovery codes).

   </details>

3. <!-- q: gap id="21993a87" answers="credential stuffing|credential-stuffing" -->
   When a site you used is breached and software then replays your leaked email-and-password pair against every other major site, opening any account where you reused that password, the attack is called ___.

   <details><summary>Answer</summary>

   Credential stuffing — the most common account compromise there is. It needs no skill, costs nothing, and runs continuously. The single defence that kills it is a different password on every site (a password manager), so one breach can't open anything else.

   </details>

4. <!-- q: mcq id="7957e9e7" -->
   Someone is leaving an abusive relationship and the ex may have had access to their devices and knows their personal details. Why can standard advice like "change your passwords" backfire here?

   - [ ] Changing passwords is always pointless.
   - [x] A password change can *alert* an adversary who's watching the account, escalating the situation — so they should consult a domestic-violence specialist before changing anything.
   - [ ] Their passwords are already strong enough.
   - [ ] Abusive exes can't access accounts.

   <details><summary>Answer</summary>

   This is the most dangerous case in the section. An intimate adversary may know the recovery answers and may be monitoring the accounts, so a sudden change can tip them off and escalate things, sometimes dangerously. The right move is to contact a domestic-violence support organisation with specialists for this *before* changing anything — general technical advice is not adequate.

   </details>

5. <!-- q: mcq id="05a733a3" -->
   Which of these is listed as *not worth your time* for an ordinary person's security?

   - [ ] Using a different password on every site.
   - [ ] Turning on two-factor authentication for your email.
   - [x] Forcing yourself to change all your passwords every 90 days.
   - [ ] Keeping a tested backup.

   <details><summary>Answer</summary>

   Forced periodic password rotation is counterproductive — it pushes people to `Summer2024!` → `Autumn2024!`, which is weaker, and even NIST now recommends against it. Change a password when there's a *reason* (a breach, a suspected compromise). The genuinely valuable steps are the ranked six, none of which is rotation.

   </details>

6. <!-- q: open id="f695954d" -->
   Explain the core idea that "security is being a worse target than the person next to you", and why that's a more useful goal for an ordinary person than "being unbreakable".

   <details><summary>Answer</summary>

   Because the attacks that reach ordinary people are automated and opportunistic — they try millions of targets cheaply and move on from anything that costs effort. The attacker isn't a person who picked you and will persist; it's software trying every door handle. So you don't need to be unbreakable (impossible, and exhausting to attempt) — you need to be expensive enough that the automation gives up and goes to an easier target. Locking your few important doors (unique passwords, 2FA on email, updates) makes you that harder target, and it takes about a weekend. "Unbreakable" chases the rare targeted attacker most people will never face, while ignoring the common opportunistic one everybody faces; "harder than average" defends against the threat that's actually coming.

   </details>

## Practice — write your own threat model
<!-- bite: 5db57332-e7ca-4698-a6f7-c1cb9efba7d4 -->

**Task.** This one's about you. On paper or in a note:

1. **Answer the three questions.** What do you have worth taking? Who would plausibly try? What would it cost you? Be honest about which targeted row (if any) applies to you.
2. **Rank what's worth protecting**, starting with your email and phone number.
3. **Check your exposure:** go to [haveibeenpwned.com](https://haveibeenpwned.com) and enter your email. Note which breaches show up — those tell you which passwords to change first.
4. **List your six things** and tick which you've already done.

## Practice: when it's done
<!-- bite: 75a11679-334e-4a0b-bc2a-34c9fec2f5a8 -->

Here's how you know the task is finished.

**Done when:** you have a written three-question model, a ranked list of what matters (email at the top), your haveibeenpwned results, and your six-things checklist with the gaps marked. The gaps are your to-do list for the rest of this section. If the "leaving an abusive relationship" row applies to you, the done-state is *contacting a specialist first* — not working through this checklist alone.

## Before moving on
<!-- bite: ce208146-9f4f-4d12-8e5e-75f2ed4677c2 -->

You can now write a three-question threat model, tell opportunistic from targeted attacks, rank what's worth protecting, and name the six things and the advice that isn't worth your time.

**Recap for later lookup:** threat model = what you have / who'd take it / what it costs. Nearly all harm to ordinary people is opportunistic (credential stuffing, mass phishing, SIM swap) — not personal. Some people *are* targeted (journalists, finance staff, the wealthy, those leaving abuse — the last needs a specialist first). Protect your email and phone number above all. The six things: password manager, 2FA, auto-updates, phishing tells, tested backup, device lock/encryption. Skip: forced rotation, consumer VPN "for security", extra antivirus.

Next: [[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager|passwords and the manager]] — thing number one, and the single highest-value hour in the section.

## Related
<!-- bite: eb524d75-6f8e-416b-a41e-a51dbd161c8d -->

- [[cybersecurity/10-protecting-yourself/index|The protecting-yourself track]] — the whole list.
- [[cybersecurity/06-attacks-and-threats/index|Attacks and threats]] — the same material, for people defending organisations.
- [[cybersecurity/01-fundamentals/02-cia-triad|The CIA triad]] — the professional framing of "what's worth protecting".

## About this lesson
<!-- bite: aaefd9e1-6a1c-4984-87a5-6c555353a6ad -->

**Level:** Beginner (no code, assumes nothing technical). **Covers:** the three-question threat model, why ordinary people are rarely targeted, who genuinely is (including the domestic-abuse case), what's worth protecting (email and phone number first), the six ranked things, and the advice that isn't worth your time, with a personal threat-model-and-exposure-check task. **Where it sits:** lesson 1 of the [[cybersecurity/10-protecting-yourself/index|Protecting Yourself]] section — read it first, because it tells you which of the rest matter for you. **Sources:** the original vault note, rebuilt to the [[COURSE-STANDARD|course standard]] with quizzes and a self-assessment task; written for the non-technical reader, in the shape of [[using-ai/index|using-ai]].
