---
id: 076ecf42-f404-46f7-89e0-d06686e3734c
---

# Defending Active Directory

**Defending Active Directory is the mirror of attacking it — and the one rule above all is to keep powerful accounts off ordinary machines.**

## Before you start
<!-- bite: 0559a3e3-cb2a-4b21-8692-feb59b801b2d -->

You should have:

- The attacks this mirrors → [[cybersecurity/12-active-directory/05-lateral-movement-and-escalation|lateral movement and escalation]] and [[cybersecurity/12-active-directory/04-credential-attacks|credential attacks]].
- The blue-team loop this plugs into → [[cybersecurity/07-security-operations/index|security operations]].

After this lesson you will be able to:

1. Explain tiering and why it's the single highest-impact AD control.
2. Map each named attack to the specific control that stops it (gMSA, LAPS, Credential Guard, KRBTGT rotation…).
3. Say why detection must be behavioural, and name two high-signal AD detections.

**Study route.** Read the kid version and tiering carefully — it's the one idea that matters most — then the countermeasure tables and detection. The practice task runs the attacker's own audit tools against your lab defensively.

## What defending AD is
<!-- bite: 4278b8f3-cf03-40c6-804e-e9c57aeca319 -->

Defending AD is the blue-team mirror of everything in this section. Every attack abuses a default, a misconfiguration, or a credential left where an attacker could reach it — so defence runs the mirror: turn off insecure defaults, remove over-generous permissions, keep powerful credentials off ordinary machines, and watch the graph for the paths attackers walk. Because every control is the answer to a specific attack, this lesson comes last: you can't see why a defence matters until you've seen the attack it blocks.

## The kid version
<!-- bite: e096e83d-06fe-4293-849f-004367f17d94 -->

Every attack in this folder abuses a *default*, a *misconfiguration*, or a *credential left where an attacker could reach it*. So defence is the mirror image: turn off insecure defaults, remove the over-generous permissions, keep powerful credentials off ordinary machines, and **watch the graph for the paths attackers walk.**

You cannot defend AD well without knowing how it's attacked — which is exactly why this note comes last.

## The single most important idea: tiering
<!-- bite: 9ff7ace0-ea6c-4289-88b4-80817e88e2c6 -->

**Powerful credentials must never touch machines an attacker can compromise.**

The whole engine of AD compromise is: attacker owns a workstation → a Domain Admin logged into it → mimikatz steals their credentials → domain over. **Break that chain and most attacks stall.**

Microsoft's answer is the **tiered administration model**, which splits the estate into three layers and forbids a higher tier's credentials from ever being used on a lower one.

## The three tiers
<!-- bite: 1ca0847e-8ee8-48bc-ba18-22e781ae6363 -->

![Microsoft's tiered administration model as three stacked layers: Tier 0 at the top holds the Domain Controllers, Active Directory and KRBTGT — the crown jewels; Tier 1 holds servers and applications; Tier 2 holds workstations; a Tier 0 admin credential is used only on Tier 0 systems, so compromising a workstation never exposes a Domain Admin credential.](../images/ad-tiering.svg)

**The rule: a Tier 0 admin credential is used ONLY on Tier 0 systems.** A Domain Admin never logs into a workstation or a regular server — so even if that machine is owned, there's no DA credential in its memory to steal.

**This is the highest-impact control by far**, and the hardest to implement because it changes how admins work. Most breached organisations had Domain Admins logging into everything.

## Countering each attack
<!-- bite: 9568be5f-69a3-4e85-afff-41810abf01aa -->

Each control is the answer to a specific attack — that's how they make sense. First, the credential and ticket attacks:

| Attack | Defence |
|---|---|
| **Kerberoasting** | **Managed Service Accounts (gMSA)** — 120-char auto-rotated passwords, uncrackable. Where you must use a human service account, give it a long random password |
| **AS-REP roasting** | Don't disable Kerberos pre-auth. Audit for accounts that have it disabled |
| **Pass-the-hash** | **LAPS** — unique random local admin password per machine, so one hash owns one box, not the fleet. Tiering. Disable NTLM where possible |
| **mimikatz / LSASS** | **Credential Guard** (virtualisation-isolated LSASS), EDR, disable WDigest, tiering so there's nothing worth stealing |
| **Golden Ticket** | **Rotate KRBTGT** periodically (twice, correctly). Monitor for anomalous TGT lifetimes |

## Countering each attack: replication, ACLs and the network
<!-- bite: de7d4b22-e8bf-47a6-86e9-3d8e9f183b86 -->

Then the replication, permission and network attacks:

| Attack | Defence |
|---|---|
| **DCSync** | Audit who has replication rights — it should be *only* DCs and DAs. Alert on replication from a non-DC |
| **ACL abuse** | Audit ACLs (BloodHound *defensively*), remove accumulated over-delegation, protect privileged groups with AdminSDHolder |
| **Delegation abuse** | Mark Tier 0 accounts "sensitive, cannot be delegated." Audit unconstrained delegation — there should be almost none. Patch the coercion bugs (PetitPotam) |
| **ADCS (ESC1–16)** | Audit templates with `certipy`; fix enrollment permissions and SAN settings |
| **Responder / NTLM relay** | Disable LLMNR/NBT-NS. **Enforce SMB signing.** Enforce LDAP signing/channel binding |

**Notice the pattern: run the attacker's own tools against yourself.** BloodHound, `certipy`, `nxc` and PingCastle are blue-team tools too — they find the paths before an attacker does.

## Detection — because prevention is never complete
<!-- bite: adec175e-5e00-4a51-b553-d240c1c354d1 -->

Enumeration and lateral movement use legitimate protocols ([[cybersecurity/12-active-directory/03-enumeration|03]]), so detection is **behavioural, not signature-based** → [[cybersecurity/07-security-operations/index|security operations]]:

- **The right event IDs** — 4768/4769 (Kerberos tickets, for roasting), 4662 (DCSync-shaped replication), 4728/4732 (privileged group changes), 4624 with anomalous logon patterns
- **Honeytokens** — a fake service account with an SPN and a tempting name. **Nobody legitimate ever requests its ticket, so a 4769 for it is a near-certain Kerberoast alert.** Cheap, high-signal, and one of the best AD detections available
- **Behavioural baselines** — one account authenticating to twenty machines, a workstation querying every ACL, a TGT with a ten-year lifetime. **Microsoft Defender for Identity and similar watch for exactly these patterns**
- **The BloodHound query, run by defenders** — "what's the shortest path to DA?" is a *remediation backlog*, not just an attack plan

## The hard truth about recovery
<!-- bite: 9994d7c6-e5f4-4068-89b7-879016ec8d2c -->

**Assume breach.** A determined attacker with a foothold and time will usually find *a* path in a large AD environment, because the misconfigurations accumulate over decades. So the goal isn't a perfect wall — it's:

1. **Raise the cost** — tiering, gMSA, LAPS, removed delegation make the easy paths disappear
2. **Detect fast** — behavioural monitoring and honeytokens catch the attacker mid-chain
3. **Recover credibly** — and know that **KRBTGT compromise is genuinely hard to recover from** (double rotation, and forest-wide trust considerations), which is why keeping attackers away from Tier 0 is worth so much

## Where cloud changes the picture
<!-- bite: 8bbf51f4-8d09-47ae-b27a-6a9e807435fd -->

**Azure AD / Entra ID** is a different model (OAuth, conditional access, no Kerberos), and hybrid environments — on-prem AD synced to Entra — introduce their own attack paths (**Azure AD Connect** compromise, PRT theft, illicit consent grants). **Hybrid is now the common case**, and it means an on-prem compromise can pivot to the cloud tenant and vice versa → [[cybersecurity/09-cloud-security/index|cloud security]].

## Key insight
<!-- bite: e094a16c-6285-4931-961f-988689213538 -->

**Every AD defence is the mirror of a specific attack, which is why you can't defend it without understanding the offence** — tiering kills credential theft, gMSA kills Kerberoasting, LAPS kills hash reuse, honeytokens catch roasting for free. The defining reality is that prevention is never complete in a decades-old domain, so the winning strategy is: make the easy paths vanish, watch behaviourally for the attacker walking the hard ones, and keep the KRBTGT-grade credentials on Tier 0 machines an attacker can't reach.

## Terms used in this lesson
<!-- bite: 138eec9c-fb4f-43f7-9d24-f55a3a390c83 -->

1. **Tiering (tiered administration)**: Splitting the estate into Tier 0 (DCs, AD, KRBTGT), Tier 1 (servers) and Tier 2 (workstations), and never using a higher tier's credentials on a lower tier. The highest-impact AD control.
2. **gMSA (group Managed Service Account)**: A service account whose 120-character password AD rotates automatically, making it uncrackable — the fix for Kerberoasting.
3. **LAPS (Local Administrator Password Solution)**: A tool that gives every machine a unique random local-admin password, so one stolen hash owns one box, not the fleet — the fix for pass-the-hash reuse.
4. **Credential Guard**: A Windows feature that isolates LSASS in a virtualised container so mimikatz can't read credentials from it.

## Terms used in this lesson: detection and recovery
<!-- bite: d7967e31-e0f1-41c9-b6d6-756044f2c6fa -->

5. **KRBTGT rotation**: Changing the KRBTGT password (twice, correctly) to invalidate forged Golden Tickets. Rarely done, which is why Golden Tickets persist.
6. **Honeytoken**: A fake, tempting account (for example a service account with an SPN) that nobody legitimate ever uses, so any request for its ticket is a near-certain attack alert.
7. **AdminSDHolder**: An AD mechanism that re-applies a protected ACL to privileged groups, used to stop ACL backdoors on those groups.
8. **Entra ID (Azure AD)**: Microsoft's cloud identity service — a different model (OAuth, conditional access, no Kerberos). Hybrid setups let an on-prem compromise pivot to the cloud and back.

## Check your understanding
<!-- bite: a8f0eb01-fad6-40b3-942b-751e449c8af7 -->

Try each one before you open the answer.

1. <!-- q: mcq id="b3853a8a" -->
   Why is tiering described as the single highest-impact AD control?

   - [ ] It encrypts all network traffic.
   - [x] It keeps powerful credentials off machines an attacker can compromise, so owning a workstation never yields a Domain Admin credential to steal.
   - [ ] It automatically patches every Domain Controller.
   - [ ] It blocks all use of PowerShell.

   <details><summary>Answer</summary>

   The engine of AD compromise is: own a workstation → a DA was logged in → mimikatz steals their credential → domain over. Tiering forbids Tier 0 credentials on lower-tier machines, so even a fully owned workstation has no DA credential in memory. It breaks the chain at its root — which is also why it's the hardest control to implement, since it changes how admins work.

   </details>

2. <!-- q: mcq id="0f3a0ede" -->
   A honeytoken service account fires an alert. Why is it considered one of the best AD detections?

   - [ ] It automatically blocks the attacker's IP.
   - [x] Nobody legitimate ever requests its ticket, so a ticket request for it is a near-certain Kerberoast with almost no false positives.
   - [ ] It rotates its password every minute.
   - [ ] It can only be triggered by Domain Admins.

   <details><summary>Answer</summary>

   A honeytoken is a decoy account with a tempting SPN that no real service uses. Because no legitimate process ever asks for its service ticket, a single event 4769 for it is high-signal: an attacker enumerated SPNs and tried to Kerberoast. Cheap to deploy, almost no noise.

   </details>

3. <!-- q: gap id="1a9c4e7b" answers="gMSA|managed service account|managed service accounts" -->
   The clean fix for Kerberoasting is to replace human-set service-account passwords with a ___, whose 120-character password AD rotates automatically so it can't be cracked.

   <details><summary>Answer</summary>

   gMSA (group Managed Service Account). Its auto-rotated 120-character password is effectively uncrackable, which removes the weak-password condition Kerberoasting depends on.

   </details>

4. <!-- q: mcq id="2d7f6a41" -->
   Why must AD detection be "behavioural, not signature-based"?

   - [ ] Because attackers always use custom malware
   - [x] Because enumeration and lateral movement use legitimate LDAP, Kerberos and admin protocols, so you have to spot anomalous *patterns* rather than known-bad tools
   - [ ] Because signatures are too expensive to license
   - [ ] Because Domain Controllers can't run antivirus

   <details><summary>Answer</summary>

   The attacker lives off the land — LDAP queries, Kerberos tickets, WMI and PsExec are all normal admin activity. There's no malicious signature to match. Detection instead flags patterns: one account authenticating to twenty machines in a minute, a workstation querying every ACL, a TGT with a ten-year lifetime, replication from a non-DC.

   </details>

5. <!-- q: open id="3e8b2c56" -->
   Why is "assume breach" the honest posture for AD, and what three things follow from it?

   <details><summary>Answer</summary>

   In a decades-old domain the misconfigurations accumulate, so a determined attacker with a foothold and time will usually find *a* path — a perfect preventive wall isn't realistic. Three things follow: (1) **raise the cost** so the easy paths vanish — tiering, gMSA, LAPS, removed delegation; (2) **detect fast** — behavioural monitoring and honeytokens to catch the attacker mid-chain; and (3) **recover credibly**, knowing KRBTGT compromise is genuinely hard to undo (double rotation, forest-wide trust), which is exactly why keeping attackers away from Tier 0 is worth so much.

   </details>

## Practice — audit your own lab
<!-- bite: 50fddcf0-3720-40d2-b2c5-1fe702841167 -->

Run the attacker's tools defensively against your lab.

- Run **BloodHound** and read "Shortest Path to Domain Admins" as a *remediation backlog* — each edge is something to fix.
- Run **`certipy find`** for vulnerable ADCS templates and **PingCastle** for an overall hygiene score.
- Pick one path and *close* it: convert a weak service account to a gMSA, remove an over-generous ACL, or mark a Tier 0 account sensitive-and-not-delegable. Re-run BloodHound and confirm the path is gone.
- Plant a **honeytoken** service account and confirm a Kerberoast attempt against it shows up (event 4769).
- **Done when:** you've removed at least one BloodHound path on your lab and verified a honeytoken fires on a roast attempt.

## Before moving on
<!-- bite: d7451ade-5581-4e17-ad6f-cfd663e4da6b -->

You should be able to explain tiering as the top control, map each attack to its specific defence, say why detection is behavioural, and name honeytokens and KRBTGT rotation as high-value measures. That closes the loop: you've attacked AD and you've defended it.

This is the last lesson in the section. Next, step back to the [[cybersecurity/index|curriculum map]], or connect this to detection engineering in [[cybersecurity/07-security-operations/index|security operations]] and to the cloud identity model in [[cybersecurity/09-cloud-security/index|cloud security]].

## Related
<!-- bite: 81f09a32-ae2d-4505-b15b-c996a4d161ad -->
- [[cybersecurity/12-active-directory/05-lateral-movement-and-escalation|lateral movement]] — the attacks this counters
- [[cybersecurity/07-security-operations/index|security operations]] — SIEM, detection, incident response
- [[cybersecurity/09-cloud-security/index|cloud security]] — Entra ID and hybrid
- [[cybersecurity/08-governance-risk-and-compliance/index|governance and compliance]] — tiering as policy

## About this lesson
<!-- bite: e774944d-789d-4484-85ea-555ba0ad791a -->

**Level:** Advanced. **Covers:** the blue-team half, and why understanding the attacks is what makes the defence make sense.

*Source: [reference] — Aug 2026.*
