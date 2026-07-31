# Cloud Fundamentals

**[reference]** — provider-agnostic grounding for the section, from roadmap.sh and vendor docs. The AWS-specific hands-on lives in [[devops/03-cloud/aws-cloud-reference|the AWS reference]].

## What "the cloud" actually is

The cloud is someone else's computers, rented by the hour (or the millisecond), with an API in front of them. You trade capital expense (buying servers) for operating expense (paying for use), and you trade control for speed — you can have a database or a fleet of machines in minutes instead of weeks, but you're now depending on a provider's abstractions and pricing.

The three service models, by how much the provider manages:

| Model | Provider manages | You manage | Example |
|---|---|---|---|
| **IaaS** (Infrastructure) | hardware, virtualization, network | OS, runtime, app, data | AWS EC2, a raw VM |
| **PaaS** (Platform) | + OS, runtime, scaling | app + data | Heroku, App Engine, Elastic Beanstalk |
| **SaaS** (Software) | everything | just your usage/config | Gmail, Datadog |
| **FaaS** (Functions) | + the server entirely | just the function code | Lambda ([[devops/03-cloud/02-serverless|serverless]]) |

The trend as you go down that list: less operational burden, less control, and usually a higher per-unit cost that's worth it until scale flips the math.

## The provider landscape

| Provider | Position | Notable for |
|---|---|---|
| **AWS** | market leader, broadest service catalog | the default; enormous breadth, steep breadth-driven complexity |
| **Azure** | strong in enterprise / Microsoft shops | AD integration, hybrid, .NET |
| **GCP** | strong in data/ML and Kubernetes | GKE (they created Kubernetes), BigQuery |
| **DigitalOcean / Hetzner / Linode** | simple, cheap, developer-friendly | predictable pricing, less breadth — great for small deploys and the [[devops/04-vps/vps-setup|VPS]] path |
| **Cloudflare** | edge/network-first | CDN, DNS, edge compute (Workers) |

The big three (AWS/Azure/GCP) offer the same *categories* of service under different names — learn the category and the specific product name is a lookup.

## The core service categories

Every provider organizes around the same primitives:

- **Compute** — VMs (EC2 / Azure VMs / Compute Engine), containers (ECS/EKS, AKS, GKE), functions (Lambda / Functions). Where your code runs.
- **Storage** — object storage (S3 / Blob / Cloud Storage) for files/blobs, block storage (EBS) for VM disks, file storage (EFS) for shared filesystems.
- **Networking** — the virtual private network (VPC), subnets, security groups/firewalls, load balancers, DNS (Route 53 / Cloud DNS), CDN.
- **Database** — managed relational (RDS / Cloud SQL), NoSQL (DynamoDB / Firestore), caches (ElastiCache / Memorystore). Managed means the provider handles backups, patching, replication.
- **Identity** — IAM: who can do what to which resource. The security backbone of everything.

## The shared responsibility model

The single most important cloud-security concept: **the provider secures the cloud; you secure what you put in it.** The line moves with the service model:

- The provider is always responsible for the physical hardware, the data-center, the hypervisor, and the managed-service internals.
- **You** are always responsible for your data, your access controls (IAM), your network config (leaving a security group open to the world is *your* breach, not theirs), and — for IaaS — patching the guest OS.

Most cloud breaches are not the provider being hacked; they're a misconfigured S3 bucket left public or an over-permissive IAM role. This is why [[devops/09-secret-management/README|secret management]] and least-privilege IAM matter so much.

## Billing — the part that bites

Cloud billing is usage-based and granular, which is a feature (pay for what you use) and a trap (costs you didn't expect). The recurring surprises:

- **Egress (data transfer out)** is charged, often heavily; ingress is usually free. Moving data *between* regions or *out* to the internet is a common bill shock.
- **"Managed" and "serverless" trade cost for convenience** — they're cheaper at low scale and can be far more expensive at high, sustained scale than raw VMs.
- **Idle resources still bill** — a stopped-but-not-terminated VM, an unattached disk, an idle load balancer. Cost hygiene (tagging, budgets, alerts) is a real DevOps responsibility.

**FinOps** is the discipline that grew up around this — treating cost as a first-class engineering metric, not an afterthought.

## Regions and availability zones

Providers split the world into **regions** (geographic areas) each containing multiple **availability zones** (AZs — isolated data centers). Spreading across AZs survives a single data-center failure; spreading across regions survives a regional outage (and reduces latency to distant users). This is the physical substrate the resilience patterns in [[devops/11-delivery-and-advanced/04-cloud-design-patterns|Cloud Design Patterns]] build on.

## Related
- [[devops/03-cloud/02-serverless|Serverless]] — the FaaS end of the compute spectrum
- [[devops/03-cloud/aws-cloud-reference|AWS Reference]] — these categories, as concrete AWS services
- [[devops/05-orchestration/README|Orchestration]] — managed Kubernetes on these providers
- [[devops/11-delivery-and-advanced/04-cloud-design-patterns|Cloud Design Patterns]] — architecting for the resilience these primitives enable
