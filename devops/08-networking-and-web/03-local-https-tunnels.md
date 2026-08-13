# Local HTTPS Tunnels

Exposing a service running on `localhost` at a public HTTPS URL, so external systems can
reach your development machine. Part of the [[devops/README|DevOps curriculum]].

Written 2026-08-12, prompted by TikTok's Login Kit refusing `http://localhost` redirect URIs.

---

## 1. Why You Need One

Some integrations cannot talk to `localhost`, because the other party is a server on the
internet, not your browser:

- **OAuth callbacks that require https.** TikTok's Login Kit for Web mandates an `https`
  redirect URI with no localhost exception. Meta, X and Reddit all allow `http://localhost`,
  so this often surfaces as "why does only *this* provider fail?"
- **Webhooks.** Stripe, GitHub, Paystack, Twilio — anything that POSTs to you needs a
  reachable URL. You can replay events locally with some CLIs, but a tunnel is the general
  answer.
- **Third-party services that fetch a URL you gave them** — link previews, media ingestion.
- **Showing work in progress** to someone on another network, without deploying.

A tunnel runs a client on your machine that holds an outbound connection to a relay; the
relay accepts public requests and forwards them down that connection. Because the connection
is outbound, no port forwarding, firewall rule, or public IP is involved.

```
Internet → relay (public https URL) → outbound tunnel ← cloudflared/ngrok on your laptop → localhost:5000
```

---

## 2. cloudflared vs ngrok

Both do the same core job. The deciding factor is usually **URL stability**.

| | cloudflared | ngrok |
|---|---|---|
| Cost | Free, unlimited | Free tier, paid for reserved domains |
| Stable URL | Yes, free — via a named tunnel on a domain you own | Paid feature on the free tier |
| Requires a domain | For stable URLs, yes (on Cloudflare) | No |
| Zero-setup mode | `--url`, random `trycloudflare.com` | `ngrok http`, random URL |
| Request inspector | No | Yes — local web UI replaying requests |
| Config as code | Yes, systemd service + YAML | Yes |

**Why URL stability matters more than it sounds.** OAuth providers match redirect URIs by
**exact string**. Every time a random tunnel URL rotates you must go back into the developer
portal and re-register. Same for webhook endpoints. If you already own a domain on
Cloudflare, a named `cloudflared` tunnel gives a permanent `api-dev.yourdomain.com` for free,
and that alone usually settles it.

**When ngrok still wins:** you don't own a domain, or you want its request inspector —
genuinely excellent for debugging webhook payloads, since you can see and replay every
request without adding logging.

---

## 3. cloudflared — Install

**Not in Fedora's repos.** Cloudflare ships its own RPM. Their `pkg.cloudflare.com` repo
targets RHEL `$releasever` values and won't resolve on Fedora.

```bash
curl -Lo /tmp/cloudflared.rpm \
  https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-x86_64.rpm
sudo dnf install /tmp/cloudflared.rpm
cloudflared --version
```

`-L` follows redirects — GitHub's `/latest/download/` is a redirect, and without it you save
the redirect page instead of the package. `-o` writes to a path.

Debian/Ubuntu: same URL with `.deb`, then `sudo dpkg -i`. macOS: `brew install cloudflared`.

Verify the asset name rather than trusting a blog post:

```bash
curl -sL https://api.github.com/repos/cloudflare/cloudflared/releases/latest \
  | grep -o '"name": "[^"]*\.rpm"' | sort -u
```

---

## 4. Quick Tunnel — Zero Setup, Rotating URL

```bash
cloudflared tunnel --url http://localhost:5000
```

Prints a random `https://<random-words>.trycloudflare.com`. No account, no DNS, no config.

Good for a one-off demo or a single test. The URL changes on every restart, so it's the
wrong tool for anything you have to register somewhere.

---

## 5. Named Tunnel — Stable Subdomain

Requires a domain on Cloudflare.

```bash
cloudflared tunnel login                    # browser; authorise a domain
cloudflared tunnel create myapp-dev         # creates tunnel + credentials JSON in ~/.cloudflared/
cloudflared tunnel route dns myapp-dev api-dev.yourdomain.com   # CNAME → the tunnel
cloudflared tunnel run --url http://localhost:5000 myapp-dev
```

`api-dev.yourdomain.com` now serves whatever is on `localhost:5000`, over HTTPS, with a valid
certificate — and keeps that name across restarts and reboots.

### Config file instead of flags

`~/.cloudflared/config.yml`:

```yaml
tunnel: myapp-dev
credentials-file: /home/you/.cloudflared/<TUNNEL-UUID>.json

ingress:
  - hostname: api-dev.yourdomain.com
    service: http://localhost:5000
  - hostname: app-dev.yourdomain.com
    service: http://localhost:3000
  - service: http_status:404          # required catch-all, must be last
```

Then just `cloudflared tunnel run myapp-dev`. Multiple hostnames through one tunnel is the
main reason to use the config file — useful when the API and frontend both need to be
reachable.

The trailing catch-all rule is mandatory; cloudflared refuses to start without it.

### Run it as a service

```bash
sudo cloudflared service install
sudo systemctl enable --now cloudflared
systemctl status cloudflared
```

See [[devops/01-linux/07-systemd-and-services|systemd and services]].

---

## 6. Gotchas

**The tunnel is a separate process from your app.** Restarting the app is fine; killing the
tunnel makes the public URL 502. When an OAuth callback mysteriously fails, check the tunnel
is still up before debugging the integration.

**Host header and redirects.** Your app now sees requests for `api-dev.yourdomain.com` but
believes it lives at `localhost:5000`. Anything building absolute URLs from a hardcoded base
— OAuth `redirect_uri`, emailed links, `Location` headers — must use the public URL. Drive it
from config:

```
APP_URL=https://api-dev.yourdomain.com
```

If only *one* integration needs the tunnel, prefer a per-integration override rather than
changing `APP_URL` globally — otherwise you invalidate every other provider's registered
redirect URI at once.

**CORS.** A browser on `http://localhost:3000` calling `https://api-dev.yourdomain.com` is
cross-origin. Add the tunnel hostname to the allowed origins.

**It's a public URL.** Anyone with the address reaches your dev machine, including a database
full of test data and any debug endpoints. Don't leave one running unattended. For named
tunnels, Cloudflare Access can put auth in front of it.

**Cookies with `Secure`/`SameSite`.** Now that you're on https, cookie behaviour changes —
sometimes fixing local problems, sometimes creating them when only part of the stack is
tunnelled.

---

## Related
- [[devops/08-networking-and-web/01-networking-and-protocols|Networking & protocols]] — DNS, HTTPS, TLS
- [[devops/08-networking-and-web/02-web-servers-and-proxies|Web servers & proxies]] — reverse proxying generally
- [[concepts/01-backend/06-oauth-provider-integrations|OAuth provider integrations]] — why https callbacks force this
- [[devops/01-linux/07-systemd-and-services|systemd services]] — running the tunnel persistently
