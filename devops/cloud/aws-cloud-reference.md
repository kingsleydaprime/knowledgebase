# AWS Cloud — Comprehensive Reference Guide

> A deep, practical reference covering AWS from first principles to production architecture.
> Covers IAM, EC2, S3, RDS, VPC, ECS/Fargate, ECR, ALB, CloudWatch, Route53, ACM,
> and how to architect a production-ready application end-to-end.
> Written for a Systems Engineer progressing toward cloud architecture.

---

## Table of Contents

1. [How AWS Works — The Mental Model](#1-how-aws-works--the-mental-model)
2. [IAM — Identity and Access Management](#2-iam--identity-and-access-management)
3. [VPC — Virtual Private Cloud](#3-vpc--virtual-private-cloud)
4. [EC2 — Elastic Compute Cloud](#4-ec2--elastic-compute-cloud)
5. [S3 — Simple Storage Service](#5-s3--simple-storage-service)
6. [RDS — Relational Database Service](#6-rds--relational-database-service)
7. [ECR — Elastic Container Registry](#7-ecr--elastic-container-registry)
8. [ECS and Fargate — Container Orchestration](#8-ecs-and-fargate--container-orchestration)
9. [ALB — Application Load Balancer](#9-alb--application-load-balancer)
10. [CloudWatch — Observability](#10-cloudwatch--observability)
11. [Route 53 — DNS](#11-route-53--dns)
12. [ACM — Certificate Manager](#12-acm--certificate-manager)
13. [ElastiCache — Managed Redis](#13-elasticache--managed-redis)
14. [Secrets Manager and Parameter Store](#14-secrets-manager-and-parameter-store)
15. [How Traffic Flows — Browser to App and Back](#15-how-traffic-flows--browser-to-app-and-back)
16. [Production Architecture on AWS](#16-production-architecture-on-aws)
17. [Free Tier — What You Get and How to Stay In It](#17-free-tier--what-you-get-and-how-to-stay-in-it)
18. [AWS CLI and SDK](#18-aws-cli-and-sdk)
19. [Cost Optimisation](#19-cost-optimisation)
20. [Security Hardening Checklist](#20-security-hardening-checklist)

---

## 1. How AWS Works — The Mental Model

### 1.1 The Global Infrastructure

AWS runs a physical network of datacenters organised into three levels:

**Regions** — geographically isolated locations (us-east-1, eu-west-1, af-south-1, etc.). Each region is independent — a failure in us-east-1 does not affect eu-west-1. Currently 30+ regions.

**Availability Zones (AZs)** — physically separate datacenters within a region, connected by high-speed private fibre. Each region has at least 3 AZs. `us-east-1a`, `us-east-1b`, `us-east-1c` are separate buildings with separate power, cooling, and networking. Deploy across multiple AZs for high availability.

**Edge Locations** — hundreds of PoPs (Points of Presence) worldwide used by CloudFront (CDN) and Route 53. Closer to users than regions.

```
Global
  ├── Region: us-east-1 (N. Virginia)
  │     ├── AZ: us-east-1a  (datacenter A)
  │     ├── AZ: us-east-1b  (datacenter B)
  │     └── AZ: us-east-1c  (datacenter C)
  ├── Region: eu-west-1 (Ireland)
  │     ├── AZ: eu-west-1a
  │     └── ...
  └── Region: af-south-1 (Cape Town)
        └── ...
```

### 1.2 How AWS Services Relate

AWS has 200+ services. For a production web application you need about 10:

```
Internet
  ↓
Route 53 (DNS) → resolves your domain to the ALB IP
  ↓
CloudFront (CDN) → optional, serves static assets at edge
  ↓
ACM (SSL certificate) → terminates HTTPS at the load balancer
  ↓
ALB (Application Load Balancer) → distributes traffic across containers
  ↓
ECS/Fargate (Containers) → runs your application code
  ↓
  ├── RDS (PostgreSQL) → relational data
  ├── ElastiCache (Redis) → caching and queues
  ├── S3 (Object storage) → files, images, backups
  └── Secrets Manager → database passwords, API keys

Supporting:
  ├── VPC (networking) → private network your resources live in
  ├── IAM (identity) → who can access what
  ├── ECR (container registry) → stores your Docker images
  └── CloudWatch (observability) → logs, metrics, alarms
```

### 1.3 The Account and Region Model

Everything in AWS is scoped to an **account** and a **region**. Resources in `us-east-1` are invisible to `eu-west-1` unless you explicitly set up cross-region access.

**Root account** — the email you used to sign up. Has unlimited access. Do not use for day-to-day work. Enable MFA immediately. Create IAM users for all actual work.

**AWS Console** — web UI at `console.aws.amazon.com`. Good for exploration and setup.

**AWS CLI** — command-line tool. Good for scripting and automation.

**AWS SDK** — libraries for Node.js, Java, Python, etc. Used inside your application code.

---

## 2. IAM — Identity and Access Management

### 2.1 What IAM Is

IAM (Identity and Access Management) controls who can do what in your AWS account. It answers two questions: **authentication** (who are you?) and **authorisation** (what are you allowed to do?).

IAM is global — it applies across all regions.

### 2.2 Core Concepts

**IAM User** — a permanent identity with credentials (username + password for console, access key + secret for CLI/SDK). Represents a human or a machine that needs long-lived credentials.

**IAM Group** — a collection of users. Attach policies to the group and all members inherit them. Never attach policies directly to users — always use groups.

**IAM Role** — an identity with permissions but **no long-lived credentials**. A role is assumed temporarily. EC2 instances, ECS tasks, Lambda functions, and cross-account access all use roles. Roles are how AWS services access other AWS services.

**IAM Policy** — a JSON document defining what actions are allowed or denied on which resources. Attached to users, groups, or roles.

### 2.3 Policy Structure

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3ReadOnSpecificBucket",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-app-bucket",
        "arn:aws:s3:::my-app-bucket/*"
      ]
    },
    {
      "Sid": "DenyDeleteEverywhere",
      "Effect": "Deny",
      "Action": "s3:DeleteObject",
      "Resource": "*"
    }
  ]
}
```

**Effect** — `Allow` or `Deny`. Explicit Deny always wins over Allow.

**Action** — the AWS API operation. `s3:GetObject`, `ec2:RunInstances`, `rds:CreateDBInstance`. Use `*` for all actions in a service.

**Resource** — the ARN (Amazon Resource Name) of the specific resource. `arn:aws:s3:::bucket-name/*` means all objects in `bucket-name`.

**Condition** — optional. Apply policy only when conditions match (specific IP, MFA required, time of day).

### 2.4 ARN Format

ARNs uniquely identify any AWS resource:

```
arn:aws:service:region:account-id:resource-type/resource-id

Examples:
arn:aws:s3:::my-bucket                           (S3 bucket — no region/account)
arn:aws:s3:::my-bucket/uploads/*                 (all objects in uploads/ prefix)
arn:aws:ec2:us-east-1:123456789:instance/i-abc   (EC2 instance)
arn:aws:rds:us-east-1:123456789:db:mydb          (RDS instance)
arn:aws:iam::123456789:user/kingsley             (IAM user)
arn:aws:iam::123456789:role/ECSTaskRole          (IAM role)
```

### 2.5 IAM Roles for Services (The Right Way)

Your ECS task should not use an access key. It should have an IAM role that grants it permissions. The task assumes the role automatically — AWS injects temporary credentials that rotate every hour.

```
ECS Task → assumes → ECSTaskRole
  ECSTaskRole policy:
    Allow: s3:GetObject on arn:aws:s3:::my-app-bucket/*
    Allow: secretsmanager:GetSecretValue on arn:aws:secretsmanager:*:*:secret:my-app/*
    Allow: logs:CreateLogGroup, logs:PutLogEvents on *
```

**Never hardcode AWS credentials in application code.** Use roles for services, environment variables for local dev, Secrets Manager for secrets.

### 2.6 Least Privilege Principle

Grant only the permissions actually needed. Start with no permissions and add what's required.

```
Bad:  Attach AdministratorAccess to your app's role
Good: Allow only the specific S3 bucket, specific secret, specific log group

Bad:  One IAM user for everything
Good: Separate roles per service, separate users per human
```

### 2.7 Setting Up a Secure Account

```bash
# 1. Enable MFA on root account immediately (Console → Account → MFA)

# 2. Create an admin IAM user for yourself (don't use root day-to-day)
aws iam create-user --user-name kingsley-admin
aws iam add-user-to-group --user-name kingsley-admin --group-name Administrators
aws iam create-access-key --user-name kingsley-admin

# 3. Create programmatic user for CI/CD
aws iam create-user --user-name github-actions-deploy
# Attach a custom policy: only what deployment needs

# 4. Enable IAM Access Analyzer (finds overly-permissive policies)
aws accessanalyzer create-analyzer --analyzer-name my-analyzer --type ACCOUNT

# 5. Set up billing alerts (see Section 17)
```

### 2.8 Common Managed Policies (Know These)

| Policy Name | What it grants |
|---|---|
| `AdministratorAccess` | Full access to everything — use only for admin users |
| `PowerUserAccess` | Full access except IAM management |
| `ReadOnlyAccess` | Read-only access to all services |
| `AmazonS3FullAccess` | Full S3 access |
| `AmazonRDSFullAccess` | Full RDS access |
| `AmazonECS_FullAccess` | Full ECS access |
| `CloudWatchFullAccess` | Full CloudWatch access |
| `AmazonEC2ContainerRegistryFullAccess` | Full ECR access |

For production, create **custom policies** that grant only what's needed rather than using these broad managed policies.

---

## 3. VPC — Virtual Private Cloud

### 3.1 What a VPC Is

A VPC (Virtual Private Cloud) is your private, isolated network inside AWS. Think of it as your own private section of the AWS cloud with its own IP address range, subnets, routing rules, and firewalls. Nothing can enter your VPC unless you explicitly allow it.

Every AWS account gets a **default VPC** in each region. It works out of the box but is not suitable for production — create a custom VPC.

### 3.2 CIDR Blocks

IP address ranges use CIDR notation. A VPC typically uses a private IP range:

```
10.0.0.0/16     → 65,536 IP addresses (10.0.0.0 to 10.0.255.255)
172.16.0.0/12   → 1,048,576 IP addresses
192.168.0.0/16  → 65,536 IP addresses

/16 = 16-bit mask = 65,536 addresses = good VPC size
/24 = 24-bit mask = 256 addresses = good subnet size
/28 = 28-bit mask = 16 addresses = minimum subnet size
```

### 3.3 Subnets

A subnet is a subdivision of your VPC's IP range, locked to a specific AZ.

**Public subnet** — has a route to the Internet Gateway. Resources here can be reached from the internet (if they have a public IP). Load balancers and bastion hosts live here.

**Private subnet** — no route to the Internet Gateway. Resources here are not directly reachable from the internet. Your application servers, databases, and caches live here.

```
VPC: 10.0.0.0/16
  ├── Public Subnet A  (10.0.1.0/24) — AZ us-east-1a
  ├── Public Subnet B  (10.0.2.0/24) — AZ us-east-1b
  ├── Private Subnet A (10.0.11.0/24) — AZ us-east-1a
  └── Private Subnet B (10.0.12.0/24) — AZ us-east-1b
```

Why two of each? High availability — if AZ `us-east-1a` goes down, resources in `us-east-1b` keep running.

### 3.4 Internet Gateway (IGW)

A horizontally-scaled, redundant gateway that allows communication between your VPC and the internet. Attach one to your VPC and add a route in your public subnet's route table pointing `0.0.0.0/0` to it.

```
Public Subnet Route Table:
  Destination     Target
  10.0.0.0/16     local          (internal VPC traffic)
  0.0.0.0/0       igw-abc123     (everything else → internet)
```

### 3.5 NAT Gateway

Resources in private subnets can't reach the internet through the IGW (because they have no public IPs and no IGW route). But they often need outbound internet access — to pull Docker images, download dependencies, call external APIs.

The NAT Gateway sits in a **public subnet**, has a public IP, and forwards outbound traffic from private subnets to the internet. It translates the private IP to its public IP (Network Address Translation).

```
Private Subnet Route Table:
  Destination     Target
  10.0.0.0/16     local
  0.0.0.0/0       nat-abc123     (outbound internet via NAT in public subnet)

Public Subnet Route Table:
  Destination     Target
  10.0.0.0/16     local
  0.0.0.0/0       igw-abc123     (NAT gateway uses this to reach internet)
```

**NAT Gateway costs money** (~$0.045/hr + $0.045/GB). For dev environments, use a NAT instance (cheaper but more work) or temporarily put resources in a public subnet.

### 3.6 Security Groups

Security groups are stateful virtual firewalls attached to individual resources (EC2, RDS, ECS tasks). They control what traffic can reach the resource.

**Stateful** — if you allow inbound traffic, the response is automatically allowed outbound. You don't need to add an explicit outbound rule for responses.

```
ALB Security Group:
  Inbound:
    Port 443 (HTTPS) from 0.0.0.0/0    (internet)
    Port 80  (HTTP)  from 0.0.0.0/0    (redirect to HTTPS)
  Outbound:
    All traffic to 0.0.0.0/0           (default — allow all outbound)

App Security Group (ECS tasks):
  Inbound:
    Port 3000 from ALB Security Group  (only ALB can reach app)
  Outbound:
    Port 5432 to RDS Security Group    (app → DB)
    Port 6379 to Redis Security Group  (app → Redis)
    Port 443  to 0.0.0.0/0            (app → external APIs, S3)

RDS Security Group:
  Inbound:
    Port 5432 from App Security Group  (only app can reach DB)
  Outbound: none needed (stateful)
```

**Security group IDs as sources** — instead of IP ranges, you can reference another security group as the source. This means "anything in that security group" — much better than hardcoding IPs which change.

### 3.7 Network ACLs

NACLs (Network Access Control Lists) operate at the subnet level. They are **stateless** — you must explicitly allow both inbound and outbound for each flow. They're evaluated in numbered order and stop at the first match.

Use security groups for most access control. NACLs are for coarse subnet-level rules — blocking a known bad IP range, for example.

### 3.8 VPC Endpoints

Normally, traffic from your VPC to S3 goes out to the internet (via NAT Gateway) and back. A **VPC Endpoint** creates a private connection from your VPC directly to S3 (or other AWS services) without leaving the AWS network.

```
Without endpoint: ECS task → NAT Gateway → internet → S3
With endpoint:    ECS task → VPC Endpoint → S3 (private, faster, free)
```

Gateway endpoints (S3 and DynamoDB) are free. Interface endpoints (most other services) cost money.

### 3.9 Building a Production VPC

```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=prod-vpc}]'

# Create subnets
aws ec2 create-subnet --vpc-id vpc-xxx \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-a}]'

# (repeat for each subnet)

# Create and attach Internet Gateway
aws ec2 create-internet-gateway
aws ec2 attach-internet-gateway --vpc-id vpc-xxx --internet-gateway-id igw-xxx

# Create route table for public subnets
aws ec2 create-route-table --vpc-id vpc-xxx
aws ec2 create-route --route-table-id rtb-xxx \
  --destination-cidr-block 0.0.0.0/0 --gateway-id igw-xxx
aws ec2 associate-subnet-with-route-table --subnet-id subnet-xxx --route-table-id rtb-xxx

# Create NAT Gateway (in public subnet)
aws ec2 allocate-address --domain vpc  # creates Elastic IP
aws ec2 create-nat-gateway \
  --subnet-id subnet-public-a \
  --allocation-id eipalloc-xxx

# In practice: use Terraform or CloudFormation for all of this
```

---

## 4. EC2 — Elastic Compute Cloud

### 4.1 What EC2 Is

EC2 (Elastic Compute Cloud) provides virtual machines (instances) in AWS. You pick an instance type (CPU + RAM), an OS image (AMI), and it boots up in minutes. You pay by the second.

With ECS/Fargate, you don't manage EC2 directly for your application. But you still need to understand EC2 because it underpins almost everything in AWS.

### 4.2 Instance Types

Instance type names follow a pattern:

```
m7g.large

m   = family (m=general purpose, c=compute, r=memory, t=burstable, g=GPU)
7   = generation (higher = newer, better price/performance)
g   = processor type (blank=Intel, a=AMD, g=Graviton/ARM)
.
large = size (nano, micro, small, medium, large, xlarge, 2xlarge, ...)

Common families:
  t3/t4g  → burstable, development and small workloads
  m6i/m7g → general purpose, balanced CPU/RAM
  c6i/c7g → compute optimised, CPU-heavy workloads
  r6i/r7g → memory optimised, large datasets
  g4dn    → GPU, ML inference and training
```

**Graviton (ARM)** instances (suffix `g`) are 20–40% cheaper and 20–40% better performance than x86 equivalents. Use them if your Docker images support ARM (`linux/arm64`).

### 4.3 AMIs — Amazon Machine Images

An AMI is a snapshot of an OS (and optionally installed software) used to launch instances.

```
Common AMIs:
  Amazon Linux 2023   → AWS's own Linux, optimised for EC2
  Ubuntu 22.04        → familiar, widely used
  Ubuntu 24.04        → latest LTS
  Windows Server      → for .NET workloads
  Custom AMI          → your own image with pre-installed software
```

AMIs are regional. An AMI in us-east-1 cannot be used in eu-west-1 without copying it.

### 4.4 EBS — Elastic Block Store

EBS is the persistent disk attached to an EC2 instance. Unlike the instance's local storage (which disappears when the instance stops), EBS volumes survive instance stop/start.

```
Volume types:
  gp3 (General Purpose SSD) → default, good for most workloads, $0.08/GB/month
  gp2                        → older version of gp3, more expensive
  io2 Block Express          → high IOPS, databases, $0.125/GB/month
  st1 (Throughput HDD)       → large sequential reads (data warehouses)
  sc1 (Cold HDD)             → archival, lowest cost

EBS snapshots:
  Point-in-time backups of a volume.
  Stored in S3 (you pay for storage).
  Used to create new volumes or AMIs.
  Incremental — only changed blocks stored after first snapshot.
```

### 4.5 Key Pairs for SSH

To SSH into an EC2 instance, you use a key pair instead of a password:

```bash
# Create key pair (download the .pem file immediately — AWS doesn't store the private key)
aws ec2 create-key-pair --key-name my-key --query 'KeyMaterial' --output text > my-key.pem
chmod 400 my-key.pem

# SSH into instance
ssh -i my-key.pem ec2-user@{public-ip}     # Amazon Linux
ssh -i my-key.pem ubuntu@{public-ip}       # Ubuntu
```

In production, avoid SSH entirely — use **AWS Systems Manager Session Manager** instead. No open port 22, no key pair management, and all sessions are logged.

### 4.6 Instance Metadata Service

From inside an EC2 instance or ECS task, you can query metadata:

```bash
# Get instance ID
curl http://169.254.169.254/latest/meta-data/instance-id

# Get IAM role credentials (this is how the SDK gets credentials automatically)
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/MyRoleName

# IMDSv2 (more secure — requires session token)
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/instance-id
```

### 4.7 User Data — Bootstrapping Instances

User data is a script that runs once when an instance first boots:

```bash
#!/bin/bash
# Example user data for Amazon Linux 2023
yum update -y
yum install -y docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install CloudWatch agent
yum install -y amazon-cloudwatch-agent
```

### 4.8 Auto Scaling

Auto Scaling Groups (ASG) automatically add or remove EC2 instances based on demand:

```
Desired capacity: 2 instances (always running)
Minimum: 1 instance
Maximum: 10 instances

Scaling policies:
  Target tracking: maintain CPU at 70% → add/remove instances to achieve
  Step scaling:    CPU > 80% for 2 min → add 2 instances
  Scheduled:       every weekday 9am → scale to 5 instances

Cooldown: 300 seconds between scaling events (prevents thrashing)
```

With ECS/Fargate, you often don't need ASGs because Fargate scales at the task level.

### 4.9 Pricing Models

| Model | When to use | Savings |
|---|---|---|
| On-Demand | Default, no commitment | 0% (baseline) |
| Reserved (1yr) | Predictable baseline load | ~30-40% |
| Reserved (3yr) | Long-term predictable load | ~60-70% |
| Spot | Fault-tolerant workloads (batch, ML) | up to 90% |
| Savings Plans | Flexible commitment (any instance family) | ~20-50% |

Spot instances can be terminated by AWS with 2 minutes notice when they need the capacity back. Use for stateless, restartable workloads.

---

## 5. S3 — Simple Storage Service

### 5.1 What S3 Is

S3 (Simple Storage Service) stores objects (files) at unlimited scale. An object can be from 1 byte to 5 TB. S3 provides 11 nines of durability (99.999999999%) — data is automatically replicated across multiple AZs in a region.

**Key concepts:**
- **Bucket** — top-level container. Name is globally unique across all AWS. Like a domain name — once taken, no one else can use it.
- **Object** — a file stored in a bucket. Has a key (the path), value (the data), and metadata.
- **Prefix** — a path-like prefix used to organise objects. `uploads/photos/abc.jpg` — `uploads/photos/` is the prefix.

### 5.2 Creating and Configuring a Bucket

```bash
# Create bucket (bucket names are globally unique)
aws s3api create-bucket \
  --bucket my-app-uploads-prod \
  --region us-east-1

# Enable versioning (keeps history of all versions of each object)
aws s3api put-bucket-versioning \
  --bucket my-app-uploads-prod \
  --versioning-configuration Status=Enabled

# Block all public access (default — good)
aws s3api put-public-access-block \
  --bucket my-app-uploads-prod \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,\
    BlockPublicPolicy=true,RestrictPublicBuckets=true

# Enable server-side encryption (AES-256 by default)
aws s3api put-bucket-encryption \
  --bucket my-app-uploads-prod \
  --server-side-encryption-configuration \
    '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
```

### 5.3 Bucket Policy

Controls who can access the bucket and how. Separate from IAM — a bucket policy can grant access to any AWS account, not just your own.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontRead",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudfront.amazonaws.com"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-app-media/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::123456789:distribution/ABCDEFG"
        }
      }
    }
  ]
}
```

### 5.4 Presigned URLs

Presigned URLs grant temporary access to a specific object without requiring the client to have AWS credentials. Perfect for client-side uploads and serving private files.

```typescript
// Node.js — generate presigned URL for upload
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';

const s3 = new S3Client({ region: 'us-east-1' });

async function getUploadUrl(fileKey: string, contentType: string) {
  const command = new PutObjectCommand({
    Bucket: 'my-app-uploads-prod',
    Key: fileKey,
    ContentType: contentType,
  });
  // URL expires in 5 minutes
  return getSignedUrl(s3, command, { expiresIn: 300 });
}

// Generate presigned URL for download (private file)
import { GetObjectCommand } from '@aws-sdk/client-s3';

async function getDownloadUrl(fileKey: string) {
  const command = new GetObjectCommand({
    Bucket: 'my-app-private-bucket',
    Key: fileKey,
  });
  return getSignedUrl(s3, command, { expiresIn: 3600 }); // 1 hour
}
```

```typescript
// Java — generate presigned upload URL
import software.amazon.awssdk.services.s3.presigner.S3Presigner;
import software.amazon.awssdk.services.s3.presigner.model.PutObjectPresignRequest;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;

S3Presigner presigner = S3Presigner.create();

PutObjectRequest objectRequest = PutObjectRequest.builder()
    .bucket("my-app-uploads-prod")
    .key("uploads/" + fileName)
    .contentType("image/jpeg")
    .build();

PutObjectPresignRequest presignRequest = PutObjectPresignRequest.builder()
    .signatureDuration(Duration.ofMinutes(5))
    .putObjectRequest(objectRequest)
    .build();

PresignedPutObjectRequest presignedRequest = presigner.presignPutObject(presignRequest);
String uploadUrl = presignedRequest.url().toString();
```

### 5.5 Storage Classes

| Class | Use case | Retrieval | Cost |
|---|---|---|---|
| Standard | Frequently accessed data | Instant | $0.023/GB |
| Intelligent-Tiering | Unknown or changing access patterns | Instant | $0.023/GB + monitoring fee |
| Standard-IA | Infrequently accessed, quick retrieval | Instant | $0.0125/GB |
| One Zone-IA | Infrequent, can tolerate AZ failure | Instant | $0.01/GB |
| Glacier Instant | Archive, occasional access | Instant | $0.004/GB |
| Glacier Flexible | Long-term archive | 1–12 hours | $0.0036/GB |
| Glacier Deep Archive | Longest-term archive | 12–48 hours | $0.00099/GB |

### 5.6 Lifecycle Rules

Automatically transition objects between storage classes or delete them:

```json
{
  "Rules": [
    {
      "ID": "MoveToGlacierAfter90Days",
      "Status": "Enabled",
      "Transitions": [
        { "Days": 90, "StorageClass": "STANDARD_IA" },
        { "Days": 365, "StorageClass": "GLACIER" }
      ],
      "Expiration": { "Days": 2555 }
    }
  ]
}
```

### 5.7 Static Website Hosting

S3 can host a static website (HTML, CSS, JS — no server-side rendering):

```bash
# Enable static website hosting
aws s3 website s3://my-app-frontend \
  --index-document index.html \
  --error-document index.html  # for SPA routing

# Sync local build to S3
aws s3 sync ./dist s3://my-app-frontend --delete

# The website URL:
# http://my-app-frontend.s3-website-us-east-1.amazonaws.com
# (then put CloudFront in front for HTTPS and caching)
```

### 5.8 S3 CLI Commands

```bash
# List buckets
aws s3 ls

# List objects in bucket
aws s3 ls s3://my-bucket/
aws s3 ls s3://my-bucket/uploads/ --recursive

# Upload file
aws s3 cp ./file.txt s3://my-bucket/file.txt
aws s3 cp ./file.txt s3://my-bucket/file.txt --storage-class STANDARD_IA

# Download file
aws s3 cp s3://my-bucket/file.txt ./file.txt

# Sync local directory to S3
aws s3 sync ./dist s3://my-bucket --delete --exclude "*.DS_Store"

# Delete object
aws s3 rm s3://my-bucket/file.txt

# Delete bucket (must be empty first)
aws s3 rb s3://my-bucket

# Move object
aws s3 mv s3://my-bucket/old.txt s3://my-bucket/new.txt
```

---

## 6. RDS — Relational Database Service

### 6.1 What RDS Is

RDS (Relational Database Service) is a managed database service. AWS handles provisioning, patching, backups, failover, and monitoring. You just connect and run queries.

**Supported engines:** PostgreSQL, MySQL, MariaDB, Oracle, SQL Server, Aurora (PostgreSQL-compatible and MySQL-compatible).

For most projects: **RDS PostgreSQL** or **Aurora PostgreSQL Serverless v2**.

### 6.2 RDS vs Self-Managed Database

| | RDS | Self-managed (on EC2) |
|---|---|---|
| Patching | AWS handles | You manage |
| Backups | Automatic, configurable | You script |
| Failover | Automatic with Multi-AZ | You configure |
| Monitoring | Built-in CloudWatch metrics | You install agents |
| Cost | Higher | Lower hardware cost but your time |
| Control | Limited | Full |

Unless you have a specific reason for full control, use RDS.

### 6.3 Creating an RDS Instance

```bash
# Create a parameter group (custom DB configuration)
aws rds create-db-parameter-group \
  --db-parameter-group-name my-postgres-params \
  --db-parameter-group-family postgres16 \
  --description "Custom PostgreSQL 16 parameters"

# Create a subnet group (RDS needs to know which subnets to use)
aws rds create-db-subnet-group \
  --db-subnet-group-name my-db-subnet-group \
  --db-subnet-group-description "Private subnets for RDS" \
  --subnet-ids subnet-private-a subnet-private-b

# Create the database
aws rds create-db-instance \
  --db-instance-identifier myapp-prod \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 16.1 \
  --master-username appuser \
  --master-user-password "$(aws secretsmanager get-secret-value ...)" \
  --db-name myappdb \
  --allocated-storage 20 \
  --storage-type gp3 \
  --storage-encrypted \
  --db-subnet-group-name my-db-subnet-group \
  --vpc-security-group-ids sg-rds-xxx \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00" \
  --no-publicly-accessible \
  --multi-az
```

### 6.4 Multi-AZ Deployment

With Multi-AZ enabled, RDS maintains a synchronous standby replica in a different AZ. If the primary fails, RDS automatically fails over to the standby — typically within 60–120 seconds. Your connection string stays the same (the endpoint DNS changes).

```
Primary (us-east-1a) ──synchronous replication──► Standby (us-east-1b)
     ↓                                                     ↓
 All reads + writes                               No traffic (just receiving replication)
                                                  Promoted to primary on failover
```

Enable Multi-AZ for production. It's a cost double but worth it.

### 6.5 Read Replicas

Asynchronous replicas that can serve read traffic. Unlike Multi-AZ standbys, read replicas are accessible.

```bash
# Create a read replica
aws rds create-db-instance-read-replica \
  --db-instance-identifier myapp-prod-reader \
  --source-db-instance-identifier myapp-prod \
  --db-instance-class db.t3.medium

# Read replica has its own endpoint:
# myapp-prod-reader.xxxxx.us-east-1.rds.amazonaws.com
```

Route read-heavy operations (reports, feed queries) to the read replica. All writes go to the primary.

### 6.6 Backups and Snapshots

**Automated backups** — RDS takes a daily backup and retains transaction logs. You can restore to any point in time within the retention period (1–35 days).

**Manual snapshots** — you trigger these. They persist until you delete them, even if you delete the RDS instance.

```bash
# Create manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier myapp-prod \
  --db-snapshot-identifier myapp-before-migration

# Restore from snapshot (creates a new RDS instance)
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier myapp-restored \
  --db-snapshot-identifier myapp-before-migration

# Restore to point in time
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier myapp-prod \
  --target-db-instance-identifier myapp-restored \
  --restore-time 2026-01-15T14:30:00Z
```

### 6.7 Connection Strings

```
PostgreSQL: postgresql://user:password@myapp.xxxxx.us-east-1.rds.amazonaws.com:5432/myappdb
MySQL:      mysql://user:password@myapp.xxxxx.us-east-1.rds.amazonaws.com:3306/myappdb
```

**RDS Proxy** — a connection pooler managed by AWS. Sits between your application and RDS, pools connections so your app can have thousands of connections without overwhelming the database. Essential for Lambda functions (which open a new connection on every invocation).

### 6.8 RDS Free Tier

- db.t3.micro or db.t4g.micro: **750 hours/month free** (12 months)
- 20 GB of General Purpose Storage
- 20 GB of backup storage

---

## 7. ECR — Elastic Container Registry

### 7.1 What ECR Is

ECR (Elastic Container Registry) is AWS's Docker image registry — the same concept as Docker Hub but private and integrated with AWS. Your CI/CD pipeline pushes images here; ECS pulls from here.

### 7.2 Creating a Repository and Pushing Images

```bash
# Create a repository
aws ecr create-repository \
  --repository-name my-app \
  --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=AES256

# Repository URI:
# 123456789.dkr.ecr.us-east-1.amazonaws.com/my-app

# Authenticate Docker to ECR (token lasts 12 hours)
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS --password-stdin \
    123456789.dkr.ecr.us-east-1.amazonaws.com

# Build, tag, and push
docker build -t my-app .
docker tag my-app:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:latest
docker tag my-app:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:abc1234
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:abc1234
```

### 7.3 Lifecycle Policies

Automatically delete old images to control storage costs:

```json
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Keep last 10 tagged images",
      "selection": {
        "tagStatus": "tagged",
        "tagPrefixList": ["sha-"],
        "countType": "imageCountMoreThan",
        "countNumber": 10
      },
      "action": { "type": "expire" }
    },
    {
      "rulePriority": 2,
      "description": "Remove untagged images after 1 day",
      "selection": {
        "tagStatus": "untagged",
        "countType": "sinceImagePushed",
        "countUnit": "days",
        "countNumber": 1
      },
      "action": { "type": "expire" }
    }
  ]
}
```

### 7.4 ECR in GitHub Actions

```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789:role/github-actions-ecr
    aws-region: us-east-1

- name: Login to ECR
  id: login-ecr
  uses: aws-actions/amazon-ecr-login@v2

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    push: true
    tags: |
      ${{ steps.login-ecr.outputs.registry }}/my-app:latest
      ${{ steps.login-ecr.outputs.registry }}/my-app:${{ github.sha }}
```

---

## 8. ECS and Fargate — Container Orchestration

### 8.1 ECS Concepts

**ECS (Elastic Container Service)** — AWS's container orchestration service. You describe what containers to run and ECS runs them.

**Cluster** — a logical grouping of ECS resources. One cluster per environment (prod, staging).

**Task Definition** — a blueprint for your container. Defines the Docker image, CPU, memory, environment variables, ports, volumes, and IAM role. Versioned — each change creates a new revision.

**Task** — a running instance of a task definition. Like a Docker container running.

**Service** — maintains a desired number of running tasks. If a task dies, the service launches a replacement. Services integrate with load balancers.

**Fargate** — serverless compute for ECS. You don't provision or manage EC2 instances. Specify CPU and memory, Fargate handles the rest. Pay per vCPU-second and GB-second.

```
Cluster (prod)
  └── Service (my-app)
        ├── Task (running: my-app:abc1234, AZ: us-east-1a)
        ├── Task (running: my-app:abc1234, AZ: us-east-1b)
        └── Desired count: 2
```

### 8.2 Task Definition

```json
{
  "family": "my-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::123456789:role/ECSExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789:role/ECSTaskRole",
  "containerDefinitions": [
    {
      "name": "my-app",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:latest",
      "portMappings": [
        { "containerPort": 3000, "protocol": "tcp" }
      ],
      "environment": [
        { "name": "NODE_ENV", "value": "production" },
        { "name": "PORT", "value": "3000" }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:my-app/DATABASE_URL"
        },
        {
          "name": "JWT_SECRET",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:my-app/JWT_SECRET"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/my-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:3000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

### 8.3 IAM Roles for ECS

Two distinct roles:

**Execution Role** — used by ECS itself (not your app) to pull the Docker image from ECR and fetch secrets from Secrets Manager. Needs `AmazonECSTaskExecutionRolePolicy` plus permission to read secrets.

**Task Role** — used by your application code inside the container. Grants your app access to S3, SQS, DynamoDB, etc. This is the principle of least privilege applied to your app.

```json
// Execution Role — minimal
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "arn:aws:secretsmanager:*:*:secret:my-app/*"
    }
  ]
}
```

### 8.4 Creating a Service

```bash
# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create cluster
aws ecs create-cluster --cluster-name prod

# Create service
aws ecs create-service \
  --cluster prod \
  --service-name my-app \
  --task-definition my-app:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --platform-version LATEST \
  --network-configuration '{
    "awsvpcConfiguration": {
      "subnets": ["subnet-private-a", "subnet-private-b"],
      "securityGroups": ["sg-app"],
      "assignPublicIp": "DISABLED"
    }
  }' \
  --load-balancers '[{
    "targetGroupArn": "arn:aws:elasticloadbalancing:...:targetgroup/my-app/...",
    "containerName": "my-app",
    "containerPort": 3000
  }]' \
  --health-check-grace-period-seconds 60
```

### 8.5 Deploying New Images

```bash
# Force a new deployment (pulls latest image tag)
aws ecs update-service \
  --cluster prod \
  --service my-app \
  --force-new-deployment

# Deploy a specific task definition revision
aws ecs update-service \
  --cluster prod \
  --service my-app \
  --task-definition my-app:5

# ECS does rolling updates by default:
# Starts new tasks → health checks pass → stops old tasks
# No downtime
```

### 8.6 Auto Scaling for ECS Services

```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/prod/my-app \
  --min-capacity 1 \
  --max-capacity 10

# Scale on CPU utilisation
aws application-autoscaling put-scaling-policy \
  --policy-name cpu-scaling \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/prod/my-app \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleOutCooldown": 60,
    "ScaleInCooldown": 300
  }'
```

### 8.7 Fargate Pricing

```
CPU:    $0.04048 per vCPU per hour
Memory: $0.004445 per GB per hour

Example: 1 task with 0.5 vCPU, 1 GB RAM
  CPU:    0.5 × $0.04048 = $0.02024/hr
  Memory: 1.0 × $0.004445 = $0.004445/hr
  Total:  ~$0.025/hr = ~$18/month per task

2 tasks: ~$36/month
Add ALB: ~$18/month
RDS t3.micro: ~$13/month (after free tier)
Total for basic prod: ~$67/month
```

---

## 9. ALB — Application Load Balancer

### 9.1 What the ALB Does

The Application Load Balancer (ALB) operates at Layer 7 (HTTP/HTTPS). It:
- Accepts HTTPS traffic from the internet (SSL termination)
- Routes requests to healthy ECS tasks based on rules
- Performs health checks and stops routing to unhealthy tasks
- Supports path-based routing (`/api/*` → API service, `/admin/*` → admin service)
- Supports host-based routing (`api.domain.com` → API, `app.domain.com` → frontend)

### 9.2 ALB Components

**Load Balancer** — the main resource. Has a DNS name (e.g. `my-alb-123.us-east-1.elb.amazonaws.com`). Lives in public subnets.

**Listener** — watches for connections on a port. Typically:
- Port 80 (HTTP) → redirect to 443
- Port 443 (HTTPS) → forward to target group based on rules

**Target Group** — a set of targets (ECS tasks, EC2 instances, IPs) to route traffic to. The ALB health-checks each target.

**Rules** — conditions on a listener that determine which target group gets the request. Rules are evaluated in priority order.

### 9.3 Creating an ALB

```bash
# Create the load balancer
aws elbv2 create-load-balancer \
  --name my-app-alb \
  --type application \
  --subnets subnet-public-a subnet-public-b \
  --security-groups sg-alb \
  --scheme internet-facing

# Create target group
aws elbv2 create-target-group \
  --name my-app-targets \
  --protocol HTTP \
  --port 3000 \
  --vpc-id vpc-xxx \
  --target-type ip \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3

# Create HTTPS listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:...:loadbalancer/app/my-app-alb/... \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:... \
  --default-actions Type=forward,TargetGroupArn=arn:aws:...

# Create HTTP listener (redirect to HTTPS)
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:...:loadbalancer/app/my-app-alb/... \
  --protocol HTTP \
  --port 80 \
  --default-actions '[{
    "Type": "redirect",
    "RedirectConfig": {
      "Protocol": "HTTPS",
      "Port": "443",
      "StatusCode": "HTTP_301"
    }
  }]'
```

### 9.4 Path-Based Routing

```bash
# Route /api/* to API service, everything else to frontend
aws elbv2 create-rule \
  --listener-arn arn:aws:... \
  --priority 10 \
  --conditions '[{
    "Field": "path-pattern",
    "Values": ["/api/*"]
  }]' \
  --actions '[{
    "Type": "forward",
    "TargetGroupArn": "arn:aws:...:targetgroup/api-service/..."
  }]'
```

### 9.5 ALB Access Logs

Enable access logs to S3 for debugging and analytics:

```bash
aws elbv2 modify-load-balancer-attributes \
  --load-balancer-arn arn:aws:... \
  --attributes Key=access_logs.s3.enabled,Value=true \
               Key=access_logs.s3.bucket,Value=my-alb-logs \
               Key=access_logs.s3.prefix,Value=my-app
```

---

## 10. CloudWatch — Observability

### 10.1 What CloudWatch Covers

CloudWatch is AWS's observability service:
- **Logs** — collect and search log output from any service
- **Metrics** — numeric time-series data (CPU, memory, request count, error rate)
- **Alarms** — trigger actions when metrics cross thresholds
- **Dashboards** — visualise metrics
- **Events/EventBridge** — trigger actions on scheduled or event-based triggers

### 10.2 Log Groups and Streams

**Log group** — a container for log streams from the same source. `/ecs/my-app` is a common pattern.

**Log stream** — a sequence of log events from a single source. ECS creates one per task: `/ecs/my-app/ecs/my-app/task-id`.

```bash
# Create log group
aws logs create-log-group \
  --log-group-name /ecs/my-app

# Set retention (90 days)
aws logs put-retention-policy \
  --log-group-name /ecs/my-app \
  --retention-in-days 90

# Tail logs in real-time (like tail -f)
aws logs tail /ecs/my-app --follow

# Filter logs
aws logs filter-log-events \
  --log-group-name /ecs/my-app \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s000)

# Insights query (SQL-like log analysis)
aws logs start-query \
  --log-group-name /ecs/my-app \
  --start-time $(date -d '24 hours ago' +%s) \
  --end-time $(date +%s) \
  --query-string '
    fields @timestamp, @message
    | filter @message like /ERROR/
    | stats count() by bin(5m)
    | sort @timestamp desc
  '
```

### 10.3 Custom Metrics

Push custom application metrics to CloudWatch:

```typescript
// Node.js — publish custom metric
import { CloudWatchClient, PutMetricDataCommand } from '@aws-sdk/client-cloudwatch';

const cloudwatch = new CloudWatchClient({ region: 'us-east-1' });

await cloudwatch.send(new PutMetricDataCommand({
  Namespace: 'MyApp',
  MetricData: [
    {
      MetricName: 'OrdersProcessed',
      Value: 1,
      Unit: 'Count',
      Dimensions: [
        { Name: 'Environment', Value: 'production' },
        { Name: 'Service', Value: 'order-service' }
      ]
    },
    {
      MetricName: 'PaymentProcessingTime',
      Value: 245,
      Unit: 'Milliseconds'
    }
  ]
}));
```

### 10.4 Alarms

```bash
# Alarm on high CPU (> 80% for 2 consecutive 5-minute periods)
aws cloudwatch put-metric-alarm \
  --alarm-name high-cpu \
  --alarm-description "ECS CPU over 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --dimensions Name=ClusterName,Value=prod Name=ServiceName,Value=my-app \
  --period 300 \
  --evaluation-periods 2 \
  --statistic Average \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:123456789:alerts \
  --ok-actions arn:aws:sns:us-east-1:123456789:alerts

# Alarm on 5xx error rate (> 1% for 1 minute)
aws cloudwatch put-metric-alarm \
  --alarm-name high-5xx-rate \
  --metric-name HTTPCode_Target_5XX_Count \
  --namespace AWS/ApplicationELB \
  --dimensions Name=LoadBalancer,Value=app/my-app-alb/xxx \
  --period 60 \
  --evaluation-periods 1 \
  --statistic Sum \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:123456789:alerts
```

### 10.5 SNS for Alert Notifications

```bash
# Create SNS topic
aws sns create-topic --name alerts

# Subscribe email
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789:alerts \
  --protocol email \
  --notification-endpoint your-email@example.com

# Subscribe Slack via Lambda or use a Slack integration service
```

### 10.6 CloudWatch Logs Insights Queries

```
# Most common errors in last 24 hours
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() as error_count by @message
| sort error_count desc
| limit 20

# Average response time by endpoint
fields @timestamp, path, duration
| stats avg(duration) as avg_ms, count() as requests by path
| sort avg_ms desc

# P99 latency per minute
fields @timestamp, duration
| stats pct(duration, 99) as p99_ms by bin(1m)
| sort @timestamp asc
```

### 10.7 Container Insights

Enables detailed metrics for ECS tasks (CPU, memory, network per task):

```bash
aws ecs update-cluster-settings \
  --cluster prod \
  --settings name=containerInsights,value=enabled
```

---

## 11. Route 53 — DNS

### 11.1 What Route 53 Does

Route 53 is AWS's DNS service. It translates domain names to IP addresses, routes traffic based on health and geography, and manages domain registration.

Route 53 is a global service (not region-specific). It uses anycast — DNS queries go to the nearest Route 53 edge location. Response times are typically < 1ms.

### 11.2 Hosted Zones

A **hosted zone** is a container for DNS records for a domain. When you register a domain in Route 53, a public hosted zone is created automatically.

```bash
# Create hosted zone for your domain
aws route53 create-hosted-zone \
  --name yourdomain.com \
  --caller-reference $(date +%s)

# List hosted zones
aws route53 list-hosted-zones

# Public hosted zone: serves DNS for internet clients
# Private hosted zone: serves DNS only within your VPC (for internal service discovery)
```

### 11.3 Record Types in Practice

```bash
# A record: domain → ALB IP address
# Use ALIAS record for AWS resources (free, updates automatically when ALB IP changes)
aws route53 change-resource-record-sets \
  --hosted-zone-id ZXXXXXXXXXX \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.yourdomain.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z35SXDOTRQ7X7K",
          "DNSName": "my-app-alb-123.us-east-1.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }'

# CNAME: subdomain → another hostname
# Cannot use CNAME at the root domain (use ALIAS instead)

# MX record: for email
# TXT record: for domain verification, SPF, DKIM
```

### 11.4 ALIAS vs CNAME

**CNAME** — maps a hostname to another hostname. Works for subdomains. Costs money per query. Cannot point to the root domain apex.

**ALIAS** — AWS-specific extension. Maps a hostname to an AWS resource (ALB, CloudFront, S3 website endpoint). Free for queries to AWS resources. Works at the root domain. Updates automatically when the AWS resource's IP changes. Always prefer ALIAS over CNAME for AWS resources.

### 11.5 Routing Policies

| Policy | How it works | Use for |
|---|---|---|
| Simple | Single record, one or more IPs | Single resource |
| Weighted | Split traffic by percentage | A/B testing, gradual migration |
| Latency | Route to region with lowest latency | Multi-region apps |
| Failover | Primary + failover record | Active-passive HA |
| Geolocation | Route based on user's country/continent | Compliance, localisation |
| Geoproximity | Route based on geographic bias | Gradually shift traffic between regions |
| Multi-value | Return up to 8 healthy IPs | Client-side load balancing |

```bash
# Weighted routing: 90% to v1, 10% to v2 (canary deployment)
aws route53 change-resource-record-sets --hosted-zone-id ZXXX \
  --change-batch '{
    "Changes": [
      {
        "Action": "UPSERT",
        "ResourceRecordSet": {
          "Name": "api.yourdomain.com",
          "Type": "A",
          "SetIdentifier": "v1-90pct",
          "Weight": 90,
          "AliasTarget": { "DNSName": "alb-v1.us-east-1.elb.amazonaws.com", ... }
        }
      },
      {
        "Action": "UPSERT",
        "ResourceRecordSet": {
          "Name": "api.yourdomain.com",
          "Type": "A",
          "SetIdentifier": "v2-10pct",
          "Weight": 10,
          "AliasTarget": { "DNSName": "alb-v2.us-east-1.elb.amazonaws.com", ... }
        }
      }
    ]
  }'
```

### 11.6 Health Checks

Route 53 health checks monitor endpoints and automatically stop routing to unhealthy ones. Used with failover routing.

```bash
aws route53 create-health-check \
  --caller-reference $(date +%s) \
  --health-check-config '{
    "IPAddress": "203.0.113.42",
    "Port": 443,
    "Type": "HTTPS",
    "ResourcePath": "/health",
    "FullyQualifiedDomainName": "api.yourdomain.com",
    "RequestInterval": 30,
    "FailureThreshold": 3
  }'
```

---

## 12. ACM — Certificate Manager

### 12.1 What ACM Does

ACM (AWS Certificate Manager) provisions and manages SSL/TLS certificates. Certificates from ACM are **free** and auto-renew. They can only be used with AWS services (ALB, CloudFront, API Gateway) — you can't download the private key for use elsewhere.

For custom servers (EC2 running Nginx), use Let's Encrypt instead.

### 12.2 Requesting a Certificate

```bash
# Request a certificate (DNS validation recommended)
aws acm request-certificate \
  --domain-name yourdomain.com \
  --subject-alternative-names "*.yourdomain.com" \
  --validation-method DNS \
  --region us-east-1  # ALB certificates must be in same region as ALB

# For CloudFront, certificates must be in us-east-1 regardless of CloudFront region
aws acm request-certificate \
  --domain-name yourdomain.com \
  --subject-alternative-names "*.yourdomain.com" \
  --validation-method DNS \
  --region us-east-1

# Get the CNAME record needed for DNS validation
aws acm describe-certificate \
  --certificate-arn arn:aws:acm:...
# Add the CNAME record to Route 53 (or manually to your DNS provider)
# ACM validates automatically once the record exists
# Certificate is issued within minutes
```

### 12.3 Wildcard Certificates

A wildcard certificate (`*.yourdomain.com`) covers all first-level subdomains: `api.yourdomain.com`, `app.yourdomain.com`, `staging.yourdomain.com`. It does **not** cover the root domain (`yourdomain.com`) or second-level subdomains (`api.staging.yourdomain.com`).

Request both `yourdomain.com` and `*.yourdomain.com` in one certificate as Subject Alternative Names (SANs) to cover everything.

---

## 13. ElastiCache — Managed Redis

### 13.1 Why ElastiCache Instead of Self-Managed Redis

ElastiCache (Redis) handles patching, failover, backups, and scaling. Like RDS but for Redis.

```bash
# Create a Redis cluster (single-node for dev, replication group for prod)
aws elasticache create-replication-group \
  --replication-group-id my-app-redis \
  --replication-group-description "My app Redis" \
  --num-cache-clusters 2 \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --engine-version 7.0 \
  --cache-subnet-group-name my-redis-subnet-group \
  --security-group-ids sg-redis \
  --at-rest-encryption-enabled \
  --transit-encryption-enabled

# Connection endpoint (primary):
# my-app-redis.xxxxx.0001.use1.cache.amazonaws.com:6379
```

**ElastiCache modes:**
- **Cluster mode disabled** — one primary, up to 5 read replicas. Simple. Scales reads not writes.
- **Cluster mode enabled** — data sharded across up to 500 nodes. Scales reads and writes. More complex.

For most applications: cluster mode disabled with one primary and one replica.

---

## 14. Secrets Manager and Parameter Store

### 14.1 The Problem

Your application needs database passwords, API keys, and JWT secrets. These must not be:
- Hardcoded in source code (version controlled = exposed)
- In environment variables baked into Docker images (visible in ECR)
- In plain text anywhere

### 14.2 Secrets Manager

For sensitive secrets that need automatic rotation:

```bash
# Store a secret
aws secretsmanager create-secret \
  --name my-app/prod/DATABASE_URL \
  --description "Production PostgreSQL connection string" \
  --secret-string "postgresql://user:pass@host:5432/db"

# Store a JSON object (multiple values in one secret)
aws secretsmanager create-secret \
  --name my-app/prod \
  --secret-string '{
    "DATABASE_URL": "postgresql://...",
    "JWT_SECRET": "very-long-random-string",
    "REDIS_URL": "redis://..."
  }'

# Retrieve a secret
aws secretsmanager get-secret-value \
  --secret-id my-app/prod/DATABASE_URL \
  --query SecretString --output text

# Update a secret
aws secretsmanager put-secret-value \
  --secret-id my-app/prod/DATABASE_URL \
  --secret-string "postgresql://newuser:newpass@newhost:5432/db"
```

In your ECS task definition, reference secrets by ARN (see Section 8.2). ECS fetches them at task launch and injects them as environment variables. Your app code just reads `process.env.DATABASE_URL` normally.

### 14.3 Parameter Store

For non-sensitive configuration values (feature flags, app config). Cheaper than Secrets Manager.

```bash
# Standard parameter (free)
aws ssm put-parameter \
  --name "/my-app/prod/MAX_UPLOAD_SIZE" \
  --value "10485760" \
  --type String

# SecureString (encrypted with KMS, cheap alternative to Secrets Manager)
aws ssm put-parameter \
  --name "/my-app/prod/API_KEY" \
  --value "sk-abc123" \
  --type SecureString

# Get parameter
aws ssm get-parameter \
  --name "/my-app/prod/MAX_UPLOAD_SIZE" \
  --query Parameter.Value --output text

# Get SecureString (with decryption)
aws ssm get-parameter \
  --name "/my-app/prod/API_KEY" \
  --with-decryption \
  --query Parameter.Value --output text
```

**Secrets Manager vs Parameter Store:**
- Secrets Manager: automatic rotation, cross-account sharing, $0.40/secret/month
- Parameter Store Standard: free, no rotation, simpler
- Parameter Store Advanced: $0.05/parameter/month, larger size, higher throughput

For secrets: Secrets Manager. For config: Parameter Store Standard.

---

## 15. How Traffic Flows — Browser to App and Back

This is the full request lifecycle for a production NestJS API on AWS.

### 15.1 DNS Resolution

```
1. User types api.yourdomain.com in their browser.
2. Browser checks local DNS cache → not found.
3. OS asks router/ISP DNS resolver → not found.
4. Resolver queries Route 53 (authoritative nameserver for yourdomain.com).
5. Route 53 returns the ALB's DNS name (ALIAS record).
6. Resolver resolves ALB DNS to an IP address.
7. Browser gets the IP. DNS response cached per TTL (60 seconds for ALB records).
```

### 15.2 TLS Handshake

```
8.  Browser opens TCP connection to ALB IP on port 443.
9.  TLS handshake begins:
    - Browser sends ClientHello (supported TLS versions and cipher suites)
    - ALB sends its SSL certificate (from ACM) and ServerHello
    - Browser verifies certificate is signed by a trusted CA (ACM uses Amazon CA)
    - Browser and ALB agree on a session key using asymmetric encryption
    - All subsequent communication encrypted with that session key (symmetric)
10. HTTPS connection established. ~50–200ms for this entire process.
```

### 15.3 ALB Routing

```
11. HTTP request arrives at ALB listener on port 443.
12. ALB evaluates routing rules:
    - Path: /api/* → forwards to API target group
    - Default: forward to frontend target group
13. ALB picks a healthy target (ECS task IP) using its algorithm (round robin).
14. ALB forwards request to chosen task on port 3000.
    - Adds X-Forwarded-For: {client IP} header
    - Adds X-Forwarded-Proto: https header
    (Your app sees the ALB's internal IP as the source, not the client's IP)
```

### 15.4 Application Processing

```
15. NestJS receives request.
16. Request passes through middleware:
    - Rate limiter (checks Redis counter)
    - JWT validation guard (decodes and verifies JWT)
    - Request logging (logs to stdout → CloudWatch)
17. Router dispatches to correct controller.
18. Controller calls service.
19. Service reads from Redis cache → cache hit → return
                                 → cache miss →
    Service queries PostgreSQL RDS (private subnet, encrypted connection).
    Response cached in Redis with TTL.
20. Service returns data → controller → NestJS serialises to JSON.
21. Response: 200 OK with JSON body.
```

### 15.5 Response Journey Back

```
22. NestJS sends HTTP response back to ALB.
23. ALB updates target health metrics (status code, response time).
24. ALB forwards response to browser (already has the TCP connection open).
25. Browser receives response body (JSON).
26. Application code processes the response, updates UI.

Logging:
  - ALB logs request to S3 (if enabled)
  - ECS task logs stdout → CloudWatch Logs /ecs/my-app
  - CloudWatch metrics update: request count, latency, 2xx/5xx counts

Total round-trip for a cache hit: ~50ms (most is TLS + network)
Total round-trip for a DB query: ~100–200ms
```

### 15.6 Diagram

```
[Browser]
    │
    │ DNS query: api.yourdomain.com
    ▼
[Route 53] ──────────────────────────────────► ALIAS to ALB DNS
    │
    │ ALB IP address
    ▼
[CloudFront] (optional, for API caching or DDoS protection)
    │
    │ HTTPS :443
    ▼
[Internet Gateway] (entry into VPC)
    │
    │ TCP to ALB in public subnet
    ▼
[ALB] ─── ACM certificate (TLS termination)
  │   └── Security Group: allow :443 from 0.0.0.0/0
  │
  │ HTTP :3000 to task IP
  ▼
[ECS Fargate Task] ── Security Group: allow :3000 from ALB SG only
  │    [NestJS App]
  │         │
  │    ┌────┼──────────────────────┐
  │    │    │                      │
  │    ▼    ▼                      ▼
  │ [Redis]  [PostgreSQL RDS]    [S3 via VPC Endpoint]
  │ (private subnet)  (private subnet)
  │
  └──── Logs ──────────────────► [CloudWatch Logs]
  └──── Metrics ───────────────► [CloudWatch Metrics]
  └──── Secrets on boot ───────  [Secrets Manager]
```

---

## 16. Production Architecture on AWS

### 16.1 The Complete Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  INTERNET                                                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    [Route 53 DNS]
                           │
              ┌────────────┴────────────┐
              │                         │
        [CloudFront]              [CloudFront]
        (API + Cache)            (Static Assets)
              │                         │
              └────────────┬────────────┘
                           │
┌─────────────────────────────────────────────────────────────────┐
│  VPC: 10.0.0.0/16                                               │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  PUBLIC SUBNETS (10.0.1.0/24, 10.0.2.0/24)              │   │
│  │  AZ: us-east-1a              AZ: us-east-1b              │   │
│  │                                                           │   │
│  │  [Internet Gateway] ←────────────────────────────────┐   │   │
│  │  [NAT Gateway A]             [NAT Gateway B]          │   │   │
│  │  [ALB] ─────────────────────────────────────────────┐ │   │   │
│  └──────────────────────────────────────────────────── │ ┘   │   │
│                                                         │     │   │
│  ┌──────────────────────────────────────────────────── │ ──┐ │   │
│  │  PRIVATE SUBNETS (10.0.11.0/24, 10.0.12.0/24)      │   │ │   │
│  │                                                      │   │ │   │
│  │  [ECS Task] [ECS Task]  ←───────────────────────────┘   │ │   │
│  │  NestJS API  NestJS API                                  │ │   │
│  │       │            │                                     │ │   │
│  │       └─────┬──────┘                                     │ │   │
│  │             │                                            │ │   │
│  │    ┌────────┼────────┐                                   │ │   │
│  │    ▼        ▼        ▼                                   │ │   │
│  │ [Redis]  [RDS Pri] [RDS Replica]                        │ │   │
│  │ [Cache]  (writes)  (reads)                              │ │   │
│  │                                                          │ │   │
│  └──────────────────────────────────────────────────────── ┘ │   │
│                                                               │   │
│  ┌────────────────────────────────────────────────────────── │ ─┐ │
│  │  AWS SERVICES (via VPC Endpoints or private network)      │   │ │
│  │  [S3 Bucket] [Secrets Manager] [ECR] [CloudWatch]       │   │ │
│  └──────────────────────────────────────────────────────────│ ──┘ │
└──────────────────────────────────────────────────────────────│ ───┘
                                                               │
                                                    [Internet: S3, external APIs]
```

### 16.2 Security Layers

```
Layer 1: CloudFront WAF rules (DDoS, rate limiting at edge)
Layer 2: ALB Security Group (allow :443 from internet only)
Layer 3: App Security Group (allow :3000 from ALB SG only)
Layer 4: RDS Security Group (allow :5432 from App SG only)
Layer 5: Redis Security Group (allow :6379 from App SG only)
Layer 6: IAM Task Role (app can only access specific S3 and secrets)
Layer 7: VPC Subnet isolation (RDS in private subnet — no public IP)
Layer 8: Encryption in transit (TLS everywhere)
Layer 9: Encryption at rest (RDS, ElastiCache, S3, Secrets Manager all encrypted)
```

### 16.3 CI/CD Pipeline to AWS

```
Developer pushes to main branch
    │
    ▼
GitHub Actions:
  1. Run tests
  2. docker build
  3. Push to ECR (tagged with git SHA)
  4. Update ECS task definition with new image
  5. Deploy ECS service (rolling update)
  6. Health check new tasks
  7. Notify Slack on success/failure

ECS Rolling Update:
  - ECS starts new task with new image
  - Waits for health check to pass (GET /health → 200)
  - Removes old task
  - Repeats for each task
  → Zero downtime
```

### 16.4 Terraform for Infrastructure as Code

Managing all of this manually via CLI is error-prone. Use Terraform:

```hcl
# main.tf — VPC
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "prod-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.11.0/24", "10.0.12.0/24"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = false   # true for cost savings in dev
}

# RDS
resource "aws_db_instance" "postgres" {
  identifier           = "myapp-prod"
  engine               = "postgres"
  engine_version       = "16.1"
  instance_class       = "db.t3.medium"
  allocated_storage    = 20
  storage_encrypted    = true
  username             = "appuser"
  password             = data.aws_secretsmanager_secret_version.db_password.secret_string
  db_subnet_group_name = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  multi_az             = true
  backup_retention_period = 7
  skip_final_snapshot  = false
}

# ECS Service
resource "aws_ecs_service" "app" {
  name            = "my-app"
  cluster         = aws_ecs_cluster.prod.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [aws_security_group.app.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "my-app"
    container_port   = 3000
  }
}
```

---

## 17. Free Tier — What You Get and How to Stay In It

### 17.1 Free Tier Types

**Always free** — no expiry, available forever.
**12 months free** — free for 12 months from account creation date.
**Free trials** — short trials of specific services.

### 17.2 The Key Free Tier Allocations

| Service | Free Tier | Watch out for |
|---|---|---|
| EC2 | 750 hours/month t2.micro or t3.micro (12 months) | Any other instance type costs immediately |
| RDS | 750 hours/month db.t2.micro or db.t3.micro (12 months) | Multi-AZ costs double |
| S3 | 5 GB storage, 20K GET, 2K PUT (12 months) | Data transfer OUT costs |
| Lambda | 1M requests/month, 400K GB-seconds (always free) | |
| CloudFront | 1 TB transfer out, 10M HTTP requests (always free) | |
| CloudWatch | 10 custom metrics, 5 GB logs (always free) | Logs ingestion costs after 5GB |
| ECR | 500 MB/month (always free) | Exceeding costs $0.10/GB |
| Data Transfer OUT | 100 GB/month (always free, first 12 months) | After free tier: $0.09/GB |
| Route 53 | $0.50/hosted zone/month — NOT free | |
| NAT Gateway | NOT free — $0.045/hr + $0.045/GB | Use sparingly in dev |
| ALB | NOT free — $0.008/hr + LCU charges | |
| Secrets Manager | $0.40/secret/month, $0.05/10K API calls — NOT free | |
| ECS/Fargate | NOT free — you pay for vCPU and memory used | Fargate is more expensive than EC2 |

### 17.3 How to Stay in Free Tier

**Set up billing alerts immediately:**
```bash
# Create a billing alarm (must be in us-east-1 for billing metrics)
aws cloudwatch put-metric-alarm \
  --region us-east-1 \
  --alarm-name billing-alert-10 \
  --alarm-description "Alert when bill exceeds $10" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --dimensions Name=Currency,Value=USD \
  --period 86400 \
  --evaluation-periods 1 \
  --statistic Maximum \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:xxx:billing-alerts

# Enable billing alerts in account settings first:
# Console → Billing → Billing Preferences → Receive Billing Alerts → Save
```

**Dev environment cost-saving strategies:**
```
1. Stop RDS when not in use (stop via Console → saves ~$0.02/hr)
   (RDS auto-starts after 7 days — schedule a Lambda to stop it daily)

2. Use t3.micro for RDS — smallest free-tier eligible

3. Avoid NAT Gateway in dev — put ECS tasks in public subnets temporarily
   (never do this in production)

4. Use S3 for static sites instead of EC2/ECS

5. Use Lambda for low-traffic APIs — stays in always-free tier

6. One NAT Gateway not two (saves ~$32/month vs high-availability setup)

7. Delete unused resources — idle load balancers, unused EBS volumes, old snapshots

8. Check the Cost Explorer weekly
   Console → Billing → Cost Explorer → View by service
```

### 17.4 Cost Monitoring Commands

```bash
# See current month's charges by service
aws ce get-cost-and-usage \
  --time-period Start=2026-01-01,End=2026-01-31 \
  --granularity MONTHLY \
  --metrics "UnblendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE

# See daily spend
aws ce get-cost-and-usage \
  --time-period Start=2026-01-01,End=2026-01-31 \
  --granularity DAILY \
  --metrics "UnblendedCost"
```

---

## 18. AWS CLI and SDK

### 18.1 CLI Setup

```bash
# Install (Ubuntu/Debian)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./aws/install

# Install (macOS)
brew install awscli

# Configure
aws configure
# AWS Access Key ID: (from IAM user)
# AWS Secret Access Key: (from IAM user)
# Default region: us-east-1
# Default output format: json (or table or text)

# Multiple profiles
aws configure --profile staging
aws configure --profile prod

# Use a profile
aws s3 ls --profile prod
export AWS_PROFILE=prod  # set for current shell session
```

### 18.2 Useful CLI Patterns

```bash
# Output as table (human-readable)
aws ec2 describe-instances --output table

# Filter output with JMESPath query
aws ec2 describe-instances \
  --query 'Reservations[*].Instances[*].{ID:InstanceId,State:State.Name,IP:PublicIpAddress}' \
  --output table

# Wait for a resource to be ready
aws rds wait db-instance-available --db-instance-identifier myapp-prod

# Use environment variables for credentials (in CI/CD)
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx
export AWS_DEFAULT_REGION=us-east-1

# Get caller identity (verify which account and role you're using)
aws sts get-caller-identity
```

### 18.3 Node.js SDK v3

```typescript
// Install
// npm install @aws-sdk/client-s3 @aws-sdk/client-rds @aws-sdk/client-ecs

// S3 — upload a file
import { S3Client, PutObjectCommand, GetObjectCommand } from '@aws-sdk/client-s3';

const s3 = new S3Client({ region: process.env.AWS_REGION || 'us-east-1' });
// SDK automatically uses IAM role credentials when running on ECS/EC2

await s3.send(new PutObjectCommand({
  Bucket: 'my-app-uploads',
  Key: 'uploads/photo.jpg',
  Body: fileBuffer,
  ContentType: 'image/jpeg',
}));

// Secrets Manager — retrieve a secret
import { SecretsManagerClient, GetSecretValueCommand } from '@aws-sdk/client-secrets-manager';

const sm = new SecretsManagerClient({ region: 'us-east-1' });
const { SecretString } = await sm.send(new GetSecretValueCommand({
  SecretId: 'my-app/prod',
}));
const secrets = JSON.parse(SecretString!);
// secrets.DATABASE_URL, secrets.JWT_SECRET, etc.

// SQS — send a message to a queue
import { SQSClient, SendMessageCommand } from '@aws-sdk/client-sqs';

const sqs = new SQSClient({ region: 'us-east-1' });
await sqs.send(new SendMessageCommand({
  QueueUrl: 'https://sqs.us-east-1.amazonaws.com/123456789/my-queue',
  MessageBody: JSON.stringify({ userId: '42', action: 'send-welcome-email' }),
  MessageGroupId: 'email',  // for FIFO queues
}));
```

### 18.4 Java SDK v2

```java
// Maven dependency
// <dependency>
//   <groupId>software.amazon.awssdk</groupId>
//   <artifactId>s3</artifactId>
//   <version>2.25.0</version>
// </dependency>

import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;

// DefaultCredentialsProvider uses: env vars → system props → AWS config → IAM role
S3Client s3 = S3Client.builder()
    .region(Region.US_EAST_1)
    .credentialsProvider(DefaultCredentialsProvider.create())
    .build();

s3.putObject(
    PutObjectRequest.builder()
        .bucket("my-app-uploads")
        .key("uploads/photo.jpg")
        .contentType("image/jpeg")
        .build(),
    RequestBody.fromBytes(fileBytes)
);

// Secrets Manager
import software.amazon.awssdk.services.secretsmanager.SecretsManagerClient;
import software.amazon.awssdk.services.secretsmanager.model.GetSecretValueRequest;

SecretsManagerClient sm = SecretsManagerClient.builder()
    .region(Region.US_EAST_1)
    .build();

String secretString = sm.getSecretValue(
    GetSecretValueRequest.builder().secretId("my-app/prod").build()
).secretString();
```

---

## 19. Cost Optimisation

### 19.1 Right-Sizing

Start small and scale up when you have data. Most applications over-provision.

```
Development: t3.micro RDS, 1 Fargate task (0.25 vCPU, 512 MB)
Staging:     t3.small RDS, 1 Fargate task (0.5 vCPU, 1 GB)
Production:  t3.medium RDS, 2+ Fargate tasks (1 vCPU, 2 GB each)
```

Use CloudWatch metrics to see actual CPU and memory usage. If consistently < 40%, downsize.

### 19.2 Savings Plans and Reserved Instances

After 3–6 months of stable usage:
- **Compute Savings Plans** — commit to $X/hour of compute for 1 or 3 years. Works for EC2, Fargate, Lambda. 20–50% savings.
- **RDS Reserved Instances** — commit to a specific instance type for 1 or 3 years. 30–60% savings.

Don't purchase before you have 3 months of usage data showing stable patterns.

### 19.3 Use Graviton (ARM) Everywhere You Can

Graviton3 instances (suffix `g`) are 20–40% cheaper and faster than x86 equivalents. Switch to ARM:
- RDS: `db.t4g.micro` instead of `db.t3.micro`
- ElastiCache: `cache.t4g.micro`
- Fargate: add `"cpuArchitecture": "ARM64"` to task definition runtime platform
- Requires your Docker images to be built for `linux/arm64`

### 19.4 S3 Intelligent-Tiering

Enable Intelligent-Tiering on buckets where access patterns are unpredictable. AWS automatically moves objects between tiers based on access frequency. No retrieval fees.

### 19.5 Delete Unused Resources

Common sources of surprise bills:
- Idle Elastic IPs ($0.005/hr when not attached)
- Unused EBS volumes ($0.08/GB/month)
- Old EBS snapshots ($0.05/GB/month)
- Unused load balancers ($0.008/hr)
- Old ECR images (check lifecycle policies)

```bash
# Find unused Elastic IPs
aws ec2 describe-addresses \
  --query 'Addresses[?AssociationId==null].[AllocationId,PublicIp]' \
  --output table

# Find unattached EBS volumes
aws ec2 describe-volumes \
  --filters Name=status,Values=available \
  --query 'Volumes[*].[VolumeId,Size,CreateTime]' \
  --output table
```

---

## 20. Security Hardening Checklist

### Production AWS Account

```
IAM:
☑ MFA enabled on root account
☑ Root account has no access keys
☑ All human users have MFA
☑ No user has AdministratorAccess except admins
☑ IAM Access Analyzer enabled
☑ Service roles use least privilege custom policies
☑ No long-lived credentials in application code

Networking:
☑ All application servers in private subnets
☑ Databases in private subnets, no public access
☑ Security groups follow least-privilege
☑ VPC Flow Logs enabled (detect unusual traffic)
☑ No broad 0.0.0.0/0 inbound rules except on ALB for :443

Data:
☑ RDS encryption at rest enabled
☑ S3 public access block enabled on all buckets
☑ S3 server-side encryption enabled
☑ Secrets in Secrets Manager, not env vars baked into images
☑ EBS volumes encrypted
☑ ElastiCache transit and at-rest encryption enabled

Monitoring:
☑ CloudTrail enabled (logs all API calls to your account)
☑ CloudWatch alarms for high CPU, error rate, unusual spend
☑ Billing alarm set up
☑ GuardDuty enabled (ML-based threat detection, $3/month)

Application:
☑ ALB access logs enabled
☑ CloudWatch log groups with retention policies
☑ Health check endpoint returns 200 only when truly healthy
☑ HTTPS everywhere — no HTTP endpoints in production
☑ ACM certificate auto-renewal (happens automatically for Route 53 validated certs)
```

### Enabling CloudTrail

```bash
# CloudTrail logs every API call made in your account
# Essential for security auditing and incident response
aws cloudtrail create-trail \
  --name my-account-trail \
  --s3-bucket-name my-cloudtrail-logs \
  --is-multi-region-trail \
  --enable-log-file-validation

aws cloudtrail start-logging --name my-account-trail
```

### Enabling GuardDuty

```bash
# Threat detection using ML — finds unusual API calls, crypto mining, data exfiltration
aws guardduty create-detector --enable --finding-publishing-frequency SIX_HOURS
# ~$3/month for a small account — worth it
```

---

*Last updated: 2026 — Built from AWS architecture experience and the AWS Well-Architected Framework.*
