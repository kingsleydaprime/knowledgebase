---
id: f85a70ab-a499-407b-a01d-8742c10eeacd
---

# When It Goes Wrong

This lesson is a checklist for when something has already gone wrong: an account taken over, money sent to a scammer, or a device lost. The steps are in order, because the order matters when time is short. Read it now, before you need it.

## Read this before you need it
<!-- bite: fe52f48a-7da9-4406-b1b0-2e74578ceac6 -->

You will not think clearly during. **The value here is the ordering** — do these in sequence, because doing them out of order wastes the window when it matters.

**And the first rule: don't freeze from embarrassment.** Being scammed says nothing about your intelligence; the operations are professional and designed by people who do this full time. **Silence is what turns a recoverable incident into an unrecoverable one.**

## An account was compromised — the order matters
<!-- bite: fcedd9ca-3273-40e7-8e67-a6c0f633bca6 -->

**1. Start with your email. Always.**
Even if the compromised account is something else. **Your email resets everything else**, so if it's also compromised, fixing anything downstream is pointless.

**2. Change the password** — from a device you trust, to something unique.

**3. Sign out all other sessions.**
Every major service has this ("Security → Active sessions → Sign out everywhere"). **A password change alone often doesn't kick out an existing session**, so skipping this leaves the attacker logged in.

**4. Check recovery settings — the step people miss.**
Attackers add *their own* recovery email, phone number, or backup 2FA so they can walk back in later. **Check and remove anything you don't recognise:**
- Recovery email and phone
- **Email forwarding rules and filters** — a classic move is a rule silently forwarding your mail, or auto-deleting bank alerts so you don't notice fraud
- Authorised apps and connected accounts
- App passwords / API keys

**5. Enable or re-enable 2FA**, ideally a passkey or app rather than SMS → [[cybersecurity/10-protecting-yourself/03-two-factor-and-passkeys|03]].

**6. Now work outward.** Every account that used that password, and every account that resets *through* that email. Prioritise money and identity.

**7. Look at what they did.** Sent messages, changed settings, new payment methods, orders. **Warn anyone they messaged from your account.**

## Money
<!-- bite: c1df9eb7-7a7a-4ed3-9855-72e0e6bfac23 -->

**Card fraud:** call the bank, freeze the card, dispute the charges. Report fast — protections are strongest early. **Then check for a small test charge before the big one**, which tells you when the details leaked.

**Bank transfer you were tricked into:** **call your bank immediately.** Same-day recall sometimes works and the window is hours. In the UK, reimbursement rules for authorised push-payment fraud have strengthened — **ask explicitly about APP fraud reimbursement**, and don't accept the first refusal.

**Crypto:** be blunt with yourself — it is **almost always unrecoverable** → [[web3/08-the-honest-assessment/02-scams-rugs-and-the-fraud-surface|the fraud surface]]. Report it anyway. **And be ready for the recovery scam**, which will find you next.

**Then:** report it (Action Fraud UK, IC3/FTC US, your national equivalent), and check your credit report for accounts opened in your name. **Consider a credit freeze** — free, and it stops new credit being taken out.

## SIM swap
<!-- bite: 9d86974a-ef8c-4231-b662-19580a6d2b1d -->

**Signs:** your phone loses service for no reason; you get an unexpected "your number has been transferred" message.

**This is an emergency** — you have minutes, not hours.

1. **Contact your mobile network immediately** — from another phone
2. **From a different device, secure your email first**, then anything using SMS 2FA
3. Move recovery off SMS once restored, and **set a port-out PIN**

## A device is compromised
<!-- bite: 5afd23f6-ac80-40cc-8cf3-5d05f4246666 -->

Signs: it slowed dramatically, unfamiliar programs, browser redirects, contacts receiving messages you didn't send, or you gave someone remote access.

1. **Disconnect it from the network**
2. **From a *different, clean* device**, change your important passwords. **Not from the suspect machine** — a keylogger captures the new ones too
3. **Wipe and reinstall.** Cleaning tools are unreliable against anything serious; **a full reinstall is the only answer you can trust**
4. Restore data from a backup **predating** the problem → [[cybersecurity/10-protecting-yourself/06-backups-and-your-data|backups]]
5. Change passwords again afterwards

## Ransomware
<!-- bite: 113201a9-f33d-4448-95ee-68f98b9e624e -->

1. **Disconnect immediately** — it spreads to network drives and synced folders
2. **Don't pay** if you have any alternative. It funds the industry, and payment frequently doesn't restore the files
3. **Check [nomoreransom.org](https://www.nomoreransom.org)** — free decryptors exist for many strains
4. **Wipe, reinstall, restore from your offline backup**
5. Report it

## Sextortion and blackmail
<!-- bite: 109236a0-fb50-447e-ae0a-0b8569542553 -->

Increasingly common, and increasingly aimed at teenagers, where the consequences have been fatal.

- **Do not pay.** Payment marks you as a payer and the demands continue
- **Do not engage**
- **Screenshot everything**, then block
- **Report** to the platform and the police. In the UK, the Revenge Porn Helpline; in the US, NCMEC's Take It Down for minors
- **Tell someone.** The leverage is entirely the fear of exposure, and **it collapses the moment someone else knows**

**And the common bluff:** most "I recorded you through your webcam" emails have nothing. They quote an old breached password to seem credible. **Change that password and ignore the rest.**

## If you're helping someone else
<!-- bite: c153bafa-487d-4b2f-9c5f-2899622c3363 -->

- **Don't lead with judgement.** They're already humiliated, and shame is what stops people reporting in time
- **Take over the sequence** — they're panicking; you're not
- **Email first**, always
- **Watch for the follow-up scam.** Victims get contacted by "recovery services". There is no such thing
- **If a child is involved**, go to the platform and the police rather than handling it privately

## Afterwards
<!-- bite: 2aa0eb87-30b2-437c-b880-2b092b91a965 -->

Once it's stable, do the boring part: **the six things** → [[cybersecurity/10-protecting-yourself/01-your-actual-threat-model|threat model]]. Most repeat incidents happen because the incident got fixed and the cause didn't.

Write down what happened and how they got in. **That's a personal postmortem**, and it's the same discipline organisations use → [[cybersecurity/07-security-operations/04-incident-response|incident response]].

## Key insight
<!-- bite: 10884afa-7bab-4fed-a88f-97365f251af6 -->

**In an incident, sequence beats speed: email first, sign out all sessions, then check recovery settings** — because an attacker who keeps a forwarding rule or a recovery phone number keeps the account no matter how many times you change the password. Most people change the password, feel safe, and get compromised again a week later by the back door they never looked for.

## Related
<!-- bite: 6a338c88-7e68-4cf1-945a-51db0908c522 -->
- [[cybersecurity/10-protecting-yourself/index|the track]]
- [[cybersecurity/10-protecting-yourself/06-backups-and-your-data|backups]] — what makes recovery possible
- [[cybersecurity/07-security-operations/04-incident-response|incident response]] — the organisational version

## About this lesson
<!-- bite: 1aafeac7-3673-4be3-9e0f-244d5e941284 -->

**Level:** Beginner. **Covers:** the checklist, in order, for the moment it's already happened.
