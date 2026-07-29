# VPS Deployment — Full Reference Guide

> A complete, production-grade reference for deploying applications on a Linux VPS.
> Covers provisioning, hardening, reverse proxy, CI/CD, firewall, observability, and logging.

---

## Table of Contents

1. [Initial Server Setup](#1-initial-server-setup)
2. [SSH Hardening](#2-ssh-hardening)
3. [Firewall Setup (UFW)](#3-firewall-setup-ufw)
4. [Installing Docker](#4-installing-docker)
5. [Traefik — Reverse Proxy & SSL](#5-traefik--reverse-proxy--ssl)
6. [CI/CD Pipeline with GitHub Actions](#6-cicd-pipeline-with-github-actions)
7. [Monitoring — Prometheus, Grafana, Loki](#7-monitoring--prometheus-grafana-loki)
8. [Logging — ELK Stack (Elasticsearch, Logstash, Kibana)](#8-logging--elk-stack-elasticsearch-logstash-kibana)
9. [Log Rotation & Disk Management](#9-log-rotation--disk-management)
10. [Fail2Ban — Intrusion Prevention](#10-fail2ban--intrusion-prevention)
11. [Automated Backups](#11-automated-backups)
12. [Useful Docker Commands](#12-useful-docker-commands)
13. [Troubleshooting Cheatsheet](#13-troubleshooting-cheatsheet)
14. [Linux Concepts Reference](#14-linux-concepts-reference)
15. [Secrets Management](#15-secrets-management)
16. [SSL — Wildcard Certs & DNS Challenge](#16-ssl--wildcard-certs--dns-challenge)
17. [Health Checks](#17-health-checks)
18. [Container Resource Limits](#18-container-resource-limits)
19. [Running Postgres in Docker](#19-running-postgres-in-docker)
20. [Swap Space](#20-swap-space)
21. [Kernel Parameter Tuning](#21-kernel-parameter-tuning)
22. [Zero Downtime & Rolling Deployments](#22-zero-downtime--rolling-deployments)
23. [SSH Jump Hosts & Bastion Servers](#23-ssh-jump-hosts--bastion-servers)
24. [Nginx — Alternative to Traefik](#24-nginx--alternative-to-traefik)
25. [Docker Volumes — The Full Picture](#25-docker-volumes--the-full-picture)
26. [When to Use Each Volume Type](#26-when-to-use-each-volume-type)
27. [Docker Networking](#27-docker-networking)
28. [Environment-Specific Compose Files](#28-environment-specific-compose-files)
29. [Dockerfile Best Practices](#29-dockerfile-best-practices)
30. [Rollback Strategy](#30-rollback-strategy)
31. [Rate Limiting & DDoS Protection](#31-rate-limiting--ddos-protection)
32. [Cron Jobs vs Systemd Timers](#32-cron-jobs-vs-systemd-timers)
33. [VPS Provider Snapshots](#33-vps-provider-snapshots)
34. [Deployment Checklist](#34-deployment-checklist)

---

## 1. Initial Server Setup

### 1.1 Buy a VPS and Point Your Domain

- Purchase a VPS (DigitalOcean, Hetzner, Vultr, Contabo, etc.)
- Point your domain's **A record** to the VPS IP address
- Wait for DNS propagation (use `dig yourdomain.com` to verify)

### 1.2 Generate an SSH Key (on your local machine)

```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
# -t ed25519: use the modern Ed25519 algorithm (faster and more secure than RSA)
# -C: adds a comment label to identify the key (usually your email)
# Keys saved to ~/.ssh/id_ed25519 (private) and ~/.ssh/id_ed25519.pub (public)
```

- Add the **public key** to your VPS provider dashboard before first login.

### 1.3 First Login as Root

```bash
ssh root@<ip-address>
```

### 1.4 Update the System

```bash
apt update && apt upgrade -y
# apt update: refreshes the package index
# apt upgrade -y: upgrades all packages; -y auto-confirms prompts
```

### 1.5 Create a Non-Root User

```bash
adduser --gecos "" username          # --gecos "" skips extra info prompts (full name, phone, etc.)
usermod -aG sudo username            # -aG: append to group without removing existing groups
```

### 1.6 Switch to the New User and Verify

```bash
su - username                        # - loads the user's full login shell environment
sudo ls /                            # Should succeed if sudo privileges are working
```

### 1.7 Copy SSH Access to the New User

**Option A — From the VPS (while logged in as root):**

```bash
mkdir /home/username/.ssh
cp ~/.ssh/authorized_keys /home/username/.ssh/
chown -R username:username /home/username/.ssh   # -R: recursive, applies to all files inside
chmod 700 /home/username/.ssh                    # Owner can read/write/enter; no one else can
chmod 600 /home/username/.ssh/authorized_keys    # Owner can read/write; no one else can
```

**Option B — From your local machine:**

```bash
ssh-copy-id username@<ip-address>   # Copies your local public key to the remote authorized_keys
```

> **Do not skip this step.** You must confirm key-based login works before disabling password auth.

---

## 2. SSH Hardening

### 2.1 Edit the SSH Config

```bash
sudo nvim /etc/ssh/sshd_config
```

Make the following changes:

```
PasswordAuthentication no       # Disable password login — key-based only
PermitRootLogin no              # Disable direct root login over SSH
UsePAM no                       # Disable PAM (safe for key-only setups)
PubkeyAuthentication yes        # Explicitly ensure public key auth is enabled
AuthorizedKeysFile .ssh/authorized_keys   # Where to look for authorized public keys
```

> **Note on `UsePAM no`:** Safe for basic key-only setups. If you plan to add 2FA (e.g., Google Authenticator) later, leave PAM enabled and configure it separately.

### 2.2 Restart SSH

```bash
sudo systemctl restart sshd
```

> Open a **second terminal** and verify you can still log in before closing your current session.

### 2.3 Change the Default SSH Port (Optional but Recommended)

```bash
# In /etc/ssh/sshd_config:
Port 2222    # Use any unused port above 1024 — reduces automated scan noise on port 22
```

Update your UFW rule accordingly (see Section 3).

---

## 3. Firewall Setup (UFW)

```bash
sudo ufw status                        # Should show inactive on first setup
sudo ufw allow 80                      # Allow HTTP traffic
sudo ufw allow 443                     # Allow HTTPS traffic
sudo ufw allow 22                      # Allow SSH (change to your custom port if applicable)
sudo ufw default deny incoming         # Block all inbound traffic not explicitly allowed
sudo ufw default allow outgoing        # Allow all outbound traffic
sudo ufw enable
sudo ufw status verbose
```

### 3.1 Restrict SSH to Your IP Only (Recommended)

```bash
sudo ufw allow from <your-ip> to any port 22   # Only allow SSH from your specific IP
sudo ufw delete allow 22                        # Remove the previously open SSH rule
```

### 3.2 Rate Limit SSH to Prevent Brute Force

```bash
sudo ufw limit 22    # Blocks IPs with 6+ connection attempts in 30 seconds
```

### 3.3 Reload After Changes

```bash
sudo ufw reload
```

---

## 4. Installing Docker

```bash
# Install prerequisites for adding external repos over HTTPS
sudo apt install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key to verify package authenticity
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add Docker's apt repository to your package sources
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Refresh sources and install Docker engine with the compose plugin
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### 4.1 Allow User to Run Docker Without Sudo

```bash
sudo usermod -aG docker username   # Add user to the docker group
newgrp docker                      # Apply the group change immediately without logging out
```

### 4.2 Verify

```bash
docker run hello-world   # Pulls a test image and runs it — confirms Docker is working
```

---

## 5. Traefik — Reverse Proxy & SSL

Traefik handles routing and auto-provisions SSL certificates via Let's Encrypt.

### 5.1 Directory Structure

```
~/traefik/
├── compose.yml
├── traefik.yml
└── acme.json        # SSL certificate store — must have chmod 600
```

### 5.2 Create the Shared Network

```bash
# This network is shared by Traefik and all services it routes to
docker network create traefik-network
```

### 5.3 `acme.json` — Certificate Store

```bash
touch ~/traefik/acme.json
chmod 600 ~/traefik/acme.json    # REQUIRED — Traefik will refuse to start if permissions are wrong
```

### 5.4 `traefik.yml` — Static Configuration

```yaml
# Traefik static config — loaded once at startup, requires restart to apply changes

api:
  dashboard: true     # Enable the Traefik web dashboard
  insecure: false     # Dashboard is not exposed on raw port 8080 — use a secured router instead

entryPoints:
  web:
    address: ":80"    # Listen on port 80 for HTTP
    http:
      redirections:
        entryPoint:
          to: websecure   # Automatically redirect all HTTP traffic to HTTPS
          scheme: https
  websecure:
    address: ":443"   # Listen on port 443 for HTTPS

certificatesResolvers:
  letsencrypt:
    acme:
      email: your-email@example.com   # Let's Encrypt sends cert expiry warnings here
      storage: /acme.json             # Where certificates are stored inside the container
      httpChallenge:
        entryPoint: web               # Use HTTP-01 challenge for domain verification

providers:
  docker:
    exposedByDefault: false   # Only route to containers that explicitly opt in via labels
    network: traefik-network  # Only watch containers connected to this network

log:
  level: INFO   # Log verbosity — options: DEBUG, INFO, WARN, ERROR

accessLog: {}   # Enable access logging with default settings (logs each request)
```

### 5.5 `compose.yml` — Traefik Service

```yaml
services:
  traefik:
    image: traefik:v3.0
    container_name: traefik
    restart: unless-stopped   # Restart on crash but not if manually stopped
    ports:
      - "80:80"               # HTTP entrypoint — host:container
      - "443:443"             # HTTPS entrypoint
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro   # Lets Traefik watch Docker events; :ro = read-only for safety
      - ./traefik.yml:/traefik.yml:ro                  # Mount static config as read-only
      - ./acme.json:/acme.json                         # Cert store must be writable so Traefik can update it
    networks:
      - traefik-network
    labels:
      - "traefik.enable=true"
      # Route the Traefik dashboard to its own subdomain
      - "traefik.http.routers.dashboard.rule=Host(`traefik.yourdomain.com`)"
      - "traefik.http.routers.dashboard.entrypoints=websecure"
      - "traefik.http.routers.dashboard.tls.certresolver=letsencrypt"
      - "traefik.http.routers.dashboard.service=api@internal"
      # Protect the dashboard with basic auth (generate password hash with htpasswd)
      - "traefik.http.routers.dashboard.middlewares=auth"
      - "traefik.http.middlewares.auth.basicauth.users=admin:$$apr1$$..."  # $$ escapes the $ sign in compose

networks:
  traefik-network:
    external: true   # This network was created manually — compose should not manage its lifecycle
```

### 5.6 Connecting Your App to Traefik

In your app's `compose.yml`:

```yaml
services:
  app:
    image: your-app-image
    restart: unless-stopped
    networks:
      - traefik-network   # Must be on the same network as Traefik for it to route traffic here
    labels:
      - "traefik.enable=true"                                                   # Opt this container into Traefik routing
      - "traefik.http.routers.app.rule=Host(`app.yourdomain.com`)"             # Route requests for this hostname here
      - "traefik.http.routers.app.entrypoints=websecure"                       # Only handle HTTPS traffic
      - "traefik.http.routers.app.tls.certresolver=letsencrypt"                # Auto-provision SSL certificate
      - "traefik.http.services.app.loadbalancer.server.port=3000"              # Forward to this port inside the container

networks:
  traefik-network:
    external: true
```

### 5.7 Start Traefik

```bash
cd ~/traefik && docker compose up -d
```

---

## 6. CI/CD Pipeline with GitHub Actions

### 6.1 Generate a Deploy SSH Key (on the VPS)

```bash
# Generate a dedicated key for GitHub Actions — keep it separate from your personal key
# -t ed25519: key type
# -C: label to identify this key
# -f: output file (separate from your personal ~/.ssh/id_ed25519)
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions
```

### 6.2 Authorize the Deploy Key on the VPS

```bash
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys   # >> appends; > would overwrite and lock you out
```

### 6.3 Add Secrets to GitHub

Go to **GitHub → Repo → Settings → Secrets → Actions** and add:

| Secret Name | Value |
|---|---|
| `VPS_HOST` | Your VPS IP address |
| `VPS_USER` | Your non-root username |
| `VPS_SSH_KEY` | Contents of `~/.ssh/github_actions` (private key) |
| `VPS_PORT` | SSH port (default: 22) |

Copy private key to clipboard:

```bash
cat ~/.ssh/github_actions    # Copy the full output including the BEGIN and END header lines
```

### 6.4 Example Workflow — `.github/workflows/deploy.yml`

```yaml
# This workflow runs on every push to main, builds a Docker image, and deploys it to the VPS
name: Deploy to VPS

on:
  push:
    branches: [main]   # Only trigger on pushes to the main branch

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3   # Enables multi-platform builds and layer caching

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_TOKEN }}   # Use an access token, not your account password

      - name: Build and push image
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: yourdockerhubuser/yourapp:latest

      - name: Deploy to VPS
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          port: ${{ secrets.VPS_PORT }}
          script: |
            cd ~/your-app
            docker compose pull                      # Pull the latest image pushed above
            docker compose up -d --remove-orphans   # Restart with new image; --remove-orphans cleans up stale containers
            docker image prune -f                   # Clean up old image layers to prevent disk from filling over time
```

---

## 7. Monitoring — Prometheus, Grafana, Loki

### 7.1 Install the Loki Docker Driver (on the VPS)

```bash
# This plugin intercepts Docker container logs and ships them directly to Loki
docker plugin install grafana/loki-docker-driver:latest \
  --alias loki \                  # Alias makes it easier to reference in compose logging config
  --grant-all-permissions
```

Verify:

```bash
docker plugin ls
```

### 7.2 Directory Structure

```
~/monitoring/
├── compose.yml
├── prometheus.yml
└── loki-config.yml
```

### 7.3 `prometheus.yml`

```yaml
global:
  scrape_interval: 15s      # How often Prometheus collects metrics from each target
  evaluation_interval: 15s  # How often alerting rules are evaluated

scrape_configs:
  # Prometheus monitoring itself — useful for tracking Prometheus's own health
  - job_name: prometheus
    static_configs:
      - targets: ["localhost:9090"]

  # Node Exporter — exposes host-level metrics: CPU, RAM, disk I/O, network
  - job_name: node
    static_configs:
      - targets: ["node-exporter:9100"]

  # cAdvisor — exposes per-container resource usage and performance metrics
  - job_name: cadvisor
    static_configs:
      - targets: ["cadvisor:8080"]
```

### 7.4 `loki-config.yml`

```yaml
# Loki is a log aggregation system — like Prometheus but designed for logs, not metrics

auth_enabled: false   # Disable multi-tenant auth for single-server setups; enable if exposing externally

server:
  http_listen_port: 3100   # Port Loki listens on for log ingestion and queries

ingester:
  lifecycler:
    ring:
      kvstore:
        store: inmemory   # In-memory ring — fine for single node; use consul/etcd for multi-node clusters
      replication_factor: 1

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper    # Index storage engine
      object_store: filesystem # Where log chunks are stored (use S3/GCS for production scale)
      schema: v11
      index:
        prefix: index_
        period: 24h            # Create a new index shard every 24 hours

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/boltdb-shipper-active
    cache_location: /loki/boltdb-shipper-cache
    shared_store: filesystem
  filesystem:
    directory: /loki/chunks    # Directory where compressed log chunks are written to disk

limits_config:
  retention_period: 168h       # 7 days — logs older than this are automatically purged

compactor:
  working_directory: /loki/compactor
  shared_store: filesystem
  retention_enabled: true      # Must be explicitly true for the retention_period above to take effect
```

### 7.5 `compose.yml` — Monitoring Stack

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml   # Mount our custom scrape config
      - prometheus_data:/prometheus                        # Persist metric data across container restarts
    networks:
      - traefik-network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.prometheus.rule=Host(`prometheus.yourdomain.com`)"
      - "traefik.http.routers.prometheus.entrypoints=websecure"
      - "traefik.http.routers.prometheus.tls.certresolver=letsencrypt"

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=your-secure-password   # Set the default admin password on first boot
      - GF_USERS_ALLOW_SIGN_UP=false                      # Prevent anyone from self-registering
    volumes:
      - grafana_data:/var/lib/grafana   # Persist dashboards, data sources, and user settings
    networks:
      - traefik-network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.grafana.rule=Host(`grafana.yourdomain.com`)"
      - "traefik.http.routers.grafana.entrypoints=websecure"
      - "traefik.http.routers.grafana.tls.certresolver=letsencrypt"

  loki:
    image: grafana/loki:latest
    container_name: loki
    restart: unless-stopped
    ports:
      - "3100:3100"   # Expose so the Loki Docker logging driver can push logs to it
    volumes:
      - ./loki-config.yml:/etc/loki/local-config.yaml   # Mount our custom Loki config
      - loki_data:/loki                                   # Persist log chunks across restarts
    command: -config.file=/etc/loki/local-config.yaml
    networks:
      - traefik-network

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    restart: unless-stopped
    volumes:
      # Mount host system paths as read-only so node-exporter can read kernel and hardware metrics
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      # Exclude virtual/system filesystems from disk metrics to reduce noise in dashboards
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    networks:
      - traefik-network

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    restart: unless-stopped
    privileged: true   # Required to access container runtime stats from the host kernel
    volumes:
      # Mount host paths so cAdvisor can read Docker container resource metrics
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    networks:
      - traefik-network

volumes:
  prometheus_data:   # Named volumes — managed by Docker, survive container removal
  grafana_data:
  loki_data:

networks:
  traefik-network:
    external: true   # Pre-existing network — not created or destroyed by this compose file
```

### 7.6 Send Container Logs to Loki

In any app `compose.yml`, add the logging driver:

```yaml
services:
  app:
    image: your-app
    logging:
      driver: loki                                              # Use the Loki plugin instead of default json-file
      options:
        loki-url: "http://localhost:3100/loki/api/v1/push"    # Loki's HTTP push endpoint
        loki-batch-size: "400"                                 # Number of log lines per batch before flushing
        loki-retries: "3"                                      # Retry failed push attempts up to 3 times
        loki-timeout: "2s"                                     # Timeout per push attempt
        loki-external-labels: "app=your-app,env=production"   # Labels used to filter logs in Grafana
```

### 7.7 Grafana Setup

1. Log in at `https://grafana.yourdomain.com`
2. Add Prometheus as a data source (`http://prometheus:9090`)
3. Add Loki as a data source (`http://loki:3100`)
4. Import useful dashboards:
   - **Node Exporter Full** — Dashboard ID `1860`
   - **cAdvisor** — Dashboard ID `14282`
   - **Loki Logs** — Use the Explore tab with LogQL

---

## 8. Logging — ELK Stack (Elasticsearch, Logstash, Kibana)

The ELK stack is a more powerful alternative to the Loki approach, best suited for high log volumes, complex querying, or when you need full-text search across logs.

> **Note:** ELK is resource-heavy. Elasticsearch alone needs at minimum 2GB RAM. Use a VPS with at least 4GB RAM for this stack.

### 8.1 Directory Structure

```
~/elk/
├── compose.yml
├── logstash/
│   ├── pipeline/
│   │   └── logstash.conf
│   └── logstash.yml
└── kibana.yml
```

### 8.2 `compose.yml` — ELK Stack

```yaml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.12.0
    container_name: elasticsearch
    restart: unless-stopped
    environment:
      - discovery.type=single-node                   # Run as a single node — no cluster configuration needed
      - xpack.security.enabled=false                 # Disable built-in auth for local dev; enable in production
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"            # JVM heap size — tune up if you have more RAM available
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data   # Persist all indexed data across container restarts
    ulimits:
      memlock:
        soft: -1   # Remove memory lock limits — Elasticsearch requires this for performance
        hard: -1
    networks:
      - traefik-network

  logstash:
    image: docker.elastic.co/logstash/logstash:8.12.0
    container_name: logstash
    restart: unless-stopped
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline          # Mount our pipeline config directory
      - ./logstash/logstash.yml:/usr/share/logstash/config/logstash.yml
    ports:
      - "5044:5044"      # Beats input — used by Filebeat to ship logs to Logstash
      - "5000:5000/tcp"  # TCP input — accepts raw or JSON log lines over TCP
      - "5000:5000/udp"  # UDP input — same but over UDP (fire-and-forget)
      - "9600:9600"      # Logstash monitoring API — check pipeline health and stats
    environment:
      - "LS_JAVA_OPTS=-Xmx256m -Xms256m"   # Keep Logstash JVM heap small if memory is limited
    depends_on:
      - elasticsearch   # Wait for Elasticsearch before starting — prevents connection errors on boot
    networks:
      - traefik-network

  kibana:
    image: docker.elastic.co/kibana/kibana:8.12.0
    container_name: kibana
    restart: unless-stopped
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200   # Tell Kibana where to find Elasticsearch
    networks:
      - traefik-network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.kibana.rule=Host(`kibana.yourdomain.com`)"
      - "traefik.http.routers.kibana.entrypoints=websecure"
      - "traefik.http.routers.kibana.tls.certresolver=letsencrypt"
    depends_on:
      - elasticsearch   # Kibana cannot function without Elasticsearch running first

volumes:
  elasticsearch_data:   # Named volume — preserves your indexed log data across container restarts

networks:
  traefik-network:
    external: true
```

### 8.3 `logstash/pipeline/logstash.conf`

```
# Logstash pipeline: data flows through input → filter → output

input {
  beats {
    port => 5044   # Receive logs shipped by Filebeat agents
  }
  tcp {
    port => 5000
    codec => json  # Expect JSON-formatted log lines on the TCP input
  }
}

filter {
  # If the log has a service label in its fields, promote it to a top-level field for easier querying
  if [fields][service] {
    mutate {
      add_field => { "service" => "%{[fields][service]}" }
    }
  }

  # Parse the timestamp field and use it as the official Elasticsearch event time
  date {
    match => ["timestamp", "ISO8601"]
  }

  # Drop health check logs — they're high-volume noise that wastes storage
  if [message] =~ "GET /health" {
    drop {}
  }
}

output {
  elasticsearch {
    hosts => ["http://elasticsearch:9200"]
    # Daily index per service — makes it easy to query and delete logs by date
    index => "logs-%{[fields][service]}-%{+YYYY.MM.dd}"
  }
  # Also print processed logs to stdout — useful for debugging the pipeline
  stdout {
    codec => rubydebug
  }
}
```

### 8.4 Shipping Logs with Filebeat (on App Servers)

Install Filebeat on the VPS or in a sidecar container:

```yaml
# Add to your app's compose.yml
  filebeat:
    image: docker.elastic.co/beats/filebeat:8.12.0
    container_name: filebeat
    user: root   # Needs root to read Docker socket and container log files
    volumes:
      - ./filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro   # Read container log files from host
      - /var/run/docker.sock:/var/run/docker.sock:ro               # Read Docker metadata to enrich logs
    networks:
      - traefik-network
```

`filebeat.yml`:

```yaml
filebeat.inputs:
  - type: container
    paths:
      - '/var/lib/docker/containers/*/*.log'   # Glob matches all container log files on the host
    processors:
      - add_docker_metadata:
          host: "unix:///var/run/docker.sock"  # Enriches each log with container name, image, labels, etc.

output.logstash:
  hosts: ["logstash:5044"]   # Ship logs to Logstash's Beats input port

fields:
  service: your-app          # Custom label — appears in the Elasticsearch index name
fields_under_root: true      # Place fields at root level instead of nested under a "fields" key
```

### 8.5 Elasticsearch Index Management

```bash
# List all indices with their health status, size, and document count
curl http://localhost:9200/_cat/indices?v

# Delete old indices manually — replace the date pattern as needed
curl -X DELETE http://localhost:9200/logs-app-2024.01.*

# Set up Index Lifecycle Management (ILM) to automatically delete logs older than 7 days
curl -X PUT http://localhost:9200/_ilm/policy/logs-policy \
  -H 'Content-Type: application/json' \
  -d '{
    "policy": {
      "phases": {
        "hot": { "actions": {} },
        "delete": {
          "min_age": "7d",
          "actions": { "delete": {} }
        }
      }
    }
  }'
```

---

## 9. Log Rotation & Disk Management

### 9.1 Configure Docker Log Rotation Globally

Edit or create `/etc/docker/daemon.json`:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

> `max-size`: rotate when a log file hits this size. `max-file`: keep this many rotated files per container.

Restart Docker:

```bash
sudo systemctl restart docker
```

> This only applies to new containers. Recreate existing ones to apply.

### 9.2 Per-Container Log Limits

```yaml
services:
  app:
    image: your-app
    logging:
      driver: json-file
      options:
        max-size: "10m"   # Rotate the log file when it hits 10MB
        max-file: "5"     # Keep up to 5 rotated files — max 50MB of logs per container
```

### 9.3 Docker Disk Cleanup

```bash
# Remove stopped containers, unused networks, dangling images, and build cache
docker system prune -f

# Also remove unused volumes — be careful, this permanently deletes volume data
docker system prune -af --volumes

# Remove only dangling images (untagged intermediate layers from old builds)
docker image prune -f

# Remove all unused images, not just dangling ones
docker image prune -a -f

# Show a breakdown of exactly how much disk Docker is using
docker system df
```

### 9.4 Check Overall Disk Usage

```bash
df -h                              # Disk usage by partition — check if you're close to full
du -sh /var/lib/docker             # Docker's total disk footprint
du -sh /var/lib/docker/volumes/*   # Per-volume sizes — identify large volumes
ncdu /                             # Interactive disk explorer (install with: apt install ncdu)
```

### 9.5 Automate Cleanup with a Cron Job

```bash
crontab -e
```

Add:

```
# Run Docker cleanup every Sunday at 2AM — log output for debugging
0 2 * * 0 docker system prune -f >> /var/log/docker-cleanup.log 2>&1
```

---

## 10. Fail2Ban — Intrusion Prevention

Fail2Ban monitors log files and bans IPs that show malicious behavior (like repeated failed SSH logins).

### 10.1 Install

```bash
sudo apt install fail2ban -y
```

### 10.2 Configure

```bash
# Never edit jail.conf directly — it gets overwritten on package updates
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nvim /etc/fail2ban/jail.local
```

Key settings to update:

```ini
[DEFAULT]
bantime  = 1h          # How long to ban the offending IP
findtime = 10m         # The time window in which failures are counted
maxretry = 5           # Number of failures within findtime before a ban is applied
backend  = systemd     # Read logs from systemd journal — correct for modern Ubuntu systems

[sshd]
enabled = true
port    = ssh          # Update to your custom port number if you changed it in sshd_config
logpath = %(sshd_log)s # Automatically resolves to the correct SSH log path for your distro
```

### 10.3 Start and Enable

```bash
sudo systemctl enable fail2ban   # Start automatically on every boot
sudo systemctl start fail2ban
```

### 10.4 Useful Commands

```bash
sudo fail2ban-client status                  # Overview of all active jails
sudo fail2ban-client status sshd             # SSH jail — shows currently banned IPs
sudo fail2ban-client set sshd unbanip <ip>   # Manually unban an IP (e.g. if you locked yourself out)
sudo fail2ban-client banned                  # List all currently banned IPs across all jails
```

---

## 11. Automated Backups

### 11.1 Backup Docker Volumes

```bash
#!/bin/bash
# backup-volumes.sh — backs up all Docker named volumes to dated directories

DATE=$(date +%Y-%m-%d)
BACKUP_DIR="/home/username/backups/$DATE"
mkdir -p "$BACKUP_DIR"

# Get a list of all named Docker volumes on this host
VOLUMES=$(docker volume ls -q)

for vol in $VOLUMES; do
  echo "Backing up $vol..."
  docker run --rm \
    -v "$vol":/source:ro \       # Mount the volume as a read-only source
    -v "$BACKUP_DIR":/backup \   # Mount backup directory as the destination
    alpine tar czf /backup/"$vol".tar.gz -C /source .   # Compress and archive volume contents
done

echo "Backup complete: $BACKUP_DIR"

# Delete backup directories older than 7 days to prevent disk from filling up
find /home/username/backups -type d -mtime +7 -exec rm -rf {} +
```

Make executable and schedule:

```bash
chmod +x backup-volumes.sh
crontab -e
# Add: 0 3 * * * /home/username/backup-volumes.sh >> /var/log/backup.log 2>&1
```

### 11.2 Backup a Postgres Database

```bash
docker exec your-postgres-container \
  pg_dump -U your-db-user your-db-name \
  | gzip > /home/username/backups/db-$(date +%Y-%m-%d).sql.gz
  # Pipes the dump directly into gzip — no uncompressed file ever touches the disk
```

### 11.3 Sync Backups to Remote Storage (S3)

```bash
sudo apt install awscli -y
aws configure   # Prompts for access key, secret key, region, and output format

# sync only uploads changed or new files — efficient for incremental daily backups
aws s3 sync /home/username/backups s3://your-bucket/vps-backups/
```

---

## 12. Useful Docker Commands

### Containers

```bash
docker ps                              # List running containers
docker ps -a                           # List all containers including stopped ones
docker logs container-name             # View container logs
docker logs -f container-name          # Follow logs live (-f = follow, like tail -f)
docker exec -it container-name bash    # Open an interactive shell inside a running container
docker inspect container-name         # Full JSON details — network settings, mounts, config, etc.
docker stats                           # Live CPU, memory, network, and disk I/O per container
docker restart container-name
docker stop container-name
docker rm container-name
```

### Images

```bash
docker images                          # List all locally stored images
docker pull image-name:tag
docker rmi image-name                  # Remove an image
docker image prune -f                  # Remove dangling images (untagged intermediate build layers)
docker image prune -af                 # Remove all images not currently used by any container
```

### Networks

```bash
docker network ls
docker network inspect network-name    # Show connected containers and their assigned IPs
docker network create network-name
docker network connect network-name container-name
```

### Compose

```bash
docker compose up -d                   # Start services in detached mode (background)
docker compose up -d --build           # Rebuild images before starting
docker compose down                    # Stop and remove containers and networks
docker compose down -v                 # Also remove named volumes — data will be lost
docker compose pull                    # Pull the latest version of all images
docker compose logs -f                 # Follow logs from all services at once
docker compose logs -f service-name    # Follow logs from a specific service only
docker compose restart service-name
docker compose -f custom.yml up -d     # Specify a custom compose file with -f
docker compose exec service-name bash  # Open a shell inside a running service
```

### Plugins

```bash
docker plugin ls
docker plugin install plugin-name --grant-all-permissions
docker plugin disable plugin-name
docker plugin rm plugin-name
```

### System

```bash
docker system df                       # Disk usage summary — images, containers, volumes, build cache
docker system prune -f                 # Remove unused resources (safe — won't touch running containers)
docker system prune -af --volumes      # Nuclear option — removes everything not currently in use
```

---

## 13. Troubleshooting Cheatsheet

| Problem | Command / Fix |
|---|---|
| Can't SSH in after config change | Use VPS provider's web console to access the machine |
| Traefik not getting SSL cert | Check `acme.json` has `chmod 600`; verify DNS is pointing correctly |
| Container not joining Traefik network | Ensure `traefik-network` is external and listed in the app's compose |
| Port already in use | `sudo lsof -i :PORT` to find the process; `sudo kill -9 PID` |
| Docker group not applied | Log out and back in, or run `newgrp docker` |
| Disk full | `docker system df`, then `docker system prune -af` |
| Container keeps restarting | `docker logs container-name` to see the crash reason |
| Elasticsearch won't start | Check `vm.max_map_count`: `sudo sysctl -w vm.max_map_count=262144` |
| UFW blocking internal Docker traffic | Docker manages its own iptables rules; avoid UFW conflicts with `DOCKER-USER` chain if needed |
| CI/CD deploy doesn't update | Ensure `docker compose pull` runs before `up -d`; old image may be cached |
| Fail2Ban banning your own IP | `sudo fail2ban-client set sshd unbanip <your-ip>` |

---

## 14. Linux Concepts Reference

### UFW — Uncomplicated Firewall

**UFW** stands for **Uncomplicated Firewall**. It is a frontend for `iptables` — Linux's underlying packet filtering system. `iptables` is powerful but has a notoriously complex syntax, so UFW was built to simplify the most common firewall management tasks into readable commands.

---

### YAML Comments

YAML supports comments using the `#` symbol. Anything after `#` on a line is ignored by the parser.

```yaml
# This is a full-line comment

services:
  app:
    image: your-app:latest  # This is an inline comment
    restart: unless-stopped

    environment:
      # Group related env vars with a header comment for readability
      - NODE_ENV=production
      - PORT=3000
```

**You cannot comment inside multi-line strings.** If you use `|` or `>` for block scalars, `#` is treated as literal text — not a comment:

```yaml
message: |
  Hello world
  # This is NOT a comment — it is part of the string value
```

**To disable a line, comment out the whole line:**

```yaml
environment:
  # - DEBUG=true    <- correct way to "comment out" a value
  - NODE_ENV=production
```

**There are no block comments.** Every commented line needs its own `#` — there is no `/* */` equivalent in YAML.

---

### chmod — File Permissions

`chmod` stands for **change mode**. It controls read, write, and execute permissions for files and directories.

#### The Three Permission Groups

| Symbol | Group |
|---|---|
| `u` | **user** — the file owner |
| `g` | **group** — users in the file's group |
| `o` | **others** — everyone else |
| `a` | **all** — shorthand for u+g+o |

#### The Three Permission Types

| Symbol | Numeric | Meaning on a file | Meaning on a directory |
|---|---|---|---|
| `r` | 4 | Read the file | List directory contents |
| `w` | 2 | Write / modify the file | Create, delete, rename files inside |
| `x` | 1 | Execute the file | Enter (`cd`) the directory |

#### Numeric (Octal) Mode

Each group gets a number from 0–7, calculated by adding the values:

| Number | Permissions | Meaning |
|---|---|---|
| `0` | `---` | No permissions |
| `1` | `--x` | Execute only |
| `2` | `-w-` | Write only |
| `3` | `-wx` | Write + Execute |
| `4` | `r--` | Read only |
| `5` | `r-x` | Read + Execute |
| `6` | `rw-` | Read + Write |
| `7` | `rwx` | Read + Write + Execute |

So `chmod 755 file` means:
- `7` → owner: rwx
- `5` → group: r-x
- `5` → others: r-x

#### Common chmod Values You'll Actually Use

| Command | Permissions | Typical Use |
|---|---|---|
| `chmod 400` | `r--------` | Private key files (read-only by owner) |
| `chmod 600` | `rw-------` | SSH keys, `acme.json`, private configs |
| `chmod 644` | `rw-r--r--` | Regular files — owner writes, others read |
| `chmod 700` | `rwx------` | Private directories (e.g. `.ssh/`) |
| `chmod 755` | `rwxr-xr-x` | Public scripts/directories — owner writes, others execute |
| `chmod 777` | `rwxrwxrwx` | Full access for everyone — **avoid in production** |

#### Symbolic Mode

Instead of numbers, you can use letters:

```bash
chmod u+x file         # Add execute for owner
chmod g-w file         # Remove write from group
chmod o=r file         # Set others to read-only exactly
chmod a+x file         # Add execute for everyone
chmod u+x,g-w file     # Multiple changes at once
chmod +x file          # Shorthand — adds execute for all
```

#### Recursive (`-R`)

```bash
chmod -R 755 /var/www    # Apply to the directory and everything inside it
```

Use with care — it applies the same permission to both files and directories, which is often not what you want for files specifically.

#### How to Read Existing Permissions

```bash
ls -la
```

Output like `-rw-r--r--` breaks down as:

```
- rw- r-- r--
│  │   │   └── others: read only
│  │   └────── group: read only
│  └────────── owner: read + write
└───────────── file type (- = file, d = directory, l = symlink)
```

---

## 15. Secrets Management

Environment variables in compose files are convenient but dangerous if mishandled. This section covers the right way to handle secrets at every level.

### 15.1 The `.env` File Pattern

Never hardcode secrets directly in `compose.yml`. Use a `.env` file that compose automatically loads:

```bash
# .env — lives next to compose.yml, NEVER committed to git
POSTGRES_PASSWORD=supersecretpassword
GRAFANA_PASSWORD=anothersecretpassword
JWT_SECRET=your-jwt-secret
```

Reference them in `compose.yml`:

```yaml
services:
  app:
    image: your-app
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}   # Pulled from .env at runtime
      - JWT_SECRET=${JWT_SECRET}
```

Add `.env` to `.gitignore` immediately:

```bash
echo ".env" >> .gitignore
```

Provide a `.env.example` with placeholder values so others know what to fill in:

```bash
# .env.example — safe to commit; no real values
POSTGRES_PASSWORD=
GRAFANA_PASSWORD=
JWT_SECRET=
```

### 15.2 Docker Secrets (Swarm Mode)

For production-grade secret management without external tools, Docker Swarm has a built-in secrets engine. Secrets are stored encrypted and only injected into containers that explicitly request them.

```bash
# Create a secret from a value
echo "supersecretpassword" | docker secret create postgres_password -

# Create from a file
docker secret create ssl_cert ./cert.pem

# List secrets
docker secret ls

# Remove a secret
docker secret rm postgres_password
```

Use in a stack compose file:

```yaml
services:
  db:
    image: postgres:16
    secrets:
      - postgres_password   # Secret is mounted at /run/secrets/postgres_password inside the container
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password   # Postgres reads the file instead of a plain env var

secrets:
  postgres_password:
    external: true   # Secret was created via docker secret create, not defined here
```

### 15.3 Using `--env-file` Explicitly

If you have multiple environments, you can specify which env file to load:

```bash
docker compose --env-file .env.production up -d
docker compose --env-file .env.staging up -d
```

### 15.4 HashiCorp Vault (Advanced)

For teams or multi-service architectures, Vault is the industry standard for secrets management. It provides dynamic secrets, fine-grained access control, and full audit logging.

```bash
# Install Vault CLI
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install vault

# Write a secret
vault kv put secret/myapp db_password="supersecret"

# Read a secret
vault kv get secret/myapp

# Read a specific field
vault kv get -field=db_password secret/myapp
```

Apps can pull secrets at startup via the Vault API or the `vault` CLI in an entrypoint script — secrets never touch environment variables or disk.

### 15.5 Common Mistakes to Avoid

| Mistake | Fix |
|---|---|
| Committing `.env` to git | Add to `.gitignore` immediately |
| Printing secrets in CI logs | Use `::add-mask::` in GitHub Actions or mask env vars in your CI provider |
| Secrets in Docker image layers | Never use `ENV` or `ARG` for secrets in Dockerfiles — pass at runtime only |
| Secrets in `docker inspect` output | Use Docker Secrets or Vault — env vars are visible in inspect output |

---

## 16. SSL — Wildcard Certs & DNS Challenge

Let's Encrypt's default HTTP challenge works for single subdomains but has two limitations: it requires port 80 to be publicly accessible, and it cannot issue wildcard certificates (`*.yourdomain.com`). For wildcards, you need a DNS challenge.

### 16.1 When to Use DNS Challenge

- You want a wildcard cert covering all subdomains
- Port 80 is not publicly accessible
- You're provisioning certs for internal/private services
- You've hit Let's Encrypt's rate limit (5 certs per registered domain per week)

### 16.2 Configure Traefik for DNS Challenge (Cloudflare Example)

Add your DNS provider API token as an environment variable:

```bash
# In your traefik .env file
CF_DNS_API_TOKEN=your-cloudflare-api-token
```

Update `traefik.yml`:

```yaml
certificatesResolvers:
  letsencrypt:
    acme:
      email: your-email@example.com
      storage: /acme.json
      # Switch from httpChallenge to dnsChallenge
      dnsChallenge:
        provider: cloudflare          # Traefik has built-in support for 100+ DNS providers
        resolvers:
          - "1.1.1.1:53"             # Use Cloudflare's resolver to verify propagation
          - "8.8.8.8:53"
        delayBeforeCheck: 30s         # Wait for DNS propagation before checking
```

Update `compose.yml` to pass the API token into the Traefik container:

```yaml
services:
  traefik:
    image: traefik:v3.0
    environment:
      - CF_DNS_API_TOKEN=${CF_DNS_API_TOKEN}   # Traefik reads this to make DNS API calls
    # ... rest of config
```

### 16.3 Using a Wildcard Cert for All Services

In your app labels, reference the wildcard cert resolver:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.app.rule=Host(`app.yourdomain.com`)"
  - "traefik.http.routers.app.entrypoints=websecure"
  - "traefik.http.routers.app.tls=true"
  - "traefik.http.routers.app.tls.certresolver=letsencrypt"
  # Tell Traefik to use the wildcard domain for this cert
  - "traefik.http.routers.app.tls.domains[0].main=yourdomain.com"
  - "traefik.http.routers.app.tls.domains[0].sans=*.yourdomain.com"
```

### 16.4 Supported DNS Providers

Traefik natively supports Cloudflare, Route53, DigitalOcean, Namecheap, GoDaddy, and 100+ others. Check the [Traefik docs](https://doc.traefik.io/traefik/https/acme/#providers) for the correct environment variable names per provider.

---

## 17. Health Checks

Docker health checks allow the engine to distinguish between a container that is *running* and one that is *actually healthy and responding*. Without them, Docker considers a container healthy the moment it starts — even if the app inside is crashing in a loop.

### 17.1 Adding Health Checks to Compose Services

```yaml
services:
  app:
    image: your-app
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]   # Command to run; non-zero exit = unhealthy
      interval: 30s       # How often to run the check
      timeout: 10s        # How long to wait before marking the check as failed
      retries: 3          # How many consecutive failures before marking the container unhealthy
      start_period: 15s   # Grace period on startup before health checks begin counting
```

### 17.2 Health Check for Common Services

**Postgres:**

```yaml
  db:
    image: postgres:16
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s   # Postgres takes time to initialize on first boot
```

**Redis:**

```yaml
  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]   # Returns PONG if Redis is ready
      interval: 10s
      timeout: 5s
      retries: 3
```

**Nginx / HTTP service:**

```yaml
  nginx:
    image: nginx:alpine
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 17.3 Using Health Checks in `depends_on`

By default, `depends_on` only waits for a container to *start*, not to be *healthy*. Fix this:

```yaml
services:
  app:
    image: your-app
    depends_on:
      db:
        condition: service_healthy   # Wait until db passes its health check before starting app
      redis:
        condition: service_healthy

  db:
    image: postgres:16
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      retries: 5
```

### 17.4 Checking Health Status

```bash
docker ps                          # HEALTH column shows: healthy, unhealthy, or starting
docker inspect --format='{{json .State.Health}}' container-name   # Full health check history
```

---

## 18. Container Resource Limits

Without resource limits, a single misbehaving container can consume all CPU and RAM on the VPS, taking down every other service. Always set limits in production.

### 18.1 Setting Limits in Compose

```yaml
services:
  app:
    image: your-app
    deploy:
      resources:
        limits:
          cpus: '0.50'       # Max 50% of one CPU core
          memory: 512M       # Hard memory ceiling — container is killed if it exceeds this
        reservations:
          cpus: '0.25'       # Guaranteed minimum CPU allocation
          memory: 256M       # Guaranteed minimum memory allocation
```

> **Note:** `deploy.resources` works with `docker compose up` as well as Docker Swarm. For standalone compose without Swarm, you can also use the older `mem_limit` and `cpus` keys directly under the service.

```yaml
services:
  app:
    image: your-app
    mem_limit: 512m      # Alternative syntax for non-Swarm compose
    cpus: 0.5
```

### 18.2 Limits for the Monitoring Stack

Monitoring services are notorious for consuming excessive resources if unchecked:

```yaml
services:
  elasticsearch:
    deploy:
      resources:
        limits:
          memory: 1G         # Elasticsearch is the most memory-hungry — tune to your VPS
        reservations:
          memory: 512M

  prometheus:
    deploy:
      resources:
        limits:
          memory: 256M

  grafana:
    deploy:
      resources:
        limits:
          memory: 256M

  loki:
    deploy:
      resources:
        limits:
          memory: 256M
```

### 18.3 Check Live Resource Usage

```bash
docker stats                          # Live view of all containers
docker stats container-name           # Single container
docker stats --no-stream              # One-shot snapshot instead of live feed
```

---

## 19. Running Postgres in Docker

Postgres has specific quirks when containerised — volume permissions, connection limits, and safe exposure all need to be handled correctly.

### 19.1 Basic Postgres Compose

```yaml
services:
  db:
    image: postgres:16-alpine          # Alpine variant is significantly smaller
    container_name: postgres
    restart: unless-stopped
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data   # NEVER use a bind mount for Postgres data — use a named volume
    networks:
      - traefik-network                # Keep on the app network; do NOT expose port 5432 publicly
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    deploy:
      resources:
        limits:
          memory: 512M

volumes:
  postgres_data:
```

> **Never expose port 5432 to the public internet.** If you need remote access, tunnel over SSH: `ssh -L 5432:localhost:5432 user@vps-ip`

### 19.2 PgBouncer — Connection Pooling

By default, Postgres creates a new OS process per connection. Under load, this becomes a bottleneck. PgBouncer sits in front of Postgres and pools connections efficiently.

```yaml
  pgbouncer:
    image: bitnami/pgbouncer:latest
    container_name: pgbouncer
    restart: unless-stopped
    environment:
      - POSTGRESQL_HOST=db                        # Point at the Postgres container
      - POSTGRESQL_PORT=5432
      - POSTGRESQL_USERNAME=${POSTGRES_USER}
      - POSTGRESQL_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRESQL_DATABASE=${POSTGRES_DB}
      - PGBOUNCER_POOL_MODE=transaction           # transaction mode is best for most web apps
      - PGBOUNCER_MAX_CLIENT_CONN=100             # Max connections PgBouncer accepts from apps
      - PGBOUNCER_DEFAULT_POOL_SIZE=20            # Max actual connections to Postgres
    networks:
      - traefik-network
    depends_on:
      db:
        condition: service_healthy
```

Your app should then connect to `pgbouncer:5432` instead of `db:5432`.

### 19.3 Connecting Remotely via SSH Tunnel

```bash
# Forward local port 5433 to Postgres on the VPS (avoids exposing 5432 publicly)
ssh -L 5433:localhost:5432 username@<vps-ip> -N

# Now connect your local Postgres client to localhost:5433
psql -h localhost -p 5433 -U your-db-user your-db-name
```

### 19.4 Common Postgres Gotchas

| Problem | Cause | Fix |
|---|---|---|
| `permission denied` on data directory | Volume created as root before Postgres init | Delete the volume and let Postgres recreate it |
| App connects before DB is ready | `depends_on` doesn't wait for healthy | Use `condition: service_healthy` in `depends_on` |
| Too many connections error | No connection pooling | Add PgBouncer in front of Postgres |
| Data lost after `docker compose down -v` | `-v` flag removes volumes | Never use `-v` in production unless intentional |

---

## 20. Swap Space

Swap acts as overflow RAM — when physical memory is exhausted, the kernel moves less-used pages to swap on disk. It's slower than RAM but prevents OOM kills that take down your services.

Especially important when running Elasticsearch or the ELK stack on a lower-RAM VPS.

### 20.1 Create and Enable a Swapfile

```bash
# Create a 2GB swapfile (adjust size to your needs — typically 1x or 2x your RAM)
sudo fallocate -l 2G /swapfile

# Secure the swapfile — only root should be able to read it
sudo chmod 600 /swapfile

# Format it as swap space
sudo mkswap /swapfile

# Enable it immediately (takes effect without reboot)
sudo swapon /swapfile

# Verify
sudo swapon --show
free -h
```

### 20.2 Make Swap Persistent Across Reboots

```bash
# Add to /etc/fstab so swap is re-enabled on boot
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 20.3 Tune Swappiness

`swappiness` controls how aggressively the kernel moves data to swap (0 = only when RAM is completely full, 100 = swap aggressively).

```bash
# Check current value (default is usually 60)
cat /proc/sys/vm/swappiness

# Set to 10 — only swap when really necessary (recommended for servers)
sudo sysctl vm.swappiness=10
```

Make it permanent (see Section 21).

### 20.4 Resize or Remove Swap

```bash
# Disable swap
sudo swapoff /swapfile

# Remove the file
sudo rm /swapfile

# Remove from /etc/fstab as well
sudo nvim /etc/fstab
```

---

## 21. Kernel Parameter Tuning

`sysctl` controls kernel parameters at runtime. Changes made with `sysctl -w` are temporary — they reset on reboot. To make them permanent, write them to `/etc/sysctl.conf` or a file in `/etc/sysctl.d/`.

### 21.1 Making Parameters Permanent

```bash
# Temporary (lost on reboot)
sudo sysctl -w vm.max_map_count=262144

# Permanent — add to sysctl config
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.d/99-custom.conf

# Apply the file without rebooting
sudo sysctl -p /etc/sysctl.d/99-custom.conf
```

### 21.2 Common Parameters for VPS Deployments

```bash
# /etc/sysctl.d/99-vps.conf

# Required for Elasticsearch — sets max virtual memory map count
vm.max_map_count=262144

# Swap tuning — only swap when really necessary (0-100; lower = less aggressive)
vm.swappiness=10

# Keep more filesystem metadata in cache — improves disk performance
vm.vfs_cache_pressure=50

# Increase system-wide file descriptor limits — important for high-traffic apps
fs.file-max=100000

# TCP tuning — increase backlog for high-connection workloads
net.core.somaxconn=65535
net.ipv4.tcp_max_syn_backlog=65535

# Reuse TIME_WAIT sockets faster — helps under heavy connection load
net.ipv4.tcp_tw_reuse=1

# Enable TCP keepalives to detect dead connections faster
net.ipv4.tcp_keepalive_time=600
net.ipv4.tcp_keepalive_intvl=60
net.ipv4.tcp_keepalive_probes=3
```

Apply all:

```bash
sudo sysctl -p /etc/sysctl.d/99-vps.conf
```

### 21.3 File Descriptor Limits (ulimits)

Alongside kernel params, you may need to raise the per-process file descriptor limit:

```bash
# Check current limit
ulimit -n

# Raise temporarily
ulimit -n 65535

# Raise permanently — add to /etc/security/limits.conf
echo "* soft nofile 65535" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65535" | sudo tee -a /etc/security/limits.conf
```

In Docker compose, set per-container ulimits:

```yaml
services:
  elasticsearch:
    ulimits:
      nofile:
        soft: 65535   # Soft limit — the default; can be raised up to the hard limit
        hard: 65535   # Hard limit — the ceiling; requires root to raise further
      memlock:
        soft: -1      # -1 means unlimited
        hard: -1
```

---

## 22. Zero Downtime & Rolling Deployments

A standard `docker compose up -d` causes a brief outage — the old container stops before the new one starts. Zero-downtime deployment keeps the old container alive and serving traffic until the new one is healthy.

### 22.1 How It Works with Traefik

Traefik watches Docker events in real time. When a new container starts and passes its health check, Traefik begins routing to it. When the old container stops, Traefik removes it from the pool. If you run two containers simultaneously during the transition, there is no gap in service.

### 22.2 Zero Downtime Deploy Script

```bash
#!/bin/bash
# deploy.sh — zero downtime deployment using docker compose scale

set -e   # Exit immediately on any error

SERVICE=app          # The compose service name to deploy
IMAGE=your-app:latest

echo "Pulling latest image..."
docker compose pull $SERVICE

echo "Scaling up — starting new container alongside old one..."
docker compose up -d --no-deps --scale $SERVICE=2 --no-recreate $SERVICE
# --no-deps: don't restart linked services
# --scale: run 2 instances simultaneously
# --no-recreate: don't touch the existing container

echo "Waiting for new container to become healthy..."
sleep 15   # Adjust based on your app's startup time; or poll health endpoint

echo "Scaling back down — removing old container..."
docker compose up -d --no-deps --scale $SERVICE=1 --no-recreate $SERVICE

echo "Cleaning up old images..."
docker image prune -f

echo "Deployment complete."
```

### 22.3 Zero Downtime in GitHub Actions

Update your deploy step in `.github/workflows/deploy.yml`:

```yaml
      - name: Deploy to VPS with zero downtime
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          port: ${{ secrets.VPS_PORT }}
          script: |
            cd ~/your-app

            # Pull the new image first
            docker compose pull app

            # Start a second instance of the app container
            docker compose up -d --no-deps --scale app=2 --no-recreate app

            # Wait for the new instance to pass its health check
            sleep 20

            # Remove the old instance — Traefik will stop routing to it automatically
            docker compose up -d --no-deps --scale app=1 --no-recreate app

            # Clean up old image layers
            docker image prune -f
```

### 22.4 True Blue-Green Deployment

For larger applications, blue-green deployment maintains two complete environments (blue = live, green = staging) and flips traffic between them with zero interruption.

```bash
# blue and green are separate compose profiles or stacks

# Deploy to green while blue is live
docker compose -f compose.green.yml up -d

# Wait for green to pass health checks
sleep 30

# Update Traefik to route to green (swap the label on the router)
# This is done by updating the active compose file Traefik is watching

# Shut down blue
docker compose -f compose.blue.yml down

# On the next deploy, blue becomes the target again
```

A simpler approach using Traefik labels — swap which stack has `traefik.enable=true`:

```bash
#!/bin/bash
# blue_green_deploy.sh

ACTIVE=$(cat /tmp/active_env 2>/dev/null || echo "blue")

if [ "$ACTIVE" = "blue" ]; then
  NEXT="green"
else
  NEXT="blue"
fi

echo "Deploying to $NEXT..."
docker compose -f compose.$NEXT.yml up -d

echo "Waiting for $NEXT to become healthy..."
sleep 20

echo "Switching traffic from $ACTIVE to $NEXT..."
# Disable Traefik routing on old stack
docker compose -f compose.$ACTIVE.yml down

echo "$NEXT" > /tmp/active_env
echo "Deployment complete. Active: $NEXT"
```

### 22.5 Health Check Polling (More Reliable Than `sleep`)

Instead of a fixed `sleep`, poll your health endpoint until it responds:

```bash
#!/bin/bash
# wait_healthy.sh — wait for a service to respond before proceeding

URL="https://app.yourdomain.com/health"
MAX_ATTEMPTS=30
INTERVAL=5

for i in $(seq 1 $MAX_ATTEMPTS); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$URL")

  if [ "$STATUS" = "200" ]; then
    echo "Service is healthy after $((i * INTERVAL)) seconds."
    exit 0
  fi

  echo "Attempt $i/$MAX_ATTEMPTS — status $STATUS. Retrying in ${INTERVAL}s..."
  sleep $INTERVAL
done

echo "Service did not become healthy in time. Aborting."
exit 1
```

---

## 23. SSH Jump Hosts & Bastion Servers

When managing multiple VPS instances, a bastion server acts as the single entry point into your infrastructure. You SSH into the bastion first, then jump from there to internal servers — none of which are exposed directly to the internet.

### 23.1 The Pattern

```
Your machine → Bastion (public IP, port 22) → Internal Server A (private IP only)
                                              → Internal Server B (private IP only)
                                              → Internal Server C (private IP only)
```

Internal servers have no public IP and no SSH port exposed — only the bastion does.

### 23.2 One-Liner Jump (No Config)

```bash
# SSH to internal-server via bastion in one command
ssh -J user@bastion-ip user@internal-server-ip

# -J: ProxyJump — connect through bastion transparently
```

### 23.3 SSH Config for Persistent Setup

Add to `~/.ssh/config` on your local machine:

```
# The bastion — your one public-facing entry point
Host bastion
  HostName <bastion-public-ip>
  User username
  IdentityFile ~/.ssh/id_ed25519
  ServerAliveInterval 60   # Send keepalives every 60s to prevent timeout

# Internal server — accessed via the bastion
Host app-server
  HostName <internal-private-ip>
  User username
  IdentityFile ~/.ssh/id_ed25519
  ProxyJump bastion          # Automatically jump through bastion

Host db-server
  HostName <internal-private-ip>
  User username
  IdentityFile ~/.ssh/id_ed25519
  ProxyJump bastion
```

Now connect directly with:

```bash
ssh app-server    # SSH client handles the jump automatically
ssh db-server
```

### 23.4 SCP and Rsync Through a Bastion

```bash
# Copy a file to an internal server via bastion
scp -J bastion ./file.txt app-server:/home/username/

# Rsync through a bastion
rsync -avz -e "ssh -J bastion" ./local-dir/ app-server:/home/username/remote-dir/
```

### 23.5 Port Forwarding Through a Bastion

```bash
# Forward local port 5432 → db-server's Postgres, via bastion
ssh -J bastion -L 5432:<db-server-private-ip>:5432 username@<db-server-private-ip> -N

# -N: don't execute a remote command — just maintain the tunnel
# Now connect your local psql to localhost:5432
```

### 23.6 Hardening the Bastion

The bastion is your most exposed server — harden it aggressively:

```bash
# On the bastion — allow SSH only from your home/office IP
sudo ufw allow from <your-ip> to any port 22
sudo ufw default deny incoming
sudo ufw enable

# Disable password auth, root login, and PAM (same as Section 2)
# Install Fail2Ban (same as Section 10)
# Consider rate limiting: sudo ufw limit 22
```

---

## 24. Nginx — Alternative to Traefik

Traefik is excellent for Docker-native setups where routing config lives in container labels. Nginx is the alternative — battle-tested, widely documented, and preferred when you want explicit control over every routing rule in a single config file.

### 24.1 Traefik vs Nginx at a Glance

| | Traefik | Nginx |
|---|---|---|
| Config location | Docker labels per container | Central config file |
| SSL auto-provisioning | Built-in via ACME | Requires Certbot separately |
| Dynamic routing | Automatic on container start | Requires reload on change |
| Learning curve | Lower for Docker setups | Steeper but more flexible |
| Load balancing | Built-in | Built-in |
| Best for | Docker-first setups | Fine-grained control, static sites |

### 24.2 Install Nginx Directly (No Docker)

```bash
sudo apt install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 24.3 Basic Reverse Proxy Config

```nginx
# /etc/nginx/sites-available/app.yourdomain.com

server {
    listen 80;
    server_name app.yourdomain.com;

    # Redirect all HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name app.yourdomain.com;

    # SSL certificates (managed by Certbot — see 24.4)
    ssl_certificate /etc/letsencrypt/live/app.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.yourdomain.com/privkey.pem;

    # Modern SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    # Proxy all requests to your app container on port 3000
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;           # Required for WebSocket support
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;          # Pass the real client IP to your app
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/app.yourdomain.com /etc/nginx/sites-enabled/
sudo nginx -t          # Test config for syntax errors before applying
sudo systemctl reload nginx
```

### 24.4 SSL with Certbot

```bash
# Install Certbot with the Nginx plugin
sudo apt install certbot python3-certbot-nginx -y

# Provision and auto-configure SSL for your domain
sudo certbot --nginx -d app.yourdomain.com

# Certbot installs a cron job to auto-renew certs — verify it works
sudo certbot renew --dry-run
```

### 24.5 Nginx in Docker (with Traefik or Standalone)

If you prefer to run Nginx in Docker but without Traefik:

```yaml
services:
  nginx:
    image: nginx:alpine
    container_name: nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro              # Mount your config as read-only
      - ./sites:/etc/nginx/sites-enabled:ro                # Mount site configs
      - certbot_certs:/etc/letsencrypt                     # Share certs with Certbot container
      - certbot_www:/var/www/certbot                       # ACME challenge directory
    networks:
      - app-network

  certbot:
    image: certbot/certbot
    container_name: certbot
    volumes:
      - certbot_certs:/etc/letsencrypt                     # Write certs here
      - certbot_www:/var/www/certbot                       # Certbot uses this for HTTP challenge
    # Run cert renewal — wire this to a cron job
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"

volumes:
  certbot_certs:
  certbot_www:
```

---

---

## 25. Docker Volumes — The Full Picture

There are three ways Docker handles persistent data. Understanding the difference prevents data loss and permission headaches.

### 25.1 Named Volumes

```yaml
services:
  db:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data   # named_volume:container_path

volumes:
  postgres_data:   # Declaring it here makes Docker manage it as a named volume
```

Docker creates and manages this volume entirely. It lives at `/var/lib/docker/volumes/postgres_data/_data` on the host, but you're not meant to touch it directly — Docker owns it.

**Key behaviours:**
- Survives `docker compose down` — containers are removed but the volume stays
- Destroyed only by `docker compose down -v` or `docker volume rm postgres_data`
- Docker handles permissions correctly on first init — this is why Postgres works better with named volumes than bind mounts
- Can be backed up, inspected, and moved

---

### 25.2 Bind Mounts

```yaml
services:
  app:
    volumes:
      - ./config:/app/config                              # relative host path:container path
      - /etc/nginx/nginx.conf:/etc/nginx/nginx.conf:ro   # absolute path; :ro = read-only inside container
```

A bind mount directly maps a path on your host machine into the container. Whatever exists at that host path is exactly what the container sees — in real time, both directions.

**Key behaviours:**
- Changes on the host immediately reflect inside the container and vice versa
- Useful for config files, source code in development, and log directories
- `:ro` makes the mount read-only inside the container — the host can still write to it
- Permissions can be tricky — the container process runs as a specific UID, and if the host folder is owned by a different user, you'll get permission denied errors

---

### 25.3 Anonymous Volumes

```yaml
services:
  app:
    volumes:
      - /app/node_modules   # No name, no host path — just a container-internal path
```

Docker creates a volume with a random hash name. It's not declared in the `volumes:` block, you can't reference it by name, and it's basically unmanageable. Avoid in production — mostly a development pattern.

---

### 25.4 Seeing the Difference

```yaml
services:
  app:
    volumes:
      - mydata:/app/data      # Named — you can reference "mydata" anywhere
      - /app/cache            # Anonymous — Docker gives it a random hash name

volumes:
  mydata:                     # Only named volumes need to be declared here
```

```bash
docker volume ls

# DRIVER    VOLUME NAME
# local     mydata                     ← named — identifiable and manageable
# local     a3f9b1c2d4e5f6...         ← anonymous — impossible to track
```

---

### 25.5 The `volumes:` Declaration Block

This trips people up constantly. The `volumes:` block at the bottom of a compose file is a **declaration**, not a creation command:

```yaml
volumes:
  postgres_data:    # Tell compose this volume exists and should be managed
  grafana_data:
  loki_data:
```

- If you reference a named volume in a service but forget to declare it here, compose throws an error
- If you declare it and the volume doesn't exist yet, Docker creates it on `docker compose up`
- If the volume already exists, Docker uses it as-is — **it never overwrites existing data**

The `external: true` flag tells compose the volume was created manually and should not be touched:

```yaml
volumes:
  my_volume:
    external: true   # Created with docker volume create — compose won't manage or delete it
```

---

### 25.6 Sharing a Volume Between Services

You can mount the same named volume in multiple containers simultaneously:

```yaml
services:
  app:
    volumes:
      - shared_uploads:/app/uploads       # App writes files here

  nginx:
    volumes:
      - shared_uploads:/usr/share/nginx/html/uploads   # Nginx serves those same files

volumes:
  shared_uploads:
```

Both containers read and write to the same underlying directory on the host. Useful for serving user-uploaded files via Nginx while your app handles the writes.

---

### 25.7 Common Gotchas

**`docker compose down -v` deletes your data permanently.** The `-v` flag removes all volumes declared in the compose file. Never run this in production unless you intend to wipe state.

**Volume data wins over image data.** If a path is mounted as a volume and your image also writes to that path during build, the volume always takes precedence. The container sees whatever is in the volume, not what the image put there. This means if you change a config file that's baked into your image but that path is also mounted as a volume, the old volume data will override it — you'd need to delete the volume and let Docker reinitialise.

**Named volumes and Postgres.** Postgres initialises its data directory on first boot. If you use a bind mount pointing to an existing non-empty directory, Postgres refuses to start. Named volumes start empty and let Postgres initialise them correctly.

**Permissions with bind mounts.** Container processes often run as a non-root user (e.g. UID 1000). If the host directory is owned by root or a different UID, the container process can't write to it. Fix by either changing the host directory ownership or configuring the container to run as a matching UID.

---

## 26. When to Use Each Volume Type

### Named Volume — Use when:

**The data needs to outlive the container and you don't need to edit it directly from the host.**

This is your default for anything stateful:

```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data   # Database data
  - grafana_data:/var/lib/grafana            # Dashboard settings
  - loki_data:/loki                          # Log chunks
  - elasticsearch_data:/usr/share/elasticsearch/data
```

The rule of thumb: if losing this data would be a problem, use a named volume. Docker manages permissions on init, it survives container restarts and removals, and it's easy to back up.

---

### Bind Mount — Use when:

**You need the host and container to share a file or directory in real time, and you own that file.**

**Config files** — you write it on the host, the container reads it:

```yaml
- ./traefik.yml:/traefik.yml:ro
- ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
- ./nginx.conf:/etc/nginx/nginx.conf:ro
```

**Development** — live code reload without rebuilding the image:

```yaml
- ./src:/app/src    # Edit locally, container sees changes instantly
```

**Log directories** — app writes logs into the container, you read them on the host:

```yaml
- ./logs:/app/logs
```

**Docker socket** — giving a container access to the Docker engine:

```yaml
- /var/run/docker.sock:/var/run/docker.sock:ro   # Used by Traefik, cAdvisor
```

The key distinction from named volumes: **you own and manage the source on the host**. Docker is just making it visible inside the container.

---

### Anonymous Volume — Use when:

Almost never in production. The one legitimate use case is **protecting a directory inside a container from being overwritten by a bind mount** — the classic `node_modules` pattern in development:

```yaml
services:
  app:
    volumes:
      - .:/app                  # Bind mount your entire project into the container
      - /app/node_modules       # Protect node_modules from being wiped by the bind mount above
```

Without that second line, the bind mount of `.` would overwrite `node_modules` that were installed inside the container during image build, because your local machine likely doesn't have them. The anonymous volume tells Docker to preserve whatever was in that path from the image.

Outside of this pattern, avoid anonymous volumes. You can't name them, reference them, back them up, or clean them up reliably.

---

### The Decision Tree

```
Does this data need to persist across container restarts?
├── No  → Don't use a volume at all
└── Yes → Do you need to read or edit this from the host in real time?
           ├── Yes → Bind mount   (config files, dev code, logs, docker socket)
           └── No  → Named volume (databases, app state, certs, dashboards)
                      Special case: protecting a path from a bind mount → anonymous volume
```

---

## 27. Docker Networking

Docker networking is what allows containers to talk to each other, to the host, and to the outside world. Understanding it explains why things like `external: true` on networks are necessary and why a container in one compose file can't reach a container in another by default.

### 27.1 How Container Networking Works

Every container gets its own virtual network interface. When containers are on the same Docker network, they can reach each other by **container name** — Docker has a built-in DNS resolver that maps names to internal IPs automatically. This is why you write `http://db:5432` instead of `http://172.18.0.3:5432` in your app config.

When containers are on **different** networks, they cannot communicate at all — even if they're on the same host. This is intentional isolation.

### 27.2 Network Drivers

**bridge (default)** — Creates a private internal network on the host. Containers on the same bridge network can talk to each other by name. Traffic to the outside world goes through NAT. This is what you use for almost everything on a single VPS.

```yaml
networks:
  app-network:
    driver: bridge   # This is the default — you don't need to specify it explicitly
```

**host** — Removes network isolation entirely. The container shares the host's network stack directly — no port mapping needed, but no isolation either. Useful for high-performance scenarios or when a tool needs direct access to host interfaces (e.g. some monitoring agents).

```yaml
services:
  app:
    network_mode: host   # Container uses the host's network directly
```

**overlay** — Used in Docker Swarm for multi-host networking. Allows containers on different physical machines to communicate as if they were on the same network. Not needed for single-VPS setups.

**none** — Completely disables networking for the container. For isolated batch jobs or security-sensitive workloads that should never touch the network.

### 27.3 Why Containers in Different Compose Files Can't Talk

Each compose project creates its own default network. A container in `~/app/compose.yml` and a container in `~/monitoring/compose.yml` are on completely separate networks and cannot reach each other — even by container name.

The fix is a shared external network that both compose files reference:

```bash
# Create it once manually
docker network create traefik-network
```

Both compose files then declare it as external:

```yaml
# In ~/app/compose.yml AND ~/monitoring/compose.yml
networks:
  traefik-network:
    external: true   # Both files use the same pre-existing network — containers can now reach each other
```

This is exactly why every service in this guide uses `traefik-network` — it's the shared backbone that lets Traefik route to any container regardless of which compose file it lives in.

### 27.4 Inspecting Networks

```bash
docker network ls                              # List all networks
docker network inspect traefik-network         # See all containers connected and their IPs
docker network connect traefik-network my-container   # Connect a running container to a network
docker network disconnect traefik-network my-container
```

### 27.5 Exposing Ports — `ports` vs `expose`

These two are commonly confused:

```yaml
services:
  app:
    ports:
      - "3000:3000"   # host_port:container_port — publishes to the HOST; accessible from outside
    expose:
      - "3000"        # Only visible to other containers on the same network — NOT accessible from outside
```

The key insight: **if your container is behind Traefik, you almost never need `ports`**. Traefik reaches your container over the internal Docker network using `expose`. Using `ports` unnecessarily punches a hole in your firewall and bypasses Traefik entirely.

Only use `ports` for:
- Traefik itself (80, 443)
- Services you intentionally want accessible directly without a reverse proxy (e.g. Loki's push endpoint on 3100)
- Local development

---

## 28. Environment-Specific Compose Files

As soon as you have more than one environment — local dev, staging, production — putting everything in a single `compose.yml` becomes messy. Docker Compose has a built-in override system designed exactly for this.

### 28.1 How Overrides Work

Compose automatically merges files in this order:

1. `compose.yml` — base config, shared across all environments
2. `compose.override.yml` — automatically loaded on top of base (usually dev overrides)

You can also specify files explicitly with `-f`.

### 28.2 The Pattern

**`compose.yml` — base, shared config:**

```yaml
# Defines the service structure but no environment-specific values
services:
  app:
    image: your-app:${IMAGE_TAG:-latest}   # Tag comes from env; default to latest
    restart: unless-stopped
    networks:
      - traefik-network
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    restart: unless-stopped
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - traefik-network

volumes:
  postgres_data:

networks:
  traefik-network:
    external: true
```

**`compose.override.yml` — development overrides (auto-loaded locally):**

```yaml
# This file is gitignored in production — only used locally
services:
  app:
    build: .                          # Build from local Dockerfile instead of pulling image
    volumes:
      - ./src:/app/src                # Live code reload
    environment:
      - NODE_ENV=development
      - DEBUG=true
    ports:
      - "3000:3000"                   # Expose directly for local access without Traefik

  db:
    ports:
      - "5432:5432"                   # Expose Postgres locally for DB tools like TablePlus
    environment:
      - POSTGRES_PASSWORD=devpassword
```

**`compose.prod.yml` — production config:**

```yaml
services:
  app:
    environment:
      - NODE_ENV=production
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.app.rule=Host(`app.yourdomain.com`)"
      - "traefik.http.routers.app.entrypoints=websecure"
      - "traefik.http.routers.app.tls.certresolver=letsencrypt"
    deploy:
      resources:
        limits:
          memory: 512M
    logging:
      driver: loki
      options:
        loki-url: "http://localhost:3100/loki/api/v1/push"
        loki-external-labels: "app=your-app,env=production"
```

### 28.3 Running Each Environment

```bash
# Local dev — compose.yml + compose.override.yml merged automatically
docker compose up -d

# Production — compose.yml + compose.prod.yml merged explicitly
docker compose -f compose.yml -f compose.prod.yml up -d

# Staging
docker compose -f compose.yml -f compose.staging.yml up -d
```

### 28.4 In CI/CD

Update your deploy workflow to use the production file:

```yaml
script: |
  cd ~/your-app
  docker compose -f compose.yml -f compose.prod.yml pull
  docker compose -f compose.yml -f compose.prod.yml up -d --remove-orphans
  docker image prune -f
```

---

## 29. Dockerfile Best Practices

The guide deploys Docker images but never covers writing them well. A poorly written Dockerfile leads to slow builds, bloated images, and security vulnerabilities. The things below have a direct impact on your deploy speed and production safety.

### 29.1 Layer Caching — Order Matters

Docker builds images layer by layer. Each instruction (`RUN`, `COPY`, `ADD`) creates a new layer. If a layer hasn't changed since the last build, Docker reuses the cached version and skips rebuilding it. The moment any layer changes, every subsequent layer is rebuilt from scratch.

**The rule: put things that change least at the top, things that change most at the bottom.**

```dockerfile
# BAD — copies source code before installing dependencies
# Any code change invalidates the npm install layer
FROM node:20-alpine
WORKDIR /app
COPY . .                    # ← copies everything including src
RUN npm install             # ← rebuilds every time any file changes
```

```dockerfile
# GOOD — install dependencies first, copy source last
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./       # ← only changes when package.json changes
RUN npm install             # ← only reruns when package.json changes
COPY . .                    # ← source changes don't invalidate npm install
RUN npm run build
```

### 29.2 Multi-Stage Builds — Smaller Images

A multi-stage build uses multiple `FROM` statements. Each stage can copy files from a previous stage, letting you build in a full environment but ship only what's needed to run. This typically reduces image size by 60–80%.

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build           # Compiles TypeScript, bundles assets, etc.

# Stage 2: Production image — starts fresh, copies only the compiled output
FROM node:20-alpine AS production
WORKDIR /app
COPY package*.json ./
RUN npm install --omit=dev  # Install only production dependencies
COPY --from=builder /app/dist ./dist   # Copy compiled output from builder stage
EXPOSE 3000
CMD ["node", "dist/main.js"]

# The final image contains no source code, no devDependencies, no build tools
```

### 29.3 Run as Non-Root

By default, processes inside a Docker container run as root. If an attacker gets code execution inside your container, they have root inside it — and potentially on the host through misconfigured mounts. Always create and switch to a non-root user.

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY --chown=node:node . .   # Copy files with correct ownership from the start
RUN npm install
USER node                    # Switch to the built-in non-root node user before running
CMD ["node", "server.js"]
```

For custom users:

```dockerfile
RUN addgroup -S appgroup && adduser -S appuser -G appgroup   # Alpine syntax
USER appuser
```

### 29.4 `.dockerignore`

The `.dockerignore` file works exactly like `.gitignore` but for the Docker build context. Without it, `COPY . .` sends your entire project directory — including `node_modules`, `.git`, logs, and secrets — to the Docker daemon. This slows builds and risks leaking sensitive files into images.

```
# .dockerignore
node_modules
.git
.env
.env.*
*.log
dist
coverage
.DS_Store
Dockerfile*
docker-compose*
README.md
```

### 29.5 Use Specific Image Tags

```dockerfile
# BAD — latest can change between builds, making them non-reproducible
FROM node:latest

# GOOD — pin to a specific version for reproducible builds
FROM node:20.11-alpine3.19
```

### 29.6 Combine RUN Commands

Each `RUN` instruction creates a new layer. Chaining commands with `&&` keeps related operations in a single layer, reducing image size and the number of intermediate layers.

```dockerfile
# BAD — three separate layers
RUN apt update
RUN apt install -y curl
RUN rm -rf /var/lib/apt/lists/*

# GOOD — one layer, cleanup in the same step so the cache files never make it into the image
RUN apt update && \
    apt install -y curl && \
    rm -rf /var/lib/apt/lists/*
```

### 29.7 A Production-Ready Node.js Dockerfile

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production   # npm ci is faster and more reliable than npm install in CI

# Stage 2: Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 3: Production runner
FROM node:20-alpine AS runner
WORKDIR /app

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy production deps and compiled output
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --chown=appuser:appgroup package*.json ./

USER appuser
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:3000/health || exit 1

CMD ["node", "dist/main.js"]
```

---

## 30. Rollback Strategy

Section 22 covers deploying with zero downtime. This covers what to do when the new deployment is bad and you need to go back. The key insight is: **`latest` is a trap**. If you always push to `latest`, you have no way to identify or retrieve previous versions.

### 30.1 Tag Images with Git SHAs

Instead of always tagging as `latest`, tag with the git commit SHA so every build is uniquely identifiable and retrievable:

```yaml
# In .github/workflows/deploy.yml

      - name: Build and push image
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: |
            yourdockerhubuser/yourapp:latest
            yourdockerhubuser/yourapp:${{ github.sha }}   # e.g. yourapp:a3f9b1c2
```

Now every deploy is traceable back to an exact commit, and you can always pull any previous version.

### 30.2 Store the Active SHA on the VPS

On each deploy, write the current SHA to a file on the VPS so you always know what's running:

```yaml
          script: |
            cd ~/your-app
            echo "${{ github.sha }}" > .current-sha    # Record what's being deployed
            docker compose pull
            docker compose up -d --remove-orphans
            docker image prune -f
```

### 30.3 Rollback Script

```bash
#!/bin/bash
# rollback.sh — roll back to a specific image SHA

set -e

if [ -z "$1" ]; then
  echo "Usage: ./rollback.sh <image-sha>"
  echo "Example: ./rollback.sh a3f9b1c2"
  exit 1
fi

SHA=$1
IMAGE="yourdockerhubuser/yourapp:$SHA"

echo "Rolling back to $IMAGE..."

# Pull the specific version
docker pull $IMAGE

# Update the compose file to use this specific tag
export IMAGE_TAG=$SHA

cd ~/your-app
docker compose up -d --no-deps app

echo "Rollback complete. Now running: $SHA"
echo "$SHA" > .current-sha
```

### 30.4 List Available Tags to Roll Back To

```bash
# See what images are available locally
docker images yourdockerhubuser/yourapp

# Or check Docker Hub via the API
curl -s "https://hub.docker.com/v2/repositories/yourdockerhubuser/yourapp/tags/?page_size=10" \
  | python3 -m json.tool \
  | grep '"name"'
```

### 30.5 Keep Recent Images on the VPS

By default `docker image prune -f` removes all dangling images. To keep the last few tagged versions available for fast rollback without pulling:

```bash
# Only remove images older than 24 hours — keeps recent builds locally available
docker image prune -a --filter "until=24h" -f
```

### 30.6 Rollback Decision Tree

```
New deployment is broken
├── Is Traefik still routing to the old container? (zero-downtime deploy)
│   └── Yes → Scale old container back up; scale new one down (Section 22)
└── Old container is gone → need to roll back the image
    ├── Do you have the previous SHA?
    │   ├── Yes → docker pull yourapp:<sha> && docker compose up -d
    │   └── No  → Check .current-sha file, Docker Hub tags, or git log
    └── Worst case → restore from VPS provider snapshot (Section 33)
```

---

## 31. Rate Limiting & DDoS Protection

UFW and Fail2Ban protect SSH. But nothing in the guide covers protecting your HTTP/HTTPS endpoints from being flooded. Traefik has built-in rate limiting middleware that sits in front of your services and throttles abusive clients before requests ever reach your app.

### 31.1 What Rate Limiting Protects Against

- **Brute force on login endpoints** — attackers hammering `/auth/login` with credential lists
- **API abuse** — bots hammering your API endpoints faster than real users ever would
- **Denial of service** — a single IP consuming all your server's capacity
- **Scraping** — automated clients crawling your site at machine speed

It does not replace a proper CDN-level DDoS mitigation (Cloudflare, etc.) for volumetric attacks, but it's a strong first line of defence for a self-hosted VPS.

### 31.2 Traefik Rate Limiting Middleware

Define the middleware once, then attach it to any router:

```yaml
# In your app's compose.yml labels

labels:
  - "traefik.enable=true"
  - "traefik.http.routers.app.rule=Host(`app.yourdomain.com`)"
  - "traefik.http.routers.app.entrypoints=websecure"
  - "traefik.http.routers.app.tls.certresolver=letsencrypt"

  # Attach the rate limit middleware to this router
  - "traefik.http.routers.app.middlewares=app-ratelimit"

  # Define the middleware — 100 requests per second average, burst up to 200
  - "traefik.http.middlewares.app-ratelimit.ratelimit.average=100"
  - "traefik.http.middlewares.app-ratelimit.ratelimit.burst=200"
  - "traefik.http.middlewares.app-ratelimit.ratelimit.period=1s"
```

When the limit is exceeded, Traefik returns a `429 Too Many Requests` response automatically — your app never sees the excess requests.

### 31.3 Stricter Limits for Sensitive Endpoints

You can define multiple middlewares and apply them selectively. For a login endpoint you'd want much tighter limits:

```yaml
  # Tight rate limit for auth routes — 5 requests per minute
  - "traefik.http.middlewares.auth-ratelimit.ratelimit.average=5"
  - "traefik.http.middlewares.auth-ratelimit.ratelimit.burst=10"
  - "traefik.http.middlewares.auth-ratelimit.ratelimit.period=1m"

  # Apply both middlewares — comma-separated
  - "traefik.http.routers.app.middlewares=app-ratelimit,auth-ratelimit"
```

### 31.4 IP Allowlisting (Block All But Specific IPs)

For admin panels or internal dashboards:

```yaml
  # Only allow traffic from specific IPs
  - "traefik.http.middlewares.admin-whitelist.ipallowlist.sourcerange=192.168.1.0/24,203.0.113.42/32"
  - "traefik.http.routers.admin.middlewares=admin-whitelist"
```

### 31.5 Cloudflare as a CDN Layer (Recommended for Production)

For serious DDoS protection, put Cloudflare in front of your VPS. Cloudflare absorbs volumetric attacks before they ever reach your server:

1. Point your domain's nameservers to Cloudflare
2. Set your DNS A record through Cloudflare (orange cloud = proxied)
3. On your VPS, configure UFW to only accept HTTP/HTTPS from Cloudflare's IP ranges

```bash
# Allow HTTP/HTTPS only from Cloudflare IPs (download the full list from cloudflare.com/ips)
sudo ufw allow from 173.245.48.0/20 to any port 80
sudo ufw allow from 173.245.48.0/20 to any port 443
# ... repeat for all Cloudflare IP ranges
sudo ufw delete allow 80    # Remove the open rules
sudo ufw delete allow 443
```

Now your VPS is invisible to attackers who try to hit it directly — all traffic must go through Cloudflare.

---

## 32. Cron Jobs vs Systemd Timers

The guide uses `crontab` for scheduled tasks like backups and Docker cleanup. Cron works, but on modern Ubuntu (20.04+), systemd timers are the more robust alternative. Understanding both helps you choose the right tool and debug when things don't run.

### 32.1 Cron — Quick and Simple

Cron is a daemon that runs scheduled commands. It's been in Linux forever, everyone knows it, and it works fine for simple tasks.

```bash
crontab -e          # Edit your user's cron jobs
crontab -l          # List current cron jobs
sudo crontab -e     # Edit root's cron jobs
```

**Cron syntax:**

```
# ┌─── minute (0–59)
# │ ┌─── hour (0–23)
# │ │ ┌─── day of month (1–31)
# │ │ │ ┌─── month (1–12)
# │ │ │ │ ┌─── day of week (0–7, 0 and 7 = Sunday)
# │ │ │ │ │
  * * * * * command

0 3 * * *   /home/username/backup.sh          # Every day at 3AM
0 2 * * 0   docker system prune -f            # Every Sunday at 2AM
*/15 * * * * /usr/local/bin/healthcheck.sh    # Every 15 minutes
0 */6 * * * /usr/local/bin/sync.sh           # Every 6 hours
```

**Cron limitations:**
- Output is silently discarded unless you redirect it or configure mail
- If the system is off when a job was supposed to run, the job is skipped entirely
- No dependency management — no way to say "run this only if that succeeded"
- Harder to debug — no built-in logging

### 32.2 Systemd Timers — More Powerful

Systemd timers are two files: a `.service` file (what to run) and a `.timer` file (when to run it). More setup, but you get logging via `journalctl`, missed run tracking, and proper dependency management.

**Example — Docker cleanup timer:**

Create the service file at `/etc/systemd/system/docker-cleanup.service`:

```ini
[Unit]
Description=Docker system cleanup
After=docker.service        # Only run after Docker is running

[Service]
Type=oneshot                # Run once and exit — not a long-running daemon
ExecStart=/usr/bin/docker system prune -f
User=username               # Run as this user, not root
```

Create the timer file at `/etc/systemd/system/docker-cleanup.timer`:

```ini
[Unit]
Description=Run Docker cleanup weekly

[Timer]
OnCalendar=weekly           # Run once per week
Persistent=true             # If the system was off when it should have run, run it on next boot

[Install]
WantedBy=timers.target
```

Enable and start the timer:

```bash
sudo systemctl daemon-reload
sudo systemctl enable docker-cleanup.timer   # Start on boot
sudo systemctl start docker-cleanup.timer    # Start now
```

**Check and debug:**

```bash
systemctl list-timers                        # List all active timers and their next run time
sudo systemctl status docker-cleanup.timer   # Timer status
sudo systemctl status docker-cleanup.service # Service status — shows last run result
journalctl -u docker-cleanup.service         # Full logs from every run
```

### 32.3 When to Use Which

| Scenario | Use |
|---|---|
| Simple scheduled commands | Cron — less setup, universally understood |
| Tasks that must run even if missed | Systemd timer with `Persistent=true` |
| Tasks that need logging and auditability | Systemd timer — logs go to journald automatically |
| Tasks with dependencies on other services | Systemd timer with `After=` directive |
| Scripts already managed by root | Cron is fine — `sudo crontab -e` |
| Production servers where missed runs matter | Systemd timers |

---

## 33. VPS Provider Snapshots

Before making any significant change to your server — kernel updates, major config overhauls, Docker version upgrades, database migrations — take a snapshot at the VPS provider level. This is your nuclear rollback option. If everything goes wrong, you restore the snapshot and you're back to exactly where you were, in minutes.

### 33.1 What a Snapshot Is

A snapshot is a complete point-in-time copy of your entire VPS — the OS, all files, all Docker volumes, all configuration. Unlike a backup, a snapshot is taken at the infrastructure level, not the application level. You don't need to configure anything on the server itself.

It is different from a backup in one important way: **snapshots are usually stored in the same data centre as your VPS**. If the data centre has an outage, both your VPS and the snapshot may be unavailable. For true disaster recovery, use both snapshots and off-site backups (Section 11).

### 33.2 When to Take a Snapshot

- Before any `apt upgrade` that touches the kernel
- Before upgrading Docker Engine
- Before a major database migration
- Before changing firewall rules significantly
- Before trying anything you're not 100% sure about

The rule: **if you're about to do something that could leave the server unbootable or inaccessible, take a snapshot first.** It takes two minutes and costs almost nothing.

### 33.3 How to Take One (Provider-Specific)

**DigitalOcean:**
- Droplet → Snapshots → Take Live Snapshot
- Or power down the droplet first for a consistent snapshot

**Hetzner:**
- Server → Snapshots → Create Snapshot
- Hetzner snapshots are taken live — no downtime required

**Vultr:**
- Server → Snapshots → Take Snapshot

All major providers charge for snapshot storage — typically a fraction of your server cost per month. Delete old snapshots once you're confident the change is stable.

### 33.4 Restoring a Snapshot

Restoration replaces the entire server disk with the snapshot state. Everything that happened after the snapshot was taken is gone. The process is done entirely from the provider dashboard — you don't need SSH access to the server (which is useful if the server is in a broken, inaccessible state).

### 33.5 Snapshot vs Backup vs Volume Backup

| | VPS Snapshot | Application Backup (S3) | Docker Volume Backup |
|---|---|---|---|
| What it covers | Entire server | Specific data (DB, files) | Specific Docker volumes |
| Where it's stored | Same data centre | Remote (S3, offsite) | Remote (S3, offsite) |
| Restore speed | Fast (minutes) | Slower (rebuild + restore) | Medium |
| Cost | Low (per GB) | Very low | Very low |
| Survives DC outage | No | Yes | Yes |
| Best for | Infra changes, quick rollback | Data recovery, DR | Data recovery |

Use all three — they protect against different failure modes.

---

## 34. Deployment Checklist

A linear list of every step, in order, for deploying a production application from scratch on a fresh VPS.

### Phase 1 — Server Provisioning

- [ ] Buy VPS (minimum 2GB RAM for basic stack; 4GB+ for ELK)
- [ ] Point domain A record to VPS IP
- [ ] Generate SSH key locally (`ssh-keygen -t ed25519`)
- [ ] Add public key to VPS provider dashboard
- [ ] SSH in as root (`ssh root@<ip>`)
- [ ] Update the system (`apt update && apt upgrade -y`)
- [ ] Create non-root user (`adduser --gecos "" username`)
- [ ] Grant sudo (`usermod -aG sudo username`)
- [ ] Copy SSH key to new user
- [ ] Verify key-based login as new user before proceeding
- [ ] Take a VPS provider snapshot before hardening

### Phase 2 — Hardening

- [ ] Disable password auth in `sshd_config`
- [ ] Disable root login in `sshd_config`
- [ ] Restart SSH and verify login still works in a second terminal
- [ ] Optionally change SSH port
- [ ] Set up UFW (allow 80, 443, 22; deny incoming by default)
- [ ] Rate limit SSH (`ufw limit 22`)
- [ ] Install and configure Fail2Ban
- [ ] Set up swap space (especially if running ELK or low on RAM)
- [ ] Apply kernel parameter tuning (`/etc/sysctl.d/99-vps.conf`)

### Phase 3 — Docker & Infrastructure

- [ ] Install Docker engine and compose plugin
- [ ] Add user to docker group (`usermod -aG docker username`)
- [ ] Verify Docker works (`docker run hello-world`)
- [ ] Create shared Traefik network (`docker network create traefik-network`)
- [ ] Set up Traefik directory (`~/traefik/`)
- [ ] Create `traefik.yml`, `compose.yml`, `acme.json`
- [ ] Set `chmod 600` on `acme.json`
- [ ] Start Traefik (`docker compose up -d`)
- [ ] Verify dashboard is accessible and SSL is provisioning

### Phase 4 — Application Deployment

- [ ] Create `.env` file with production secrets
- [ ] Add `.env` to `.gitignore`
- [ ] Write `compose.yml` and `compose.prod.yml` for your app
- [ ] Add health checks to all services
- [ ] Add resource limits to all containers
- [ ] Connect services to `traefik-network`
- [ ] Add Traefik labels to app service
- [ ] Start the app (`docker compose -f compose.yml -f compose.prod.yml up -d`)
- [ ] Verify the app is accessible via HTTPS
- [ ] Verify SSL cert was issued correctly

### Phase 5 — CI/CD Pipeline

- [ ] Generate deploy SSH key (`ssh-keygen -t ed25519 -C "github-actions"`)
- [ ] Add public key to VPS `authorized_keys`
- [ ] Add secrets to GitHub Actions (HOST, USER, KEY, PORT)
- [ ] Write `.github/workflows/deploy.yml`
- [ ] Tag images with both `latest` and git SHA
- [ ] Write rollback script and deploy it to the VPS
- [ ] Test the pipeline with a dummy commit
- [ ] Confirm zero-downtime deploy is working (check Traefik logs during deploy)

### Phase 6 — Observability

- [ ] Install Loki Docker driver plugin
- [ ] Set up `~/monitoring/` directory
- [ ] Write `prometheus.yml`, `loki-config.yml`, monitoring `compose.yml`
- [ ] Start monitoring stack
- [ ] Add Loki logging driver to all app containers
- [ ] Log in to Grafana and configure data sources (Prometheus + Loki)
- [ ] Import Node Exporter and cAdvisor dashboards
- [ ] Set up Docker global log rotation in `/etc/docker/daemon.json`
- [ ] Configure cron or systemd timer for Docker disk cleanup

### Phase 7 — Backup & Recovery

- [ ] Write and test volume backup script
- [ ] Schedule backup cron job or systemd timer
- [ ] Configure S3 sync for off-site backup storage
- [ ] Document rollback procedure — where SHAs are stored, how to restore
- [ ] Take a final VPS snapshot now that everything is running
- [ ] Test a restore from snapshot in a staging environment if possible

### Phase 8 — Ongoing Maintenance

- [ ] Monitor Grafana dashboards regularly
- [ ] Check `sudo ufw status` and `sudo fail2ban-client status` periodically
- [ ] Review and rotate secrets every few months
- [ ] Keep Docker images updated (pull and redeploy regularly)
- [ ] Delete old VPS snapshots once they're no longer needed
- [ ] Run `docker system df` monthly to catch disk creep early

---

*Last updated: 2026 — Built from real deployment experience.*

---

## 28. Real-World Infrastructure: Vibe Events Platform Reference

> Concrete infrastructure decisions from a real NestJS + PostgreSQL + Redis project. Use as a template for MVP-scale systems.

### 28.1 Stack

```
API:        NestJS (TypeScript)
Database:   PostgreSQL
Cache:      Redis (queues + caching + pub/sub)
Storage:    MinIO (self-hosted S3-compatible)
CDN:        Cloudflare (proxies MinIO, serves media at edge)
Real-time:  Socket.IO + Redis Adapter
Queues:     BullMQ (on top of Redis)
Hosting:    Railway or Render (MVP) → AWS ECS (medium scale)
```

### 28.2 Job Queues with BullMQ

BullMQ runs on Redis. Jobs stored in Redis, workers read from Redis, retries automatic.

| Queue | Triggered by | Does |
|---|---|---|
| `media.queue` | PostcardsModule, EventsModule | Resize photos, generate thumbnails, normalise video, update DB |
| `notification.queue` | Every module | FCM push, email via Resend — retries automatically |
| `leaderboard.queue` | GamesModule | Compute ranks, assign rewards, notify winners |
| `email.queue` | AuthModule, EventsModule | Verification emails, password reset, event reminders |

Separate email from notification queue — failures shouldn't block each other. Different retry policies, throttle limits, and costs.

**Job flow:**
```
1. API validates, creates DB record, returns response immediately
2. queue.add('job', payload) — stored in Redis instantly
3. Worker (separate process) picks up job
4. Success: update DB
5. Failure: retry 3× with exponential backoff → dead-letter queue
```

### 28.3 Redis Caching Key Patterns

| Key | TTL | Reason |
|---|---|---|
| `refresh:{userId}:{tokenId}` | 30 days | Token validation and revocation |
| `event:{eventId}` | 5 min | Event pages are read constantly |
| `discover:events:{lat}:{lng}:{tag}` | 2 min | Most-hit endpoint — same query for nearby users |
| `vibe-tags:all` | 1 hour | Tags rarely change |
| `leaderboard:{gameId}` | 30 sec | Polled frequently during active games |
| `user:{userId}` | 10 min | Profile shown on every postcard and comment |
| `checkin:{userId}:{eventId}` | 24 hours | Must be fast — checked on every postcard creation |

**Invalidation:** Delete cached key immediately on update.
```typescript
await redis.del(`user:${userId}`);
```

### 28.4 CDN + MinIO

```
Upload to MinIO at:   minio.yourdomain.com/bucket/key
Cloudflare proxies:   cdn.yourdomain.com/key → never hits MinIO directly
Cached at edge:       photos, videos, backdrops, avatars
Bypasses CDN:         all API responses (user-specific, dynamic)
DDoS protection:      free on all Cloudflare plans
```

### 28.5 Socket.IO Scaling with Redis Adapter

```
MVP (single server): direct delivery, no adapter needed.

Multiple servers:
  User A (Server 1) → DM to User B (Server 2)
  Without adapter: message lost — Server 1 has no connection to User B
  With Redis adapter:
    Server 1 → redis.publish('socket:user:B', payload)
    Server 2 → subscribed → delivers to User B

Install @socket.io/redis-adapter at MVP. Zero refactor when you scale.
```

Events: `dm:{conversationId}`, `chat:{eventId}:{section}`, `leaderboard:{gameId}`, `notifications:{userId}`

### 28.6 Scaling Path

```
MVP:    Railway/Render — managed Postgres + Redis, auto-deploy from GitHub
Medium: AWS — ECS, RDS with replicas, ElastiCache, S3, CloudFront
Large:  Kubernetes multi-region, auto-scaling per service
```
