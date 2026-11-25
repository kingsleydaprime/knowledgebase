---
id: 9980acf7-ff4d-4877-bbb3-27a1bec96ca1
---

# Enumeration

**Enumeration is drawing the map of a domain after your first foothold — who the users are, who the admins are, which machines exist, and who can log into what.**

## Before you start
<!-- bite: 7bba0b7e-8f82-4580-8dc8-3960d1994426 -->

You should have:

- The structure and the four-part mental model → [[cybersecurity/12-active-directory/01-what-active-directory-is|what Active Directory is]].
- The Kerberos basics, especially SPNs → [[cybersecurity/12-active-directory/02-authentication-and-kerberos|authentication and Kerberos]].
- A lab domain and one low-privilege credential to enumerate with → [[cybersecurity/02-ethical-hacking/01-rules-of-engagement-and-legal|rules of engagement]].

After this lesson you will be able to:

1. List what you enumerate — users, groups, sessions, ACLs, delegation — and say why sessions and ACLs are the non-obvious gold.
2. Explain what BloodHound does and why it turned "path to Domain Admin" into a menu item.
3. Name the right tool for each starting position: Windows foothold, Linux with credentials, or nothing but network access.

**Study route.** Read the kid version and what-you're-looking-for, then study BloodHound and the tools. The practice task runs a real collection against your lab.

## What enumeration is
<!-- bite: dc9b0467-8815-4357-9dfa-10ef4aea780f -->

Enumeration is the information-gathering stage that comes right after your first foothold: with one low-privilege account you collect every user, group, computer, session, permission and trust in the domain, then read the chain of "this person controls that group, which controls that account, which is admin on that server." That chain is an attack path, and in AD the map almost always contains one that reaches Domain Admin. The skill is reading the map — and one tool, BloodHound, now reads it for you.

## The kid version
<!-- bite: a5f54e5a-30e3-48b0-a4fc-43cccfe6b440 -->

You've landed on one machine as one low-privilege user. Before attacking anything, you need a map: who the users are, which are admins, which computers exist, who can log into what, and — crucially — **the chain of "this person can control that group which controls that account which is admin on that server."**

Enumeration is drawing that map. **The map almost always contains a path to Domain Admin; the skill is reading it.**

## What you're looking for
<!-- bite: 6889e2f3-fdb7-48b4-8bae-900abf493a00 -->

```text
Users          → who exists, who's an admin, who has an SPN (Kerberoastable),
                  who has pre-auth disabled (AS-REP roastable), stale accounts
Groups         → Domain Admins, Enterprise Admins, and nested memberships
Computers      → servers, workstations, OS versions, who's a local admin where
Sessions       → which users are LOGGED IN where (so you know whose creds are grabbable)
ACLs           → who has dangerous rights over whom (WriteDACL, GenericAll, …)
GPOs           → which policies you might abuse to run code
Trusts         → other domains you could pivot into
Delegation     → accounts configured for delegation (a fast escalation path)
```

**Sessions and ACLs are the non-obvious gold.** Knowing that a Domain Admin is currently logged into a server *you* have access to turns into credential theft; knowing a group you're in has `WriteDACL` over another group turns into escalation → [[cybersecurity/12-active-directory/05-lateral-movement-and-escalation|escalation]].

## BloodHound — the game-changer
<!-- bite: 6081dbc7-04b6-4031-aafd-0aff8f5742ea -->

**BloodHound treats AD as a graph and finds the shortest path from where you are to Domain Admin.** Before it, this analysis was manual and missed things; now it's a query.

```text
1. A COLLECTOR (SharpHound / BloodHound.py / RustHound) gathers the data —
   every user, group, computer, session, ACL, and their relationships
2. Load it into BloodHound (a Neo4j graph + UI)
3. Run a query: "Shortest Path to Domain Admins from Owned Principals"
4. It draws the exact chain of abuses
```

## Reading a BloodHound path
<!-- bite: 21068d17-4c17-425c-b41a-35e0498e67ee -->

The graph edges are named attacks: `MemberOf`, `AdminTo`, `HasSession`, `CanRDP`, `WriteDACL`, `GenericAll`, `AllowedToDelegate`, `Owns`. Each edge is a documented technique with a tool, and a path strings them together:

![A BloodHound attack path drawn as four nodes joined by labelled edges: your low-privilege user connects by MemberOf to the Help Desk group, which connects by GenericAll to the Server Admins group, which connects by AdminTo to the Domain Controller — a chain of three legitimate permissions that walks from a foothold to Domain Admin.](../images/ad-bloodhound-path.svg)

**"Find the shortest path to DA" is a menu item.** This is why AD compromise feels mechanical to someone who knows the tool and impossible to someone who doesn't — the analysis that used to take an expert days is now a graph query. **Learning BloodHound is the highest-leverage single skill in AD attacking.**

## The tools
<!-- bite: bdf65277-d446-4488-8026-306a31ee531e -->

**From a Windows foothold:**
- **PowerView** (PowerShell) — the classic interactive enumerator: `Get-DomainUser`, `Get-DomainGroup`, `Get-NetSession`, `Find-InterestingDomainAcl`
- **SharpHound** — the BloodHound collector
- **AD module** (`Get-ADUser` etc.) — built-in, blends in, needs RSAT

## The tools: Linux and pre-credential
<!-- bite: eef3760e-5e30-4c95-a29e-9a37fe13da03 -->

**From Linux / a foothold with credentials** (the impacket suite — *the* toolkit):
- **`GetADUsers.py`, `GetUserSPNs.py`** — enumerate users, find Kerberoastable accounts
- **`bloodhound-python`** — collect the graph remotely, no Windows needed
- **`ldapsearch` / windapsearch / ldapdomaindump** — raw LDAP queries
- **`nxc` (NetExec, formerly CrackMapExec)** — the swiss-army knife: spray, enumerate, check access across many hosts at once

**From nothing but network access** (pre-credential):
- **`enum4linux-ng`** — SMB/RPC enumeration, sometimes yields users via null sessions
- **`kerbrute`** — enumerate valid usernames via Kerberos (no lockout risk on username guessing), then password-spray
- **Responder** — poison LLMNR/NBT-NS/mDNS to capture NTLM hashes off the wire, often your *first* credential → [[cybersecurity/12-active-directory/04-credential-attacks|04]]

## Enumeration is mostly legitimate traffic
<!-- bite: f63ab190-6068-4cfc-835a-4a2e5dc58936 -->

The uncomfortable-for-defenders truth: **most enumeration uses normal LDAP and Kerberos queries** that any user is allowed to make. It looks like an application reading the directory. This is why:

- **It's hard to detect** without behavioural baselines — a workstation suddenly querying every ACL in the domain is anomalous, but only if you're watching for *that pattern* → [[cybersecurity/07-security-operations/index|detection]]
- **Attackers "live off the land"** — built-in tools and legitimate queries evade signature-based detection → [[cybersecurity/12-active-directory/05-lateral-movement-and-escalation|05]]
- **BloodHound's collection is noisy** and *can* be caught (a burst of session/ACL queries), which is why attackers throttle it or collect selectively

## The workflow
<!-- bite: 04715565-1c42-46ce-80f1-1161d5f6fb17 -->

```text
1. Get one credential (spray / phish / Responder / a found password)
2. bloodhound-python or SharpHound → collect the graph
3. Load into BloodHound → "Shortest Path to Domain Admins"
4. GetUserSPNs → Kerberoast every service account in parallel
5. Read the ACL/delegation paths BloodHound found
6. Execute the shortest path → escalate → repeat with new creds
```

## Key insight
<!-- bite: dbf282b3-a207-4d8c-9c7b-bfee527d665c -->

**Enumeration is drawing the who-can-do-what-to-whom graph, and BloodHound turned reading that graph from expert intuition into a menu item — "shortest path to Domain Admin."** The data is gathered with legitimate LDAP and Kerberos queries any user may make, which is exactly why it's powerful and hard to detect. The single highest-leverage AD skill is fluency with BloodHound: it converts a domain that looks impenetrable into a labelled path from your foothold to the crown.

## Terms used in this lesson
<!-- bite: 98da2ca6-5471-4082-979b-bdaca2bab55f -->

1. **Enumeration**: The stage after a foothold where you collect every object and relationship in the domain to build an attack map.
2. **BloodHound**: A tool that loads AD data into a graph and finds the shortest path from your account to Domain Admin. The single highest-leverage AD skill.
3. **Collector**: The program (SharpHound on Windows, `bloodhound-python` on Linux) that gathers the users, groups, sessions and ACLs BloodHound draws.
4. **ACL (Access Control List)**: The list of who holds which rights over an AD object. Dangerous rights like `WriteDACL` or `GenericAll` are escalation edges.
5. **Session**: A record of which user is currently logged into which machine. Knowing a Domain Admin is logged into a box you control turns into credential theft.
6. **Delegation**: A configuration letting a service act on behalf of a user. Misconfigured, it's a fast escalation path.
7. **PowerView / impacket / NetExec (`nxc`)**: The staple enumeration toolkits — PowerView on a Windows foothold, impacket and `nxc` from Linux with credentials.
8. **Responder**: A tool that poisons LLMNR/NBT-NS to capture NTLM hashes off the wire — often your *first* credential when you start with only network access.

## Check your understanding
<!-- bite: 1dbabc90-a990-4d6b-901f-8ed415d94891 -->

Try each one before you open the answer.

1. <!-- q: mcq id="98b3cbcb" -->
   Why is BloodHound described as turning AD compromise "from expert intuition into a menu item"?

   - [ ] It automatically exploits every vulnerability it finds.
   - [x] It models AD as a graph and computes the shortest path from your account to Domain Admin, so the analysis that once took an expert days becomes a query.
   - [ ] It brute-forces the Domain Admin password.
   - [ ] It disables Windows Defender on every host.

   <details><summary>Answer</summary>

   BloodHound collects the users, groups, sessions and ACLs, builds a graph of who-can-do-what-to-whom, and runs "shortest path to Domain Admins." It doesn't exploit anything — it finds the path. Walking it is the next lessons' job.

   </details>

2. <!-- q: mcq id="5a49744d" -->
   During enumeration you discover a Domain Admin has an active session on a server you already have admin rights to. Why is that "non-obvious gold"?

   - [ ] It lets you reset the DA's password directly.
   - [x] Their credentials are in that server's memory, so you can harvest them and become Domain Admin.
   - [ ] Sessions grant you Kerberos tickets automatically.
   - [ ] It proves the DA account has a weak password.

   <details><summary>Answer</summary>

   A logged-in user's credentials sit in LSASS memory. If you own the machine they're logged into, tools like mimikatz (lesson 04) dump those credentials — so a DA session on a box you control is a direct route to Domain Admin.

   </details>

3. <!-- q: gap id="052614e0" answers="LDAP|Kerberos" -->
   Enumeration is hard to detect because most of it uses normal ___ queries that any authenticated user is allowed to make — it looks like an application reading the directory.

   <details><summary>Answer</summary>

   LDAP (Kerberos also accepted). The directory is *meant* to be queried over LDAP, so reading users, groups and ACLs looks legitimate. Detection has to be behavioural — spotting *that* a single workstation suddenly queried every ACL — not signature-based.

   </details>

4. <!-- q: mcq id="5e3963d8" -->
   You have only network access to a target and no credentials yet. Which tool is the natural first choice?

   - [ ] BloodHound's GUI
   - [ ] PowerView
   - [x] Responder, to capture an NTLM hash off the wire
   - [ ] `secretsdump.py`

   <details><summary>Answer</summary>

   With no credentials, Responder poisons LLMNR/NBT-NS to capture an NTLM hash when a machine mistypes a share name — frequently your first credential. PowerView and BloodHound's richer collection need an account; `secretsdump` needs admin already.

   </details>

5. <!-- q: open id="c2df89e2" -->
   Someone says "I have one low-privilege domain account; there's nothing I can do without admin." Correct them.

   <details><summary>Answer</summary>

   One authenticated account is enough to enumerate the entire domain — users, groups, computers, sessions, ACLs, SPNs — run a full BloodHound collection, find the shortest path to Domain Admin, and Kerberoast every service account. The first credential is the hard part; after that, AD hands you the map. "No admin" doesn't mean "no attack surface."

   </details>

## Practice — collect and read the graph
<!-- bite: 8a3cded4-1c68-4675-b363-24a4cb5422c7 -->

On your lab, run a real enumeration end to end.

- From your low-privilege account, run a collector: `bloodhound-python -u user -p 'pass' -d corp.local -ns <DC-IP> -c all` (or SharpHound on Windows).
- Load the data into BloodHound and run **Shortest Path to Domain Admins from Owned Principals**.
- Read the path out loud, edge by edge, and name the technique each edge represents (`MemberOf`, `GenericAll`, `AdminTo`…).
- Separately, list the Kerberoastable accounts (`GetUserSPNs.py`) — you'll attack them next lesson.
- **Done when:** BloodHound draws at least one path to Domain Admin on your lab and you can explain every edge on it.

## Before moving on
<!-- bite: 9ae7049a-9a86-47bb-a461-21658c5816d8 -->

You should be able to say what you enumerate and why sessions and ACLs matter most, run a BloodHound collection, and read the path it draws as a sequence of named techniques. You now have the map; the next two lessons walk it.

Next: [[cybersecurity/12-active-directory/04-credential-attacks|credential attacks]] — turning the accounts you found into credentials you hold, starting with Kerberoasting the service accounts you just listed.

## Related
<!-- bite: 13f68818-aed8-4094-aa8f-fe2df62d9695 -->
- [[cybersecurity/12-active-directory/04-credential-attacks|credential attacks]] — what you do with the accounts you find
- [[cybersecurity/12-active-directory/05-lateral-movement-and-escalation|lateral movement]] — walking the path BloodHound drew
- [[cybersecurity/02-ethical-hacking/06-scanning-and-enumeration|scanning and enumeration]] — the general discipline
- [[cybersecurity/12-active-directory/06-defending-active-directory|defending AD]] — detecting this

## About this lesson
<!-- bite: e447da66-b4c2-4458-9449-cc3676f7e606 -->

**Level:** Intermediate → Advanced. **Covers:** mapping the domain after your first foothold, and why BloodHound changed the game.

*Source: [reference] — Aug 2026.*
