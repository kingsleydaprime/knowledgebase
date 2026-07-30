# Access Network-Attached Storage

> RHCSA V10

Part of [[README|RHCSA V10]]. RHCSA tests the **client** side of this — mounting storage that lives on another machine — not standing up an NFS server yourself.

---

## NFS — Network File System

The standard way Linux machines share filesystems with each other over the network. RHEL 10 defaults to **NFSv4.2**, though NFSv3 is still fully supported — worth knowing there are two, because how you *discover* what a server exports is genuinely different between them, not just a version number.

```bash
sudo dnf install nfs-utils          # client tooling, if not already present
```

**NFSv3** exports are queried with `showmount`, which relies on the legacy RPC protocol (`rpcbind`, listening on port 111 — this is *why* NFS needs more than one firewall service opened, see below):
```bash
showmount -e nfs-server.example.com
```
```
Export list for nfs-server.example.com:
/exports/data    192.168.1.0/24
```

**NFSv4** drops the RPC/`rpcbind` dependency entirely and instead exposes a single **export tree** — mount the server's root export to browse what's available, rather than querying it:
```bash
mkdir /mnt/browse
mount nfs-server.example.com:/ /mnt/browse    # mounts the export TREE, not any actual data
ls /mnt/browse                                  # browse it like a directory listing to see what's exported
```
Since this is what RHEL 10 actually defaults to, don't assume `showmount` is guaranteed to work against a modern server — if it comes back empty or refuses to connect, mounting the root export to browse it is the NFSv4-native alternative, not a sign anything's broken.

### Mounting

```bash
sudo mkdir -p /mnt/nfsdata
sudo mount -t nfs nfs-server.example.com:/exports/data /mnt/nfsdata
```

### Persistent — /etc/fstab

```
nfs-server.example.com:/exports/data   /mnt/nfsdata   nfs   defaults,_netdev   0   0
```

`_netdev` tells the boot process this mount needs the network to be up first — without it, the system can try to mount an NFS share before networking has even initialized and hang or fail at boot. This is the single most important option to remember for a network filesystem entry, distinct from the local-disk fstab entries covered in [[08-maintain-basic-storage|maintain-basic-storage]].

Test before trusting it to survive a reboot, same discipline as any fstab edit:
```bash
sudo mount -a
```

### "device is busy" — unmounting a share still in use

`umount` refuses if anything is still using the mount — an open file, or just a shell with its working directory sitting inside it. Find out what, rather than guessing:
```bash
lsof /mnt/nfsdata
```
```
COMMAND  PID  USER   FD  TYPE DEVICE  SIZE/OFF  NODE NAME
program 5534  user  txt  REG  252,4    910704   128  /mnt/nfsdata/file
```
Close whatever's listed (or `cd` out of the mount if it's just a shell sitting in it) and retry. Only if nothing else works — and only understanding this risks losing unwritten data for any file still open — force it:
```bash
sudo umount -f /mnt/nfsdata
```

---

## autofs — mount on demand instead of at boot

Mounting every NFS share at boot means the boot process can hang or fail if a remote server is briefly unreachable. **autofs** solves this by mounting a share automatically the first time something accesses its path, and unmounting it again after a period of inactivity — nothing is mounted at boot at all.

```bash
sudo dnf install autofs
```

### Indirect maps — the common case

`/etc/auto.master` maps a base directory to a map file:
```
/mnt/auto    /etc/auto.misc
```

`/etc/auto.misc` then defines what goes under that base, keyed by the subdirectory name that triggers the mount:
```
data    -rw,soft    nfs-server.example.com:/exports/data
```
Accessing `/mnt/auto/data` triggers autofs to mount `nfs-server.example.com:/exports/data` there on the fly. It disappears again after the configured idle timeout (`/etc/autofs.conf`, default 10 minutes).

### Direct maps — less common, exact path control

Defined straight in `/etc/auto.master` with a `/-` map:
```
/-    /etc/auto.direct
```
```
/mnt/exact/path    -ro    nfs-server.example.com:/exports/readonly
```
Here the mount point is the *exact* path, not a base directory with keyed subdirectories.

```bash
sudo systemctl enable --now autofs      # apply and persist across reboots
```

---

## SMB/CIFS — briefly

**SMB (Server Message Block)** — and **CIFS (Common Internet File System)**, an older dialect of the same protocol — is the Windows-world equivalent of NFS. Same idea, different protocol, for completeness:
```bash
sudo dnf install cifs-utils
sudo mount -t cifs //server/share /mnt/smb -o credentials=/root/.smbcreds
```
`/root/.smbcreds` holds `username=`/`password=` so a plaintext password never ends up sitting directly in `/etc/fstab` (which is world-readable).

---

## Firewall

A share that mounts fine from the server's own shell but times out from a client is very often just the firewall on the server side — see [[12-manage-network-security|manage-network-security]]:
```bash
sudo firewall-cmd --add-service=nfs --permanent
sudo firewall-cmd --reload
```
