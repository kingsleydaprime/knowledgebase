---
id: 82bca27d-f5e4-449b-8331-6c81ddf03b02
---

# Ethical Hacking — Practice Exercises

**Goal-only drills against your own lab — you're told the objective, not the commands, because a real engagement doesn't hand you the payload either.** This is the file that tests whether the section became a *skill* rather than a set of notes. Run every one against the lab from [[cybersecurity/02-ethical-hacking/05-home-lab-setup|lesson 05]] — **never against anything you don't own**, per [[cybersecurity/02-ethical-hacking/01-rules-of-engagement-and-legal|rules of engagement]].

## How to use this
<!-- bite: 049276f6-029c-4b2f-b539-66be7ecb8e65 -->

- **Targets.** The web drills run against **Juice Shop** (tier 1 — everyone has it). The network drills need a multi-service host: your **VPS**, or **Metasploitable** from the three-VM alternative lab. The cracking drills use files and a database **you create**. Wireless is **your own router**.
- **Try before you look.** Reach for [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|exploitation concepts]] and [[cybersecurity/02-ethical-hacking/08-common-tools|common tools]] before any walkthrough. The goal is transferable skill, not memorising one target. Solutions are in [[cybersecurity/02-ethical-hacking/13-practice-exercises-solutions|lesson 13]] — after you've tried.
- **Snapshot / reset first.** Restart the Juice Shop container, or revert a VM/VPS to its `clean` snapshot, before a drill that leaves the target broken.
- **Finish every drill the senior way.** For each one, write a one-paragraph note: what you found, how, **the fix, and the detection that would catch it**. That fix-and-detect habit (stage 7 of the [[cybersecurity/02-ethical-hacking/02-penetration-testing-methodology|loop]]) is the actual difference between "ran a tool" and "did a pentest".

## Reconnaissance and scanning
<!-- bite: deb1c9a1-e843-468c-99e6-c3690cbdf7a7 -->

1. Against your Juice Shop, build a map of the attack surface **from the browser and content enumeration only** — the stack, the API prefixes, and any path the UI doesn't link to.
   **Verify:** a written list of at least five endpoints/paths, each noted as "where it came from" (header, `robots.txt`, `ffuf`, Network tab).

2. Against a host target (your VPS or Metasploitable), determine every open TCP port and the service + version on each, without exploiting anything yet.
   **Verify:** a written port → service → version list; flag anything exposed that shouldn't be (a database, an admin service).

3. From that service list, identify a service running a version with a **publicly documented, named vulnerability** (an actual CVE, not just "old").
   **Verify:** you can name the vulnerability and cite where you confirmed it (`searchsploit`, a CVE database).

## Web exploitation — Juice Shop
<!-- bite: 7ca1ef5c-d16a-4065-9885-93c16c38c680 -->

4. Log in as the administrator **without knowing the password**, through the login form.
   **Verify:** you're logged in as admin; you can state the exact input you used and *why* it worked (which part became SQL).

5. Using the product search, extract data the search was never meant to return (e.g. a table it shouldn't reach), first **by hand** before any automated tool.
   **Verify:** the extracted data, plus the exact injected input.

6. Read **another user's** data (e.g. their basket) by changing an identifier in a request, without ever being granted that access.
   **Verify:** the exact parameter/id you changed and the unauthorized data it returned (capture the request/response in Burp).

7. Find an XSS in the search (or another reflected field) and demonstrate impact **beyond** a plain `alert()` — describe precisely what a real payload would exfiltrate.
   **Verify:** a working payload plus one sentence on what it would let an attacker do in a real victim's browser.

8. Confirm the injection from exercise 5 with an **automated tool** and enumerate more of the schema than you pulled by hand.
   **Verify:** a list of tables/columns the tool extracted, and the authenticated option (cookie/token) you had to pass it.

## Network exploitation — host target (optional)
<!-- bite: 6d28eeed-e561-4726-9be6-4128c21e3c8f -->

*Needs Metasploitable (the three-VM alternative lab) or another deliberately-vulnerable host you own. Juice Shop is a single web app and won't give a host shell.*

9. Gain a remote shell on the host using one of the named vulnerabilities from exercise 3, via an exploitation framework rather than a hand-written exploit.
   **Verify:** a working shell with `whoami` returning a result, and the specific CVE you used.

10. Determine the privilege level you landed at, and — if not already root — escalate.
    **Verify:** `id` shows `uid=0(root)`.

11. Gain a shell via an **entirely different** vulnerable service than exercise 9 — don't reuse the technique.
    **Verify:** a second, independent shell via a different named vulnerability.

## Password and offline cracking — your own files
<!-- bite: a3b37461-bd2c-4bda-809c-04f41e900c10 -->

12. Seed a throwaway database (or a text file) with a handful of **dummy** accounts whose passwords you hashed yourself (some weak, one long-random). Extract the hashes and crack what you can offline.
    **Verify:** the weak passwords recovered, the strong one *not* recovered, and the hash format you identified before choosing a mode.

13. Lock a PDF **you created** with AES-256 and a weak password; extract its hash and crack it. Then repeat with a long random password and confirm it resists.
    **Verify:** the weak one cracked (with a rough time), the strong one not — and one line on why.

14. If a host service accepts logins over the network, demonstrate a successful login using a **wordlist-based** attack (not a guess), against your own host.
    **Verify:** a successful authenticated session plus the username/password pair the attack found.

## Wireless — your own network
<!-- bite: 8ebc8217-293b-4fb2-9f68-8956c69e565a -->

*Your own router and devices only. Needs a monitor-mode adapter → [[cybersecurity/02-ethical-hacking/04-lab-setup-and-os-choice|lesson 04]].*

15. Temporarily set your router's passphrase to a weak one in `rockyou.txt`, capture a WPA2 handshake (deauth one of **your** devices if needed), and crack it offline — proving your pipeline before you'd trust it against an unknown passphrase.
    **Verify:** the recovered key matches your configured password. Restore your real passphrase afterward.

16. Check whether your network has WPS enabled, and state what it means for practical security regardless of passphrase strength.
    **Verify:** a clear yes/no on WPS plus a one-sentence risk statement.

## Reporting
<!-- bite: 22a42ab7-25ac-4880-acca-87329b7c3304 -->

17. Take the web drills you completed (4–8) and write them up as a short-form findings report, structured the way [[cybersecurity/02-ethical-hacking/09-post-exploitation-and-reporting|lesson 09]] describes: title, description, steps to reproduce, evidence, impact, **remediation, and detection**. Rank them by severity (likelihood × impact).
    **Verify:** someone who wasn't there could read it, reproduce each finding, understand why it matters, apply the fix — and you named the detection gap for at least one. **This is the deliverable the whole section builds toward.**

## Hosted platforms — once the lab feels routine
<!-- bite: 6cdd80dc-0f5e-4dd1-96e8-1659e0b5b6ce -->

[[cybersecurity/02-ethical-hacking/08-common-tools|Common tools]] points at **PortSwigger's Web Security Academy** (free, the best web practice there is), **HackTheBox** and **TryHackMe**. The natural next step after this file: pick one beginner machine/room per category above and repeat the same drills against a target **you didn't build**. That's the real test of whether the skill transferred, or whether you just memorised Juice Shop and Metasploitable specifically.

## Related
<!-- bite: 0b7d4a99-19d1-4184-8939-0d9b6369ae65 -->

- [[cybersecurity/02-ethical-hacking/13-practice-exercises-solutions|Solutions]] — after you've attempted each drill, not before.
- [[cybersecurity/02-ethical-hacking/05-home-lab-setup|Home lab setup]] — the lab these run against.
- [[cybersecurity/02-ethical-hacking/09-post-exploitation-and-reporting|Post-exploitation and reporting]] — the shape of exercise 17.

## About this page
<!-- bite: 2000570d-8ed0-4fa2-9ae0-cdf613831786 -->

**Level:** Intermediate. **What this is:** a goal-only drill bank (no walkthroughs here — they're in [[cybersecurity/02-ethical-hacking/13-practice-exercises-solutions|lesson 13]]) covering recon, web exploitation (Juice Shop), network exploitation (optional host), offline cracking (your own files), wireless (your own network) and reporting. **Where it sits:** lesson 12 of the [[cybersecurity/02-ethical-hacking/index|Ethical Hacking]] section — the test of whether the section became a skill. Retargeted from the original Metasploitable/DVWA bank to the Juice Shop + optional-host lab. Runs are tracked in `cybersecurity/LIVE-RUNS-TODO.md`.
