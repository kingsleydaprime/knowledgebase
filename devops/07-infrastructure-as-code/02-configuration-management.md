# Configuration Management

**[reference]** — from roadmap.sh and the Ansible docs.

## Provisioning vs configuration, again

[[devops/07-infrastructure-as-code/01-provisioning-and-terraform|Provisioning]] creates the machine. **Configuration management** decides what's *on* it: packages installed, config files written, services running, users created — bringing an existing server to a desired software state and keeping it there.

The defining requirement is **idempotency**: running the config repeatedly must converge to the same state without repeating side effects. "Ensure nginx is installed and running" should install it the first time and do nothing the next — never "install nginx" (which errors or duplicates on the second run). Config-management tools are built around describing desired *state*, not *steps*.

## Ansible

The most popular config-management tool, and the easiest to start with because it's **agentless** — it connects over plain SSH ([[devops/01-linux/14-basic-ssh-config|SSH config]]) and needs nothing installed on the targets but Python. You describe desired state in YAML **playbooks**:

```yaml
- hosts: webservers
  become: true                     # run with sudo
  tasks:
    - name: Install nginx
      apt: { name: nginx, state: present }      # idempotent: "ensure present"

    - name: Deploy config
      template:
        src: nginx.conf.j2                        # a Jinja2 template
        dest: /etc/nginx/nginx.conf
      notify: reload nginx                        # trigger a handler on change

    - name: Ensure nginx is running
      service: { name: nginx, state: started, enabled: true }

  handlers:
    - name: reload nginx
      service: { name: nginx, state: reloaded }   # runs only if notified
```

- **Inventory** — the list of hosts (grouped, e.g. `webservers`, `dbservers`), static or dynamically pulled from a cloud API.
- **Modules** — the idempotent units (`apt`, `template`, `service`, `copy`, `user`). Each declares desired state.
- **Roles** — reusable, shareable bundles of tasks/templates/vars (Ansible Galaxy is the community registry).
- **Handlers** — actions triggered only when something changed (reload the service only if its config actually changed).

Because it's push-based over SSH with no agents, Ansible is trivial to adopt on existing servers — its main win over the alternatives.

## The landscape

| Tool | Model | Language | Notes |
|---|---|---|---|
| **Ansible** | push, **agentless** (SSH) | YAML + Jinja2 | easiest to adopt; the current default. Push means the control node initiates. |
| **Puppet** | pull, **agent** | Puppet DSL (declarative) | agents poll a central server and converge; mature, strong in large stable fleets |
| **Chef** | pull, **agent** | Ruby DSL | powerful, code-heavy ("recipes"/"cookbooks"); steeper curve |
| **Salt** | push *or* pull, agent (or agentless) | YAML + Jinja2 | fast, event-driven, scales to very large fleets |

The two axes: **push (Ansible/Salt) vs pull (Puppet/Chef agents polling a server)** — push is simpler to start, pull scales and self-heals drift continuously; and **agentless (Ansible) vs agent-based** — agentless is easier to adopt, agents give continuous enforcement. Ansible's agentless-push model is why it's usually the on-ramp.

## Where it fits — and the immutable-infrastructure alternative

Config management shines for **long-lived, mutable servers** you patch and evolve in place (a fleet of VMs, on-prem hardware). But the modern container/cloud pattern often sidesteps it entirely with **immutable infrastructure**: instead of mutating a running server, you bake a fresh machine image or container image (with [[devops/02-docker/README|Docker]], or Packer for VM images), and *replace* the old instance rather than reconfiguring it. No drift, because nothing is ever changed in place — you redeploy.

So the honest framing: config management is essential for mutable-server worlds and still ubiquitous, but for containerized/cloud-native stacks the [[devops/02-docker/README|container image]] + [[devops/05-orchestration/01-kubernetes|orchestrator]] often *is* the configuration mechanism, and Ansible/Puppet recede to provisioning the cluster hosts themselves.

## Related
- [[devops/07-infrastructure-as-code/01-provisioning-and-terraform|Provisioning & Terraform]] — creates the machines this configures
- [[devops/01-linux/14-basic-ssh-config|SSH Config]] — Ansible's transport
- [[devops/02-docker/README|Docker]] — the immutable-image alternative
