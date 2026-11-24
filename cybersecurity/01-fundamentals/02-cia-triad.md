---
id: 0bf33fe3-275c-4484-82fe-e63a938690d5
---

# The CIA Triad

**The CIA triad is the three things security protects about any data or system: confidentiality (only the right people see it), integrity (it stays correct), and availability (it works when it's needed).**

## Before you start
<!-- bite: 934e1475-3e2d-462d-a2e9-bf9c1464dca1 -->

You should have:

- Met assets, threats, vulnerabilities and risk → [[cybersecurity/01-fundamentals/01-what-is-cybersecurity|what is cybersecurity]].

After this lesson you will be able to:

1. Define confidentiality, integrity and availability, with an example of each going wrong.
2. Classify a security incident by which of the three it hits.
3. Name the main controls that protect each one.
4. Explain how the three pull against each other, and why availability is the one people forget.

**Study route.** Kid version and §1–4, then the worked example, where you classify six Mama Put incidents.

## What the CIA triad is
<!-- bite: ed5116d7-245d-4c3e-a1dc-cacc28f3405a -->

Lesson 01 said cybersecurity protects assets. But "protect" from *what*, exactly? It turns out nearly every security problem is one of three things going wrong: someone saw what they shouldn't, something got changed that shouldn't have, or something stopped working when it was needed.

Those three are the **CIA triad** (nothing to do with the American spy agency). Naming which one a problem hits is the fastest way to understand it, explain it, and pick the right fix. You'll use these three words in every lesson after this one.

## The kid version
<!-- bite: efba3d9f-a487-4711-bce7-bb466a9c19dc -->

Imagine your school report card. Three things could go wrong with it.

A classmate could read it without asking: that's a **confidentiality** problem. Someone could change your C into an A, or an A into an F: that's an **integrity** problem. Or it could get lost on results day so nobody can see it at all: that's an **availability** problem.

Keeping a report card safe means guarding against all three.

**Where the analogy stops working.** A report card is one piece of paper. Computer data is copied everywhere (backups, logs, other servers, people's phones), and every copy needs the same three protections. Often the original is well guarded and a forgotten copy is what leaks.

## 1. Confidentiality — only the right people see it
<!-- bite: 48215d6a-868a-4ba0-a48e-889abd229a07 -->

**Confidentiality** means information is seen only by the people and systems allowed to see it.

At Mama Put, that's customers' phone numbers and home addresses, staff passwords, and the Paystack secret key. It goes wrong through stolen passwords, a database left open to the internet, data sent without encryption, or a staff member who can see more than their job needs.

The main protections: **access control** (logging in, and checking what each user may see), **encryption** (so stolen or intercepted data is unreadable), and **least privilege** (each person and program gets only the access it needs, which lesson 04 covers).

## 2. Integrity — it stays correct
<!-- bite: b0930c8e-fcc9-4356-b545-9984a9113aa7 -->

**Integrity** means information stays accurate and unchanged, except by people allowed to change it, in the ways they're allowed to.

At Mama Put: an order's price, whether it's marked "paid", a customer's delivery address, the menu. It goes wrong when an attacker changes a price to ₦0, a forged message marks an unpaid order as paid, malware edits files, or even when an honest bug quietly corrupts data.

The main protections: access control again (who may *change* things), **hashes and signatures** to detect changes (the [[cybersecurity/05-cryptography/index|cryptography]] section), **audit logs** that record who changed what, and checks on every input.

Integrity failures are often the sneakiest. A leak is noticed when the data turns up online; a quietly changed price might never be noticed at all.

## 3. Availability — it works when it's needed
<!-- bite: 737dca8a-9835-43ab-b57b-8a6a175c76d9 -->

**Availability** means the system and its data can be used, by the right people, when they need them.

At Mama Put, availability is the whole lunchtime rush. If the app is down from 12 to 2, she loses the day's orders. It goes wrong through **denial-of-service** attacks that flood the app with traffic, **ransomware** that locks the data until a ransom is paid, a failed disk, a deleted table, or an unpaid hosting bill.

The main protections: **backups** (tested ones, which you've actually restored from), **redundancy** (more than one of anything important), capacity to handle busy times, and protection against traffic floods.

Availability is the one people new to security forget, because leaks get the headlines. For a lot of real businesses, an outage costs more than a leak.

## Terms used in this lesson
<!-- bite: 91be506b-3a35-46ed-8017-1e4144d9bbdd -->

1. **Confidentiality**: This means information is seen only by those allowed to see it.
2. **Integrity**: This means information stays accurate, and is changed only by those allowed, in allowed ways.
3. **Availability**: This means systems and data can be used when they're needed.
4. **Access control**: This is deciding who may see or do what, and enforcing it. Logging in (**authentication**) is the first half; checking permissions (**authorization**) is the second.

## Terms used in this lesson: the attacks and extras
<!-- bite: 56f2e5c3-5830-4830-85c6-fada19ef3586 -->

The rest of the terms name attacks you'll hear about, and two goals that extend the triad.

5. **DoS (denial of service)**: The letters stand for those words. It's an attack that makes a system unavailable, often by flooding it. **DDoS** is the same with traffic from many machines at once.
6. **Ransomware**: This is malware that encrypts a victim's data and demands payment to unlock it. It hits availability, and often confidentiality too, when the data is also stolen.
7. **Authenticity**: This means being sure who something came from. It's often listed alongside the triad.
8. **Non-repudiation**: This means someone can't credibly deny an action they took, because there's proof, like a signature or a reliable log.

## 4. The three pull against each other
<!-- bite: 7e0621db-df0d-45d6-af98-e9d62b13e1ab -->

You can't simply maximise all three. Strengthening one often costs another, so good security is a balance chosen for each system.

1. **Confidentiality against availability.** Very strict access (two approvals before anyone can see an order) protects data but slows the kitchen down at lunchtime. Lose the only copy of an encryption key and the data is perfectly confidential and completely unavailable.
2. **Integrity against confidentiality.** Detailed logs of every change protect integrity, but if they contain customers' addresses, the logs become something else to keep confidential.
3. **Availability against integrity.** Letting the app keep taking orders when the payment provider is down keeps it available, but some orders may later turn out unpaid.

The right balance depends on what matters most. For Mama Put at lunchtime, availability is king. For a hospital's patient records, integrity and confidentiality come first.

## Worked example — classify Mama Put's incidents
<!-- bite: 42b085a7-5b4e-4b1f-a705-aa980e7267a5 -->

Here are six things that could happen to Mama Put. For each one, decide which of C, I and A it hits (some hit more than one). **Predict first**, then check.

1. A bot floods the app with fake requests at 12:30, and nobody can order.
2. A hacker downloads the customer table, with phone numbers and addresses.
3. A customer edits the request their phone sends and pays ₦100 for a ₦3,000 order.
4. Ransomware encrypts the database, and the attackers threaten to publish it unless paid.
5. A kitchen worker can see every customer's full card details on the staff screen.
6. Someone sends a fake "payment received" message, and unpaid orders are cooked.

## Worked example: the answers
<!-- bite: af9f79e6-6d90-449a-abb2-68e3bcf59d82 -->

1. **Availability.** Nothing was seen or changed; it simply stopped working.
2. **Confidentiality.** Data was seen by someone who shouldn't see it.
3. **Integrity.** The price was changed by someone not allowed to change it.
4. **Availability and confidentiality.** The data is locked away (A), and it has also been stolen (C). Modern ransomware usually does both, which is why backups alone no longer solve it.
5. **Confidentiality.** Nothing was stolen yet, but people can see more than their job needs. That's a vulnerability waiting for a careless or bitter employee.
6. **Integrity** (and authenticity). The order's "paid" status was changed by a forged message. The fix, checking the message's HMAC signature, is in [[cybersecurity/05-cryptography/03-hashing-and-integrity|hashing and integrity]].

Notice that 3 and 6 lose Mama Put money directly and might go unnoticed for weeks. Integrity failures are quiet.

## Common pitfalls and traps
<!-- bite: 39cc6230-7115-4748-817a-fda2fa84c245 -->

1. **Only thinking about leaks.** Confidentiality gets the headlines, but changed data and outages are often costlier.
2. **Backups you've never restored.** A backup you haven't tested restoring is a hope, not an availability control.
3. **Guarding the original and forgetting the copies.** Logs, backups, exports and test databases need the same protection.
4. **Calling every problem a "breach".** Naming which of C, I and A it hits makes the real damage, and the right fix, clear.
5. **Maximising one property blindly.** Locking everything down so tightly that staff can't work just moves the failure from C to A.

## Check your understanding
<!-- bite: d0385101-611e-47cc-9a43-6489287c9eaa -->

Try each one before you open the answer.

1. <!-- q: mcq id="9a08413f" -->
   A hospital's appointment system is taken offline by a flood of traffic for six hours. No data is seen or changed. Which part of the triad is hit?

   - [ ] Confidentiality
   - [ ] Integrity
   - [x] Availability
   - [ ] None, because no data was touched

   <details><summary>Answer</summary>

   Availability. The system couldn't be used when it was needed, which is a serious harm for a hospital even though nothing leaked.

   </details>

2. <!-- q: mcq id="fbf44468" -->
   A student gets into the school's grading system and changes their own maths grade from 45 to 85. Which part of the triad is hit?

   - [ ] Confidentiality
   - [x] Integrity
   - [ ] Availability
   - [ ] Authenticity only

   <details><summary>Answer</summary>

   Integrity: the data was changed by someone not allowed to change it. If they also looked at other students' grades, confidentiality would be hit too.

   </details>

3. <!-- q: mcq id="607f2f46" -->
   Ransomware encrypts a company's files, and the attackers say they've also copied the files and will publish them unless paid. Which parts of the triad are hit? Choose all that apply.

   - [x] Confidentiality
   - [ ] Integrity
   - [x] Availability

   <details><summary>Answer</summary>

   Availability, because the files are locked, and confidentiality, because they've been copied out. That double attack is why good backups no longer fully solve ransomware: they bring the data back, but they can't un-leak it.

   </details>

4. <!-- q: gap id="297e73aa" answers="availability" -->
   A company encrypts its backups and then loses the only copy of the key. The data is still perfectly confidential, but the company has lost its ___.

   <details><summary>Answer</summary>

   Availability. It shows how pushing one property to the limit, here confidentiality, can wreck another.

   </details>

5. <!-- q: mcq id="bd570b74" -->
   Which control mainly protects integrity?

   - [ ] A second copy of the server in another city.
   - [x] Digital signatures that detect any change to a message.
   - [ ] Encrypting data so it can't be read.
   - [ ] More bandwidth for busy periods.

   <details><summary>Answer</summary>

   A signature detects tampering, which is integrity. The second server and extra bandwidth protect availability, and encryption mainly protects confidentiality.

   </details>

6. <!-- q: open id="03a97ca8" -->
   A food-ordering app's owner says: "We don't store card numbers, so we have nothing to protect." Using all three parts of the triad, explain why they're wrong.

   <details><summary>Answer</summary>

   Confidentiality: they still hold customers' names, phone numbers and addresses, plus staff passwords and API keys. Integrity: attackers could change prices, mark unpaid orders as paid, or alter the menu, which costs money directly. Availability: if the app goes down at a busy time, the business loses its sales. Not storing card numbers removes one asset; it doesn't remove the need for security.

   </details>

## Practice — the triad for your own app
<!-- bite: 58ee06f2-ea35-4bdd-8a95-df4281610593 -->

**Task.** For an app you use or have built, write three short lists.

1. **C:** the three most sensitive pieces of data it holds, and who should be able to see each.
2. **I:** the three pieces of data whose *change* would hurt most, and who should be able to change each.
3. **A:** the busiest time it must be up, and what happens to its owner if it's down then.
4. For each list, name the one protection you'd add first.

## Practice: when your lists are done
<!-- bite: 3264a10c-c1f1-4664-be13-92aaf75e008d -->

Here is how you know the task is finished.

**Done when:** each list has three items and one first protection, and you've written one sentence on where two of your protections pull against each other.

## Before moving on
<!-- bite: 806b51d4-7079-4281-9ac8-338ae18060f0 -->

You can now define confidentiality, integrity and availability, classify an incident by which it hits, name the main protections for each, and explain how they trade off.

**Recap for later lookup:** C = only the right people see it (access control, encryption, least privilege). I = it stays correct (access control, hashes and signatures, audit logs). A = it works when needed (tested backups, redundancy, capacity). Ransomware hits A and usually C. Integrity failures are quiet; availability is the one people forget. Balance the three for each system.

Next: [[cybersecurity/01-fundamentals/03-attacker-and-hacker-types|attacker and hacker types]], the people on the other side of all three.

## Related
<!-- bite: 03ba006a-e76d-447c-9be4-0a626f56c785 -->

- [[cybersecurity/05-cryptography/01-what-is-cryptography|What is cryptography]] — the tools behind C and I.
- [[cybersecurity/07-security-operations/04-incident-response|Incident response]] — what to do when one of the three actually fails.
- [[cybersecurity/10-protecting-yourself/index|Protecting yourself]] — the triad for your own phone and accounts.

## About this lesson
<!-- bite: e36010d6-eadb-45d1-ae70-2bdc49199b54 -->

**Level:** Beginner. **Covers:** confidentiality, integrity and availability with examples of each failing, the main protections for each, authenticity and non-repudiation, how the three trade off, and classifying six incidents on Mama Put. **Where it sits:** lesson 2 of the [[cybersecurity/01-fundamentals/index|Fundamentals]] section. **Sources:** the original vault note, rebuilt around the Mama Put running example.
