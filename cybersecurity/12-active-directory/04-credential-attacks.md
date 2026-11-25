---
id: 76e4a488-6d24-4cce-bcd4-304f02a76eeb
---

# Credential Attacks

**A credential attack collects the things that prove who someone is — password hashes and login tickets — so you can act as them, usually without ever learning the real password.**

## Before you start
<!-- bite: 8eaed463-2b2e-4635-ba09-84f157e841e4 -->

You should have:

- The two keys of Kerberos and why a service ticket is crackable → [[cybersecurity/12-active-directory/02-authentication-and-kerberos|authentication and Kerberos]].
- Your list of Kerberoastable accounts from enumeration → [[cybersecurity/12-active-directory/03-enumeration|enumeration]].
- `hashcat` or `john`, the impacket suite, and a wordlist (`rockyou.txt`) on your attacking box → [[cybersecurity/02-ethical-hacking/01-rules-of-engagement-and-legal|rules of engagement]].

After this lesson you will be able to:

1. Run the four core techniques — Kerberoasting, AS-REP roasting, pass-the-hash, machine harvesting — and say what each needs to start.
2. Explain why "the hash is as good as the password" makes a stolen hash a full compromise, not a puzzle.
3. Pick the right `hashcat` mode for a Kerberoast, an AS-REP and a raw NTLM hash.

**Study route.** Read the kid version, then the four techniques in order — they go from "needs one account" to "needs admin on a box." The practice task Kerberoasts your lab.

## What a credential attack is
<!-- bite: 58b50a5d-bbc3-4a14-bf0a-9f103b5c8417 -->

In Windows networks you rarely need to *know* someone's password. You need their password *hash* or a *ticket*, both of which work just as well as the password itself: NTLM authenticates with the hash directly, and Kerberos tickets are accepted on sight. So credential attacks are about harvesting these password-equivalents — stealing them from a machine's memory, capturing them off the wire, or forcing the system to hand you something crackable. This lesson is the four main ways to do it, roughly in order of how little you need to start.

## The kid version
<!-- bite: 9baf1b95-ebf4-4b5d-af4e-c4efedc1fbcd -->

In Windows networks you often don't need to *know* someone's password — you need their password *hash*, or a *ticket*, both of which work just as well as the password itself. So credential attacks are about harvesting these password-equivalents: stealing them from memory, capturing them off the wire, or forcing the system to hand you something crackable.

**"The hash is as good as the password" is the single idea behind most of this.**

## 1. Kerberoasting — the most reliable AD attack
<!-- bite: b4c9976b-2a78-48f0-9ca6-a7cb9b75c9b7 -->

Recall from [[cybersecurity/12-active-directory/02-authentication-and-kerberos|Kerberos]]: a service ticket is encrypted with the *service account's* password hash, and **any authenticated user can request one.**

```text
GetUserSPNs.py corp.local/alice:Password1 -request -dc-ip 10.0.0.1
   → dumps a $krb5tgs$ hash for every service account with an SPN
hashcat -m 13100 hashes.txt rockyou.txt
   → crack them offline, at whatever speed your GPU allows
```

## Why Kerberoasting works so well
<!-- bite: 03cbfdac-a6e1-451c-bd33-366c201731c1 -->

- Needs only *one* valid domain account — no privilege.
- Service accounts are frequently set up with **weak, human-chosen, non-expiring passwords** (`Summer2019!`, the company name).
- Cracking is **offline** — no lockout, no logging on the DC beyond a normal ticket request.
- Service accounts are often **over-privileged** (local admin everywhere, sometimes Domain Admin).

**This is usually the first thing to try after getting any credential.** It's low-noise, low-risk, and frequently yields a high-value account.

## 2. AS-REP Roasting — no credentials needed
<!-- bite: 1be4ef1e-c1ee-4302-bb69-356c3a02ae13 -->

If an account has **"Kerberos pre-authentication not required"** set (a legacy compatibility option), the KDC will send an AS-REP — encrypted with that account's password hash — to *anyone who asks*, without proving they're that user.

```text
GetNPUsers.py corp.local/ -usersfile users.txt -no-pass -dc-ip 10.0.0.1
   → for any pre-auth-disabled account, dumps a $krb5asrep$ hash
hashcat -m 18200 hashes.txt rockyou.txt
```

**This needs no credentials at all** — just a list of usernames (from OSINT, kerbrute, or a null session). Rarer than Kerberoastable accounts, but a genuine no-auth foothold when present.

## 3. Pass-the-Hash — skip cracking entirely
<!-- bite: 50ee20b2-5951-4c56-9987-3035be62cca5 -->

Because **NTLM authenticates with the hash directly** ([[cybersecurity/12-active-directory/02-authentication-and-kerberos|02]]), if you steal an NTLM hash you can authenticate *as that user without ever cracking it*:

```text
nxc smb 10.0.0.0/24 -u administrator -H <NTLM_hash>
   → authenticates as administrator to every box that accepts that hash
psexec.py -hashes :<NTLM_hash> administrator@10.0.0.5
   → a shell, no password
```

**This is why a stolen hash is a full compromise, not a puzzle to solve.** It's also why **local admin password reuse is catastrophic** — the same local admin hash on 500 machines means one hash owns all 500. (Microsoft's **LAPS** exists precisely to randomise local admin passwords per machine → [[cybersecurity/12-active-directory/06-defending-active-directory|defending AD]].)

**Pass-the-Ticket** is the Kerberos equivalent — steal or forge a ticket and inject it into your session (`Rubeus`, `mimikatz`).

## 4. Harvesting credentials from a machine
<!-- bite: f749e236-352a-4180-9c8b-2f999665705f -->

Once you have admin on a box, you loot it for credentials to *other* accounts:

- **mimikatz** — the famous tool. `sekurlsa::logonpasswords` dumps hashes (and, on older/misconfigured systems, plaintext passwords via WDigest) of everyone logged into that machine from LSASS memory. **A Domain Admin logged into a server you own = their credentials in your hands**
- **LSASS dump** — snapshot the LSASS process memory (comsvcs.dll, Task Manager, nanodump) and parse it offline with mimikatz/pypykatz. **Quieter than running mimikatz directly**, which every EDR flags
- **SAM + SYSTEM** — the local account database; `secretsdump.py` extracts local hashes
- **DPAPI** — decrypt saved browser passwords, Wi-Fi keys, RDP credentials
- **Files** — config files, scripts, and `SYSVOL` (the old **GPP `cpassword`** bug stored an AES-encrypted password with a *publicly known key* in group policy — still found in legacy environments)

**Harvesting is the engine of lateral movement:** each machine you own yields credentials to accounts that own *other* machines → [[cybersecurity/12-active-directory/05-lateral-movement-and-escalation|lateral movement]].

## Getting the first credential (pre-foothold)
<!-- bite: 7f74f2f3-ac79-41fe-9016-85a1024c74fa -->

Before any of the above, you need *one* credential. The usual doors:

- **Password spraying** — try *one* common password (`Winter2025!`) against *many* users. Stays under the lockout threshold that guessing many passwords against one user would trip. `nxc`, `kerbrute`
- **Responder** — poison LLMNR/NBT-NS to capture NTLMv2 hashes when a machine mistypes a share name → crack, or relay
- **NTLM relay** (`ntlmrelayx`) — relay a captured authentication to another service instead of cracking it — **no cracking needed** if SMB signing isn't enforced
- **Phishing** → [[cybersecurity/06-attacks-and-threats/01-social-engineering|social engineering]]
- **Found credentials** — password reuse, credentials in code, breach dumps → [[cybersecurity/10-protecting-yourself/02-passwords-and-the-manager|the reuse problem]]

## Cracking, practically
<!-- bite: cbf8d145-c33d-445c-93a6-9aabe6780741 -->

```text
hashcat -m 13100 kerb.txt rockyou.txt -r rules/best64.rule   # Kerberoast
hashcat -m 1000  ntlm.txt rockyou.txt                        # raw NTLM
```

**NTLM hashes are unsalted and fast to crack** — billions per second on a GPU — which is a reason the *hash* is the target, not the plaintext. Wordlists + rules beat brute force. `hashcat`'s mode number depends on the hash type; knowing `-m 13100` (Kerberoast), `-m 18200` (AS-REP), `-m 1000` (NTLM) covers most of it → [[cybersecurity/05-cryptography/06-cryptographic-attacks-and-best-practices|cracking]].

## Key insight
<!-- bite: 31cc013e-d456-4c6b-83d7-f1c43cef5f01 -->

**In AD, a hash or a ticket is a password-equivalent, so credential attacks aim to harvest those rather than to learn passwords** — Kerberoasting hands you an offline-crackable hash for any service account, pass-the-hash skips cracking entirely, and mimikatz loots the credentials of everyone logged into a machine you own. The engine of a whole-domain compromise is that each machine yields credentials to accounts that own other machines, so the attack compounds: one weak service password becomes Domain Admin in a few hops.

## Terms used in this lesson
<!-- bite: df9a033e-fe45-4410-91da-9f8354b5fd5e -->

1. **Kerberoasting**: Requesting service tickets for accounts with an SPN and cracking them offline, because each is encrypted with the service account's password hash. The most reliable AD attack; needs only one valid account.
2. **AS-REP roasting**: Requesting the AS-REP of an account that has Kerberos pre-authentication disabled and cracking it offline — no credentials needed, just a username.
3. **Pass-the-hash**: Authenticating with a stolen NTLM hash directly, without ever cracking it to a password.
4. **Pass-the-ticket**: The Kerberos equivalent — injecting a stolen or forged ticket into your session.

## Terms used in this lesson: harvesting and cracking
<!-- bite: 96442e16-f7bc-45dc-b3f9-7b7d699d49e7 -->

5. **mimikatz**: The tool that dumps hashes (and sometimes plaintext passwords) of everyone logged into a machine you have admin on, from LSASS memory.
6. **LSASS**: The Windows process that holds the credentials of logged-in users in memory. Dumping it is how you harvest those credentials.
7. **Password spraying**: Trying one common password against many users, staying under the lockout threshold — a common way to get the *first* credential.
8. **`hashcat` mode**: The `-m` number that tells hashcat which hash type it's cracking — `13100` Kerberoast, `18200` AS-REP, `1000` raw NTLM.

## Check your understanding
<!-- bite: a2a0c482-e3ca-4c13-b4d6-5dda33016ae0 -->

Try each one before you open the answer.

1. <!-- q: mcq id="10b18a0d" -->
   What is the minimum an attacker needs to Kerberoast every service account in a domain?

   - [ ] Domain Admin rights
   - [ ] Admin on a Domain Controller
   - [x] One valid domain account of any privilege
   - [ ] Physical access to the DC

   <details><summary>Answer</summary>

   Any authenticated user can request a service ticket for any SPN, and that ticket is encrypted with the service account's hash. So one ordinary account — from a spray or a phish — is enough to collect crackable hashes for every service account. No privilege required.

   </details>

2. <!-- q: mcq id="5139f6ee" -->
   Why is a stolen NTLM hash described as "a full compromise, not a puzzle to solve"?

   - [ ] NTLM hashes are trivially reversible to plaintext.
   - [x] NTLM authenticates with the hash directly, so you can pass-the-hash and log in as that user without ever cracking it.
   - [ ] The hash contains the password in base64.
   - [ ] Windows emails you the password when you present the hash.

   <details><summary>Answer</summary>

   You don't need the plaintext. Because NTLM proves knowledge of the hash, you authenticate *with the hash itself* (pass-the-hash). This is also why local-admin password reuse is catastrophic: one reused hash owns every machine that accepts it.

   </details>

3. <!-- q: exact id="fecced8f" answer="18200" -->
   You've dumped a `$krb5asrep$` hash from an account with pre-authentication disabled. Which `hashcat -m` mode cracks it? (Give the number.)

   <details><summary>Answer</summary>

   18200. Kerberoast (`$krb5tgs$`) is `-m 13100`, AS-REP (`$krb5asrep$`) is `-m 18200`, and raw NTLM is `-m 1000`. Knowing these three covers most AD cracking.

   </details>

4. <!-- q: mcq id="71a76303" -->
   AS-REP roasting is unusual among these attacks because it:

   - [ ] Requires Domain Admin to work
   - [x] Needs no credentials at all — just a username for an account with pre-auth disabled
   - [ ] Only works against Domain Controllers
   - [ ] Cannot be cracked offline

   <details><summary>Answer</summary>

   If an account has "pre-authentication not required" set, the KDC hands its AS-REP (encrypted with that account's hash) to anyone who asks, without proof of identity. So with just a username list you can collect crackable hashes — a genuine no-credential foothold when such an account exists.

   </details>

5. <!-- q: gap id="335ce62e" answers="LSASS|lsass" -->
   Once you have admin on a machine, mimikatz dumps the credentials of everyone logged into it from the ___ process's memory — which is why a Domain Admin logged into a box you own is game over.

   <details><summary>Answer</summary>

   LSASS. It holds logged-in users' credentials in memory, so dumping it (or snapshotting it and parsing offline) harvests those credentials. A DA session on a machine you control hands you their credentials.

   </details>

6. <!-- q: open id="d20c369b" -->
   Explain how machine harvesting makes credential attacks "compound" into a whole-domain compromise.

   <details><summary>Answer</summary>

   Each machine you own yields the credentials of the users logged into it, and those users are often admins on *other* machines. So you harvest on box A, use those credentials to move to box B, harvest there to reach box C, and so on — each hop giving credentials to accounts with more reach. One weak service password becomes Domain Admin in a few hops, because the attack feeds itself rather than needing a fresh exploit each time.

   </details>

## Practice — Kerberoast your lab
<!-- bite: 8091ec19-3da0-487b-bb3c-dc96ffe4e396 -->

Use the service accounts you listed during enumeration.

- Request the tickets: `GetUserSPNs.py corp.local/lowpriv:'pass' -request -dc-ip <DC-IP> -outputfile kerb.txt`.
- Crack them: `hashcat -m 13100 kerb.txt rockyou.txt -r /usr/share/hashcat/rules/best64.rule`.
- If GOAD's service accounts crack (they're deliberately weak), note which account you recovered and check in BloodHound what it's admin on.
- **Done when:** you've cracked at least one service account on your lab, and you can state the `-m` mode and why the cracking happened offline with nothing logged on the DC beyond a normal ticket request.

## Before moving on
<!-- bite: 3c3060c0-5de8-4afc-b620-9d4e56d2f006 -->

You should be able to run all four techniques, say what each needs to start, pick the right `hashcat` mode, and explain why harvesting compounds one weak password into Domain Admin. You now *have* credentials; next you spend them.

Next: [[cybersecurity/12-active-directory/05-lateral-movement-and-escalation|lateral movement and escalation]] — using the credentials you harvested to move between machines and climb to Domain Admin.

## Related
<!-- bite: 7efcf9f8-1ff4-46d0-a634-bcc8f5a01cff -->
- [[cybersecurity/12-active-directory/05-lateral-movement-and-escalation|lateral movement]] — spending the credentials you harvested
- [[cybersecurity/12-active-directory/02-authentication-and-kerberos|Kerberos]] — why service tickets are crackable
- [[cybersecurity/05-cryptography/06-cryptographic-attacks-and-best-practices|cryptographic attacks]] — offline cracking
- [[cybersecurity/12-active-directory/06-defending-active-directory|defending AD]] — LAPS, managed service accounts, tiering

## About this lesson
<!-- bite: 60b6ddb2-a09c-4510-af34-7fe3cf611ea4 -->

**Level:** Advanced. **Covers:** the four techniques that turn one foothold into more accounts, and why "hash = password" is the recurring theme.

*Source: [reference] — Aug 2026.*
