# Protecting Yourself

**This is the personal-security course for someone who doesn't work in security and doesn't write code: eight short lessons about protecting your own accounts, devices and money.**

Everything else in [[cybersecurity/index|cybersecurity/]] is written for someone defending an organisation — SIEMs, threat hunting, penetration testing, compliance. Useful, and not what you need at 11pm when a text says your bank account is suspended. This section is the other audience: you, your family, and the people who ring you when something goes wrong. No jargon that isn't defined on the spot, no code, and honest about which advice is oversold.

## What you'll be able to do

By the end of this section you will be able to:

- write a realistic threat model and know which advice actually applies to you;
- set up a password manager and real two-factor so a stolen password opens nothing;
- recognise phishing and scams, and secure your devices, Wi-Fi and backups;
- run the right ordered checklist the day something gets through anyway.

## The six things

**If you do nothing else, do these.** Ranked by harm prevented per hour, and together about a weekend:

| # | Do this | Why |
|---|---|---|
| 1 | **Password manager, stop reusing** | Kills credential stuffing, the commonest compromise there is |
| 2 | **Real 2FA on email and banking** | Kills stolen-password attacks |
| 3 | **Turn on automatic updates** | Kills most malware. One click |
| 4 | **Learn the phishing tells** | The commonest way people lose money |
| 5 | **A backup you have tested** | The only defence against ransomware and loss |
| 6 | **Lock your phone, encrypt your laptop** | Makes theft a hardware loss, not a data loss |

**And the single most important framing:** your primary email is the master key — password resets for everything else land there. Protect it more carefully than your bank.

## Reading order

Read **01** first — it tells you which of the rest matter for you. After that **02, 03 and 04 are load-bearing**; the rest can be read in any order.

1. [[cybersecurity/10-protecting-yourself/01-your-actual-threat-model|01 — Your Actual Threat Model]] — **[Beginner]** — who's realistically after you (almost never you specifically), who genuinely is targeted, the six things ranked, and what isn't worth your time.
2. [[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager|02 — Passwords, and the Manager]] — **[Beginner, load-bearing]** — reuse, not strength, is the whole problem; which manager, the master passphrase, the "one basket" objection, and lying on security questions.
3. [[cybersecurity/10-protecting-yourself/03-two-factor-and-passkeys|03 — Two-Factor and Passkeys]] — **[Beginner]** — why SMS is weakest, SIM swap, why passkeys are categorically better, and the backup codes everyone skips.
4. [[cybersecurity/10-protecting-yourself/04-phishing-and-scams|04 — Phishing and Scams]] — **[Beginner, load-bearing]** — the tells (and the two AI killed), BEC, romance and investment fraud, and the two habits that stop nearly all of it.
5. [[cybersecurity/10-protecting-yourself/05-your-devices-and-networks|05 — Your Devices and Networks]] — **[Beginner]** — updates and encryption, app permissions, home Wi-Fi, and an honest answer about VPNs.
6. [[cybersecurity/10-protecting-yourself/06-backups-and-your-data|06 — Backups and Your Data]] — **[Beginner]** — 3-2-1, why sync is not backup, and the ten-minute restore test nobody does.
7. [[cybersecurity/10-protecting-yourself/07-your-privacy-footprint|07 — Your Privacy Footprint]] — **[Beginner]** — why privacy is a security problem, email aliases, and what's worth doing versus what's sold to you.
8. [[cybersecurity/10-protecting-yourself/08-when-it-goes-wrong|08 — When It Goes Wrong]] — **[Beginner]** — the checklist, in order. Read it before you need it.

## If you only take three things

1. **Every account gets a different password**, because the attack that reaches you is a list from someone else's breach ([[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager|02]]).
2. **Never act from a link in a message** — open the app, or type the address yourself ([[cybersecurity/10-protecting-yourself/04-phishing-and-scams|04]]).
3. **Nobody legitimate will ever ask you for a code that was sent to you** ([[cybersecurity/10-protecting-yourself/03-two-factor-and-passkeys|03]]).

## One note on the hardest case

If you're worried about someone who **knows you personally** — an ex-partner, a family member, someone who has had physical access to your devices — the advice here can backfire. Changing a password can alert them and escalate things. Domestic-violence support organisations have specialists for exactly this; **talk to them before changing anything.** A general guide is not adequate there, and this one isn't pretending to be.

## If you're the person people call

Most technical people end up as family IT support. Two things that work better than explaining:

- **Set the six things up *for* them.** Doing beats teaching.
- **Give one rule they'll remember:** *"If it's urgent and about money, hang up and call me."* Then **agree a family code word** for verifying urgent calls — AI voice cloning has made this genuinely necessary.

## Related

- [[cybersecurity/index|The cybersecurity course]] — sections 01–09, written for defending organisations.
- [[using-ai/index|Using AI]] — the vault's other course for non-technical readers.
- [[cybersecurity/06-attacks-and-threats/01-social-engineering|Social engineering]] — the professional treatment of lesson 04.

## About this section

**How it's built:** eight no-code lessons for the non-technical reader, each brought to the [[COURSE-STANDARD|course standard]] with a plain definition, a kid version, numbered terms, a tagged quiz, and a *personal* practice task (set up a manager, turn on 2FA, test a restore) in place of a code lab. Four flows (credential stuffing, SIM swap, sync-is-not-backup, privacy-to-breach) are drawn as `ps-*.svg` diagrams. Written in the shape of [[using-ai/index|using-ai]]: honest about which advice is oversold.
