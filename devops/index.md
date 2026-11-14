# DevOps

## What DevOps is

**DevOps is everything involved in getting code off a developer's laptop and running reliably on servers for real users, and keeping it running.**

Writing an app is only half the job. Someone has to put it on a computer that's always on and connected to the internet (a **server**), make sure it starts up again if it crashes, release new versions without breaking anything, and notice when something goes wrong before users complain. In the past, "developers" wrote code and a separate "operations" team ran it. DevOps joins the two: the people who build the software also care about shipping and running it, and they automate as much of that work as possible.

The tools you'll meet include **Linux** (the operating system most servers run), **Docker** (packaging an app with everything it needs), **cloud providers** like AWS (renting servers instead of buying them), and **CI/CD** (automatically testing and releasing every change).

## What you'll be able to do

By the end you will be able to:
- use Linux confidently from the command line;
- package an app in a container so it runs the same everywhere;
- put an app on a real server with its own domain name and HTTPS;
- set up automatic testing and releasing for every change;
- keep passwords and keys out of your code;
- monitor a live app and get alerted when it breaks;
- describe servers and their setup in code, so they can be rebuilt automatically;
- run many containers across many machines with Kubernetes.

## Where to start

**Before you start:** basic programming ([[programming-fundamentals/index|Programming Fundamentals]]) and [[git/index|Git]]. Knowing [[networking/index|how networks work]] and [[os/index|what an operating system does]] makes everything here easier.

Read in the order below; the section numbers follow it. Networking and web servers come early because you need them to put a site on a server, and Kubernetes comes late because it builds on everything else.

### The basics

1. [[devops/00-the-physical-layer/index|The Physical Layer]]: the real machines, buildings and cables under "the cloud", and how one physical computer is split into many virtual ones.
2. [[devops/01-linux/index|Linux]]: the command line, files, users, running programs and services, and remote login with SSH, up to the RHCSA certification if you want it.
3. [[devops/02-networking-and-web/index|Networking and Web Servers]]: domain names, HTTPS, and Nginx, the program that sits in front of your app and passes requests to it.
4. [[devops/03-docker/index|Docker]]: packaging an app with everything it needs into a container.
5. [[devops/04-vps/vps-setup|Deploying to a Server]]: putting a real app on a rented Linux server (a VPS), using everything above.

### Shipping changes safely

6. [[devops/05-ci-cd/index|CI/CD]]: automatically testing every change and releasing it, mostly with GitHub Actions.
7. [[devops/06-secret-management/index|Secret Management]]: keeping passwords and keys out of your code and out of Git.
8. [[devops/07-observability/index|Observability]]: seeing what a live app is doing through metrics, logs and traces, and deciding when to alert someone.

### Working at larger scale

9. [[devops/08-cloud/index|Cloud]]: what AWS, Azure and Google Cloud offer, and how to choose between their services.
10. [[devops/09-infrastructure-as-code/index|Infrastructure as Code]]: describing servers and their setup in files, so they can be created and changed automatically.
11. [[devops/10-orchestration/index|Orchestration and Kubernetes]]: running many containers across many machines, and restarting or moving them automatically.
12. [[devops/11-delivery-and-advanced/index|Delivery and Advanced Topics]]: releasing by updating a Git repository (GitOps), storing build outputs, and service meshes.
13. [[devops/12-sre-and-platform-engineering/index|SRE and Platform Engineering]]: the ways of working, not the tools: how teams share on-call duty, cut repetitive work, and build internal platforms for other developers.

## For quick lookup

- [[devops/devops-reference|DevOps reference]]: the whole DevOps landscape in one long reference, for looking things up.
- [[devops/minio-guide|MinIO guide]]: setting up your own file storage server.

## Practice

- [[devops/projects|Projects]]: hands-on tasks, from easy (🟢) to hard (🔴), each with a clear "done when".
- [[devops/interview/index|DevOps interview prep]].
- DevOps is learned by doing more than reading. The best practice is to deploy something real: a small app on a server, with a pipeline that releases it when you push.

## Key ideas to remember

1. **Automate anything you'd otherwise do by hand twice.** Manual steps get forgotten or done differently each time.
2. **A container runs the same on your laptop and on the server,** which ends "it works on my machine". → [[devops/03-docker/index|Docker]]
3. **Passwords and keys never go in Git,** even in a private repository. → [[devops/06-secret-management/index|Secret Management]]
4. **If you can't see it, you can't fix it.** Set up logs and alerts before you need them. → [[devops/07-observability/index|Observability]]
5. **"The cloud" is still physical machines in physical buildings.** That's why spreading across several data centres protects you. → [[devops/00-the-physical-layer/index|The Physical Layer]]

## Related

- [[git/index|Git]]: where every change starts.
- [[os/index|Operating Systems]]: what's happening underneath Linux commands.
- [[networking/index|Networking]]: the theory behind section 02.
- [[backend/index|Backend]]: the apps you'll be deploying.
- [[cybersecurity/index|Cybersecurity]]: protecting everything you run.

---

## About this course

- **Where it came from:** Linux, Docker and the server deploy come from real use (Linux certification study and real deployments). The physical layer and SRE sections were added in August 2026 from an IT fundamentals course. Kubernetes, Terraform, Ansible, Prometheus and the other advanced tools were written from the [roadmap.sh DevOps roadmap](https://roadmap.sh/devops) and official documentation, not from running them in production. The CI/CD section uses this vault's own deploy workflow as its example.
- **Renumbered in November 2026** so the sections follow the reading order. They used to be numbered in the order they were added.
