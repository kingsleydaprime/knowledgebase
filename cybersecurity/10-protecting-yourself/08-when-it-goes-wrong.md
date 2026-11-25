---
id: f85a70ab-a499-407b-a01d-8742c10eeacd
---

# When It Goes Wrong

**This is the checklist for when something has already gone wrong — account taken over, money sent, device lost — in order, because order matters.**

## Before you start
<!-- bite: 82645bfc-d9db-4eee-bf95-f0240d284370 -->

You should have:

- Done the six things, so recovery is possible → [[cybersecurity/10-protecting-yourself/01-your-actual-threat-model|the six things]].
- A tested backup, which several steps rely on → [[cybersecurity/10-protecting-yourself/06-backups-and-your-data|backups]].

After this lesson you will be able to:

1. Recover a compromised account *in the right order* — email first, then recovery settings.
2. Respond to money fraud, SIM swap, a compromised device, and ransomware.
3. Handle sextortion and the common webcam bluff calmly.
4. Help someone else through an incident without making it worse.

**Study route.** Read it now, before you need it. The practice task is making your own ordered plan while you're calm.

## What this lesson is
<!-- bite: 9429cc1a-ac41-454d-83e7-5f40f4d2ff9d -->

This is the last of the section, and the one to read *before* anything happens — because you won't think clearly during. The value here isn't new information; it's the **ordering**. Doing the right steps in the wrong sequence wastes the narrow window when recovery is still possible.

And the first rule underneath all of it: **don't freeze from embarrassment.** Being scammed says nothing about your intelligence — the operations are professional, designed by people who do this full time. Silence is what turns a recoverable incident into an unrecoverable one. This lesson is the sequence for an account takeover, for money, for SIM swap, for a compromised device, for ransomware, and for sextortion — plus how to help someone else.

## The kid version
<!-- bite: 7006044a-3cd5-46ad-adda-ee27718577ba -->

Imagine a fire in the kitchen. There's a right order: get people out, then call for help, then tackle the fire if it's safe — not rummage for the extinguisher while the room fills with smoke. Panic makes people do things out of order and lose the minutes that matter. So you learn the order *before* there's a fire, when you're calm, and on the day you just follow it.

This lesson is that fire drill for a hack. The single most important thing in it isn't a clever trick — it's "email first, then check what the attacker left behind", learned now so you can run it on autopilot later.

**Where the analogy stops working.** A kitchen fire is visible and over quickly. A compromise can be *quiet* — an attacker who changes a password feels resolved, but they may have left a recovery email or a forwarding rule so they can walk back in next week. So unlike a fire, "it looks out" isn't enough: you have to go looking for the back doors they planted, or you'll be compromised again.

## 1. An account was compromised — the order matters
<!-- bite: 87f7ed6e-8131-40ba-b6e6-3106061ae311 -->

1. **Start with your email. Always.** Even if the compromised account is something else — your email resets everything, so if it's also compromised, fixing anything downstream is pointless.
2. **Change the password** — from a device you trust, to something unique.
3. **Sign out all other sessions** ("Security → Active sessions → Sign out everywhere"). A password change alone often doesn't kick out an existing session.
4. **Check recovery settings — the step people miss.** Attackers add *their own* recovery email, phone, or 2FA, and **email forwarding rules** that silently copy your mail or auto-delete bank alerts. Remove anything you don't recognise.
5. **Enable or re-enable 2FA**, ideally a passkey or app, not SMS.
6. **Work outward** — every account that used that password, and every account that resets *through* that email. Prioritise money and identity.
7. **Look at what they did** — sent messages, changed settings, new payment methods — and warn anyone they messaged.

## 2. Money, and SIM swap
<!-- bite: c154068f-07b6-481a-b89b-84c4f256d7bd -->

**Card fraud:** call the bank, freeze the card, dispute the charges — protections are strongest early. Check for a small *test* charge before the big one, which tells you when the details leaked.

**A transfer you were tricked into:** call your bank **immediately** — same-day recall sometimes works and the window is hours. In the UK, ask explicitly about authorised-push-payment (APP) fraud reimbursement, and don't accept the first refusal.

**Crypto:** be blunt — it's almost always unrecoverable. Report it anyway, and be ready for the **recovery scam** that will find you next.

**SIM swap** (your phone loses service for no reason, or an unexpected "number transferred" message) is an **emergency — minutes, not hours**: contact your network from another phone, secure your email first from a different device, then anything using SMS 2FA, and set a port-out PIN once restored.

## 3. A compromised device, and ransomware
<!-- bite: abc57119-6e53-405f-a1eb-8b835b277ccd -->

**Device signs:** sudden slowdown, unfamiliar programs, browser redirects, contacts getting messages you didn't send, or you gave someone remote access.

1. **Disconnect it from the network.**
2. **From a *different, clean* device**, change your important passwords — not from the suspect machine, where a keylogger captures the new ones too.
3. **Wipe and reinstall.** Cleaning tools are unreliable against anything serious; a full reinstall is the only answer you can trust.
4. **Restore data from a backup predating the problem** → [[cybersecurity/10-protecting-yourself/06-backups-and-your-data|backups]].

**Ransomware:** disconnect immediately (it spreads to network drives and synced folders); **don't pay** if you have any alternative (it funds the industry and often doesn't restore the files); check [nomoreransom.org](https://www.nomoreransom.org) for a free decryptor; then wipe, reinstall, and restore from your offline backup. Report it.

## 4. Sextortion and the webcam bluff
<!-- bite: e2d5dedf-4600-4605-894e-19f42b306e89 -->

Increasingly common, increasingly aimed at teenagers, where consequences have been fatal:

1. **Do not pay** — it marks you as a payer and the demands continue.
2. **Do not engage.**
3. **Screenshot everything**, then block.
4. **Report** to the platform and the police (UK: Revenge Porn Helpline; US: NCMEC's Take It Down for minors).
5. **Tell someone.** The leverage is entirely the fear of exposure, and it **collapses the moment someone else knows**.

**The common bluff:** most "I recorded you through your webcam" emails have nothing. They quote an old breached password to seem credible. **Change that password and ignore the rest.**

## If you're helping someone else, and afterwards
<!-- bite: 7b8ce790-66ca-48af-abd5-d9d6ee605658 -->

**Helping:** don't lead with judgement (shame stops people reporting in time); take over the sequence (they're panicking, you're not); **email first, always**; watch for the follow-up "recovery service" scam (there's no such thing); and if a child is involved, go to the platform and police rather than handling it privately.

**Afterwards:** once it's stable, do the boring part — **the six things** → [[cybersecurity/10-protecting-yourself/01-your-actual-threat-model|threat model]]. Most repeat incidents happen because the incident got fixed and the *cause* didn't. Write down what happened and how they got in — that's a personal postmortem, the same discipline organisations use → [[cybersecurity/07-security-operations/04-incident-response|incident response]].

## Terms used in this lesson
<!-- bite: 3fd1b1db-f993-43a1-b557-1371bea369da -->

1. **Account recovery settings**: These are the recovery email, phone, and backup 2FA attached to an account — which an attacker alters so they can get back in, and which you must check and clean.
2. **Session**: This is a logged-in connection to a service; "sign out all sessions" ends the attacker's even after you change the password.
3. **Forwarding rule**: This is an email filter that auto-copies or auto-deletes messages — a classic attacker back door (silently forwarding your mail, hiding bank alerts).
4. **Keylogger**: This is malware that records what you type, which is why you change passwords from a *different, clean* device after a compromise.

## Terms used in this lesson: the money and the bluff
<!-- bite: cb6c8f08-8b78-473d-bd0c-47d480ec99f1 -->

5. **APP fraud reimbursement**: This is the (UK) scheme to refund authorised-push-payment fraud — a transfer you were tricked into making; ask for it explicitly.
6. **SIM swap**: This is your number being moved to an attacker's SIM — a minutes-not-hours emergency, because it unlocks SMS resets.
7. **Recovery scam**: This is a follow-up fraud targeting people already scammed, promising to get their money back; it never works.
8. **Sextortion**: This is blackmail threatening to release intimate material; the leverage is secrecy, which collapses once you tell someone and report.

## Check your understanding
<!-- bite: d6f06fab-a1b3-403b-8e9f-2909d20a1ae7 -->

Try each one before you open the answer.

1. <!-- q: mcq id="4653b813" -->
   Several of your accounts were compromised. Which do you secure *first*, and why?

   - [ ] Your bank, because money is most urgent.
   - [x] Your email, because it resets everything else — securing anything downstream is pointless if your email is still compromised.
   - [ ] Whichever was compromised most recently.
   - [ ] Your social media, to stop impersonation.

   <details><summary>Answer</summary>

   Email first, always. It's the master key: as long as an attacker controls it, they can reset any account you just fixed. Secure the email (new password, sign out all sessions, clean recovery settings, strong 2FA), then work outward to money and identity. Sequence beats speed here.

   </details>

2. <!-- q: mcq id="f5c86c63" -->
   After changing a compromised account's password, why must you also check the recovery settings and email rules?

   - [ ] To update your contact details.
   - [x] Attackers add their own recovery email/phone and forwarding rules so they can walk back in or siphon your mail — a password change doesn't remove those back doors.
   - [ ] It's required by law.
   - [ ] To improve the account's security score.

   <details><summary>Answer</summary>

   This is the step people miss and the reason they get re-compromised a week later. An attacker who added a recovery phone number, a backup 2FA method, or a silent forwarding rule keeps access no matter how many times you change the password. You have to find and remove the back doors — that's why "email first, sign out sessions, *then check recovery*" is the order.

   </details>

3. <!-- q: mcq id="3e08bc5a" -->
   You realise your laptop is compromised. Where should you change your important passwords from?

   - [ ] The compromised laptop, immediately.
   - [x] A different, clean device — because a keylogger on the compromised laptop would capture the new passwords as you type them.
   - [ ] Any device, it doesn't matter.
   - [ ] Don't change them until the laptop is fixed.

   <details><summary>Answer</summary>

   Changing passwords on the infected machine just hands the new ones to the keylogger. Use a different, trusted device. The full sequence for a compromised device: disconnect it from the network, change passwords from a clean device, then wipe and reinstall (cleaning tools can't be trusted against serious malware), and restore from a backup predating the infection.

   </details>

4. <!-- q: mcq id="d8e398f5" -->
   You get an email saying "I recorded you through your webcam, pay me or I'll release it" — and it quotes a password you recognise as an old one. What's the right response?

   - [ ] Pay quickly before they release it.
   - [x] It's almost certainly a bluff using a password from an old breach — change that password (if still used anywhere) and ignore the rest; don't pay or engage.
   - [ ] Reply asking for proof.
   - [ ] Cover your webcam and pay a smaller amount.

   <details><summary>Answer</summary>

   These mass "webcam" emails almost never have anything; they quote an old breached password to seem credible. Paying marks you as a payer and invites more. Change that password if you still use it anywhere, and ignore the message. For genuine sextortion the rules are: don't pay, don't engage, screenshot, report, and tell someone — the threat's power is secrecy, which collapses once someone else knows.

   </details>

5. <!-- q: gap id="54f83eba" answers="SIM swap|SIM-swap|sim swap" -->
   Your phone suddenly loses all service for no reason, and you get a message that your number has been transferred. This is the sign of a ___, which is a minutes-not-hours emergency because it hands your SMS reset codes to an attacker.

   <details><summary>Answer</summary>

   A SIM swap. Act fast: contact your mobile network from another phone, secure your email first from a different device, then anything using SMS 2FA, and set a port-out PIN once restored. Because your number resets so many accounts, a SIM swap can cascade into everything, which is why it's one of the few true emergencies in the section.

   </details>

6. <!-- q: open id="e02e7f9a" -->
   A friend calls, panicking, having just been scammed, and is too embarrassed to tell anyone. Explain why "don't freeze from embarrassment" is treated as the first rule, and the one piece of ordering you'd walk them through.

   <details><summary>Answer</summary>

   Embarrassment is the single biggest cause of a recoverable incident becoming unrecoverable, because it causes silence and delay — and nearly every response here has a narrow time window (same-day transfer recall, early fraud protections, stopping an attacker before they entrench). The scams are run by professionals who do this full time, so being fooled says nothing about intelligence; treating it as shameful just helps the attacker by buying them time. So the first thing to do is take the shame off the table — "this happens to smart people, let's just move fast" — so they act and report in time. The one piece of ordering I'd walk them through is **email first**: whatever got compromised, secure the email before anything else (new password from a trusted device, sign out all sessions, and *check the recovery settings and forwarding rules* for back doors the attacker added), because the email resets everything else and fixing downstream accounts is pointless while the email is still open. Then work outward to money and identity. Calm, and in order — that's what preserves the window.

   </details>

## Practice — make your plan before you need it
<!-- bite: 5591f5ff-28e6-48a5-b5d3-c5360fe6b34f -->

**Task.** Prepare while you're calm.

1. Find, for each major service, where "sign out all sessions" and the recovery settings live — so you're not hunting during an incident.
2. Write your own short ordered checklist (email first → password → sign out sessions → check recovery → 2FA → work outward), and save it somewhere you could reach from another device.
3. Note the real reporting contacts for your country (fraud reporting, your bank's fraud line) now.
4. Confirm you have a tested backup predating any problem (from lesson 6), since device recovery depends on it.

## Practice: when it's done
<!-- bite: 13661af1-a047-4f4d-980d-0a739a4c48b5 -->

Here's how you know the task is finished.

**Done when:** you have a personal, ordered incident checklist saved where you could reach it from a second device, you know where sessions and recovery settings live on your key accounts, and you have your country's fraud-reporting details written down. The point is that on the bad day you *follow* a plan instead of inventing one while panicking.

## Before moving on
<!-- bite: e915b18f-3906-4b30-a947-7e1bdaac63c5 -->

You can now recover an account in the right order, respond to money fraud, SIM swap, a compromised device and ransomware, handle sextortion and the webcam bluff, and help someone else.

**Recap for later lookup:** sequence beats speed. Account takeover: email first → change password (from a trusted device) → sign out all sessions → *check recovery settings and forwarding rules* → re-enable 2FA → work outward. Money: call the bank immediately (same-day recall), ask about APP reimbursement; crypto is usually gone; beware the recovery scam. SIM swap = emergency. Compromised device: disconnect, change passwords from a *clean* device, wipe and reinstall, restore from a pre-incident backup. Ransomware: disconnect, don't pay, check nomoreransom.org, restore offline backup. Sextortion: don't pay/engage, screenshot, report, tell someone. Afterwards: do the six things, write a postmortem.

**The section, in one line:** 01 told you which threats are yours; 02–07 are the six things that make you a hard target; and 08 is the ordered plan for the day one gets through anyway.

Next: back to [[cybersecurity/index|the cybersecurity course]] for the organisational side, or [[using-ai/index|using AI]] for the vault's other non-technical course.

## Related
<!-- bite: 7ac1e098-2adc-4b0e-aede-d756369dbc86 -->

- [[cybersecurity/10-protecting-yourself/index|The protecting-yourself track]] — the whole list.
- [[cybersecurity/10-protecting-yourself/06-backups-and-your-data|Backups]] — what makes device and ransomware recovery possible.
- [[cybersecurity/07-security-operations/04-incident-response|Incident response]] — the organisational version of this checklist.

## About this lesson
<!-- bite: b80a6cb5-5bfa-4eb7-a0ae-e158a4ee2534 -->

**Level:** Beginner (no code). **Covers:** the ordered checklist for a compromised account (email first, sign out sessions, check recovery settings), money fraud and SIM swap, a compromised device and ransomware, sextortion and the webcam bluff, and helping someone else, with a make-your-own-plan task. **Where it sits:** lesson 8 of the [[cybersecurity/10-protecting-yourself/index|Protecting Yourself]] section, the last of it — read before you need it. **Sources:** the original vault note, rebuilt to the [[COURSE-STANDARD|course standard]] with quizzes and a personal task; written for the non-technical reader.
