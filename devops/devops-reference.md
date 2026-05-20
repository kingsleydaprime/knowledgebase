# DevOps — Full Reference Guide

> A concept-first reference covering the full DevOps landscape.
> Builds on the notes in `devops/vps/`, `devops/docker/`, and `devops/linux/` — read those first for foundational knowledge.
> This file goes wider: cloud, Kubernetes, IaC, GitOps, security, reliability, and more.

---

## Table of Contents

1. [What DevOps Actually Is](#1-what-devops-actually-is)
2. [Cloud Fundamentals](#2-cloud-fundamentals)
3. [AWS Core Services](#3-aws-core-services)
4. [Infrastructure as Code — Terraform](#4-infrastructure-as-code--terraform)
5. [Container Orchestration — Kubernetes](#5-container-orchestration--kubernetes)
6. [Helm — Kubernetes Package Manager](#6-helm--kubernetes-package-manager)
7. [Advanced CI/CD](#7-advanced-cicd)
8. [GitOps — ArgoCD and Flux](#8-gitops--argocd-and-flux)
9. [Service Mesh — Istio and Linkerd](#9-service-mesh--istio-and-linkerd)
10. [Secrets at Scale](#10-secrets-at-scale)
11. [Distributed Tracing and Advanced Observability](#11-distributed-tracing-and-advanced-observability)
12. [DevSecOps — Security in the Pipeline](#12-devsecops--security-in-the-pipeline)
13. [Database Operations at Scale](#13-database-operations-at-scale)
14. [High Availability and Multi-Server Architecture](#14-high-availability-and-multi-server-architecture)
15. [Cloud Cost Management](#15-cloud-cost-management)
16. [SRE Practices — SLOs, Error Budgets, Chaos Engineering](#16-sre-practices--slos-error-budgets-chaos-engineering)
17. [DevOps Progression Map](#17-devops-progression-map)
18. [Web Servers — Nginx and Caddy](#18-web-servers--nginx-and-caddy)
19. [Configuration Management — Ansible](#19-configuration-management--ansible)
20. [Serverless](#20-serverless)
21. [Artifact Management](#21-artifact-management)
22. [Cloud Design Patterns](#22-cloud-design-patterns)

---

## 1. What DevOps Actually Is

### 1.1 The Core Idea

DevOps is not a tool, a role, or a set of commands. It is a **culture and practice** that collapses the wall between the team that writes software and the team that runs it. Before DevOps, development and operations were separate departments with opposing incentives — developers wanted to ship changes fast, operations wanted stability. That tension caused slow releases, blame culture, and systems that nobody fully understood.

DevOps answers that with a simple principle: **the people who build the software are responsible for running it in production.** You build it, you ship it, you watch it, you fix it when it breaks.

Everything in this file — Terraform, Kubernetes, CI/CD pipelines, observability — is just tooling that enables that principle at scale.

### 1.2 The Three Ways

The foundational DevOps philosophy comes from *The Phoenix Project* and is expressed as three principles:

**First Way — Systems Thinking.** Optimise the whole, not the parts. A deployment pipeline that takes 3 days is a problem even if each individual step takes minutes. Look at the end-to-end flow from code commit to production.

**Second Way — Amplify Feedback Loops.** Get information back to where it's useful, fast. Monitoring, alerting, and observability exist to make production feedback reach the developer within hours, not weeks.

**Third Way — Culture of Experimentation.** Treat failures as learning opportunities, not blame events. The goal is to make it safe to experiment and safe to fail — so teams can move fast without fear.

### 1.3 DevOps vs SRE vs Platform Engineering

These terms are often confused:

**DevOps** is the cultural philosophy — breaking silos, shared ownership, automation.

**SRE (Site Reliability Engineering)** is Google's implementation of DevOps. It's more prescriptive — SREs use software engineering to solve operations problems. They define SLOs, manage error budgets, and do capacity planning. SRE is DevOps with engineering rigour applied to reliability.

**Platform Engineering** is the next evolution. Instead of every team doing their own DevOps, a dedicated platform team builds internal tools and infrastructure that other teams use — a "paved road" so developers don't have to think about Kubernetes, Terraform, or deployment pipelines. They just use the platform.

### 1.4 The DevOps Lifecycle

```
Plan → Code → Build → Test → Release → Deploy → Operate → Monitor → (back to Plan)
```

Each phase has tooling:

| Phase | Tools |
|---|---|
| Plan | Jira, Linear, Notion |
| Code | Git, GitHub, GitLab |
| Build | Docker, Webpack, Maven, Gradle |
| Test | Jest, Pytest, Selenium, k6 |
| Release | GitHub Actions, GitLab CI, Jenkins |
| Deploy | Kubernetes, Helm, ArgoCD, Terraform |
| Operate | Docker, Kubernetes, Linux |
| Monitor | Prometheus, Grafana, Datadog, OpenTelemetry |

---

## 2. Cloud Fundamentals

### 2.1 Why Cloud

A VPS gives you a single server. Cloud gives you an API over a global network of servers, storage, databases, and networking infrastructure — pay for what you use, scale up or down in seconds.

The three major providers are **AWS** (largest, most services), **GCP** (strongest in AI/ML and data), and **Azure** (dominant in enterprises running Microsoft workloads). AWS is the right one to learn first — it has the most market share, the most documentation, and the most jobs.

### 2.2 Regions and Availability Zones

Cloud infrastructure is physically distributed:

**Region** — A geographic area with multiple data centres. Examples: `us-east-1` (North Virginia), `eu-west-1` (Ireland), `ap-southeast-1` (Singapore). Choose a region close to your users.

**Availability Zone (AZ)** — An isolated data centre within a region. `us-east-1` has `us-east-1a`, `us-east-1b`, `us-east-1c`, etc. Each AZ has independent power, cooling, and networking. Spreading your infrastructure across multiple AZs protects against a single data centre failure.

**The rule:** anything that needs to be highly available should run in at least two AZs.

### 2.3 The Shared Responsibility Model

In cloud, security is split between you and the provider:

**Provider is responsible for:** Physical security, hardware, the hypervisor, managed service uptime.

**You are responsible for:** What you put in the cloud — your OS configuration, IAM permissions, encryption settings, network rules, application code.

Most cloud security breaches are not the provider's fault — they're misconfigured S3 buckets, overly permissive IAM roles, or unpatched OS instances. The cloud gives you the tools; you have to use them correctly.

### 2.4 Compute Options — Choosing the Right One

| Service | What it is | When to use it |
|---|---|---|
| EC2 (VM) | A virtual machine you manage fully | Full control, custom OS, long-running workloads |
| ECS (Containers) | Managed Docker container runner | Containerised apps without learning Kubernetes |
| EKS (Kubernetes) | Managed Kubernetes cluster | Containerised apps at scale, microservices |
| Lambda (Serverless) | Run a function on demand, no server | Event-driven, short tasks, unpredictable traffic |
| Fargate | Serverless containers (no EC2 to manage) | Containers without managing underlying VMs |
| App Runner | Fully managed container deployment | Simple web apps, least operational overhead |

### 2.5 Networking Concepts You Must Know

**VPC (Virtual Private Cloud)** — Your own isolated private network inside AWS. Think of it as the cloud equivalent of your office network. Every resource you create lives inside a VPC.

**Subnet** — A subdivision of your VPC with its own IP range.
- **Public subnet** — has a route to the internet. Put load balancers and bastion servers here.
- **Private subnet** — no direct internet access. Put databases and application servers here.

**Internet Gateway** — Attaches to a VPC to allow public subnets to reach the internet.

**NAT Gateway** — Sits in a public subnet and allows resources in private subnets to initiate outbound internet connections (e.g. to pull Docker images) without being directly reachable from the internet.

**Security Group** — A stateful firewall attached to an individual resource (EC2, RDS, etc.). Controls what traffic can reach that resource. Think of it as UFW but for cloud resources.

**NACL (Network Access Control List)** — A stateless firewall attached to a subnet. Less common than security groups but useful for subnet-level rules.

**Route Table** — Defines where network traffic is directed. Public subnets have a route to the Internet Gateway; private subnets have a route to the NAT Gateway.

A well-architected VPC looks like this:

```
VPC (10.0.0.0/16)
├── Public Subnet (10.0.1.0/24) — AZ-1
│   ├── Load Balancer
│   ├── NAT Gateway
│   └── Bastion Server
├── Public Subnet (10.0.2.0/24) — AZ-2
│   └── Load Balancer
├── Private Subnet (10.0.3.0/24) — AZ-1
│   └── App Servers (EC2 / ECS)
├── Private Subnet (10.0.4.0/24) — AZ-2
│   └── App Servers (EC2 / ECS)
├── Private Subnet (10.0.5.0/24) — AZ-1
│   └── Database (RDS primary)
└── Private Subnet (10.0.6.0/24) — AZ-2
    └── Database (RDS replica)
```

### 2.6 IAM — Identity and Access Management

IAM controls who and what can do what in your AWS account. It is the most important security surface in cloud — misconfigured IAM is the number one cause of cloud breaches.

**Users** — Human identities. Each person gets their own IAM user with their own credentials. Never share credentials.

**Roles** — Identities for machines and services. An EC2 instance assumes a role to get permissions to call other AWS services. A Lambda function assumes a role to write to S3. No hardcoded credentials needed.

**Policies** — JSON documents that define permissions. Attached to users, groups, or roles.

**The principle of least privilege** — every user, role, and service should have the minimum permissions needed to do its job and nothing more. An app that only reads from S3 should have a role that only allows `s3:GetObject` on that specific bucket — not `s3:*` on all buckets.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-specific-bucket/*"
    }
  ]
}
```

---

## 3. AWS Core Services

### 3.1 EC2 — Elastic Compute Cloud

EC2 is a virtual machine in the cloud. It's the closest equivalent to your VPS, but with on-demand provisioning, dozens of instance types, and deep integration with the rest of AWS.

**Instance types** follow a naming pattern: `t3.medium`, `m5.large`, `c6i.xlarge`
- First letter: family (`t` = burstable, `m` = general purpose, `c` = compute optimised, `r` = memory optimised)
- Number: generation (higher = newer, cheaper, faster)
- Size: `nano`, `micro`, `small`, `medium`, `large`, `xlarge`, `2xlarge`, etc.

**Pricing models:**
- **On-Demand** — pay per hour, no commitment. Most expensive but most flexible.
- **Reserved Instances** — commit to 1 or 3 years, save up to 75%. For stable, always-on workloads.
- **Spot Instances** — use spare AWS capacity at up to 90% discount. Can be terminated with 2 minutes notice. For fault-tolerant batch jobs and stateless workloads.
- **Savings Plans** — flexible commitment (commit to $/hour spend, not specific instance type). Easier than Reserved Instances.

### 3.2 S3 — Simple Storage Service

S3 is object storage — not a filesystem, not a database, but a flat key-value store for files of any size. Infinitely scalable, extremely durable (11 nines — 99.999999999% durability), and cheap.

```bash
# AWS CLI basics
aws s3 ls                                    # List buckets
aws s3 ls s3://my-bucket/                    # List objects in a bucket
aws s3 cp file.txt s3://my-bucket/           # Upload a file
aws s3 cp s3://my-bucket/file.txt ./         # Download a file
aws s3 sync ./local-dir s3://my-bucket/dir/  # Sync a directory
aws s3 rm s3://my-bucket/file.txt            # Delete a file
```

**Common uses:**
- Static website hosting
- Application asset storage (images, videos, documents)
- Backup storage (Section 11 in VPS file)
- Terraform state storage (Section 4 in this file)
- Log archiving
- Data lake for analytics

**Key concepts:**
- Buckets are globally unique by name
- Objects are private by default — never make a bucket public unless you intend to
- Versioning can be enabled to keep a history of all object changes
- Lifecycle policies can auto-delete or archive objects after a set period
- S3 is eventually consistent for overwrites and deletes — not a database

### 3.3 RDS — Relational Database Service

RDS is managed Postgres, MySQL, MariaDB, Oracle, or SQL Server. You don't manage the OS, the database engine, or backups — AWS handles all of that. You just use the database.

```bash
# Connect to RDS via psql (from inside your VPC or via SSH tunnel)
psql -h your-rds-endpoint.rds.amazonaws.com -U username -d dbname
```

**Key features:**
- **Automated backups** — daily snapshots retained for up to 35 days
- **Multi-AZ** — synchronous standby replica in another AZ, automatic failover in ~60 seconds if primary fails
- **Read replicas** — asynchronous copies for read scaling. Can be promoted to primary if needed.
- **Parameter groups** — tune database settings without SSH access
- **Performance Insights** — built-in query performance monitoring

**Aurora** is AWS's own cloud-native database engine compatible with Postgres and MySQL. It's faster, more resilient, and scales storage automatically — but costs more. For serious production workloads it's worth considering.

### 3.4 ELB — Elastic Load Balancing

Load balancers distribute traffic across multiple instances. AWS has three types:

**ALB (Application Load Balancer)** — Layer 7 (HTTP/HTTPS). Can route based on URL path, hostname, headers. This is what you use for web apps and APIs.

**NLB (Network Load Balancer)** — Layer 4 (TCP/UDP). Extremely high performance, handles millions of requests per second. Use for non-HTTP workloads or when you need static IPs.

**CLB (Classic Load Balancer)** — Legacy. Don't use for new projects.

ALB in practice:
```
Internet → ALB (public subnet)
         → Target Group A → EC2 instances running app-v1
         → Target Group B → EC2 instances running app-v2
         → Rules: /api/* → API service, /* → Frontend service
```

### 3.5 CloudWatch — Monitoring and Logs

CloudWatch is AWS's native monitoring service. Every AWS service publishes metrics and logs here automatically.

```bash
# Tail logs from a log group
aws logs tail /aws/ec2/my-app --follow

# Query logs with CloudWatch Insights
aws logs start-query \
  --log-group-name /aws/ec2/my-app \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, @message | filter @message like /ERROR/'
```

**Alarms** — trigger actions (SNS notification, Auto Scaling) when a metric crosses a threshold.
**Dashboards** — custom metric visualisation (similar to Grafana but AWS-native).
**Log Insights** — SQL-like query language for searching logs.

### 3.6 Route 53 — DNS

Route 53 is AWS's DNS service. Beyond basic DNS, it supports:
- **Health checks** — monitor endpoints and remove unhealthy targets from DNS
- **Routing policies** — Latency-based (route to closest region), Weighted (A/B traffic split), Failover (primary/secondary)
- **Private hosted zones** — DNS that only resolves inside your VPC

---

## 4. Infrastructure as Code — Terraform

### 4.1 Why IaC

Clicking through cloud consoles to provision infrastructure is not reproducible. If your VPC or EC2 instances were created manually, you can't recreate them reliably, you can't track what changed over time, and you can't review changes before applying them. Infrastructure as Code (IaC) solves this by describing your infrastructure in code that is version-controlled, reviewed, and applied systematically.

**Terraform** is the dominant IaC tool. It's cloud-agnostic (works with AWS, GCP, Azure, and 1000+ providers), declarative (you describe the end state, Terraform figures out how to get there), and has a massive ecosystem.

The key mental model: Terraform maintains a **state file** that maps your code to real infrastructure. When you run `terraform apply`, it compares your code to the state file and makes only the changes needed to reach the desired state.

### 4.2 Core Concepts

**Provider** — A plugin that knows how to talk to a specific API (AWS, GCP, Cloudflare, GitHub, etc.)

**Resource** — A piece of infrastructure: an EC2 instance, an S3 bucket, a VPC, a DNS record.

**Data source** — Read existing infrastructure without managing it. Query for the latest Ubuntu AMI ID, look up an existing VPC, etc.

**Variable** — Input parameters that make your config reusable across environments.

**Output** — Values exported from your Terraform config — like the IP address of a created instance.

**Module** — A reusable package of Terraform resources. Like a function in programming — define once, use many times.

**State** — The file Terraform uses to track what it has created. Should be stored remotely (S3) and locked (DynamoDB) in team environments.

### 4.3 Terraform Workflow

```bash
terraform init      # Download providers and modules — run once per project
terraform plan      # Preview what changes will be made — always review before applying
terraform apply     # Apply the planned changes
terraform destroy   # Tear down all managed infrastructure
terraform fmt       # Format code consistently
terraform validate  # Check config for syntax errors
terraform output    # Show output values
terraform state list  # List all resources in state
```

### 4.4 Project Structure

```
infrastructure/
├── main.tf           # Main resource definitions
├── variables.tf      # Input variable declarations
├── outputs.tf        # Output value declarations
├── providers.tf      # Provider configuration
├── terraform.tfvars  # Variable values (gitignored for sensitive values)
└── modules/
    ├── vpc/          # Reusable VPC module
    ├── ec2/          # Reusable EC2 module
    └── rds/          # Reusable RDS module
```

### 4.5 Example — VPC and EC2

**`providers.tf`:**

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"   # Pin to major version to prevent breaking changes
    }
  }

  # Store state remotely in S3 — required for team use
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-state-lock"   # Prevents simultaneous applies
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
}
```

**`variables.tf`:**

```hcl
variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name: dev, staging, production"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}
```

**`main.tf`:**

```hcl
# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true   # Allows EC2 instances to get DNS names

  tags = {
    Name        = "${var.environment}-vpc"
    Environment = var.environment
  }
}

# Public subnet
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true   # Instances get public IPs automatically

  tags = {
    Name = "${var.environment}-public-subnet"
  }
}

# Internet gateway — connects the VPC to the internet
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
}

# Route table — public subnet routes to internet gateway
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"                    # All traffic
    gateway_id = aws_internet_gateway.main.id   # Goes through the internet gateway
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Security group — allow SSH and HTTP/HTTPS
resource "aws_security_group" "app" {
  name   = "${var.environment}-app-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["YOUR_IP/32"]   # Only your IP
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"             # All outbound traffic allowed
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 instance
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]   # Canonical's AWS account ID

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-*-22.04-amd64-server-*"]
  }
}

resource "aws_instance" "app" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.app.id]
  key_name               = "your-key-pair-name"

  root_block_device {
    volume_size = 30          # GB
    volume_type = "gp3"       # General purpose SSD — cheaper and faster than gp2
    encrypted   = true
  }

  tags = {
    Name        = "${var.environment}-app-server"
    Environment = var.environment
  }
}
```

**`outputs.tf`:**

```hcl
output "instance_public_ip" {
  description = "Public IP of the app server"
  value       = aws_instance.app.public_ip
}

output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.app.id
}
```

### 4.6 Remote State Setup

Before using the S3 backend, create the bucket and DynamoDB table:

```hcl
# bootstrap/main.tf — run once to create state infrastructure
resource "aws_s3_bucket" "terraform_state" {
  bucket = "your-terraform-state-bucket"
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"   # Keep history of all state file versions
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"   # Encrypt state at rest
    }
  }
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-state-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
```

### 4.7 Workspaces — Multiple Environments

Terraform workspaces let you manage multiple environments (dev, staging, production) from the same config:

```bash
terraform workspace new staging      # Create staging workspace
terraform workspace select staging   # Switch to staging
terraform workspace list             # List all workspaces
```

Use the workspace name in your config:

```hcl
locals {
  environment = terraform.workspace   # "staging", "production", etc.
}

resource "aws_instance" "app" {
  instance_type = terraform.workspace == "production" ? "t3.large" : "t3.micro"
  # Production gets a bigger instance; other environments get the smallest
}
```

---

## 5. Container Orchestration — Kubernetes

### 5.1 Why Kubernetes

Docker Compose on a single VPS works until it doesn't — until you need more than one server, until a container crashes and takes a minute to restart, until you need to deploy 50 microservices, until you need to scale one service independently of others.

Kubernetes (K8s) is a container orchestration platform. It manages a cluster of machines and runs your containers across them, handling:
- **Scheduling** — deciding which machine each container runs on
- **Self-healing** — restarting crashed containers, replacing failed nodes
- **Scaling** — adding or removing container replicas based on load
- **Service discovery** — containers finding each other by name
- **Rolling deployments** — updating containers with zero downtime
- **Load balancing** — distributing traffic across replicas

The tradeoff: Kubernetes is complex. It has a steep learning curve and significant operational overhead. For a single-server app with low traffic, it's overkill — your VPS with Docker Compose is the right tool. Kubernetes pays off when you have multiple services, multiple team members, and need the reliability and scalability it provides.

### 5.2 Core Concepts

**Cluster** — A set of machines (nodes) managed by Kubernetes. Has one or more control plane nodes and multiple worker nodes.

**Control Plane** — The brain. Runs the API server, scheduler, and controller manager. Manages the cluster state. On managed Kubernetes (EKS, GKE, AKS), AWS/Google/Azure runs this for you.

**Node** — A worker machine (VM or physical). Runs your containers. Has a container runtime (containerd), kubelet (talks to control plane), and kube-proxy (networking).

**Pod** — The smallest deployable unit in Kubernetes. A pod is one or more containers that share a network namespace and storage. Usually one container per pod.

**Deployment** — Manages a set of identical pods. Handles rolling updates, rollbacks, and desired replica count.

**Service** — A stable network endpoint for a set of pods. Pods come and go; the Service IP stays constant.

**Ingress** — Routes external HTTP/HTTPS traffic to Services. Think of it as the Kubernetes equivalent of Traefik or Nginx.

**ConfigMap** — Store non-sensitive configuration as key-value pairs. Injected into pods as environment variables or mounted as files.

**Secret** — Store sensitive data (passwords, tokens). Encoded in base64 (not encrypted by default — use Sealed Secrets or external secrets for real encryption).

**Namespace** — Virtual clusters within a cluster. Separate teams, projects, or environments.

**PersistentVolume (PV) / PersistentVolumeClaim (PVC)** — Kubernetes's equivalent of Docker named volumes. PVC is what your pod requests; PV is the actual storage.

### 5.3 The Kubernetes Object Model

Every Kubernetes resource is a YAML manifest with the same structure:

```yaml
apiVersion: apps/v1      # Which API group this resource belongs to
kind: Deployment         # The type of resource
metadata:
  name: my-app           # Name of this resource
  namespace: production  # Which namespace it lives in
  labels:
    app: my-app          # Labels for selecting and grouping
spec:                    # The desired state — what you want
  # ...
status:                  # The actual state — what Kubernetes reports back (read-only)
  # ...
```

### 5.4 Core Manifests

**Deployment:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: production
spec:
  replicas: 3                    # Run 3 identical pods
  selector:
    matchLabels:
      app: my-app                # Manage pods with this label
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1                # Create 1 extra pod during update before removing old ones
      maxUnavailable: 0          # Never go below desired replica count during update — zero downtime
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: my-app
          image: yourdockerhubuser/my-app:a3f9b1c2   # Always use specific tag, not latest
          ports:
            - containerPort: 3000
          env:
            - name: NODE_ENV
              value: production
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: app-secrets      # Reference a Secret object
                  key: db-password
          resources:
            requests:
              memory: "128Mi"            # Minimum guaranteed resources
              cpu: "100m"                # 100 millicores = 0.1 CPU core
            limits:
              memory: "512Mi"            # Hard ceiling — pod is killed if exceeded
              cpu: "500m"
          readinessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 10      # Wait before first probe
            periodSeconds: 5            # Check every 5 seconds
          livenessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 30
            periodSeconds: 10
            failureThreshold: 3          # Restart after 3 consecutive failures
```

**Service:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
  namespace: production
spec:
  selector:
    app: my-app           # Route traffic to pods with this label
  ports:
    - protocol: TCP
      port: 80            # Port the service exposes
      targetPort: 3000    # Port on the pod to forward to
  type: ClusterIP         # Internal only — ClusterIP, NodePort, or LoadBalancer
```

**Ingress:**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  namespace: production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod   # Auto-provision SSL via cert-manager
spec:
  tls:
    - hosts:
        - app.yourdomain.com
      secretName: my-app-tls    # cert-manager will create this Secret with the cert
  rules:
    - host: app.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-app-service
                port:
                  number: 80
```

**Secret:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: production
type: Opaque
data:
  db-password: c3VwZXJzZWNyZXQ=   # base64 encoded — echo -n "supersecret" | base64
```

**ConfigMap:**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: production
data:
  NODE_ENV: production
  LOG_LEVEL: info
  API_URL: https://api.yourdomain.com
```

### 5.5 kubectl — The Kubernetes CLI

```bash
# Context and cluster
kubectl config get-contexts              # List all configured clusters
kubectl config use-context my-cluster    # Switch to a cluster
kubectl config current-context          # Show active cluster

# Getting resources
kubectl get pods                         # List pods in default namespace
kubectl get pods -n production           # List pods in production namespace
kubectl get pods -A                      # List pods in all namespaces
kubectl get deployments
kubectl get services
kubectl get ingress
kubectl get all                          # List everything

# Inspecting resources
kubectl describe pod my-pod-name         # Detailed info — events, conditions, config
kubectl describe deployment my-app
kubectl logs my-pod-name                 # View pod logs
kubectl logs my-pod-name -f              # Follow logs live
kubectl logs my-pod-name --previous      # Logs from the previous (crashed) container

# Applying and deleting
kubectl apply -f manifest.yml            # Create or update resource
kubectl apply -f ./k8s/                  # Apply all files in a directory
kubectl delete -f manifest.yml           # Delete resource
kubectl delete pod my-pod-name           # Delete a specific pod (Deployment will recreate it)

# Debugging
kubectl exec -it my-pod-name -- bash     # Shell into a running pod
kubectl port-forward pod/my-pod 8080:3000  # Forward local port to pod port

# Scaling
kubectl scale deployment my-app --replicas=5

# Rollout management
kubectl rollout status deployment/my-app          # Watch a rolling update
kubectl rollout history deployment/my-app         # View revision history
kubectl rollout undo deployment/my-app            # Roll back to previous version
kubectl rollout undo deployment/my-app --to-revision=2  # Roll back to specific revision

# Namespace management
kubectl create namespace production
kubectl get namespaces
```

### 5.6 Managed Kubernetes — EKS, GKE, AKS

Running your own Kubernetes control plane is complex and error-prone. Use managed Kubernetes in production:

**EKS (AWS)** — Most common in enterprise. Integrates with IAM, ALB, EBS, and other AWS services. More manual setup than GKE but more flexibility.

**GKE (Google)** — The most polished managed Kubernetes. Google invented Kubernetes so they know it best. Autopilot mode removes even node management.

**AKS (Azure)** — Best for organisations already in the Microsoft ecosystem.

```bash
# Create an EKS cluster with eksctl (the recommended tool)
eksctl create cluster \
  --name production \
  --region us-east-1 \
  --nodegroup-name workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 5 \
  --managed    # Use AWS-managed node groups

# Update kubeconfig to connect kubectl to the cluster
aws eks update-kubeconfig --name production --region us-east-1
```

### 5.7 Horizontal Pod Autoscaler

Automatically scales replicas based on CPU or memory usage:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2           # Never scale below 2
  maxReplicas: 10          # Never scale above 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70   # Scale up when average CPU exceeds 70%
```

---

## 6. Helm — Kubernetes Package Manager

### 6.1 What Helm Is

Writing raw Kubernetes YAML for every service gets repetitive fast. Helm is a package manager for Kubernetes — it lets you define your app as a **chart** (a collection of templated YAML) and install it with a single command, passing in values to customise the deployment.

Think of it as `apt` or `npm` for Kubernetes. You can use community charts (for Postgres, Redis, Prometheus, etc.) or write your own.

### 6.2 Core Concepts

**Chart** — A package of Kubernetes manifests with templating. Has a `Chart.yaml` (metadata), `values.yaml` (default config), and `templates/` directory.

**Release** — An installed instance of a chart. You can install the same chart multiple times with different names and values.

**Repository** — A collection of charts, like a package registry. ArtifactHub is the main public registry.

### 6.3 Basic Helm Commands

```bash
# Repository management
helm repo add bitnami https://charts.bitnami.com/bitnami   # Add a chart repository
helm repo update                                            # Refresh repository index
helm search repo postgres                                   # Search for charts

# Installing charts
helm install my-postgres bitnami/postgresql \
  --namespace production \
  --create-namespace \
  --set auth.postgresPassword=mysecretpassword \
  --set primary.persistence.size=20Gi

# Managing releases
helm list -A                             # List all releases across all namespaces
helm status my-postgres -n production    # Status of a release
helm upgrade my-postgres bitnami/postgresql --set auth.postgresPassword=newpassword
helm rollback my-postgres 1              # Roll back to revision 1
helm uninstall my-postgres -n production

# Values
helm show values bitnami/postgresql      # Show all configurable values for a chart
helm get values my-postgres              # Show values used in a current release
```

### 6.4 Writing a Helm Chart

```
my-app/
├── Chart.yaml           # Chart metadata
├── values.yaml          # Default values
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    └── _helpers.tpl     # Reusable template snippets
```

**`Chart.yaml`:**

```yaml
apiVersion: v2
name: my-app
description: My application Helm chart
version: 0.1.0          # Chart version
appVersion: "1.0.0"     # App version — usually the image tag
```

**`values.yaml`:**

```yaml
replicaCount: 2

image:
  repository: yourdockerhubuser/my-app
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: true
  host: app.yourdomain.com

resources:
  limits:
    memory: 512Mi
    cpu: 500m
  requests:
    memory: 128Mi
    cpu: 100m

env:
  NODE_ENV: production
  LOG_LEVEL: info
```

**`templates/deployment.yaml`:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-{{ .Chart.Name }}   # Release name + chart name
  labels:
    app: {{ .Chart.Name }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Chart.Name }}
  template:
    metadata:
      labels:
        app: {{ .Chart.Name }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - containerPort: 3000
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

Install your own chart:

```bash
helm install my-app ./my-app \
  --namespace production \
  --values ./values.production.yaml   # Override values for production
```

---

## 7. Advanced CI/CD

### 7.1 Beyond GitHub Actions

GitHub Actions is excellent for most projects. At scale, teams use dedicated CI platforms with more power and flexibility:

**GitLab CI** — Built into GitLab. Pipeline defined in `.gitlab-ci.yml`. Strong for monorepos and self-hosted setups. Runners can be your own machines.

**Jenkins** — The old standard. Extremely flexible, massive plugin ecosystem, but high operational overhead. Running less in greenfield projects but still dominant in enterprises.

**CircleCI** — Hosted, fast, strong Docker support. Good for teams that want speed without Jenkins complexity.

**Tekton** — Kubernetes-native CI/CD. Pipelines are Kubernetes resources. Part of the CNCF ecosystem.

### 7.2 Pipeline Design Principles

A good CI/CD pipeline has clear stages that fail fast and give useful feedback:

```
Trigger (push/PR)
    ↓
Lint & Format check      ← Fast — fail in seconds on obvious issues
    ↓
Unit tests               ← Fast — fail in minutes
    ↓
Build Docker image       ← Tag with git SHA
    ↓
Integration tests        ← Slower — test against real dependencies
    ↓
Security scan            ← Scan image for vulnerabilities
    ↓
Push image to registry   ← Only if all tests pass
    ↓
Deploy to staging        ← Automatic
    ↓
Smoke tests              ← Quick sanity checks against staging
    ↓
Deploy to production     ← Manual approval gate or automatic on merge to main
    ↓
Post-deploy health check ← Verify production is healthy; auto-rollback if not
```

### 7.3 GitHub Actions — Advanced Patterns

**Matrix builds** — run jobs across multiple versions/environments in parallel:

```yaml
jobs:
  test:
    strategy:
      matrix:
        node-version: [18, 20, 22]        # Test on all three Node versions simultaneously
        os: [ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm test
```

**Reusable workflows** — define a workflow once and call it from multiple pipelines:

```yaml
# .github/workflows/reusable-deploy.yml
on:
  workflow_call:          # This workflow can be called by others
    inputs:
      environment:
        required: true
        type: string
    secrets:
      VPS_SSH_KEY:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        # ...deploy steps using inputs.environment and secrets.VPS_SSH_KEY
```

```yaml
# .github/workflows/deploy-production.yml
jobs:
  deploy:
    uses: ./.github/workflows/reusable-deploy.yml
    with:
      environment: production
    secrets:
      VPS_SSH_KEY: ${{ secrets.VPS_SSH_KEY }}
```

**Environment protection rules** — require manual approval before deploying to production:

```yaml
jobs:
  deploy-production:
    environment:
      name: production     # Defined in GitHub repo settings with required reviewers
      url: https://app.yourdomain.com
    steps:
      # ...
```

**Caching** — speed up builds by caching dependencies:

```yaml
      - name: Cache node modules
        uses: actions/cache@v3
        with:
          path: ~/.npm
          key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
          restore-keys: |
            ${{ runner.os }}-node-
```

### 7.4 Canary Releases

A canary release sends a small percentage of traffic to the new version before fully rolling out. If the canary shows elevated error rates, you roll it back with minimal user impact.

With Kubernetes and a service mesh (Section 9) or Argo Rollouts:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
spec:
  replicas: 10
  strategy:
    canary:
      steps:
        - setWeight: 10      # Send 10% of traffic to new version
        - pause: {duration: 5m}   # Wait 5 minutes — watch metrics
        - setWeight: 50      # Increase to 50%
        - pause: {duration: 5m}
        - setWeight: 100     # Full rollout
```

### 7.5 Feature Flags

Feature flags decouple deployment from release. You deploy code with a new feature disabled, then enable it for specific users or percentages without redeploying.

Tools: **LaunchDarkly** (most popular), **Unleash** (open source, self-hosted), **Flagsmith** (open source).

```javascript
// In your app code
if (featureFlags.isEnabled('new-checkout-flow', userId)) {
  return newCheckoutFlow();
} else {
  return legacyCheckoutFlow();
}
```

This lets you:
- Test features on internal users before external rollout
- Instantly disable a broken feature without a rollback
- Run A/B tests without code changes

---

## 8. GitOps — ArgoCD and Flux

### 8.1 What GitOps Is

GitOps is a deployment model where **Git is the single source of truth for what should be running in production**. Instead of CI pipelines pushing changes to Kubernetes directly, a GitOps controller running inside the cluster continuously compares the desired state (what's in Git) with the actual state (what's running) and reconciles any drift.

The benefits: every change is a Git commit (auditable, reversible), the cluster self-heals if someone manually changes something, and the deployment process is the same whether you're deploying for the first time or the hundredth.

**ArgoCD** and **Flux** are the two dominant GitOps tools for Kubernetes.

### 8.2 ArgoCD

ArgoCD is a Kubernetes controller that watches a Git repository and keeps the cluster in sync with it.

```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Get the initial admin password
kubectl get secret argocd-initial-admin-secret -n argocd \
  -o jsonpath="{.data.password}" | base64 -d

# Port-forward to access the UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

**Application manifest — tells ArgoCD what to sync:**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/yourusername/your-repo
    targetRevision: main          # Track the main branch
    path: k8s/production          # Path within the repo containing manifests
  destination:
    server: https://kubernetes.default.svc   # The current cluster
    namespace: production
  syncPolicy:
    automated:
      prune: true      # Delete resources that are removed from Git
      selfHeal: true   # Re-sync if someone manually changes the cluster
    syncOptions:
      - CreateNamespace=true
```

**The GitOps workflow with ArgoCD:**

```
Developer pushes code
    ↓
CI pipeline builds and tests
    ↓
CI updates the image tag in the k8s/ manifests in Git (a separate commit)
    ↓
ArgoCD detects the Git change
    ↓
ArgoCD applies the new manifests to the cluster
    ↓
Kubernetes rolls out the new version
```

### 8.3 Flux

Flux is similar to ArgoCD but more modular and CLI-driven. It's part of the CNCF and tightly integrated with Helm.

```bash
# Bootstrap Flux onto a cluster (with GitHub)
flux bootstrap github \
  --owner=your-github-username \
  --repository=your-fleet-repo \
  --branch=main \
  --path=clusters/production \
  --personal
```

---

## 9. Service Mesh — Istio and Linkerd

### 9.1 What a Service Mesh Is

In a microservices architecture, services talk to each other over the network. As the number of services grows, managing that communication becomes complex — you need encryption between services (mTLS), traffic control (retries, timeouts, circuit breaking), and visibility (which services are talking to which, with what latency and error rate).

A service mesh solves this by injecting a **sidecar proxy** into every pod. The proxy (usually Envoy) intercepts all network traffic to and from the pod and applies policies — without any changes to the application code.

Think of it as Traefik, but for service-to-service traffic inside the cluster rather than external traffic coming in.

### 9.2 What a Service Mesh Gives You

**mTLS (mutual TLS)** — Every service-to-service connection is encrypted and authenticated. Services prove their identity to each other using certificates managed by the mesh. No manual certificate management.

**Traffic management** — Route 10% of traffic to a new version, retry failed requests automatically, set timeouts per route, circuit-break to a failing service.

**Observability** — Automatic metrics (latency, error rate, request volume) and distributed traces for every service-to-service call — without instrumenting your code.

**Policy enforcement** — Define which services are allowed to call which other services. Block unauthorised internal traffic at the network level.

### 9.3 Istio vs Linkerd

**Istio** — More features, more complexity. The most widely adopted service mesh. Uses Envoy as the sidecar proxy. Can be overkill for smaller setups.

**Linkerd** — Simpler, lighter, easier to operate. Uses its own proxy (written in Rust). Excellent observability out of the box. Better choice if you just want mTLS and basic traffic management without the full Istio complexity.

### 9.4 When to Consider a Service Mesh

You probably don't need a service mesh until:
- You have 5+ services communicating with each other
- You need encrypted service-to-service communication (compliance requirement)
- You're debugging latency issues between services and need granular visibility
- You want fine-grained traffic control (canary releases, A/B testing at the mesh level)

For most applications on a single VPS or a small Kubernetes cluster, it's unnecessary complexity. Add it when you feel the pain it solves.

---

## 10. Secrets at Scale

### 10.1 The Problem with Kubernetes Secrets

Kubernetes Secrets are only base64 encoded, not encrypted. Anyone with access to the cluster or the etcd database can read them. For serious production use, you need a better approach.

### 10.2 Sealed Secrets

Sealed Secrets encrypts your secrets using a public key so they're safe to commit to Git. Only the controller running in the cluster (which holds the private key) can decrypt them.

```bash
# Install the kubeseal CLI
brew install kubeseal   # or download from releases

# Create a regular Kubernetes Secret
kubectl create secret generic app-secrets \
  --from-literal=db-password=supersecret \
  --dry-run=client -o yaml > secret.yaml

# Seal it — now safe to commit to Git
kubeseal --format yaml < secret.yaml > sealed-secret.yaml

# Apply to cluster — controller decrypts and creates the real Secret
kubectl apply -f sealed-secret.yaml
```

### 10.3 External Secrets Operator

A Kubernetes operator that syncs secrets from external sources (AWS Secrets Manager, HashiCorp Vault, GCP Secret Manager) into Kubernetes Secrets automatically.

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: app-secrets
  namespace: production
spec:
  refreshInterval: 1h          # Re-sync every hour — picks up rotated secrets automatically
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  target:
    name: app-secrets          # Name of the Kubernetes Secret to create
  data:
    - secretKey: db-password   # Key in the Kubernetes Secret
      remoteRef:
        key: production/app    # Path in AWS Secrets Manager
        property: db-password  # Specific field within that secret
```

### 10.4 HashiCorp Vault with Kubernetes

Vault can dynamically generate secrets — database credentials that expire, AWS credentials that are valid for only one hour. No long-lived static credentials anywhere.

```bash
# Enable Kubernetes auth in Vault
vault auth enable kubernetes

# Configure Vault to trust your cluster
vault write auth/kubernetes/config \
  kubernetes_host="https://kubernetes.default.svc"

# Create a policy
vault policy write app-policy - <<EOF
path "secret/data/production/*" {
  capabilities = ["read"]
}
EOF

# Bind the policy to a Kubernetes service account
vault write auth/kubernetes/role/app \
  bound_service_account_names=app-service-account \
  bound_service_account_namespaces=production \
  policies=app-policy \
  ttl=1h
```

Apps then authenticate to Vault using their Kubernetes service account token and retrieve secrets at runtime — no secrets baked into images or stored in environment variables.

---

## 11. Distributed Tracing and Advanced Observability

### 11.1 The Observability Stack

Full observability has three pillars:

**Metrics** — Numerical measurements over time (CPU, memory, request count, error rate, latency percentiles). Answered by Prometheus + Grafana (covered in VPS file).

**Logs** — Timestamped records of events. Answered by Loki or ELK (covered in VPS file).

**Traces** — The path a single request takes through your system — which services it touched, how long each took, where errors occurred. This is what's new in this section.

Metrics tell you *something is wrong*. Logs tell you *what happened*. Traces tell you *why it happened and where*.

### 11.2 Distributed Tracing

In a microservices system, a single user request might touch 10 services. If that request is slow or fails, which service is responsible? Distributed tracing answers this by assigning each request a unique trace ID and propagating it through every service call, recording the timing of each step (called a **span**).

```
User request (trace_id: abc123)
├── API Gateway (span: 5ms)
│   ├── Auth Service (span: 12ms)
│   ├── User Service (span: 8ms)
│   └── Product Service (span: 45ms)  ← this is your bottleneck
│       └── Database query (span: 40ms)
└── Response (total: 70ms)
```

### 11.3 OpenTelemetry

OpenTelemetry (OTel) is the open standard for instrumentation. It provides SDKs for every major language that let you emit traces, metrics, and logs in a vendor-neutral format. Instrument once, send to any backend (Jaeger, Zipkin, Honeycomb, Datadog).

```javascript
// Node.js — instrument your app with OpenTelemetry
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({
    url: 'http://otel-collector:4318/v1/traces',   // Send to OpenTelemetry collector
  }),
});

sdk.start();
// From here, HTTP requests and DB calls are automatically traced
```

### 11.4 Jaeger — Trace Storage and UI

Jaeger is an open-source distributed tracing backend. It stores traces and provides a UI for searching and visualising them.

```yaml
# Add to your monitoring compose or Kubernetes manifests
services:
  jaeger:
    image: jaegertracing/all-in-one:latest   # All-in-one for development; use separate components in production
    container_name: jaeger
    ports:
      - "16686:16686"   # Jaeger UI
      - "4317:4317"     # OTLP gRPC receiver
      - "4318:4318"     # OTLP HTTP receiver
    environment:
      - COLLECTOR_OTLP_ENABLED=true
```

### 11.5 SLOs and Advanced Alerting

**SLI (Service Level Indicator)** — A metric that measures service health. Examples: request success rate, p99 latency, availability.

**SLO (Service Level Objective)** — A target for an SLI. Example: "99.9% of requests succeed", "p99 latency < 500ms over 30 days".

**SLA (Service Level Agreement)** — A contractual commitment to customers. SLAs are based on SLOs.

**Error Budget** — The allowed amount of failure implied by your SLO. If your SLO is 99.9% availability, your error budget is 0.1% — about 43 minutes of downtime per month. If you've used up your error budget, you stop shipping new features and focus on reliability.

Defining SLOs in Prometheus:

```yaml
# prometheus rules — alert when error rate burns through budget too fast
groups:
  - name: slos
    rules:
      - alert: HighErrorBudgetBurn
        expr: |
          (
            sum(rate(http_requests_total{status=~"5.."}[1h]))
            /
            sum(rate(http_requests_total[1h]))
          ) > 0.001   # Error rate exceeds 0.1% (burns through monthly budget in ~1h)
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Error budget burning too fast"
```

### 11.6 APM Tools

For teams that want full observability without building it themselves:

**Datadog** — The most complete commercial observability platform. Metrics, logs, traces, APM, dashboards, alerting — all in one. Expensive but saves significant engineering time.

**New Relic** — Similar to Datadog. Good free tier for small projects.

**Honeycomb** — Focused on high-cardinality observability. Excellent for microservices debugging. Built by observability experts.

**Sentry** — Error tracking and performance monitoring. Especially good for frontend and mobile. More developer-facing than Datadog.

---

## 12. DevSecOps — Security in the Pipeline

### 12.1 The Shift Left Principle

Traditional security reviews happened at the end — code was written, tested, deployed, and then security looked at it. By then, fixing vulnerabilities is expensive. "Shift left" means moving security earlier in the development process — into the IDE, the pull request, the CI pipeline — where fixes are cheap.

DevSecOps integrates security into every phase of the DevOps lifecycle automatically, so it's not a gate but a continuous check.

### 12.2 Container Image Scanning

Every Docker image you build may contain vulnerable OS packages or dependencies. Scan images in your CI pipeline before pushing them to production.

**Trivy** — Open source, fast, comprehensive. Scans OS packages, language dependencies, IaC files, and Kubernetes manifests.

```bash
# Install Trivy
brew install trivy   # or download from releases

# Scan a local image
trivy image your-app:latest

# Scan with a severity filter
trivy image --severity HIGH,CRITICAL your-app:latest

# Exit with non-zero code if HIGH or CRITICAL vulns found — use in CI to block builds
trivy image --exit-code 1 --severity HIGH,CRITICAL your-app:latest
```

In GitHub Actions:

```yaml
      - name: Scan image for vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: yourdockerhubuser/your-app:${{ github.sha }}
          format: sarif                  # GitHub Security tab format
          output: trivy-results.sarif
          severity: HIGH,CRITICAL
          exit-code: 1                  # Fail the pipeline on critical vulns

      - name: Upload scan results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: trivy-results.sarif
```

### 12.3 SAST — Static Application Security Testing

SAST analyses your source code for security vulnerabilities without running it.

**Semgrep** — Open source, fast, supports 30+ languages. Write custom rules or use the community ruleset.

```bash
# Install
pip install semgrep

# Run against your codebase using the default security ruleset
semgrep --config=p/security-audit .

# Run against a specific language
semgrep --config=p/nodejs .
```

**CodeQL** — GitHub's SAST tool. Free for open source, runs in GitHub Actions:

```yaml
      - name: Initialize CodeQL
        uses: github/codeql-action/init@v2
        with:
          languages: javascript, python

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v2
```

### 12.4 DAST — Dynamic Application Security Testing

DAST tests a running application for vulnerabilities — SQL injection, XSS, auth bypass, etc.

**OWASP ZAP** — The most popular open-source DAST tool.

```yaml
      - name: DAST scan with ZAP
        uses: zaproxy/action-full-scan@v0.7.0
        with:
          target: 'https://staging.yourdomain.com'
          rules_file_name: '.zap/rules.tsv'   # Custom rules to include/exclude
```

### 12.5 Dependency Scanning

**Dependabot** — Built into GitHub. Automatically opens PRs to update vulnerable dependencies.

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: npm
    directory: /
    schedule:
      interval: weekly
    open-pull-requests-limit: 10

  - package-ecosystem: docker
    directory: /
    schedule:
      interval: weekly
```

**Snyk** — Commercial tool with a generous free tier. Scans dependencies, container images, and IaC.

### 12.6 Secrets Scanning

Prevent secrets from being committed to Git in the first place.

**Gitleaks** — Scans git history and staged changes for secrets:

```bash
# Scan the entire repo history
gitleaks detect --source .

# Scan only staged changes (use as a pre-commit hook)
gitleaks protect --staged
```

**TruffleHog** — Similar to Gitleaks but with more entropy-based detection:

```bash
trufflehog git file://. --only-verified
```

In GitHub Actions — block PRs that introduce secrets:

```yaml
      - name: Scan for secrets
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 12.7 Compliance Frameworks

At the enterprise level, security is governed by compliance frameworks:

**SOC 2** — US standard for security, availability, processing integrity, confidentiality, and privacy. Required by many enterprise customers.

**ISO 27001** — International information security management standard.

**PCI DSS** — Required if you handle credit card data.

**HIPAA** — Required if you handle health data in the US.

These aren't tools — they're audit frameworks. DevSecOps practices (image scanning, SAST, access controls, audit logs) are the technical evidence that satisfies these audits.

---

## 13. Database Operations at Scale

### 13.1 Zero-Downtime Migrations

Database schema changes are the riskiest part of deployment. The wrong migration can lock tables, corrupt data, or break running application instances. Zero-downtime migrations require a three-phase approach:

**Phase 1 — Expand (backward-compatible change):**
Add new columns as nullable, create new tables, add new indexes concurrently.

```sql
-- Safe — adding a nullable column doesn't break existing code
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- Safe — CREATE INDEX CONCURRENTLY builds without locking the table
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
```

**Phase 2 — Migrate:**
Deploy new application code that writes to both old and new schema. Backfill old data.

```sql
-- Backfill in batches to avoid locking
UPDATE users SET phone = '' WHERE phone IS NULL AND id BETWEEN 1 AND 10000;
-- Repeat in batches
```

**Phase 3 — Contract (remove old schema):**
Once all application instances are using the new schema and old columns have no data, remove them.

```sql
-- Only after all app instances are updated and old column is unused
ALTER TABLE users DROP COLUMN old_column;
```

**Never** run `DROP COLUMN` or `ALTER COLUMN` on a live table with concurrent traffic unless you've verified no application code references it.

### 13.2 Read Replicas

A read replica is an asynchronous copy of the primary database that handles read queries. This offloads read traffic from the primary, which then only handles writes.

```
Application
├── Write queries  → Primary DB (us-east-1a)
└── Read queries   → Read Replica (us-east-1b)
                    Read Replica (us-east-1c)
```

In your application:

```javascript
// Use separate connection pools for reads and writes
const writePool = new Pool({ host: process.env.DB_PRIMARY_HOST });
const readPool  = new Pool({ host: process.env.DB_REPLICA_HOST });

// Route accordingly
async function getUser(id) {
  return readPool.query('SELECT * FROM users WHERE id = $1', [id]);
}

async function createUser(data) {
  return writePool.query('INSERT INTO users ...', data);
}
```

**Replication lag** is the delay between a write on the primary and when it's visible on the replica. Usually milliseconds, but can be seconds under load. Don't read your own writes from a replica immediately after writing.

### 13.3 Connection Pooling at Scale

At scale, connection pooling becomes critical. Postgres has a process-per-connection model — each connection spawns an OS process. At 1000 connections, Postgres is using significant RAM just for connection overhead.

**PgBouncer** (covered in VPS file) handles this for a single application. At Kubernetes scale, use **PgBouncer in pooler mode** or **RDS Proxy** (AWS-managed connection pooler).

### 13.4 Database Sharding

Sharding is horizontal partitioning — splitting data across multiple database instances by a shard key. User IDs 1–1M go to shard 1, 1M–2M to shard 2, etc.

This is complex and introduces significant application complexity. Consider it only when:
- A single database (with replicas and optimised queries) can't handle your write throughput
- You've exhausted vertical scaling options
- You need to distribute data geographically

Most applications never need sharding. Premature sharding is one of the most expensive mistakes in database engineering.

### 13.5 Point-in-Time Recovery

PITR lets you restore a database to any point in time — not just the last backup, but any second within a retention window.

On RDS, PITR is enabled by default. Restore to a specific time:

```bash
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier my-database \
  --target-db-instance-identifier my-database-restored \
  --restore-time 2026-01-15T14:30:00Z
```

For self-hosted Postgres, WAL archiving to S3 enables PITR:

```bash
# In postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'aws s3 cp %p s3://my-bucket/wal/%f'
```

---

## 14. High Availability and Multi-Server Architecture

### 14.1 What High Availability Means

High Availability (HA) means the system continues to function even when components fail. The key metric is **availability** — the percentage of time the system is operational.

| Availability | Downtime per year | Downtime per month |
|---|---|---|
| 99% (two nines) | 3.65 days | 7.3 hours |
| 99.9% (three nines) | 8.77 hours | 43.8 minutes |
| 99.99% (four nines) | 52.6 minutes | 4.38 minutes |
| 99.999% (five nines) | 5.26 minutes | 26.3 seconds |

Three nines is a reasonable target for most production systems. Five nines requires enormous engineering investment and is only justified for critical infrastructure.

### 14.2 Eliminating Single Points of Failure

A single point of failure (SPOF) is any component whose failure brings down the entire system. A single VPS is a SPOF — if it goes down, everything goes down.

To eliminate SPOFs:

```
Single VPS (SPOF)
    ↓
Load Balancer (AWS ALB — managed, highly available by design)
├── App Server — AZ-1
└── App Server — AZ-2

Primary DB — AZ-1
    ↓ (sync replication, automatic failover)
Standby DB — AZ-2
```

Every layer now has redundancy. No single component failure takes down the system.

### 14.3 Load Balancing Algorithms

**Round Robin** — Requests distributed evenly in order: server 1, server 2, server 3, server 1, ... Default for most load balancers. Simple but doesn't account for server load.

**Least Connections** — New requests go to the server with fewest active connections. Better for long-lived connections.

**Weighted** — Some servers get more traffic than others. Useful for gradually shifting traffic (canary releases) or when servers have different capacities.

**IP Hash** — The same client IP always goes to the same server. Useful for stateful sessions, but defeats the purpose of load balancing if session state isn't shared.

**For stateless apps:** Round Robin or Least Connections — no session affinity needed.
**For stateful apps:** Store session state externally (Redis) and use Round Robin — don't rely on IP Hash.

### 14.4 Multi-Region Architecture

For global applications or the highest availability requirements, deploy across multiple geographic regions:

```
Users in EU → eu-west-1 (Ireland) → Regional Load Balancer
                                   → App Servers
                                   → Regional Database

Users in US → us-east-1 (Virginia) → Regional Load Balancer
                                    → App Servers
                                    → Regional Database

Global DNS (Route 53 Latency-based routing)
  → Route each user to closest region
```

**Data replication between regions** is the hardest part. Options:
- **Active-Passive** — one region is primary (all writes go here), other region is a warm standby with a replica. Failover takes seconds to minutes.
- **Active-Active** — both regions accept writes. Extremely complex — requires conflict resolution, eventual consistency, or a distributed database (CockroachDB, PlanetScale, Spanner).

### 14.5 CDN — Content Delivery Network

A CDN caches static assets (images, CSS, JS, videos) at edge locations close to users. Instead of a request for an image travelling from Lagos to a server in Virginia, it's served from a Cloudflare or AWS CloudFront edge node much closer.

Benefits:
- Dramatically lower latency for static assets
- Reduces load on your origin servers
- Absorbs DDoS traffic at the edge
- Automatic geographic distribution

For dynamic content, CDN can still help with edge caching (short TTL) or edge compute (Cloudflare Workers, Lambda@Edge).

---

## 15. Cloud Cost Management

### 15.1 Why Cloud Bills Surprise People

Cloud pricing is complex and often counterintuitive. Resources you forgot to delete, data transfer costs you didn't anticipate, and services running at over-provisioned sizes are the most common culprits.

The guiding principle: **you pay for what you provision, not what you use** — except for serverless. An EC2 instance that's idle still costs the same as one under full load.

### 15.2 The Biggest Cost Drivers

**Compute (EC2, ECS, EKS nodes)** — Usually the largest line item. Right-size your instances — a `t3.micro` for a service that uses 5% CPU is wasteful; paying for a `c5.2xlarge` when you need a `t3.medium` is even more so.

**Data Transfer** — Ingress (data coming into AWS) is free. Egress (data leaving AWS to the internet) costs money. Cross-AZ and cross-region data transfer also has a cost. This surprises many people.

**RDS** — Managed databases are expensive relative to a self-hosted Postgres. Multi-AZ roughly doubles the cost. Choose the right instance size carefully.

**NAT Gateway** — Often overlooked. NAT Gateways charge per GB of data processed. Instances in private subnets pulling Docker images or making API calls run all that traffic through NAT Gateway.

**Load Balancers** — ALBs have a fixed hourly cost plus a per-LCU (Load Balancer Capacity Unit) charge based on traffic.

### 15.3 Cost Optimisation Strategies

**Right-sizing** — Use CloudWatch metrics to find over-provisioned instances. If your EC2 averages 10% CPU, it's probably over-provisioned.

```bash
# AWS CLI — get average CPU utilisation for an instance over 7 days
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-1234567890 \
  --start-time $(date -d '7 days ago' -u +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 86400 \
  --statistics Average
```

**Reserved Instances / Savings Plans** — Commit to 1 or 3 years for up to 75% savings on stable workloads. Use Savings Plans over Reserved Instances for flexibility.

**Spot Instances** — Use for stateless, fault-tolerant workloads (batch jobs, CI runners, dev environments). Up to 90% cheaper. Combine with On-Demand in an Auto Scaling Group for resilience.

**Auto Scaling** — Scale in during off-peak hours. Don't run 10 instances at 3AM when 2 are sufficient.

**S3 Lifecycle Policies** — Move infrequently accessed data to cheaper storage classes automatically:

```json
{
  "Rules": [{
    "Status": "Enabled",
    "Transitions": [
      {"Days": 30, "StorageClass": "STANDARD_IA"},     // After 30 days → Infrequent Access
      {"Days": 90, "StorageClass": "GLACIER"}           // After 90 days → Glacier (cheapest)
    ],
    "Expiration": {"Days": 365}                         // Delete after 1 year
  }]
}
```

**Delete unused resources** — Unattached EBS volumes, old snapshots, idle load balancers, unused Elastic IPs. Run a regular audit.

### 15.4 Cost Monitoring Tools

**AWS Cost Explorer** — Built-in tool for analysing your bill by service, region, tag, and time. Set up monthly budgets with alerts.

**AWS Budgets** — Alert when actual or forecasted spend exceeds a threshold:

```bash
aws budgets create-budget \
  --account-id 123456789 \
  --budget '{"BudgetName":"monthly-limit","BudgetLimit":{"Amount":"100","Unit":"USD"},"TimeUnit":"MONTHLY","BudgetType":"COST"}' \
  --notifications-with-subscribers '[{"Notification":{"NotificationType":"ACTUAL","ComparisonOperator":"GREATER_THAN","Threshold":80},"Subscribers":[{"SubscriptionType":"EMAIL","Address":"you@example.com"}]}]'
```

**Infracost** — Open source tool that shows you the cost impact of Terraform changes before you apply them:

```bash
infracost breakdown --path .   # Show cost of current Terraform config
infracost diff --path .        # Show cost diff of pending changes
```

**Tag everything** — Apply consistent tags to all resources so you can track costs by team, service, environment, and project:

```hcl
# In Terraform — apply tags to all AWS resources
provider "aws" {
  default_tags {
    tags = {
      Environment = var.environment
      Project     = "my-app"
      Team        = "backend"
      ManagedBy   = "terraform"
    }
  }
}
```

---

## 16. SRE Practices — SLOs, Error Budgets, Chaos Engineering

### 16.1 The SRE Mindset

Site Reliability Engineering (SRE) is Google's answer to the question: how do you run large-scale systems reliably without slowing down development?

The core insight is that **100% reliability is not the goal** — it's impossible, and chasing it means you never ship anything. Instead, define an acceptable level of unreliability (the error budget), use it to balance innovation and stability, and invest engineering effort proportionally to how close you are to the budget.

### 16.2 Defining SLOs

Start by asking: **what matters to your users?** Not what's easy to measure — what users actually experience.

Good SLIs:
- Request success rate: `successful_requests / total_requests`
- Latency: `% of requests completing in < 500ms`
- Availability: `time_system_available / total_time`

Bad SLIs:
- CPU usage (users don't experience CPU)
- Number of deployments (not user-facing)

```yaml
# Example SLO definitions (document in a simple file — not necessarily in code)
SLOs:
  availability:
    SLI: HTTP success rate (non-5xx responses)
    target: 99.9% over rolling 30 days
    error_budget: 0.1% = 43.2 minutes/month

  latency:
    SLI: p99 response time < 500ms
    target: 95% of requests
    measurement_window: rolling 30 days
```

### 16.3 Error Budgets in Practice

```
Monthly error budget = (1 - SLO) × total_requests

If SLO = 99.9% and you have 1M requests/month:
Error budget = 0.1% × 1,000,000 = 1,000 allowed failures

Track burn rate:
- If you've had 500 failures in the first week → you'll exhaust the budget in 2 weeks
- Alert when burn rate is 2x or more than the normal rate
```

**What to do when budget is consumed:**
- Freeze non-essential feature releases
- Focus engineering effort on reliability improvements
- Conduct a thorough postmortem on what consumed the budget

**What to do when budget has plenty of room:**
- Ship features faster
- Run experiments
- Do infrastructure changes that carry some risk

### 16.4 Postmortems

A postmortem is a structured review after an incident. The goal is learning, not blame. **Blameless postmortems** are essential to psychological safety — if people fear punishment for incidents, they'll hide problems instead of surfacing them.

A good postmortem template:

```markdown
## Incident: [Date] — [Brief title]

**Duration:** [Start time] → [End time] ([Total duration])
**Severity:** P1 / P2 / P3
**Impact:** [How many users affected, what was broken]

## Timeline
- HH:MM — Event
- HH:MM — Alert fired
- HH:MM — On-call paged
- HH:MM — Root cause identified
- HH:MM — Fix deployed
- HH:MM — Service restored

## Root Cause
[Technical explanation of what went wrong and why]

## Contributing Factors
[Things that made the incident worse or harder to detect]

## What Went Well
[Detection, response, communication]

## Action Items
| Action | Owner | Due Date |
|---|---|---|
| Add alert for X | @person | YYYY-MM-DD |
| Fix root cause Y | @person | YYYY-MM-DD |
| Add test for Z | @person | YYYY-MM-DD |
```

### 16.5 Chaos Engineering

Chaos engineering is the practice of deliberately injecting failures into your system to verify it handles them correctly — before a real failure does it for you in production.

The philosophy: **if you don't test failure, you don't know how your system behaves when it fails.** Most systems fail in ways that were never anticipated. Chaos engineering surfaces those failure modes in a controlled way.

**Principles:**
1. Define your steady state (what does normal look like?)
2. Hypothesise that the system will remain in steady state during the experiment
3. Introduce failure (kill a pod, block network traffic, fill disk, spike latency)
4. Observe — does the system recover? How quickly? Was the impact user-visible?
5. Fix any gaps discovered and repeat

**Tools:**

**Chaos Monkey** — Netflix's original chaos tool. Randomly terminates EC2 instances in production. Forces teams to build fault-tolerant systems because they have no choice.

**LitmusChaos** — Kubernetes-native chaos framework. Define chaos experiments as Kubernetes resources:

```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: pod-delete-chaos
  namespace: production
spec:
  appinfo:
    appns: production
    applabel: app=my-app
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-delete
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: "30"          # Kill pods randomly for 30 seconds
            - name: CHAOS_INTERVAL
              value: "10"          # Kill one every 10 seconds
            - name: FORCE
              value: "false"
```

**Chaos Toolkit** — Python-based, cloud-agnostic. Write experiments in JSON:

```json
{
  "title": "Can we handle losing a pod?",
  "steady-state-hypothesis": {
    "title": "Service is healthy",
    "probes": [{
      "type": "http",
      "url": "https://app.yourdomain.com/health",
      "expected_status": 200
    }]
  },
  "method": [{
    "type": "action",
    "name": "kill-pod",
    "provider": {
      "type": "python",
      "module": "chaosk8s.pod.actions",
      "func": "terminate_pods",
      "arguments": { "label_selector": "app=my-app" }
    }
  }],
  "rollbacks": []
}
```

**Start small with chaos engineering** — begin in staging, with small blast radius, with monitoring already in place. Never run chaos experiments without the ability to immediately stop them.

---

## 17. DevOps Progression Map

### 17.1 Where the VPS Reference File Sits

```
Foundation (VPS Reference File)
├── Linux fundamentals
├── SSH and server hardening
├── Docker and Docker Compose
├── Traefik and SSL
├── GitHub Actions CI/CD
├── Prometheus, Grafana, Loki
├── ELK Stack
└── Basic backup and recovery

↓

Intermediate (This File — Part 1)
├── Cloud fundamentals (AWS VPC, IAM, EC2, S3, RDS)
├── Terraform basics
├── Kubernetes fundamentals
├── Helm
└── Advanced CI/CD patterns

↓

Intermediate-Advanced (This File — Part 2)
├── GitOps (ArgoCD, Flux)
├── Service Mesh (Istio, Linkerd)
├── Secrets at scale (Vault, External Secrets)
├── Distributed tracing (OpenTelemetry, Jaeger)
└── DevSecOps (Trivy, SAST, DAST)

↓

Advanced (This File — Part 3)
├── Database operations at scale
├── High availability and multi-region
├── Cost management
└── SRE practices (SLOs, chaos engineering)

↓

Staff / Principal Level
├── Platform engineering
├── Multi-cloud strategy
├── FinOps (cloud cost as an engineering discipline)
├── Large-scale incident command
└── Organisation-wide reliability culture
```

### 17.2 Realistic Learning Path

**Months 1–2: Cloud + Terraform**
- Get AWS free tier account
- Complete AWS Solutions Architect Associate (or Cloud Practitioner to start)
- Build the VPC + EC2 setup from Section 4 of this file
- Deploy your Nextvibe backend on EC2 instead of a VPS
- Set up RDS instead of Docker Postgres
- Store Terraform state in S3

**Months 3–4: Kubernetes**
- Run a local cluster with `kind` or `minikube`
- Port your Docker Compose app to Kubernetes manifests
- Deploy to a real EKS cluster (use `eksctl`)
- Add a Helm chart for your app
- Set up cert-manager for SSL

**Months 5–6: GitOps + Observability**
- Install ArgoCD on your cluster
- Move all manifests to a Git repo and let ArgoCD sync
- Add OpenTelemetry to your Node.js app
- Send traces to Jaeger
- Build Grafana dashboards that tie together metrics, logs, and traces

**Months 7–9: Security + Reliability**
- Add Trivy scanning to your CI pipeline
- Set up Dependabot
- Define SLOs for your Nextvibe backend
- Write and run your first chaos experiment in staging
- Complete the AWS Security Specialty or Certified Kubernetes Security Specialist

**Ongoing**
- Build things and break things
- Read: *The Phoenix Project*, *Site Reliability Engineering* (Google SRE Book — free online), *Accelerate* by Nicole Forsgren
- Contribute to open source infrastructure tools
- Follow: Kelsey Hightower, Liz Fong-Jones, Charity Majors

### 17.3 Certifications Worth Having

| Certification | Provider | Value |
|---|---|---|
| AWS Solutions Architect Associate | AWS | High — validates cloud fundamentals |
| Certified Kubernetes Administrator (CKA) | CNCF | High — practical K8s operations |
| Certified Kubernetes Application Developer (CKAD) | CNCF | Good for dev-focused roles |
| AWS DevOps Engineer Professional | AWS | Strong for AWS-heavy teams |
| HashiCorp Terraform Associate | HashiCorp | Good signal for IaC roles |
| AWS Security Specialty | AWS | Valuable for security-conscious teams |

Start with AWS SAA — it covers the cloud fundamentals that everything else builds on, it's widely recognised, and it has the most preparation material available.

### 17.4 How This Connects to Your Stack

Everything in this file has direct application to what you've already built:

- **Terraform** — provision the Nextvibe infrastructure reproducibly instead of clicking through DigitalOcean
- **RDS** — replace the Aiven PostgreSQL with managed AWS RDS for better reliability and PITR
- **EKS** — move Nextvibe from Docker Compose on a single VPS to a resilient multi-node cluster
- **GitOps** — make deployments fully declarative and auditable — no more SSH-and-pull
- **OpenTelemetry** — add tracing to the NestJS backend to see exactly where latency comes from
- **Trivy + Gitleaks** — add to the GitHub Actions pipeline to catch vulnerabilities before they reach production
- **SLOs** — define what "Nextvibe is working" actually means numerically, and build alerting around it

The SIWES DevOps phase you planned is the right starting point. Cloud + Linux + Docker is the base. Everything else in this file is what comes after that base is solid.

---

## 18. Web Servers — Nginx and Caddy

### 18.1 What a Web Server Does

A web server sits at the entry point of your infrastructure and handles:
- Serving static files directly (HTML, CSS, JS, images)
- Acting as a **reverse proxy** — forwarding requests to your application server
- Terminating SSL/TLS so your app only sees plain HTTP internally
- Load balancing between multiple backend instances
- Caching, rate limiting, compression, security headers

Your Node.js or Python process is an application server, not a web server. You put a proper web server in front of it.

### 18.2 Nginx

Nginx (pronounced "engine-x") is the most widely used web server. It handles static files with extremely low memory usage and is the standard reverse proxy in Linux deployments.

**Installation:**

```bash
sudo apt update && sudo apt install nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

**Configuration structure:**

```
/etc/nginx/
├── nginx.conf               ← global settings (worker count, logging, mime types)
├── sites-available/         ← all your server block configs
│   └── your-app
└── sites-enabled/           ← symlinks to active configs
    └── your-app → ../sites-available/your-app
```

```bash
sudo ln -s /etc/nginx/sites-available/your-app /etc/nginx/sites-enabled/
sudo nginx -t          # test config before reloading — always run this
sudo systemctl reload nginx
```

**Reverse proxy (the most common config):**

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

**With SSL after Certbot:**

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}
```

**Serving a static SPA (React, Vue, etc.):**

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /var/www/html;
    index index.html;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    location / {
        try_files $uri $uri/ /index.html;   # fallback to index.html for client-side routing
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**Rate limiting:**

```nginx
http {
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    server {
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://localhost:3000;
        }
    }
}
```

**Essential commands:**

```bash
sudo nginx -t                       # Test config syntax without reloading
sudo systemctl reload nginx         # Reload config — no downtime
sudo systemctl restart nginx        # Full restart — brief downtime
tail -f /var/log/nginx/access.log   # Watch access logs
tail -f /var/log/nginx/error.log    # Watch error logs
```

### 18.3 Getting SSL with Certbot

```bash
sudo apt install certbot python3-certbot-nginx

# Obtain cert and auto-configure Nginx in one step
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run

# Certbot installs a systemd timer — verify it's running
sudo systemctl status certbot.timer
```

### 18.4 Caddy

Caddy is a modern web server written in Go. Its defining feature: **automatic HTTPS by default**. Point it at a domain name and it obtains and renews a Let's Encrypt certificate automatically — no Certbot, no manual SSL configuration.

The same reverse proxy config that takes 25 lines in Nginx takes 3 in Caddy:

```
yourdomain.com {
    reverse_proxy localhost:3000
}
```

That's it. Caddy handles the certificate, HTTP→HTTPS redirect, and renewal.

**More complete Caddyfile:**

```
yourdomain.com {
    reverse_proxy localhost:3000 {
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
    }

    handle /static/* {
        root * /var/www
        file_server
    }

    log {
        output file /var/log/caddy/access.log
    }
}
```

**Installation:**

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' \
  | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' \
  | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install caddy
```

### 18.5 Nginx vs Caddy

| | Nginx | Caddy |
|---|---|---|
| SSL setup | Manual (Certbot) | Automatic |
| Config complexity | High | Low |
| Performance | Extremely high | Very high |
| Ecosystem | Massive | Smaller but growing |
| Use when | Complex routing, large teams, maximum control | New projects, simplicity, auto-HTTPS |

For a new personal project or startup: Caddy. For large-scale production with complex routing requirements or an existing Nginx team: Nginx.

---

## 19. Configuration Management — Ansible

### 19.1 IaC vs Configuration Management

Terraform (Section 4) provisions infrastructure — it creates VMs, VPCs, and databases. It answers: **what servers exist?**

Configuration management answers: **what is installed and configured on those servers?** Once Terraform creates 10 EC2 instances, something needs to install Docker, configure Nginx, create users, copy SSH keys, and keep all 10 consistent. That's Ansible's job.

| Tool | Answers |
|---|---|
| Terraform | What infrastructure exists |
| Ansible | What is configured on that infrastructure |

They're complementary, not competing. A typical workflow: Terraform creates the instances, Ansible configures them.

### 19.2 Why Ansible Over Chef and Puppet

Chef and Puppet are older tools that require:
- A master server that nodes check in with periodically
- An agent installed on every managed node
- Learning their own DSLs (Ruby for Chef, Puppet language for Puppet)

Ansible requires:
- **Nothing on managed nodes** — it connects over SSH, which is already there
- YAML playbooks — readable by anyone who understands YAML
- No master server for basic use cases

For most teams starting fresh, Ansible is the right choice. Chef and Puppet make sense if you're joining an organisation already invested in them, or if you need their specific pull-based model (nodes checking in on their own schedule).

### 19.3 Core Concepts

**Inventory** — A list of servers Ansible manages. Static file or dynamic (queried from AWS, GCP, etc.).

**Playbook** — A YAML file describing what should happen on which servers. The main unit of work.

**Task** — A single action: install a package, copy a file, restart a service.

**Module** — Built-in functionality for a task type. `apt` installs packages. `copy` copies files. `systemd` manages services. There are thousands of community modules.

**Role** — A reusable, self-contained collection of tasks, templates, and variables for configuring one thing (e.g., an `nginx` role).

**Handler** — A task that only runs when notified — typically to restart a service after its config file changes.

### 19.4 Inventory

```ini
# inventory.ini
[web]
web1.yourdomain.com
web2.yourdomain.com

[db]
db1.yourdomain.com

[all:vars]
ansible_user=ubuntu
ansible_ssh_private_key_file=~/.ssh/id_rsa

[web:vars]
http_port=80
```

### 19.5 Writing Playbooks

```yaml
# setup-webserver.yml
---
- name: Configure web servers
  hosts: web
  become: yes       # sudo
  vars:
    app_port: 3000
    node_version: "20"

  tasks:
    - name: Update apt cache
      apt:
        update_cache: yes
        cache_valid_time: 3600   # only update if cache is older than 1 hour

    - name: Install required packages
      apt:
        name:
          - nginx
          - git
          - curl
        state: present

    - name: Install Node.js
      shell: |
        curl -fsSL https://deb.nodesource.com/setup_{{ node_version }}.x | bash -
        apt-get install -y nodejs
      args:
        creates: /usr/bin/node   # skip if already installed — makes it idempotent

    - name: Copy nginx config
      template:
        src: templates/nginx.conf.j2
        dest: /etc/nginx/sites-available/myapp
        mode: '0644'
      notify: Reload nginx      # only runs the handler if this task changed something

    - name: Enable nginx site
      file:
        src: /etc/nginx/sites-available/myapp
        dest: /etc/nginx/sites-enabled/myapp
        state: link

    - name: Ensure nginx is started and enabled
      systemd:
        name: nginx
        state: started
        enabled: yes

  handlers:
    - name: Reload nginx
      systemd:
        name: nginx
        state: reloaded
```

**Jinja2 template (`templates/nginx.conf.j2`):**

```
server {
    listen 80;
    server_name {{ inventory_hostname }};

    location / {
        proxy_pass http://localhost:{{ app_port }};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Running playbooks:**

```bash
ansible-playbook -i inventory.ini setup-webserver.yml

# Dry run — show what would change without changing anything
ansible-playbook -i inventory.ini setup-webserver.yml --check

# Run only tasks tagged 'nginx'
ansible-playbook -i inventory.ini setup-webserver.yml --tags nginx

# Limit to a specific host
ansible-playbook -i inventory.ini setup-webserver.yml --limit web1.yourdomain.com

# Pass extra variables at runtime
ansible-playbook -i inventory.ini setup-webserver.yml -e "node_version=22"
```

**Ad-hoc commands — one-liners for quick tasks:**

```bash
ansible all -i inventory.ini -m ping                                        # Ping all hosts
ansible web -i inventory.ini -m shell -a "df -h"                           # Check disk space
ansible web -i inventory.ini -m apt -a "name=htop state=present" --become  # Install a package
ansible web -i inventory.ini -m systemd -a "name=nginx state=restarted" --become
```

### 19.6 Roles

Roles package tasks for reuse. The directory structure is conventional:

```
roles/
└── nginx/
    ├── tasks/
    │   └── main.yml       # Tasks
    ├── handlers/
    │   └── main.yml       # Handlers
    ├── templates/
    │   └── nginx.conf.j2  # Jinja2 templates
    ├── files/
    │   └── nginx.pem      # Static files to copy
    ├── vars/
    │   └── main.yml       # Role variables
    └── defaults/
        └── main.yml       # Default values (overridable by caller)
```

Using roles in a playbook:

```yaml
- name: Configure servers
  hosts: web
  become: yes
  roles:
    - nginx
    - nodejs
    - monitoring
```

**Ansible Galaxy** — community role registry. Don't write an Nginx role from scratch:

```bash
ansible-galaxy install geerlingguy.nginx
ansible-galaxy install -r requirements.yml   # install from a requirements file
```

### 19.7 Ansible Vault — Encrypting Secrets

```bash
# Create an encrypted vars file
ansible-vault create vars/secrets.yml

# Edit an encrypted file
ansible-vault edit vars/secrets.yml

# Run a playbook with vault password
ansible-playbook playbook.yml --ask-vault-pass

# Better for CI — use a password file
ansible-playbook playbook.yml --vault-password-file .vault_pass
```

The encrypted file looks like normal YAML when decrypted:

```yaml
db_password: supersecretpassword
api_key: your-api-key-here
```

---

## 20. Serverless

### 20.1 What Serverless Means

"Serverless" doesn't mean no servers — it means you don't manage servers. You deploy a function; the platform handles provisioning, scaling, and maintenance.

**Traditional server:** You provision a VM, it runs 24/7, you pay whether or not there's traffic.

**Serverless:** Your function runs only when called. At zero traffic, you pay zero.

The trade-off: you give up control (can't tune the OS, can't keep long-lived connections, have execution time limits) in exchange for zero operational overhead and infinite automatic scaling.

### 20.2 When Serverless Makes Sense

**Good fit:**
- Infrequent or bursty traffic — a webhook handler that fires 100 times per day
- Event-driven tasks — resize an image when it's uploaded to S3
- Scheduled jobs — run a database cleanup every night at 2 AM
- APIs with unpredictable or spiky traffic patterns

**Poor fit:**
- Long-running processes — Lambda has a 15-minute max execution time
- Low-latency requirements — cold starts add 100ms–2s on first invocation
- WebSocket servers or any stateful, persistent connections
- High, steady traffic — at sustained scale, Lambda can cost more than a reserved EC2 instance

### 20.3 AWS Lambda

Lambda is the dominant serverless platform. Functions are triggered by event sources.

**Common triggers:**

| Trigger | Use case |
|---|---|
| API Gateway | HTTP request → Lambda (REST API) |
| S3 Event | File uploaded → Lambda (process it) |
| SQS | Message in queue → Lambda (worker) |
| EventBridge | Cron schedule → Lambda (scheduled job) |
| DynamoDB Stream | DB change → Lambda (react to writes) |
| SNS | Notification → Lambda (fan-out processing) |

**Basic Lambda function (Node.js):**

```javascript
// handler.js
exports.handler = async (event, context) => {
  // event.body contains the HTTP request body when triggered via API Gateway
  const body = JSON.parse(event.body);

  const result = await processData(body);

  return {
    statusCode: 200,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ success: true, data: result }),
  };
};
```

**Deploy via AWS CLI:**

```bash
zip -r function.zip handler.js node_modules/

aws lambda create-function \
  --function-name my-function \
  --runtime nodejs20.x \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-role \
  --handler handler.handler \
  --zip-file fileb://function.zip \
  --timeout 30 \
  --memory-size 256

# Update code only
aws lambda update-function-code \
  --function-name my-function \
  --zip-file fileb://function.zip

# Test invoke
aws lambda invoke \
  --function-name my-function \
  --payload '{"body":"{\"key\":\"value\"}"}' \
  output.json
```

### 20.4 Cold Starts

A cold start occurs when Lambda initialises a new execution environment — downloading your code, starting the runtime, running top-level initialisation. This adds latency on the first invocation after idle.

**Approximate cold start times by runtime:**

| Runtime | Cold start |
|---|---|
| Node.js | 100–300ms |
| Python | 100–300ms |
| Go | 100–200ms |
| Java | 1–5s |
| .NET | 1–3s |

**Minimising cold starts:**

Move initialisation code outside the handler — it's cached and reused across warm invocations:

```javascript
// Good — DB connection created once, reused on subsequent calls
const db = new Pool({ host: process.env.DB_HOST });

exports.handler = async (event) => {
  const result = await db.query('SELECT ...');   // no reconnect cost
  return result;
};
```

Keep your deployment package small — large `node_modules` increases init time. Use **Provisioned Concurrency** to keep N instances always warm if cold starts are unacceptable for your use case.

### 20.5 Serverless Framework

The Serverless Framework manages packaging, IAM role creation, and deployment:

```yaml
# serverless.yml
service: my-api

provider:
  name: aws
  runtime: nodejs20.x
  region: us-east-1

functions:
  api:
    handler: handler.handler
    events:
      - httpApi:
          path: /users
          method: GET
      - httpApi:
          path: /users/{id}
          method: GET

  processUpload:
    handler: upload.handler
    events:
      - s3:
          bucket: my-uploads-bucket
          event: s3:ObjectCreated:*

  nightlyCleanup:
    handler: cleanup.handler
    events:
      - schedule: cron(0 2 * * ? *)   # 2 AM UTC daily
```

```bash
npm install -g serverless
serverless deploy          # deploy everything
serverless deploy -f api   # deploy one function
serverless logs -f api -t  # tail logs
serverless remove          # tear down everything
```

### 20.6 Cloudflare Workers — Edge Serverless

Cloudflare Workers run JavaScript/TypeScript at Cloudflare's edge — 300+ locations worldwide. Unlike Lambda (which runs in one AWS region), Workers run in the location closest to the user.

**No cold starts** — Workers run in V8 isolates, not full Node.js processes. They're always warm but have a 10ms CPU time limit on the free tier and no access to Node.js APIs.

```javascript
// worker.js
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (url.pathname === '/api/hello') {
      return new Response(JSON.stringify({ message: 'Hello from the edge' }), {
        headers: { 'Content-Type': 'application/json' },
      });
    }

    return fetch(request);   // pass everything else to the origin
  },
};
```

```bash
npm install -g wrangler
wrangler login
wrangler deploy
```

Use Workers for: auth middleware, request routing, A/B testing, edge caching logic, geographic redirects — anything lightweight that benefits from running close to users.

---

## 21. Artifact Management

### 21.1 What Artifact Management Is

An artifact is anything your build process produces — a Docker image, an npm package, a compiled JAR, a Python wheel, a binary. Artifact management means storing, versioning, and distributing these outputs reliably across your pipeline.

Without a proper registry:
- You can't guarantee the exact binary that was tested is the one that gets deployed — rebuilding from source can produce different results if a dependency changed
- You have no single source of truth for what's in production
- You can't enforce access control on deployable artifacts

### 21.2 Container Image Registries

**Docker Hub** — the public default. Free tier has pull rate limits. Fine for public images and personal projects.

**GitHub Container Registry (GHCR)** — the easiest choice if you're on GitHub. Uses the same `GITHUB_TOKEN` as Actions — no extra credentials:

```yaml
# GitHub Actions
- name: Log in to GHCR
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: |
      ghcr.io/${{ github.repository }}:latest
      ghcr.io/${{ github.repository }}:${{ github.sha }}
```

**AWS ECR (Elastic Container Registry)** — the right choice when deploying to ECS or EKS. No egress fees within AWS:

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Create a repository
aws ecr create-repository --repository-name my-app --region us-east-1

# Tag and push
docker tag my-app:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/my-app:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/my-app:latest
```

**ECR image lifecycle policy** — automatically delete old images to control storage cost:

```json
{
  "rules": [{
    "rulePriority": 1,
    "description": "Keep last 10 images",
    "selection": {
      "tagStatus": "any",
      "countType": "imageCountMoreThan",
      "countNumber": 10
    },
    "action": { "type": "expire" }
  }]
}
```

### 21.3 Nexus Repository Manager

Nexus is the most widely deployed self-hosted artifact manager. It handles multiple package formats in one place: Docker, npm, Maven, PyPI, NuGet, Helm charts.

**Why self-host:**
- Air-gapped environments with no internet access in production
- Proxy and cache public registries — if npm or Docker Hub is down, your builds still work
- One internal registry for all artifact types
- Consistent access control across package formats

```bash
# Pull through Nexus proxy — caches the image locally on first pull
docker pull nexus.yourdomain.com:8082/library/node:20

# Push a private image
docker tag my-app nexus.yourdomain.com:8083/my-app:1.0.0
docker push nexus.yourdomain.com:8083/my-app:1.0.0
```

```bash
# .npmrc — point npm at your Nexus proxy
registry=https://nexus.yourdomain.com/repository/npm-proxy/
```

**JFrog Artifactory** is the commercial alternative with a better UI, native Kubernetes support, and stronger security features. It's the enterprise standard in Java/Maven-heavy organisations. For most teams starting out: GHCR for containers + standard npm. Nexus or Artifactory only if you have air-gapped, compliance, or multi-format requirements.

### 21.4 Tagging Strategy

**Never use `latest` for production deployments.** `latest` is mutable — it points to different images at different times. You can't audit which version is running.

A solid strategy:

```bash
# Tag with git SHA — immutable, always traceable to a commit
docker tag my-app ghcr.io/org/my-app:a3f9b1c2

# Also tag with semver for explicit version references
docker tag my-app ghcr.io/org/my-app:v1.4.2

# Also tag with branch name for staging
docker tag my-app ghcr.io/org/my-app:main
```

Your Kubernetes manifests always reference the SHA tag. The CI pipeline sets it:

```yaml
- name: Set image tag
  run: echo "IMAGE_TAG=${GITHUB_SHA::8}" >> $GITHUB_ENV

- name: Deploy
  run: |
    kubectl set image deployment/my-app \
      my-app=ghcr.io/org/my-app:${{ env.IMAGE_TAG }}
```

---

## 22. Cloud Design Patterns

### 22.1 Why These Patterns Matter

Cloud systems fail in ways that local systems don't — network calls fail transiently, services go down independently, latency spikes unpredictably. These patterns are proven solutions to recurring distributed systems problems. They're not code patterns — they're architectural decisions about how services communicate and recover.

### 22.2 Availability Patterns

**Circuit Breaker**

Wraps calls to an external service and stops calling it if it's failing — giving it time to recover rather than hammering it with requests that will all fail.

```
State machine:
CLOSED (normal) → too many failures → OPEN (fast-fail all requests)
OPEN → timeout → HALF-OPEN (allow one test request)
HALF-OPEN → success → CLOSED | failure → OPEN again
```

```javascript
const CircuitBreaker = require('opossum');

const breaker = new CircuitBreaker(callExternalService, {
  timeout: 3000,
  errorThresholdPercentage: 50,   // open after 50% failure rate
  resetTimeout: 30000,             // retry after 30 seconds
});

breaker.fallback(() => getCachedData());   // return cached data when open
```

**Retry with Exponential Backoff**

Transient failures resolve on their own. Retrying immediately adds load. Retrying with increasing delays gives the upstream time to recover.

```javascript
async function callWithRetry(fn, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxRetries) throw error;
      const delay = Math.pow(2, attempt) * 100;   // 200ms, 400ms, 800ms
      const jitter = Math.random() * 100;          // prevents thundering herd
      await sleep(delay + jitter);
    }
  }
}
```

**Bulkhead**

Isolate parts of your system so a failure in one doesn't cascade. Named after ship compartments — if one floods, the others stay dry.

In practice: give each downstream service its own connection pool with a fixed max size. A failing payment service can't exhaust all connections and take down auth with it.

**Health Endpoint Monitoring**

Every service exposes a `/health` endpoint that checks its own dependencies:

```javascript
app.get('/health', async (req, res) => {
  const checks = await Promise.allSettled([
    db.query('SELECT 1'),
    redis.ping(),
  ]);

  const healthy = checks.every(c => c.status === 'fulfilled');
  res.status(healthy ? 200 : 503).json({
    status: healthy ? 'healthy' : 'degraded',
    checks: { database: checks[0].status, redis: checks[1].status },
  });
});
```

Load balancers and Kubernetes readiness probes call this. Non-200 responses remove the instance from rotation.

### 22.3 Data Management Patterns

**CQRS — Command Query Responsibility Segregation**

Separate the model for writing data from the model for reading it.

```
Write path: Command → Command Handler → Write Model → Database (normalised)
Read path:  Query  → Query Handler  → Read Model  → Read-optimised view
```

Write models enforce business rules and maintain consistency. Read models are optimised for how data is queried — often denormalised, pre-joined, cached. One model trying to do both is compromised at both. Use CQRS when read and write patterns differ significantly, or you need to scale them independently.

**Event Sourcing**

Instead of storing the current state of a record, store the sequence of events that produced it.

```
Traditional:    { userId: 1, balance: 750 }

Event sourced:
  AccountOpened   amount: 1000
  WithdrawalMade  amount: 200
  DepositMade     amount: 50
  WithdrawalMade  amount: 100
  → current balance: 1000 - 200 + 50 - 100 = 750
```

Benefits: complete audit trail, ability to replay events to rebuild state, ability to derive multiple read projections from the same event stream. Cost: more complex to query current state, requires event replay infrastructure.

**Saga Pattern**

Manages distributed transactions across multiple services without a two-phase commit. A saga is a sequence of local transactions, each publishing an event that triggers the next — with compensating transactions that undo completed steps if a later step fails.

```
Order placement saga:
1. OrderService: Create order (PENDING) → emit OrderCreated
2. PaymentService: Charge payment → emit PaymentCharged
   on failure: emit PaymentFailed → compensate step 1 (cancel order)
3. InventoryService: Reserve stock → emit StockReserved
   on failure: emit StockUnavailable → compensate steps 1-2
4. OrderService: Confirm order (CONFIRMED)
```

### 22.4 Design and Implementation Patterns

**Strangler Fig**

Migrate a legacy system incrementally. Build new functionality alongside the old system and route traffic piece by piece until the legacy system can be removed.

```
Phase 1: New feature A → new system | everything else → legacy
Phase 2: Feature group B → new system | remaining → legacy
Phase 3: All requests → new system | legacy decommissioned
```

An API gateway or load balancer handles the routing split. This is how you rewrite a monolith to microservices without a risky big-bang rewrite.

**Anti-Corruption Layer**

When integrating with an external system, put a translation layer between it and your domain. Your code talks to the ACL in your own language; the ACL translates to the external system's API. Prevents the external model from corrupting your domain — you can swap the external system later by only changing the ACL.

**Backends for Frontends (BFF)**

Instead of one general-purpose API serving all clients, create a dedicated backend for each client type:

```
Mobile app → Mobile BFF  ↘
Web app    → Web BFF      → Core services
Partners   → Partner API ↗
```

Mobile needs different response shapes, different auth flows, and different data granularity than web. A general API compromises for all; a BFF is optimised for one.

### 22.5 Management and Monitoring Patterns

**Sidecar**

Deploy a secondary container alongside your application container that provides supporting capabilities (logging, monitoring, proxying) without modifying the application itself.

```yaml
spec:
  containers:
    - name: my-app         # main application
      image: my-app:v1
    - name: log-shipper    # sidecar ships logs to central store
      image: fluent-bit:latest
```

This is how Istio works — it injects an Envoy sidecar into every pod to handle mTLS, retries, and observability without touching your application code.

**Throttling**

Control the rate of resource consumption to protect services from being overwhelmed. At scale this runs in Redis so limits apply across all service instances:

```javascript
// Token bucket — Redis-backed so it works across multiple instances
async function checkRateLimit(userId) {
  const key = `ratelimit:${userId}`;
  const requests = await redis.incr(key);
  if (requests === 1) await redis.expire(key, 60);   // set 60-second window on first request
  return requests <= 100;   // allow 100 requests per 60 seconds
}
```

**Queue-Based Load Levelling**

Place a queue between a producer and a consumer so traffic spikes don't overwhelm the downstream service. The producer writes to the queue at any rate; the consumer processes at a controlled rate.

```
High-volume event → SQS queue → Lambda worker (processes at controlled rate)
```

This decouples throughput from processing capacity. The queue absorbs spikes; the worker processes at whatever rate it can sustain. Used extensively in this codebase's planned BullMQ migration (see Part 21).

---

*Last updated: 2026 — Built from real deployment experience and study.*
