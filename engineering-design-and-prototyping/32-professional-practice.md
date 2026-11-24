---
id: 38f819ed-6a93-4794-9e6e-cffde4d90971
---

# Professional Practice

Professional practice is how an engineer works responsibly with others: protecting the public, protecting ideas, managing the project, and keeping a record of every decision.

## Before you start
<!-- bite: 9ea02511-e6e4-4b3e-8f69-2e608a583f1e -->

You should know codes of ethics and standards ([[engineering-design-and-prototyping/19-considerations-of-good-design-3|19 — Considerations of Good Design 3]]).

After this lesson you will be able to:

1. state an engineer's main professional duties and the role of registration;
2. tell patents, registered designs, trademarks, copyright and trade secrets apart;
3. describe design reviews, a design log and revision control.

## What professional practice is
<!-- bite: 3fd12be2-5fb5-4391-924f-15272ed9c28a -->

Everything up to now has been about designing the product. Professional practice is about how the engineer behaves while doing it. A brilliant design can still cause harm, be copied, run months late, or become impossible to fix because nobody recorded why it was made that way. This lesson covers the duties, the protection of ideas, the running of a team, and the records. Lesson 33 then covers how engineers communicate.

## The engineer's duties
<!-- bite: 8b3f391f-a5a4-4259-a5c7-5014aedb7ec8 -->

Codes of ethics (lesson 19) agree on the core duties:

1. **Public safety first:** hold the safety, health and welfare of the public above the client's or employer's wishes.
2. **Competence:** only take on work you are qualified for, and keep learning (**continuing professional development**).
3. **Honesty:** report results truthfully, including failures, and never sign off a design you haven't checked.
4. **Confidentiality:** protect the client's and employer's information.
5. **Avoid conflicts of interest,** or declare them.

In Nigeria, the **Council for the Regulation of Engineering in Nigeria (COREN)** registers engineers and can discipline them, and the **Nigerian Society of Engineers (NSE)** is the professional body. Registration is what allows an engineer to take legal responsibility for designs such as buildings and bridges. Engineers can also be held liable when a product they designed injures someone through a design fault: **product liability**.

## Protecting ideas: intellectual property
<!-- bite: eb1dcb3b-bee7-4055-a12c-d0e64d91a061 -->

**Intellectual property (IP)** is legal ownership of ideas and creative work.

| Protection | Protects | Example | How long, roughly |
| --- | --- | --- | --- |
| Patent | A new, inventive, useful invention: how something works | A new folding mechanism for a desk | 20 years, then anyone may use it |
| Registered design | How a product looks: its shape and pattern | The outline of a bottle | Up to about 25 years, renewed |
| Trademark | A name or logo that identifies a brand | A company's logo | As long as it is renewed and used |
| Copyright | Written and drawn work, including software and drawings | A product's manual or code | The author's life plus decades |
| Trade secret | Information kept secret | A recipe or a process setting | As long as it stays secret |

Two practical habits:

1. **Search prior art** before investing in a design: an existing patent may already cover it, and a patent is only granted for something new.
2. **Use a non-disclosure agreement (NDA)** before showing an unprotected idea to a supplier or partner. Showing an invention publicly before applying can stop it being patented.

## Running the project
<!-- bite: 35538fe8-95ab-439f-bde9-a7484753a501 -->

1. **Teams and roles:** agree who does what: team lead, designers for each subsystem, the person responsible for testing, the person who keeps the records.
2. **Plan:** break the work into tasks with durations and dependencies, and show it on a **Gantt chart** with **milestones**.
3. **Design reviews:** formal checkpoints where the design is examined by people outside the team before moving on. A **concept review** after selection, a **preliminary design review (PDR)** once the architecture is set, and a **critical design review (CDR)** before building, when the detailed design must be complete.
4. **Meetings:** short, with an agenda, and **minutes** recording decisions and actions, each with a name and a date.

## Keeping records
<!-- bite: ba313cf6-5245-476a-a4a0-2d61edd46184 -->

1. **Design log or engineering notebook:** a dated record of ideas, calculations, test results and decisions, including the ones that didn't work. It shows how the design developed, helps prove when an invention was made, and lets someone else pick up the work.
2. **Revision control:** every drawing and model has a revision letter or number (A, B, C). Only the current revision is used for making parts, and old ones are marked superseded.
3. **Engineering change notice (ECN):** a formal record of each change after a design is released: what changed, why, and who approved it. It is the paperwork side of change control (lesson 07).
4. **Bill of materials (BOM):** the list of every part, with numbers and quantities.

## Common pitfalls
<!-- bite: c7590c32-3f44-47de-9409-f9b1492f889d -->

1. **Putting the client ahead of public safety.** The public comes first, always.
2. **Showing an invention before protecting it.** Use an NDA, or apply first.
3. **Decisions with no record.** Six months later nobody knows why the design is the way it is.
4. **Several "latest" versions of a drawing.** Use revision control so the factory builds the right one.

Professional practice keeps the work responsible and recorded. Next lesson covers getting it across to other people: reports, drawings and presentations.

## Check your understanding
<!-- bite: 41e1c5cc-096e-49a7-ac1e-c74ffa490d13 -->

Try each one before you open the answer.

1. <!-- q: mcq id="f1eae83a" -->
   A client asks an engineer to approve a balcony design to save money, though the engineer's calculations show it is unsafe. What should the engineer do?

   - [ ] Approve it, since the client is paying
   - [x] Refuse, and explain the safety problem, because public safety comes first
   - [ ] Approve it but add a warning sign
   - [ ] Stay silent and let someone else decide

   <details><summary>Answer</summary>

   Refuse and explain. Every code of ethics puts the safety of the public above the client's wishes.

   </details>

2. <!-- q: mcq id="203349dc" -->
   A company invents a new mechanism that lets a desk fold flat in one movement. Which protection fits how it works?

   - [x] A patent
   - [ ] A trademark
   - [ ] A registered design
   - [ ] Copyright

   <details><summary>Answer</summary>

   A patent protects how an invention works. A registered design would protect only its appearance.

   </details>

3. <!-- q: gap id="8c948a08" answers="PDR|preliminary design review;CDR|critical design review" -->
   The design review held once the architecture is set is the ___, and the review held before building, when the detailed design should be complete, is the ___.

   <details><summary>Answer</summary>

   The preliminary design review (PDR), then the critical design review (CDR).

   </details>

4. <!-- q: open id="8b367074" -->
   A student team wants to show its new invention to a manufacturer to get a quote, before applying for a patent. What should it do first, and why?

   <details><summary>Answer</summary>

   Have the manufacturer sign a non-disclosure agreement. Showing an unprotected invention can let someone copy it, and a public disclosure before applying can stop it being patented because it would no longer be new. Searching prior art first is also wise.

   </details>

5. <!-- q: open id="27ea07ce" -->
   Give three things an engineering notebook or design log should contain, and two reasons for keeping one.

   <details><summary>Answer</summary>

   Contents, any three: dated ideas and sketches, calculations, test results, decisions and the reasons for them, failed ideas. Reasons, any two: it shows how the design developed; it lets someone else continue the work; it can help prove when an invention was made; it explains later why the design is the way it is.

   </details>

6. <!-- q: mcq id="0d1e2cf0" -->
   The factory made 500 brackets from revision B of a drawing, though revision C had changed a hole size. What practice failed?

   - [ ] Intellectual property
   - [x] Revision control
   - [ ] Continuing professional development
   - [ ] The power-interest grid

   <details><summary>Answer</summary>

   Revision control: only the current revision should be released for production, with older ones marked superseded.

   </details>

## Before moving on
<!-- bite: 9d95e4b1-d3c4-4340-b6db-00dfdf420242 -->

You can state an engineer's duties, choose the right IP protection, run reviews and keep proper records. **Next:** [[engineering-design-and-prototyping/33-technical-communication|33 — Technical Communication]]: reports, figures and presentations that the right reader can act on.

## Related
<!-- bite: be888be3-e650-4022-b6d5-4359f7da5e54 -->

- [[engineering-design-and-prototyping/index|Engineering design and prototyping map]]

## About this lesson
<!-- bite: fa29166f-772b-4a7f-8317-ffbd44ce2e54 -->

**Level:** Beginner. **Covers:** professional duties, COREN, NSE and product liability, the kinds of intellectual property, prior art and NDAs, teams, plans, design reviews and minutes, and design logs, revision control, ECNs and the BOM.

**Where it sits:** lesson 32 of 36, in part 9 (making it and working as a professional).

**Source:** written from general engineering practice, because the SSG 532 lecture notes cover codes of ethics but not wider professional practice; it is on the official course outline. The IP durations are rough and vary by country; check Nigerian law for exact terms.
