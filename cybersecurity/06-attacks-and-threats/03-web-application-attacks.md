---
id: f48e81bd-3fff-454a-862b-ea30ad84dff1
---

# Web Application Attacks

**A web application attack sends an app input, or requests, that make it do something it shouldn't, like show another user's data or run the attacker's code.**

## Before you start
<!-- bite: 7563f205-0487-438b-a705-5f48b86d8d54 -->

You should have:

- Run the login SQL injection and the basket IDOR on Juice Shop → [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|exploitation concepts]].
- Met the fixes: parameterised queries, output encoding, and authorization on every request → [[cybersecurity/04-web-security/index|web security]].

After this lesson you will be able to:

1. Say what the OWASP Top 10 is, and use it as a vocabulary and a checklist.
2. Name the main web attack classes: broken access control, injection, XSS, CSRF, SSRF and misconfiguration.
3. Reduce almost every web attack to one of two root causes.
4. Classify a real finding by its OWASP category, and run the list as a review of an app.

**Study route.** Kid version and §1–4, then the worked example: classify the Juice Shop bugs you already found, then use the list on your own app.

## What web application attacks are
<!-- bite: 8725905d-1fe8-4d0a-8f01-a199d8f19389 -->

The web-security section taught the *defences* one at a time. This lesson is the attacker's catalogue: the named classes of web attack, organised the way the industry organises them, so you can recognise one in a report, a bug bounty, or your own code review.

The organising tool is the **OWASP Top 10**: a list, updated every few years by the Open Worldwide Application Security Project, of the most serious kinds of web app weakness. It's the shared vocabulary of web security, and it's most useful as a *checklist*: run down it against any app and ask "could this one happen here?"

## The kid version
<!-- bite: fcb34a6d-b186-4028-8c5b-3b5099c5a4f4 -->

Think of a shop with a self-service till. Most attacks on it are one of a few tricks. Scanning a cheap barcode stuck over an expensive item (making the machine believe a lie you typed in). Walking into the "staff only" stockroom because the door was unlocked (going where you're not allowed). Or finding the till still logged in as the manager (using access that was left lying around).

Web attacks are the same handful of tricks, in different costumes. The OWASP Top 10 is the shop's list of "the ten ways people rob us", so staff know what to watch for.

**Where the analogy stops working.** A shop has a few tills in one building. A web app has thousands of "tills": every form, every URL, every API endpoint. So a single oversight, one endpoint that forgot to check who's asking, is enough, and attackers try them all automatically. The list tells you the *kinds* of oversight; finding every instance is the work.

## 1. The OWASP Top 10 (2025)
<!-- bite: 57d6962b-4f05-423a-b092-32aa91577403 -->

Here's the current list. Don't memorise the numbers (they shift each edition); learn the categories and what each means.

1. **A01 Broken Access Control** — users doing things they shouldn't be allowed to: reading another user's order by changing an ID, reaching admin pages without being admin. Still number one. Now includes **SSRF** (§3).
2. **A02 Security Misconfiguration** — default passwords, verbose error pages, debug endpoints left on, missing security headers. The commonest issue in the wild.
3. **A03 Software Supply Chain Failures** — weaknesses in the libraries, build tools and dependencies you pull in, not code you wrote (the Log4Shell kind of problem). New and rising.
4. **A04 Cryptographic Failures** — sensitive data unprotected: no HTTPS, plaintext or fast-hashed passwords, weak algorithms.
5. **A05 Injection** — untrusted input treated as code: SQL injection, command injection, and cross-site scripting (XSS).

## 1. The OWASP Top 10: the lower half
<!-- bite: 802743f8-6e72-46ed-a9b3-492e57acdb57 -->

The bottom five round out the list.

The rest sit lower but matter: **Insecure Design** (flaws in the plan, not the code), **Authentication Failures** (weak logins, poor sessions), **Software and Data Integrity Failures** (trusting unverified updates or data), **Logging and Alerting Failures** (not noticing the breach), and **Mishandling of Exceptional Conditions** (errors handled in a way that leaks or fails open). The official list at owasp.org is the authority on exact wording and order.

## 2. Broken access control — the number one
<!-- bite: 7c25b7f7-da50-45ad-9e24-d3135e09a7b0 -->

**Broken access control** is the app failing to enforce who may do or see what. It tops the list because it's common, easy to exploit, and high impact.

The everyday form is **IDOR** (insecure direct object reference), which you already did: change `/orders/41` to `/orders/42` and see someone else's order, because the app checked you were logged *in* but not that order 42 was *yours*. In API terms this is **BOLA** (broken object level authorization), the top API risk.

The other form is **privilege escalation**: reaching an admin function without being an admin, because the app hid the admin link but didn't actually check the role on the request.

The fix is one rule, applied everywhere: **check authorization on the server, on every request, against the logged-in user** (the complete-mediation principle from fundamentals). Hiding a button is not access control.

## 3. Injection, XSS and SSRF — input in the wrong place
<!-- bite: 53d3905c-06a3-4f4d-bace-0eafef313a70 -->

Three of the classic attacks share one shape: **input ends up somewhere it's treated as more than data.**

1. **Injection** — input reaches an interpreter and becomes part of a command. SQL injection (`' OR 1=1--`) is the famous one; command and NoSQL injection are the same idea. Fix: parameterised queries, argument lists, never building commands from strings.
2. **XSS (cross-site scripting)** — input reaches another user's browser and runs as script, to steal their session or act as them. Fix: encode output for its context, and a strong Content Security Policy.
3. **SSRF (server-side request forgery)** — input is a URL your *server* then fetches, so the attacker aims it at internal services or the cloud metadata endpoint. Fix: allowlist destinations, block internal addresses.

You met all three fixes in the web-security section. Here, the point is to recognise them as a family: injection hits the *database's* parser, XSS hits the *browser's*, SSRF abuses the *server's* own network position.

## 4. The two root causes
<!-- bite: 4a6eeb2b-a2e6-42bf-8c32-cae9559e7bfa -->

Step back and nearly every web attack reduces to one of two sentences:

1. **Untrusted input was treated as trusted** — as code (injection, XSS), as a destination (SSRF), or as truth (a price the client sent, an unverified update). The fix is always a boundary: validate input, and keep data as data.
2. **An access check was missing or wrong** — broken access control, privilege escalation, a forgotten authorization check. The fix is always to check, server-side, on every request.

Misconfiguration and outdated components are the third theme: weaknesses you inherit rather than write. The checklist exists because it's easy to secure the input on one form and forget the next one, or to patch one library and miss another.

## Terms used in this lesson
<!-- bite: 4de839cf-b654-4ca0-af0b-c3d70e9a45c4 -->

1. **OWASP Top 10**: This is a regularly updated list of the most serious kinds of web application weakness, used as a shared checklist.
2. **Broken access control**: This is an app failing to enforce who may do or see what.
3. **IDOR / BOLA**: These name the same bug: reaching another user's data by changing an identifier, because ownership isn't checked. BOLA is the API term.
4. **Injection**: This is untrusted input reaching an interpreter and changing a command instead of being treated as data.

## Terms used in this lesson: the rest of the family
<!-- bite: eece342c-2d22-49ff-b5d6-7758a715fae6 -->

The rest of the terms name the other attack classes you'll meet by name.

5. **XSS (cross-site scripting)**: The letters stand for those words. It's injecting script that runs in other users' browsers.
6. **CSRF (cross-site request forgery)**: The letters stand for those words. It's tricking a logged-in user's browser into making a state-changing request to your site.
7. **SSRF (server-side request forgery)**: The letters stand for those words. It's making the server fetch a URL the attacker chose, often an internal one.
8. **Security misconfiguration**: This is a weakness from how a system is set up, not its code: default passwords, debug pages left on, missing headers.

## Worked example — classify the Juice Shop bugs
<!-- bite: 5ab216f7-9400-48f0-a137-a913e7e1bcf7 -->

You already found several bugs on Juice Shop in the ethical-hacking section. Put each one in its OWASP category. **Predict first**, then check.

1. Logging in with `' OR 1=1--` in the email field.
2. Reading `/rest/basket/2` when you're the owner of basket 1.
3. The admin user list reachable once you're the first user.
4. A stored comment containing `<script>` that runs when another user views it.

| Bug | OWASP category |
|---|---|
| 1. `' OR 1=1--` login bypass | **A05 Injection** (SQL injection) |
| 2. Reading another user's basket | **A01 Broken Access Control** (IDOR / BOLA) |
| 3. Reaching admin data | **A01 Broken Access Control** (privilege escalation) |
| 4. Stored `<script>` | **A05 Injection** (stored XSS) |

## Worked example: the pattern, and the checklist
<!-- bite: 6a70d0af-28a7-4160-81d2-4033b48dbe69 -->

Look at the two root causes in that table. Bugs 1 and 4 are both "input treated as code". Bugs 2 and 3 are both "a missing access check". Two sentences cover four different-looking bugs, which is exactly why the root causes are worth holding in your head.

Now use the list the other way, as a review. Take your own app and go down the Top 10, writing one line each:

```text
A01 Access control  — does every endpoint check the object belongs to the user?  __
A02 Misconfiguration — debug off? default creds changed? security headers set?    __
A03 Supply chain     — when did I last run `npm audit` / `pip-audit`?             __
A04 Crypto           — HTTPS everywhere? passwords bcrypt/argon2?                 __
A05 Injection        — parameterised queries? output encoded? (grep for them)    __
...                                                                               __
```

That checklist, filled in honestly, is a basic threat model for an app, and the first week-7 deliverable of SWE 101. It's the difference between "I think it's secure" and "I checked these ten things."

## Common pitfalls and traps
<!-- bite: e9b6012d-dbdb-4754-a50f-7a2fd6e12ffe -->

1. **Hiding instead of checking.** Removing an admin link isn't access control; the endpoint must check the role on every request.
2. **Filtering input instead of fixing the boundary.** Blocking the word `script` or stripping quotes is a denylist attackers slip past. Parameterise and encode instead.
3. **Securing one form and forgetting the rest.** Attackers try every endpoint. The checklist is per-endpoint, not per-app.
4. **Ignoring your dependencies.** Most code in a modern app is libraries. An unpatched one is a supply-chain hole you didn't write but still own.
5. **Treating the Top 10 as exhaustive.** It's the common, high-impact kinds, not every bug. Business-logic flaws unique to your app aren't on any list.

## Check your understanding
<!-- bite: 08ea593b-f6f2-4074-92b6-1d6669c65d33 -->

Try each one before you open the answer.

1. <!-- q: mcq id="838333da" -->
   A logged-in user changes the URL `/api/invoices/1001` to `/api/invoices/1002` and sees another customer's invoice. Which OWASP category is this?

   - [x] A01 Broken Access Control (IDOR / BOLA)
   - [ ] A05 Injection
   - [ ] A02 Security Misconfiguration
   - [ ] A04 Cryptographic Failures

   <details><summary>Answer</summary>

   Broken access control: the app checked the user was logged in but not that invoice 1002 belonged to them. The fix is to check ownership on the server for every request, not to make the IDs harder to guess.

   </details>

2. <!-- q: mcq id="3a1acc9e" -->
   A "share by URL" feature lets a user give any link, and the server fetches it to make a preview. An attacker enters `http://169.254.169.254/latest/meta-data/`. What is this attack?

   - [ ] XSS
   - [ ] SQL injection
   - [x] SSRF (server-side request forgery)
   - [ ] CSRF

   <details><summary>Answer</summary>

   SSRF: the attacker makes the server fetch a URL they chose, here the cloud metadata endpoint, which can leak credentials. Fix: allowlist what the server may fetch and block internal and link-local addresses.

   </details>

3. <!-- q: mcq id="f275a4c5" -->
   Which two root causes do most web attacks reduce to? Choose all that apply.

   - [x] Untrusted input treated as trusted (as code, a destination, or truth).
   - [x] A missing or wrong access check.
   - [ ] Servers being too slow.
   - [ ] Users choosing weak passwords only.

   <details><summary>Answer</summary>

   Those two cover injection, XSS, SSRF and client-trusted data on one side, and broken access control and privilege escalation on the other. Weak passwords are a real problem (authentication failures) but not the unifying root cause of web attacks.

   </details>

4. <!-- q: gap id="ee7e34dc" answers="stored" accept="persistent" -->
   An attacker saves a comment containing a `<script>` tag, and it runs in the browser of every user who later views that comment. This kind of XSS, where the payload is saved and served to others, is called ___ XSS.

   <details><summary>Answer</summary>

   Stored (also called persistent) XSS. It's more dangerous than reflected XSS, which needs the victim to click a crafted link, because it hits everyone who views the page.

   </details>

5. <!-- q: mcq id="2289e889" -->
   An app is fully patched and has no injection or access-control bugs, but its admin panel still uses the default password `admin/admin` and its error pages print full stack traces. Which category covers this?

   - [ ] A01 Broken Access Control
   - [ ] A05 Injection
   - [x] A02 Security Misconfiguration
   - [ ] A03 Software Supply Chain Failures

   <details><summary>Answer</summary>

   Security misconfiguration: default credentials and verbose errors are setup problems, not code bugs. It's one of the most common findings in real reviews, and among the easiest to fix.

   </details>

6. <!-- q: open id="c0e44fbc" -->
   Your company uses a popular open-source library, and a serious vulnerability is announced in it (like Log4Shell). You didn't write the buggy code. Explain which OWASP category this falls under and why it's still your responsibility.

   <details><summary>Answer</summary>

   It's A03 Software Supply Chain Failures (formerly "vulnerable and outdated components"). Most of a modern app is third-party code, and a vulnerability in a dependency is reachable in your running app just like one in your own code, so attackers exploit it against you regardless of who wrote it. It's your responsibility because you chose to include it and you run it: you have to track your dependencies, scan them (`npm audit`, `pip-audit`, a software bill of materials), and patch or replace a vulnerable one quickly.

   </details>

## Practice — run the Top 10 against your app
<!-- bite: 9d1d1e5f-7575-4e2e-83c4-6c230f01446b -->

**Task.** Use the OWASP Top 10 as a review checklist on your own app (the SWE 101 flagship, or any app you've built).

1. For each of the ten categories, write one specific line about your app: where it applies, and whether you're confident it's handled.
2. For A05, actually grep for string-built SQL and for disabled escaping, as in the web-security lesson. For A03, run your language's dependency audit.
3. Pick the weakest category and fix one concrete thing, with a test.
4. If you have Juice Shop running, find one more bug not in the worked example and classify it.

## Practice: when your review is done
<!-- bite: 8a572367-d3d1-4473-b4fb-4d073924f335 -->

Here is how you know the task is finished.

**Done when:** all ten categories have a specific line, the dependency audit has been run, and one fix is made with a test. Keep the checklist; it's the start of a threat model.

## Before moving on
<!-- bite: 3a9c5487-d43a-4ed2-bee4-d12d1e2a640b -->

You can now say what the OWASP Top 10 is and use it as a checklist, name the main web attack classes, reduce most web attacks to two root causes, and classify a real finding by its category.

**Recap for later lookup:** OWASP Top 10 = the shared checklist of serious web weaknesses (2025: access control #1, misconfiguration, supply chain, crypto, injection…). Broken access control = missing ownership/role checks; fix server-side, every request. Injection, XSS, SSRF = input treated as code / destination. Two root causes: untrusted input treated as trusted, and a missing access check. Dependencies are yours too.

Next: [[cybersecurity/06-attacks-and-threats/04-password-malware-and-exploits|password attacks, malware and exploits]], the attacks aimed below the web app.

## Related
<!-- bite: 308f0705-0a42-4e94-a2c9-877ce61bea76 -->

- [[cybersecurity/04-web-security/index|Web security]] — the defence for every attack here.
- [[cybersecurity/02-ethical-hacking/07-exploitation-concepts|Exploitation concepts]] — proving these bugs on Juice Shop.
- [[cybersecurity/14-api-security/index|API security]] — BOLA and the OWASP API Top 10, for machine clients.

## About this lesson
<!-- bite: ae051b38-3aa1-40c1-98d9-e8b8e423d498 -->

**Level:** Intermediate. **Covers:** the OWASP Top 10 (2025 edition) as vocabulary and checklist, broken access control (IDOR, BOLA, privilege escalation), injection, XSS, CSRF and SSRF as one input family, security misconfiguration and supply-chain failures, the two root causes of web attacks, and classifying Juice Shop findings by category. **Where it sits:** lesson 3 of the [[cybersecurity/06-attacks-and-threats/index|Attacks and Threats]] section. **Sources:** the original vault note (from the roadmap.sh roadmap, OWASP branch), updated to the OWASP Top 10 2025 list and rebuilt around the Juice Shop findings from the ethical-hacking section.
