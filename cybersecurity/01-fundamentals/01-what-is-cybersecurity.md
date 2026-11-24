---
id: 0e1ef6eb-a4cf-42d3-a5ec-2924bad7abb7
---

# What Is Cybersecurity

**Cybersecurity is protecting computers, networks and data from being seen, changed or stopped by people who aren't allowed to.**

## Before you start
<!-- bite: c45c1fbc-2daf-4e1e-be30-cf912431e25e -->

You don't need anything except having used a website, an app and a password. This is the first lesson of the course.

After this lesson you will be able to:

1. Use the four words the field runs on (asset, threat, vulnerability, risk) correctly, about a real app.
2. Say what defensive and offensive security are, and why they need each other.
3. Name the main areas of the field, and find each one in this course.
4. Rank a list of risks by likelihood × impact, and explain why "fully secure" isn't a thing.

**Study route.** Kid version and §1–4, then the worked example on Mama Put. No computer needed beyond reading.

## What cybersecurity is
<!-- bite: a24e9747-6d73-4b04-93cc-23b2a2da66b0 -->

All through this course we'll keep coming back to one small business: **Mama Put**, a roadside food seller whose customers now order on their phones. Her app (you may have built its backend in the framework subjects) has a menu, customer accounts, orders, staff logins for the kitchen, and card payments through Paystack.

Mama Put isn't a bank or a government, but she still has plenty to lose: customers' phone numbers and addresses, the money flowing through payments, and the app itself, which is now how she earns a living. Cybersecurity is the work of keeping all of that safe. This lesson gives you the words to talk about it, a map of the field, and the one sum, likelihood × impact, that decides what to fix first.

## The kid version
<!-- bite: e0217cb7-efd4-4e92-aeaa-ffe704c6c1ea -->

Think about how you keep your house safe. You know what's valuable inside (your phone, your savings). You know who might want it (thieves). You know the weak spots (the back window that doesn't close properly). And you decide what to fix first: the broken window that faces the street, before the tiny window on the third floor.

Cybersecurity is exactly that, for computers and data: know what's valuable, who wants it, where you're weak, and fix the most dangerous weak spots first.

**Where the analogy stops working.** A house thief has to come to your street. On the internet, every app is "on the street" for every attacker in the world at once, and most attacks are run by programs that try every door on millions of houses every day, without caring whose house it is. That changes which weak spots matter most.

## 1. The four words
<!-- bite: 63962fc3-5379-42c1-b544-34cdb4757b94 -->

The whole field runs on four words, and people mix them up all the time. Here they are, with Mama Put.

1. **Asset** — something worth protecting. Mama Put's customer list, her payment account, her app being up at lunchtime.
2. **Threat** — someone or something that could cause harm. A criminal who steals customer data; a competitor; a power cut.
3. **Vulnerability** — a weakness a threat can use. The admin password is `mamaput123`; the database has no backups.
4. **Risk** — the chance of harm, and how bad it would be, when a threat meets a vulnerability on an asset.

Remember this one: **a vulnerability with no threat and no asset is just a curiosity; risk is where all three meet.** "The admin password is weak" is a vulnerability. "Anyone on the internet can guess the weak admin password and see every customer's address" is a risk.

## 2. Two sides of the same work
<!-- bite: e46f450a-de2d-46a1-92a1-80c19f8a493f -->

Cybersecurity has two sides, and they need each other.

**Defensive security**, often called the **blue team**, builds and runs systems so they resist attack: setting things up safely, watching for trouble, patching, responding when something happens. Most security jobs are on this side.

**Offensive security**, the **red team** or ethical hacking, attacks systems *with permission* to find the weak spots before a criminal does. It's how you check that defences really work, instead of hoping.

The line between ethical hacking and crime isn't skill; it's **permission**. The same command is a job with written permission and a crime without it. This course teaches attacks only against things you own, and [[cybersecurity/02-ethical-hacking/01-rules-of-engagement-and-legal|the rules of engagement]] lesson makes that line exact.

## 3. The map of the field
<!-- bite: 2ea8c36c-bbb3-47c6-b378-30980acada08 -->

Cybersecurity is a big field, and each part has a section in this course:

1. **Network security** — what can reach your machines, and protecting data as it travels → [[cybersecurity/03-network-security/index|network security]].
2. **Web and application security** — making the software itself safe → [[cybersecurity/04-web-security/index|web security]] and [[cybersecurity/14-api-security/index|API security]].
3. **Cryptography** — the maths behind secrecy and trust → [[cybersecurity/05-cryptography/index|cryptography]].
4. **Security operations** — watching, detecting and responding → [[cybersecurity/07-security-operations/index|security operations]].
5. **Cloud, identity and systems** — [[cybersecurity/09-cloud-security/index|cloud]], [[cybersecurity/12-active-directory/index|Active Directory]], [[cybersecurity/11-binary-exploitation/index|binary exploitation]] and [[cybersecurity/13-malware-and-reverse-engineering/index|malware]].
6. **Governance, risk and compliance** — rules, policies and the business side → [[cybersecurity/08-governance-risk-and-compliance/index|GRC]].
7. **Protecting yourself** — the same ideas for your own life → [[cybersecurity/10-protecting-yourself/index|protecting yourself]].

You don't need them all at once. This fundamentals section gives you the words and the way of thinking every one of them uses.

## Terms used in this lesson
<!-- bite: 37480ad4-3227-4d0c-a2a8-b14fdc5b1065 -->

1. **Asset**: This is anything worth protecting: data, money, a service being available, a reputation.
2. **Threat**: This is someone or something that could cause harm to an asset, on purpose or by accident.
3. **Vulnerability**: This is a weakness a threat could use, like a weak password, a bug, or a missing backup.
4. **Risk**: This is how likely harm is and how bad it would be. It's often scored as **likelihood × impact**.

## Terms used in this lesson: the two sides
<!-- bite: f6b0c137-7ae2-4f09-9a07-5edc19ee2d56 -->

The rest of the terms name the two sides of the work and the word for an attack that worked.

5. **Blue team**: This is the defenders: the people who build, watch and protect systems.
6. **Red team**: This is the attackers on the defenders' side: people who attack systems with permission to test them.
7. **Exploit**: This is using a vulnerability to actually cause harm, or the code that does it.
8. **Incident**: This is a security event that actually happened and needs a response, like a breach or an outage.

## 4. Nothing is fully secure — so rank by risk
<!-- bite: 7a83560c-cb45-4d86-b9c7-45d28b39b86c -->

There's no such thing as a fully secure system. New bugs are found every week, software changes, and people make mistakes. Security isn't a finish line; it's **raising the cost of an attack** above what attackers are willing to pay, and keeping it there.

Since you can't fix everything, you fix the biggest risks first. The usual way to rank them is to give each one a score:

**Risk = likelihood × impact.** Score each from 1 (low) to 3 (high), and multiply. A 9 is "fix today". A 1 is "write it down and maybe never".

This is why a weak password on an internet-facing admin page usually beats a clever, hard-to-use bug in a page nobody visits. Likelihood matters as much as how scary something sounds.

## Worked example — rank Mama Put's risks
<!-- bite: f25c4a84-110d-4903-8ece-cf6396bad581 -->

Here are four things wrong with Mama Put's setup. Score each one's likelihood and impact from 1 to 3, then multiply. **Predict first:** which is the top risk?

1. The admin dashboard is on the internet, and its password is `mamaput123`.
2. The database has never been backed up.
3. The menu page could be defaced, showing a rude message for a few hours.
4. A foreign government could steal her jollof recipe.

## Worked example: the scores
<!-- bite: 4ed2bcc7-3e67-4ad6-9d51-e7fbf2619678 -->

| Risk | Likelihood | Impact | Score |
|---|---|---|---|
| Weak admin password on the internet | 3: bots try common passwords on every login page, every day | 3: every customer's details, every order | **9** |
| No database backups | 2: disks fail, mistakes delete tables | 3: the whole business's records, gone | **6** |
| Menu page defaced | 2: it happens to small sites | 1: embarrassing, quick to fix | **2** |
| Government steals the recipe | 1: nobody's coming for it | 1: it's on her stall's sign anyway | **1** |

The weak password wins, and it's also the cheapest to fix: one long, unique password and a second factor. That's the usual pattern: **the top risks are often boring, and cheap to fix.** The scariest-sounding item came last.

## Common pitfalls and traps
<!-- bite: 8e4f4d61-5a07-4e99-94a8-046f080b81c4 -->

1. **Mixing up vulnerability and risk.** A weakness only becomes a risk when a threat can use it on something valuable.
2. **Fixing the scariest thing first.** Rank by likelihood × impact, not by how dramatic it sounds.
3. **Thinking "we're too small to be attacked".** Most attacks are automated and try everyone. Small sites are attacked constantly, precisely because they're often weak.
4. **Treating security as a project that finishes.** Software, threats and people change. It's ongoing.
5. **Thinking security is only technical.** Backups, staff habits, who has which password, and what you'd do in an emergency matter as much as any tool.

## Check your understanding
<!-- bite: aff8b30b-6c23-4923-989c-215184870a0d -->

Try each one before you open the answer.

1. <!-- q: mcq id="9b1b3a7f" -->
   A school's results website has a login page with no limit on password attempts. Which word describes "no limit on password attempts"?

   - [ ] Asset
   - [ ] Threat
   - [x] Vulnerability
   - [ ] Incident

   <details><summary>Answer</summary>

   It's a vulnerability, a weakness. The students' results are the asset, someone guessing passwords is the threat, and the risk is all three together.

   </details>

2. <!-- q: exact id="b102b70e" answer="6" -->
   A shop scores a risk's likelihood as 3 and its impact as 2, on 1-to-3 scales. Using risk = likelihood × impact, what is its score?

   <details><summary>Answer</summary>

   3 × 2 = 6. On a 1-to-9 scale, that's high: worth fixing soon, after anything scoring 9.

   </details>

3. <!-- q: mcq id="efd126d0" -->
   Two people run the same password-guessing tool against the same company's login page. One has written permission from the company; the other doesn't. What's the difference?

   - [ ] The one with permission is more skilled.
   - [x] Permission: the first is doing a security test, the second is committing a crime.
   - [ ] Nothing; both are ethical hacking.
   - [ ] The tool they use.

   <details><summary>Answer</summary>

   The action is identical. Written permission from someone with authority over the system is the whole difference between a job and a crime.

   </details>

4. <!-- q: mcq id="aa15681b" -->
   A small bakery's owner says "nobody would bother attacking us, we're tiny." Why is that wrong?

   - [ ] Because small businesses are always targeted by governments.
   - [x] Because most attacks are automated and try every site they can reach, whatever its size.
   - [ ] Because all bakeries store card numbers.
   - [ ] It isn't wrong; small sites are never attacked.

   <details><summary>Answer</summary>

   Bots scan the whole internet for weak passwords and old software without caring whose site it is. Small sites are often weaker, which makes them easy wins.

   </details>

5. <!-- q: mcq id="16532fb6" -->
   Four risks, scored likelihood × impact: A = 3 × 1, B = 1 × 3, C = 2 × 3, D = 2 × 2. Which should be fixed first?

   - [ ] A
   - [ ] B
   - [x] C
   - [ ] D

   <details><summary>Answer</summary>

   C scores 6; A and B score 3, and D scores 4. C is fixed first.

   </details>

6. <!-- q: open id="10dfaa88" -->
   Explain in your own words why "this system is fully secure" is never a true statement, and what security teams aim for instead.

   <details><summary>Answer</summary>

   New vulnerabilities are always being found, software and systems keep changing, and people make mistakes, so there's never a point where nothing can go wrong. Instead, teams aim to make attacks cost more than they're worth to attackers, fix the biggest risks first by likelihood × impact, and keep at it, watching, patching and testing, as things change.

   </details>

## Practice — your own risk list
<!-- bite: 3863f2ca-df4d-413e-8785-96b2877c1d47 -->

**Task.** Do the worked example for something of your own: an app you've built, or just your phone and online accounts.

1. List five assets (what would hurt to lose?).
2. For each, name one realistic threat and one vulnerability.
3. Score each risk's likelihood and impact from 1 to 3, and rank them.
4. For the top two, write one cheap fix each.

## Practice: when your list is done
<!-- bite: bb103e41-dfa0-4bf5-9796-4244b28c2434 -->

Here is how you know the task is finished.

**Done when:** you have five ranked risks with scores, and you've actually done the fix for the top one (a new password, turning on two-factor, making a backup). Keep the list; lesson 05 turns it into a proper threat model.

## Before moving on
<!-- bite: 08d72288-ed41-4a16-be45-7ad47d208fc0 -->

You can now use asset, threat, vulnerability and risk correctly, explain the two sides of the work and the permission line between them, find each area of the field in this course, and rank risks by likelihood × impact.

**Recap for later lookup:** asset (worth protecting), threat (could cause harm), vulnerability (a weakness), risk (where they meet; likelihood × impact). Blue team defends, red team tests with permission. Nothing is fully secure; raise the cost and fix the top risks first. The top risks are often boring and cheap.

Next: [[cybersecurity/01-fundamentals/02-cia-triad|the CIA triad]], the three things every one of those assets needs protecting.

## Related
<!-- bite: 22ace25c-3e09-43e6-9c16-7ca50bced573 -->

- [[cybersecurity/index|The cybersecurity course]] — the whole map.
- [[cybersecurity/08-governance-risk-and-compliance/01-risk-and-frameworks|Risk and frameworks]] — risk scoring as organisations do it.
- [[backend/frameworks/express/index|Mama Put API (Express)]] — the app this section keeps using as its example.

## About this lesson
<!-- bite: 2c68481d-40aa-4e46-b7bb-0d685385cca7 -->

**Level:** Beginner. **Covers:** assets, threats, vulnerabilities and risk; defensive and offensive security and the permission line; a map of the field and where each area sits in this course; why nothing is fully secure; and ranking risks by likelihood × impact, worked on Mama Put. **Where it sits:** lesson 1 of the [[cybersecurity/01-fundamentals/index|Fundamentals]] section, the first lesson of the course. **Sources:** the original vault note, rebuilt around the Mama Put running example.
