## Docker — The Big Picture

Before commands, you need to understand what Docker actually is and why it exists.

---

### The problem it solves

You've definitely experienced this:
```
"It works on my machine"
```

Your app works locally but breaks on the server. Why? Different OS, different Node version, different library versions, different environment variables.

Docker solves this by packaging your app and everything it needs — runtime, dependencies, config — into one unit called a **container**. That container runs identically everywhere.

---

### Virtual Machines vs Containers

You might think "that's just a VM." It's not.

| | Virtual Machine | Container |
|---|---|---|
| Includes | Full OS + kernel | Just the app + dependencies |
| Size | GBs | MBs |
| Startup | Minutes | Seconds |
| Resource usage | Heavy | Lightweight |
| Isolation | Complete | Process-level |

A VM virtualizes hardware. A container virtualizes the OS — it shares your kernel but isolates everything else.

---

### Core concepts

| Concept | What it is |
|---|---|
| **Image** | Blueprint — read only template for creating containers |
| **Container** | Running instance of an image |
| **Dockerfile** | Instructions for building an image |
| **Registry** | Storage for images (Docker Hub, AWS ECR) |
| **Volume** | Persistent storage for containers |
| **Network** | How containers communicate |

The relationship:
```
Dockerfile → build → Image → run → Container
```

Like programming:
```
Class → instantiate → Object
Image → run        → Container
```

---

### How containers work under the hood

Remember processes? A container is essentially just a process with three Linux kernel features applied:

| Feature | What it does |
|---|---|
| **Namespaces** | Isolates — container has its own PID tree, network, filesystem |
| **Cgroups** | Limits — controls how much CPU/RAM the container can use |
| **Union filesystem** | Layers — images are built in layers, containers add a writable layer on top |

Docker didn't invent anything new — it just packaged existing Linux kernel features into a developer-friendly tool.

---

Check if Docker is installed:

```bash
docker --version
docker info
```

Tell me what you see.

```zsh
> sudo docker info
Client: Docker Engine - Community
 Version:    29.4.2
 Context:    default
 Debug Mode: false
 Plugins:
  buildx: Docker Buildx (Docker Inc.)
    Version:  v0.33.0
    Path:     /usr/libexec/docker/cli-plugins/docker-buildx
  compose: Docker Compose (Docker Inc.)
    Version:  v5.1.3
    Path:     /usr/libexec/docker/cli-plugins/docker-compose
Server:
 Containers: 5
  Running: 0
  Paused: 0
  Stopped: 5
 Images: 19
 Server Version: 29.4.2
 Storage Driver: overlay2
  Backing Filesystem: extfs
  Supports d_type: true
  Using metacopy: false
  Native Overlay Diff: true
  userxattr: false
 Logging Driver: json-file
 Cgroup Driver: systemd
 Cgroup Version: 2
 Plugins:
  Volume: local
  Network: bridge host ipvlan macvlan null overlay
  Log: awslogs fluentd gcplogs gelf journald json-file local splunk syslog
 CDI spec directories:
  /etc/cdi
  /var/run/cdi
 Swarm: inactive
 Runtimes: io.containerd.runc.v2 runc
 Default Runtime: runc
 Init Binary: docker-init
 containerd version: 77c84241c7cbdd9b4eca2591793e3d4f4317c590
 runc version: v1.3.5-0-g488fc13e
 init version: de40ad0
 Security Options:
  apparmor
  seccomp
   Profile: builtin
  cgroupns
 Kernel Version: 6.8.0-111-generic
 Operating System: Ubuntu 24.04.4 LTS
 OSType: linux
 Architecture: x86_64
 CPUs: 4
 Total Memory: 15.55GiB
 Name: kingsley-pc
 ID: 5a80ece0-ebc1-4605-9737-2604b3707550
 Docker Root Dir: /var/lib/docker
 Debug Mode: false
 Experimental: false
 Insecure Registries:
  ::1/128
  127.0.0.0/8
 Live Restore Enabled: false
 Firewall Backend: iptables
~
```

Good. You already have 19 images and 5 stopped containers from previous work.

A few things worth noting from that output:

**Storage driver: overlay2** — this is the union filesystem we talked about. It's how Docker layers images on top of each other.

**Cgroup Driver: systemd** — Docker is using systemd's cgroup management. Remember cgroups — resource limiting for containers. This means Docker integrates directly with systemd for that.

**Security: apparmor + seccomp** — two Linux security layers Docker uses to restrict what containers can do.

**Runc** — the actual container runtime underneath Docker. Docker is just a friendly interface — `runc` is what actually talks to the kernel to create containers.

**Network plugins you have:**
`bridge host ipvlan macvlan null overlay` — we'll cover what each does.

---

Since you've used Docker before let's move fast. Run:

```bash
docker images
docker ps -a
```

Show me what images and containers you already have — that'll tell me how deep you've gone before and we'll pick up from there rather than starting from zero.

Solid background. Traefik + Grafana means you've done reverse proxy and monitoring setup — that's beyond basic.

We'll still cover everything from the ground up for your notes, but we'll move faster and go deeper where it matters.

---

## Docker Basics

### The core workflow

```
Write Dockerfile → Build Image → Run Container → Push to Registry
```

### Your first container

```bash
docker run hello-world
```

That single command did five things:
1. Looked for `hello-world` image locally
2. Didn't find it → pulled from Docker Hub
3. Created a container from the image
4. Ran the container
5. Container printed its message and exited

---

### docker run flags

```bash
docker run image                      # run a container
docker run -d image                   # detached — runs in background
docker run -it image                  # interactive — gives you a terminal
docker run -p 8080:80 image           # map host port 8080 to container port 80
docker run -e KEY=value image         # set environment variable
docker run -v /host/path:/container   # mount a volume
docker run --name mycontainer image   # give it a name
docker run --rm image                 # delete container after it exits
docker run --network mynetwork image  # connect to a network
```

---

### Managing containers

```bash
docker ps                    # running containers
docker ps -a                 # all containers including stopped
docker start container       # start a stopped container
docker stop container        # graceful stop
docker kill container        # force stop
docker rm container          # delete container
docker rm -f container       # force delete running container
docker logs container        # see container logs
docker logs -f container     # follow logs live
docker exec -it container bash   # get shell inside running container
docker inspect container     # full details in JSON
```

---

### Managing images

```bash
docker images                # list images
docker pull image:tag        # download image
docker rmi image             # delete image
docker rmi -f image          # force delete
docker image prune           # delete unused images
docker system prune          # delete everything unused
docker history image         # see image layers
docker inspect image         # full image details
```

---

Try these:

```bash
docker run -it ubuntu:latest bash
```

This pulls Ubuntu and drops you into a shell inside the container. Once inside:

```bash
ls /
cat /etc/os-release
ps aux
exit
```

Tell me what you notice about the process list inside the container vs your host.

```txt
Also what is the difference between images and containers?
```

Same relationship as what we covered with classes and objects — or executables and processes.

```
Image     = the blueprint. Static. Read-only. Lives on disk.
Container = a running instance of that image. Live. Has its own writable layer.
```

More concretely:

| | Image | Container |
|---|---|---|
| State | Static | Running/stopped |
| Writable | No | Yes — but changes are lost when deleted |
| Stored | `/var/lib/docker/images` | `/var/lib/docker/containers` |
| Created by | `docker build` | `docker run` |
| Can have multiple | — | Yes — run 10 containers from one image |

The key insight — **one image, many containers.** You can spin up 10 postgres containers from the same `postgres:15-alpine` image. Each gets its own isolated writable layer on top, but they all share the same base image underneath.

When you `docker stop` a container — the container still exists, just stopped. Your writable layer is preserved.
When you `docker rm` a container — it's gone. Anything written inside that wasn't in a volume is lost forever.

That's why volumes exist — to persist data outside the container's lifecycle.

Now run that ubuntu container and tell me what the process list looks like inside.

```txt
I've run it. Similar processes but much fewer after the first process compared to mine
```

Exactly. That's the whole point of containers.

Inside the container you probably saw something like:

```
PID   COMMAND
1     bash
10    ps aux
```

That's it. Two processes.

On your host you have hundreds. But inside the container — it only sees its own isolated process tree. PID 1 inside the container is just bash, not systemd.

This is **PID namespace isolation** at work — one of the kernel features we mentioned. The container has its own PID namespace. It thinks it's the only thing running. It can't see your host processes at all.

Same isolation applies to:
- **Network** — container has its own network interfaces
- **Filesystem** — container has its own root `/`
- **Users** — container has its own user IDs

That's why when you ran `ls /` inside the Ubuntu container, you saw a full Linux filesystem — but it's not your filesystem. It's the container's isolated view.

---

One more thing to try. On your host run:

```bash
docker run -d --name myubuntu ubuntu:latest sleep 1000
docker inspect myubuntu | grep -i pid
```

You'll see the container's PID from the host's perspective — proof that it's just a regular Linux process on your machine with isolation applied on top.

Tell me what PID you see.

```What am I supposed to see?```

You'll see something like:

```json
"Pid": 45231
```

That's the container's main process PID as seen from your host. Then run:

```bash
ps aux | grep 45231
```

You'll see it's just a regular `sleep 1000` process on your host — with a normal PID. But inside the container, that same process thinks its PID is 1.

Same process, two different PID views — host sees 45231, container sees 1. That's namespace isolation in action.

Run it and tell me what you see.

Yhh I saw that.
Perfect. That's the most important mental model for containers:

**A container is just a Linux process with namespaces and cgroups applied. Nothing magical.**

Docker's genius was packaging that complexity into a simple CLI.

---

Clean up:

```bash
docker stop myubuntu
docker rm myubuntu
```

---

## Docker Images & Layers

Every image is built in layers. Each instruction in a Dockerfile creates a new layer.

```
Layer 4: COPY app files        ← your code
Layer 3: RUN npm install       ← dependencies  
Layer 2: RUN apt update        ← system packages
Layer 1: FROM ubuntu:22.04     ← base image
```

Layers are cached. If layer 2 hasn't changed, Docker reuses it from cache — makes builds fast.

See the layers of any image:

```bash
docker history postgres:15-alpine
docker history mongo:latest
```

Notice each layer has a size. The total image size is all layers combined.

---

Key insight about layer caching — **order matters in your Dockerfile.**

Put things that change least at the top, things that change most at the bottom:

```dockerfile
FROM node:20-alpine        # rarely changes
WORKDIR /app
COPY package.json .        # changes occasionally
RUN npm install            # expensive — cache this
COPY . .                   # changes constantly — put last
```

If you put `COPY . .` before `npm install`, every code change busts the cache and reinstalls all dependencies. Expensive.

---

Run:
```bash
docker history redis:alpine
```

Tell me how many layers you see and which is the largest.

```zsh
> sudo docker history redis:alpine
[sudo] password for kijuchihe:
IMAGE          CREATED       CREATED BY                                      SIZE      COMMENT
13b871aaf97f   3 weeks ago   CMD ["redis-server"]                            0B        buildkit.dockerfile.v0
<missing>      3 weeks ago   EXPOSE map[6379/tcp:{}]                         0B        buildkit.dockerfile.v0
<missing>      3 weeks ago   ENTRYPOINT ["docker-entrypoint.sh"]             0B        buildkit.dockerfile.v0
<missing>      3 weeks ago   COPY docker-entrypoint.sh /usr/local/bin/ # …   4.85kB    buildkit.dockerfile.v0
<missing>      3 weeks ago   WORKDIR /data                                   0B        buildkit.dockerfile.v0
<missing>      3 weeks ago   RUN |2 REDIS_DOWNLOAD_URL=https://github.com…   0B        buildkit.dockerfile.v0
<missing>      3 weeks ago   RUN |2 REDIS_DOWNLOAD_URL=https://github.com…   88.2MB    buildkit.dockerfile.v0
<missing>      3 weeks ago   ARG REDIS_DOWNLOAD_SHA=cef021615ec4aef355a82…   0B        buildkit.dockerfile.v0
<missing>      3 weeks ago   ARG REDIS_DOWNLOAD_URL=https://github.com/re…   0B        buildkit.dockerfile.v0
<missing>      3 weeks ago   RUN /bin/sh -c set -eux;  apk add --no-cache…   568kB     buildkit.dockerfile.v0
<missing>      3 weeks ago   RUN /bin/sh -c set -eux;  addgroup -S -g 100…   3.05kB    buildkit.dockerfile.v0
<missing>      3 weeks ago   CMD ["/bin/sh"]                                 0B        buildkit.dockerfile.v0
<missing>      3 weeks ago   ADD alpine-minirootfs-3.23.4-x86_64.tar.gz /…   8.45MB    buildkit.dockerfile.v0
~                                                           took 4s at 16:23:18
>
```

13 layers. Let's read it bottom to top — that's the actual build order:

```
ADD alpine-minirootfs...     8.45MB   ← base Alpine Linux
CMD ["/bin/sh"]              0B       ← default shell
addgroup/adduser             3.05kB   ← create redis user
apk add --no-cache           568kB    ← install dependencies
ARG REDIS_DOWNLOAD_URL       0B       ← build arguments (no size)
ARG REDIS_DOWNLOAD_SHA       0B       ← build arguments (no size)
RUN download & compile       88.2MB   ← the actual Redis binary ← BIGGEST
RUN cleanup                  0B       ← cleanup (deleted files)
WORKDIR /data                0B       ← create data directory
COPY entrypoint.sh           4.85kB   ← startup script
ENTRYPOINT                   0B       ← how container starts
EXPOSE 6379                  0B       ← document the port
CMD ["redis-server"]         0B       ← default command
```

Key observations:

**88.2MB** is the biggest layer — compiling Redis from source.

**0B layers** — instructions like `CMD`, `EXPOSE`, `ENTRYPOINT` don't add size. They're just metadata.

**The cleanup layer is 0B** — this is a common gotcha. If you `RUN apt install something` then `RUN rm -rf /var/cache` in separate layers, the files still exist in the previous layer. To actually reduce size you must chain commands:

```dockerfile
# Wrong — cleanup doesn't actually reduce image size
RUN apt install something
RUN rm -rf /var/cache

# Correct — single layer, actually reduces size
RUN apt install something && rm -rf /var/cache
```

---

Now let's write a Dockerfile. Create a simple Node.js app:

```bash
mkdir ~/docker-practice && cd ~/docker-practice
```

Create `app.js`:
```bash
nano app.js
```

```javascript
const http = require('http');

const server = http.createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
        message: 'Hello from Docker',
        hostname: require('os').hostname(),
        timestamp: new Date().toISOString()
    }));
});

server.listen(3000, () => {
    console.log('Server running on port 3000');
});
```

Create `package.json`:
```bash
nano package.json
```

```json
{
    "name": "docker-practice",
    "version": "1.0.0",
    "main": "app.js"
}
```

Now create the `Dockerfile`:
```bash
nano Dockerfile
```

```dockerfile
# Base image
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files first (layer caching)
COPY package.json .

# Install dependencies
RUN npm install

# Copy rest of code
COPY . .

# Document the port
EXPOSE 3000

# Start command
CMD ["node", "app.js"]
```

Build and run it:
```bash
docker build -t docker-practice .
docker run -d -p 3000:3000 --name myapp docker-practice
curl http://localhost:3000
```

Tell me what you get.