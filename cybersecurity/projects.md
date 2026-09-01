# Cybersecurity — Projects

*Security is learned by doing — safely and legally, on systems you own or are explicitly authorised to test. **[[cybersecurity/02-ethical-hacking/01-rules-of-engagement-and-legal|Read the rules of engagement note first]]**; the technical skill and the legal exposure scale together.*

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

## The ladder

- 🟢 ⭐ **Secure one of *your own* apps** — threat-model it, fix its [[cybersecurity/06-attacks-and-threats/03-web-application-attacks|OWASP Top 10]] issues, add [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy|security headers]], scan its dependencies, get secrets out of the repo. Highest relevance — it hardens real work and teaches app-sec, the natural security path for a developer.
- 🟢 **Build a home lab** — a VM lab ([[cybersecurity/02-ethical-hacking/05-home-lab-setup|home lab setup]]) with Kali + a deliberately-vulnerable target (Juice Shop, DVWA, Metasploitable), isolated from your real network. The sandbox for everything below.
- 🟢 **Capture the Flag** — work a beginner path on TryHackMe / HackTheBox / picoCTF. The fastest, most fun way to build hands-on offensive intuition ([[cybersecurity/02-ethical-hacking/12-practice-exercises|practice]]).
- 🟡 **Stand up a SIEM and catch an attack** — deploy Wazuh or Elastic Security, ship logs to it, run a benign attack against your lab target, and *write the detection rule* that catches it ([[cybersecurity/07-security-operations/02-logging-siem-and-detection|logging & SIEM]]). Real blue-team reps.
- 🟡 **Authorized web-app pentest + report** — pentest a vulnerable app you host, then write a professional [[cybersecurity/02-ethical-hacking/09-post-exploitation-and-reporting|findings report]]. The report is the actual deliverable of the job.
- 🟡 **Harden a server to CIS + an IR runbook** — take a fresh VM, harden it to a [[cybersecurity/08-governance-risk-and-compliance/01-risk-and-frameworks|CIS benchmark]], verify it; and write an [[cybersecurity/07-security-operations/04-incident-response|incident-response runbook]] for a scenario, then tabletop it.
- 🔴 **Detection engineering from ATT&CK** — pick a [[cybersecurity/07-security-operations/03-threat-intelligence-and-hunting|MITRE ATT&CK]] technique, emulate it in your lab, and build the detection that fires on it. The core skill of a modern blue team.


## The platforms that actually build the skill

Notes give you the map. **These give you the reps, and they're where the hours should go:**

- 🟢 ⭐ **PortSwigger Web Security Academy** — free, and the best security learning resource that exists. Maps directly onto [[cybersecurity/04-web-security/README|web security]] and [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|exploitation concepts]]. **Done when:** you've cleared the SQLi, XSS, and access-control paths.
- 🟡 ⭐ **Break an API's authorization** — spin up **crAPI** (OWASP's vulnerable API) or PortSwigger's API/access-control labs, and with two accounts find a **BOLA** (swap object IDs) and a **BFLA** (call an admin route). **Done when:** you've read another user's data by changing an ID, and you can state the server-side fix → [[cybersecurity/14-api-security/03-authorization-and-bola|API authorization]]. **The #1 real-world API bug.**
- 🟢 **TryHackMe** → 🟡 **HackTheBox** — guided, then unguided. **Done when:** you've rooted a box with no walkthrough.
- 🟡 **picoCTF / a live CTF** — where it stops being exercises. **Done when:** you've solved something nobody handed you.
- 🟡 **Write the walkthrough** — for every box you root, write the report as if for a client → [[cybersecurity/02-ethical-hacking/09-post-exploitation-and-reporting|reporting]]. **The report is the actual deliverable of the job**, and almost nobody practises it.

**The two things OSCP and real corporate pentests are mostly made of** now have their own sections — build reps against them:

- 🟡 ⭐ **Own a domain in GOAD** — stand up [Game of Active Directory](https://github.com/Orange-Cyberdefense/GOAD) (a free, deliberately-vulnerable AD lab), get one foothold, run BloodHound, and walk a path to Domain Admin. **Done when:** you've DCSync'd KRBTGT and forged a Golden Ticket → [[cybersecurity/12-active-directory/README|active directory]].
- 🟢 ⭐ **Climb ROP Emporium** — ret2win → ret2libc → ROP, one concept per challenge, with pwntools. **Done when:** you've written a working ROP chain against a No-PIE binary → [[cybersecurity/11-binary-exploitation/README|binary exploitation]].
- 🟡 **pwn.college and how2heap** — the structured path through memory, shellcode, ROP and the heap. **Done when:** you've popped a shell via tcache poisoning.
- 🟢 ⭐ **Reverse a crackme** — take a binary from crackmes.one or a CTF `rev` challenge into Ghidra, find the check, and recover the password *without running it*. **Done when:** you've read the logic from the decompiler and beaten it → [[cybersecurity/13-malware-and-reverse-engineering/02-static-analysis|static analysis]]. **Zero infection risk — start here.**
- 🟡 ⭐ **Analyse a real sample in an isolated lab** — build FLARE VM + REMnux with host-only networking and FakeNet, then triage a MalwareBazaar sample: hash-check, strings, imports, sandbox run, and **write a YARA rule** for it. **Done when:** you have IOCs and a rule that would catch it → [[cybersecurity/13-malware-and-reverse-engineering/06-the-malware-analysis-workflow|the workflow]]. **Only once your lab isolation is solid.**


## If you only do one

**PortSwigger's Academy, then secure your own app.** The first builds offensive intuition for free; the second is the defensive rep that's directly relevant to the work you actually do.


## Related

- [[cybersecurity/README|the cybersecurity course]] · [[cybersecurity/interview/README|interview bank]]
- [[cybersecurity/02-ethical-hacking/12-practice-exercises|ethical hacking exercises]]
- [[cybersecurity/02-ethical-hacking/05-home-lab-setup|home lab setup]] — build this first
- [[project-ideas|Project Ideas]] — the vault-wide index
