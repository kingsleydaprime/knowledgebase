## Users & Groups

Linux is a multi-user system. From day one it was designed for many people using one machine simultaneously. Everything ties back to that.

---

### Users

Every process, every file, every action on the system is tied to a user.

There are three types:

| Type | Description | Example |
|---|---|---|
| Root user | Superuser — unlimited access to everything | `root` (UID 0) |
| Regular users | Normal humans with limited access | `kingsley`, `alice` |
| System users | Created by the OS for running services, not for humans to log into | `www-data` (nginx), `postgres` |

---

### See all users on the system

```bash
cat /etc/passwd
```

Each line looks like:
```
kingsley:x:1000:1000::/home/kingsley:/bin/bash
```

Breaking it down:
```
username : password : UID : GID : comment : home dir : shell
```

- `x` in the password field means password is stored in `/etc/shadow` (hashed, not plaintext)
- **UID** = User ID (root is always 0, regular users start at 1000 on Ubuntu)
- **GID** = primary Group ID

---

### Groups

A group is just a collection of users. Used to give shared permissions to multiple people.

```bash
cat /etc/group    # see all groups
groups            # see which groups YOUR user belongs to
id                # see your UID, GID, and all your groups
```

---

```zsh
> cat /etc/passwd
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:100:102:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin
systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin
messagebus:x:102:105::/nonexistent:/usr/sbin/nologin
systemd-timesync:x:103:106:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin
syslog:x:104:111::/home/syslog:/usr/sbin/nologin
_apt:x:105:65534::/nonexistent:/usr/sbin/nologin
tss:x:106:113:TPM software stack,,,:/var/lib/tpm:/bin/false
uuidd:x:107:116::/run/uuidd:/usr/sbin/nologin
systemd-oom:x:108:117:systemd Userspace OOM Killer,,,:/run/systemd:/usr/sbin/nologin
tcpdump:x:109:118::/nonexistent:/usr/sbin/nologin
usbmux:x:111:46:usbmux daemon,,,:/var/lib/usbmux:/usr/sbin/nologin
dnsmasq:x:112:65534:dnsmasq,,,:/var/lib/misc:/usr/sbin/nologin
kernoops:x:113:65534:Kernel Oops Tracking Daemon,,,:/:/usr/sbin/nologin
avahi:x:114:121:Avahi mDNS daemon,,,:/run/avahi-daemon:/usr/sbin/nologin
cups-pk-helper:x:115:122:user for cups-pk-helper service,,,:/home/cups-pk-helper:/usr/sbin/nologin
rtkit:x:116:123:RealtimeKit,,,:/proc:/usr/sbin/nologin
whoopsie:x:117:124::/nonexistent:/bin/false
sssd:x:118:125:SSSD system user,,,:/var/lib/sss:/usr/sbin/nologin
speech-dispatcher:x:119:29:Speech Dispatcher,,,:/run/speech-dispatcher:/bin/false
fwupd-refresh:x:120:126:fwupd-refresh user,,,:/run/systemd:/usr/sbin/nologin
nm-openvpn:x:121:127:NetworkManager OpenVPN,,,:/var/lib/openvpn/chroot:/usr/sbin/nologin
saned:x:122:129::/var/lib/saned:/usr/sbin/nologin
colord:x:123:130:colord colour management daemon,,,:/var/lib/colord:/usr/sbin/nologin
geoclue:x:124:131::/var/lib/geoclue:/usr/sbin/nologin
pulse:x:125:132:PulseAudio daemon,,,:/run/pulse:/usr/sbin/nologin
gnome-initial-setup:x:126:65534::/run/gnome-initial-setup/:/bin/false
hplip:x:127:7:HPLIP system user,,,:/run/hplip:/bin/false
gdm:x:128:134:Gnome Display Manager:/var/lib/gdm3:/bin/false
kijuchihe:x:1000:1000:Kingsley Ihemelandu,,,:/home/kijuchihe:/usr/bin/zsh
mongodb:x:129:65534::/home/mongodb:/usr/sbin/nologin
dhcpcd:x:130:65534:DHCP Client Daemon,,,:/usr/lib/dhcpcd:/bin/false
cups-browsed:x:131:122::/nonexistent:/usr/sbin/nologin
polkitd:x:999:999:User for polkitd:/:/usr/sbin/nologin
gnome-remote-desktop:x:996:996:GNOME Remote Desktop:/var/lib/gnome-remote-desktop:/usr/sbin/nologin
swtpm:x:110:140:virtual TPM software stack,,,:/var/lib/swtpm:/bin/false
libvirt-qemu:x:64055:109:Libvirt Qemu,,,:/var/lib/libvirt:/usr/sbin/nologin
libvirt-dnsmasq:x:132:142:Libvirt Dnsmasq,,,:/var/lib/libvirt/dnsmasq:/usr/sbin/nologin
postgres:x:133:143:PostgreSQL administrator,,,:/var/lib/postgresql:/bin/bash
redis:x:134:144::/var/lib/redis:/usr/sbin/nologin
mysql:x:135:145:MySQL Server,,,:/nonexistent:/bin/false
dcmtk:x:136:146::/var/lib/dcmtk/db:/usr/sbin/nologin
epmd:x:137:147::/run/epmd:/usr/sbin/nologin
rabbitmq:x:138:148:RabbitMQ messaging server,,,:/var/lib/rabbitmq:/usr/sbin/nologin
snapd-range-524288-root:x:524288:524288::/nonexistent:/usr/bin/false
snap_daemon:x:584788:584788::/nonexistent:/usr/bin/false
nvidia-persistenced:x:139:150:NVIDIA Persistence Daemon,,,:/nonexistent:/usr/sbin/nologin
minioadmin:x:998:994::/home/minioadmin:/bin/sh
```


Your `/etc/passwd` tells a story about your machine. A few things worth pointing out:

**Your user:**
```
kijuchihe:x:1000:1000:Kingsley Ihemelandu,,,:/home/kijuchihe:/usr/bin/zsh
```
UID 1000 — first real human user on the machine. And you're using **zsh** not bash.

**Your stack is visible here:**
```
postgres:x:133:143:...
redis:x:134:144:...
mysql:x:135:145:...
mongodb:x:129:...
rabbitmq:x:138:148:...
```
Every service you've installed created its own system user. That's Linux security — services run as their own isolated user, not as you or root.

**Notice the shells:**
- `/usr/sbin/nologin` — these users can't log in. They're just for running services.
- `/bin/false` — same, even more restrictive.
- `/bin/bash`, `/usr/bin/zsh` — actual humans.

---

Now run:

```bash
id
groups
```

Tell me what comes back.

**BTW `passwd` means Password file.**

Historical name. Originally it stored actual passwords in plaintext. Then that became an obvious security disaster, so passwords got moved to `/etc/shadow` (which is hashed and only root can read).

The name `passwd` stuck even though passwords aren't really there anymore — just that `x` placeholder.

Run `sudo cat /etc/shadow` and you'll see the actual hashed passwords.

```zsh
> id
uid=1000(kijuchihe) gid=1000(kijuchihe) groups=1000(kijuchihe),4(adm),20(dialout),24(cdrom),27(sudo),30(dip),46(plugdev),122(lpadmin),135(lxd),136(sambashare),141(libvirt)
> groups
kijuchihe adm dialout cdrom sudo dip plugdev lpadmin lxd sambashare libvirt
>
```

```txt
How do I change my username?
How can I add a user to a group.
I'm seeing sudo in groups, so I'm guessing it is a group I can add a user to.
How do I change the name of my pc in linux from say kingsley-pc to something else.
```

Your sudo observation was sharp — that's exactly how privilege escalation works on Linux. `sudo` isn't magic, it's just a group. Any user in it can run commands as root. That's worth understanding deeply.

---

### Change your username
```bash
sudo usermod -l newname oldname
```
Also rename the home directory:
```bash
sudo usermod -d /home/newname -m newname
```

| Flag | Meaning | Example |
|---|---|---|
| `-l` | new login name | `sudo usermod -l kingsley kijuchihe` |
| `-d` | new home directory path | `sudo usermod -d /home/kingsley kijuchihe` |
| `-m` | move contents of old home dir to new one | `sudo usermod -d /home/kingsley -m kijuchihe` |
| `-u` | change UID | `sudo usermod -u 1001 kijuchihe` |
| `-s` | change default shell | `sudo usermod -s /bin/bash kijuchihe` |
| `-e` | set account expiry date | `sudo usermod -e 2026-12-31 kijuchihe` |
| `-L` | lock the account | `sudo usermod -L kijuchihe` |
| `-U` | unlock the account | `sudo usermod -U kijuchihe` |

---

### Add a user to a group
```bash
sudo usermod -aG groupname username
```
So to give a user sudo access:
```bash
sudo usermod -aG sudo username
```
Log out and back in for group changes to take effect.

| Flag | Meaning | Example |
|---|---|---|
| `-a` | append — add to group without removing from others | `sudo usermod -aG docker kijuchihe` |
| `-G` | specify supplementary groups | `sudo usermod -G sudo,docker kijuchihe` |
| `-g` | change primary group | `sudo usermod -g developers kijuchihe` |

---

### Remove a user from a group
```bash
sudo gpasswd -d username groupname
```

| Flag | Meaning | Example |
|---|---|---|
| `-d` | delete user from group | `sudo gpasswd -d kijuchihe docker` |
| `-a` | add user to group | `sudo gpasswd -a kijuchihe docker` |
| `-M` | set the full member list of a group | `sudo gpasswd -M kingsley,alice developers` |
| `-A` | set group administrators | `sudo gpasswd -A kingsley developers` |

---

### Change your PC hostname
```bash
sudo hostnamectl set-hostname new-name
```
Verify:
```bash
hostnamectl
```
Also update `/etc/hosts` or your terminal might show weird warnings:
```bash
sudo nano /etc/hosts
```
Find the line with your old hostname and replace it with the new one. Then reboot.

| Subcommand | Meaning | Example |
|---|---|---|
| `set-hostname` | set the system hostname | `sudo hostnamectl set-hostname spectroniq-dev` |
| `status` | show current hostname and related info | `hostnamectl status` |
| `set-icon-name` | set icon name for the machine | `sudo hostnamectl set-icon-name computer-laptop` |
| `set-chassis` | set chassis type | `sudo hostnamectl set-chassis laptop` |
| `set-location` | set physical location of the machine | `sudo hostnamectl set-location "Accra, Ghana"` |
