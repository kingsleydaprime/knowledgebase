## Symbolic Links

A symlink is a pointer to another file or directory. Like a shortcut on Windows but more powerful — the OS treats it as if it were the actual file.

```bash
# create a symlink
ln -s /path/to/original /path/to/link

# example
ln -s /home/kijuchihe/sysinfo.sh /usr/local/bin/sysinfo
```

Now you can run `sysinfo` from anywhere instead of `./sysinfo.sh`.

---

### View symlinks

```bash
ls -la /bin | head -5       # see symlinks in /bin
ls -la /usr/bin/python3     # check if python3 is a symlink
```

The `->` arrow shows what it points to:
```
lrwxrwxrwx  python3 -> python3.12
```

The `l` at the start of permissions = symlink.

---

### Remove a symlink

```bash
unlink /path/to/link       # correct way
rm /path/to/link           # also works but be careful with directories
```

Never use `rm -r` on a symlink to a directory — it'll delete the actual directory contents.

---

### Hard link vs Soft link

| | Soft link (symlink) | Hard link |
|---|---|---|
| Points to | file path | file data directly |
| Works across filesystems | yes | no |
| If original deleted | link breaks | data still accessible |
| Used for | almost everything | rarely |

---

Try this:

```bash
# create a symlink to sysinfo.sh
ln -s /home/kijuchihe/sysinfo.sh ~/sysinfo-link.sh

# run it through the symlink
./sysinfo-link.sh

# check it
ls -la | grep sysinfo
```

Tell me what you see.

```zsh
> ln -s /home/kijuchihe/sysinfo.sh ~/sysinfo-link.sh
> ./sysinfo-link.sh
zsh: no such file or directory: ./sysinfo-link.sh
> cd ~
> ./sysinfo-link.sh
================================
       SYSTEM INFORMATION
================================
Basic Info:
Hostname:    kingsley-pc
User:        kijuchihe
Date:        Tue 12 May 2026 09:56:36 GMT
Uptime:      up 5 hours, 7 minutes
CPU:
Model:       Intel(R) Core(TM) i7-4500U CPU @ 1.80GHz
Cores:       4
Load avg:    2.53 1.49 1.29
Memory:
Used: 6.9Gi / Total: 15Gi (Free: 3.3Gi)
Disk:
Used: 199G / Total: 916G (23% used)
Top 5 Processes (CPU):
USER       PID    %CPU   COMMAND
kijuchi+   28439  200    ps
kijuchi+   17269  16.2   /snap/firefox/8274/usr/lib/firefox/firefox
kijuchi+   3434   11.8   /snap/firefox/8274/usr/lib/firefox/firefox
kijuchi+   3394   5.8    /proc/self/exe
kijuchi+   12446  5.5    /snap/firefox/8274/usr/lib/firefox/firefox
Network Interfaces:
lo 127.0.0.1/8
eno1
wlo1 192.168.2.107/24
virbr0 192.168.122.1/24
================================
> ls -la | grep sysinfo
lrwxrwxrwx   1 kijuchihe kijuchihe        26 May 12 09:56 sysinfo-link.sh -> /home/kijuchihe/sysinfo.sh
-rw-rw-r--   1 kijuchihe kijuchihe     31813 May 12 09:56 sysinfo.log
-rwxrwxr-x   1 kijuchihe kijuchihe      2215 May  5 08:04 sysinfo.sh
~                                                                   at 09:56:49
>
```

Working perfectly.

Notice in the `ls -la` output:
```
lrwxrwxrwx  sysinfo-link.sh -> /home/kijuchihe/sysinfo.sh
```
- `l` at the start = symlink
- `->` shows exactly what it points to
- `lrwxrwxrwx` — symlinks always show full permissions, the actual permissions are controlled by the target file

---

The first failure was because you weren't in your home directory — `~/sysinfo-link.sh` created it in `~` but you were running `./sysinfo-link.sh` from a different directory. Good catch fixing it with `cd ~`.

---

You've now completed everything for Week 1:

✅ OS concepts & kernel
✅ Boot process
✅ Filesystem hierarchy
✅ Permissions & ownership
✅ Users & groups
✅ Process management
✅ Package management
✅ File operations & text manipulation
✅ Shell scripting
✅ Networking fundamentals
✅ systemd & services
✅ Cron jobs
✅ SSH
✅ Environment variables
✅ Symbolic links

---

Ready for Docker?