# Self-Hosting n8n

> **[Intermediate]** · Docker, the database, the encryption key — and an honest account of when hosting it yourself is the wrong call.

## Why self-host

**Data residency** is the real reason. A workflow reading your email, touching your CRM and holding credentials for twenty services is a high-value target and a compliance question. Self-hosting means that data never leaves infrastructure you control → [[cybersecurity/08-governance-risk-and-compliance/README|GRC]].

Secondary: cost at volume (cloud plans price per execution), no execution limits, and network access to internal systems a hosted service cannot reach.

**Against it, honestly:** you now operate a stateful service with a database, backups, upgrades, TLS and monitoring. **That is a real, ongoing cost**, and for a small team the cloud plan is frequently the better trade → [[foundations/systems-engineering/05-trade-studies|trade studies]].

## The licence, stated plainly

n8n is **fair-code**, under the Sustainable Use Licence — **not open source** by the OSI definition. You may self-host freely for internal business use and modify it. You may **not** sell it as a service or offer it as a hosted product to others. Some enterprise features (SSO, the Git integration, log streaming) are separately licensed.

**For internal automation this is a non-issue. If you intended to resell it, read the licence properly** — that's exactly the sort of constraint a trade study should surface before the build, not after.

## The minimum real deployment

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: n8n
      POSTGRES_USER: n8n
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes: [pgdata:/var/lib/postgresql/data]

  n8n:
    image: docker.n8n.io/n8nio/n8n
    restart: unless-stopped
    environment:
      DB_TYPE: postgresdb
      DB_POSTGRESDB_HOST: postgres
      DB_POSTGRESDB_PASSWORD: ${DB_PASSWORD}
      N8N_ENCRYPTION_KEY: ${ENCRYPTION_KEY}
      N8N_HOST: n8n.example.com
      WEBHOOK_URL: https://n8n.example.com/
      N8N_PROTOCOL: https
      EXECUTIONS_DATA_PRUNE: "true"
      EXECUTIONS_DATA_MAX_AGE: "336"        # hours (14 days)
    volumes: [n8n_data:/home/node/.n8n]
    depends_on: [postgres]

volumes: { pgdata: {}, n8n_data: {} }
```

Behind a reverse proxy terminating TLS → [[devops/08-networking-and-web/README|networking and web]].

**Five things in there that are load-bearing:**

**1. Use PostgreSQL, not the default SQLite.** SQLite is the default and is fine for evaluation only — it degrades badly with concurrent executions and makes backups awkward → [[databases/README|databases]].

**2. `N8N_ENCRYPTION_KEY` is the whole security model.** Every stored credential is encrypted with it. **Set it explicitly, back it up separately from the database, and never rotate it casually** — lose it and every credential must be re-entered by hand. A backup of the database *without* this key is useless.

**3. `WEBHOOK_URL` must be the public URL.** Behind a proxy, n8n doesn't know its own external address and will hand out webhook URLs pointing at `localhost` — a confusing failure that looks like a networking problem.

**4. Prune execution data.** Every run stores its full payload at every node. **Unpruned, this grows until the disk fills**, and it's the single most common self-hosting incident.

**5. `restart: unless-stopped`**, because the process will die eventually.

## Scaling, when you get there

The default is one process doing everything. Past a few hundred executions an hour:

**Queue mode** — a main process handling the UI and webhooks, Redis as the queue, and **N worker containers** executing workflows. Horizontal, and the standard answer.

**The scaling limits worth knowing:**
- **Long-running workflows hold a worker** for their duration. A few slow ones can starve everything else — chunk them, or split into triggered stages
- **Concurrency is bounded by workers, not by CPU**
- **The database becomes the bottleneck** before the workers do, largely because of execution-data writes — which is another reason pruning matters

## Operating it

**Backups:** the Postgres database **and** the encryption key, tested by actually restoring → [[databases/12-operating-a-database|operating a database]].

**Upgrades:** pin a version tag rather than `latest`, read the release notes for breaking node changes, and **test on a copy first.** Workflows can break on upgrade when a node's behaviour changes.

**Version control:** export workflows to JSON and commit them, or use the paid Git integration. **Without this, your automations exist only in a database** with no history and no review → [[git/README|git]].

**Access control:** the free tier's user management is basic. **Anyone who can edit a workflow can use every stored credential** — they can't read the secret, but they can make it call anything. Treat editor access as credential access, and keep the instance off the public internet if you can, or behind SSO.

**Monitoring:** health endpoint, plus the absence-alerting from [[ai-automation/05-error-handling-and-retries|note 05]]. **A monitoring system that only watches the container is watching the wrong thing** — the container stays up while every workflow silently fails.

## When not to self-host

**Be honest about this**, because the enthusiasm for self-hosting frequently outruns the appetite for operating it:

- **A small team with no one on call.** n8n Cloud costs less than the hours
- **Automations that are business-critical from day one** — start managed, move when you have the operational muscle
- **No existing Docker/Postgres competence.** This is a poor first stateful service to learn on → [[devops/04-vps/vps-setup|VPS setup]] is the better starting point

**The pattern that works: start on cloud, self-host once you know what your workflows actually are.** Migration is an export and an import; premature self-hosting is weeks of yak-shaving before you've validated the automation is even useful.

## Related
- [[ai-automation/05-error-handling-and-retries|error handling and retries]]
- [[devops/02-docker/README|Docker]] · [[devops/04-vps/vps-setup|VPS setup]]
- [[devops/09-secret-management/README|secret management]] — the encryption-key argument
- [[databases/12-operating-a-database|operating a database]]

*Source: [reference] — from the n8n self-hosting documentation, Aug 2026.*
