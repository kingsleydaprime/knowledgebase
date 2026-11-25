---
id: 33ea81d3-0ca0-4a91-9172-31dc9bee1844
---

# Lateral Movement and Escalation

**Lateral movement spreads sideways between machines; escalation climbs to more powerful accounts — interleaved until the attacker owns the domain.**

## Before you start
<!-- bite: cc921647-78f5-450b-9994-fbd234fe6046 -->

You should have:

- Credentials or hashes harvested from the domain → [[cybersecurity/12-active-directory/04-credential-attacks|credential attacks]].
- The attack paths BloodHound drew for you → [[cybersecurity/12-active-directory/03-enumeration|enumeration]].
- Why KRBTGT's hash is the master key → [[cybersecurity/12-active-directory/02-authentication-and-kerberos|authentication and Kerberos]].

After this lesson you will be able to:

1. Name the remote-execution methods (PsExec, WMI, WinRM…) and say why they blend into normal admin traffic.
2. Explain the named escalations — DCSync, Golden/Silver Tickets, ACL abuse, delegation, ADCS — as abuses of legitimate features.
3. Trace the full kill chain from one foothold to Domain Admin and persistence.

**Study route.** Read the kid version and lateral movement, then study the named attacks — these are the BloodHound edges made real. The practice task walks one path end to end on your lab.

## What lateral movement and escalation are
<!-- bite: ea2dd396-e1d3-47cc-b160-245ed9d0e57d -->

Once you have a credential, lateral movement spends it: you use it to execute code on *other* machines, spreading sideways across the network with the same remote-administration protocols real admins use. Escalation is the vertical move — turning a foothold account into a more powerful one by abusing a misconfiguration. They interleave: move to a machine, harvest a better credential, escalate, move somewhere better, until you reach Domain Admin or the Domain Controller itself. Every named attack in this lesson is one of the BloodHound edges from enumeration, made real.

## The kid version
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

## Why lateral movement is hard to catch
<!-- bite: ea761889-e4dc-4196-b077-c284b1d4660d -->

**These are the same tools admins use.** That's the point — lateral movement blends into normal administrative traffic, which is why it evades signature detection and why [[cybersecurity/12-active-directory/06-defending-active-directory|defenders]] must watch for *patterns* (one account authenticating to twenty machines in a minute) rather than tools.

`nxc smb <range> -u user -H hash -x "command"` sprays a command across every host that accepts the credential — **this is how one hash becomes fifty shells.**

## The named attacks: tickets and replication
<!-- bite: 3cddb71f-33fd-47b8-adfc-a70a29945068 -->

These are the BloodHound edges made real. The first family abuses Kerberos trust and replication; in rough order of how you'll meet them:

**DCSync — steal every hash without touching the DC's disk.**
Any account with the **replication rights** (`DS-Replication-Get-Changes`) — Domain Admins have them, but so do surprisingly many delegated accounts — can *ask a DC to replicate password data*, which is a legitimate DC-to-DC operation. You get every account's hash, **including KRBTGT's**:

```text
secretsdump.py -just-dc corp.local/admin@10.0.0.1
mimikatz # lsadump::dcsync /domain:corp.local /user:krbtgt
```

**Finding an account with replication rights that you can compromise is a top BloodHound win** — it hands you the whole domain database.

## Golden and Silver Tickets
<!-- bite: 0d86f304-1416-46fe-b758-fe765ad0bf3c -->

Both forge Kerberos tickets from a stolen hash; they differ in scope.

**Golden Ticket — forge any TGT, forever.**
With **KRBTGT's hash** (from DCSync), you forge a TGT for any user, including a fabricated Domain Admin. Because the TGT is encrypted with KRBTGT's key ([[cybersecurity/12-active-directory/02-authentication-and-kerberos|Kerberos]]), the KDC accepts it. **This is the ultimate persistence** — it survives password resets of every account *except KRBTGT*, and KRBTGT is almost never rotated:

```text
mimikatz # kerberos::golden /user:Administrator /domain:corp.local /sid:<domain-SID> /krbtgt:<hash> /ptt
```

**Silver Ticket — forge a ticket to one service.**
With a *service account's* hash, forge a service ticket to that one service. Narrower than Golden (one service, not the domain) but stealthier — **it never contacts the DC at all**, so the DC logs nothing.

## ACL abuse — the misconfiguration goldmine
<!-- bite: d38c991a-de3b-4b90-bbc9-d8e7905948ef -->

Dangerous rights over an object, which BloodHound surfaces, are the second family — and the most common real-world path, because over-generous permissions accumulate over years:

- **`GenericAll` / `WriteDACL`** over a user → reset their password, or grant yourself rights
- **`WriteDACL`** over a group → add yourself to it (e.g. into Domain Admins)
- **`GenericWrite`** over a user → set an SPN on them and Kerberoast (**targeted Kerberoasting**), or configure delegation
- **`Owns`** → change the object's ACL, then do any of the above

**These are pure misconfiguration** — nobody exploited a bug; the permissions were simply too generous.

## Delegation and certificate abuse
<!-- bite: 89907755-d791-4efe-bf40-295e8105e599 -->

The third family abuses two powerful, legitimate features.

**Delegation abuse.** Kerberos delegation lets a service act *on behalf of* a user (so a web app can reach a database as you). Misconfigured:
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

Every lesson in this section is one stage of a single chain, from one credential to the whole domain:

![The Active Directory attack kill chain in seven stages: foothold from one credential, enumerate with BloodHound to find the shortest path to Domain Admin, harvest credentials by Kerberoasting and running mimikatz on owned boxes, move laterally by pass-the-hash, escalate through ACL abuse, delegation, ADCS or DCSync, reach Domain Admin by DCSyncing KRBTGT and forging a Golden Ticket, then persist — and on an engagement, document every step.](../images/ad-kill-chain.svg)

## Key insight
<!-- bite: 5e157a5c-7037-45fe-a9bc-cba3f17d22f7 -->

**Escalation in AD is a chain of legitimate features abused with harvested credentials — DCSync is a real replication operation, Golden Tickets exploit real Kerberos trust, ACL and delegation abuse exploit real (over-generous) permissions.** The DC is usually patched; the domain falls through misconfiguration and credential reuse anyway. The single most important target is KRBTGT's hash, because it forges tickets forever — which is why the endgame is always DCSync, and why recovering from it is so painful for defenders.

## Terms used in this lesson
<!-- bite: a0e76322-091b-476b-b9d1-03edb0f2fbf5 -->

1. **Lateral movement**: Using a credential from one machine to execute code on another, spreading sideways across the network.
2. **DCSync**: Asking a Domain Controller to replicate password data — a legitimate DC-to-DC operation — to dump every account's hash, including KRBTGT's. Needs replication rights.
3. **Golden Ticket**: A TGT forged with KRBTGT's hash. It authenticates as anyone and survives password resets of every account except KRBTGT, so it's the ultimate persistence.
4. **Silver Ticket**: A service ticket forged with a service account's hash. Narrower than a Golden Ticket (one service) but stealthier — it never contacts the DC.
5. **ACL abuse**: Exploiting dangerous rights (`GenericAll`, `WriteDACL`, `GenericWrite`, `Owns`) over an object to reset passwords, add yourself to groups, or grant yourself rights.

## Terms used in this lesson: delegation and persistence
<!-- bite: b2f6ce42-6858-4598-90c3-8982b6b15ec5 -->

6. **Delegation abuse**: Exploiting Kerberos delegation (unconstrained, constrained, or RBCD) to impersonate a user — often a Domain Admin — to a service.
7. **RBCD (Resource-Based Constrained Delegation)**: A modern delegation escalation: abuse `GenericWrite` over a computer object to configure delegation to it and impersonate any user to its services.
8. **ADCS abuse (ESC1–ESC16)**: Exploiting misconfigured Active Directory Certificate Services templates to request a certificate that authenticates as a Domain Admin. `certipy find` enumerates vulnerable templates.
9. **PetitPotam / printer bug**: Coercion techniques that force a machine (even a DC's computer account) to authenticate to a server you control, feeding delegation attacks.
10. **DCShadow / Skeleton Key**: Persistence techniques — registering a rogue DC to push changes, or patching LSASS on a DC to accept a master password.

## Check your understanding
<!-- bite: 316ba05d-9119-464e-b718-440d44dbd253 -->

Try each one before you open the answer.

1. <!-- q: mcq id="8e2e5c95" -->
   DCSync lets an attacker dump every account's hash. Why is it so hard to distinguish from legitimate activity?

   - [ ] It encrypts the DC's disk first.
   - [x] It uses the normal DC-to-DC replication protocol, so to the DC it looks like another controller syncing password data.
   - [ ] It only runs at night.
   - [ ] It deletes the security logs as it goes.

   <details><summary>Answer</summary>

   DCSync asks a DC to replicate password data — exactly what controllers do with each other. Any account holding replication rights (`DS-Replication-Get-Changes`) can request it. Detection has to flag replication coming from a *non-DC* (event 4662), because the operation itself is legitimate.

   </details>

2. <!-- q: mcq id="53dcc54e" -->
   Why is a Golden Ticket called "the ultimate persistence"?

   - [ ] It can never be detected by any tool.
   - [x] It's forged with KRBTGT's hash, which is almost never rotated, so it keeps working even after every other account's password is reset.
   - [ ] It gives physical access to the server room.
   - [ ] It disables Kerberos entirely.

   <details><summary>Answer</summary>

   A Golden Ticket is a TGT encrypted with KRBTGT's key, so the KDC accepts it for any user. Because recovering from KRBTGT compromise requires rotating its password *twice* and organisations rarely do, the forged ticket survives a full password-reset response. That's why keeping attackers away from KRBTGT (DCSync) matters so much.

   </details>

3. <!-- q: gap id="d3333b29" answers="misconfiguration|misconfig" -->
   The lesson stresses that the DC is usually fully patched and the domain falls anyway. The thing it actually falls through — over-generous permissions, weak service passwords, excessive delegation — is ___, not an unpatched vulnerability.

   <details><summary>Answer</summary>

   Misconfiguration. AD escalation is overwhelmingly about how the domain is *configured*, not about a CVE. DCSync, ACL abuse and delegation abuse are all legitimate features used against over-generous settings.

   </details>

4. <!-- q: mcq id="f59f4d5e" -->
   You have `WriteDACL` over the Domain Admins group. What does that let you do most directly?

   - [ ] Read the Domain Admins' passwords in plaintext
   - [x] Modify the group's permissions and add your own account to it
   - [ ] Forge a Golden Ticket
   - [ ] Shut down the Domain Controller

   <details><summary>Answer</summary>

   `WriteDACL` means you can rewrite the object's access control list — so you grant yourself the right to add members, then add your account to Domain Admins. This is pure ACL abuse, the most common real-world escalation path, and exactly the kind of edge BloodHound surfaces.

   </details>

5. <!-- q: open id="7ee809b3" -->
   A junior says "we patch our DCs religiously, so we're safe from these AD attacks." Explain why that misses the point.

   <details><summary>Answer</summary>

   Almost none of these attacks exploit an unpatched DC. DCSync is legitimate replication, Golden/Silver Tickets abuse normal Kerberos trust, ACL and delegation abuse exploit over-generous permissions, and Kerberoasting cracks weak service passwords — all against a fully patched domain. The attack surface is *configuration and credentials*, not missing patches. Defence is tiering, least privilege, auditing ACLs and delegation, rotating KRBTGT, and behavioural detection — not just patching.

   </details>

## Practice — walk one path to Domain Admin
<!-- bite: 4869508f-332e-4fa3-9bc5-fe74d558ab30 -->

Take the shortest path BloodHound drew on your lab and execute it end to end.

- Follow the edges in order: use each credential to move or escalate (`nxc`, `evil-winrm`, `psexec.py`, or an ACL abuse with `bloodyAD`/PowerView).
- When you reach replication rights, DCSync KRBTGT: `secretsdump.py -just-dc-user krbtgt corp.local/admin@<DC-IP>`.
- Forge a Golden Ticket with the recovered KRBTGT hash and use it to access the DC.
- Keep a numbered log of every command and what it gave you — that log *is* the engagement report → [[cybersecurity/02-ethical-hacking/09-post-exploitation-and-reporting|post-exploitation and reporting]].
- **Done when:** you've gone from your foothold account to Domain Admin on the lab, and your log reads back as a clean kill chain.

## Before moving on
<!-- bite: b80dc9f3-77d2-4951-8af5-a8813f37dea3 -->

You should be able to name the remote-execution methods, explain each named escalation as an abused legitimate feature, and trace the whole chain from one credential to KRBTGT. One idea ties it together: the DC is patched; the domain falls through misconfiguration and credential reuse. That's the bridge to the last lesson.

Next: [[cybersecurity/12-active-directory/06-defending-active-directory|defending Active Directory]] — the blue-team mirror, where every attack you just ran has a specific defence.

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
