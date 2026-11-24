# Cybersecurity — live runs still to do

The pentesting lessons are written against targets the learner owns, but the commands and
exploits in them have **not been run yet** while writing (same policy as the framework lessons:
write first, run later, on an isolated setup). This file lists what to actually execute and
confirm before any lesson is marked fully verified. Every item assumes the owned-target model:
your own app, a real open-source app you cloned onto **your own VPS**, a PDF you locked, and a
database of dummy accounts you seeded. Nothing belonging to anyone else.

## The three target tiers (decided 2026-11-24)

The worked examples are written against **tier 1** so they're reproducible; practice tasks extend to tiers 2 and 3.

1. **Tier 1 — OWASP Juice Shop, local Docker.** Runnable now, no VPS. The teaching target for every worked example. `docker run -d -p 3000:3000 bkimminich/juice-shop`.
2. **Tier 2 — a real production-grade OSS app on your own VPS.** Added when you rent the box.
3. **Tier 3 — your own app, a PDF you locked, a database of dummy accounts.** For app-sec, document and password cracking.

## Lab the runs need

- [ ] Docker on the laptop, Juice Shop pulled and running (tier 1). Confirm it loads on `localhost:3000`.
- [ ] A VPS you control (any provider), with a snapshot taken before testing so you can roll back (tier 2).
- [ ] One real open-source web app deployed to the VPS (the real engagement target). Record which one.
- [ ] Your own small app deployed, for the app-sec track (tier 3).
- [ ] A locked PDF you created, for the document-cracking lesson (tier 3).
- [ ] A throwaway database seeded with dummy accounts and known passwords, for the hashing lesson (tier 3).
- [ ] Kali (or a vanilla Linux box with the tools) to run the attacks from.

## Per-lesson checks

### 02-ethical-hacking
- [ ] 01 rules-of-engagement — no commands; confirm the authorization decision chart matches the lab.
- [ ] 03 reconnaissance — run the passive + active recon commands against your own deployed target.
- [ ] 06 scanning-and-enumeration — run the real `nmap`/enumeration commands against the VPS target; confirm the outputs in the lesson.
- [ ] 07 exploitation — reproduce each vulnerability class on the owned target; capture the proof.
- [ ] 09 post-exploitation-and-reporting — produce the actual report from a real finding.
- [ ] 10 pdf-and-document-security — lock a PDF, then crack it; confirm timings.
- [ ] 11 wifi-security-testing — only against your own access point.
- [ ] 12/13 practice-exercises — work them end to end on the lab.

_(Add lessons here as the rebuild reaches them.)_

## Done
_(Move items here once run and confirmed, with the date.)_
