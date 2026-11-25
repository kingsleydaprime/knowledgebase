---
id: 96cfa2bd-23ce-41ce-b0a2-79f6d29cdd93
---

# Authentication and Kerberos

**Kerberos is how a Windows network checks who you are — using stamped "tickets" instead of sending your password to every server.**

## Before you start
<!-- bite: 75a38663-f8c0-4a4e-8128-ecf0bd18ff81 -->

You should have:

- The structure and mental model → [[cybersecurity/12-active-directory/01-what-active-directory-is|what Active Directory is]].
- A rough idea of a password *hash* — a one-way scramble of a password → [[cybersecurity/05-cryptography/03-hashing-and-integrity|hashing]].

After this lesson you will be able to:

1. Trace the three-step Kerberos ticket exchange and name who holds which key.
2. Explain the two encryption keys — KRBTGT's and the service account's — that generate almost every named attack.
3. Say why "any authenticated user can request a service ticket" is the crack that makes Kerberoasting work.

**Study route.** Read the kid version and the two protocols, then study the ticket flow and the two keys slowly — the whole attack section (04–05) is applied versions of this one diagram.

## What Kerberos is
<!-- bite: 767357e4-7eab-4252-b95a-a4bf586b6ffe -->

Kerberos is the authentication protocol an AD network uses to prove who you are. Rather than send your password to every server, you prove yourself once to a central authority and get back a **ticket** — a stamped pass the other servers trust because it carries that authority's stamp. NTLM, an older scheme, still runs alongside it. Nearly every named AD attack is a trick played on this ticketing, so the whole attack section is really applied Kerberos — which is why this lesson comes before the attacks.

## The kid version
<!-- bite: eeb5bed7-a9aa-40aa-86bd-28bbe2c62d30 -->

When you log into a Windows domain, you don't send your password to every server you use. Instead you get a **ticket** from a central authority — a stamped pass that says "this really is Alice." You show the ticket to file servers, databases and apps, and they trust it because it's stamped by the authority they all trust.

**Almost every AD attack is a trick played on this ticket system:** stealing a ticket, forging a ticket, or forcing the system to hand you a ticket you can crack offline.

## Two protocols: NTLM and Kerberos
<!-- bite: 489ab9cb-f063-4ceb-8164-9eeb1f94863e -->

AD supports both, and the difference matters:

**NTLM** — the old challenge-response scheme. The server challenges, the client proves it knows the password hash. **The critical weakness: it uses the password *hash* directly, so the hash is a password-equivalent** — steal the hash and you don't need to crack it, you just *use* it → [[cybersecurity/12-active-directory/04-credential-attacks|pass-the-hash]].

**Kerberos** — the modern default, ticket-based, and where most named attacks live. More complex, and its complexity is the attack surface.

**NTLM is still enabled almost everywhere** for backward compatibility, which is why pass-the-hash still works in 2026.

## How Kerberos works
<!-- bite: 89a914d3-0fc4-47c6-b0d4-266a1f79e39c -->

Three parties: the **client**, the service it wants, and the **KDC** (Key Distribution Center) — which runs on the Domain Controller. The exchange happens in three request/response pairs:

1. **AS-REQ / AS-REP** — "I'm Alice." The KDC returns a **TGT**, encrypted with **KRBTGT's** hash.
2. **TGS-REQ / TGS-REP** — present the TGT, ask for SQL. The KDC returns a **service ticket**, encrypted with the **service account's** hash.
3. **AP-REQ** — present the service ticket to SQL; it decrypts with its own key and trusts you.

## Seeing the ticket exchange
<!-- bite: 4810d0a6-b1ae-4060-b587-f03daaeb8023 -->

Follow the two keys as you read the picture: the TGT is sealed with KRBTGT's hash, and each service ticket is sealed with that service's account hash. Those two facts are the whole attack surface.

![The Kerberos ticket exchange in three steps: the client sends AS-REQ to the KDC and gets back a TGT encrypted with the KRBTGT account's hash, then sends TGS-REQ with that TGT and gets back a service ticket encrypted with the service account's hash, then sends AP-REQ with the service ticket to the SQL server, which decrypts it with its own key and trusts it.](../images/ad-kerberos-flow.svg)

## The two keys that are the whole story
<!-- bite: e2fb2d70-12f9-4299-b65b-92b92b8fc27f -->

Which account's hash encrypts which ticket is the fact that generates nearly every named attack:

- **The TGT is encrypted with the KRBTGT account's hash.** So whoever knows KRBTGT's hash can forge *any* TGT for *any* user — a **Golden Ticket** → [[cybersecurity/12-active-directory/05-lateral-movement-and-escalation|05]].
- **Each service ticket is encrypted with that service account's hash.** So if you can *request* a service ticket, you're holding something encrypted with the service account's password — **crack it offline** → Kerberoasting.

That second point is the crucial one: a service ticket is, in effect, an offline password-guessing oracle for the service account's password, and *any* authenticated user can request one.

**That second point is the crucial insight**: a service ticket is, in effect, an offline password-guessing oracle for the service account's password, and *any* authenticated user can request one.

## Why each design choice becomes an attack
<!-- bite: 5ccfb12c-a5f2-4e82-b0fb-35cda1b5ba55 -->

| Kerberos feature | The attack it enables |
|---|---|
| Service tickets encrypted with the service account's hash | **Kerberoasting** — request tickets for service accounts, crack them offline |
| Accounts with "pre-auth not required" | **AS-REP roasting** — request their AS-REP and crack it, no credentials needed |
| TGT encrypted with KRBTGT's hash | **Golden Ticket** — know KRBTGT's hash, forge any TGT forever |
| Service ticket trusted by its server | **Silver Ticket** — know a service's hash, forge tickets to it |
| Delegation (a service acts "as" a user) | **Unconstrained / constrained / RBCD delegation abuse** |

**This is why note 04 and 05 are mostly a tour of Kerberos.** Nearly every named AD attack is "abuse the fact that a ticket is encrypted with an account's password hash."

## SPNs — the Kerberoasting enabler
<!-- bite: bd0a831a-10ee-4a7b-817e-2d6d5c7c26c5 -->

A **Service Principal Name** links a service (like `MSSQLSvc/db.corp.local`) to the account that runs it. To request a ticket for a service, you ask for it *by SPN*. So:

```text
"give me every account that has an SPN"   ← these are the service accounts
   → request a Kerberos ticket for each
      → each ticket is encrypted with that account's password hash
         → crack them offline
```

**Any authenticated domain user can enumerate SPNs and request tickets** — no special privilege. That's why Kerberoasting is the single most reliable AD attack: it needs only *a* valid account, and service accounts frequently have weak, human-set, non-expiring passwords → [[cybersecurity/12-active-directory/04-credential-attacks|credential attacks]].

## What "as an authenticated user" buys you
<!-- bite: 91753fff-1ebb-4425-8921-538458cf02ab -->

The recurring phrase in AD attacks is *"as any authenticated domain user."* Once you have **one** valid credential — from a phish, a password spray, a config file, a network capture — you can:

- Enumerate the entire domain (users, groups, computers, ACLs, SPNs)
- Run BloodHound to map every attack path
- Kerberoast every service account
- AS-REP roast every pre-auth-disabled account

**So the first foothold is the hard part; after that, AD hands you the map.** This is why password spraying and phishing get so much attention — they're the door into everything else → [[cybersecurity/12-active-directory/03-enumeration|enumeration]].

## Key insight
<!-- bite: ce427794-13a0-4d8a-997d-b6387ad67f68 -->

**Kerberos is a ticket system where every ticket is encrypted with some account's password hash, and that single fact generates nearly every named AD attack** — Kerberoasting cracks service tickets, Golden Tickets forge TGTs from KRBTGT's hash, Silver Tickets forge service tickets, and NTLM's pass-the-hash skips cracking entirely. Understand that a service ticket is an offline crackable object *any* user can request, and that KRBTGT's hash is the master key to the whole domain, and the rest of AD attacking is applying those two ideas.

## Terms used in this lesson
<!-- bite: e70abf19-cddd-4fc5-9c17-db28b4b3d92b -->

1. **Kerberos**: The ticket-based authentication protocol AD uses by default. You prove yourself once and carry tickets to everything else.
2. **NTLM**: An older Windows authentication scheme, challenge-response, still enabled almost everywhere. It authenticates with the password hash directly, which is why a stolen hash is usable as-is.
3. **KDC (Key Distribution Center)**: The service, running on the Domain Controller, that issues Kerberos tickets.
4. **TGT (Ticket-Granting Ticket)**: The first ticket you get, proving you logged in. It's encrypted with the KRBTGT account's hash.

## Terms used in this lesson: tickets and accounts
<!-- bite: 36d11f70-bcd4-41fe-8f13-ad7809bb0345 -->

5. **TGS (service ticket)**: A ticket for one specific service, handed out when you present a valid TGT. It's encrypted with that service's account hash.
6. **KRBTGT**: The special account whose hash encrypts every TGT. Knowing it lets an attacker forge tickets forever (a Golden Ticket), so it is the domain's master key.
7. **SPN (Service Principal Name)**: A label, like `MSSQLSvc/db.corp.local`, that links a running service to the account behind it. You request a ticket for a service *by its SPN*.
8. **Service account**: An account that runs a service (SQL, IIS) rather than a person. Often has a weak, non-expiring password and more rights than it needs.

## Check your understanding
<!-- bite: c87da150-395d-4419-9bca-a13de2de9dbd -->

Try each one before you open the answer.

1. <!-- q: mcq id="60deedcb" -->
   In the Kerberos exchange, which account's hash is a TGT encrypted with?

   - [ ] The user's own hash
   - [x] The KRBTGT account's hash
   - [ ] The target service's hash
   - [ ] The Domain Controller's machine hash

   <details><summary>Answer</summary>

   The TGT is encrypted with the KRBTGT account's hash. That's why an attacker who learns KRBTGT's hash can forge a valid TGT for anyone — a Golden Ticket — and why KRBTGT is the domain's master key.

   </details>

2. <!-- q: mcq id="969e3923" -->
   Kerberoasting works because of which fact about service tickets?

   - [ ] Service tickets are stored in plaintext on the DC.
   - [x] A service ticket is encrypted with the service account's hash, and any authenticated user can request one — so it can be cracked offline.
   - [ ] Service tickets never expire.
   - [ ] The KDC emails service tickets to anyone who asks.

   <details><summary>Answer</summary>

   Any authenticated user can request a service ticket for any SPN, and that ticket is encrypted with the service account's password hash. That makes it an offline password-guessing target — no privilege needed, no lockout, nothing logged beyond a normal ticket request.

   </details>

3. <!-- q: gap id="3a3144a6" answers="hash" -->
   The reason pass-the-hash works is that NTLM authenticates with the password ___ directly, making it a password-equivalent you can use without ever cracking it.

   <details><summary>Answer</summary>

   Hash. NTLM proves knowledge of the hash, not the plaintext, so stealing the hash is as good as stealing the password — you authenticate with it directly.

   </details>

4. <!-- q: mcq id="1f193678" -->
   A pentester gets a single low-privilege domain account from a password spray. Which of these can they do immediately, with no further privilege?

   - [ ] Read every file on the Domain Controller
   - [x] Enumerate the domain and Kerberoast every service account
   - [ ] Reset the Administrator password
   - [ ] Forge a Golden Ticket

   <details><summary>Answer</summary>

   "As any authenticated user" you can enumerate users, groups, computers, ACLs and SPNs, run BloodHound, and Kerberoast every service account. Resetting Administrator or forging a Golden Ticket needs privileges you don't have yet — those come later in the chain.

   </details>

5. <!-- q: open id="72cfd215" -->
   Why is it fair to say "the attack section of this course is mostly applied Kerberos"? Give the single sentence that ties the named attacks together.

   <details><summary>Answer</summary>

   Every Kerberos ticket is encrypted with some account's password hash, and nearly every named attack abuses that one fact: Kerberoasting cracks a service ticket (service account's hash), AS-REP roasting cracks an AS-REP (the user's hash, when pre-auth is off), Golden Tickets forge a TGT (KRBTGT's hash), and Silver Tickets forge a service ticket (the service's hash). Learn which hash wraps which ticket and the attacks become obvious.

   </details>

## Practice — watch the tickets
<!-- bite: 5d0d8b5e-f597-40c1-bea6-07fe8ca6b505 -->

On your lab, make the ticket exchange visible instead of abstract.

- Log into a domain workstation as a normal user, then run `klist` — you'll see your cached TGT and any service tickets. Note the lifetimes and the services.
- Access a share or SQL instance, run `klist` again, and watch a new service ticket (TGS) appear for that SPN.
- List the accounts that have an SPN set (`setspn -Q */*` on Windows, or `GetUserSPNs.py` from Linux). These are exactly the Kerberoastable accounts lesson 04 attacks.
- **Done when:** you can point at a real TGT and a real TGS in `klist` output and say which account's hash each is encrypted with.

## Before moving on
<!-- bite: 8b5e81a3-70e0-4139-825b-644635d04d36 -->

You should be able to draw the three-step flow from memory, name KRBTGT's hash as the key behind the TGT and the service account's hash as the key behind a service ticket, and explain why *requesting* a service ticket is already half of Kerberoasting. That diagram is the spine of the next two lessons.

Next: [[cybersecurity/12-active-directory/03-enumeration|enumeration]] — mapping the domain after your first foothold, and the one tool (BloodHound) that turns "path to Domain Admin" into a menu item.

## Related
<!-- bite: a5201b7a-60ec-4fc6-85cc-2a6fd56d8ab8 -->
- [[cybersecurity/12-active-directory/04-credential-attacks|credential attacks]] — Kerberoasting, AS-REP, pass-the-hash in practice
- [[cybersecurity/12-active-directory/05-lateral-movement-and-escalation|lateral movement]] — Golden/Silver tickets, DCSync
- [[cybersecurity/05-cryptography/05-digital-signatures-and-pki|signatures and PKI]] — the crypto Kerberos relies on
- [[cybersecurity/04-web-security/02-secure-authentication|secure authentication]] — the general principles

## About this lesson
<!-- bite: d99d1db5-4a5c-4c8a-b32c-6d97a5541c63 -->

**Level:** Advanced. **Covers:** how AD proves who you are, because nearly every named AD attack is an abuse of this one protocol.

*Source: [reference] — Aug 2026.*
