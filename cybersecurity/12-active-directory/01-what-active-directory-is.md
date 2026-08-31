# What Active Directory Is

**[Intermediate]** — the corporate backbone, why it's the pentester's main event, and the attacker's mental model. Assumes the authorization in [[cybersecurity/02-ethical-hacking/01-rules-of-engagement-and-legal|rules of engagement]].

## The kid version first

Almost every company runs Windows, and **Active Directory is the thing that decides who's allowed to log into what.** One central system holds every user, every computer, every group, and the rules connecting them. Log in once and it lets you into everything you're allowed to touch.

That central control is convenient for the company — and it's why an attacker who compromises one laptop spends all their effort trying to reach *that central system*, because owning it means owning the whole network.

## Why AD is the pentester's main event

**Internal network penetration testing is, in practice, Active Directory penetration testing.** The overwhelming majority of corporate environments run AD, and a real engagement looks like:

```
phish one user / find one weak password
   → land on one workstation as a low-privilege user
      → enumerate AD to map the terrain
         → find a path of misconfigurations
            → escalate to Domain Admin
               → you own every machine in the domain
```

**This is the gap most self-taught hackers have.** They learn web exploitation and buffer overflows, then hit a real corporate network — or a HackTheBox Pro Lab, or the OSCP AD set — and have no idea what they're looking at. **AD is what the actual job is**, and it barely resembles the CTF `pwn` and web categories.

## The structure

```
   FOREST                         ← the top-level security boundary
     └── DOMAIN  (corp.local)     ← a unit of administration; users, computers, policy
           ├── Domain Controllers (DCs)   ← THE servers running AD. The prize
           ├── Organizational Units (OUs) ← folders for organising objects
           ├── Users                      ← accounts (people and services)
           ├── Computers                  ← every joined machine is an AD object
           └── Groups                     ← collections; membership grants rights
```

- **Domain Controller (DC)** — the server that runs AD, holds the database of every object, and authenticates logins. **Compromising a DC = compromising the domain.** There are usually several for redundancy; they replicate to each other
- **Domain** — the administrative and (mostly) security unit. `corp.local`
- **Forest** — one or more domains with trust between them. **The forest, not the domain, is the true security boundary** — a subtlety that matters for escalation across trusts
- **The database** is a file called `NTDS.dit` on the DC, holding every account's password hash. **Stealing it is game over** → [[cybersecurity/12-active-directory/04-credential-attacks|credential attacks]]

## The objects that matter

- **Domain Admins** — the group whose members control the entire domain. **The goal**
- **Service accounts** — accounts that run services (SQL, IIS). Often over-privileged, often with weak or non-expiring passwords, and **exploitable via Kerberoasting** → [[cybersecurity/12-active-directory/04-credential-attacks|04]]
- **Computer accounts** — every joined machine has one, with its own password. They matter more than beginners expect (delegation, resource-based attacks)
- **GPOs (Group Policy Objects)** — push configuration and scripts to machines. **Control a GPO and you run code on every machine it applies to**
- **Kerberos** — the authentication protocol AD uses, and the source of most named attacks → [[cybersecurity/12-active-directory/02-authentication-and-kerberos|Kerberos]]

## The attacker's mental model

Internalise these four ideas and AD stops being opaque:

**1. It's a graph, not a hierarchy.** Users, groups, computers and permissions form a graph of "who can do what to whom." Attack paths are *paths through that graph* from where you are to Domain Admin. **This is literally how [[cybersecurity/12-active-directory/03-enumeration|BloodHound]] works** — it draws the graph and finds the shortest path.

**2. Credentials are currency.** The whole game is collecting credentials (passwords, hashes, tickets) and using them to reach accounts with more access. You rarely "exploit a vulnerability" in the CTF sense; **you abuse legitimate features with stolen credentials.**

**3. Misconfiguration, not vulnerability.** AD compromise is overwhelmingly about *how it's configured* — over-privileged accounts, weak service passwords, dangerous ACLs, excessive delegation — not about a CVE. **The DC is usually fully patched; the domain falls anyway.**

**4. Living off the land.** Attackers use built-in Windows tools and legitimate protocols, because they blend in with normal admin activity and evade detection → [[cybersecurity/12-active-directory/05-lateral-movement-and-escalation|lateral movement]].

## Why defenders struggle

AD is **decades old, backward-compatible to a fault, and insecure by default in the name of "it just works."** Legacy protocols stay enabled, default permissions are generous, and the same features that make it manageable make it exploitable. **Defence is largely about turning off defaults and watching the graph** → [[cybersecurity/12-active-directory/06-defending-active-directory|defending AD]].

## Key insight

**Active Directory compromise is graph traversal with stolen credentials, not vulnerability exploitation** — you land somewhere, map the graph of who-can-do-what-to-whom, and follow a path of *misconfigurations* to Domain Admin. That's why it's the pentester's main event and the biggest blind spot for people who learned on CTFs: the skill isn't finding a bug, it's reading the terrain and abusing legitimate features. Learn the graph, the credentials, and the defaults, and the named attacks become obvious.

## Related
- [[cybersecurity/12-active-directory/02-authentication-and-kerberos|authentication and Kerberos]] — the protocol underneath the attacks
- [[cybersecurity/12-active-directory/03-enumeration|enumeration]] — BloodHound and mapping the graph
- [[cybersecurity/01-fundamentals/01-what-is-cybersecurity|fundamentals]] · [[cybersecurity/03-network-security/README|network security]]
- [[cybersecurity/11-binary-exploitation/README|binary exploitation]] — the other big offensive gap

*Source: [reference] — Aug 2026. Authorised-testing / lab material.*
