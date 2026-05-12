## SSH — Secure Shell

SSH lets you remotely control another Linux machine through an encrypted terminal session. Every server you deploy to, every cloud instance you spin up — you access via SSH.

---

### Basic usage

```bash
ssh username@ip-address
ssh username@domain.com
ssh -p 2222 username@ip-address    # if server uses non-standard port
```

---

### How it works

```
Your machine                    Remote server
    │                               │
    │──── encrypted connection ─────│
    │                               │
    └── you type commands here      └── they run here
```

Everything is encrypted. Nobody on the network can see what you're typing or what the server responds.

---

### Password vs Key authentication

Two ways to authenticate:

**Password** — simple but weak. Every hacker on the internet will try to brute force it.

**SSH Keys** — the right way. A key pair:
- **Private key** — stays on your machine, never shared with anyone
- **Public key** — placed on the server

When you connect, the server checks if your private key matches the public key it has. No password needed.

```
Your machine          Server
private key    ←→    public key
```

---

### Generate an SSH key pair

```bash
ssh-keygen -t ed25519 -C "your@email.com"
```

| Flag | Meaning |
|---|---|
| `-t ed25519` | key type — ed25519 is modern and secure |
| `-t rsa` | older type, still widely used |
| `-b 4096` | key size in bits (for RSA) |
| `-C` | comment — usually your email for identification |

It'll ask where to save — press Enter for default (`~/.ssh/id_ed25519`).
It'll ask for a passphrase — adds extra security, optional.

---

### After generating

```bash
ls ~/.ssh/
```

You'll see:
| File | What it is |
|---|---|
| `id_ed25519` | your private key — never share this |
| `id_ed25519.pub` | your public key — this goes on servers |
| `known_hosts` | servers you've connected to before |
| `authorized_keys` | public keys allowed to connect to this machine |

---

### Copy your public key to a server

```bash
ssh-copy-id username@server-ip
```

This appends your public key to `~/.ssh/authorized_keys` on the server. After this you connect without a password.

---

### SSH config file

Instead of typing `ssh kijuchihe@192.168.2.103 -p 22` every time, create `~/.ssh/config`:

```bash
nano ~/.ssh/config
```

```
Host myserver
    HostName 192.168.2.103
    User kijuchihe
    Port 22
    IdentityFile ~/.ssh/id_ed25519

Host itc
    HostName itconsortiumgh.com
    User kingsley
    Port 22
    IdentityFile ~/.ssh/id_ed25519
```

Now connect with just:
```bash
ssh myserver
ssh itc
```

---

### Hardening SSH on a server

When you set up a server, first thing you do is edit `/etc/ssh/sshd_config`:

```bash
sudo nano /etc/ssh/sshd_config
```

Key settings to change:

```ini
Port 2222                        # change from default 22 — reduces bot attacks
PermitRootLogin no               # never allow root to SSH in directly
PasswordAuthentication no        # force key-only authentication
PubkeyAuthentication yes         # enable key auth
MaxAuthTries 3                   # only 3 attempts before disconnect
```

After editing:
```bash
sudo systemctl restart ssh
```

---

### Useful SSH tricks

```bash
# run a single command on remote server without full session
ssh user@server "ls -la /var/log"

# copy files to remote server
scp file.txt user@server:/path/to/destination

# copy files from remote server
scp user@server:/path/to/file.txt .

# copy entire directory
scp -r folder/ user@server:/path/

# SSH tunnel — forward remote port to local
ssh -L 8080:localhost:80 user@server
```

---

Run these now:

```bash
ssh-keygen -t ed25519 -C "your email"
ls ~/.ssh/
cat ~/.ssh/id_ed25519.pub
```


Here's the list:

**SSH — Return to later (when you have a remote server)**
1. SSH tunneling & port forwarding
2. Jump hosts / bastion servers
3. SSH agent forwarding
4. `tmux` over SSH — persistent sessions
5. Fail2ban — auto-blocking brute force attempts
6. SSH certificates — large scale access management