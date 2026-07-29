## Cron Jobs

Cron is the Linux task scheduler. It runs commands automatically at specified times — every minute, every day, every Monday at 3am, whatever you need.

---

### Crontab

Each user has their own crontab file — a list of scheduled tasks.

```bash
crontab -e      # edit your crontab
crontab -l      # list your current cron jobs
crontab -r      # delete all your cron jobs
```

---

### Cron syntax

Every line in a crontab follows this format:

```
* * * * * command
│ │ │ │ │
│ │ │ │ └── day of week (0-7, 0 and 7 = Sunday)
│ │ │ └──── month (1-12)
│ │ └────── day of month (1-31)
│ └──────── hour (0-23)
└────────── minute (0-59)
```

---

### Examples

```bash
# every minute
* * * * * command

# every day at midnight
0 0 * * * command

# every day at 3am
0 3 * * * command

# every Monday at 9am
0 9 * * 1 command

# every 15 minutes
*/15 * * * * command

# every hour
0 * * * * command

# first day of every month at noon
0 12 1 * * command

# every weekday at 8am
0 8 * * 1-5 command
```

`*` means "every". `/15` means "every 15".

---

### Real example — log your system info every minute

```bash
crontab -e
```

Add this line:

```bash
* * * * * /bin/bash /home/kijuchihe/sysinfo.sh >> /home/kijuchihe/sysinfo.log 2>&1
```

Save and exit. Then watch it run:

```bash
watch -n 5 tail /home/kijuchihe/sysinfo.log
```

`watch -n 5` reruns the command every 5 seconds so you see it update live.

Wait about a minute and tell me what you see.

```log
Every 5.0s: tail /home/kijuchihe/sysinfo.log                                                       kingsley-pc: Tue May 12 09:27:19 2026
kijuchi+   20236  6.7    /snap/firefox/8274/usr/lib/firefox/firefox
kijuchi+   12446  6.6    /snap/firefox/8274/usr/lib/firefox/firefox
Network Interfaces:
lo 127.0.0.1/8
eno1
wlo1 192.168.2.107/24
virbr0 192.168.122.1/24
================================
```

Cron is working. Your sysinfo script ran automatically and logged its output.

---

A few practical things:

**Always use full paths in cron** — cron runs with a minimal environment, it doesn't know your `PATH`. So never write:
```bash
* * * * * sysinfo.sh          # wrong — cron can't find it
* * * * * /bin/bash /home/kijuchihe/sysinfo.sh   # correct
```

**Redirect output or it gets lost:**
```bash
>> /path/to/file.log 2>&1    # append stdout and stderr to log
> /dev/null 2>&1             # discard everything silently
```

**System-wide cron jobs** live in:
```bash
/etc/crontab          # system crontab
/etc/cron.d/          # drop-in cron files
/etc/cron.daily/      # scripts that run daily
/etc/cron.hourly/     # scripts that run hourly
/etc/cron.weekly/     # scripts that run weekly
/etc/cron.monthly/    # scripts that run monthly
```

---

Now remove that cron job so it stops logging every minute:

```bash
crontab -e
```

Delete the line, save and exit.

---

You've now covered:
- ✅ crontab — edit, list, remove
- ✅ Cron syntax
- ✅ Logging cron output
- ✅ Full paths rule

---

Last topic for Week 1 — **SSH**. This is arguably the most important tool for DevOps. Every server you'll ever touch, you access via SSH. Ready?