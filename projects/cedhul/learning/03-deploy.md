# 03 — Static site → GitHub → Vercel

See also: [01-security-incident.md](01-security-incident.md) · [02-shell.md](02-shell.md)

## Why Vercel needs no config here

The site is plain HTML/CSS/JS with no build step. Vercel detects "Other" as the framework preset,
skips the build, and serves the repo root as static files. Every push to `main` deploys
to production. Every push to another branch/PR gets its own **preview URL**, so you can review before merging.

## What `.htaccess` did and the Vercel equivalent

`.htaccess` is Apache-only config, and Vercel ignores it. The legitimate rule in it was the
"send unknown paths to index" fallback (the rest was the attacker's cloaking). On Vercel:

- `index.html` at the root is served for `/` automatically (so `index.php` → `index.html`).
- A custom `404.html` at the root is served for missing pages.
- `vercel.json` `"cleanUrls": true` makes `/about` serve `about.html`.

## Custom domain

Vercel project → Settings → Domains → add the domain. Vercel then tells you which DNS records
to create at the registrar: an `A` record for the apex domain, and a `CNAME` to Vercel's
DNS target for `www`. HTTPS certificates are issued automatically.

## Files to keep out of the repo (`.gitignore`)

- `index.zip`: 150 MB. GitHub rejects any file over 100 MB, and it's a backup, not source.
- `.vscode/`, `settings.json` (editor config), `.ftpquota` (cPanel leftover).
