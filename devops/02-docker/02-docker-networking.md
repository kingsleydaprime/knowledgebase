## Docker Networking

By default containers are isolated — they can't talk to each other or the outside world unless you explicitly configure it.

---

### Network types

| Driver | What it does |
|---|---|
| `bridge` | Default. Containers on same bridge can talk to each other |
| `host` | Container shares host's network directly — no isolation |
| `none` | No networking at all — fully isolated |
| `overlay` | Multi-host networking — for Docker Swarm/K8s |
| `macvlan` | Container gets its own MAC address — appears as physical device |

---

### Default bridge network

When you run a container without specifying a network, it goes on the default bridge network `docker0`.

```bash
docker network ls
docker network inspect bridge
```

Problem with the default bridge — containers can't reach each other by name, only by IP. IPs change every restart. That's why you create custom networks.

---

### Custom bridge network

```bash
# create a network
docker network create mynetwork

# run containers on it
docker run -d --name db --network mynetwork postgres:15-alpine
docker run -d --name app --network mynetwork docker-practice

# containers can now reach each other by name
# from inside app container:
# ping db        ← works
# ping db:5432   ← works
```

On a custom network Docker provides automatic **DNS resolution** — container names become hostnames. That's how in Docker Compose your app connects to `postgres` just by using `postgres` as the hostname.

---

### Networking commands

```bash
docker network ls                          # list networks
docker network create mynetwork            # create network
docker network rm mynetwork                # delete network
docker network inspect mynetwork           # detailed info
docker network connect mynetwork container    # add container to network
docker network disconnect mynetwork container # remove from network
```

---

### Port mapping

```
-p host_port:container_port
```

```bash
docker run -p 3000:3000 myapp    # host 3000 → container 3000
docker run -p 8080:3000 myapp    # host 8080 → container 3000
docker run -p 3000:3000 -p 5432:5432 myapp   # multiple ports
```

Without `-p` — container port is only accessible from inside Docker network, not from your host.

---

Try this:

```bash
# create a custom network
docker network create practiceNetwork

# run two containers on it
docker run -d --name redis-test --network practiceNetwork redis:alpine
docker run -d --name app-test --network practiceNetwork --rm docker-practice node -e "require('dns').lookup('redis-test', (err, addr) => console.log(addr))"

# inspect the network
docker network inspect practiceNetwork
```

Tell me what IP address redis-test got assigned.

```zsh
> # create a custom network
sudo docker network create practiceNetwork

# run two containers on it
sudo docker run -d --name redis-test --network practiceNetwork redis:alpine
sudo docker run -d --name app-test --network practiceNetwork --rm docker-practice node -e "require('dns').lookup('redis-test', (err, addr) => console.log(addr))"

# inspect the network
sudo docker network inspect practiceNetwork
750688a006bd9c513b93c13b404bad7fc5d642db8f7344ffd5c6ca6ca94e207a
05eeeadfbdf7e9f81659451856c69bbc30ac795dd1578b4be289c81ff3722f87
475b8e9c0b0cf292472d1870f20053e32c6ea088d4d8069ab93f30aef67c1e70
[
    {
        "Name": "practiceNetwork",
        "Id": "750688a006bd9c513b93c13b404bad7fc5d642db8f7344ffd5c6ca6ca94e207a",
        "Created": "2026-05-12T16:42:39.131580405Z",
        "Scope": "local",
        "Driver": "bridge",
        "EnableIPv4": true,
        "EnableIPv6": false,
        "IPAM": {
            "Driver": "default",
            "Options": {},
            "Config": [
                {
                    "Subnet": "172.18.0.0/16",
                    "Gateway": "172.18.0.1"
                }
            ]
        },
        "Internal": false,
        "Attachable": false,
        "Ingress": false,
        "ConfigFrom": {
            "Network": ""
        },
        "ConfigOnly": false,
        "Options": {},
        "Labels": {},
        "Containers": {
            "05eeeadfbdf7e9f81659451856c69bbc30ac795dd1578b4be289c81ff3722f87": {
                "Name": "redis-test",
                "EndpointID": "52e75abba8c196d45fb9ed73505627d1d7725e20b21b82a8779567b6d4248742",
                "MacAddress": "9a:90:37:1e:20:c7",
                "IPv4Address": "172.18.0.2/16",
                "IPv6Address": ""
            },
            "475b8e9c0b0cf292472d1870f20053e32c6ea088d4d8069ab93f30aef67c1e70": {
                "Name": "app-test",
                "EndpointID": "434369226d2536f8aafe391aa9be577018e3a126d17fe43ba38aa66513b948b3",
                "MacAddress": "32:f0:5d:d5:f6:6f",
                "IPv4Address": "172.18.0.3/16",
                "IPv6Address": ""
            }
        },
        "Status": {
            "IPAM": {
                "Subnets": {
                    "172.18.0.0/16": {
                        "IPsInUse": 5,
                        "DynamicIPsAvailable": 65531
                    }
                }
            }
        }
    }
]
```

Perfect. A few things worth noting:

**Redis got `172.18.0.2`** — first container on the network.
**App got `172.18.0.3`** — second container.
**Gateway is `172.18.0.1`** — Docker's virtual router for this network.
**Subnet is `172.18.0.0/16`** — 65,531 IPs available. That's why Docker uses `/16` — room for many containers.

And the DNS resolution worked — `app-test` successfully looked up `redis-test` by name and got back `172.18.0.2`. That's Docker's internal DNS doing its job.

---

Clean up before volumes:

```bash
docker stop redis-test app-test
docker rm redis-test
docker network rm practiceNetwork
```

`app-test` was created with `--rm` so it deleted itself automatically.

---

Now run the volume exercise:

```bash
docker volume create pgdata

docker run -d \
  --name pg-test \
  -v pgdata:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=secret \
  -p 5432:5432 \
  postgres:15-alpine

docker ps
docker volume inspect pgdata
```

Tell me where Docker stored the volume data on your host.