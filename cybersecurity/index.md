# Cybersecurity

## What cybersecurity is

**Cybersecurity is protecting computers, networks and data from people who want to steal, change or break them.**

Every day, people try to guess passwords, trick staff into clicking fake links, break into websites, and lock companies' files until a ransom is paid. Cybersecurity is the work of stopping them, and of noticing and recovering when they get through anyway.

The field has two sides that need each other. **Defenders** (the "blue team") build protections, watch for attacks and respond to them. **Ethical hackers** (the "red team") attack systems with permission, to find weaknesses before criminals do. Nothing is ever perfectly secure; the goal is to make attacks hard, noticeable and limited in the damage they can do.

## What you'll be able to do

By the end you will be able to:
- protect your own accounts and devices, and help family and friends do the same;
- explain the main ways attackers get in, and how each is stopped;
- think through what could go wrong in a system before building it;
- secure a website or API against the most common attacks;
- explain how encryption keeps data private and proves who sent it;
- describe how a security team detects and responds to an attack;
- find weaknesses yourself in a legal practice lab.

## Where to start

**Not working in security?** Start with [[cybersecurity/10-protecting-yourself/index|Protecting Yourself]]. It's eight notes with no jargon, for keeping you and your family safe.

**Want to work in security?** Read the fundamentals first, then follow your interest. Sections 03 to 09 can be read in any order once the fundamentals are done.

### Fundamentals (start here)

1. [[cybersecurity/01-fundamentals/01-what-is-cybersecurity|What Is Cybersecurity]]: defenders and attackers, the main areas of the field, and why nothing is ever "fully secure".
2. [[cybersecurity/01-fundamentals/02-cia-triad|The CIA Triad]]: the three things security protects: keeping data secret, keeping it correct, and keeping it available.
3. [[cybersecurity/01-fundamentals/03-attacker-and-hacker-types|Attacker and Hacker Types]]: who attacks and why, from beginners using ready-made tools to government-backed groups and insiders.
4. [[cybersecurity/01-fundamentals/04-security-principles|Security Principles]]: lasting design rules, such as giving every person and program only the access it needs.
5. [[cybersecurity/01-fundamentals/05-threat-modeling|Threat Modelling]]: a simple method for listing what could go wrong in a system and deciding what to fix first.

### Protecting yourself

- [[cybersecurity/10-protecting-yourself/index|Protecting Yourself]]: passwords and why reusing them is the real danger, why text-message codes are the weakest kind of two-step login, spotting scams now that AI writes them, backups, privacy, and a checklist for when you've already been hacked.

### How attacks work

- [[cybersecurity/06-attacks-and-threats/index|Attacks and Threats]]: a catalogue of the main attacks: tricking people, attacking networks, attacking websites, cracking passwords and malware.
- [[cybersecurity/02-ethical-hacking/index|Ethical Hacking]]: attacking systems with permission to find weaknesses: the rules, the steps, the tools, setting up a practice lab, and the career path.

### Defending systems

- [[cybersecurity/03-network-security/index|Network Security]]: firewalls, splitting networks into zones, VPNs, and systems that spot intruders.
- [[cybersecurity/04-web-security/index|Web Security]]: protecting websites: storing passwords safely, two-step login, blocking the most common website attacks, and browser security settings.
- [[cybersecurity/14-api-security/index|API Security]]: protecting APIs, where the most common bug is letting a user see someone else's data by changing a number in a request.
- [[cybersecurity/05-cryptography/index|Cryptography]]: the maths that keeps data secret and proves who sent it: encryption, hashing and digital signatures, and the mistakes that break them.
- [[cybersecurity/09-cloud-security/index|Cloud Security]]: securing apps on AWS and other clouds: who's responsible for what, access control, and containers.

### Running security in an organisation

- [[cybersecurity/07-security-operations/index|Security Operations]]: the defenders' daily work: collecting logs, detecting attacks, hunting for intruders, responding to incidents and investigating afterwards.
- [[cybersecurity/08-governance-risk-and-compliance/index|Governance, Risk and Compliance]]: the management side: judging risk, following security standards, and certifications for your career.

### Advanced specialisms

- [[cybersecurity/11-binary-exploitation/index|Binary Exploitation]]: breaking compiled programs through memory bugs, and the defences against it. Needs [[languages/04-c/index|C]] and [[computer-architecture/index|Computer Architecture]].
- [[cybersecurity/13-malware-and-reverse-engineering/index|Malware Analysis and Reverse Engineering]]: taking apart malicious programs safely to understand what they do and how to detect them.
- [[cybersecurity/12-active-directory/index|Active Directory]]: attacking and defending the system most companies use to manage staff logins, the core of real internal security testing.

## Practice

- [[cybersecurity/projects|Projects]]: hands-on tasks, from easy (🟢) to hard (🔴), each with a clear "done when".
- [[cybersecurity/interview/index|Cybersecurity interview prep]].
- **Only practise attacks on systems you own or have written permission to test.** The [[cybersecurity/02-ethical-hacking/index|Ethical Hacking]] section explains how to set up a legal practice lab.

## Key ideas to remember

1. **Nothing is perfectly secure.** Make attacks hard, noticeable and limited in damage. → [[cybersecurity/01-fundamentals/01-what-is-cybersecurity|What Is Cybersecurity]]
2. **Give every person and program only the access it needs.** A break-in then reaches less. → [[cybersecurity/01-fundamentals/04-security-principles|Security Principles]]
3. **Reusing a password is the real danger,** not a weak one: one leaked site unlocks all the others. → [[cybersecurity/10-protecting-yourself/index|Protecting Yourself]]
4. **Most attacks start by tricking a person,** not by breaking technology. → [[cybersecurity/06-attacks-and-threats/index|Attacks and Threats]]
5. **Check permission on every request,** not just at login. Forgetting is the most common API bug. → [[cybersecurity/14-api-security/index|API Security]]

## Related

- [[networking/index|Networking]]: how the networks being protected work.
- [[backend/index|Backend]]: where most security checks in an app live.
- [[devops/index|DevOps]]: the infrastructure behind cloud security.

---

## About this course

- **How it grew:** sections 01–05 are the original course. Sections 06–09 were added by checking the vault against the [roadmap.sh cybersecurity roadmap](https://roadmap.sh/cyber-security); security operations (the defenders' daily work) was the biggest gap. Sections 10–14 were added later. That's why the section numbers don't follow the reading order above.
