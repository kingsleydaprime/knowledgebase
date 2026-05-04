## Package Management

When you need software on Linux, you don't go to a website and download an installer like Windows. You use a **package manager** — it handles downloading, installing, updating, and removing software from centralized **repositories**.

On Ubuntu you use **apt** (Advanced Package Tool).

---

### The basics

```bash
sudo apt update                  # refresh the list of available packages
sudo apt upgrade                 # install available updates
sudo apt install package-name    # install a package
sudo apt remove package-name     # remove a package
sudo apt purge package-name      # remove + delete its config files
sudo apt autoremove              # remove unused dependencies
sudo apt search package-name     # search for a package
apt show package-name            # see details about a package
sudo apt list --upgradable       # see packages that can be upgraded
```

---

### Important distinction

`apt update` does **not** install anything — it just syncs the package list from repositories. Always run it before installing anything.

```bash
sudo apt update && sudo apt install htop
```

---

### Where do packages come from?

The repository sources are defined in:
```bash
cat /etc/apt/sources.list
ls /etc/apt/sources.list.d/
```

That's where apt knows where to look online for packages.

---

Run:
```bash
cat /etc/apt/sources.list
```

And also:
```bash
apt show curl
```

Tell me what you see from `apt show curl`.

```zsh
> cat /etc/apt/sources.list
# Ubuntu sources have moved to /etc/apt/sources.list.d/ubuntu.sources

> apt show curl
Package: curl
Version: 8.5.0-2ubuntu10.8
Priority: optional
Section: web
Origin: Ubuntu
Maintainer: Ubuntu Developers <[ubuntu-devel-discuss@lists.ubuntu.com](mailto:ubuntu-devel-discuss@lists.ubuntu.com)>
Original-Maintainer: Debian Curl Maintainers <[team+curl@tracker.debian.org](mailto:team+curl@tracker.debian.org)>
Bugs: https://bugs.launchpad.net/ubuntu/+filebug
Installed-Size: 534 kB
Depends: libc6 (>= 2.34), libcurl4t64 (= 8.5.0-2ubuntu10.8), zlib1g (>= 1:1.1.4)
Homepage: https://curl.se/
Task: cloud-minimal, cloud-image, cloud-image, server-minimal, ubuntu-wsl, server, ubuntu-server-raspi, lubuntu-desktop, ubuntustudio-publishing, ubuntu-budgie-desktop-minimal, ubuntu-budgie-desktop, ubuntu-budgie-desktop-raspi
Download-Size: 227 kB
APT-Manual-Installed: yes
APT-Sources: http://ng.archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages
Description: command line tool for transferring data with URL syntax
 curl is a command line tool for transferring data with URL syntax,
 supporting DICT, FILE, FTP, FTPS, GOPHER, HTTP, HTTPS, IMAP, IMAPS, LDAP,
 LDAPS, POP3, POP3S, RTMP, RTSP, SCP, SFTP, SMTP, SMTPS, TELNET and TFTP.
 .
 curl supports SSL certificates, HTTP POST, HTTP PUT, FTP uploading, HTTP
 form based upload, proxies, cookies, user+password authentication (Basic,
 Digest, NTLM, Negotiate, kerberos...), file transfer resume, proxy
 tunneling and a busload of other useful tricks.
N: There is 1 additional record. Please use the '-a' switch to see it
```

Good. A few things worth noting from that output:

**Dependencies:**
```
Depends: libc6, libcurl4t64, zlib1g
```
curl doesn't work alone — it needs these libraries. apt handles installing them automatically. That's the whole point of a package manager.

**APT-Sources:**
```
http://ng.archive.ubuntu.com/ubuntu noble-updates/main
```
That `ng` means you're hitting the Nigerian Ubuntu mirror. apt picked the closest server geographically. Since you're in Ghana it might be worth pointing to a closer mirror but not critical.

**APT-Manual-Installed: yes** — means you explicitly installed curl yourself, not pulled in as a dependency.

---

### One more useful command

```bash
dpkg -l | grep package-name    # check if something is installed
which curl                     # shows where the binary lives
whereis curl                   # shows binary + docs + source locations
```

Run:
```bash
which curl
whereis curl
dpkg -l | grep curl
```

---

After this we move into something you'll use constantly — **file operations and text manipulation**. Things like reading files, searching through them, editing them from the terminal. That's where `cat`, `grep`, `sed`, `awk`, `find` live — the real Linux power tools.

Tell me what those three commands return first.
