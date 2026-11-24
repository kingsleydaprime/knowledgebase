---
id: cab3ad6b-93f9-42a3-82d4-d8575b28a6d2
---

# Career Path and Best Practices — Getting to Senior

**"Senior" in this field isn't a longer list of tools — it's understanding *why* a finding matters, chaining small issues into a real attack path, and writing a report that gets a fix funded.**

## Before you start
<!-- bite: ac3d1c87-b6a2-44a3-a0f4-70926373bc80 -->

You should have:

- Worked through the engagement loop (lessons 01–09) at least once against your own lab.

After this lesson you will be able to:

1. Name the skills to build toward senior, roughly in order, and why each one underpins the next.
2. Place the main certifications (Security+, CEH, OSCP) and say what each is and isn't good for.
3. List the habits that actually mark a senior, beyond tool use.
4. Build a visible portfolio when most real work is under NDA.

**Study route.** Kid version and §1–5, then the practice task: write your own path from where you are now.

## What senior means here
<!-- bite: ed8cab89-c0bc-432a-8e7e-00b9e7830c15 -->

This lesson maps the skills to build, in order, and the habits that actually separate junior from senior, on top of everything else in this section.

## The kid version
<!-- bite: ca81602f-b197-4839-914c-44e9c1be2e27 -->

Think about the difference between someone who can drive and a rally driver. Both turn the same wheel and press the same pedals. What makes the rally driver isn't extra buttons — it's that they understand *why* the car behaves as it does, so they can handle a corner they've never seen, on a road nobody mapped for them. The learner driver can only do roads they've practised.

Junior and senior in security is the same gap. A junior runs tools and recognises bugs they've seen before. A senior understands the mechanisms well enough to find a bug nobody has catalogued, chain small things into a big one, and explain it so it gets fixed. This lesson is how you cross from the first to the second.

**Where the analogy stops working.** A rally driver's skills are fairly fixed once learned. Security never stands still — new vulnerability classes, new tools, new defences arrive constantly. So the real senior skill isn't a destination you arrive at; it's the *habit* of continuous learning. That's §5.

## 1. The skill progression, roughly in order
<!-- bite: 6e198e47-0c8c-4129-97f1-668215ada218 -->

Each of these underpins the next — skipping one leaves the later ones as memorised patterns instead of real understanding:

1. **Networking fundamentals** — TCP/IP, DNS, HTTP, routing. Every tool in [[cybersecurity/02-ethical-hacking/08-common-tools|common tools]] automates an interaction with these; you can't reason about *why* a scan or exploit works without them. → [[networking/index|networking]].
2. **Linux proficiency** — filesystem, permissions, processes, shell. Nearly all serious tooling runs on Linux, and comfort with it frees you to focus on the security concept, not the environment.
3. **Scripting (Python and/or Bash)** — the point where you stop being limited to what existing tools do and can write a quick script to test an idea, parse output, or automate a repetitive step.
4. **How the web really works** — requests, cookies, sessions, the browser–server conversation. Required before [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|exploitation]]'s web classes (injection, XSS, access control) make deep sense rather than being memorised.

## 1. The skill progression: from code to specialism
<!-- bite: 01feba54-39c4-4c5e-a619-851d4d34aca7 -->

The second half of the path moves from understanding systems to going deep in one area.

5. **Reading code** — not writing production software, but reading source and spotting where user input reaches a dangerous sink. This is the skill behind finding *novel* bugs, not just recognising known ones.
6. **Structured practice** — CTFs, HackTheBox, TryHackMe: running the full [[cybersecurity/02-ethical-hacking/02-penetration-testing-methodology|methodology]] against realistic legal targets, repeatedly, until it's second nature.
7. **Formal validation (optional)** — certifications, below, to structure learning and signal competence — not a substitute for step 6.
8. **Specialisation** — most seniors go deep in one or two areas (web, infrastructure, mobile, cloud, red teaming, reverse engineering) rather than staying a generalist. Depth is usually what "senior" actually signals.

## Terms used in this lesson
<!-- bite: 5c792ca2-7d7a-4a80-9c31-a96802375d10 -->

1. **Security+**: This is CompTIA's broad, entry-level, mostly-theoretical certification — a reasonable first credential.
2. **CEH (Certified Ethical Hacker)**: This is a broad, conceptual certification covering tools and methodology; more knowledge-recall than hands-on.
3. **OSCP (Offensive Security Certified Professional)**: This is a heavily hands-on certification with a 24-hour practical exam where you actually compromise machines — a strong, credible signal of real skill.

## Terms used in this lesson: the work and the people
<!-- bite: 26ff54b7-53a8-4f17-971c-531baa5b5232 -->

The rest of the terms are about how the work is done, who you work against, and where bugs hide.

4. **NDA (non-disclosure agreement)**: This is the contract that stops you publishing real client work, which is why a portfolio takes effort to build.
5. **Bug bounty**: This is a sanctioned program (HackerOne, Bugcrowd) that authorises you to test a company's systems and pay out for valid findings — authorized by the program's own terms.
6. **Blue team**: This is the defensive side — the people who detect and respond to attacks. Understanding them makes your offence sharper.
7. **Attack path**: This is a chain of individually-small weaknesses that combine into serious impact — spotting these is a senior skill.
8. **Sink**: This is a dangerous destination for user input in code (a SQL query, a shell call, an HTML page); finding input-to-sink paths is how novel bugs are found.

## 2. Certifications worth knowing
<!-- bite: 4c7bf7ed-b321-47e8-9e35-7ff58841ad94 -->

1. **CompTIA Security+** — broad, entry-level, theoretical. A reasonable start if you're new to IT/security generally.
2. **CEH** — broad conceptual coverage of tools and methodology; a structured overview, criticised by many practitioners for being more recall than hands-on skill.
3. **OSCP** — heavily hands-on: you compromise machines in a timed practical exam, not multiple choice. Widely regarded as a strong signal of real practical skill, and a common target once the fundamentals above are solid.
4. **Beyond OSCP** — more specialised offensive certs exist per specialisation (web, mobile, exploit development). Worth researching once you know your specialisation, not before.

Certifications matter most for getting past HR filters and structuring knowledge. They **don't** replace the hands-on repetition of step 6, and plenty of strong practitioners are certification-light but portfolio-heavy (§4).

## 3. What actually separates senior from junior
<!-- bite: 182b57eb-fa2c-4188-b2d6-0e8d4e660032 -->

Everything in this section has been building these habits. They're what "senior" really means:

1. **Root-cause understanding over tool output.** A junior reports "the scanner flagged this"; a senior explains *why* it's exploitable, under what conditions, and exactly what fixes it — the [[cybersecurity/02-ethical-hacking/09-post-exploitation-and-reporting|shallow-vs-investigated]] distinction.
2. **Chaining low findings into real impact.** Three "low" issues (a verbose error, a predictable id scheme, a missing rate limit) can combine into account takeover. Pure tool output never hands you the chain — this is exactly the escalation from lesson 07.
3. **Communication and reporting.** A report an executive will act on is as much a senior skill as the finding. A brilliant finding, badly written, gets deprioritised and never fixed.

## 3. What separates senior from junior: staying sharp
<!-- bite: c0a2b9e0-c7d8-479d-958d-985600cb3102 -->

The last three habits keep you sharp once the basics are solid.

4. **Staying current.** Following CVE disclosures, research blogs and conference talks (Black Hat and similar). The field moves fast enough that stale knowledge misses whole modern classes.
5. **Writing your own tools when existing ones fall short.** The scripting skill applied — not being limited to what Burp or Metasploit ship with.
6. **Understanding the defensive side.** Knowing how a blue team detects and responds (logging, SIEM, EDR) makes your testing sharper — you can reason about what would and wouldn't be noticed, instead of running the loudest tool. This is the fix-and-detect half of every exploitation lesson, made into a career habit.

## 4. Building a visible portfolio
<!-- bite: eeb261b7-9ce1-420d-88a7-33c8cb130c12 -->

Most real work happens under NDA — client engagements aren't publishable — so you prove skill through things you *can* show:

- **CTF results and public writeups** — competition ranks, and breakdowns of how you solved challenges.
- **A HackTheBox / TryHackMe public rank.**
- **Bug-bounty reports** through sanctioned platforms (HackerOne, Bugcrowd) — authorised by the program's own terms, so inherently legal.
- **Open-source security-tool contributions.**
- **Technical blog posts** breaking down a vulnerability class or a CTF challenge in depth.

This is often what gets a junior noticed for a first role, more than certifications alone. A writeup of the engagement you ran against your own Juice Shop + VPS, with the full loop and a real report, is a portfolio piece you can build *today*.

## 5. Best practices, as a mindset
<!-- bite: 15bee2b2-4e79-4849-90a5-0516d16a7cf1 -->

Not a rule list to pass, a way of working:

1. **Authorization always comes first** — not a legal formality but the ethical core of the discipline ([[cybersecurity/02-ethical-hacking/01-rules-of-engagement-and-legal|lesson 01]]). It's the difference between this whole skill set being a career or a crime.
2. **Document as you go**, not just at report time — screenshots, commands, timestamps — for the report and so you can reconstruct exactly what you did if asked.
3. **Minimise impact** — prove a finding the least disruptive way (show that injection is *possible*, don't delete data to prove it). A professional norm, not just a scope rule.
4. **Treat "senior" as a direction, not a destination** — the tools and the vulnerability landscape keep shifting, so the habit of continuous learning *is* the senior skill, more than any technique mastered today.

## Check your understanding
<!-- bite: 169ca342-39ea-4b72-8512-79cbed1e6e7f -->

Try each one before you open the answer.

1. <!-- q: mcq id="ab3f832d" -->
   Which best captures what separates a senior pentester from a junior?

   - [ ] Knowing more tools and their command flags.
   - [x] Understanding *why* findings matter, chaining small issues into real impact, and writing reports that get fixes funded.
   - [ ] Holding more certifications.
   - [ ] Running scans faster.

   <details><summary>Answer</summary>

   Seniority is root-cause understanding, chaining, and communication — not a longer tool list, more certs, or raw speed. A senior can handle an unseen target and make the business act on a finding; tool-count and certs don't confer that.

   </details>

2. <!-- q: mcq id="8def8132" -->
   What is the OSCP, specifically, and what is it good for?

   - [ ] A multiple-choice exam testing security theory; good for proving broad knowledge.
   - [x] A hands-on exam where you compromise machines in a timed practical; a credible signal of real practical skill.
   - [ ] A networking certification unrelated to pentesting.
   - [ ] A bug-bounty platform.

   <details><summary>Answer</summary>

   OSCP is heavily practical — you actually compromise machines in a timed exam, not answer multiple choice — which is why it's regarded as a strong signal of real skill. CEH and Security+ are the broader, more theoretical credentials; the OSCP is the common target once fundamentals are solid.

   </details>

3. <!-- q: gap id="ca298671" answers="chaining|chain" -->
   Three individually low-severity findings — a verbose error message, a predictable ID scheme, and a missing rate limit — combine into an account-takeover path. Turning small issues into serious impact this way is called ___, and it's a senior skill tool output won't hand you.

   <details><summary>Answer</summary>

   Chaining. Recognising how low findings combine into a real attack path is a hallmark of senior work and exactly the escalation the exploitation lesson showed (one bug → admin → everything). A scanner reports each issue in isolation; the chain is human insight.

   </details>

4. <!-- q: mcq id="561b1029" -->
   Why does building a portfolio take deliberate effort in this field?

   - [ ] There's nothing worth showing until you're senior.
   - [x] Most real client work is under NDA and can't be published, so you prove skill through CTFs, writeups, bug-bounty reports and open-source work instead.
   - [ ] Employers only look at certifications.
   - [ ] Portfolios aren't actually useful for getting hired.

   <details><summary>Answer</summary>

   Client engagements are confidential (NDA), so the skill they build isn't publicly visible. You demonstrate ability through things you *can* share — CTF writeups, HTB/THM ranks, sanctioned bug-bounty reports, open-source contributions, blog posts — which often get a junior noticed more than certs alone.

   </details>

5. <!-- q: open id="7c41898c" -->
   Why does understanding the *defensive* side (how a blue team detects attacks) make someone a better *offensive* tester? Connect it to the fix-and-detect habit from the exploitation lessons.

   <details><summary>Answer</summary>

   Knowing how defenders detect and respond (logging, SIEM alerts, EDR) lets an offensive tester reason about what would and wouldn't be noticed, rather than just running the loudest tool — useful for realistic, especially red-team, work. It also directly produces better findings: every exploitation lesson paired an attack with its detection, so a tester who understands detection can report not just "here's the bug and fix" but "here's the log pattern that should have alerted, and it didn't" — turning one finding into two and making the client genuinely safer. Offence and defence sharpen each other.

   </details>

## Practice — write your own path
<!-- bite: 69000d8b-5575-45d4-acc3-7218abaa1d5b -->

**Task.** Write a short, honest plan from where you are now toward senior.

**Your plan should state:**
1. **Where you are** on the §1 progression (be honest about the first gap — networking? scripting? reading code?).
2. **The next concrete step** — the specific skill or practice to build next, and how (a course, a platform, a CTF track).
3. **One portfolio piece you can build in the next month** — e.g. a writeup of your Juice Shop + VPS engagement, with the full loop and report.
4. **A certification target** (if any) and when it makes sense relative to your fundamentals.

**Done when:** you have a one-page plan naming your current gap, your next step, a concrete portfolio piece, and whether/when a cert fits — specific enough to act on this week.

**Stretch.** Turn the engagement you ran through lessons 05–09 into an actual public writeup (sanitised, your own lab) — your first portfolio piece.

## Before moving on
<!-- bite: 7c2200be-bd52-4d2b-9243-16a3203a675d -->

You now have the map from here to senior: the skill progression (networking → Linux → scripting → web → reading code → structured practice → specialisation), where the certifications fit, the habits that actually mark a senior (root cause, chaining, communication, currency, own tools, knowing the blue team), and how to build a visible portfolio under NDA.

**Recap for later lookup:** senior = why-it-matters + chaining + reporting, not tool count. Progression is fundamentals-first. OSCP is the hands-on signal; Security+/CEH are broader. Portfolio from CTFs, writeups, bug bounties, open source. Mindset: authorization first, document as you go, minimise impact, keep learning.

This closes the Ethical Hacking section. Next, apply it: the [[cybersecurity/02-ethical-hacking/projects|projects]] and the deeper sections — [[cybersecurity/04-web-security/index|web security]], [[cybersecurity/14-api-security/index|API security]], [[cybersecurity/12-active-directory/index|Active Directory]] and [[cybersecurity/11-binary-exploitation/index|binary exploitation]] — each go deeper on one area to specialise in.

## Related
<!-- bite: 721097e2-2f3c-4142-9f7b-7ad45e1dc603 -->

- [[cybersecurity/02-ethical-hacking/02-penetration-testing-methodology|Methodology]] — the loop these habits run.
- [[cybersecurity/02-ethical-hacking/09-post-exploitation-and-reporting|Post-exploitation and reporting]] — the communication skill that marks a senior.
- [[cybersecurity/02-ethical-hacking/12-practice-exercises|Practice exercises]] — the structured reps that build the skill.
- [[cybersecurity/projects|Cybersecurity projects]] — portfolio-grade tasks.

## About this lesson
<!-- bite: d1f79c42-51af-4aba-aae9-691cd5e48d44 -->

**Level:** Intermediate. **Covers:** the skill progression to senior, the main certifications (Security+, CEH, OSCP) and what each is for, the habits that separate senior from junior (root-cause understanding, chaining, communication, staying current, writing tools, knowing the blue team), building a portfolio under NDA, and best practices as a mindset. **Where it sits:** lesson 14 — the closing lesson of the [[cybersecurity/02-ethical-hacking/index|Ethical Hacking]] section. **Sources:** the original vault note, brought to the course standard and tied to the engagement you ran in lessons 05–09. `[reference]` — not drawn from a personal paid engagement.
