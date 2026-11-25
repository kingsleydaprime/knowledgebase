---
id: da9e2c7c-b046-45f2-bf63-adad1e82d3f5
---

# Social Engineering

**Social engineering is tricking a person into giving away access, money or information, instead of breaking the technology.**

## Before you start
<!-- bite: c3f6c688-74c9-48f0-b167-76fc9ffa2050 -->

You should have:

- Met attacker types and the CIA triad → [[cybersecurity/01-fundamentals/03-attacker-and-hacker-types|attacker types]].
- Met MFA and why passkeys resist phishing → [[cybersecurity/04-web-security/02-secure-authentication|secure authentication]].
- A terminal with `dig` (in the `bind-utils` package on Fedora).

After this lesson you will be able to:

1. Explain why social engineering works, using the pressures it relies on.
2. Name the main kinds: phishing and its variants, pretexting, business email compromise, baiting and tailgating.
3. Read an email's authentication results (SPF, DKIM, DMARC), and say why a lookalike domain passes all three.
4. Check your own domain's email protection, and set up the process checks that stop the costliest scams.

**Study route.** Kid version and §1–4, then the worked example: two scams aimed at Mama Put, taken apart line by line.

## What social engineering is
<!-- bite: 58955245-094b-49ac-94ec-6edba0184e3a -->

Every section of this course so far has defended technology: firewalls, encryption, safe code. Social engineering walks around all of it. Why break a password hash when you can text someone "your account will be suspended, confirm your PIN here" and have them type it in for you?

Most real breaches start this way, with one person fooled. "Your BVN needs updating" texts, fake bank calls, and "urgent, pay this supplier today" emails from a boss who never sent them are all social engineering. This lesson opens the section on how attacks actually happen, because this is how most of them start.

## The kid version
<!-- bite: e41f9e75-0451-41d3-a9bd-d6f941456fd6 -->

Imagine a stranger at your gate who says, "Your mum sent me to collect her purse, she needs it quickly, she's waiting in the car!" He sounds rushed and confident, he knows your mum's name, and you want to help. The gate is strong, but you just opened it yourself.

Social engineering is that trick, played with emails, texts and phone calls. The attacker doesn't break the lock; they get someone inside to open it.

**Where the analogy stops working.** A stranger at the gate can only try one house at a time. A phishing email can go to a million people at once for almost nothing, so even if only one in a thousand falls for it, the attacker wins a thousand times. That's why you can't rely on everyone being careful; some people always click.

## 1. Why it works — the pressures
<!-- bite: 5c35ab1e-6116-4192-b291-e70c6269ca40 -->

Social engineering doesn't exploit a bug in software. It exploits normal, decent human habits, and you can't patch those. Almost every scam leans on one or more of these pressures:

1. **Urgency** — "act now or your account is closed". Rushing stops people thinking.
2. **Authority** — "this is your bank", "this is the CEO", "this is IT". People obey people in charge.
3. **Fear** — "suspicious login detected", "you'll be fined". Fear rushes people too.
4. **Helpfulness** — "I'm locked out, can you just read me the code?". Kind people want to help.
5. **Greed or curiosity** — "you've won", "see who viewed your profile", a USB stick labelled "Salaries 2026".

Remember this one: **when a message makes you feel rushed or scared, that feeling is the attack.** Slow down and check through a different channel.

## 2. The phishing family
<!-- bite: d0566fc6-cc7e-4bf7-9abc-db8bc898734e -->

**Phishing** is a fake message pretending to be from someone you trust, to steal a password, plant malware, or get a payment. It's named by how it's sent and who it targets:

1. **Phishing** — mass emails to anyone.
2. **Spear phishing** — targeted at one person, using details researched about them.
3. **Whaling** — spear phishing aimed at a boss or executive.
4. **Smishing** — phishing by SMS, like the "BVN update" and "parcel delivery fee" texts.
5. **Vishing** — phishing by voice call, often a fake bank or "customer care" agent asking for an OTP.

The goal is nearly always one of three things: get you to **type a secret** into a fake page, **open a file** that installs malware, or **send money**.

## 3. Scams without a link — BEC, pretexting and physical tricks
<!-- bite: d574adbf-3239-49f8-86ba-626176893de9 -->

Some of the most expensive scams contain no link and no malware at all.

1. **Business email compromise (BEC)** — an email "from the owner" or "from a supplier" asking to pay an invoice or change bank details. No malware, just a believable request. It's among the costliest kinds of cybercrime worldwide.
2. **Pretexting** — inventing a story and an identity to extract information: "Hi, I'm from the bank's fraud team, I need to verify your card."
3. **Baiting** — leaving an infected USB stick where someone curious will plug it in.
4. **Tailgating** — following someone through a door that needs a key card.
5. **Shoulder surfing** — reading a PIN or password over someone's shoulder.

Because there's nothing technical to scan for, the defence against these is mostly **process**: rules like "every change to a supplier's bank details is confirmed by phone, on the number we already have".

## Terms used in this lesson
<!-- bite: 735eb722-a1f9-4551-abf8-f3d1ede24cf6 -->

1. **Social engineering**: This is manipulating people, rather than technology, to get access, money or information.
2. **Phishing**: This is a fake message pretending to come from someone trusted. **Smishing** is by SMS and **vishing** is by voice call.
3. **Spear phishing**: This is phishing aimed at one person, using details about them to look genuine.
4. **BEC (business email compromise)**: The letters stand for those words. It's an email that impersonates a boss or supplier to get a payment made or bank details changed.

## Terms used in this lesson: email's ID checks
<!-- bite: d9e3f375-0398-4512-9d37-4bef9ea6b3b5 -->

The rest of the terms are the three checks that tell an email server whether a message really came from the domain it claims.

5. **SPF (Sender Policy Framework)**: The letters stand for those words. It's a DNS record listing which servers may send email for a domain.
6. **DKIM (DomainKeys Identified Mail)**: The letters stand for those words. It's a digital signature on each email, made with the sending domain's private key.
7. **DMARC (Domain-based Message Authentication, Reporting and Conformance)**: The letters stand for those words. It's a DNS record telling receivers what to do with mail that fails SPF and DKIM for that domain: nothing, spam folder, or reject.
8. **Lookalike domain**: This is a domain that resembles a real one, like `mamaput-ng.com` for `mamaput.ng`, registered by an attacker.

## 4. What email checks can and can't stop
<!-- bite: b0152e6d-c966-4f67-9a3a-99610eac0b1a -->

Email was designed in the 1970s with no proof of who sent a message; anyone can type any "From" address. SPF, DKIM and DMARC were added later to fix that, and together they let a receiving server check: **did this really come from the domain in the From line?**

If Mama Put publishes a strict DMARC record for `mamaput.ng`, an attacker *cannot* send convincing email from `owner@mamaput.ng`: it fails the checks and is rejected. That's a big win, and it's why every domain should have one.

But notice what it doesn't cover. An attacker who registers `mamaput-ng.com` controls that domain, so their email passes SPF, DKIM and DMARC perfectly, **for their own domain**. The checks prove the email came from `mamaput-ng.com`; they can't tell you that's not who you meant. So email checks stop exact spoofing, and people and processes have to catch the lookalikes.

## Worked example — two scams aimed at Mama Put
<!-- bite: ca421647-b629-47c4-a503-e87260e4a192 -->

**Scam 1, a text to Mama Put's phone:**

```text
From: PAY-ALERT
Your merchant account has been SUSPENDED due to unusual activity.
Verify within 2 hours to avoid losing today's settlements:
https://paystack-merchant-verify.com.ng/login
```

**Predict first:** list every warning sign before reading on.

Urgency ("2 hours", "losing today's settlements"), fear ("SUSPENDED"), authority (it claims to be her payment provider), and a link to a domain that isn't the provider's real one, made to look official. The page will look exactly like the real login, and anything she types goes to the attacker. MFA helps, but a fake page can also ask for the code; a passkey wouldn't work there at all.

**What to do:** never log in from a link in a message. Open the app or type the address you already know.

## Worked example: the boss who never sent it
<!-- bite: a814dedd-ecbe-4c15-8530-a88fed42b6c7 -->

**Scam 2, an email to Mama Put's bookkeeper, Ada.** Here are the important headers, the part most email apps hide (in Gmail: *Show original*):

```text
From: "Mama Put" <owner@mamaput-ng.com>
Reply-To: owner.mamaput@gmail.com
Subject: Urgent - supplier payment today
Authentication-Results: mx.example.net;
       spf=pass smtp.mailfrom=mamaput-ng.com;
       dkim=pass header.d=mamaput-ng.com;
       dmarc=pass header.from=mamaput-ng.com

Ada, pay the rice supplier's invoice today to their NEW account below.
I'm in a meeting, don't call, just do it. Will explain later.
```

**Predict first:** all three checks say `pass`. Is the email genuine?

## Worked example: reading the headers
<!-- bite: d448373a-2deb-45d6-8eda-e57856d3e040 -->

No. Read the domain, not the result. Every `pass` is for `mamaput-ng.com`, a lookalike the attacker registered. Mama Put's real domain is `mamaput.ng`. The checks honestly report that this email really came from the attacker's domain.

The other signs are all social: authority (the owner), urgency ("today"), a reason not to verify ("don't call"), a *new* bank account, and a `Reply-To` that sends Ada's answer to a Gmail address. That's textbook BEC.

**What stops it** is a process, not a tool: any new or changed bank details are confirmed by calling the supplier on the number already on file, and by checking with the owner in person or by phone. Thirty seconds of checking beats any filter here.

## Worked example: check your own domain
<!-- bite: 4c803179-0921-47c9-9a57-fe87e4f3ee98 -->

Now check whether a domain you own (or any domain you're curious about) protects itself against exact spoofing:

```bash
dig +short TXT mamaput.ng | grep spf          # the SPF record: who may send
dig +short TXT _dmarc.mamaput.ng              # the DMARC record: what to do with failures
```

A strong DMARC record looks like `v=DMARC1; p=reject; rua=mailto:dmarc@mamaput.ng`. `p=reject` tells receivers to refuse mail that fails; `p=none` only watches, and `rua` asks for daily reports so you can see who is sending as you. No `_dmarc` record at all means anyone can send mail as your exact domain. Put `mamaput.ng` aside and run it against your own domain, or a big company's, and compare.

## Common pitfalls and traps
<!-- bite: ba03640f-9daa-4314-85e6-cb4f4ed3ccae -->

1. **"Our staff are too smart to fall for it."** Targeted, well-timed phishing fools careful people. Design so that one person being fooled isn't a disaster: MFA, least privilege, payment checks.
2. **Trusting "pass" in the headers.** It means the email really came from *that* domain. Read which domain.
3. **No DMARC record.** Then anyone can send email as your exact domain. Publish one, start at `p=none`, and move to `p=reject`.
4. **Bank detail changes by email.** Always confirm on a known phone number. This one rule stops most BEC losses.
5. **Blaming the person who clicked.** People who are shamed stop reporting. Make reporting a suspicious message quick and thanked, because early reports stop attacks.

## Check your understanding
<!-- bite: 331cee8d-9947-42f2-8825-a9661efc27b0 -->

Try each one before you open the answer.

1. <!-- q: mcq id="655c5593" -->
   A text says: "Your bank account will be blocked in 1 hour. Confirm your BVN and OTP at bvn-update-ng.com." Which pressures does it use? Choose all that apply.

   - [x] Urgency
   - [x] Fear
   - [x] Authority
   - [ ] Greed

   <details><summary>Answer</summary>

   Urgency ("1 hour"), fear ("blocked") and authority (it claims to be the bank). No real bank asks for your OTP; an OTP is the second factor, and giving it away lets the attacker past MFA.

   </details>

2. <!-- q: mcq id="be4fda6a" -->
   An email claims to be from `ceo@acme.ng`. Its headers show `spf=fail dkim=none dmarc=fail`, and acme.ng publishes `p=reject`. What should the receiving server do?

   - [ ] Deliver it, because the From address is correct.
   - [x] Reject it, because it fails the checks and the domain's DMARC policy says to reject such mail.
   - [ ] Deliver it to the spam folder only if it contains a link.
   - [ ] Ask the CEO.

   <details><summary>Answer</summary>

   DMARC tells receivers what the real domain owner wants done with failing mail. With `p=reject`, the server refuses it, so exact spoofing of acme.ng doesn't reach the inbox.

   </details>

3. <!-- q: mcq id="e4aea66c" -->
   An email from `billing@acme-ng.co` shows `spf=pass dkim=pass dmarc=pass`. The real company uses `acme.ng`. What do the passes prove?

   - [ ] That the email is from the real company.
   - [x] Only that it really came from acme-ng.co, a different domain, which an attacker could own.
   - [ ] That it contains no malware.
   - [ ] That the company has approved it.

   <details><summary>Answer</summary>

   The checks prove the email came from the domain in its From line, here the lookalike. They say nothing about whether that's the domain you think it is. Lookalikes have to be caught by people and processes.

   </details>

4. <!-- q: gap id="f4902835" answers="p=reject|reject" -->
   For a domain's DMARC record to tell receiving servers to refuse email that fails the checks, its policy tag should be set to ___.

   <details><summary>Answer</summary>

   `p=reject`. `p=none` only monitors (useful at first, to see who's sending as you), and `p=quarantine` sends failures to spam.

   </details>

5. <!-- q: mcq id="3fb3638a" -->
   A bookkeeper gets an email from a long-time supplier saying their bank account has changed and asking for the next payment to go to the new one. What's the best response?

   - [ ] Pay, because the email came from the supplier's usual address.
   - [ ] Reply to the email asking if it's genuine.
   - [x] Call the supplier on the phone number already on file and confirm before changing anything.
   - [ ] Forward it to the boss and pay if they don't reply in an hour.

   <details><summary>Answer</summary>

   The supplier's email account may itself have been hacked, so even their real address isn't proof, and replying goes straight to the attacker. Confirming through a separate channel you already trust is what stops BEC.

   </details>

6. <!-- q: open id="7879e66e" -->
   Explain why "train everyone not to click" can't be the whole defence against phishing, and name three other layers that help.

   <details><summary>Answer</summary>

   Phishing goes to many people, it's often well crafted and well timed, and some people will always be busy, tired or fooled, so at least one click is likely. The defences have to assume it: phishing-resistant MFA (passkeys) so a stolen password or code isn't enough; email authentication (SPF, DKIM, DMARC at `p=reject`) to stop exact spoofing; least privilege so a phished account can do little; processes like phone confirmation of payment changes; monitoring for unusual logins after a phish; and a quick, blame-free way to report suspicious messages.

   </details>

## Practice — check a domain and build a phishing checklist
<!-- bite: 0eda4ded-0f2b-447e-ab31-541be196e2c1 -->

**Task.** Two short pieces.

1. Run the two `dig` commands against a domain you own, your school's or employer's domain, and one large company's. Record each one's SPF and DMARC policy.
2. Find a real phishing message in your own inbox or SMS (everyone has one). Without clicking anything, list every warning sign, and if it's an email, open *Show original* and read the authentication results and the domains.
3. Write a five-line checklist you'd give a small business's staff, including one process rule about payments.

## Practice: when your checks are done
<!-- bite: 94fd03fb-fcf8-41bc-bd30-1c186e6b9c4d -->

Here is how you know the task is finished.

**Done when:** you have three domains' SPF and DMARC policies recorded, one real phishing message annotated, and your five-line checklist. If your own domain has no DMARC record, add one at `p=none` with a report address.

## Before moving on
<!-- bite: ae7744b1-a6cd-4137-b07d-f2fd76a065a2 -->

You can now explain why social engineering works, name its main forms, read an email's SPF, DKIM and DMARC results and spot a lookalike that passes them, check a domain's email protection, and put process checks in place for the costliest scams.

**Recap for later lookup:** pressures: urgency, authority, fear, helpfulness, greed. Phishing, spear phishing, whaling, smishing, vishing; BEC, pretexting, baiting, tailgating. SPF (who may send), DKIM (signed), DMARC (what to do on failure; aim for `p=reject`). A pass proves the domain, not the intent; read the domain. Confirm payment changes on a known number. Assume someone will click.

Next: [[cybersecurity/06-attacks-and-threats/02-network-attacks|network attacks]], where the attacker goes after the traffic instead of the person.

## Related
<!-- bite: 01f1845e-e5e1-414f-8551-26b0643d1e44 -->

- [[cybersecurity/04-web-security/02-secure-authentication|Secure authentication]] — MFA and phishing-resistant passkeys.
- [[cybersecurity/10-protecting-yourself/index|Protecting yourself]] — spotting scams in your own life.
- [[cybersecurity/07-security-operations/02-logging-siem-and-detection|Logging, SIEM and detection]] — catching the unusual login after a successful phish.

## About this lesson
<!-- bite: a53f1ad8-766d-4efc-80d0-5b5e80ad4e7a -->

**Level:** Beginner. **Covers:** the pressures social engineering uses, the phishing family (spear phishing, whaling, smishing, vishing), BEC, pretexting, baiting and tailgating, SPF, DKIM and DMARC and their limits against lookalike domains, checking a domain's records with `dig`, and process defences, with two scams against Mama Put taken apart. **Where it sits:** lesson 1 of the [[cybersecurity/06-attacks-and-threats/index|Attacks and Threats]] section. **Sources:** the original vault note (from the roadmap.sh cyber-security roadmap), rebuilt around the Mama Put running example; the email headers are constructed for teaching, using a made-up domain.
