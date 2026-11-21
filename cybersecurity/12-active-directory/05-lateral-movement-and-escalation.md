---
id: 33ea81d3-0ca0-4a91-9172-31dc9bee1844
---

# Lateral Movement and Escalation

Lateral movement is using login details from one computer to get into another on the same network. Escalation is climbing from a normal account to a more powerful one. An attacker usually does both in turns until they control the whole network.

## The kid version first
<!-- bite: b37e1113-1d00-4ebe-9232-6b8782543f89 -->

**Lateral movement** is using credentials from one machine to log into another — spreading sideways across the network. **Escalation** is climbing from a normal account to a powerful one. They interleave: you move to a machine, harvest better credentials, use them to move somewhere better, until you reach a Domain Admin or the Domain Controller itself.

## Lateral movement — the techniques
<!-- bite: d3f03dc2-06d9-4c46-a968-41a83dfda4cd -->

Once you have valid credentials (or a hash, or a ticket), you execute code on other machines using **legitimate Windows remote-administration protocols**:

| Method | Protocol | Notes |
|---|---|---|
| **PsExec** | SMB + service creation | Classic, noisy, drops a service. impacket's `psexec.py` |
| **WMI** | WMI/RPC | Quieter; `wmiexec.py`. Common |
| **WinRM** | WinRM (5985/5986) | `evil-winrm`; clean shells if you have the right |
| **DCOM** | DCOM | Alternative when others are blocked |
| **RDP** | RDP | Interactive; leaves the most traces |
| **SMB exec** | SMB | `smbexec.py` |

**These are the same tools admins use.** That's the point — lateral movement blends into normal administrative traffic, which is why it evades signature detection and why [[cybersecurity/12-active-directory/06-defending-active-directory|defenders]] must watch for *patterns* (one account authenticating to twenty machines in a minute) rather than tools.

`nxc smb <range> -u user -H hash -x "command"` sprays a command across every host that accepts the credential — **this is how one hash becomes fifty shells.**

## The escalation techniques — the named attacks
<!-- bite: 3cddb71f-33fd-47b8-adfc-a70a29945068 -->

These are the BloodHound edges made real. In rough order of how you'll meet them:

**DCSync — steal every hash without touching the DC's disk.**
Any account with the **replication rights** (`DS-Replication-Get-Changes`) — Domain Admins have them, but so do surprisingly many delegated accounts — can *ask a DC to replicate password data*, which is a legitimate DC-to-DC operation. You get every account's hash, **including KRBTGT's**:

```text
secretsdump.py -just-dc corp.local/admin@10.0.0.1
mimikatz # lsadump::dcsync /domain:corp.local /user:krbtgt
```

**Finding an account with replication rights that you can compromise is a top BloodHound win** — it hands you the whole domain database.

**Golden Ticket — forge any TGT, forever.**
With **KRBTGT's hash** (from DCSync), you forge a TGT for any user, including a fabricated Domain Admin. Because the TGT is encrypted with KRBTGT's key ([[cybersecurity/12-active-directory/02-authentication-and-kerberos|Kerberos]]), the KDC accepts it. **This is the ultimate persistence** — it survives password resets of every account *except KRBTGT*, and KRBTGT is almost never rotated:

```text
mimikatz # kerberos::golden /user:Administrator /domain:corp.local /sid:<domain-SID> /krbtgt:<hash> /ptt
```

**Silver Ticket — forge a ticket to one service.**
With a *service account's* hash, forge a service ticket to that one service. Narrower than Golden (one service, not the domain) but stealthier — **it never contacts the DC at all**, so the DC logs nothing.

**ACL abuse — the misconfiguration goldmine.**
Dangerous rights over an object, which BloodHound surfaces:
- **`GenericAll` / `WriteDACL`** over a user → reset their password, or grant yourself rights
- **`WriteDACL`** over a group → add yourself to it (e.g. into Domain Admins)
- **`GenericWrite`** over a user → set an SPN on them and Kerberoast (**targeted Kerberoasting**), or configure delegation
- **`Owns`** → change the object's ACL, then do any of the above

**These are pure misconfiguration** — over-generous delegated permissions accumulated over years — and they're the most common real-world path.

**Delegation abuse.**
Kerberos delegation lets a service act *on behalf of* a user (so a web app can reach a database as you). Misconfigured:
- **Unconstrained delegation** — a server so configured caches the TGT of *anyone who connects*. Get admin on it, coerce a Domain Admin (or a DC's computer account, via the **printer bug / PetitPotam**) to authenticate to it, and steal their TGT
- **Constrained / RBCD (Resource-Based Constrained Delegation)** — abuse `GenericWrite` over a computer object to configure delegation *to* it and impersonate any user to its services. **A very common modern escalation**

**Certificate abuse (ADCS).**
If the org runs Active Directory Certificate Services, misconfigured certificate templates (the **ESC1–ESC16** family) let a low-priv user **request a certificate that authenticates as a Domain Admin**. `certipy find` enumerates vulnerable templates. **One of the most impactful modern AD attack surfaces**, and frequently present.

## Persistence
<!-- bite: 7ee02cfc-985d-4414-b764-706a4eb58a8b -->

Once you own the domain, staying in:
- **Golden Ticket** (above) — the classic
- **DCShadow** — register a rogue DC and push malicious changes
- **AdminSDHolder / ACL backdoors** — grant yourself rights that survive cleanup
- **Skeleton Key** — patch LSASS on a DC to accept a master password

**The defensive implication is grim:** true recovery from KRBTGT compromise requires rotating the KRBTGT password *twice* and often rebuilding trust — which is why "assume breach" and monitoring matter more than any single control → [[cybersecurity/12-active-directory/06-defending-active-directory|defending AD]].

## The full kill chain
<!-- bite: f8cd4b52-4e5a-4245-ba80-039a6a774ec0 -->

```text
1. foothold      one credential (spray / phish / Responder)
2. enumerate     BloodHound → shortest path to DA
3. harvest       Kerberoast; mimikatz on owned boxes
4. move          pass-the-hash across machines with nxc/psexec
5. escalate      ACL abuse / delegation / ADCS / DCSync
6. domain admin  DCSync KRBTGT → Golden Ticket
7. persist       and, on an engagement, DOCUMENT every step
```

## Key insight
<!-- bite: 5e157a5c-7037-45fe-a9bc-cba3f17d22f7 -->

**Escalation in AD is a chain of legitimate features abused with harvested credentials — DCSync is a real replication operation, Golden Tickets exploit real Kerberos trust, ACL and delegation abuse exploit real (over-generous) permissions.** The DC is usually patched; the domain falls through misconfiguration and credential reuse anyway. The single most important target is KRBTGT's hash, because it forges tickets forever — which is why the endgame is always DCSync, and why recovering from it is so painful for defenders.

## Related
<!-- bite: 0b3877e9-d39c-4bc3-a5eb-25803f390b06 -->
- [[cybersecurity/12-active-directory/04-credential-attacks|credential attacks]] — how you get the credentials this spends
- [[cybersecurity/12-active-directory/03-enumeration|enumeration]] — BloodHound draws these paths
- [[cybersecurity/12-active-directory/06-defending-active-directory|defending AD]] — how each is detected and prevented
- [[cybersecurity/02-ethical-hacking/09-post-exploitation-and-reporting|post-exploitation and reporting]]

## About this lesson
<!-- bite: bc47eca1-b3bf-4625-832b-bfd839877502 -->

**Level:** Advanced. **Covers:** moving from one machine to the next, and from a foothold to owning the domain.

*Source: [reference] — Aug 2026. Authorised-testing / lab material.*
