## Multi-Stage Builds

The problem with a basic Dockerfile — your final image contains everything used to build the app. Compilers, build tools, dev dependencies — none of that is needed to run the app. It just bloats the image.

Multi-stage builds fix this. You use one stage to build, another stage to run — only copying the compiled output across.

---

### Example — without multi-stage

```dockerfile
FROM node:20                  # full Node image ~1GB
WORKDIR /app
COPY package.json .
RUN npm install               # includes devDependencies
COPY . .
RUN npm run build
CMD ["node", "dist/index.js"]
```

Final image: ~1GB+ — contains Node, npm, all source files, devDependencies, build tools.

---

### Same app — with multi-stage

```dockerfile
# ─── Stage 1: Builder ────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json .
RUN npm install               # installs everything including devDeps
COPY . .
RUN npm run build             # compiles the app

# ─── Stage 2: Runner ────────────────────────────
FROM node:20-alpine AS runner
WORKDIR /app
COPY package.json .
RUN npm install --omit=dev    # production dependencies only
COPY --from=builder /app/dist ./dist    # copy ONLY the build output
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

Final image: fraction of the size — no build tools, no devDependencies, no source files.

---

### The key instruction

```dockerfile
COPY --from=builder /app/dist ./dist
```

`--from=builder` pulls files from the previous stage. The builder stage gets discarded entirely — it never makes it into the final image.

---

### Real world example — Go app

Go is the best example because it compiles to a single binary:

```dockerfile
# ─── Stage 1: Build ──────────────────────────────
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum .
RUN go mod download
COPY . .
RUN go build -o server .

# ─── Stage 2: Run ────────────────────────────────
FROM alpine:latest AS runner
WORKDIR /app
COPY --from=builder /app/server .
EXPOSE 8080
CMD ["./server"]
```

Builder image: ~300MB (Go compiler + source)
Final image: ~10MB (just the binary + Alpine)

That's a 30x size reduction.

---

### You can go even smaller — scratch

```dockerfile
FROM scratch    # literally empty — no OS at all
COPY --from=builder /app/server .
CMD ["./server"]
```

Final image: just the binary. A few MB. Only works for statically compiled languages like Go or Rust.

---

Update your `docker-practice` Dockerfile to use multi-stage. Since it's plain Node with no build step, simulate it like this:

```dockerfile
# ─── Stage 1: Install all deps ───────────────────
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .

# ─── Stage 2: Production ─────────────────────────
FROM node:20-alpine AS runner
WORKDIR /app
COPY package.json .
RUN npm install --omit=dev
COPY --from=builder /app/app.js .
EXPOSE 3000
CMD ["node", "app.js"]
```

Build it:
```bash
docker stop myapp && docker rm myapp
docker build -t docker-practice .
docker images | grep docker-practice
```

Tell me the image size.

```zsh
sudo docker stop myapp && sudo docker rm myapp
sudo docker build -t docker-practice .
sudo docker images | grep docker-practice
Error response from daemon: No such container: myapp
[+] Building 14.6s (12/12) FINISHED                              docker:default
 => [internal] load build definition from Dockerfile                       0.2s
 => => transferring dockerfile: 492B                                       0.0s
 => [internal] load metadata for docker.io/library/node:20-alpine          1.3s
 => [internal] load .dockerignore                                          0.2s
 => => transferring context: 2B                                            0.0s
 => [internal] load build context                                          0.2s
 => => transferring context: 549B                                          0.0s
 => [builder 1/5] FROM docker.io/library/node:20-alpine@sha256:fb4cd12c85  0.0s
 => CACHED [builder 3/5] COPY package.json .                               0.0s
 => CACHED [builder 2/5] WORKDIR /app                                      0.0s
 => CACHED [builder 4/5] RUN npm install                                   0.0s
 => [runner 4/5] RUN npm install --omit=dev                                7.3s
 => [builder 5/5] COPY . .                                                 2.5s
 => [runner 5/5] COPY --from=builder /app/app.js .                         2.1s
 => exporting to image                                                     1.4s
 => => exporting layers                                                    0.9s
 => => writing image sha256:d85ff59cfb55844c3e64a45eefce321b950df0be13ba1  0.1s
 => => naming to docker.io/library/docker-practice                         0.1s
docker-practice:latest   d85ff59cfb55        136MB             0B
WARNING: This output is designed for human readability. For machine-readable output, please use --format.
~/docker-practice                                          took 15s at 16:37:07
>
```

Good — multi-stage build worked. You can see both stages in the output:

```
[builder 1/5] ... 
[runner 4/5] ...
```

But size is still 136MB — same as before. That's because this app has no devDependencies and no build step, so there's nothing to cut. The multi-stage pattern doesn't help much here.

The real gains show with:
- TypeScript projects — compile TS → JS, discard TS compiler
- Go/Rust — compile to binary, discard entire compiler
- React — build static files, discard node_modules entirely

---

To actually see the size difference, check the base image size:

```bash
docker images | grep node
```

You'll see `node:20-alpine` is ~140MB. Your app adds almost nothing on top — it's a tiny script with no real dependencies.

---

One important thing to add to every Dockerfile — `.dockerignore`. Same concept as `.gitignore` — stops unnecessary files from being copied into the image:

```bash
nano .dockerignore
```

```
node_modules
.env
*.log
.git
README.md
```

Without this, `COPY . .` copies `node_modules` from your host into the build context — slow and pointless since you `RUN npm install` inside anyway.

---

Ready to move into Docker networking?