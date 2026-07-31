# Provisioning & Terraform

**[reference]** — from roadmap.sh and the Terraform docs. Not yet run against a real cloud account; the honest next step is a `terraform apply` on a throwaway account.

## Infrastructure as Code — the idea

**IaC** means defining your infrastructure (servers, networks, databases, DNS, load balancers) in version-controlled code instead of clicking through a cloud console. The payoff:

- **Reproducible** — the same code builds an identical environment every time, so staging really matches prod.
- **Versioned & reviewed** — infrastructure changes go through git and code review like application code; you can see who changed what and roll back.
- **Documented** — the code *is* the documentation of what exists; no drift between a wiki and reality.
- **No "click-ops"** — the console is for looking, not for making changes that no one can reproduce.

The mental shift is from **imperative** ("run these steps to create a server") to **declarative** ("I want a server that looks like this") — you describe the desired end state and the tool figures out the changes to get there.

## Two disciplines: provisioning vs configuration

IaC splits into two related jobs, and conflating them causes confusion:

- **Provisioning** — *creating* the infrastructure itself: the VM, the network, the load balancer, the managed database. **Terraform**, Pulumi, CloudFormation.
- **Configuration management** — *setting up what runs on* already-existing machines: installing packages, writing config files, starting services. **Ansible**, Chef, Puppet ([[devops/07-infrastructure-as-code/02-configuration-management|next note]]).

A common pattern: Terraform provisions the servers, then Ansible configures them. (Immutable-infrastructure shops skip config management entirely — they bake a machine image and provision from it, replacing rather than mutating.)

## Terraform

Terraform is the de-facto provisioning standard. You write **HCL** (HashiCorp Configuration Language) describing resources; Terraform figures out how to create/change/destroy them via each provider's API.

```hcl
provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "web" {          # declare a VM
  ami           = "ami-0abcd1234"
  instance_type = "t3.micro"
  tags = { Name = "web-server" }
}

resource "aws_s3_bucket" "assets" {      # declare a bucket
  bucket = "myapp-assets"
}
```

The core workflow — three commands that encode Terraform's whole model:

```bash
terraform init      # download provider plugins
terraform plan      # show exactly what will change BEFORE doing it — the safety feature
terraform apply     # make reality match the code
terraform destroy   # tear it all down
```

### The three concepts that define Terraform

- **State** — Terraform records what it created in a **state file** (`terraform.tfstate`), mapping your code to real resource IDs. This is how it knows what already exists and what to change. State is critical and dangerous: it must be stored **remotely and locked** (e.g. an S3 bucket + DynamoDB lock) so a team doesn't corrupt it with concurrent applies, and it can contain secrets, so it must be secured. Mismanaged state is the #1 source of Terraform pain.
- **Plan before apply** — `terraform plan` shows the exact diff (what will be created/changed/**destroyed**) before you commit. Reading the plan — especially spotting an unintended *destroy* — is the discipline that prevents catastrophes.
- **Declarative + idempotent** — apply the same config twice and the second run is a no-op; Terraform only changes what drifted from the declared state. It reconciles desired vs actual, the same principle as [[devops/05-orchestration/01-kubernetes|Kubernetes]].

Reusable modules, input variables, and outputs let you parameterize and compose infrastructure (a `vpc` module reused across environments).

## The provisioning landscape

| Tool | Language | Scope | Notes |
|---|---|---|---|
| **Terraform** | HCL (declarative) | multi-cloud | the standard; huge provider ecosystem. (Note the OpenTofu fork after the license change.) |
| **Pulumi** | real languages (TS/Python/Go) | multi-cloud | IaC in a general-purpose language — loops/functions/tests, for teams who want code not HCL |
| **CloudFormation** | YAML/JSON | AWS only | AWS-native; deep AWS integration, locked to AWS |
| **AWS CDK** | real languages → CloudFormation | AWS (mainly) | write TS/Python that *generates* CloudFormation |
| **ARM/Bicep** | Azure DSL | Azure only | the Azure-native equivalent |

The axis that matters: **HCL/declarative (Terraform) vs a real programming language (Pulumi/CDK)** — declarative is simpler and more predictable; real-language IaC is more powerful and testable but easier to over-engineer. And **multi-cloud (Terraform/Pulumi) vs cloud-native (CloudFormation/Bicep)** — native tools integrate deepest but lock you in.

## Where IaC runs

IaC belongs in a [[devops/06-ci-cd/README|CI/CD pipeline]], not on someone's laptop: a change to the `.tf` files triggers a `plan` (posted for review on the PR) and, on merge, an `apply`. And IaC must **never hardcode secrets** — credentials come from a [[devops/09-secret-management/README|secret manager]] at apply time, never committed to the repo or baked into state carelessly.

## Related
- [[devops/07-infrastructure-as-code/02-configuration-management|Configuration Management]] — the other half of IaC
- [[devops/03-cloud/README|Cloud]] — what provisioning tools create
- [[devops/06-ci-cd/README|CI/CD]] — where `terraform apply` actually runs
- [[devops/09-secret-management/README|Secret Management]] — keeping credentials out of IaC
