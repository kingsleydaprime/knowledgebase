## Docker Volumes

Containers are ephemeral — when you delete a container, everything written inside it is gone. Volumes solve this by storing data outside the container lifecycle.

---

### Three types of storage

```
┌─────────────────────────────────────────┐
│           Host Machine                  │
│                                         │
│  Named Volume        Bind Mount         │
│  /var/lib/docker  ←→  /your/path   ←→  Container
│  /volumes/mydata      /home/king/data   │
└─────────────────────────────────────────┘
```

| Type | What it is | When to use |
|---|---|---|
| **Named volume** | Docker manages the location | Databases, persistent app data |
| **Bind mount** | You specify exact host path | Development — live code reloading |
| **tmpfs** | Stored in memory only | Sensitive data that shouldn't touch disk |

---

### Named volumes

```bash
# create a volume
docker volume create mydata

# use it
docker run -d \
  --name postgres-test \
  -v mydata:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=secret \
  postgres:15-alpine

# list volumes
docker volume ls

# inspect
docker volume inspect mydata

# delete
docker volume rm mydata
```

Data in `/var/lib/postgresql/data` inside the container is stored in `mydata` volume on your host. Delete the container — data survives. Spin up a new container with the same volume — data is there.

---

### Bind mounts

```bash
docker run -d \
  -v /home/kijuchihe/docker-practice:/app \
  -p 3000:3000 \
  docker-practice
```

Your local `/home/kijuchihe/docker-practice` is mounted directly into `/app` inside the container. Edit a file on your host — container sees it immediately. This is how dev environments work.

---

### Volume in Dockerfile

```dockerfile
VOLUME /app/data
```

Documents that this path should be a volume. Doesn't create a named volume — just signals to whoever runs the container that this path needs persistence.

---

### Key difference

```bash
# Named volume — Docker manages it
-v mydata:/var/lib/postgresql/data

# Bind mount — you specify the path
-v /home/kijuchihe/mydata:/var/lib/postgresql/data
```

Named volumes are preferred for production — Docker manages permissions and location. Bind mounts are preferred for development — direct access to your code.

---

Try this:

```bash
# create a volume
docker volume create pgdata

# run postgres with it
docker run -d \
  --name pg-test \
  -v pgdata:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=secret \
  -p 5432:5432 \
  postgres:15-alpine

# check it's running
docker ps
docker volume inspect pgdata
```

Tell me where Docker stored the volume data on your host.