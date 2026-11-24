---
id: ed29afbc-d0b7-40e5-9a08-438fb3244ea7
---

# Reconnaissance

**Reconnaissance is building a picture of your target before you touch it — ideally before you touch it in any way it could notice.**

## Before you start
<!-- bite: 35929f83-d6f9-4801-ab8d-e24b665173ad -->

You should be able to:

- Name the stages of an engagement → [[cybersecurity/02-ethical-hacking/02-penetration-testing-methodology|methodology]].
- Say what a domain, a DNS record and an HTTP header are → [[networking/index|networking]].

After this lesson you will be able to:

1. Tell passive reconnaissance from active, and say why engagements start passive.
2. List the main categories of open-source intelligence (OSINT) and run the basic passive lookups.
3. Do first-pass recon on a web app from the browser alone, and read what it gives away.
4. Explain why recon quality caps the whole engagement, and why it's revisited, not done once.

**Study route.** Kid version and §1–4, then the worked example (recon on Juice Shop from the browser), then the practice task.

## What reconnaissance is

It's stage 2 of the [[cybersecurity/02-ethical-hacking/02-penetration-testing-methodology|engagement loop]], and it decides how good the rest of the test is: you can't scan or break what you don't know is there.

## The kid version
<!-- bite: ca7d13eb-8f48-4250-a613-db36c61d397c -->

Before a good pickpocket makes a move, they watch. Who's carrying a bag loosely, which pocket the phone went into, who's distracted on their phone, where the exits are. They never touch anyone during this — they just look, and by the time they act they already know exactly what they're reaching for.

Reconnaissance is that watching, for a computer system. You learn everything you can from the outside — the names, the addresses, the software, the open doors — so that when you finally do reach out and touch the system, you already know where to reach.

**Where the analogy stops working.** A pickpocket's watching leaves no trace. Some of your recon does: the moment you start *asking the target's own machines* questions (resolving its DNS, loading its website), you show up in its logs. That line — between looking at public records and poking the target itself — is the line between passive and active, and it matters enough to be §1.

## 1. Passive versus active
<!-- bite: 86b061d5-2717-49d4-9fe4-482f388eaf6b -->

There are two kinds of recon, and the difference is **whether any of your traffic reaches the target.**

**Passive recon** gathers information without touching the target's systems at all. You read public records, search engines, social media, DNS registries, job adverts (which love to list the exact tech stack they hire for), and public breach databases. None of this sends a packet to the target, so it's effectively invisible to them.

**Active recon** interacts with the target directly — pinging its hosts, resolving its DNS through its own servers, browsing its website, loading its API. Still low-risk and usually in scope, but now you're in its logs.

Engagements **start entirely passive** and only go active once the passive groundwork is done. You learn everything free and invisible first, so that by the time you make noise, you're making as little as possible. On your own lab this is lower-stakes — it's your box — but the habit is the skill.

## Terms used in this lesson
<!-- bite: 85a8ae0e-5643-4b6d-a7b5-a59c151a9ede -->

1. **Reconnaissance**: This is also just called **recon**. It's gathering information about a target to plan the attack.
2. **OSINT (open-source intelligence)**: The letters stand for those three words. It's information gathered from public sources — anything you can find without special access.
3. **Attack surface**: This is the full set of things an attacker could poke at: every domain, subdomain, open port, page, input and API the target exposes.
4. **WHOIS**: This is a public record saying who registered a domain, when, and through which company. The name is literally "who is" (the owner).
## Terms used in this lesson: what the records reveal

The last four terms are the places recon finds things.

5. **DNS record**: This is an entry in the domain name system that maps a name to something — an address (`A`), a mail server (`MX`), another name (`CNAME`). Reading them reveals infrastructure.
6. **Subdomain**: This is a name under a main domain, like `admin.example.com` under `example.com`. Forgotten subdomains are a classic easy win.
7. **Breach data**: This is data (emails, passwords) leaked from past hacks of *other* services, now public. If a target's staff reused those passwords, the leak is a way in.
8. **Technical footprint**: This is the visible evidence of what software a target runs — headers, error pages, job adverts, public code — that tells you what you're up against.

## 2. OSINT — the categories
<!-- bite: 6adc1961-e21d-48fd-8098-cb882662976a -->

Passive recon is mostly OSINT, and it falls into four buckets:

1. **Domain and DNS information** — WHOIS records (who owns the domain), and DNS records revealing mail servers, hosting providers and subdomains.
2. **Organisational information** — company structure, staff names and roles. These suggest likely usernames (`first.last@`) and are the raw material for any *authorized* social-engineering test.
3. **Technical footprint** — job adverts naming technologies, public code repositories, exposed documentation, cached pages showing content that was since removed.
4. **Breach data** — whether a target's email domains appear in known public breaches, which hints at reused or weak credentials still floating around.

For your **own lab**, the public footprint is tiny — a fresh VPS has almost no OSINT trail — so the OSINT reps come from thinking about what a *real* target would leak. The active, hands-on recon you'll do today is against the target itself, next.

## 3. The passive lookups, as commands
<!-- bite: 61593e75-9f44-43a8-a933-50e0cba96526 -->

These three are the bread-and-butter passive DNS lookups. They query public registries and DNS, not the target's own web servers, so they stay on the passive side. Run them against a domain you own (or a big public one, to see fuller output):

```bash
whois example.com                 # who registered the domain, when, through whom
dig example.com ANY               # all DNS records: addresses, mail servers, name servers
dig +short MX example.com         # just the mail servers — who handles their email
```

`dig` (domain information groper) is the modern tool; `nslookup -type=MX example.com` does the same on systems without it. What you're reading out of these: the hosting provider (from the address ranges), the email provider (from `MX`), and any subdomains that show up — each one a new piece of attack surface to note and, later, to check against scope.

## 4. First-pass recon from the browser
<!-- bite: 13e555d4-a48a-4699-bf8b-cc8fab4e492e -->

For a web app, a huge amount of recon needs nothing but a browser and its developer tools (F12). This is *active* — you're loading the target's pages — but it's the gentlest active recon there is, indistinguishable from a normal visitor. On any web target you'll check:

1. **The technology.** The Network tab shows response headers (`Server:`, `X-Powered-By:`), cookie names, and the shape of the JavaScript bundles — often enough to name the framework and server.
2. **`/robots.txt` and `/sitemap.xml`.** These list paths the site *doesn't* want crawled — which is a map of the interesting ones.
3. **The routes and inputs.** Click around with the Network tab open and watch which API endpoints get called. Every URL, form field and query parameter is a place you can test later.
4. **Error pages and source comments.** A stack trace or a leftover `<!-- TODO: remove debug endpoint -->` is pure gift.

This is where recon hands off to [[cybersecurity/02-ethical-hacking/06-scanning-and-enumeration|scanning]]: recon tells you the app exists and roughly what it is; scanning maps it exhaustively.

## 5. Why recon quality caps everything
<!-- bite: b09f1b2f-2c71-4933-8cce-b7191539b762 -->

Here's the rule that makes people take this seriously: **you can only attack what you found.** A thorough recon phase can map an organisation's entire external surface — every subdomain, every exposed service, every piece of software — often before a single scan runs. The single easiest win in many real engagements (a forgotten admin panel, a misconfigured cloud bucket, a staging site with debug mode on) is a *recon* find, not a clever exploit. Rush recon and you simply never see it, and no amount of exploitation skill later recovers a target you didn't know existed.

And recon isn't a one-time, upfront step. On a long engagement a subdomain you found in week one may be gone by week three, and a new one may have appeared. Recon is **revisited throughout** — every new thing a later stage uncovers sends you back here to look again. That's the loop-back arrow from the methodology lesson.

## 6. Social engineering is separately scoped
<!-- bite: 745f01fc-4af6-4d0e-b4b2-98515cc071df -->

Some engagements include testing people, not just machines — phishing simulations, pretext phone calls. This is powerful (most real breaches start with a tricked person), but it's a **distinct, separately-authorized activity**, not a default part of recon. The reason: it involves real humans who didn't individually consent the way a system owner signed off on testing their servers. It only happens when it's explicitly in [[cybersecurity/02-ethical-hacking/01-rules-of-engagement-and-legal|scope]], and the OSINT you gather about staff is background for it — never a licence to actually contact anyone unless the paperwork says so.

## Worked example — recon Juice Shop from the browser
<!-- bite: 097bf8b2-9ce9-407b-b786-7dd2d5100d6c -->

You'll run Juice Shop for real in [[cybersecurity/02-ethical-hacking/05-home-lab-setup|lesson 05]]; here's what first-pass browser recon on it *finds*, so you know what you're looking for. Open `http://localhost:3000` with dev tools on the Network tab.

| What you look at | What it tells you |
| --- | --- |
| Response headers | A Node/Express back end (sometimes an `X-Powered-By: Express`), serving a single-page app. |
| The loaded bundle | An **Angular** front end — the whole UI is JavaScript talking to an API. |
| Network tab while clicking | API calls to `/rest/...` and `/api/...` — the real attack surface, not the HTML. |
| `http://localhost:3000/robots.txt` | A short list, including a hint toward `/ftp` — a directory you're clearly meant to find. |
| The product search box | Typing a letter fires `/rest/products/search?q=...` — one query parameter, one obvious thing to test later. |

**What recon just handed you:** the stack (Angular + Express), the two API prefixes, a suspicious `/ftp` path, and a search parameter. You haven't attacked anything — every one of those was a normal page load — but you now have a *target list* for scanning and exploitation. That list is the entire output of recon, and notice how much of it came from just reading, before any tool.

## Common pitfalls and traps
<!-- bite: 436b258e-ce92-4815-811f-0f9649e56e73 -->

1. **Treating recon as a box to tick once.** It's revisited all engagement. New findings reopen it.
2. **Passive recon that drifts out of scope.** Gathering info about a target's *subsidiary* or an unrelated subdomain can create legal exposure even though you never sent them a packet. Scope covers what you may *research*, not just what you may attack.
3. **Confusing "no packets" with "safe to pursue."** Finding a juicy subdomain passively doesn't authorize touching it — check it against scope first.
4. **Skipping browser recon because it feels too simple.** The Network tab and `/robots.txt` routinely reveal more, faster, than any scanner. Simple isn't the same as low-value.
5. **Mistaking OSINT about people for permission to contact them.** That's social engineering, and it needs its own sign-off.

## Check your understanding
<!-- bite: b50bc781-4f88-49f1-8b91-d0fabab54344 -->

Try each one before you open the answer.

1. <!-- q: mcq id="b6b4c6d8" -->
   Which activity is **passive** reconnaissance — leaving no trace on the target's own systems?

   - [ ] Browsing the target's website with developer tools open.
   - [ ] Running `nmap` against the target's web server.
   - [x] Reading the target's WHOIS record and a public breach database.
   - [ ] Loading the target's `/robots.txt` file.

   <details><summary>Answer</summary>

   Reading WHOIS and public breach data queries third-party registries and databases, not the target, so no traffic reaches the target and it leaves no trace there. Browsing the site, loading `/robots.txt`, and running nmap all send requests to the target's own systems — that's active recon (or scanning).

   </details>

2. <!-- q: gap id="a18810b5" answers="subdomain" -->
   `admin.example.com` sitting under `example.com` is an example of a ___ — and a forgotten one is a classic easy win because it's often less maintained than the main site.

   <details><summary>Answer</summary>

   A subdomain. Enumerating subdomains is a core recon task precisely because forgotten or staging ones (`old.`, `dev.`, `admin.`) are frequently weaker than the main site and widen the attack surface.

   </details>

3. <!-- q: mcq id="2187241a" -->
   Why do professional engagements begin with passive recon before any active recon?

   - [ ] Passive recon finds more vulnerabilities than active recon.
   - [x] It gathers information invisibly, so you learn as much as possible before making any noise the target could notice.
   - [ ] Active recon is illegal without a second authorization.
   - [ ] Passive recon is faster to run.

   <details><summary>Answer</summary>

   Passive recon sends nothing to the target, so it's effectively undetectable. Doing it first means you arrive at the active stage already knowing the layout, so you can make as little detectable noise as possible. It isn't inherently faster, nor does it find *more* bugs — and active recon is normally in scope, not separately illegal.

   </details>

4. <!-- q: open id="f42cf3c3" -->
   You have brilliant exploitation skills but you rush recon, spending five minutes on it. Explain, using the idea of attack surface, why this caps how good your whole engagement can be — no matter how good your exploitation is.

   <details><summary>Answer</summary>

   You can only attack the surface you found. Recon is what discovers the subdomains, services, panels and inputs that make up the attack surface; anything you don't find in recon simply isn't on your list to scan or exploit later. A forgotten admin panel or a staging site with debug mode on is often the easiest way in, and it's a recon find — so rushing recon can make you miss the single best path entirely, and no amount of exploitation skill recovers a target you never knew existed. Recon quality sets a ceiling on everything after it.

   </details>

5. <!-- q: mcq id="4b52279e" -->
   During an authorized network pentest (systems only), your OSINT turns up the CEO's email and the fact they use a particular webmail. What may you do with it?

   - [ ] Send a test phishing email to see if they click.
   - [ ] Try logging into their webmail with passwords from a breach database.
   - [x] Note it as background; take no action against the person unless social engineering is separately in scope.
   - [ ] Call them pretending to be IT to test their awareness.

   <details><summary>Answer</summary>

   Note it and stop. Testing people — phishing, pretext calls, trying their credentials — is a separately-scoped activity because it involves a human who didn't individually consent. Finding information passively never authorizes acting on it; your scope here is systems only.

   </details>

## Practice — passive then active recon on something you own
<!-- bite: 0ec1075d-73b4-4705-8950-637ff3a4e6f2 -->

**Task.** Pick a domain you own (or, if you have none, a large public site like `wikipedia.org`, which is fine to *passively* look up). Do a recon pass in two clearly separated halves.

1. **Passive:** run `whois`, `dig ANY`, and `dig +short MX`. Write down the registrar, the hosting/address ranges, and the mail provider.
2. **Active (your own site only):** open it with dev tools, and record the server/framework from the headers, anything in `/robots.txt`, and three API endpoints or query parameters you'd test later.

**Done when:** you have a one-page recon note with a *passive* section and an *active* section, and a short "attack surface" list at the bottom — the endpoints and inputs a later stage would target. **If you used a public site, do the active half only against your own property**, never someone else's.

**Stretch.** For a real target, which single OSINT find would worry you most as the *defender*, and why? (Hint: think about what a forgotten subdomain with debug mode on would hand an attacker.)

## Before moving on
<!-- bite: b50bc781-4f88-49f1-8b91-d0fabab54345 -->

You can now separate passive recon (invisible, public sources) from active (touches the target, shows in logs), run the basic passive DNS lookups, and pull a target list out of a web app with nothing but a browser. You know recon quality caps the whole engagement and that it's revisited, not done once.

**Recap for later lookup:** recon = build the picture before touching. Passive (WHOIS, DNS, breach data, OSINT) first, then active (browser, pings). Output is the attack surface — the list everything later works from. Social engineering is separately scoped.

Next: [[cybersecurity/02-ethical-hacking/04-lab-setup-and-os-choice|lab setup and OS choice]] — what to actually run your tools *from* before the hands-on stages begin.

## Related
<!-- bite: b50bc781-4f88-49f1-8b91-d0fabab54346 -->

- [[cybersecurity/02-ethical-hacking/02-penetration-testing-methodology|Methodology]] — recon is stage 2 of the loop.
- [[cybersecurity/02-ethical-hacking/06-scanning-and-enumeration|Scanning and enumeration]] — stage 3, where recon's target list gets mapped exhaustively.
- [[cybersecurity/02-ethical-hacking/01-rules-of-engagement-and-legal|Rules of engagement]] — scope covers what you may research, not only attack.

## About this lesson
<!-- bite: 312c59de-f284-4ff7-92a1-b2a219613330 -->

**Level:** Beginner. **Covers:** passive versus active reconnaissance, the four OSINT categories, the basic passive DNS lookups, first-pass browser recon on a web app, why recon quality caps the engagement, and social engineering as a separately-scoped activity. **Where it sits:** lesson 3 of the [[cybersecurity/02-ethical-hacking/index|Ethical Hacking]] section — stage 2 of the engagement loop, between methodology and lab setup. **Sources:** the original vault note, reframed around browser recon on Juice Shop (the section's tier-1 target). `[reference]` — not drawn from a personal paid engagement. Live lookups are tracked in `cybersecurity/LIVE-RUNS-TODO.md`.
