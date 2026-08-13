# 03 — Cloud

Cloud provider fundamentals: the landscape of providers, the core service categories every one of them offers, the serverless model, and how the whole thing is billed and secured. Part of the [[devops/README|DevOps curriculum]].

The AWS-specific deep reference predates this pass; the fundamentals and serverless notes were added to give the section provider-agnostic grounding before the AWS specifics.

## Reading order

1. [[devops/03-cloud/01-cloud-fundamentals|Cloud Fundamentals]] — **[Beginner → Intermediate]** — what "the cloud" is, the AWS/Azure/GCP landscape, the core service categories (compute, storage, network, database), the shared-responsibility model, and how billing works
2. [[devops/03-cloud/02-serverless|Serverless]] — **[Intermediate]** — FaaS (Lambda, Azure/GCP Functions), managed containers, and when serverless is and isn't the right call
3. [[devops/03-cloud/03-object-storage-and-direct-uploads|Object Storage & Direct Uploads]] — **[Intermediate]** — S3-compatible storage, presigned browser uploads, CORS vs public access, and why egress drives the provider choice
4. [[devops/03-cloud/aws-cloud-reference|AWS Reference]] — **[Intermediate]** — the existing AWS-specific deep reference (EC2, S3, IAM, VPC, and friends)

## Related
- [[devops/05-orchestration/README|Orchestration]] — managed Kubernetes runs on these providers
- [[devops/11-delivery-and-advanced/04-cloud-design-patterns|Cloud Design Patterns]] — architecting *on* the cloud for resilience and scale
- [[devops/README|DevOps curriculum map]]
