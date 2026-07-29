# Ethical Hacking

Offensive security, done with explicit authorization, to find weaknesses before someone without authorization does. Every note here assumes the authorization step in [[01-rules-of-engagement-and-legal|rules-of-engagement-and-legal]] has already happened — that's what makes this "ethical hacking" rather than a crime using identical techniques.

## Reading order
1. [[01-rules-of-engagement-and-legal|rules-of-engagement-and-legal]] — **[Beginner]** — authorization, scope, the legal frameworks involved — read this first, not last
2. [[02-penetration-testing-methodology|penetration-testing-methodology]] — **[Beginner]** — the overall phase structure everything else fits into
3. [[03-reconnaissance|reconnaissance]] — **[Beginner]** — passive/active info-gathering, OSINT
4. [[04-lab-setup-and-os-choice|lab-setup-and-os-choice]] — **[Beginner]** — Kali/Parrot vs vanilla Linux, VM vs bare metal, the Wi-Fi adapter monitor-mode gotcha, building a home lab
5. [[05-home-lab-setup|home-lab-setup]] — **[Beginner]** — the concrete build: VirtualBox + Kali + Metasploitable2 + DVWA on an isolated host-only network, step by step, ready to attack tonight
6. [[06-scanning-and-enumeration|scanning-and-enumeration]] — **[Intermediate]** — mapping what's reachable and running, vulnerability scanning
7. [[07-exploitation-concepts|exploitation-concepts]] — **[Intermediate]** — the major vulnerability categories and why each works mechanically (injection, broken auth, XSS, broken access control, memory-safety bugs, misconfigurations)
8. [[08-common-tools|common-tools]] — **[Intermediate]** — the standard tool landscape (Nmap, Burp Suite, Metasploit, etc.) and where to legally practice (HackTheBox, TryHackMe, CTFs)
9. [[09-post-exploitation-and-reporting|post-exploitation-and-reporting]] — **[Intermediate]** — determining real impact and writing a report that actually gets things fixed
10. [[10-pdf-and-document-security|pdf-and-document-security]] — **[Intermediate]** — the same offline-cracking pattern applied to password-protected files you own
11. [[11-wifi-security-testing|wifi-security-testing]] — **[Advanced]** — WPA2/WPA3 handshake cracking, WPS weaknesses, testing your own network specifically
12. [[12-practice-exercises|practice-exercises]] — **[Intermediate]** — goal-only hands-on drills against the lab from [[05-home-lab-setup|home-lab-setup]] — this is the one that actually tests whether the rest of this folder transferred into a skill
13. [[13-practice-exercises-solutions|practice-exercises-solutions]] — **[Intermediate]** — worked, step-by-step solutions to every task above — check here after attempting each one yourself, not before
14. [[14-career-path-and-best-practices|career-path-and-best-practices]] — **[Intermediate]** — the skill progression to senior level, certifications, what actually separates senior from junior

## Related
- [[cybersecurity/README|cybersecurity curriculum map]]
- [[03-attacker-and-hacker-types|attacker-and-hacker-types]] — white/grey/black hat, and why the distinction is authorization, not skill
