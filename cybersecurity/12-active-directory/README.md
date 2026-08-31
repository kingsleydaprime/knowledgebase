# Active Directory

**Internal network penetration testing is, in practice, Active Directory penetration testing.** Nearly every company runs AD, and a real engagement is: one foothold → map the domain → follow a chain of misconfigurations → Domain Admin. **This is the biggest blind spot for people who learned on CTFs**, where nothing resembles it.

**Every note assumes the authorization in [[cybersecurity/02-ethical-hacking/01-rules-of-engagement-and-legal|rules of engagement]].** Lab, CTF (HackTheBox Pro Labs, the OSCP AD set), and authorised-engagement material.

> **The one idea:** AD compromise is **graph traversal with stolen credentials, not vulnerability exploitation.** You abuse legitimate features — Kerberos tickets, replication, delegation, ACLs — with harvested credentials, following a path through the who-can-do-what-to-whom graph. The DC is usually patched; the domain falls through misconfiguration anyway.

## Why this exists

The vault treated AD as a single table row (Kerberoasting). **It's what the actual internal-pentest job is**, and the natural home for the offensive skills that CTF `web` and `pwn` never teach — so it earns a section, paired with [[cybersecurity/11-binary-exploitation/README|binary exploitation]] as the two big offensive gaps closed Aug 2026.

## Reading order

**Read 01–02 before the attacks** — nearly every named attack is an abuse of the Kerberos model in note 02, and won't make sense without it.

1. [[cybersecurity/12-active-directory/01-what-active-directory-is|what-active-directory-is]] — **[Intermediate]** — the structure, why it's the pentester's main event, and **the four-part attacker's mental model (it's a graph, credentials are currency, misconfig not vuln, live off the land)**
2. [[cybersecurity/12-active-directory/02-authentication-and-kerberos|authentication-and-kerberos]] — **[Advanced]** — NTLM vs Kerberos, the ticket flow, and **why "every ticket is encrypted with an account's hash" generates nearly every named attack**
3. [[cybersecurity/12-active-directory/03-enumeration|enumeration]] — **[Intermediate → Advanced]** — mapping the domain, and **why BloodHound turned "path to Domain Admin" from expert intuition into a menu item**
4. [[cybersecurity/12-active-directory/04-credential-attacks|credential-attacks]] — **[Advanced]** — Kerberoasting, AS-REP roasting, pass-the-hash, mimikatz — and **"the hash is as good as the password"**
5. [[cybersecurity/12-active-directory/05-lateral-movement-and-escalation|lateral-movement-and-escalation]] — **[Advanced]** — moving between machines, and the named escalations: **DCSync, Golden/Silver Tickets, ACL abuse, delegation, ADCS**
6. [[cybersecurity/12-active-directory/06-defending-active-directory|defending-active-directory]] — **[Advanced]** — the blue-team mirror: **tiering (the highest-impact control), gMSA, LAPS, honeytokens, and behavioural detection**

## If you only take three things

1. **BloodHound is the highest-leverage single skill** — it draws the graph and finds the shortest path to Domain Admin ([[cybersecurity/12-active-directory/03-enumeration|03]]).
2. **One valid credential unlocks the whole map** — enumerate, Kerberoast, and roast all "as any authenticated user" ([[cybersecurity/12-active-directory/02-authentication-and-kerberos|02]]).
3. **KRBTGT's hash is the master key** — DCSync it, forge Golden Tickets forever; and it's why tiering matters most defensively ([[cybersecurity/12-active-directory/05-lateral-movement-and-escalation|05]]).

## Practice

- **[HackTheBox](https://hackthebox.com) Pro Labs** (Dante, Zephyr, and the AD-focused ones) and AD-heavy machines
- **[TryHackMe](https://tryhackme.com)** — the "Attacking Active Directory" and "Compromising AD" paths, gentler
- **[GOAD (Game of Active Directory)](https://github.com/Orange-Cyberdefense/GOAD)** — a free, deliberately-vulnerable AD lab you run yourself. **The best way to build a home AD to attack**
- **The OSCP** now includes an Active Directory set — this folder maps onto it

## Related
- [[cybersecurity/README|cybersecurity curriculum map]] · [[cybersecurity/11-binary-exploitation/README|binary exploitation]]
- [[cybersecurity/02-ethical-hacking/README|ethical hacking]] — the methodology this fits inside
- [[cybersecurity/07-security-operations/README|security operations]] — detecting all of this
- [[cybersecurity/projects|cybersecurity projects]] — the reps ladder
