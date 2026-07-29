# Career Path & Best Practices — Getting to Senior Level

"Senior" in this field isn't a tool checklist — it's the difference between running a scanner and knowing *why* a finding matters, chaining small issues into a serious attack path, and writing a report that gets budget approved. This note maps the skill progression and the habits that actually separate junior from senior, on top of everything else in this folder.

## The skill progression, roughly in order

1. **Networking fundamentals** — TCP/IP, DNS, HTTP, routing. Every tool in [[08-common-tools|common-tools]] is automating an interaction with these underlying protocols; you can't reason about *why* a scan or exploit works without this.
2. **Linux proficiency** — the filesystem, permissions, processes, shell scripting. Nearly all serious tooling runs on Linux, and comfort with it stops being a barrier to focusing on the actual security concept.
3. **Scripting (Python and/or Bash)** — the point where you stop being limited to whatever existing tools happen to do, and can write a quick script to test a specific idea, parse tool output, or automate a repetitive step.
4. **How the web actually works** — HTTP requests/responses, cookies/sessions, how a browser and server communicate — required before [[07-exploitation-concepts|exploitation-concepts]]'s web-focused categories (injection, XSS, broken access control) make deep sense rather than being memorized patterns.
5. **Reading code** — not necessarily writing production software, but being able to read source (in whatever language a target application is written in) and spot where user input reaches a dangerous sink, which is the actual skill behind finding *novel* vulnerabilities instead of only recognizing known ones.
6. **Structured practice** — CTFs, HackTheBox, TryHackMe (see [[04-lab-setup-and-os-choice|lab-setup-and-os-choice]]) — deliberately practicing the full methodology in [[02-penetration-testing-methodology|penetration-testing-methodology]] against realistic, legal targets, repeatedly, until it's second nature rather than a checklist you're consciously working through.
7. **Formal validation (optional but common)** — certifications, covered below, as a way to structure learning and signal competence, not a substitute for the hands-on practice in step 6.
8. **Specialization** — most senior practitioners go deep in one or two areas (web application security, network/infrastructure, mobile, cloud security, red teaming, reverse engineering/malware analysis) rather than staying a generalist indefinitely — depth in a chosen area is usually what "senior" actually signals in practice.

## Certifications worth knowing about

- **CompTIA Security+** — broad, entry-level, more theoretical; a reasonable starting credential if you're new to IT/security generally.
- **CEH (Certified Ethical Hacker)** — broad conceptual coverage of tools and methodology; useful as a structured overview, criticized by some practitioners for being more knowledge-recall than hands-on skill.
- **OSCP (Offensive Security Certified Professional)** — heavily hands-on, exam-based (you actually compromise machines in a timed practical exam, not multiple choice); widely regarded in the industry as a strong, credible signal of real practical skill, and a common target once the fundamentals above are solid.
- Beyond OSCP: more specialized offensive-security certifications exist per specialization (web, mobile, exploit development) — worth researching once you know which specialization you're pursuing, not before.

Certifications matter most for getting past HR filters and validating structured knowledge — they don't replace the hands-on repetition from step 6 above, and plenty of highly capable practitioners are certification-light but portfolio-heavy (see below).

## What actually separates senior from junior in practice

- **Root-cause understanding over tool output** — a junior reports "the scanner flagged this"; a senior explains *why* it's a real vulnerability, what conditions make it exploitable, and what specifically fixes it — the same distinction covered in [[09-post-exploitation-and-reporting|post-exploitation-and-reporting]] between a shallow finding and a fully investigated one.
- **Chaining low-severity findings into real impact** — three individually "low" findings (a verbose error message, a predictable ID scheme, a missing rate limit) can combine into a serious account-takeover path — recognizing these chains is a senior-level skill that pure tool output won't hand you.
- **Communication and reporting** — the ability to write a report an executive will act on (see [[09-post-exploitation-and-reporting|post-exploitation-and-reporting]]) is as much a senior skill as the technical finding itself; a brilliant finding that's poorly communicated gets deprioritized and never fixed.
- **Staying current** — following CVE disclosures, security research blogs, and conference talks (DEF CON, Black Hat, and their published papers/talks) — the field changes fast enough that stale knowledge from a few years ago misses entire classes of modern vulnerability.
- **Writing your own tools when existing ones fall short** — the scripting skill from step 3 above, applied: a senior practitioner isn't limited to what Metasploit or Burp Suite ship with out of the box.
- **Understanding the defensive side** — knowing how a blue team actually detects and responds (logging, SIEM alerting, EDR) makes offensive testing sharper, since you can reason about what would and wouldn't get noticed, rather than just running the loudest available tool.

## Building a visible portfolio

Since a lot of the work happens under NDA (real client engagements aren't publishable), visible proof of skill tends to come from: CTF competition results and public writeups, a HackTheBox/TryHackMe public rank, bug bounty reports (through official, sanctioned platforms like HackerOne or Bugcrowd — inherently authorized by the platform's own program terms), open-source security tool contributions, and technical blog posts breaking down a vulnerability class or a CTF challenge in depth. This is often what actually gets a junior noticed for a first role, more than certifications alone.

## Best practices, restated as a mindset rather than a rule list

- **Authorization always comes first** — not as a legal formality to get past, but as the actual ethical core of the discipline (see [[01-rules-of-engagement-and-legal|rules-of-engagement-and-legal]]); this is the difference between the entire skill set described in this folder being a career or a crime.
- **Document everything as you go**, not just at report time — screenshots, commands run, timestamps — both for the eventual report and so you can reconstruct exactly what you did if a question comes up later.
- **Minimize impact** — prefer the least disruptive way to prove a finding (demonstrating that an injection is possible, rather than actually deleting data to prove it); this is a professional norm as much as a scope requirement.
- **Treat "senior" as a direction, not a destination** — the field's tools and vulnerability landscape keep shifting; the habit of continuous learning described above is itself the senior-level skill, more than any specific technique mastered today.

## Related
- [[02-penetration-testing-methodology|penetration-testing-methodology]]
- [[09-post-exploitation-and-reporting|post-exploitation-and-reporting]]
- [[04-lab-setup-and-os-choice|lab-setup-and-os-choice]]
- [[01-rules-of-engagement-and-legal|rules-of-engagement-and-legal]]
