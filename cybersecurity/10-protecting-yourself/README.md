# Protecting Yourself

**A course for someone who doesn't work in security — and doesn't write code.** Eight notes, readable in an evening, about protecting your own accounts, devices and money.

**Everything else in [[cybersecurity/README|cybersecurity/]] is written for someone defending an organisation** — SIEMs, threat hunting, penetration testing, compliance frameworks. Useful, and not what you need at 11pm when a text says your bank account is suspended. This folder is the other audience: **you, your family, and the people who ring you when something goes wrong.**

Written in the same shape as [[using-ai/README|using-ai/]] — no jargon that isn't defined on the spot, no code, and honest about which advice is oversold.

## The six things

**If you do nothing else, do these.** Ranked by harm prevented per hour spent, and together they're about a weekend:

| # | Do this | Why |
|---|---|---|
| 1 | **Password manager, stop reusing** | Kills credential stuffing, the most common compromise there is |
| 2 | **Real 2FA on email and banking** | Kills stolen-password attacks |
| 3 | **Turn on automatic updates** | Kills most malware. **One click** |
| 4 | **Learn the phishing tells** | The most common way people actually lose money |
| 5 | **A backup you have tested** | The only defence against ransomware and loss |
| 6 | **Lock your phone, encrypt your laptop** | Makes theft a hardware loss, not a data loss |

**And the single most important framing:** your primary email is the master key. Password resets for everything else land there. **Protect it more carefully than your bank.**

## Reading order

Read **01** first — it tells you which of the rest matter for you. After that, **02, 03 and 04 are the load-bearing ones**; the rest can be read in any order.

1. [[cybersecurity/10-protecting-yourself/01-your-actual-threat-model|your-actual-threat-model]] — **[Beginner]** — who's realistically after you (almost never *you* specifically), who genuinely is targeted, the six things ranked, and **what isn't worth your time**
2. [[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager|passwords-and-the-manager]] — **[Beginner, load-bearing]** — **reuse is the whole problem**, not strength. Which manager, the master passphrase, the "all eggs in one basket" objection answered, and why you should lie on security questions
3. [[cybersecurity/10-protecting-yourself/03-two-factor-and-passkeys|two-factor-and-passkeys]] — **[Beginner]** — why SMS is the weakest kind, SIM swap, **why passkeys are categorically better rather than incrementally**, and the backup codes everyone skips
4. [[cybersecurity/10-protecting-yourself/04-phishing-and-scams|phishing-and-scams]] — **[Beginner, load-bearing]** — the tells (and the two that AI has killed), BEC, romance and investment fraud, **and the two habits that stop nearly all of it**
5. [[cybersecurity/10-protecting-yourself/05-your-devices-and-networks|your-devices-and-networks]] — **[Beginner]** — updates and encryption, app permissions, home Wi-Fi, and **an honest answer about VPNs**
6. [[cybersecurity/10-protecting-yourself/06-backups-and-your-data|backups-and-your-data]] — **[Beginner]** — 3-2-1, **why sync is not backup**, and the ten-minute restore test nobody does
7. [[cybersecurity/10-protecting-yourself/07-your-privacy-footprint|your-privacy-footprint]] — **[Beginner]** — why privacy is a security problem, email aliases, what's worth doing and what's sold to you
8. [[cybersecurity/10-protecting-yourself/08-when-it-goes-wrong|when-it-goes-wrong]] — **[Beginner]** — **the checklist, in order.** Read it before you need it

## If you only take three things

1. **Every account gets a different password**, because the attack that reaches you is a list from someone else's breach ([[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager|02]]).
2. **Never act from a link in a message** — open the app, or type the address yourself ([[cybersecurity/10-protecting-yourself/04-phishing-and-scams|04]]).
3. **Nobody legitimate will ever ask you for a code that was sent to you** ([[cybersecurity/10-protecting-yourself/03-two-factor-and-passkeys|03]]).

## One note on the hardest case

If you're worried about someone who **knows you personally** — an ex-partner, a family member, someone who has had physical access to your devices — **the advice in this folder can backfire.** Changing a password can alert them and escalate the situation.

Domestic-violence support organisations have specialists for exactly this. **Talk to them before changing anything.** A general guide is not adequate there, and this one isn't pretending to be.

## If you're the person people call

Most technical people end up as family IT support. Two things that work better than explaining:

- **Set the six things up *for* them.** Doing beats teaching
- **Give one rule they'll remember:** *"If it's urgent and about money, hang up and call me."* Then **agree a family code word** for verifying urgent calls — AI voice cloning has made this genuinely necessary

## Related
- [[cybersecurity/README|the cybersecurity course]] — sections 01–09, written for defending organisations
- [[using-ai/README|using AI]] — the vault's other course for non-technical readers
- [[cybersecurity/06-attacks-and-threats/01-social-engineering|social engineering]] — the professional treatment of note 04
- [[web3/08-the-honest-assessment/02-scams-rugs-and-the-fraud-surface|the crypto fraud surface]] — the same discipline, where losses are irreversible
