# Defending Active Directory

**[Advanced]** — the blue-team half, and why understanding the attacks is what makes the defence make sense.

## The kid version first

Every attack in this folder abuses a *default*, a *misconfiguration*, or a *credential left where an attacker could reach it*. So defence is the mirror image: turn off insecure defaults, remove the over-generous permissions, keep powerful credentials off ordinary machines, and **watch the graph for the paths attackers walk.**

You cannot defend AD well without knowing how it's attacked — which is exactly why this note comes last.

## The single most important idea: tiering

**Powerful credentials must never touch machines an attacker can compromise.**

The whole engine of AD compromise is: attacker owns a workstation → a Domain Admin logged into it → mimikatz steals their credentials → domain over. **Break that chain and most attacks stall.**

Microsoft's **tiered administration model**:

```
Tier 0   Domain Controllers, AD, KRBTGT — the crown jewels
Tier 1   Servers and applications
Tier 2   Workstations
```

**The rule: a Tier 0 admin credential is used ONLY on Tier 0 systems.** A Domain Admin never logs into a workstation or a regular server — so even if that machine is owned, there's no DA credential in its memory to steal.

**This is the highest-impact control by far**, and the hardest to implement because it changes how admins work. Most breached organisations had Domain Admins logging into everything.

## Countering each attack

Mapping defences to the attacks, because that's how they make sense:

| Attack | Defence |
|---|---|
| **Kerberoasting** | **Managed Service Accounts (gMSA)** — 120-char auto-rotated passwords, uncrackable. Where you must use a human service account, give it a long random password |
| **AS-REP roasting** | Don't disable Kerberos pre-auth. Audit for accounts that have it disabled |
| **Pass-the-hash** | **LAPS** — unique random local admin password per machine, so one hash owns one box, not the fleet. Tiering. Disable NTLM where possible |
| **mimikatz / LSASS** | **Credential Guard** (virtualisation-isolated LSASS), EDR, disable WDigest, tiering so there's nothing worth stealing |
| **DCSync** | Audit who has replication rights — it should be *only* DCs and DAs. Alert on replication from a non-DC |
| **Golden Ticket** | **Rotate KRBTGT** periodically (twice, correctly). Monitor for anomalous TGT lifetimes |
| **ACL abuse** | Audit ACLs (BloodHound *defensively*), remove accumulated over-delegation, protect privileged groups with AdminSDHolder |
| **Delegation abuse** | Mark Tier 0 accounts "sensitive, cannot be delegated." Audit unconstrained delegation — there should be almost none. Patch the coercion bugs (PetitPotam) |
| **ADCS (ESC1–16)** | Audit templates with `certipy`; fix enrollment permissions and SAN settings |
| **Responder / NTLM relay** | Disable LLMNR/NBT-NS. **Enforce SMB signing.** Enforce LDAP signing/channel binding |

**Notice the pattern: run the attacker's own tools against yourself.** BloodHound, `certipy`, `nxc` and PingCastle are blue-team tools too — they find the paths before an attacker does.

## Detection — because prevention is never complete

Enumeration and lateral movement use legitimate protocols ([[cybersecurity/12-active-directory/03-enumeration|03]]), so detection is **behavioural, not signature-based** → [[cybersecurity/07-security-operations/README|security operations]]:

- **The right event IDs** — 4768/4769 (Kerberos tickets, for roasting), 4662 (DCSync-shaped replication), 4728/4732 (privileged group changes), 4624 with anomalous logon patterns
- **Honeytokens** — a fake service account with an SPN and a tempting name. **Nobody legitimate ever requests its ticket, so a 4769 for it is a near-certain Kerberoast alert.** Cheap, high-signal, and one of the best AD detections available
- **Behavioural baselines** — one account authenticating to twenty machines, a workstation querying every ACL, a TGT with a ten-year lifetime. **Microsoft Defender for Identity and similar watch for exactly these patterns**
- **The BloodHound query, run by defenders** — "what's the shortest path to DA?" is a *remediation backlog*, not just an attack plan

## The hard truth about recovery

**Assume breach.** A determined attacker with a foothold and time will usually find *a* path in a large AD environment, because the misconfigurations accumulate over decades. So the goal isn't a perfect wall — it's:

1. **Raise the cost** — tiering, gMSA, LAPS, removed delegation make the easy paths disappear
2. **Detect fast** — behavioural monitoring and honeytokens catch the attacker mid-chain
3. **Recover credibly** — and know that **KRBTGT compromise is genuinely hard to recover from** (double rotation, and forest-wide trust considerations), which is why keeping attackers away from Tier 0 is worth so much

## Where cloud changes the picture

**Azure AD / Entra ID** is a different model (OAuth, conditional access, no Kerberos), and hybrid environments — on-prem AD synced to Entra — introduce their own attack paths (**Azure AD Connect** compromise, PRT theft, illicit consent grants). **Hybrid is now the common case**, and it means an on-prem compromise can pivot to the cloud tenant and vice versa → [[cybersecurity/09-cloud-security/README|cloud security]].

## Key insight

**Every AD defence is the mirror of a specific attack, which is why you can't defend it without understanding the offence** — tiering kills credential theft, gMSA kills Kerberoasting, LAPS kills hash reuse, honeytokens catch roasting for free. The defining reality is that prevention is never complete in a decades-old domain, so the winning strategy is: make the easy paths vanish, watch behaviourally for the attacker walking the hard ones, and keep the KRBTGT-grade credentials on Tier 0 machines an attacker can't reach.

## Related
- [[cybersecurity/12-active-directory/05-lateral-movement-and-escalation|lateral movement]] — the attacks this counters
- [[cybersecurity/07-security-operations/README|security operations]] — SIEM, detection, incident response
- [[cybersecurity/09-cloud-security/README|cloud security]] — Entra ID and hybrid
- [[cybersecurity/08-governance-risk-and-compliance/README|governance and compliance]] — tiering as policy

*Source: [reference] — Aug 2026.*
