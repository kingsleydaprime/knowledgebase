---
id: d19dd4bc-1fea-4a0b-989f-0afc3bfb618a
---

# Common Tools of the Trade

**This is the standard toolkit — what each tool is for, where it fits in the engagement loop, and a concrete example against your own lab.**

## Before you start
<!-- bite: d5766c0e-84bc-46fe-a0b0-0f5e73e06537 -->

You should have:

- Walked the loop conceptually → [[cybersecurity/02-ethical-hacking/02-penetration-testing-methodology|methodology]], and met scanning and exploitation (lessons 06–07).
- A target live: Juice Shop on `localhost:3000`.

After this lesson you will be able to:

1. Name the standard tool for each stage of the loop and say what task it automates.
2. Run the core web-testing workflow: intercept a request, edit it, resend it.
3. Explain why the concept matters more than the tool's exact flags.
4. Point to where to practise each tool legally beyond your own lab.

**Study route.** Kid version, the tools by stage (§1–6), then the worked example (Burp on Juice Shop), then the practice task.

## What the toolkit is

Every tool here just automates a task you already understand from the earlier lessons; knowing the landscape is what lets you follow a writeup, a report, or a conversation between practitioners.

## The kid version
<!-- bite: 93c75a73-5f2e-4b02-accd-839c5f9fa6a5 -->

A mechanic's toolbox has a tool per job: a wrench for bolts, a multimeter for electrics, a jack for lifting. You don't admire the tools — you reach for the one the job needs. A beginner mechanic who's memorised every tool's part number but doesn't know *which job needs which* can't fix a car. One who understands the jobs can pick up an unfamiliar tool and work out how to use it in minutes.

Security tools are the same. Each one does one job in the loop — map the network, intercept web traffic, crack a hash. Learn the *jobs* (you already did, in lessons 03–07) and the tools are just the wrenches you reach for.

**Where the analogy stops working.** A mechanic's tools rarely change. Security tools get replaced, renamed and updated constantly — the popular scanner this year isn't the one from five years ago. So memorising flags for today's favourite is a bad bet; understanding the job it does (which doesn't change) is what lasts. That's §6.

## 1. Recon tools
<!-- bite: 0ff03a4e-294f-4f36-a75e-3d552139e4c7 -->

These map to [[cybersecurity/02-ethical-hacking/03-reconnaissance|reconnaissance]] — gathering the picture before touching the target.

**theHarvester** — pulls emails, subdomains and hostnames for a domain from public sources (search engines, certificate logs) in one pass.

```text
theHarvester -d example.com -b all     # -d: domain   -b: sources ("all" = every supported source)
```

**Shodan** — a search engine that indexes internet-connected devices and exposed services. You query *its* index, so you learn what's publicly reachable **without sending a packet at the target yourself** — pure passive recon.

```text
shodan host 93.184.216.34              # everything Shodan already knows about an IP
```

## Terms used in this lesson
<!-- bite: cf3c4c51-ba0f-4206-9a31-695c1ab932d6 -->

1. **Intercepting proxy**: This is a tool that sits between your browser and the target, so every request and response can be viewed, paused and edited in flight. Burp and ZAP are the two.
2. **Repeater**: This is a Burp panel that resends one request over and over with your edits — the manual "change one thing and see what happens" tool.
3. **Intruder**: This is a Burp panel that automates sending many payloads at one spot in a request (e.g. a list of ids, or passwords).
4. **Wordlist**: This is a file of candidate values — paths, passwords — a tool tries one by one. `rockyou.txt` is the famous leaked-password list.
## Terms used in this lesson: cracking, exploits and traffic

The last four terms come from the cracking, exploit and traffic tools, plus the two best-known certifications.

5. **Hash**: This is the scrambled, one-way form a password is stored as. Cracking means finding an input that produces a captured hash.
6. **Exploit module**: This is a packaged, ready-to-run exploit for a known vulnerability, as in Metasploit.
7. **Capture vs display filter**: In traffic tools, one chooses *what to record*, the other *what to show* from a recording — different syntaxes.
8. **OSCP / CEH**: These are the two best-known pentest certifications — OSCP hands-on and exam-based, CEH broader and more conceptual.

## 2. Scanning and enumeration tools
<!-- bite: 96bd7c19-ea74-44c5-a99d-248a22fe6dbb -->

These map to [[cybersecurity/02-ethical-hacking/06-scanning-and-enumeration|scanning and enumeration]].

**Nmap** — the default first tool for mapping what's reachable and what's running.

```bash
nmap -sV -sC <target-ip>               # version detection + default scripts
nmap -p- -T4 <target-ip>               # every port, faster timing
```

**ffuf / gobuster** — content enumeration: find hidden web paths by trying a wordlist (this is how you found Juice Shop's `/ftp`).

```bash
ffuf -u http://localhost:3000/FUZZ -w /usr/share/wordlists/dirb/common.txt
```

**Nikto** — a quick web-server scanner for common misconfigurations and outdated software. **OpenVAS / Nessus** — full automated vulnerability scanners that rank discovered services against known CVEs; driven through a web UI, producing a ranked report (confirm every finding by hand).

## 3. Web application testing tools
<!-- bite: d4ad7468-645a-42bd-b97d-a9127440de26 -->

The heart of web pentesting, mapping to [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|exploitation]].

**Burp Suite** — the intercepting proxy. Point your browser at Burp's local proxy (`127.0.0.1:8080`) and every request passes through it to view, pause and edit before it reaches the server. The core workflow: browse normally with intercept on, send an interesting request to **Repeater** to tweak a parameter by hand (test injection or access control), or to **Intruder** to automate many payloads against one spot. This is worked example material — § worked example.

**OWASP ZAP** — a free, open-source alternative with an automated-scan mode plus the same manual intercept/repeat workflow.

**sqlmap** — once you've found a likely SQL-injection point by hand, sqlmap automates confirming and exploiting it.

```text
sqlmap -u "http://localhost:3000/rest/products/search?q=1" --dbs   # test the q parameter, list databases if injectable
```

## 4. Exploitation and network tools
<!-- bite: a7284695-4e09-496a-a6e5-33eb7bdb968b -->

**Metasploit** — a framework of maintained **exploit modules** plus payload generation, so a known vulnerability's real impact can be demonstrated without writing an exploit from scratch. The workflow is always the same shape: pick a module, set the target (`RHOSTS`), set a payload, run.

```text
msfconsole
use exploit/.../<module_for_a_known_CVE>
set RHOSTS <target-ip>
set PAYLOAD <payload>
run
```

**Wireshark** — captures and inspects raw traffic in detail. Offensive (what does a target's traffic reveal?) and defensive (a core blue-team investigation tool). Its companion `tcpdump` captures from the command line:

```text
tcpdump -i eth0 port 443 -w capture.pcap      # capture HTTPS traffic to a file
```

Inside Wireshark, *display filters* pick what to show from a capture: `http.request`, `ip.addr == <host>`, `tcp.flags.syn == 1 && tcp.flags.ack == 0` (new connections only).

## 5. Password and credential tools
<!-- bite: a6bc5c05-78c5-49ac-8d44-03c43cb2ab3c -->

These crack captured hashes offline — the technique behind [[cybersecurity/02-ethical-hacking/10-pdf-and-document-security|PDF cracking]] and [[cybersecurity/02-ethical-hacking/11-wifi-security-testing|Wi-Fi cracking]], both of which you'll do on things you own.

**Hashcat** — GPU-accelerated cracking against a captured hash.

```text
hashcat -m 0 -a 0 hashes.txt rockyou.txt       # -m 0: MD5, -a 0: straight dictionary attack
hashcat -m 1000 -a 3 hashes.txt ?u?l?l?l?l?d?d  # NTLM, mask: Upper + 4 lower + 2 digits
```

**John the Ripper** — a long-standing alternative, loved for its format-specific extractor scripts that turn a file into a crackable hash:

```text
pdf2john locked.pdf > hash.txt                 # extract the hash from a PDF you locked
john --wordlist=rockyou.txt hash.txt
john --show hash.txt                           # show what's been cracked
```

**Wordlists matter as much as the tool.** `rockyou.txt` (bundled with Kali) is the common default, but a mask attack or a target-specific list often beats a generic one → [[cybersecurity/02-ethical-hacking/10-pdf-and-document-security|PDF and document security]].

## 6. Why the concept beats the tool
<!-- bite: 71450d8b-d6f8-476c-84c1-199e60c29f9e -->

Every tool here automates a task that maps straight onto a loop stage you already understand: a scanner is [[cybersecurity/02-ethical-hacking/06-scanning-and-enumeration|scanning]], a proxy is [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|exploitation]], a cracker is offline password work. Tools get replaced, renamed and updated; the *task* doesn't. So the thing to internalise is "what job does this category of tool do, and why" — that transfers to whatever tool is popular in five years. And a tool without the [[cybersecurity/02-ethical-hacking/02-penetration-testing-methodology|methodology]] produces scattered, incomplete testing: the tools support the loop, they don't replace it.

## Worked example — Burp's intercept → Repeater, on Juice Shop
<!-- bite: b5044ef3-3b5a-41a7-9347-1bf76ba1b8a8 -->

The single most important web workflow, against your own Juice Shop. This is how you turn "I think this is broken access control" into proof.

1. **Set the proxy.** Point your browser at Burp (`127.0.0.1:8080`), and trust Burp's CA cert so HTTPS works.
2. **Browse normally.** Log in as a normal user and open your basket. In Burp's HTTP history you see the request go by: `GET /rest/basket/1`.
3. **Send to Repeater.** Right-click that request → *Send to Repeater*. Repeater holds one request you can edit and resend by hand.
4. **Change one thing.** In Repeater, change `/rest/basket/1` to `/rest/basket/2` and hit *Send*.
5. **Read the response.** If you get back someone else's basket contents, you've just proved an **IDOR** (broken access control) — the app checked you were logged in but not that basket 2 was yours.

## Worked example — why intercept → Repeater matters

This one workflow is behind almost every web finding.

**Why this is the workflow that matters.** Almost every web finding is "change something the app trusted and watch what happens," and Repeater is the tool for exactly that one-change-at-a-time probing. Intruder is the same idea automated — feed it `1,2,3,...` as basket ids and it pulls every basket in one run. Notice the tool added nothing conceptual: you already understood IDOR from lesson 07; Burp just let you *do* it cleanly and capture the proof a report needs.

## Where to practise legally
<!-- bite: a2d9c6e2-6e7c-4d4a-b970-27335113f385 -->

Beyond your own lab, these give legally-sanctioned targets to run the tools against end to end:

- **PortSwigger Web Security Academy** — free, made by Burp's authors, the best web-security practice there is.
- **HackTheBox / TryHackMe** — hosted, intentionally-vulnerable machines; TryHackMe guided, HackTheBox less so.
- **picoCTF / live CTFs** — where it stops being exercises and nobody hands you the answer.

And two certifications structure the path: **OSCP** (heavily hands-on, a 24-hour practical exam) and **CEH** (broader, more conceptual) → [[cybersecurity/02-ethical-hacking/14-career-path-and-best-practices|career path]]. Before any of those, your own lab ([[cybersecurity/02-ethical-hacking/05-home-lab-setup|lesson 05]]) and the [[cybersecurity/02-ethical-hacking/12-practice-exercises|practice exercises]] are the "use these for real" step.

## Common pitfalls and traps
<!-- bite: d26d76c6-d294-4f3d-a708-453de4d90396 -->

1. **Memorising flags instead of jobs.** The tool changes; the task it does doesn't. Learn the job.
2. **Tools without methodology.** A pile of scanner output isn't a test. The loop is what makes testing thorough.
3. **Trusting automated output.** Vulnerability scanners and sqlmap over-report; confirm by hand before it's a finding.
4. **Running anything against a target you don't own.** Every example here assumes your own lab or a sanctioned platform. The same command elsewhere is the same crime as any unauthorized access.
5. **Ignoring wordlist choice.** A generic `rockyou.txt` run can miss what a targeted or mask-based list catches.

## Check your understanding
<!-- bite: c93374bd-b665-4849-b057-7694369b9197 -->

Try each one before you open the answer.

1. <!-- q: mcq id="0b505d6b" -->
   In Burp Suite, you've captured `GET /rest/basket/1` and want to test whether you can read other users' baskets by hand, one id at a time. Which tool do you use?

   - [ ] Intruder, to automate thousands of payloads.
   - [x] Repeater, to resend the request with the id changed and read each response.
   - [ ] The proxy's intercept, to block the request.
   - [ ] sqlmap, to dump the database.

   <details><summary>Answer</summary>

   Repeater holds one request you edit and resend by hand — ideal for changing `1` to `2` and reading the response. Intruder is the *automated* version (feed it a list of ids), useful once you've confirmed the bug in Repeater. Intercept pauses traffic; sqlmap is for SQL injection, not access control.

   </details>

2. <!-- q: gap id="266e0a65" answers="Shodan" -->
   The search engine that indexes internet-connected devices and exposed services, letting you learn what's publicly reachable about a target without sending it a single packet yourself, is ___.

   <details><summary>Answer</summary>

   Shodan. Because you query Shodan's own index rather than the target, it's pure passive reconnaissance — no traffic reaches the target.

   </details>

3. <!-- q: mcq id="571e08f1" -->
   Why is "understand the job the tool does" better advice than "memorise the tool's flags"?

   - [ ] Flags are secret and jobs are public.
   - [x] Tools get replaced, renamed and updated constantly, but the underlying task (scan, intercept, crack) doesn't change — so job-knowledge transfers to new tools.
   - [ ] Jobs are easier to remember than flags.
   - [ ] Flags only work with authorization.

   <details><summary>Answer</summary>

   The popular scanner or proxy changes over the years, and flags change with it; but "map the network," "intercept and edit web traffic," "crack a hash" are stable tasks. Understanding the task lets you pick up whatever tool is current and work out its flags quickly.

   </details>

4. <!-- q: mcq id="b9e27cc0" -->
   You run OpenVAS and it produces a list of 40 "vulnerabilities." What must you do before any of them goes into a report?

   - [ ] Nothing — an automated scanner's output is authoritative.
   - [ ] Email all 40 to the client immediately.
   - [x] Manually confirm each one is really exploitable, because scanners over-report (false positives).
   - [ ] Re-run the scan with more threads.

   <details><summary>Answer</summary>

   Automated scanners match signatures and over-report, so every flagged item needs manual verification of actual exploitability before it's a finding. Shipping raw scanner output as a report is a classic junior mistake — it's full of false positives and misses the logic bugs scanners can't see.

   </details>

5. <!-- q: mcq id="2f9b7eee" -->
   `hashcat -m 0 -a 0 hashes.txt rockyou.txt` — what is this doing?

   - [x] A straight dictionary attack: trying every password in rockyou.txt against MD5 hashes.
   - [ ] A brute-force attack trying every possible character combination.
   - [ ] Encrypting the file hashes.txt.
   - [ ] Scanning a network for open ports.

   <details><summary>Answer</summary>

   `-m 0` sets the hash type to MD5, `-a 0` is a straight dictionary (wordlist) attack, and `rockyou.txt` is the wordlist — so it hashes each candidate password and checks it against the captured hashes. A mask/brute-force attack would be `-a 3` with a character pattern.

   </details>

6. <!-- q: open id="b22d375e" -->
   A friend says "I learned Metasploit, so now I can pentest." Using the idea that tools support the methodology, explain what's missing.

   <details><summary>Answer</summary>

   Metasploit automates one stage — running known exploits — but a pentest is the whole loop: scope, recon, scan, exploit, chain, report, fix/detect. Without the methodology, tool skill produces scattered, incomplete testing: firing exploits with no recon or scanning behind them, no chaining of findings, and — crucially — no report, fix or detection, which is the actual deliverable. The tools support the process; they don't replace knowing which stage you're in and why. Knowing one tool is a wrench, not a trade.

   </details>

## Practice — run the web workflow end to end
<!-- bite: 51417676-0020-4382-b410-95896b0264a9 -->

**Task.** Use Burp (or ZAP) against your own Juice Shop to prove one access-control bug, capturing the evidence a report would need.

1. Proxy your browser through Burp and trust its certificate.
2. Log in as a normal user, do something that loads your own data (your basket).
3. Send that request to Repeater, change the object id, and resend.
4. Capture the request and response showing you reached data that isn't yours.

**Done when:** you have a saved request/response pair proving an IDOR, the exact thing lesson 09 turns into a finding. Add the run to `cybersecurity/LIVE-RUNS-TODO.md`.

**Stretch.** Send the same request to **Intruder**, feed it a range of ids (1–20), and note how it automates what you did by hand — then say why you'd still confirm one by hand first.

## Before moving on
<!-- bite: c93374bd-b665-4849-b057-7694369b9198 -->

You now know the standard tool for each stage of the loop, you've run the core web workflow (intercept → Repeater → resend), and you understand why the job matters more than the flags. You know where to practise each tool legally.

**Recap for later lookup:** recon = theHarvester, Shodan. Scan = nmap, ffuf, Nikto, OpenVAS. Web = Burp/ZAP (intercept→Repeater→Intruder), sqlmap. Exploit = Metasploit. Traffic = Wireshark/tcpdump. Cracking = hashcat, John. The tool automates a task you already understand; methodology is what ties them together.

Next: [[cybersecurity/02-ethical-hacking/09-post-exploitation-and-reporting|post-exploitation and reporting]] — turning a proven bug into the finding and the report that's the actual deliverable.

## Related
<!-- bite: c93374bd-b665-4849-b057-7694369b9199 -->

- [[cybersecurity/02-ethical-hacking/06-scanning-and-enumeration|Scanning and enumeration]] and [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|exploitation concepts]] — the stages these tools serve.
- [[cybersecurity/02-ethical-hacking/05-home-lab-setup|Home lab setup]] — where to run them safely.
- [[cybersecurity/02-ethical-hacking/14-career-path-and-best-practices|Career path]] — OSCP, CEH and the climb to senior.

## About this lesson
<!-- bite: 06723193-16ea-4089-b750-a2cdbd9f18c7 -->

**Level:** Intermediate. **Covers:** the standard toolkit by engagement-loop stage (theHarvester, Shodan, nmap, ffuf, Nikto, OpenVAS, Burp/ZAP, sqlmap, Metasploit, Wireshark, hashcat, John), the core intercept→Repeater web workflow, why the concept outlasts the tool, and where to practise legally. **Where it sits:** lesson 8 of the [[cybersecurity/02-ethical-hacking/index|Ethical Hacking]] section — the tools that automate the loop. **Sources:** the original vault note, reorganised by loop stage with a concrete Burp workflow against Juice Shop. `[reference]` — not drawn from a personal paid engagement. Commands are tracked in `cybersecurity/LIVE-RUNS-TODO.md` for a verified run.
