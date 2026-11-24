---
id: c859b3e0-e107-4ef7-8235-0392ea9df044
---

# Threat Modelling

**Threat modelling is planning ahead for what could go wrong with a system, by answering four questions about it, so you know what to protect first.**

## Before you start
<!-- bite: befdb4ad-9397-4122-a5c4-b5172c3e032c -->

You should have:

- Ranked risks by likelihood × impact → [[cybersecurity/01-fundamentals/01-what-is-cybersecurity|what is cybersecurity]].
- Listed a system's realistic attackers → [[cybersecurity/01-fundamentals/03-attacker-and-hacker-types|attacker types]].
- Met the security principles → [[cybersecurity/01-fundamentals/04-security-principles|security principles]].

After this lesson you will be able to:

1. Run the four questions of threat modelling on a real system.
2. Draw a data-flow diagram and mark its trust boundaries.
3. Use STRIDE to list threats systematically, at each flow and boundary.
4. Choose a response for each threat (mitigate, eliminate, transfer, accept) and rank them.

**Study route.** Kid version and §1–4, then the worked example: a full threat model of Mama Put's order flow. Keep paper handy; you'll draw.

## What threat modelling is
<!-- bite: cd7490d4-f99b-43fa-9950-627b3174a0e0 -->

Every lesson so far gave you a piece: risk scoring (01), the three things to protect (02), who attacks (03), and the principles that guide defences (04). Threat modelling puts the pieces together into a plan for one specific system.

Without it, security is guesswork: you defend against whatever you read about last. With it, you get a short, ranked list of the threats that matter for *your* system, each with a decision about what to do. And it's cheapest at the very start: a threat found on a whiteboard costs a conversation; the same threat found after launch costs an incident.

## The kid version
<!-- bite: 5dfc7515-3530-46ac-99d8-44f835d6331a -->

Before a school trip to the beach, a good teacher sits down and thinks. What are we doing? (Taking 30 children to the sea.) What could go wrong? (Someone gets lost, someone swims too far, someone gets sunburnt.) What will we do about each? (Buddy pairs, a swimming line, sunscreen.) Did our plan work? (Count everyone on the bus home.)

That's threat modelling: the same four questions, asked about a computer system.

**Where the analogy stops working.** The teacher can picture the beach. A software system is mostly invisible: data moving between programs and machines you can't see. So the first job in threat modelling is literally drawing it, so there's something to look at and point to.

## 1. The four questions
<!-- bite: 5b47d424-3745-4a16-a8a7-fdcec9277445 -->

The whole method, from Adam Shostack's work on threat modelling, is four questions. You can run them on a whiteboard in half an hour.

1. **What are we building?** Draw the system: who uses it, the programs, where data is stored, and how data flows between them.
2. **What can go wrong?** List the threats, using a checklist like STRIDE (§3) so you don't rely on imagination.
3. **What are we going to do about it?** For each threat, decide: fix it, remove it, hand it off, or accept it (§4).
4. **Did we do a good job?** Check the fixes really work (that's what testing and penetration testing are for), and revisit when the system changes.

A threat model is a living document. Every new feature adds new flows, and new flows bring new threats.

## 2. Drawing the system — data flows and trust boundaries
<!-- bite: 23713733-f83a-4cda-96c5-55b1f3b8b506 -->

The usual drawing is a **data-flow diagram**: people and outside systems, the processes that handle data, the places data is stored, and arrows for the data moving between them.

The most important thing on it is the **trust boundary**: a line where data crosses from something you trust less to something you trust more, like from a customer's phone to your server, or from your server into the database. **Attacks happen at trust boundaries**, because that's where data from someone else arrives.

## 2. Drawing the system: Mama Put's order flow
<!-- bite: e9e26944-ec3a-4a48-805a-9915531409ed -->

Here is Mama Put's order flow, drawn this way.

![A data-flow diagram of Mama Put: the customer places an order with the API, the API saves it to the database and charges the card through a payment provider, the provider sends a paid webhook back, and the API confirms to the customer; dashed red boxes mark the trust boundaries around the server and the database.](../images/fu-mama-put-dfd.svg)

Every arrow that crosses a dashed red line is a place to look hard: flow 1 (the customer's order), flow 3 and flow 4 (to and from Paystack), and flow 2 (into the database).

## 3. STRIDE — a checklist for "what can go wrong?"
<!-- bite: f261dcd4-f215-4809-bccf-d83c54d367ca -->

**STRIDE** is the most common checklist. Each letter is one kind of threat, and each one breaks one security goal you've already met:

| Letter | Threat | What it breaks | A Mama Put example |
|---|---|---|---|
| **S** | Spoofing | Authentication | Pretending to be a customer, a staff member or Paystack |
| **T** | Tampering | Integrity | Changing an order's price on its way to the server |
| **R** | Repudiation | Non-repudiation | A staff member denies issuing a refund, and there's no log |
| **I** | Information disclosure | Confidentiality | Customer addresses leaking |
| **D** | Denial of service | Availability | Flooding the app at lunchtime |
| **E** | Elevation of privilege | Authorization | A customer reaching the admin dashboard |

Run STRIDE against **each flow that crosses a trust boundary**: for flow 1, can it be spoofed? Tampered with? Denied? Can it leak? Can it be used to gain more access? Asking all six for each flow is what makes the list thorough instead of whatever you happened to think of.

## 4. Deciding what to do, and in what order
<!-- bite: 90a11f1f-853c-4a47-8646-6ca54fcf85b3 -->

For each threat, choose one of four responses:

1. **Mitigate** — add a control that reduces it. The usual choice, guided by the principles in lesson 04.
2. **Eliminate** — remove the feature or data that creates it. Don't store card numbers, and they can't leak.
3. **Transfer** — hand the risk to someone better placed, like letting Paystack handle card details, or buying insurance.
4. **Accept** — decide to live with it, in writing, because fixing it costs more than the risk.

Then rank by **likelihood × impact**, from lesson 01. You'll always have more threats than time. A threat that's easy, likely and costly gets fixed now; a hard, unlikely, cheap one gets accepted. And write down what you accept: an accepted risk is a decision, but an unnoticed one is a surprise.

## Terms used in this lesson
<!-- bite: 762193ab-495d-4bb2-a789-be424a06c386 -->

1. **Threat model**: This is the written result of threat modelling: the system drawing, the threats, and what you decided for each.
2. **Data-flow diagram**: This is a drawing of a system's people, processes, data stores and the data moving between them.
3. **Trust boundary**: This is a line where data crosses from a less-trusted part of a system to a more-trusted one. Attacks concentrate there.
4. **STRIDE**: This is a checklist of six threat kinds: spoofing, tampering, repudiation, information disclosure, denial of service and elevation of privilege.

## Terms used in this lesson: responses and tools
<!-- bite: 18ed1275-3f54-488b-9329-1710c90ce5ab -->

The rest of the terms name the responses to a threat and one other tool.

5. **Mitigate**: This means adding a control that reduces a threat's likelihood or impact.
6. **Accept**: This means deciding, in writing, to live with a threat because fixing it costs more than the risk.
7. **Attack tree**: This is a drawing with an attacker's goal at the top ("get free food") and the ways to reach it branching below. It's good for thinking through one high-value goal.
8. **Spoofing**: This is pretending to be someone or something else, like sending a message that claims to come from Paystack.

## Worked example — threat-model Mama Put's order flow
<!-- bite: 1c0c3f1c-3ae3-4d86-9bab-1ddc06ddc7ad -->

Take the diagram from §2 and run STRIDE across the flows that cross a trust boundary. **Predict first:** of all the threats, which one would cost Mama Put the most money, most easily?

**Flow 4, the "paid" webhook from the payment provider, under S for spoofing.** The API marks an order paid when it receives a message saying so. If it doesn't check that the message really came from Paystack, anyone who knows the address can send `{"order": 42, "status": "paid"}` and get their food free, as many times as they like.

That's the top threat: easy to do, directly costly, and invisible until the takings don't add up.

## Worked example: the rest of the model
<!-- bite: f17b82ad-aadd-4dc7-91b0-96174c63a790 -->

Here are the most important threats from the other flows, each with a response:

1. **Flow 4, spoofed webhook** → *mitigate*: verify the webhook's HMAC signature with the shared secret, and re-check the payment with Paystack's API ([[cybersecurity/05-cryptography/03-hashing-and-integrity|hashing and integrity]]).
2. **Flow 1, tampered price** → *mitigate*: the server works out the price from the menu itself; it never trusts a price the phone sends.
3. **Flow 1, elevation of privilege** (a customer changes `/orders/41` to `/orders/42`) → *mitigate*: check on every request that the order belongs to the logged-in customer.
## Worked example: data, cards and floods
<!-- bite: 6b080991-fd18-4ce9-be9f-909f8164a29a -->

The last three threats are about stored data, card details and lunchtime traffic.

4. **Flow 2, information disclosure** (a database leak) → *mitigate and eliminate*: least-privilege database accounts, and don't store anything the business doesn't need.
5. **Card details** → *transfer*: card numbers never touch Mama Put's server; Paystack handles them.
6. **Denial of service at lunchtime** → *mitigate partly, accept the rest*: rate limiting and a cheap hosting plan that can scale; accept that a large, determined flood could still take her down for an afternoon.

Ranked by likelihood × impact, 1, 2 and 3 are fixed first. Each one is a few lines of code, and together they close the cheapest ways to steal from her.

## Keeping it practical
<!-- bite: 8348f51b-18c0-4db9-9d1a-a8793b2aeaac -->

Threat modelling has a reputation for being heavy: formal diagrams and long meetings. That reputation is why people skip it. Keep it light:

1. **Do it often and small.** Thirty minutes at a whiteboard for each new feature beats a 40-page document once a year.
2. **Start at the trust boundaries.** That's where the threats are.
3. **Use the four questions even informally.** "What could go wrong here, and what would we do?" asked on every design catches most of the value.
4. **Write down what you accept.** It turns a surprise into a decision.

## Common pitfalls and traps
<!-- bite: 017828a8-d891-4481-8417-4924c8c114d6 -->

1. **Starting with tools instead of the system.** Draw what you're building first; you can't defend what you haven't mapped.
2. **Skipping trust boundaries.** A diagram without them hides exactly where the attacks will land.
3. **Relying on imagination.** Run all six STRIDE letters on every boundary-crossing flow.
4. **Treating it as a one-off.** New features mean new flows and new threats. Update it.
5. **Forgetting to rank.** An unranked list of fifty threats doesn't tell anyone what to do on Monday.

## Check your understanding
<!-- bite: 157c7f0f-7551-43a4-b6dd-c1ed23793c59 -->

Try each one before you open the answer.

1. <!-- q: mcq id="d7406762" -->
   In a data-flow diagram, where do attacks concentrate, and so where should you look hardest?

   - [ ] Inside the database.
   - [x] At trust boundaries, where data crosses from a less-trusted part of the system to a more-trusted one.
   - [ ] At the user's screen.
   - [ ] In the programming language the app is written in.

   <details><summary>Answer</summary>

   At trust boundaries. That's where data someone else controls enters your system, so that's where it must be checked. Flows that never cross a boundary carry data you already trust.

   </details>

2. <!-- q: mcq id="8e900eb9" -->
   A shopping app's server accepts the total price sent by the customer's phone and charges that amount. Which STRIDE letter is this threat?

   - [ ] S — Spoofing
   - [x] T — Tampering
   - [ ] R — Repudiation
   - [ ] D — Denial of service

   <details><summary>Answer</summary>

   Tampering: the customer can change the price on its way to the server. The fix is for the server to calculate the price itself from its own menu.

   </details>

3. <!-- q: gap id="2cba1c06" answers="repudiation" -->
   A staff member issues a large refund to a friend, and later says they never did it. There's no record of who issued it. In STRIDE, this threat is called ___.

   <details><summary>Answer</summary>

   Repudiation: someone can deny an action because there's no proof. Logging who did what, ideally where staff can't edit the log, is the fix.

   </details>

4. <!-- q: mcq id="34c89793" -->
   A small charity stops collecting donors' dates of birth, because it never used them. Which response to the threat of leaking them is this?

   - [ ] Mitigate
   - [x] Eliminate
   - [ ] Transfer
   - [ ] Accept

   <details><summary>Answer</summary>

   Eliminate: removing the data removes the threat entirely. Data you never store can't leak. It's the attack-surface principle from lesson 04.

   </details>

5. <!-- q: mcq id="c5b83818" -->
   An online shop lets a payment company handle all card details, so card numbers never reach the shop's own server. Which response is this?

   - [ ] Mitigate
   - [ ] Eliminate
   - [x] Transfer
   - [ ] Accept

   <details><summary>Answer</summary>

   Transfer: the risk of holding card data is handed to a company built to carry it. (You could also argue it eliminates the data from the shop's side; the key idea is that someone better placed now carries that risk.)

   </details>

6. <!-- q: open id="4755c2f4" -->
   An app marks orders as paid whenever its webhook endpoint receives `{"order": N, "status": "paid"}`. Explain the threat using STRIDE, why it ranks highly, and how to fix it.

   <details><summary>Answer</summary>

   It's spoofing (S): anyone who learns the endpoint's address can pretend to be the payment provider and mark any order paid, getting goods for free, as often as they like. It ranks highly because it's easy (one HTTP request), directly costly, and hard to notice. The fix is to verify every webhook's HMAC signature with the secret shared with the provider, compare in constant time, reject old messages, and, for extra safety, confirm the payment with the provider's API before marking the order paid.

   </details>

## Practice — threat-model your own app
<!-- bite: 4f66884b-6d96-40d3-8427-8794ef031795 -->

**Task.** Run the four questions on the app you used in this section's earlier practice tasks. Give it 30 to 45 minutes.

1. **What are we building?** Draw its data-flow diagram, and mark every trust boundary.
2. **What can go wrong?** For each flow that crosses a boundary, try all six STRIDE letters. Aim for at least eight threats.
3. **What will we do?** Give each threat a response, and score it by likelihood × impact.
4. **Did we do a good job?** Pick the top threat, fix it, and write how you'd test that the fix works.

## Practice: when your threat model is done
<!-- bite: a68decff-6de3-4898-9b64-22dc2dfdb195 -->

Here is how you know the task is finished.

**Done when:** you have a diagram with trust boundaries, a ranked list of at least eight threats each with a response, at least one written "accept" with a reason, and the top threat fixed. Keep it in the project's repository; it's a living document.

## Before moving on
<!-- bite: 3ddc472a-fe03-43d0-990a-c37dcb0676b8 -->

You can now run the four questions on a system, draw a data-flow diagram with trust boundaries, list threats with STRIDE, choose and rank responses, and keep threat modelling light enough to actually do.

**Recap for later lookup:** four questions: what are we building, what can go wrong, what will we do, did we do a good job. Draw data flows; mark trust boundaries; attacks happen there. STRIDE = spoofing, tampering, repudiation, information disclosure, denial of service, elevation of privilege. Respond: mitigate, eliminate, transfer, accept (in writing). Rank by likelihood × impact. Small and often.

**The section, in one line:** lesson 01 gave you the words, 02 what to protect, 03 who attacks, 04 how to reason about defences, and 05 how to turn all four into a plan for a real system.

Next: [[cybersecurity/02-ethical-hacking/index|ethical hacking]], where you test a system the way an attacker would, starting with the rules that keep it legal.

## Related
<!-- bite: 64cb3a2d-1647-41e2-a443-7f128b0c576f -->

- [[cybersecurity/08-governance-risk-and-compliance/01-risk-and-frameworks|Risk and frameworks]] — ranking and treating risk at the organisation level.
- [[cybersecurity/02-ethical-hacking/02-penetration-testing-methodology|Penetration testing methodology]] — question 4, "did we do a good job?", done by attacking.
- [[architecture/index|Architecture]] — drawing systems, the first step of every threat model.

## About this lesson
<!-- bite: b232271c-f54f-4770-96a0-247a3df896de -->

**Level:** Intermediate. **Covers:** Shostack's four questions, data-flow diagrams and trust boundaries, STRIDE, attack trees, the four responses (mitigate, eliminate, transfer, accept), ranking by likelihood × impact, and a full threat model of Mama Put's order flow, led by the spoofed payment webhook. **Where it sits:** lesson 5 of the [[cybersecurity/01-fundamentals/index|Fundamentals]] section, the bridge to the rest of the course. **Sources:** Adam Shostack's four-question framework and STRIDE, rebuilt from the original vault note around the Mama Put running example.
