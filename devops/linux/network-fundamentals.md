## Networking Fundamentals

Before commands, you need to understand the concepts.

---

### IP Addresses

Every device on a network has an IP address — its unique identifier.

Two types:
- **Private IP** — only valid inside your local network (192.168.x.x, 10.x.x.x) — what your WiFi router assigns you
- **Public IP** — your address on the internet — what the world sees

Your machine right now:
- Private: `192.168.2.103` (we saw this in sysinfo)
- Public: whatever your router's IP is

---

### Ports

An IP address gets you to a machine. A port gets you to a specific service on that machine.

Think of it like:
```
IP address = building address
Port       = apartment number
```

Common ports worth memorizing:

| Port | Service |
|---|---|
| 22 | SSH |
| 80 | HTTP |
| 443 | HTTPS |
| 3000 | Node/React dev servers |
| 5432 | PostgreSQL |
| 6379 | Redis |
| 27017 | MongoDB |
| 3306 | MySQL |
| 5672 | RabbitMQ |
| 8080 | Alternative HTTP |

---

### DNS

Domain Name System — translates human names to IP addresses.

```
google.com → 142.250.185.46
```

Your machine asks a DNS server "what's the IP for google.com?" and gets back an address it can connect to.

Local DNS mappings live in:
```bash
cat /etc/hosts
```

---

### OSI Model

How network communication is structured in layers:

| Layer | Name | What it does | Example |
|---|---|---|---|
| 7 | Application | What the user interacts with | HTTP, FTP, SSH |
| 6 | Presentation | Encryption, compression | TLS, SSL |
| 5 | Session | Managing connections | Sockets |
| 4 | Transport | End to end delivery, ports | TCP, UDP |
| 3 | Network | Routing between networks | IP |
| 2 | Data Link | Device to device on same network | Ethernet, WiFi |
| 1 | Physical | Actual cables and signals | Cables, radio waves |

---

### TCP vs UDP

| | TCP | UDP |
|---|---|---|
| Connection | Yes — handshake first | No — just sends |
| Reliable | Yes — guarantees delivery | No — fire and forget |
| Speed | Slower | Faster |
| Use case | HTTP, SSH, databases | Video streaming, DNS, gaming |

---

Run these and tell me what you see:

```bash
cat /etc/hosts
cat /etc/resolv.conf
```

> Results of my own commands

```txt
> cat /etc/hosts | head -30
# Title: StevenBlack/hosts with the porn extension
#
# This hosts file is a merged collection of hosts from reputable sources,
# with a dash of crowd sourcing via GitHub
#
# Date: 15 December 2025 23:58:48 (UTC)
# Extensions added to this file: porn
# Number of unique domains: 162,289
#
# Fetch the latest version of this file: https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/porn/hosts
# Project home page: https://github.com/StevenBlack/hosts
# Project releases: https://github.com/StevenBlack/hosts/releases
#
# ===============================================================
127.0.0.1 localhost
127.0.0.1 localhost.localdomain
127.0.0.1 local
255.255.255.255 broadcasthost
::1 localhost
::1 ip6-localhost
::1 ip6-loopback
fe80::1%lo0 localhost
ff00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
ff02::3 ip6-allhosts
0.0.0.0 0.0.0.0
```

Interesting. You're using **StevenBlack's hosts file** — a popular ad and porn blocker that works by redirecting 162,289 domains to `0.0.0.0` (nowhere). Solid setup.

This is exactly how hosts-based blocking works — before your browser even makes a DNS request, your OS checks `/etc/hosts` first. If the domain is there pointing to `0.0.0.0`, the request dies immediately. No DNS query ever leaves your machine.

A few entries worth understanding:

| Entry | Meaning |
|---|---|
| `127.0.0.1 localhost` | your machine's loopback |
| `::1 localhost` | same but IPv6 |
| `255.255.255.255 broadcasthost` | network broadcast address |
| `0.0.0.0 0.0.0.0` | null route — blocked domains point here |

---

Now run:
```bash
cat /etc/resolv.conf
```

And also:
```bash
# test DNS resolution
nslookup google.com

# trace the full route to google
traceroute google.com

# check if a host is reachable
ping -c 4 google.com
```

> Another result

```txt
> cat /etc/resolv.conf
# This is /run/systemd/resolve/stub-resolv.conf managed by man:systemd-resolved(8).
# Do not edit.
#
# This file might be symlinked as /etc/resolv.conf. If you're looking at
# /etc/resolv.conf and seeing this text, you have followed the symlink.
#
# This is a dynamic resolv.conf file for connecting local clients to the
# internal DNS stub resolver of systemd-resolved. This file lists all
# configured search domains.
#
# Run "resolvectl status" to see details about the uplink DNS servers
# currently in use.
#
# Third party programs should typically not access this file directly, but only
# through the symlink at /etc/resolv.conf. To manage man:resolv.conf(5) in a
# different way, replace this symlink by a static file or a different symlink.
#
# See man:systemd-resolved.service(8) for details about the supported modes of
# operation for /etc/resolv.conf.
nameserver 127.0.0.53
options edns0 trust-ad
search .
```

Notice `nameserver 127.0.0.53` — that's not an external DNS server. That's **systemd-resolved** running locally on your machine as a DNS stub resolver.

So your DNS flow is:
```
Your app → 127.0.0.53 (systemd-resolved) → actual DNS server upstream
```

To see what the actual upstream DNS servers are:
```bash
resolvectl status
```

---

Now run the other three:
```bash
nslookup google.com
ping -c 4 google.com
traceroute google.com
```

My response
```sh
> nslookup google.com
ping -c 4 google.com
traceroute google.com
Server:		127.0.0.53
Address:	127.0.0.53#53
Non-authoritative answer:
Name:	google.com
Address: 172.217.22.78
Name:	google.com
Address: 2a00:1450:4007:80a::200e
PING google.com (172.217.22.78) 56(84) bytes of data.
64 bytes from tlv04s05-in-f14.1e100.net (172.217.22.78): icmp_seq=1 ttl=113 time=118 ms
64 bytes from tlv04s05-in-f14.1e100.net (172.217.22.78): icmp_seq=2 ttl=113 time=160 ms
64 bytes from tlv04s05-in-f14.1e100.net (172.217.22.78): icmp_seq=3 ttl=113 time=112 ms
64 bytes from tlv04s05-in-f14.1e100.net (172.217.22.78): icmp_seq=4 ttl=113 time=163 ms
--- google.com ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3000ms
rtt min/avg/max/mdev = 112.370/138.428/163.049/23.251 ms
traceroute to google.com (172.217.22.78), 30 hops max, 60 byte packets
 1  _gateway (192.168.2.1)  26.059 ms  26.961 ms  26.954 ms
 2  unifi.prime.itconsortiumgh.com (172.20.40.1)  26.934 ms  26.911 ms  26.889 ms
 3  156.0.235.1 (156.0.235.1)  26.858 ms  26.826 ms  26.799 ms
 4  10.11.12.2 (10.11.12.2)  26.780 ms  26.756 ms  26.780 ms
 5  156.0.234.1 (156.0.234.1)  26.756 ms  26.739 ms  26.710 ms
 6  45.222.212.73 (45.222.212.73)  26.692 ms  10.249 ms *
 7  41.75.80.26 (41.75.80.26)  134.207 ms 41.75.94.246 (41.75.94.246)  134.288 ms  134.197 ms
 8  41.75.80.26 (41.75.80.26)  134.200 ms  134.074 ms 41.75.94.246 (41.75.94.246)  134.094 ms
 9  154.113.219.9 (154.113.219.9)  133.993 ms  134.107 ms  134.053 ms
10  172.253.176.219 (172.253.176.219)  134.046 ms  133.838 ms 172.253.176.227 (172.253.176.227)  26.352 ms
11  192.178.248.60 (192.178.248.60)  133.866 ms 66.249.94.90 (66.249.94.90)  133.801 ms 192.178.248.60 (192.178.248.60)  133.817 ms
12  192.178.108.185 (192.178.108.185)  135.956 ms 192.178.80.81 (192.178.80.81)  107.305 ms 192.178.108.185 (192.178.108.185)  101.888 ms
13  172.253.76.39 (172.253.76.39)  117.870 ms 172.253.76.33 (172.253.76.33)  117.769 ms 172.253.76.39 (172.253.76.39)  117.737 ms
14  209.85.255.107 (209.85.255.107)  117.591 ms 72.14.238.54 (72.14.238.54)  116.430 ms 192.178.252.188 (192.178.252.188)  117.464 ms
15  108.170.255.239 (108.170.255.239)  116.513 ms 192.178.104.29 (192.178.104.29)  112.965 ms 108.170.255.239 (108.170.255.239)  113.206 ms
16  142.251.64.131 (142.251.64.131)  129.823 ms  116.546 ms 142.251.64.129 (142.251.64.129)  119.761 ms
17  fra15s17-in-f78.1e100.net (172.217.22.78)  116.180 ms  119.654 ms  119.852 ms
~
```


This is gold. You can see your entire network path to Google.

**nslookup told you:**
- `127.0.0.53` handled the query (systemd-resolved)
- Google's IPv4: `172.217.22.78`
- Google's IPv6: `2a00:1450:4007:80a::200e`

**ping told you:**
- 0% packet loss — clean connection
- ~138ms average — you're in Accra hitting a Google server, that latency is expected

**traceroute told you the full journey:**

```
Your machine
  → 192.168.2.1          (your WiFi router)
  → 172.20.40.1          (itconsortiumgh.com — IT Consortium's network)
  → 156.0.235.1          (ISP)
  → ...several ISP hops...
  → 41.75.x.x            (African backbone — latency jumps here to 134ms)
  → 154.113.x.x          (peering point)
  → 172.253.x.x          (Google's network — you're inside Google now)
  → 172.217.22.78        (Google's server)
```

You can literally see your traffic leaving IT Consortium's network, hitting the African internet backbone, entering Google's network, and arriving at the destination. 17 hops total.

---

Now the practical networking commands you'll use constantly:

```bash
# see your network interfaces and IPs
ip addr

# see routing table
ip route

# see active connections and listening ports
ss -tulnp

# check if a port is open on a remote host
nc -zv google.com 443

# your public IP
curl ifconfig.me
```

Seems like 172 usually means an internal network

Good observation but not exactly.

`172.x.x.x` doesn't automatically mean internal. It depends on the range:

**Private ranges** (internal networks only):
```
10.0.0.0    – 10.255.255.255
172.16.0.0  – 172.31.255.255      ← only this specific range
192.168.0.0 – 192.168.255.255
```

So `172.16.x.x` to `172.31.x.x` = private. But `172.217.x.x` (Google's IP) is way outside that range — that's a fully public IP.

In your traceroute:
- `172.20.40.1` — private (IT Consortium's internal network, falls in 172.16-31 range)
- `172.217.22.78` — public (Google)
- `172.253.x.x` — public (Google's backbone)

The pattern to memorize:
```
10.x.x.x        → always private
172.16-31.x.x   → private
192.168.x.x     → always private
everything else → public
```

These are defined by **RFC 1918** — the standard that reserved these ranges for private use.

Let's talk about what `ss -tulnp` showed you since that's the most important one for DevOps.

Run it again and paste the output:

```bash
ss -tulnp
```

```zsh
> ss -tulnp
Netid  State    Recv-Q   Send-Q      Local Address:Port      Peer Address:Port  Process
udp    UNCONN   0        0           192.168.122.1:53             0.0.0.0:*     
udp    UNCONN   0        0              127.0.0.54:53             0.0.0.0:*     
udp    UNCONN   0        0           127.0.0.53%lo:53             0.0.0.0:*     
udp    UNCONN   0        0          0.0.0.0%virbr0:67             0.0.0.0:*     
udp    UNCONN   0        0                 0.0.0.0:42575          0.0.0.0:*      users:(("zen",pid=3594,fd=249))
udp    UNCONN   0        0                 0.0.0.0:53117          0.0.0.0:*      users:(("zen",pid=3594,fd=367))
udp    UNCONN   0        0                 0.0.0.0:5353           0.0.0.0:*     
udp    UNCONN   0        0                 0.0.0.0:38582          0.0.0.0:*     
udp    UNCONN   0        0                    [::]:53297             [::]:*     
udp    UNCONN   0        0                    [::]:5353              [::]:*     
tcp    LISTEN   0        4096           127.0.0.54:53             0.0.0.0:*     
tcp    LISTEN   0        4096            127.0.0.1:631            0.0.0.0:*     
tcp    LISTEN   0        32          192.168.122.1:53             0.0.0.0:*     
tcp    LISTEN   0        4096        127.0.0.53%lo:53             0.0.0.0:*     
tcp    LISTEN   0        4096                [::1]:631               [::]:*     
tcp    LISTEN   0        4096                    *:4369                 *:*
```

Let's decode this.

**The flags you used:**

| Flag | Meaning |
|---|---|
| `-t` | show TCP |
| `-u` | show UDP |
| `-l` | show listening ports only |
| `-n` | show numbers not names |
| `-p` | show which process owns it |

---

**What's listening on your machine:**

| Port | Protocol | What it is |
|---|---|---|
| `53` | UDP+TCP | DNS — three instances (systemd-resolved, virbr0, 127.0.0.54) |
| `67` | UDP | DHCP server — your VM network handing out IPs |
| `631` | TCP | CUPS — your printer service |
| `4369` | TCP | epmd — Erlang port mapper (RabbitMQ uses this) |
| `5353` | UDP | mDNS — local network discovery |

**Zen browser** is using two random UDP ports (`42575`, `53117`) — WebRTC for video/audio.

---

Key insight for DevOps — when you deploy a service and it's not working, first thing you check:

```bash
ss -tulnp | grep 8080    # is my app actually listening?
ss -tulnp | grep 5432    # is postgres up?
```

If nothing shows up — your service isn't running. If it shows `127.0.0.1` instead of `0.0.0.0` — it's only accepting local connections, not external ones.

---

## Firewalls - ufw

A firewall controls what network traffic is allowed in and out of your machine. On Ubuntu the tool is **ufw** (Uncomplicated Firewall) — a frontend for the more complex `iptables` underneath.

---

### Basic commands

```bash
sudo ufw status                  # check if firewall is on and see rules
sudo ufw enable                  # turn on firewall
sudo ufw disable                 # turn off firewall
sudo ufw status verbose          # detailed view
```

---

### Allowing and blocking

```bash
sudo ufw allow 22                # allow SSH
sudo ufw allow 80                # allow HTTP
sudo ufw allow 443               # allow HTTPS
sudo ufw allow 5432              # allow PostgreSQL
sudo ufw deny 3306               # block MySQL from outside
sudo ufw allow from 192.168.1.0/24    # allow entire subnet
sudo ufw allow from 192.168.1.5       # allow specific IP only
```

---

### By service name instead of port

```bash
sudo ufw allow ssh               # same as allow 22
sudo ufw allow http              # same as allow 80
sudo ufw allow https             # same as allow 443
```

---

### Removing rules

```bash
sudo ufw delete allow 80
sudo ufw delete deny 3306
```

---

### Default policies

```bash
sudo ufw default deny incoming   # block all incoming by default
sudo ufw default allow outgoing  # allow all outgoing by default
```

This is the standard server setup — deny everything coming in, then explicitly open only what you need.

---

Run:
```bash
sudo ufw status verbose
```

Result
```zsh
> sudo ufw status verbose
[sudo] password for kijuchihe:
Status: inactive
```

```txt
You said entire subnet. What is the subnet.
Why would you want to allow a specific IP? Oh oh. Like when a request is coming from that particular ip right?
```

Both questions — yes exactly. You only allow a specific IP when you want to restrict access to trusted sources. Example: only allow your office IP to connect to your database. Anyone else gets blocked even if they know the port.

---

**Subnet** — a subdivision of a network.

Your home/office network isn't just one device — it's many. A subnet groups them together under one address range.

Your IP is `192.168.2.103`. Your subnet is probably `192.168.2.0/24` — meaning all devices from `192.168.2.1` to `192.168.2.254` are on the same network.

The `/24` is called **CIDR notation** — it tells you how many devices the subnet can hold:

| CIDR | Hosts available | Example |
|---|---|---|
| `/32` | 1 — single IP | `192.168.1.5/32` |
| `/24` | 254 | `192.168.1.0/24` |
| `/16` | 65,534 | `192.168.0.0/16` |
| `/8` | 16 million | `10.0.0.0/8` |

The number after `/` = how many bits are the network part. The rest = host addresses.

---

**Your firewall is inactive.** For a personal machine that's fine. On a server — first thing you'd do is:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw enable
```

In that exact order — if you enable before allowing SSH, you'll lock yourself out of a remote server permanently.

---

Ready to move into **systemd and services** — how Linux manages background services like nginx, postgres, redis?
