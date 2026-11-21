---
id: 76e4a488-6d24-4cce-bcd4-304f02a76eeb
---

# Credential Attacks

A credential attack is collecting the things that prove who someone is, such as password hashes and login tickets, so you can act as them. In Windows networks you often do not need the real password, because the hash or the ticket works just as well. This lesson goes through the four main ways attackers collect them.

## The kid version first
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

**Why it works so well:**
- Needs only *one* valid domain account — no privilege
- Service accounts are frequently set up with **weak, human-chosen, non-expiring passwords** (`Summer2019!`, the company name)
- Cracking is **offline** — no lockout, no logging on the DC beyond a normal ticket request
- Service accounts are often **over-privileged** (local admin everywhere, sometimes Domain Admin)

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
