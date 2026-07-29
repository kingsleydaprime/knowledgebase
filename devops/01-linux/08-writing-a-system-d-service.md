## Writing a systemd Service

A service unit file tells systemd how to run your program — what to execute, when to start, what to do if it crashes.

---

Unit files live in `/etc/systemd/system/`. Create one:

```bash
sudo nano /etc/systemd/system/myapp.service
```

Paste this:

```ini
[Unit]
Description=My First Service
After=network.target

[Service]
Type=simple
User=kijuchihe
WorkingDirectory=/home/kijuchihe
ExecStart=/bin/bash /home/kijuchihe/sysinfo.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

### What each section means

**[Unit]**

| Option | Meaning |
|---|---|
| `Description` | human readable name |
| `After` | start this service only after network is up |
| `Requires` | hard dependency — if it fails, this fails too |
| `Wants` | soft dependency — start it but don't fail if it doesn't |

**[Service]**

| Option | Meaning |
|---|---|
| `Type=simple` | process stays running (use for servers) |
| `Type=oneshot` | runs once and exits (use for scripts) |
| `User` | which user to run as |
| `WorkingDirectory` | where to run from |
| `ExecStart` | the actual command to run |
| `ExecStop` | command to run on stop |
| `Restart=on-failure` | restart if it crashes |
| `Restart=always` | restart no matter what |
| `RestartSec=5` | wait 5 seconds before restarting |
| `Environment` | set environment variables |
| `EnvironmentFile` | load env vars from a file |

**[Install]**

| Option | Meaning |
|---|---|
| `WantedBy=multi-user.target` | start during normal system boot |

---

Now run it:

```bash
# reload systemd so it sees the new file
sudo systemctl daemon-reload

# start it
sudo systemctl start myapp

# check status
sudo systemctl status myapp
```

Tell me what you see.

```zsh
○ myapp.service - My First Service
     Loaded: loaded (/etc/systemd/system/myapp.service; disabled; preset: enabled)
     Active: inactive (dead)

May 12 09:13:14 kingsley-pc bash[23593]: kijuchi+   17269  12.2   /snap/firefox/8274/usr/lib/firefox/firefox
May 12 09:13:14 kingsley-pc bash[23593]: kijuchi+   3434   12.1   /snap/firefox/8274/usr/lib/firefox/firefox
May 12 09:13:14 kingsley-pc bash[23593]: kijuchi+   20236  11.5   /snap/firefox/8274/usr/lib/firefox/firefox
May 12 09:13:14 kingsley-pc bash[23571]: Network Interfaces:
May 12 09:13:14 kingsley-pc bash[23595]: lo 127.0.0.1/8
May 12 09:13:14 kingsley-pc bash[23595]: eno1
May 12 09:13:14 kingsley-pc bash[23595]: wlo1 192.168.2.107/24
May 12 09:13:14 kingsley-pc bash[23595]: virbr0 192.168.122.1/24
May 12 09:13:14 kingsley-pc bash[23571]: ================================
May 12 09:13:14 kingsley-pc systemd[1]: myapp.service: Deactivated successfully.
```

Perfect. It worked.

`inactive (dead)` is correct for a `oneshot` service — it ran, finished, and exited cleanly. "Deactivated successfully" confirms it.

You can also see your sysinfo script output right there in the systemd logs — that's because systemd captures everything a service prints to stdout and stores it in the **journal**.

Which leads perfectly into the next thing:

```bash
journalctl -u myapp          # all logs for your service
journalctl -u myapp -f       # follow live
journalctl -u myapp --since "10 minutes ago"
journalctl -xe               # last logs with explanations — useful for debugging
journalctl -b                # logs since last boot
```

Run:
```bash
journalctl -u myapp
```

You'll see the full output of your sysinfo script captured by systemd. This is exactly how you debug services on a real server — no guessing, everything is logged.

Tell me what you see.

```zsh
> journalctl -u myapp
May 12 09:11:13 kingsley-pc systemd[1]: Started myapp.service - My First Service.
May 12 09:11:13 kingsley-pc bash[23145]: /bin/bash: /home/kijuchihe/sysinfo.sh: No such file or directory
May 12 09:11:13 kingsley-pc systemd[1]: myapp.service: Main process exited, code=exited, status=127/n/a
May 12 09:11:13 kingsley-pc systemd[1]: myapp.service: Failed with result 'exit-code'.
May 12 09:11:18 kingsley-pc systemd[1]: myapp.service: Scheduled restart job, restart counter is at 1.
May 12 09:11:18 kingsley-pc systemd[1]: Started myapp.service - My First Service.
May 12 09:11:18 kingsley-pc bash[23152]: /bin/bash: /home/kijuchihe/sysinfo.sh: No such file or directory
May 12 09:11:18 kingsley-pc systemd[1]: myapp.service: Main process exited, code=exited, status=127/n/a
May 12 09:11:18 kingsley-pc systemd[1]: myapp.service: Failed with result 'exit-code'.
May 12 09:11:23 kingsley-pc systemd[1]: myapp.service: Scheduled restart job, restart counter is at 2.
May 12 09:11:23 kingsley-pc systemd[1]: Started myapp.service - My First Service.
May 12 09:11:23 kingsley-pc bash[23169]: /bin/bash: /home/kijuchihe/sysinfo.sh: No such file or directory
May 12 09:11:23 kingsley-pc systemd[1]: myapp.service: Main process exited, code=exited, status=127/n/a
May 12 09:11:23 kingsley-pc systemd[1]: myapp.service: Failed with result 'exit-code'.
May 12 09:11:29 kingsley-pc systemd[1]: myapp.service: Scheduled restart job, restart counter is at 3.
May 12 09:11:29 kingsley-pc systemd[1]: Started myapp.service - My First Service.
May 12 09:11:29 kingsley-pc bash[23179]: /bin/bash: /home/kijuchihe/sysinfo.sh: No such file or directory
May 12 09:11:29 kingsley-pc systemd[1]: myapp.service: Main process exited, code=exited, status=127/n/a
May 12 09:11:29 kingsley-pc systemd[1]: myapp.service: Failed with result 'exit-code'.
May 12 09:11:34 kingsley-pc systemd[1]: myapp.service: Scheduled restart job, restart counter is at 4.
May 12 09:11:34 kingsley-pc systemd[1]: Started myapp.service - My First Service.
May 12 09:11:34 kingsley-pc bash[23220]: /bin/bash: /home/kijuchihe/sysinfo.sh: No such file or directory
May 12 09:11:34 kingsley-pc systemd[1]: myapp.service: Main process exited, code=exited, status=127/n/a
May 12 09:11:34 kingsley-pc systemd[1]: myapp.service: Failed with result 'exit-code'.
May 12 09:11:39 kingsley-pc systemd[1]: myapp.service: Scheduled restart job, restart counter is at 5.
May 12 09:11:39 kingsley-pc systemd[1]: Started myapp.service - My First Service.
May 12 09:11:39 kingsley-pc bash[23229]: /bin/bash: /home/kijuchihe/sysinfo.sh: No such file or directory
May 12 09:11:39 kingsley-pc systemd[1]: myapp.service: Main process exited, code=exited, status=127/n/a
May 12 09:11:39 kingsley-pc systemd[1]: myapp.service: Failed with result 'exit-code'.
May 12 09:11:44 kingsley-pc systemd[1]: myapp.service: Scheduled restart job, restart counter is at 6.
May 12 09:11:44 kingsley-pc systemd[1]: Started myapp.service - My First Service.
May 12 09:11:44 kingsley-pc bash[23240]: /bin/bash: /home/kijuchihe/sysinfo.sh: No such file or directory
May 12 09:11:44 kingsley-pc systemd[1]: myapp.service: Main process exited, code=exited, status=127/n/a
```

This is a perfect real-world debugging lesson.

You can see exactly what happened:
1. Service started
2. Couldn't find `sysinfo.sh`
3. Failed with exit code 127
4. `Restart=on-failure` kicked in every 5 seconds
5. Same failure, over and over — restart counter climbing 1, 2, 3, 4, 5, 6...

This is how you debug any service on a real server. The journal tells you exactly what went wrong and when.

---

This is also why `Restart=always` can be dangerous on a broken service — it'll hammer your system in a crash loop. Always pair it with:

```ini
StartLimitIntervalSec=60
StartLimitBurst=5
```

That stops systemd from restarting more than 5 times in 60 seconds.

---

You've now covered:
- ✅ systemctl — start, stop, restart, enable, disable
- ✅ Writing unit files
- ✅ Service types — simple, oneshot
- ✅ journalctl — reading logs
- ✅ Debugging a failed service

---

Next is **cron jobs** — scheduling tasks to run automatically at specific times. Then after that we wrap up Week 1 with **SSH**. Ready?