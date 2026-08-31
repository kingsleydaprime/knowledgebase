# Authentication and Kerberos

**[Advanced]** — how AD proves who you are, because nearly every named AD attack is an abuse of this one protocol.

## The kid version first

When you log into a Windows domain, you don't send your password to every server you use. Instead you get a **ticket** from a central authority — a stamped pass that says "this really is Alice." You show the ticket to file servers, databases and apps, and they trust it because it's stamped by the authority they all trust.

**Almost every AD attack is a trick played on this ticket system:** stealing a ticket, forging a ticket, or forcing the system to hand you a ticket you can crack offline.

## Two protocols: NTLM and Kerberos

AD supports both, and the difference matters:

**NTLM** — the old challenge-response scheme. The server challenges, the client proves it knows the password hash. **The critical weakness: it uses the password *hash* directly, so the hash is a password-equivalent** — steal the hash and you don't need to crack it, you just *use* it → [[cybersecurity/12-active-directory/04-credential-attacks|pass-the-hash]].

**Kerberos** — the modern default, ticket-based, and where most named attacks live. More complex, and its complexity is the attack surface.

**NTLM is still enabled almost everywhere** for backward compatibility, which is why pass-the-hash still works in 2026.

## How Kerberos works

Three parties: the **client**, the service it wants, and the **KDC** (Key Distribution Center) — which runs on the Domain Controller. The flow:

```
1. AS-REQ / AS-REP   client → KDC: "I'm Alice, prove it"
                     KDC returns a TGT (Ticket-Granting Ticket),
                     encrypted with the KRBTGT account's secret

2. TGS-REQ / TGS-REP client → KDC: "here's my TGT, I want the SQL service"
                     KDC returns a TGS (service ticket),
                     encrypted with the SERVICE account's secret

3. AP-REQ            client → SQL server: "here's my service ticket"
                     server decrypts it with its own key → trusts it
```

**Two encryption keys are the whole story:**

- **The TGT is encrypted with the KRBTGT account's hash.** So whoever knows KRBTGT's hash can forge *any* TGT for *any* user — a **Golden Ticket** → [[cybersecurity/12-active-directory/05-lateral-movement-and-escalation|05]]
- **Each service ticket is encrypted with that service account's hash.** So if you can *request* a service ticket, you're holding something encrypted with the service account's password — **crack it offline** → Kerberoasting

**That second point is the crucial insight**: a service ticket is, in effect, an offline password-guessing oracle for the service account's password, and *any* authenticated user can request one.

## Why each design choice becomes an attack

| Kerberos feature | The attack it enables |
|---|---|
| Service tickets encrypted with the service account's hash | **Kerberoasting** — request tickets for service accounts, crack them offline |
| Accounts with "pre-auth not required" | **AS-REP roasting** — request their AS-REP and crack it, no credentials needed |
| TGT encrypted with KRBTGT's hash | **Golden Ticket** — know KRBTGT's hash, forge any TGT forever |
| Service ticket trusted by its server | **Silver Ticket** — know a service's hash, forge tickets to it |
| Delegation (a service acts "as" a user) | **Unconstrained / constrained / RBCD delegation abuse** |

**This is why note 04 and 05 are mostly a tour of Kerberos.** Nearly every named AD attack is "abuse the fact that a ticket is encrypted with an account's password hash."

## SPNs — the Kerberoasting enabler

A **Service Principal Name** links a service (like `MSSQLSvc/db.corp.local`) to the account that runs it. To request a ticket for a service, you ask for it *by SPN*. So:

```
"give me every account that has an SPN"   ← these are the service accounts
   → request a Kerberos ticket for each
      → each ticket is encrypted with that account's password hash
         → crack them offline
```

**Any authenticated domain user can enumerate SPNs and request tickets** — no special privilege. That's why Kerberoasting is the single most reliable AD attack: it needs only *a* valid account, and service accounts frequently have weak, human-set, non-expiring passwords → [[cybersecurity/12-active-directory/04-credential-attacks|credential attacks]].

## What "as an authenticated user" buys you

The recurring phrase in AD attacks is *"as any authenticated domain user."* Once you have **one** valid credential — from a phish, a password spray, a config file, a network capture — you can:

- Enumerate the entire domain (users, groups, computers, ACLs, SPNs)
- Run BloodHound to map every attack path
- Kerberoast every service account
- AS-REP roast every pre-auth-disabled account

**So the first foothold is the hard part; after that, AD hands you the map.** This is why password spraying and phishing get so much attention — they're the door into everything else → [[cybersecurity/12-active-directory/03-enumeration|enumeration]].

## Key insight

**Kerberos is a ticket system where every ticket is encrypted with some account's password hash, and that single fact generates nearly every named AD attack** — Kerberoasting cracks service tickets, Golden Tickets forge TGTs from KRBTGT's hash, Silver Tickets forge service tickets, and NTLM's pass-the-hash skips cracking entirely. Understand that a service ticket is an offline crackable object *any* user can request, and that KRBTGT's hash is the master key to the whole domain, and the rest of AD attacking is applying those two ideas.

## Related
- [[cybersecurity/12-active-directory/04-credential-attacks|credential attacks]] — Kerberoasting, AS-REP, pass-the-hash in practice
- [[cybersecurity/12-active-directory/05-lateral-movement-and-escalation|lateral movement]] — Golden/Silver tickets, DCSync
- [[cybersecurity/05-cryptography/05-digital-signatures-and-pki|signatures and PKI]] — the crypto Kerberos relies on
- [[cybersecurity/04-web-security/02-secure-authentication|secure authentication]] — the general principles

*Source: [reference] — Aug 2026.*
