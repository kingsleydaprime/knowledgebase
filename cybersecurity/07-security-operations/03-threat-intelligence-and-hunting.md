---
id: 220a0707-fac4-42dc-b90a-b0d1b79c0dae
---

# Threat Intelligence and Hunting

**Threat intelligence is knowledge about how attackers work, and threat hunting is using it to go looking for an attacker who may already be inside.**

## Before you start
<!-- bite: a9ccf8eb-fe21-4be1-8d2d-e9047c079c87 -->

You should have:

- Written detection rules and understood what a SIEM holds → [[cybersecurity/07-security-operations/02-logging-siem-and-detection|logging, SIEM and detection]].
- Performed several attacks yourself — recon, SQLi, ARP spoofing, spraying → [[cybersecurity/06-attacks-and-threats/index|attacks and threats]] and [[cybersecurity/02-ethical-hacking/03-reconnaissance|reconnaissance]].
- Access to a log source you can query (your lab's `auth.log` is enough).

After this lesson you will be able to:

1. Tell strategic, operational and tactical intelligence apart, and place IOCs vs TTPs.
2. Describe the cyber kill chain, MITRE ATT&CK and the diamond model, and what each is for.
3. Map an attack you performed to ATT&CK tactics and technique IDs.
4. Run a hypothesis-driven hunt and turn a finding into a new detection.

**Study route.** Kid version and §1–3, then the worked example: mapping your own labs to ATT&CK and running one hunt.

## What threat intelligence and hunting are
<!-- bite: 254cd596-0748-4811-a6c0-176a811970bd -->

Detection (lesson 2) catches what you already wrote a rule for. But the best attackers ([[cybersecurity/01-fundamentals/03-attacker-and-hacker-types|APTs]]) move "low and slow" and never trip a signature. Two things close that gap.

**Threat intelligence** is organised knowledge about adversaries — who targets your industry, what infrastructure they use, what indicators to watch for — so you defend against *known* behaviour proactively instead of reacting blindly. **Threat hunting** is the active side: assuming a breach has already happened and going to look for it, guided by that intelligence. Tying them together is a set of **frameworks** that give the whole field a shared language for attacker behaviour — and by the end you'll have spoken that language about your own earlier labs.

## The kid version
<!-- bite: 5656e1c1-af03-4d5f-84c1-6bb3afb447d8 -->

Two ways to keep a house safe. The first: learn how burglars in your area actually work — which window they favour, what time they come, what they look for. That's intelligence. The second: instead of waiting for the alarm, you walk the house at night checking: is that window unlatched, are there muddy prints by the back door, is anything moved? That's hunting — you assume someone *might* already be in and go look, using what you learned about how they operate.

**Where the analogy stops working.** A burglar leaves muddy prints; a skilled intruder in a network tries hard to leave none, and "walking the house" means querying millions of log lines, not glancing around. So a hunt isn't a vague look — it's a *specific* question ("if they moved sideways using stolen password hashes, I'd see exactly *this* pattern") that you can answer with data, and when you find it you write a rule so you never have to hunt for *that* again.

## 1. Threat intelligence
<!-- bite: 37954603-7c4e-49a2-9b10-8ae6c4f50b23 -->

**Threat intelligence** is knowledge about adversaries used to defend proactively. It comes at three levels:

1. **Strategic** — high-level trends for leadership: which threat actors target our industry, and why.
2. **Operational** — specific campaigns, tactics and infrastructure an adversary is using now.
3. **Tactical** — concrete **IOCs** (Indicators of Compromise): malicious IPs, domains, file hashes and URLs you can feed straight into [[cybersecurity/07-security-operations/02-logging-siem-and-detection|detection]].

**OSINT** (Open-Source Intelligence) is gathering intel from public sources — WHOIS, DNS, certificate transparency (you used `crt.sh` in [[cybersecurity/04-web-security/03-https-and-tls|HTTPS and TLS]]), breach dumps, Shodan. It's how attackers do [[cybersecurity/02-ethical-hacking/03-reconnaissance|reconnaissance]] *and* how defenders find their own exposure. Platforms like MISP share indicators across the community.

## 1. Threat intelligence: the pyramid of pain
<!-- bite: 4a5adb51-66a6-42db-a7b6-4b300fd83808 -->

There's a hierarchy of how much an indicator *costs the attacker* to change. IOCs — hashes, IPs, domains — are the **lowest** rung: an attacker swaps a hash or rents a new server for pennies, so blocking them helps for a day.

The high-value intel is **TTPs** (Tactics, Techniques, Procedures) — *how* an adversary behaves. Changing their whole method (how they move sideways, how they persist) is expensive and slow for them, so a detection built on behaviour survives where a blocklist of IPs rots overnight. This is why the frameworks below describe *behaviour*, not indicators — and why a hunt targets a technique, not an IP.

## 2. The frameworks — a shared language
<!-- bite: 185d1c29-6b52-40b2-8464-1b47e1a83760 -->

Three frameworks let defenders describe, detect and communicate about attacker behaviour. **The cyber kill chain** (Lockheed Martin) models an intrusion as seven sequential stages:

![The seven sequential stages of the cyber kill chain — reconnaissance, weaponisation, delivery, exploitation, installation, command and control, and actions on objectives — where detecting the intrusion at any one stage breaks the chain and the attack fails.](../images/so-kill-chain.svg)

The value: every stage is a chance to *break the chain*. Detect and disrupt at any step and the attack fails before its goal. It maps cleanly onto the offensive [[cybersecurity/02-ethical-hacking/02-penetration-testing-methodology|pentest methodology]] — the same stages, seen from the defender's side.

## 2. The frameworks: ATT&CK and the diamond model
<!-- bite: efa97a96-0f8e-4952-86c3-5718cd8738ae -->

Two more, each with a different job.

**MITRE ATT&CK** is the industry-standard knowledge base of adversary tactics and techniques, drawn from real attacks. It's a matrix: **tactics** across the top (the *why* — Initial Access, Persistence, Privilege Escalation, Lateral Movement, Exfiltration) and **techniques** underneath (the *how* — each with an ID like `T1566` Phishing or `T1110` Brute Force). It's the lingua franca of blue teams: detection rules, threat reports and hunts are all tagged with ATT&CK technique IDs, so everyone means the same thing. **If you learn one framework deeply, learn this one.**

**The diamond model** analyses a single intrusion through four linked points — **Adversary, Capability, Infrastructure, Victim** — to understand *who* attacked *how* against *whom*, useful for attribution and linking related incidents.

## 3. Threat hunting
<!-- bite: 71d82747-0dba-4cf2-b729-8c832fd858dd -->

**Threat hunting** is proactively searching for attackers who evaded your automated detection — *assuming breach* and going to look, rather than waiting for an alert. A hunt is **hypothesis-driven**:

> "If an attacker used pass-the-hash for lateral movement (ATT&CK `T1550.002`), I'd see one account authenticating to many machines in a short window from an unusual host. Let me query for that."

The hunter forms the hypothesis from ATT&CK knowledge, queries the SIEM or EDR data, and confirms or refutes it. The crucial last step: **turn any finding into a new automated detection**, so the next occurrence alerts on its own and you never hunt for *that* technique by hand again. Hunting is what separates a mature SOC from one that only watches its alert queue — it's how you find the adversaries who never trip a signature.

## Terms used in this lesson
<!-- bite: ad064b42-972d-4413-8865-fee2095316d5 -->

1. **Threat intelligence**: This is organised knowledge about adversaries — who they are, what they target, how they operate — used to defend proactively instead of reacting.
2. **IOC (Indicator of Compromise)**: This is a concrete artefact of an attack — a malicious IP, domain, URL or file hash — that you can match against your logs. Cheap for an attacker to change.
3. **TTPs (Tactics, Techniques, Procedures)**: This is *how* an adversary behaves. Much harder for them to change than an IOC, so detections built on TTPs last longer.
4. **OSINT (Open-Source Intelligence)**: This is intelligence gathered from public sources — WHOIS, DNS, certificate logs, Shodan, breach dumps. Used by attackers for recon and by defenders to find their own exposure.

## Terms used in this lesson: frameworks and hunting
<!-- bite: f3c9f7af-6bc3-4349-aaa9-b53ca1b177a0 -->

5. **Cyber kill chain**: This is Lockheed Martin's model of an intrusion as seven stages; disrupting any stage breaks the attack.
6. **MITRE ATT&CK**: This is the standard knowledge base of adversary tactics (the *why*) and techniques (the *how*, each with an ID like `T1566`), used as the shared language of blue teams.
7. **Diamond model**: This analyses one intrusion through four points — adversary, capability, infrastructure, victim — for attribution and linking incidents.
8. **Threat hunting**: This is proactively searching log and endpoint data for attackers who evaded detection, driven by a specific hypothesis, and ending by writing a new detection.

## Worked example — map your own labs to ATT&CK
<!-- bite: e0dd1310-71d0-4b3b-9b2d-8d864f0d6930 -->

You've already *performed* a chain of attacks in this course. Naming them in ATT&CK is how a SOC would describe them — and it's the fastest way to learn the matrix. Take what you did and tag each step:

| What you did (lesson) | ATT&CK tactic | Technique (ID) |
|---|---|---|
| `nmap`/recon on the lab VPS (02-eth-hacking) | Reconnaissance | Active Scanning (`T1595`) |
| `crt.sh` for subdomains (04-web/03) | Reconnaissance | Search Open Technical Databases (`T1596`) |
| Login SQL injection on Juice Shop (02-eth/07) | Initial Access | Exploit Public-Facing Application (`T1190`) |
| Password spraying (06/04) | Credential Access | Brute Force: Password Spraying (`T1110.003`) |
| ARP spoofing MITM (06/02) | Credential Access / Collection | Adversary-in-the-Middle (`T1557.002`) |

**Predict first:** which tactic is missing from your chain that a real intruder would need next, once they have a foothold and credentials?

## Worked example: reading the map
<!-- bite: 31a85908-df94-40fa-83d4-c20df9da910c -->

The gap is **Lateral Movement** and **Persistence** — you got *in* and got *credentials*, but a real adversary then spreads to other machines and installs a way back. That's not a flaw in your labs; it's what the later [[cybersecurity/12-active-directory/index|Active Directory]] section covers, and ATT&CK is exactly how you'd notice the gap.

This map is also a *defender's to-do list*. Each technique ID links to ATT&CK's page of **detections and mitigations** for it. `T1110.003` (spraying) tells you to detect distinct-users-per-IP — which is precisely the rule you wrote in lesson 2. The framework turns "we got attacked" into "here are the twelve specific things to detect", in a vocabulary every tool and report shares.

## Worked example: run one hunt
<!-- bite: 7f1fdad6-20ad-4937-974b-0aa678035e4c -->

Now hunt, hypothesis-first. Pick a technique from the map and ask what it would look like in data you have. For **spraying (`T1110.003`)** against your lab's `auth.log`:

> **Hypothesis:** if someone sprayed us, one source IP failed against many distinct usernames in a short window.

```bash
# Hunt: source IPs that failed against 5+ distinct users
grep "Failed password" /var/log/auth.log \
  | awk '{for(i=1;i<=NF;i++) if($i=="from") ip=$(i+1); for(i=1;i<=NF;i++) if($i=="user") u=$(i+1); print ip, u}' \
  | sort -u | awk '{c[$1]++} END{for(i in c) if(c[i]>=5) print c[i]" distinct users from "i}'
```

If a row comes back, the hypothesis is **confirmed** — go to [[cybersecurity/07-security-operations/04-incident-response|incident response]]. Either way, the hunt's real output is the *rule*: you just proved the query works, so promote it to a standing Sigma detection (lesson 2) and you never hunt for spraying by hand again. That promotion — hunt once, detect forever — is the entire point.

## Common pitfalls and traps
<!-- bite: c2ae9505-d25d-43bd-9341-058db30006f2 -->

1. **Collecting IOCs and calling it intelligence.** A feed of IPs to block is the lowest, most perishable rung. Invest in understanding TTPs.
2. **A hunt with no hypothesis.** "Let me look around the logs" finds nothing. State what technique you're hunting and what its evidence would look like *before* you query.
3. **Finding something and not writing a rule.** An un-promoted hunt finding means you'll hunt the same thing again next month. Always end a hunt by automating it.
4. **Treating ATT&CK as trivia.** Its value is operational: every technique links to concrete detections and mitigations. Use it as a checklist, not a glossary.
5. **Hunting without good telemetry.** You can't hunt in data you don't collect. Hunting depends on the logging foundation from lesson 2.

## Check your understanding
<!-- bite: 7617a535-dce5-47e1-a0fe-bda79af6274d -->

Try each one before you open the answer.

1. <!-- q: mcq id="7747b768" -->
   A vendor sells a feed of "the latest malicious IP addresses" to block. Per the pyramid-of-pain idea, why is this the *least* durable kind of intelligence?

   - [ ] IP addresses are hard to collect.
   - [x] An attacker can swap IPs cheaply and instantly, so a blocklist of them is stale almost immediately.
   - [ ] IP addresses are encrypted.
   - [ ] Blocking IPs is illegal.

   <details><summary>Answer</summary>

   IOCs like IPs, domains and hashes are the lowest rung: trivially cheap for an attacker to change. Durable detection targets *TTPs* — how the adversary behaves — because changing their whole method is slow and expensive for them. That's why a behaviour-based rule outlives an IP blocklist.

   </details>

2. <!-- q: mcq id="38c3faf0" -->
   What is MITRE ATT&CK, and why is it called the "lingua franca" of blue teams?

   - [ ] A firewall product that blocks known attacks.
   - [x] A knowledge base of adversary tactics and techniques (each with an ID like T1566) that detection rules, reports and hunts all reference, so everyone means the same thing.
   - [ ] A password-cracking tool.
   - [ ] A compliance framework for audits.

   <details><summary>Answer</summary>

   ATT&CK is a shared catalogue of real-world attacker behaviour, organised as tactics (the why) and techniques (the how, each with a stable ID). Because detections, threat reports and hunts are all tagged with those IDs, teams and tools communicate precisely — "we detect T1110.003" is unambiguous.

   </details>

3. <!-- q: gap id="42ed8e7c" answers="break|disrupt|interrupt" -->
   The cyber kill chain's main lesson for defenders is that every one of its seven stages is a chance to ___ the chain: detect and disrupt the intrusion at any single stage and the whole attack fails before reaching its goal.

   <details><summary>Answer</summary>

   Break (disrupt/interrupt) the chain. Because the stages are sequential — recon, weaponise, deliver, exploit, install, command-and-control, act — stopping the attacker at any one of them prevents everything after it. Defenders aim to catch the intrusion as early in the chain as possible.

   </details>

4. <!-- q: mcq id="bf9550f8" -->
   What makes threat hunting different from running detection rules?

   - [ ] Hunting is fully automated; detection is manual.
   - [x] Hunting proactively searches for attackers who evaded the rules, starting from a specific hypothesis, rather than waiting for a pre-written rule to fire.
   - [ ] Hunting only looks at firewall logs.
   - [ ] Hunting requires no log data.

   <details><summary>Answer</summary>

   Detection waits for known-bad patterns you already wrote rules for. Hunting assumes a breach slipped past those rules and goes looking, driven by a hypothesis about a specific technique ("if they did X, I'd see Y"). A good hunt ends by converting its finding into a new automated detection.

   </details>

5. <!-- q: exact id="b79d902e" answer="T1110.003" accept="t1110.003|T1110|t1110" -->
   You performed password spraying — one common password across many accounts — against your lab. In MITRE ATT&CK, this maps to Brute Force: Password Spraying, whose technique ID is ___.

   <details><summary>Answer</summary>

   `T1110.003` (a sub-technique of `T1110`, Brute Force). Tagging your own attack with its ATT&CK ID is how a SOC would describe it, and ATT&CK's page for that ID lists the exact detections (distinct users per source IP) and mitigations (MFA, lockout) for it.

   </details>

6. <!-- q: open id="8c902cbe" -->
   You run a hunt and confirm that one internal host authenticated to twelve other machines in two minutes — consistent with lateral movement. Beyond escalating it as an incident, what is the one step that makes the hunt worth repeating, and why does skipping it waste the effort?

   <details><summary>Answer</summary>

   Promote the hunt query into a standing automated detection (e.g. a Sigma rule for "one account authenticating to N+ hosts in a short window"). The whole value of hunting is that it finds techniques your rules missed; if you don't automate the finding, the same technique can recur next month and you'll have to hunt for it manually all over again. "Hunt once, detect forever" — each successful hunt should shrink the space of things you still have to hunt for by hand.

   </details>

## Practice — map an attack and hunt for it
<!-- bite: f92f1d08-75fc-4bf4-b33f-a882cddf19af -->

**Task.** Take one attack you haven't mapped yet and carry it through the whole loop.

1. Pick an attack from an earlier lesson (DNS spoofing, the webhook forgery attempt, directory brute-forcing). Find its ATT&CK tactic and technique ID on attack.mitre.org.
2. Read that technique's "Detection" section and write down what evidence it leaves in logs you collect.
3. Form a hypothesis and write a query (shell or Sigma) that would find it.
4. If you can reproduce the attack on your lab, run it and confirm the query fires.

## Practice: when it's done
<!-- bite: 79b60b3e-8df8-4eb1-bcb4-00d577cb3b82 -->

Here's how you know the task is finished.

**Done when:** you can state the attack's ATT&CK tactic and technique ID, you have a query that would detect it, and (if reproducible) you confirmed it fires on the real attack and not on normal traffic. Record the technique ID and query in `cybersecurity/LIVE-RUNS-TODO.md`. Bonus: promote the query to a standing detection in your lesson-2 rule set.

## Before moving on
<!-- bite: e04c2669-42e3-4df8-90bd-68f7dfe7ff7c -->

You can now tell intelligence levels apart and place IOCs vs TTPs, describe the kill chain, ATT&CK and the diamond model and what each is for, map an attack to ATT&CK technique IDs, and run a hypothesis-driven hunt that ends in a new detection.

**Recap for later lookup:** intelligence = strategic / operational / tactical; IOCs (IPs, hashes — cheap to change) vs TTPs (behaviour — durable). Frameworks: kill chain (7 stages, break any one), ATT&CK (tactics × techniques with IDs — the shared language), diamond model (adversary/capability/infrastructure/victim). Hunting = hypothesis-driven search for what evaded detection, ending by automating the finding. Spraying = `T1110.003`.

Next: [[cybersecurity/07-security-operations/04-incident-response|incident response]] — what you do the moment a hunt or an alert turns up a real, confirmed attacker.

## Related
<!-- bite: 8f6346b9-754f-4eeb-8068-3f919a91507f -->

- [[cybersecurity/07-security-operations/02-logging-siem-and-detection|Logging, SIEM and detection]] — the data a hunt queries and where its findings become rules.
- [[cybersecurity/02-ethical-hacking/03-reconnaissance|Reconnaissance]] — OSINT from the attacker's side, the mirror of defensive intel.
- [[cybersecurity/07-security-operations/04-incident-response|Incident response]] — what a confirmed hunt finding triggers.

## About this lesson
<!-- bite: baa81938-5d8e-4bee-88e4-659a68285adf -->

**Level:** Advanced. **Covers:** strategic/operational/tactical intelligence, IOCs vs TTPs and the pyramid of pain, OSINT, the cyber kill chain, MITRE ATT&CK and the diamond model, hypothesis-driven threat hunting, and a hands-on exercise mapping your own earlier attacks to ATT&CK technique IDs and running a hunt against your lab's auth log. **Where it sits:** lesson 3 of the [[cybersecurity/07-security-operations/index|Security Operations]] section. **Sources:** the original vault note (from the roadmap.sh cyber-security roadmap), rebuilt to the [[COURSE-STANDARD|course standard]] with an ATT&CK mapping and hunt exercise; the hunt query is tracked for a live run in `cybersecurity/LIVE-RUNS-TODO.md`.
