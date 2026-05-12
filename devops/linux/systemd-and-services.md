# systemd & Services

Every background program running on your system — nginx, postgres, redis, ssh — is managed by **systemd** as a **service**.

systemd is PID 1. It starts, stops, restarts, and monitors all services. If a service crashes, systemd can automatically restart it.

---

### Basic service commands

```bash
sudo systemctl start service      # start a service
sudo systemctl stop service       # stop a service
sudo systemctl restart service    # stop then start
sudo systemctl reload service     # reload config without stopping
sudo systemctl status service     # check if running
sudo systemctl enable service     # start automatically on boot
sudo systemctl disable service    # don't start on boot
sudo systemctl is-active service  # quick check — active or not
```

---

### Viewing all services

```bash
systemctl list-units --type=service              # all active services
systemctl list-units --type=service --all        # including inactive
systemctl list-unit-files --type=service         # enabled/disabled status
```

---

Try these on services you already have installed:

```bash
sudo systemctl status postgresql
sudo systemctl status redis
sudo systemctl status ssh
sudo systemctl status nginx
```

Tell me what you see — particularly the colored dot and the "Active:" line.

```zsh
> systemctl status postgresql
○ postgresql.service - PostgreSQL RDBMS
     Loaded: loaded (/usr/lib/systemd/system/postgresql.service; disabled; pres>
     Active: inactive (dead)
~                                                          took 11s at 08:55:27
```

That tells you everything:

| Part | Meaning |
|---|---|
| `○` | grey circle — service is stopped |
| `Loaded: disabled` | won't start automatically on boot |
| `Active: inactive (dead)` | not running right now |

---

The circles you'll see:

| Symbol | Color | Meaning |
|---|---|---|
| `●` | green | running |
| `○` | grey | stopped |
| `●` | red | failed/crashed |

---

Start postgres and check again:

```bash
sudo systemctl start postgresql
sudo systemctl status postgresql
```

You should see it flip to green. Then:

```bash
sudo systemctl stop postgresql
sudo systemctl enable postgresql
sudo systemctl status postgresql
```

Notice after `enable` — the `disabled` changes to `enabled` but it's still not running. Enable just means "start on boot" — it doesn't start it right now.

To start it now AND on every boot:
```bash
sudo systemctl enable --now postgresql
```

Tell me what you see.

```zsh
> sudo systemctl enable --now postgresql
[sudo] password for kijuchihe:
Synchronizing state of postgresql.service with SysV service script with /usr/lib/systemd/systemd-sysv-install.
Executing: /usr/lib/systemd/systemd-sysv-install enable postgresql
Created symlink /etc/systemd/system/multi-user.target.wants/postgresql.service → /usr/lib/systemd/system/postgresql.service.
> sudo systemctl status postgresql
● postgresql.service - PostgreSQL RDBMS
     Loaded: loaded (/usr/lib/systemd/system/postgresql.service; enabled; prese>
     Active: active (exited) since Tue 2026-05-12 09:04:46 GMT; 28s ago
    Process: 21931 ExecStart=/bin/true (code=exited, status=0/SUCCESS)
   Main PID: 21931 (code=exited, status=0/SUCCESS)
        CPU: 1ms
May 12 09:04:46 kingsley-pc systemd[1]: Starting postgresql.service - PostgreSQ>
May 12 09:04:46 kingsley-pc systemd[1]: Finished postgresql.service - PostgreSQ>
~                                                           took 3s at 09:05:18
>
```

Notice something interesting — it says `active (exited)`. That's different from `active (running)`.

| Status | Meaning |
|---|---|
| `active (running)` | process is alive and running right now |
| `active (exited)` | ran successfully but the process itself exited — it was a one-shot task |
| `active (waiting)` | running but waiting for an event |

PostgreSQL's main systemd unit is just a wrapper — the actual database processes are managed separately. Run:

```bash
sudo systemctl status postgresql@16-main
```

That's the real postgres instance. You'll see the actual running process there.

---

Also notice this line:
```
Created symlink /etc/systemd/system/multi-user.target.wants/postgresql.service → /usr/lib/systemd/system/postgresql.service
```

That's how `enable` works under the hood — it creates a symlink in the target directory. When systemd boots into `multi-user.target` (normal system operation), it starts everything symlinked in that folder.

---

Now disable it so it doesn't run on every boot since you don't always need it:

```bash
sudo systemctl disable --now postgresql
```

Ready to move into writing your own service unit file?