---
id: 4fe354f5-5f28-4f60-9f73-174d5c1d0ee7
---

# Defensive Architecture

**Defensive architecture is building a system with many layers of protection instead of one, so that if a single layer fails, the next still stops the attacker.**

## Before you start
<!-- bite: 115a1e6d-d825-4578-90d4-d41c6763bc16 -->

You should have:

- Built most of the individual layers already — a firewall → [[cybersecurity/03-network-security/01-firewalls|firewalls]], segmentation → [[cybersecurity/03-network-security/02-network-segmentation|segmentation]], HTTPS → [[cybersecurity/04-web-security/03-https-and-tls|HTTPS and TLS]], and authentication → [[cybersecurity/04-web-security/02-secure-authentication|secure authentication]].
- Met the attacks these defend against → [[cybersecurity/06-attacks-and-threats/index|attacks and threats]].
- A Linux machine (your laptop or lab VPS) and a terminal.

After this lesson you will be able to:

1. Explain defence in depth and zero trust, and why neither relies on a single control.
2. Harden a machine: shrink its attack surface and say what each step removes.
3. Audit your own machine's attack surface and hardening level, and measure a before-and-after.
4. Place the blue, red and purple teams, and say why architecture comes before detection.

**Study route.** Kid version and §1–4, then the worked example: auditing and hardening your own box with `ss` and `lynis`.

## What defensive architecture is
<!-- bite: f73363df-6f1b-44b8-a23c-87aa7fb63534 -->

Everything earlier in this course was one control at a time: a firewall here, HTTPS there, a hashed password somewhere else. This lesson is the strategy that ties them together: how you arrange controls so the whole system survives when one of them fails — because one of them *will* fail.

The core idea has a name: **defence in depth**. Instead of trusting any single wall, you stack several, so an attacker has to beat all of them and you only need one to hold. The modern refinement of it is **zero trust**: stop trusting anything just because it's "inside". Then **hardening** is the hands-on work of making each layer thinner to attack. Those three, plus the teams who run them, are this lesson.

## The kid version
<!-- bite: 49ac762b-63d8-4e73-8534-519bd73bf87d -->

Think of a bank. The money isn't protected by one thing. There's a locked front door, a guard watching, cameras, a counter the public can't cross, and a vault at the very back with its own thick door and time lock. A robber has to beat *all* of them. The guard only has to notice *one* thing wrong.

That's defence in depth: many layers, so no single failure is a disaster. If the front door is left unlocked one morning, the guard and the vault still stand between the robber and the money.

**Where the analogy stops working.** A bank trusts anyone past the front door less than the staff behind the counter — but it still trusts "staff" as a group. Zero trust goes further: it checks *every* person at *every* door every time, even staff, even deep inside, because a robber who steals a uniform shouldn't get a free pass. Online, a stolen password *is* that uniform.

## 1. Defence in depth
<!-- bite: 50aa1342-9323-462d-895f-577135943f8c -->

**Defence in depth** means no single control is trusted to stop everything, so you layer them. A request from the outside has to cross the firewall, *then* a segmented network, *then* a hardened host, *then* the application's own checks, *then* reach encrypted data — and monitoring watches across all of them.

![A single file of layers an attacker must pass one after another, from perimeter firewall through network segmentation, host hardening, application controls and data encryption to the crown jewels, with the defender needing only one layer to hold.](../images/so-defense-in-depth.svg)

The asymmetry is the whole point: the attacker must defeat *every* layer, the defender needs just *one* to catch or stop them. Each layer you already built is one of these. A phished password ([[cybersecurity/06-attacks-and-threats/01-social-engineering|social engineering]]) gets past "identity" but still meets segmentation and least privilege.

## 2. Zero trust
<!-- bite: 653feaae-a09a-4b99-b34a-fb551cbf7128 -->

The old model was "castle and moat": a hard perimeter, and everything inside trusted. It broke the moment work moved to the cloud, laptops and phones — there's no single wall any more. **Zero trust** replaces it with one rule: **never trust, always verify.** Its three tenets:

1. **Verify explicitly.** Authenticate and authorise *every* request on identity, device health and context — not on where it came from. Being "inside the network" grants nothing.
2. **Least privilege.** Give the minimum access needed, just in time. Assume any account can be stolen, so limit how far it reaches.
3. **Assume breach.** Design as if attackers are already inside: segment, encrypt everywhere, monitor continuously.

Zero trust is the architectural answer to *lateral movement* — why one stolen credential or one foothold shouldn't reach everything.

## 3. Hardening — shrinking the attack surface
<!-- bite: 11f27624-b5fc-4b84-ae9e-5e381c76fa26 -->

**Hardening** is removing what isn't needed and locking down what remains. The **attack surface** is everything an attacker could poke at — every open port, running service, default account, enabled feature. Every one you remove is one fewer thing to exploit *or* patch. The moves:

- Disable unused services and ports; remove default accounts; change default credentials.
- Run only what the machine must (*least functionality*): a web server doesn't need a database port open to the world.
- Patch promptly — most real attacks use *known*, unpatched bugs.
- Turn on the OS's own protections: `SELinux`/`AppArmor`, a host firewall, `ASLR`.
- Follow a baseline (the **CIS Benchmarks**) and enforce it at scale with config management (Ansible → [[devops/09-infrastructure-as-code/02-configuration-management|IaC]]).

You'll measure a machine's attack surface and hardening in the worked example.

## 4. The teams: blue, red, purple
<!-- bite: 6c8e7916-fda8-4df4-8eaf-00eeea6ef57c -->

Security operations is organised around adversarial roles:

1. **Red team** — offensive; simulates real attackers to find the weaknesses ([[cybersecurity/02-ethical-hacking/index|ethical hacking]] is the discipline).
2. **Blue team** — defensive; monitors, detects and responds. This whole section is the blue team's job.
3. **Purple team** — not a separate team but a *way of working*: red attacks, blue watches whether they caught it, and they share findings in a tight loop so detection actually improves. Offense and defence sharpening each other beats working in silos.

Architecture is the blue team's foundation: you can't monitor your way out of a flat, unhardened, over-permissioned network.

## Terms used in this lesson
<!-- bite: 92699c34-0440-4f81-bb24-8e83247ed4c5 -->

1. **Defence in depth**: This is layering several independent controls so that the failure or bypass of one is caught by the next. An attacker must beat every layer; a defender needs one to hold.
2. **Attack surface**: This is the sum of everything an attacker could interact with — open ports, running services, accounts, features. Hardening shrinks it.
3. **Zero trust**: This is the model that trusts nothing by default and verifies every request on identity and context, rather than trusting anything for being "inside" the network.
4. **Least privilege**: This is giving each account or process the minimum access it needs, so a stolen one reaches as little as possible.

## Terms used in this lesson: hardening and teams
<!-- bite: 8668256c-d1e3-4f54-b3d7-b67b05e0f0ea -->

5. **Hardening**: This is reducing a system's attack surface by removing unneeded services, accounts and features and locking down what's left.
6. **Lateral movement**: This is an attacker spreading from the first machine they land on to others inside the network. Segmentation and zero trust limit it.
7. **Blue team / red team**: The blue team defends (detects and responds); the red team attacks (simulates adversaries to find gaps).
8. **Purple team**: This is red and blue working together in a loop — attack, check detection, improve — rather than in isolation.

## Worked example — audit and harden your own box
<!-- bite: 51adcc12-e23c-4681-af82-52b205a68a7b -->

Hardening is abstract until you measure a machine. Use your own laptop or the lab VPS. **First, see the attack surface** — every port the machine is listening on:

```bash
ss -tulpn | grep LISTEN
```

Each line is a service reachable by someone. **Predict first:** before you run it, guess how many listening ports your machine has. Most people guess two or three and find eight — a printer service, a name resolver, a database bound to all interfaces it meant to keep local. Every surprise on that list is attack surface you didn't know you had.

## Worked example: measuring the hardening level
<!-- bite: 8e3c86c9-3069-4b70-a25f-6b118f8300e4 -->

`lynis` is a free hardening auditor. It runs hundreds of checks and prints a **hardening index** out of 100, with specific suggestions. Install and run it (read-only — it changes nothing):

```bash
sudo dnf install lynis     # Fedora; apt install lynis on Debian/Ubuntu
sudo lynis audit system
```

The end of the report is the part that matters:

```text
  Hardening index : 67 [#############       ]
  Suggestion: Install a firewall [FIRE-4512]
  Suggestion: Set a password on the GRUB bootloader [BOOT-5122]
  Suggestion: Disable unused services: avahi-daemon, cups [...]
```

That index is your baseline number — a measurable starting point, not a guess.

## Worked example: the before-and-after
<!-- bite: e29f23b6-9f7c-4874-8b67-d1d921bfae20 -->

Now harden one thing from the list and measure the change. Say `ss` showed a service you don't need listening (the common ones are `cups` printing and `avahi` discovery on a server). Disable it, then re-scan:

```bash
sudo systemctl disable --now cups.service avahi-daemon.service
ss -tulpn | grep LISTEN          # those ports are gone
sudo lynis audit system | grep "Hardening index"
```

The listening-port list is shorter and the hardening index ticks up. That's defence in depth made concrete: you removed attack surface and the number proves it. Do the same for the firewall suggestion (you already built one in [[cybersecurity/03-network-security/01-firewalls|firewalls]]) and watch it climb again.

This is exactly what a blue team does at scale — baseline, harden, re-measure — only across thousands of machines with Ansible instead of one by hand.

## Common pitfalls and traps
<!-- bite: c13298f7-29d1-476a-9325-4bedbcff8cce -->

1. **One strong wall, nothing behind it.** A great firewall and a flat, trusting internal network means one phished password owns everything. Depth, not a single wall.
2. **"Inside = safe."** The castle-and-moat assumption behind most breaches. Verify every request, including internal ones.
3. **Hardening once and never again.** New packages add services, updates change defaults. Re-audit on a schedule.
4. **Chasing the hardening index instead of the real risks.** The number is a guide, not the goal; disabling a service you actually need to score points is self-harm.
5. **Binding services to all interfaces by default.** A database on `0.0.0.0` is reachable from the internet; bind it to `localhost` or a private network. This is where `ss` earns its keep.

## Check your understanding
<!-- bite: 8590137c-62bc-402a-b31f-4a08825f7c9c -->

Try each one before you open the answer.

1. <!-- q: mcq id="1d4298c1" -->
   A company has an excellent perimeter firewall, but once you're past it the internal network is flat and every service trusts every other. An attacker phishes one employee's laptop. What principle did this design most violate?

   - [ ] Encryption in transit
   - [x] Defence in depth — there were no layers behind the perimeter to contain the breach
   - [ ] Strong password hashing
   - [ ] Certificate transparency

   <details><summary>Answer</summary>

   Defence in depth. A single perimeter with nothing behind it means one bypass reaches everything. Segmentation, least privilege and host hardening are the inner layers that would have contained the phished foothold. Zero trust is the modern name for "don't trust the inside either".

   </details>

2. <!-- q: gap id="3c4f7427" answers="attack surface" -->
   Everything an attacker could interact with on a machine — every open port, running service, default account and enabled feature — is collectively called its ___.

   <details><summary>Answer</summary>

   Its attack surface. Hardening is the work of shrinking it: fewer services, fewer open ports, no default accounts. Every item removed is one fewer thing to exploit or patch.

   </details>

3. <!-- q: mcq id="61484b1c" -->
   Which statement best captures *zero trust*?

   - [ ] Encrypt all data at rest and in transit.
   - [x] Verify every request on identity and context, and never grant access just because it came from inside the network.
   - [ ] Trust internal traffic but inspect everything from the internet.
   - [ ] Give every user administrator rights for convenience.

   <details><summary>Answer</summary>

   Zero trust = never trust, always verify. The old castle-and-moat model trusted anything inside the perimeter; zero trust checks every request regardless of origin, which is what stops a single stolen credential from moving laterally through the network.

   </details>

4. <!-- q: mcq id="71d81b19" -->
   A red team runs a simulated attack. The blue team then checks their monitoring to see what they caught and what they missed, and the two groups adjust the detection rules together. What is this collaborative way of working called?

   - [ ] A bug bounty
   - [ ] A penetration test
   - [x] Purple teaming
   - [ ] A tabletop exercise

   <details><summary>Answer</summary>

   Purple teaming: red (offense) and blue (defence) working in a loop — attack, check detection, improve — rather than in silos. It's the fastest way to turn "we have rules" into "our rules actually fire".

   </details>

5. <!-- q: exact id="ebae3916" answer="localhost" accept="127.0.0.1|loopback" -->
   `ss -tulpn` shows your database is listening on `0.0.0.0:5432`, meaning it's reachable from any network including the internet. To keep it reachable only from the same machine, you should bind it to this address instead.

   <details><summary>Answer</summary>

   `localhost` (127.0.0.1, the loopback address). Binding to `0.0.0.0` exposes the service on every interface; binding to localhost keeps it private to the machine. This is a classic hardening fix and a common real-world exposure.

   </details>

6. <!-- q: open id="6430a453" -->
   Your lynis hardening index went from 67 to 72 after you disabled two unused services and enabled the firewall. A colleague says "the number went up, so we're more secure". In what sense is that true, and in what sense is it misleading?

   <details><summary>Answer</summary>

   True in that you genuinely removed attack surface — fewer listening services means fewer things to exploit or patch, and that's real risk reduction you can point to. Misleading in that the index is a weighted checklist, not a measure of your actual risk: it can't see your weakest real control (an over-permissioned app, a reused admin password, an unpatched dependency), and chasing the number can tempt you to disable something you actually need. Use it as a baseline and a prompt, not a scoreboard.

   </details>

## Practice — harden the lab VPS
<!-- bite: 81773e15-20ab-4225-bf71-5034df8dacfa -->

**Task.** On your lab VPS (or laptop), take a hardening baseline and improve it deliberately.

1. Run `ss -tulpn | grep LISTEN` and write down every listening service. For each, decide: needed, or remove?
2. Run `sudo lynis audit system` and record the hardening index and the top five suggestions.
3. Fix three suggestions that don't break anything you need (disable a service, bind a port to localhost, enable the firewall from the [[cybersecurity/03-network-security/01-firewalls|firewalls]] lesson).
4. Re-run both commands and record the new numbers.

## Practice: when it's done
<!-- bite: b610826c-6b83-4434-9884-f270c4c5aa0e -->

Here's how you know the task is finished.

**Done when:** your listening-port list is shorter than it started, your hardening index went up, and you can name for each change *what attack surface it removed*. Record the before-and-after numbers in `cybersecurity/LIVE-RUNS-TODO.md`. Nothing you rely on should have broken — if it did, that service was "needed" after all, which is itself a finding.

## Before moving on
<!-- bite: c74af7ae-bb6e-41a4-82d6-4ac9cf1c7a4e -->

You can now explain defence in depth and zero trust, harden a machine and name what each step removes, measure a box's attack surface and hardening level before and after, and place the blue, red and purple teams.

**Recap for later lookup:** defence in depth = layers, attacker beats all, defender needs one. Zero trust = never trust, always verify; verify explicitly, least privilege, assume breach. Hardening = shrink the attack surface (fewer services, ports, accounts; patch; OS protections; CIS baseline). `ss -tulpn` shows listening services; `lynis audit system` gives a hardening index. Blue defends, red attacks, purple is the loop between them.

Next: [[cybersecurity/07-security-operations/02-logging-siem-and-detection|logging, SIEM and detection]] — a well-architected system makes failures *noisy and survivable*, and detection is how you hear the noise. Architecture determines how much the blue team can even see.

## Related
<!-- bite: 60f5b6f4-dd55-4fe4-bfe4-433d25071e88 -->

- [[cybersecurity/03-network-security/02-network-segmentation|Network segmentation]] — a core defence-in-depth and zero-trust layer, built hands-on.
- [[cybersecurity/07-security-operations/02-logging-siem-and-detection|Logging, SIEM and detection]] — monitoring across the layers this builds.
- [[cybersecurity/08-governance-risk-and-compliance/index|Governance, risk and compliance]] — the frameworks (CIS, NIST) that mandate this.

## About this lesson
<!-- bite: 54cac6f1-3efd-46c3-8dce-22972c81334a -->

**Level:** Intermediate. **Covers:** defence in depth, zero trust (verify explicitly, least privilege, assume breach), system hardening and the attack surface, the blue/red/purple teams, and a hands-on audit-and-harden lab with `ss` and `lynis`. **Where it sits:** lesson 1 of the [[cybersecurity/07-security-operations/index|Security Operations]] section, the strategy the rest of the section operates within. **Sources:** the original vault note (from the roadmap.sh cyber-security roadmap), rebuilt to the [[COURSE-STANDARD|course standard]] with a measurable hardening lab; the `ss`/`lynis` commands are tracked for a live run in `cybersecurity/LIVE-RUNS-TODO.md`.
