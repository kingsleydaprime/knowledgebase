---
id: 725c5d4f-5178-4266-a045-1f23c9c524d1
---

# Attacker and Hacker Types

**Attackers differ in why they attack, how much skill and money they have, and whether they're allowed to, and knowing which kind is realistic for you decides what you defend against.**

## Before you start
<!-- bite: c9818950-fcae-45c5-bde6-41dc888c01ab -->

You should have:

- Met assets, threats and risk → [[cybersecurity/01-fundamentals/01-what-is-cybersecurity|what is cybersecurity]].
- Met the CIA triad → [[cybersecurity/01-fundamentals/02-cia-triad|the CIA triad]].

After this lesson you will be able to:

1. Explain white, grey and black hat, and why permission, not skill, is the line.
2. Describe the main kinds of attacker by motive and resources, from bots to nation-states.
3. Explain why insiders and automated attacks matter more than the headlines suggest.
4. Pick the realistic attackers for a given organisation, and say what that means for its defences.

**Study route.** Kid version and §1–4, then the worked example: who would really attack Mama Put?

## What attacker types are
<!-- bite: 40fa3c84-c2b7-4174-adee-83b0da53af62 -->

Lesson 01 called a threat "someone or something that could cause harm". This lesson is about the *someone*. The word "hacker" in films means a hooded genius. Real attackers are mostly much more ordinary: programs that try every door, criminals running a business, and sometimes people who already have a key.

Knowing which of them is realistic for you is what keeps security sensible. A food app doesn't need defences built for spies, and a bank can't get away with defences built for bored teenagers. By the end you'll have Mama Put's realistic attackers listed, ready for the threat model in lesson 05.

## The kid version
<!-- bite: 0e3c5c20-98c6-4347-b8f1-19fe3f15551b -->

Think about who might take sweets from a shop. A small child might grab one when nobody's looking. A gang might rob the till every week as a business. An unhappy shop worker might help themselves, because they already have the keys. And very rarely, a master thief might plan for months to steal one priceless item from a museum.

The shop owner doesn't defend against all of them equally. They put the sweets where kids can't reach, lock the till, and keep an eye on who has keys. They don't build a museum vault for the sweets.

**Where the analogy stops working.** A shop only meets the thieves who walk past it. Online, every shop is next to every thief in the world, and the "small child grabbing sweets" is a program that visits millions of shops a day. So the most common attacker online isn't a person choosing you at all.

## 1. The hats — permission is the line
<!-- bite: cea29d58-0b30-4427-a01e-6509cbdb42f3 -->

"Hacker" really just means someone very good at making systems do things they weren't obviously built to do. It says nothing about whether they're good or bad. The field uses hat colours for that:

1. **White hat** — hacks with written permission, to help: penetration testers, bug bounty hunters, researchers who report bugs properly. This is ethical hacking.
2. **Black hat** — hacks without permission, to harm or profit: stealing data, ransomware, fraud.
3. **Grey hat** — hacks without permission but without harmful intent, like testing a site uninvited and then reporting the bug.

Remember this one: **the difference between white and grey isn't skill or kindness; it's permission.** A grey hat who means well has usually still broken the law, because accessing a system without permission is the crime. That's why the ethical-hacking section starts with [[cybersecurity/02-ethical-hacking/01-rules-of-engagement-and-legal|rules of engagement]] before any tool.

## 2. Attackers by motive and resources
<!-- bite: 29757f12-c368-435c-b4bd-832a63100b20 -->

Beyond the hats, attackers differ in two ways that matter most: **why** they attack, and **what they can spend** (skill, money, time).

1. **Automated attacks and bots** — programs that scan the whole internet for weak passwords, old software and open databases. No one chose you; you were simply reachable. By far the most common attack on any small site.
2. **Script kiddies** — low-skill people using tools others wrote, often for fun or bragging rights.
3. **Cybercriminals** — attacking as a business, for money: ransomware gangs, card thieves, fraudsters, people who sell stolen logins. Organised, and the biggest source of real damage by volume.
## 2. Attackers by motive: causes, insiders and governments
<!-- bite: 3339600c-2e43-4ec5-bf36-8e35b7a61176 -->

The last three kinds attack for reasons other than quick money.

4. **Hacktivists** — attacking for a cause: defacing sites, leaking data, flooding services to make a point.
5. **Insiders** — staff, ex-staff or contractors who misuse access they were given, on purpose or by mistake.
6. **Nation-state groups (APTs)** — government-backed teams with large budgets and patience, after secrets or strategic damage. Rare, and rarely interested in small businesses.

## 3. Two attackers people underrate
<!-- bite: 8b30002f-cd8e-4080-abdd-4be5e06cdbf3 -->

Two kinds deserve extra attention, because they're the most likely and the least respected.

**Automated attacks.** Put any server on the internet and, within minutes, programs start trying it. You'll see this in your own firewall logs in the [[cybersecurity/03-network-security/01-firewalls|network-security]] section: knocks on every port, all day, from all over the world. They aren't clever, but they're tireless, and they find every default password and every unpatched app. Most of the defence against them is boring basics: strong unique passwords, two-factor login, updates.

**Insiders.** An insider doesn't need to break in; they already have access. That's what makes them dangerous: the firewall, the password and the encryption are all on their side. Insider harm is often an accident, like a staff member sending a customer list to the wrong email, or falling for a phishing message. The defences are giving each person only the access their job needs, logging who did what, and removing access the day someone leaves.

## Terms used in this lesson
<!-- bite: 185c9602-da54-4cc4-a6dd-8f1ccf8809aa -->

1. **Hacker**: This is someone highly skilled at making systems do unexpected things. On its own, it says nothing about good or bad intent.
2. **White hat, grey hat, black hat**: These mean hacking with permission, without permission but without harmful intent, and without permission to cause harm.
3. **Script kiddie**: This is a low-skill attacker who runs tools other people wrote.
4. **Cybercriminal**: This is someone attacking for money, often as part of an organised group.

## Terms used in this lesson: the bigger threats
<!-- bite: ed80d09b-6694-426e-a756-312657165206 -->

The rest of the terms name the attackers with the most access or the most resources.

5. **Insider threat**: This is harm from someone who already has legitimate access, on purpose or by accident.
6. **Hacktivist**: This is someone attacking to promote a political or social cause.
7. **APT (advanced persistent threat)**: The letters stand for those words. It's a well-funded group, often backed by a government, that attacks patiently and stays hidden for months.
8. **Opportunistic versus targeted attack**: An opportunistic attack hits whoever is weak; a targeted attack picks one victim on purpose and works at it.

## 4. Why it matters — defend against your real attackers
<!-- bite: 2aa76e0d-fca6-4d35-81a2-eb9a19ff4475 -->

Different attackers need different defences, and money spent on the wrong ones is wasted. Two common mistakes go in opposite directions:

1. **Over-defending:** a small business buying expensive tools built for nation-state attacks, while its staff still share one admin password and nothing is patched. The bots walk in through the basics.
2. **Under-defending:** a bank or a payments company acting like nobody would target it specifically. Criminals with real budgets *will*, and basics aren't enough for them.

So the question to ask is: **who would realistically attack us, why, and with what?** The answer tells you which defences come first. Lesson 05 makes this a formal step, called threat modelling, and this lesson's list is its starting point.

## Worked example — who would really attack Mama Put?
<!-- bite: 8649e067-8002-4d3a-a850-3ed5570e13f5 -->

Go through the six kinds of attacker for Mama Put's food app. For each, ask: would they bother, and what would they want? **Predict first** which three are realistic.

1. **Bots:** yes, certainly. They try her login page and scan her server whatever she does. Want: any weak password or old software, to take over the server or steal data.
2. **Script kiddies:** possible. A defaced menu would be their idea of fun.
3. **Cybercriminals:** yes. Customer phone numbers sell, and a fake "paid" message gets free food. Ransomware gangs hit small businesses because they often pay.
4. **Hacktivists:** unlikely, unless Mama Put becomes part of a public argument.
5. **Insiders:** yes. Kitchen staff log into the app, and an ex-worker might still know a password.
6. **Nation-states:** no. She has nothing they want.

## Worked example: what that means for her defences
<!-- bite: a909a1d2-a73c-4a8d-a75c-356542b7f7a8 -->

Mama Put's realistic attackers are **bots, cybercriminals and insiders**. That gives a short, sensible list of what to do first:

1. Against bots: long unique passwords, two-factor on the admin login, rate limiting, and keeping software updated.
2. Against criminals: verify payment webhooks properly, keep tested backups for ransomware, and store as little customer data as possible.
3. Against insiders: give kitchen staff only the screens they need, log every change to orders and prices, and remove an employee's access the day they leave.

Notice what's *not* on the list: nothing aimed at spies. And notice how cheap most of it is. Matching defences to realistic attackers is what keeps security affordable for a business like hers.

## Common pitfalls and traps
<!-- bite: 218a1cfc-c6d3-432f-883e-71e494372f47 -->

1. **"Hacker" means criminal.** It means skilled. Say "attacker" or "criminal" when that's what you mean.
2. **"I meant well" as a defence.** Grey hat hacking is usually still illegal. Permission is the line.
3. **"Nobody would target us."** Nobody has to; bots target everyone reachable.
4. **Forgetting insiders.** The person with the keys skips every outside defence. Limit and log access.
5. **Defending against the wrong attacker.** Spy-grade tools with basic hygiene missing protect against nobody.

## Check your understanding
<!-- bite: 94c1737a-f807-4e7c-bb58-f650946040f5 -->

Try each one before you open the answer.

1. <!-- q: mcq id="88c1ae4f" -->
   A security researcher, without asking, tests a company's website, finds a serious bug, and reports it to the company politely, asking for nothing. What hat is this, and is it legal?

   - [ ] White hat, and legal, because the intent was good.
   - [x] Grey hat, and usually illegal, because the testing was done without permission.
   - [ ] Black hat, because all unrequested testing is criminal in intent.
   - [ ] White hat, because the bug was reported.

   <details><summary>Answer</summary>

   Grey hat. Good intentions don't make unauthorised access legal in most countries; permission is the line. The legal route is a bug bounty programme or the company's published disclosure policy, which gives that permission.

   </details>

2. <!-- q: mcq id="8e76fb22" -->
   A new web server is put on the internet with a default admin password. Within an hour it's taken over. Which attacker is most likely?

   - [ ] A nation-state group.
   - [ ] A hacktivist.
   - [x] An automated scanner trying default passwords on every reachable server.
   - [ ] An insider.

   <details><summary>Answer</summary>

   Automated attacks scan the whole internet constantly and try default passwords first. Nobody chose this server; it was simply reachable and weak.

   </details>

3. <!-- q: gap id="df1e02cb" answers="insider|insider threat" -->
   A finance employee who already has access to the payroll system quietly pays themselves extra each month. This kind of attacker is called an ___.

   <details><summary>Answer</summary>

   An insider (an insider threat). They bypass outside defences because their access is legitimate. Least privilege, logging, and separation of duties (two people for big payments) are what limit them.

   </details>

4. <!-- q: mcq id="dc972f60" -->
   Which attacker best fits this description: well funded, patient, uses custom tools, stays hidden inside a defence ministry's network for over a year, and takes secret documents?

   - [ ] A script kiddie.
   - [ ] A cybercriminal gang.
   - [x] An APT (advanced persistent threat).
   - [ ] A hacktivist.

   <details><summary>Answer</summary>

   An APT. Long, hidden, well-resourced campaigns after secrets, usually backed by a government, are what the name describes.

   </details>

5. <!-- q: mcq id="b70fdd74" -->
   A five-person accounting firm is choosing where to spend its small security budget. Which spend fits its realistic attackers best?

   - [ ] An advanced tool for detecting nation-state spies.
   - [x] Two-factor login for everyone, automatic updates, and tested backups.
   - [ ] A full-time red team.
   - [ ] Nothing, because small firms aren't attacked.

   <details><summary>Answer</summary>

   Its realistic attackers are bots, phishing criminals and ransomware gangs, and the basics stop most of them. Spy-grade tools without the basics leave the easy doors open.

   </details>

6. <!-- q: open id="e6f6be7d" -->
   Explain why insiders can be more dangerous than outside attackers even though there are far fewer of them, and name two defences.

   <details><summary>Answer</summary>

   Insiders already have legitimate access, so firewalls, passwords and encryption, the defences against outsiders, don't stop them; they're already past them. They also know where valuable data is and how the business works, and harm is often accidental (a misdirected email, a phished login). Defences: least privilege (each person sees and does only what their job needs), logging of who did what, separation of duties for sensitive actions, and removing access immediately when someone leaves.

   </details>

## Practice — your attackers, ranked
<!-- bite: 630d0dfe-01c3-4263-a0bc-27c5350611a3 -->

**Task.** Do the worked example for the app or organisation you used in lesson 01's practice.

1. Go through the six kinds of attacker. For each, write whether they'd realistically bother, and what they'd want.
2. Circle your top three.
3. For each of the three, write the two cheapest defences that would stop most of them.

## Practice: when your ranking is done
<!-- bite: 5d7acf1c-a184-44da-b2a5-2859ba7012b4 -->

Here is how you know the task is finished.

**Done when:** every one of the six has a yes or no with a reason, your top three each have two defences, and at least one defence is aimed at insiders. Keep it for lesson 05.

## Before moving on
<!-- bite: 7492b3a2-2b32-4e04-ae8b-e9daffe74ef1 -->

You can now explain the hats and why permission is the line, describe attackers by motive and resources, explain why automated attacks and insiders matter so much, and choose the realistic attackers for an organisation and the defences that follow.

**Recap for later lookup:** hacker = skill, not intent. White = permission; grey = no permission, no harm meant (still usually illegal); black = no permission, harm meant. Bots, script kiddies, cybercriminals, hacktivists, insiders, APTs. Bots hit everyone reachable; insiders skip outside defences. Defend against your realistic attackers, starting with the cheap basics.

Next: [[cybersecurity/01-fundamentals/04-security-principles|security principles]], the handful of rules that guide every defence against all of them.

## Related
<!-- bite: 2c4864e0-9ee1-44e6-8d3c-80feeee49e3a -->

- [[cybersecurity/02-ethical-hacking/01-rules-of-engagement-and-legal|Rules of engagement and the law]] — the permission line, made exact.
- [[cybersecurity/06-attacks-and-threats/index|Attacks and threats]] — what each kind of attacker actually does.
- [[cybersecurity/01-fundamentals/05-threat-modeling|Threat modelling]] — where this lesson's list gets used.

## About this lesson
<!-- bite: 6ae7f47e-b5f1-45fd-b1e8-e9a94a5d8f81 -->

**Level:** Beginner. **Covers:** white, grey and black hats and the permission line, attackers by motive and resources (bots, script kiddies, cybercriminals, hacktivists, insiders, APTs), opportunistic versus targeted attacks, why automated attacks and insiders are underrated, and choosing realistic attackers for Mama Put and the defences that follow. **Where it sits:** lesson 3 of the [[cybersecurity/01-fundamentals/index|Fundamentals]] section. **Sources:** the original vault note, rebuilt around the Mama Put running example.
