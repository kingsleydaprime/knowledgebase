# Manage SELinux Security

> RHCSA V10

Part of [[README|RHCSA V10]]. RHEL-specific — no equivalent exists elsewhere in this vault, since the other Linux notes here are Ubuntu/Debian-based, which use AppArmor instead. This is the single biggest conceptual gap between "knows Linux" and "knows RHEL," and it shows up constantly on the exam as "why won't this service start / serve files / connect out, even though the permissions are clearly right."

---

## The core idea: MAC vs. DAC

Everything in [[devops/01-linux/02-navigating-file-system|Navigating the Filesystem]] — `chmod`, `chown`, owner/group/other — is **DAC (Discretionary Access Control)**. The owner of a resource *discretionarily* decides who can access it. If `httpd` runs as root, DAC gives it access to literally everything root can touch — which is way more than a web server should ever need.

**SELinux is MAC (Mandatory Access Control)** — a second, independent layer of rules enforced by the kernel, on top of DAC, that no user (not even root) can override by just changing ownership. A process only gets access to something if **both** DAC *and* SELinux policy allow it. This is why `chmod 777` on a file sometimes still doesn't fix "permission denied" — DAC says yes, SELinux says no.

---

## Modes

```bash
getenforce                       # current mode: Enforcing / Permissive / Disabled
setenforce 0                     # switch to Permissive — RUNTIME ONLY, doesn't survive reboot
setenforce 1                     # switch back to Enforcing
```

| Mode | Behavior |
|---|---|
| **Enforcing** | Policy violations are blocked AND logged — production default |
| **Permissive** | Policy violations are only logged, never blocked — invaluable for debugging: "would this be allowed if SELinux were on?" |
| **Disabled** | SELinux entirely off, no logging either — almost never the right answer; prefer Permissive for debugging |

Persistent setting lives in `/etc/selinux/config`:
```ini
SELINUX=enforcing
SELINUXTYPE=targeted
```
Changing `SELINUX=` here requires a **reboot** to take effect (unlike `setenforce`, which is instant but temporary). Switching to/from `disabled` specifically triggers a full filesystem relabel on next boot — slow on a big disk, expected behavior.

---

## Contexts — SELinux's version of ownership

Every process and every file has an SELinux **context**: `user:role:type:level`. For file access decisions, the part that matters almost all the time is the **type**.

```bash
ls -Z /var/www/html/index.html
# unconfined_u:object_r:httpd_sys_content_t:s0   index.html

ps -eZ | grep httpd
# system_u:system_r:httpd_t:s0   1234 ?  httpd

id -Z
# unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
```

The policy (type `httpd_t` can read type `httpd_sys_content_t`) is what actually grants `httpd` access — not the fact that root owns the file, not the `rwx` bits.

---

## Fixing file contexts — the classic exam scenario

**Setup:** you move (or `mkdir`) a new web root at `/web` instead of the default `/var/www/html`, put files there, point Apache's config at it. Apache 403s anyway, even though DAC permissions are fine. This is *always* an SELinux context problem: files created outside `/var/www/html` don't inherit `httpd_sys_content_t` automatically.

```bash
# Wrong tool: chcon — sets the context directly but TEMPORARILY
chcon -t httpd_sys_content_t /web/index.html   # works until the next full relabel wipes it out

# Right tool for anything persistent: semanage fcontext + restorecon
semanage fcontext -a -t httpd_sys_content_t "/web(/.*)?"   # register the RULE in policy (regex — covers the dir + everything under it)
restorecon -Rv /web                                          # APPLY that rule to the actual files, recursively, verbose
```

`semanage fcontext` writes a persistent rule; `restorecon` is what actually walks the filesystem and applies it. You need both — `semanage` alone doesn't touch existing files, and `chcon` alone doesn't survive a relabel. This two-step (`semanage fcontext -a` then `restorecon -Rv`) is worth having memorized outright.

```bash
semanage fcontext -l | grep web        # confirm the rule is registered
```

---

## Booleans — policy on/off switches without editing policy

Booleans are pre-defined toggles for common "should this be allowed" questions, so you don't need custom policy just to, say, let a web server make outbound network connections (needed for reverse proxying, calling an API, etc.).

```bash
getsebool -a                                    # list every boolean and its current state
getsebool httpd_can_network_connect              # check one specifically
setsebool httpd_can_network_connect on           # change it — RUNTIME ONLY
setsebool -P httpd_can_network_connect on        # -P = persistent, survives reboot — almost always what you actually want
```

`-P` is the same trap as `setenforce` vs. editing `/etc/selinux/config` — forgetting it means the fix silently disappears on next boot.

---

## Troubleshooting when something's denied

```bash
tail -f /var/log/audit/audit.log | grep AVC     # raw denial log — AVC = Access Vector Cache, the denial event type
ausearch -m avc -ts recent                       # cleaner filtered view of recent AVC denials
sealert -a /var/log/audit/audit.log              # setroubleshoot — human-readable explanation + suggested fix command (dnf install setroubleshoot-server if missing)
```

`sealert` is worth leaning on — it doesn't just show the denial, it usually prints the exact `semanage`/`setsebool` command to fix it.

```bash
audit2allow -a                    # generate a custom policy MODULE from recent denials — last resort, not a first move
```
`audit2allow` should be treated as a last resort on the exam and in real life: it's how you accidentally grant way more access than intended by blindly allowing everything that got denied recently, instead of understanding *which specific* denial actually needs fixing.

---

## Quick diagnostic checklist

1. `getenforce` — is SELinux even enforcing right now?
2. `ls -Z` / `ps -eZ` — what context does the file/process actually have?
3. `ausearch -m avc -ts recent` or `sealert` — what got denied, and why?
4. Fix with `semanage fcontext -a` + `restorecon -Rv` (files) or `setsebool -P` (behavior toggle) — not `chcon`, not `setenforce 0`, not disabling SELinux outright.
