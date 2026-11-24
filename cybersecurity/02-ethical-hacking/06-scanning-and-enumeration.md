---
id: 5571bc7f-99a5-452e-8ab6-482c3d1ca7e9
---

# Scanning and Enumeration

**Scanning and enumeration is going from "roughly what's there" to an exact map: which hosts are alive, which ports are open, which service and version sits on each, and what each service will tell you about itself when asked directly.**

## Before you start
<!-- bite: e2aed982-d542-41a6-8650-d3971d0dd75e -->

You should have:

- A target live: Juice Shop on `localhost:3000`, and ideally a VPS → [[cybersecurity/02-ethical-hacking/05-home-lab-setup|home lab setup]].
- `nmap` installed on your attacker box.

After this lesson you will be able to:

1. Scan a host for open ports and identify the service and version on each.
2. Explain why a version number alone can be a finding.
3. Enumerate a web app's hidden paths and endpoints, and say why that's the web equivalent of port scanning.
4. Tell port scanning, enumeration and vulnerability scanning apart, and know which is noisiest.

**Study route.** Kid version and §1–5, then the two worked examples (nmap on a host, directory enumeration on Juice Shop), then the practice task.

## What scanning and enumeration is
<!-- bite: 6f167a37-abe9-4d6c-9a9f-65ae388c3208 -->

It's stage 3 of the [[cybersecurity/02-ethical-hacking/02-penetration-testing-methodology|engagement loop]], and it turns [[cybersecurity/02-ethical-hacking/03-reconnaissance|recon]]'s rough picture into a concrete list of things to attack.

## The kid version
<!-- bite: 00e152c7-a4d2-49c0-86b5-7a3156bad4be -->

Imagine checking out a building you're allowed to survey. First you walk every side and write down which doors and windows actually exist and which are open — not what's inside yet, just which openings are there (that's port scanning). Then, at each open door, you lean in and ask questions: what's this room for, how old is the lock, who has keys? (that's enumeration). By the end you don't just know "there are three open doors" — you know "the side door is a 2009 lock model with a known flaw," which is a much more useful thing to know.

A port scan finds the open doors. Enumeration leans into each one and makes it talk.

**Where the analogy stops working.** Walking around a building is silent. Scanning a computer is not — every door you rattle shows up in the target's logs. A port scan is already an *active* action against a live system, loud enough to notice, which is why §5 is about noise.

## 1. Port scanning — finding the open doors
<!-- bite: 3969712d-920a-4a8b-98c3-44ba79eb74df -->

A **port** is a numbered doorway a service listens on: web servers usually on 80 and 443, SSH on 22, databases on their own numbers. A **port scan** asks each port "are you open?" and notes which answer. **Nmap** (network mapper) is the standard tool.

The single most useful scan adds **version detection** (`-sV`) — it doesn't just find open ports, it works out what software and version is behind each:

```bash
nmap -sV <target-ip>              # common ports, with service + version detection
nmap -p- <target-ip>              # all 65535 ports, not just the common ~1000
nmap -sC -sV <target-ip>          # version detection + nmap's default info-gathering scripts
```

- `-sV` is the workhorse: "what's running here?"
- `-p-` is thorough but slow: services hidden on odd ports (an admin panel on 8080, a database on 5432) only show up here.
- `-sC` runs safe default scripts that pull extra detail — banners, certificate names, supported options.

## Terms used in this lesson
<!-- bite: f26d01c1-e564-4c9c-adbd-11bf51eaa453 -->

1. **Port**: This is a numbered endpoint a network service listens on. Open means something is answering there.
2. **Port scan**: This is checking which of a host's ports are open, to see which services are exposed.
3. **Service / version detection**: This is working out not just that a port is open, but *what software and which version* is behind it (`nmap -sV`).
4. **Enumeration**: This is extracting detail from a discovered service — users, folders, shares, exact config — by talking to it directly.

## Terms used in this lesson: banners, web content and scanners
<!-- bite: 0c9511ca-6f93-4aef-8356-ed92ebc0bf2a -->

The last four terms are about what services give away, and what automated scanners get wrong.

5. **Banner**: This is the identifying text a service sends when you connect, often naming the software and version outright.
6. **Directory / content enumeration**: This is the web equivalent of a port scan: finding pages, folders and endpoints that aren't linked anywhere, by trying a wordlist of likely names.
7. **Vulnerability scan**: This is an automated check of discovered services against a database of known vulnerabilities (CVEs), producing a ranked list of likely weaknesses.
8. **False positive**: This is a scanner flagging something as vulnerable when it isn't really exploitable. Every automated finding needs manual confirming.

## 2. Why a version number is a finding
<!-- bite: b5847458-a742-4787-9b41-936710768e58 -->

Here's why `-sV` matters so much. Public vulnerability databases ([CVE](https://cve.org) records) are indexed *by software and version*. So the moment a scan tells you a port runs, say, `OpenSSH 7.2` or `Apache 2.4.49`, you can look up every publicly known weakness in that exact version — before touching it further. An **open port running an old, known-vulnerable version is itself the finding**: you've matched a door to a published flaw in its lock.

This is the direct handoff from scanning to [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|exploitation]]: the version-to-CVE match tells you *which* weakness to try first, instead of guessing. It's also why keeping software patched is such a big deal on the defence side — a version banner is a shopping list for attackers.

## 3. Enumeration — making each service talk
<!-- bite: ab89da95-ab20-4afb-a9d4-9aa7c228743f -->

A port scan says a door is open. Enumeration leans in and asks questions, which is more intrusive — you're actively conversing with the service, sometimes half-authenticating — and so needs firmer scope. What you enumerate depends on the service:

- **Users** — some services will confirm which usernames exist, handing you half of every login.
- **Shares** — networked file shares and their permissions (which folders are readable without a password?).
- **Web content** — hidden pages, folders, admin panels and API endpoints that nothing links to.
- **DNS** — subdomains, pulled harder than passive recon allowed.

For a web app, **content enumeration is the main event**, and it's the web's version of a port scan: instead of trying port numbers, you try a wordlist of likely paths (`/admin`, `/api`, `/backup`, `/.git`) and see which return something. That's worked example 2.

## 4. Vulnerability scanning — the automated pass
<!-- bite: 39b7a988-c6b2-45e4-94d6-0e68ec1c6dfc -->

A **vulnerability scanner** (Nessus, OpenVAS, and for web servers, Nikto) takes the services you found and checks each against a big database of known CVEs and misconfigurations, producing a ranked list. It's fast and thorough *for known issues*, and a sensible early pass. But it has two hard limits:

1. **False positives.** It flags things by signature, so it over-reports; every finding needs manual confirmation before it goes in a report.
2. **It only knows what's in its database.** It will never find a *logic* flaw — "the discount code can be applied twice," "you can read order #124 by asking for it" — because those aren't a signature in any database. Those are found by hand, which is why [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|exploitation]] is a human skill and not a button.

A clean vulnerability scan therefore does **not** mean a target is secure. It means no *known-signature* issue was found. The interesting bugs usually aren't signatures.

## 5. Noise — scanning is loud
<!-- bite: 60a18452-0a4d-4660-b3c7-9c8e0fb5f6c2 -->

Unlike passive recon, scanning is **active and noisy**. A full `-p-` scan rattling all 65535 ports, or a vulnerability scanner hammering a service, lights up the target's monitoring far more than recon ever did. Two consequences:

- **In a red-team engagement** that tests the defenders, your *stealth* can matter as much as your results — a slower, quieter scan (`nmap -T2`, fewer ports) may be required, and getting caught is itself a finding (for the blue team).
- **Against fragile systems**, aggressive scanning can cause real disruption. The classic example is old industrial control equipment that falls over when scanned. A scan is an action against a live system, not a passive read, so scan intensity is a **scoped decision** — your [[cybersecurity/02-ethical-hacking/01-rules-of-engagement-and-legal|RoE]] should say how hard you may scan.

On your own lab, scan as loud as you like — it's yours. But build the habit of treating scan intensity as a choice, because on a real target it is one.

## Worked example 1 — nmap a host
<!-- bite: 3c8042e6-5554-44a8-adfb-ecdfa68e3c76 -->

Run this against a host you own — your VPS (in scope per your `roe.txt`), or Metasploitable in the VM lab. (Juice Shop alone is thin here: it's one web port. A real host is the point.)

```bash
nmap -sV <your-vps-ip>
```

A host target produces something like this (abridged — the exact list depends on what you installed):

```text
PORT     STATE SERVICE  VERSION
22/tcp   open  ssh      OpenSSH 8.9p1 Ubuntu
80/tcp   open  http     nginx 1.18.0
443/tcp  open  ssl/http nginx 1.18.0
5432/tcp open  postgresql PostgreSQL 14.5
```

## Worked example 1: reading the nmap output
<!-- bite: c5be2ac5-1a41-474c-9e0d-2229eca3134e -->

Each line of that output is a door, and the versions are the clues.

**How you read this.** Four open doors. SSH (login service), a web server on 80/443, and — the interesting one — **PostgreSQL exposed on 5432**. A database reachable from the internet is almost always a misconfiguration worth a finding on its own, before you've tried a single password. Note the versions: each one is a lookup against the CVE database for known flaws. The scan just turned "a server exists" into a prioritised to-do list.

**Predict first:** before running `-p-`, guess which of your services sit on non-standard ports. Then run it and see what the common-ports scan missed.

## Worked example 2 — enumerate Juice Shop's hidden content
<!-- bite: fc5ed075-794e-4389-a4e2-52fa8ed4dd8d -->

Now the web kind, against Juice Shop on `localhost:3000`. Recon (lesson 03) found `/rest` and a hint toward `/ftp`; content enumeration finds the rest, by trying a wordlist of common paths. `ffuf` (or `gobuster`) is the standard tool:

```bash
ffuf -u http://localhost:3000/FUZZ -w /usr/share/wordlists/dirb/common.txt
```

`FUZZ` is where each word from the list is substituted. You're looking for paths that return `200` (exists) rather than `404`. On Juice Shop this surfaces things the UI never links to, for example:

```text
ftp                     [Status: 200]      # the directory robots.txt hinted at
/rest/products/search   [Status: 200]      # the search API (one query parameter)
ftp/legal.md            [Status: 200]      # files sitting in that open ftp folder
```

**What enumeration just handed you.** An open `/ftp` directory serving files, and the `search` API endpoint. Combine with recon's `/rest` and `/api` prefixes and you have the real attack surface — the API, not the pretty Angular front end. Every one of those endpoints is an input to test in [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|exploitation]]. Notice this is exactly worked example 1's logic — try many things, note what answers — applied to web paths instead of ports.

## Common pitfalls and traps
<!-- bite: aaeb16ac-9301-476d-910d-690a353d1841 -->

1. **Only scanning common ports.** The juiciest service (an admin panel on 8080, a database on 5432) often hides on an odd port that `-p-` would catch and a default scan won't.
2. **Trusting a vulnerability scanner's output as-is.** It over-reports. Confirm every finding by hand before it's a finding.
3. **Believing a clean scan means "secure."** Scanners only know signatures; logic bugs and access-control flaws are invisible to them.
4. **Forgetting scanning is loud.** On a real or fragile target, intensity is a scoped decision, not a default — a hard scan can disrupt, or get you caught when stealth was the test.
5. **Enumerating a web app from the browser only.** The UI hides most of the surface. The hidden endpoints that content enumeration finds are usually where the bugs are.

## Check your understanding
<!-- bite: c1c0feaa-073a-426c-b63f-ab55cb2524f2 -->

Try each one before you open the answer.

1. <!-- q: mcq id="11721a98" -->
   Your `nmap -sV` reports `3306/tcp open mysql MySQL 5.5.40`. Why is this line, on its own, already worth noting as a finding?

   - [ ] Because port 3306 should never be open on any machine.
   - [x] A database exposed to the network, plus a specific old version you can look up for known CVEs, is a prioritised weakness before you've even tried a password.
   - [ ] Because nmap only reports ports that are vulnerable.
   - [ ] Because MySQL is insecure by design.

   <details><summary>Answer</summary>

   Two things make it a finding: a database port reachable over the network is usually a misconfiguration (databases shouldn't be broadly exposed), and the exact version (`5.5.40`) can be matched against published CVEs to see known flaws. nmap reports open ports regardless of vulnerability; the *judgement* that this one matters is yours.

   </details>

2. <!-- q: gap id="fa75a5c1" answers="-sV" -->
   The nmap flag that identifies not just which ports are open but which software and version is running on each — turning an open port into a CVE lookup — is ___.

   <details><summary>Answer</summary>

   `-sV` (service/version detection). The version is what lets you match a service to its known published vulnerabilities, which is the bridge from scanning to exploitation.

   </details>

3. <!-- q: mcq id="8e8a2a25" -->
   A vulnerability scanner reports zero issues against a web app. The app also lets any logged-in user read other users' orders by changing the order number in the URL. Why did the scanner miss it?

   - [ ] The scanner wasn't run with admin privileges.
   - [ ] The bug isn't real if the scanner didn't find it.
   - [x] It's a logic / access-control flaw with no known signature, and scanners only match against a database of known issues.
   - [ ] Scanners only check network ports, never web apps.

   <details><summary>Answer</summary>

   Access-control and business-logic flaws aren't signatures in any database, so a signature-matching scanner is blind to them. This is exactly the gap manual testing exists to fill — a clean scan means "no known-signature issue," not "secure."

   </details>

4. <!-- q: mcq id="30e00e59" -->
   Content enumeration (e.g. `ffuf`) against a web app is best described as:

   - [ ] A way to crack the app's passwords.
   - [x] The web equivalent of a port scan — trying a wordlist of likely paths to find pages and endpoints nothing links to.
   - [ ] A passive recon technique that leaves no trace.
   - [ ] A vulnerability scanner that confirms exploitable bugs.

   <details><summary>Answer</summary>

   It's the web version of port scanning: instead of trying port numbers, you try many likely paths and note which exist. It's active (it hits the server, leaving traces), it doesn't crack passwords, and it finds surface — it doesn't confirm exploitability, which is the next stage.

   </details>

5. <!-- q: mcq id="54f8c75e" -->
   You're on a red-team engagement explicitly testing whether the client's security team notices an intrusion. How does that change how you scan?

   - [ ] You skip scanning entirely.
   - [ ] You scan as fast and aggressively as possible to finish quickly.
   - [x] You scan slowly and quietly, because getting detected is itself a (blue-team) finding and stealth is part of the test.
   - [ ] You only use passive recon and never touch the target.

   <details><summary>Answer</summary>

   In a red team, stealth matters as much as results — a loud scan that trips their monitoring is a finding *for the defenders*. You'd slow down (`nmap -T2`, fewer ports) to stay under the radar, because the goal is testing detection, not just enumerating the surface.

   </details>

6. <!-- q: open id="18d2a7d9" -->
   Explain, in terms of the engagement loop, why scanning sits *between* recon and exploitation — what does it take from recon, and what does it hand to exploitation?

   <details><summary>Answer</summary>

   Recon hands scanning a rough picture: which hosts and web apps exist, roughly what they are. Scanning turns that into an exact map — open ports, exact service versions, hidden endpoints — by actively probing. It then hands exploitation a prioritised, concrete target list: *this* version with *this* known CVE, *this* exposed database, *these* API endpoints to test. Without scanning you'd be exploiting blind (recon isn't specific enough); without recon you wouldn't know what to scan. Each stage's output is the next stage's input.

   </details>

## Practice — scan and enumerate your lab
<!-- bite: 6ab85024-2506-4ca3-8123-b624059ec941 -->

**Task.** Produce a target map of your own lab, in two halves.

1. **Host scan** (your VPS or Metasploitable, in scope): run `nmap -sV`, then `nmap -p-`. Record every open port, its service, and its version. Flag anything that looks like it shouldn't be exposed (a database, an admin service).
2. **Web enumeration** (Juice Shop): run `ffuf` with a common wordlist against `localhost:3000`. Record every path that returns `200` and isn't linked from the UI.

**Done when:** you have a one-page "attack surface" map: a list of host services (with versions) and a list of web endpoints, each annotated with why it's interesting. This is the input to lesson 07. Add the runs to `cybersecurity/LIVE-RUNS-TODO.md`.

**Stretch.** Pick one service version from your host scan and look it up on the CVE database. Does the version have any published vulnerabilities? Write down the CVE id — that's a scanning finding, before any exploitation.

## Before moving on
<!-- bite: aa1fd0f4-26d6-4ad8-831f-5965c90bb40b -->

You can now turn a rough recon picture into an exact map: open ports and their versions with `nmap -sV`, hidden web endpoints with content enumeration, and you know a version number is itself a CVE lookup. You can tell port scanning, enumeration and vulnerability scanning apart, and you treat scan intensity as a choice because scanning is loud.

**Recap for later lookup:** `nmap -sV` (versions → CVEs), `-p-` (all ports), `-sC` (default scripts). Web: `ffuf`/`gobuster` for hidden paths. Vulnerability scanners find known signatures only — logic bugs are manual. Scanning is active and noisy; intensity is scoped.

Next: [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|exploitation concepts]] — taking the target map and proving a weakness really works.

## Related
<!-- bite: aa1fd0f4-26d6-4ad8-831f-5965c90bb40c -->

- [[cybersecurity/02-ethical-hacking/03-reconnaissance|Reconnaissance]] — stage 2, the rough picture scanning sharpens.
- [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|Exploitation concepts]] — stage 4, what the target map feeds.
- [[cybersecurity/02-ethical-hacking/08-common-tools|Common tools]] — nmap, ffuf, Nikto and OpenVAS in the wider toolkit.

## About this lesson
<!-- bite: 1d571192-81d7-4a5e-a5d4-008f145b681b -->

**Level:** Intermediate. **Covers:** port scanning and version detection with nmap, why a version is a finding, service enumeration, web content enumeration with ffuf, vulnerability scanning and its limits, and scan noise as a scoped decision. **Where it sits:** lesson 6 of the [[cybersecurity/02-ethical-hacking/index|Ethical Hacking]] section — stage 3 of the engagement loop, between recon and exploitation. **Sources:** the original vault note, made concrete with real nmap output and ffuf enumeration against the VPS and Juice Shop targets. `[reference]` — not drawn from a personal paid engagement. Commands are tracked in `cybersecurity/LIVE-RUNS-TODO.md` for a verified run.
