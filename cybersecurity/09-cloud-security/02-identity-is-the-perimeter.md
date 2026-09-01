# Identity Is the New Perimeter

**[Advanced]** — why IAM is the primary control in the cloud, and the privilege-escalation paths that make over-permissioning the most dangerous misconfiguration there is.

## The kid version first

On-premises, security was a wall around the building — inside was trusted, outside wasn't. **The cloud has no wall.** Every resource has an internet-reachable API, so "are you inside the network?" is meaningless. The only question left is: **for this specific action on this specific resource, is this identity allowed?**

So identity — who can do what to which resource — *becomes* the perimeter. And the most dangerous mistake is giving an identity more power than it needs, because a single compromised credential then inherits all of it.

## What replaced the firewall

**IAM (Identity and Access Management)** is the cloud's core access-control system: it decides, on every API call, whether a *principal* (a user, a service, a machine) may perform an *action* on a *resource*, subject to *conditions*.

```
   principal  →  action  →  resource  →  allow / deny
   (this app)    (s3:GetObject)  (this bucket)   ← evaluated on EVERY request
```

Because everything in the cloud is an API call, **IAM is evaluated on literally every operation** — reading a file, starting a VM, decrypting a secret. That makes it the single highest-leverage control: get IAM right and most attacks stall; get it wrong and everything else is decoration → [[cybersecurity/09-cloud-security/01-the-shared-responsibility-model|the perimeter dissolved]].

## Least privilege — the discipline

**Grant the minimum permissions needed to do the job, and nothing more.** It's the cloud embodiment of [[cybersecurity/07-security-operations/01-defensive-architecture|zero trust]], and it's the single most important cloud-security practice.

Why it matters so much: **a compromised identity can do exactly what it's permitted to do — no more, no less.** If your web server's role can only read one bucket, a compromise of that server reads one bucket. If its role has `AdministratorAccess` "to make things work," a compromise of that server owns your entire account.

**Over-permissioning is the most common and most dangerous cloud misconfiguration**, because it converts a small compromise into a total one. Yet it's endemic, for a mundane reason: broad permissions make things *work* immediately, and tightening them later is tedious and risky, so nobody does. Wildcards (`Action: "*"`, `Resource: "*"`) accumulate like debt.

**How to actually do least privilege:**
- **Start from zero and add** — grant nothing, then add the specific permissions each failure reveals you need. The opposite of "grant admin, remove later" (which never happens)
- **Use the providers' access analyzers** — AWS Access Analyzer, and CSPM tools, generate least-privilege policies from *observed* usage
- **Scope to specific resources**, not `*` — this role reads *this* bucket, not all buckets
- **Review and prune** — permissions granted for a one-off migration linger for years

## Machine identity beats human credentials

The second discipline: **prefer temporary, role-based credentials over long-lived static keys.**

- **Roles** — an application *assumes a role* and gets short-lived credentials (valid for minutes to hours) that auto-expire. Nothing to leak permanently
- **Static access keys** — a long-lived key pair. **These are the classic breach vector**: committed to Git, baked into an image, left in a config file, and — because they never expire — usable forever once leaked → [[cybersecurity/09-cloud-security/03-the-cloud-attack-surface|exposed secrets]]

**Leaked static keys in a public Git repo are scraped within minutes** by bots watching for exactly that, then used to spin up crypto miners (denial-of-wallet) or exfiltrate data. The fix is structural: **don't have long-lived keys to leak.** Use roles for services, federated SSO for humans, and workload identity for containers → [[devops/09-secret-management/README|secret management]].

**And MFA everywhere**, especially on privileged and root accounts. The root account should be locked away, MFA-protected, and never used for daily work.

## IAM privilege escalation — the attack the misconfig enables

Here's why over-permissioning is so dangerous, concretely. **IAM itself has permissions, and some of them let an identity grant itself more power.** An attacker who compromises a *low*-privilege identity looks for a path to *high* privilege — and IAM misconfigurations provide dozens:

- **`iam:CreatePolicyVersion`** or `iam:PutRolePolicy` → the identity can *rewrite its own permissions* to admin
- **`iam:PassRole` + a compute service** → pass a powerful role to a new EC2 instance / Lambda you control, and inherit it
- **`sts:AssumeRole`** on an over-broad trust policy → assume a more powerful role directly
- **Modifying a Lambda / CI pipeline** that runs with a privileged role → run your code as that role
- **The confused deputy** — trick a more-privileged service into acting on your behalf

**These are all *authorization* logic, not exploits** — the same lesson as [[cybersecurity/14-api-security/03-authorization-and-bola|BOLA in APIs]]: the danger is permissions that let you *reach* more permissions. Tools like **PMapper** and **Cloudsplaining** map these escalation paths in an account automatically — run them defensively, before an attacker does. The single best defence is the boring one: **least privilege, so there's no path to escalate along.**

## The providers, briefly

The model is the same; the vocabulary differs → [[devops/03-cloud/README|cloud]]:

- **AWS IAM** — users, roles, policies (JSON), STS for temporary credentials. The most granular and the most footgun-prone
- **Azure** — RBAC + Entra ID (formerly Azure AD); role assignments over scopes
- **GCP** — IAM with predefined/custom roles bound to resources; service accounts for workloads

**Hybrid and multi-cloud add trust relationships between all of these**, and each seam is an attack path — an on-prem AD synced to Entra ID, or a role that a partner account can assume → [[cybersecurity/12-active-directory/06-defending-active-directory|hybrid identity]].

## Key insight

**In the cloud, identity replaces the firewall as the perimeter, so IAM is evaluated on every single API call and least privilege becomes the highest-leverage control there is** — because a compromised identity can do exactly what it's permitted, and over-permissioning silently converts a small breach into a total one. The specific danger is IAM privilege escalation: permissions that let an identity reach *more* permissions, which is authorization logic (like API BOLA), not exploitation. Grant from zero, prefer short-lived role credentials over leakable static keys, and map your own escalation paths before an attacker maps them for you.

## Related
- [[cybersecurity/09-cloud-security/03-the-cloud-attack-surface|the cloud attack surface]] — where compromised identities come from
- [[cybersecurity/07-security-operations/01-defensive-architecture|defensive architecture]] — zero trust
- [[cybersecurity/14-api-security/03-authorization-and-bola|API authorization]] — the same "permissions that reach permissions" problem
- [[devops/09-secret-management/README|secret management]] — killing static keys

*Source: [reference] — Aug 2026.*
