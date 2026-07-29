# Access Network-Attached Storage

> RHCSA V10

Part of [[README|RHCSA V10]]. RHCSA tests the **client** side of this — mounting storage that lives on another machine — not standing up an NFS server yourself.

---

## NFS — Network File System

The standard way Linux machines share filesystems with each other over the network.

```bash
sudo dnf install nfs-utils          # client tooling, if not already present

showmount -e nfs-server.example.com # list what that server is EXPORTING (sharing) before mounting anything
```

```
Export list for nfs-server.example.com:
/exports/data    192.168.1.0/24
```

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

Same idea, Windows-world protocol, for completeness:
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
