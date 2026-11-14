# 01 — Anatomy of a hacked cPanel site (CEDHUL, Oct 2026)

See also: [02-shell.md](02-shell.md) · [03-deploy.md](03-deploy.md)

The CEDHUL website (cedhul.com.ng, Centre for Digital Humanities, UNILAG) was a hand-written
static HTML site on shared cPanel hosting, with no version control. It was compromised. This
is what was found when the files were pulled down and audited on 2026-10-30.

## What the attacker added

| Artifact | Type | What it did |
|---|---|---|
| `.htaccess` first two rule blocks | **SEO cloaking** | Googlebot (or a visitor arriving *from* Google) asking for `/event.html` was silently served `/pageview/theme.php` — a gambling spam page. Humans typing the URL saw the real page, so the owner never noticed. |
| `pageview/index.php`, `theme.php`, `px.txt` | Spam payload | Indonesian online-gambling ("slot gacor") landing page + a traffic-distribution script (`CAMPAIGN_ID`, `ENC_KEY`) |
| `robots.txt` | SEO spam | Advertised 16 fake `sitemap-N.xml` files to push spam URLs into Google's index |
| `mon/project-squareup-…/` | **Phishing kit** | Fake Square login with admin panel, OTP/security-question capture, IP blocking, "Antibot" to hide from security scanners. The server was being used to steal *other people's* credentials. |
| `file.php` (6 MB) | **Webshell** | Starts with `error_reporting(0); set_time_limit(0);` then a fake "Horde Text_Diff" docblock as camouflage. Gives the attacker a remote file manager/shell. |
| `oxo_test.php` | Access resale | Sends "This cpanel … is delivering, you can buy it now" then deletes itself. The cPanel login was being **sold**. |
| `www.php`, `public_html.php` | Empty files | Markers/leftovers |
| `cedsite/` | Duplicate | Whole copy of the site *including* the phishing kit |

## Red flags worth recognising on sight

- `error_reporting(0)` at the top of a PHP file — hide every error so nothing leaks into logs.
- Huge single PHP files in a site that otherwise has no PHP backend.
- `.htaccess` rules conditioned on `HTTP_USER_AGENT Googlebot` or `HTTP_REFERER google` — that is
  the definition of cloaking; no legitimate site does this.
- Random-looking folder names (`sb1-sdfvgertgr43563456dfvg4`).
- `robots.txt` listing sitemaps that don't exist in the file tree.

## How the audit was done (method, reusable)

1. **Never execute anything** from the compromised tree — read only (`cat`, `head -c`, `grep`, `unzip -l`).
2. Find a known-good baseline (here: `index.zip`, a Dec 2025 backup) and diff the live files against it.
   Differences were legitimate content edits (Admissions/Trivia/Blog pages), not injections.
3. Grep for obfuscation patterns: `eval(`, `base64_decode`, `gzinflate`, `str_rot13`, `atob(`,
   `fromCharCode`, plus spam keywords. Expect false positives (jQuery legitimately uses `fromCharCode`
   and `globalEval`; `<slot>` is an HTML element) — read each hit, don't just count them.
4. List every external domain the HTML links to and eyeball it for anything unexpected.

## Why moving to Git + Vercel fixes the root problem

On cPanel, the live server *was* the source of truth: whatever was on disk was the site, and an
attacker with FTP/cPanel access could change it invisibly. With Git as the source of truth and a
host that builds from the repo:

- every change is a reviewed, attributable commit — an injected file would show up in `git status`/diffs;
- the deploy target is immutable output; there's no writable server for a webshell to live on;
- there is no PHP runtime at all, so a whole class of attack (webshells, phishing kits) can't run.

## Cleanup outside the code (owed — not fixed by a new repo)

- [ ] Change cPanel, FTP, email and any database passwords on the old host; assume they're known.
- [ ] Take the old host offline or wipe it once DNS points at Vercel.
- [ ] Google Search Console: request removal of spam URLs, resubmit the real sitemap, check "Security issues".
- [ ] Restrict the Google Maps API key in the HTML to the new domain (HTTP referrer restriction).
- [ ] Optionally report the phishing kit to the host so they can check other accounts.
