# Enumeration

**[Intermediate → Advanced]** — mapping the domain after your first foothold, and why BloodHound changed the game.

## The kid version first

You've landed on one machine as one low-privilege user. Before attacking anything, you need a map: who the users are, which are admins, which computers exist, who can log into what, and — crucially — **the chain of "this person can control that group which controls that account which is admin on that server."**

Enumeration is drawing that map. **The map almost always contains a path to Domain Admin; the skill is reading it.**

## What you're looking for

```
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

**BloodHound treats AD as a graph and finds the shortest path from where you are to Domain Admin.** Before it, this analysis was manual and missed things; now it's a query.

```
1. A COLLECTOR (SharpHound / BloodHound.py / RustHound) gathers the data —
   every user, group, computer, session, ACL, and their relationships
2. Load it into BloodHound (a Neo4j graph + UI)
3. Run a query: "Shortest Path to Domain Admins from Owned Principals"
4. It draws the exact chain of abuses
```

The graph edges are named attacks: `MemberOf`, `AdminTo`, `HasSession`, `CanRDP`, `WriteDACL`, `GenericAll`, `AllowedToDelegate`, `Owns`. **A path might read:** *your user* → `MemberOf` → *Help Desk* → `GenericAll` → *Server Admins* → `AdminTo` → *DC01*. Each edge is a documented technique with a tool.

**"Find the shortest path to DA" is a menu item.** This is why AD compromise feels mechanical to someone who knows the tool and impossible to someone who doesn't — the analysis that used to take an expert days is now a graph query. **Learning BloodHound is the highest-leverage single skill in AD attacking.**

## The tools

**From a Windows foothold:**
- **PowerView** (PowerShell) — the classic interactive enumerator: `Get-DomainUser`, `Get-DomainGroup`, `Get-NetSession`, `Find-InterestingDomainAcl`
- **SharpHound** — the BloodHound collector
- **AD module** (`Get-ADUser` etc.) — built-in, blends in, needs RSAT

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

The uncomfortable-for-defenders truth: **most enumeration uses normal LDAP and Kerberos queries** that any user is allowed to make. It looks like an application reading the directory. This is why:

- **It's hard to detect** without behavioural baselines — a workstation suddenly querying every ACL in the domain is anomalous, but only if you're watching for *that pattern* → [[cybersecurity/07-security-operations/README|detection]]
- **Attackers "live off the land"** — built-in tools and legitimate queries evade signature-based detection → [[cybersecurity/12-active-directory/05-lateral-movement-and-escalation|05]]
- **BloodHound's collection is noisy** and *can* be caught (a burst of session/ACL queries), which is why attackers throttle it or collect selectively

## The workflow

```
1. Get one credential (spray / phish / Responder / a found password)
2. bloodhound-python or SharpHound → collect the graph
3. Load into BloodHound → "Shortest Path to Domain Admins"
4. GetUserSPNs → Kerberoast every service account in parallel
5. Read the ACL/delegation paths BloodHound found
6. Execute the shortest path → escalate → repeat with new creds
```

## Key insight

**Enumeration is drawing the who-can-do-what-to-whom graph, and BloodHound turned reading that graph from expert intuition into a menu item — "shortest path to Domain Admin."** The data is gathered with legitimate LDAP and Kerberos queries any user may make, which is exactly why it's powerful and hard to detect. The single highest-leverage AD skill is fluency with BloodHound: it converts a domain that looks impenetrable into a labelled path from your foothold to the crown.

## Related
- [[cybersecurity/12-active-directory/04-credential-attacks|credential attacks]] — what you do with the accounts you find
- [[cybersecurity/12-active-directory/05-lateral-movement-and-escalation|lateral movement]] — walking the path BloodHound drew
- [[cybersecurity/02-ethical-hacking/06-scanning-and-enumeration|scanning and enumeration]] — the general discipline
- [[cybersecurity/12-active-directory/06-defending-active-directory|defending AD]] — detecting this

*Source: [reference] — Aug 2026.*
