# Logging, SIEM & Detection

**[reference]** — from the roadmap.sh cyber-security roadmap. The eyes and ears of the [[cybersecurity/07-security-operations/README|SOC]] — you can't respond to what you can't see. This is the same logging/monitoring foundation as [[devops/10-observability/README|DevOps observability]], turned toward *security* signals.

## Logs — the raw material

Every meaningful action leaves a trace; security operations lives or dies on collecting and analyzing them. The sources that matter:

- **Endpoint/OS logs** — Windows Event Logs, Linux syslog/auth logs (logins, process creation, privilege use).
- **Network logs** — firewall logs, **NetFlow** (who talked to whom), DNS query logs, proxy logs.
- **Application logs** — web server access/error logs, authentication events, database queries.
- **Cloud logs** — AWS CloudTrail, Azure/GCP audit logs (API calls, IAM changes).

The failure mode is [[cybersecurity/06-attacks-and-threats/03-web-application-attacks|OWASP's "logging & monitoring failures"]] — a breach no one noticed because nothing was logged, or logs no one looked at. Log centrally (so an attacker can't delete local evidence), retain enough history, and *actually analyze* it.

## SIEM — making sense of the flood

A **SIEM** (Security Information and Event Management) aggregates logs from everywhere into one place and **correlates** them to surface threats a single log wouldn't reveal. Its jobs:

- **Aggregation & normalization** — collect disparate log formats into a common schema.
- **Correlation** — connect events across sources into a story: "failed logins on 50 accounts (spray) → one success → new admin account created → outbound data transfer" is a breach; each event alone is noise.
- **Alerting** — fire on detection rules (correlated patterns, thresholds, known-bad indicators).
- **Dashboards & search** — for analysts to investigate and hunt.

Examples: Splunk, Elastic Security, Microsoft Sentinel, Wazuh (open-source). The eternal challenge is **tuning** — too many alerts and analysts drown in false positives (alert fatigue → real alerts ignored, the same failure mode as [[devops/10-observability/01-observability-fundamentals|noisy DevOps alerting]]); too few rules and real attacks slip through. **SOAR** (Security Orchestration, Automation and Response) sits alongside, automating repetitive response steps (enrich an alert, isolate a host) to fight the volume — see [[cybersecurity/07-security-operations/04-incident-response|incident response]].

## Detection systems

The sensors that feed detection:

- **IDS / IPS** — Intrusion Detection (alerts) / Prevention (blocks) Systems, at the network (**NIDS**, e.g. Snort/Suricata) or host (**HIDS**) level. Covered from the network angle in [[cybersecurity/03-network-security/04-intrusion-detection-and-prevention|network security]].
- **EDR / XDR** — Endpoint Detection and Response: agents on every host that record process/file/network behavior, detect malicious *behavior* (not just known signatures), and enable remote investigation/containment. The modern successor to signature antivirus, and the key defense against [[cybersecurity/06-attacks-and-threats/04-password-malware-and-exploits|fileless/behavioral malware]]. **XDR** extends it across endpoint + network + cloud.
- **NDR** — Network Detection and Response, analyzing traffic for anomalies.

## Detection approaches

- **Signature-based** — match known-bad patterns (a malware hash, an exploit string). Precise but blind to novel/[[cybersecurity/06-attacks-and-threats/04-password-malware-and-exploits|zero-day]] attacks.
- **Anomaly/behavior-based** — baseline "normal" and flag deviations (a user logging in at 3am from a new country, a server suddenly beaconing out). Catches unknowns but generates more false positives.
- **Honeypots** — decoy systems with no legitimate purpose, so *any* interaction is suspicious by definition — a high-signal, low-noise detection trick and a way to study attacker behavior.

The mature SOC combines all three, tuned to its environment, feeding a [[cybersecurity/07-security-operations/03-threat-intelligence-and-hunting|hunt]] and [[cybersecurity/07-security-operations/04-incident-response|response]] process. Detection metrics — **false positive / false negative** rates, and mean-time-to-detect — are how you measure whether it's working.

## What a detection actually looks like

Everything above is vocabulary until you write one. Take the most common detection in existence: **SSH password spraying followed by a success.**

The raw material, from a Linux auth log ([[devops/01-linux/17-logs-and-journald|logs & journald]] — `/var/log/auth.log` on Debian/Ubuntu, `/var/log/secure` on RHEL):

```
Failed password for invalid user admin from 203.0.113.9 port 54122 ssh2
Failed password for invalid user root from 203.0.113.9 port 54124 ssh2
Accepted password for deploy from 203.0.113.9 port 54180 ssh2
```

Three lines. The first two are noise on any internet-facing box; the third *after* the first two is an incident. Detection is the act of expressing "after" in a query.

**On one box, before any SIEM exists:**

```bash
journalctl -u ssh --since "1 hour ago" | grep -c "Failed password"
journalctl -u ssh --since "1 hour ago" | grep "Accepted" 
# then: does any IP appear in BOTH lists?
grep "Failed password" /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head
```

That last line — count failures per source IP, descending — is the single most useful one-liner in host-level detection, and it needs no product at all.

**In Splunk (SPL):**

```
index=linux sourcetype=secure "Failed password"
| stats count AS failures, dc(user) AS users_tried BY src_ip
| where failures > 20 AND users_tried > 5
| join src_ip [ search index=linux sourcetype=secure "Accepted password" | stats count AS successes BY src_ip ]
| where successes > 0
```

**As a Sigma rule** — the portable detection format, which converts to Splunk/Elastic/Sentinel syntax, so rules are shared as Sigma rather than rewritten per platform:

```yaml
title: SSH Brute Force Followed by Successful Login
logsource:
  product: linux
  service: sshd
detection:
  failed:
    message|contains: 'Failed password'
  success:
    message|contains: 'Accepted password'
  timeframe: 15m
  condition: failed | count() by src_ip > 20 and success
level: high
falsepositives:
  - Misconfigured automation retrying with stale credentials
  - A vulnerability scanner in an authorised test window
```

Note the `falsepositives` block. **A rule without one will be disabled within a fortnight** — the analyst who gets paged at 3am by your monitoring service's expired credential will turn it off, and it will still be off during the real intrusion.

## Tuning is the actual job

Writing the rule is an afternoon. Making it survivable is the work:

- **Baseline before you threshold.** Run the query without the `where` clause for a week and look at the distribution. A threshold of 20 is a guess; the 99th percentile of your own traffic is a decision.
- **Exclude by identity, not by silence.** Suppress the known vulnerability scanner *by its source IP and only during its window*, rather than dropping the threshold until it stops firing.
- **Every alert needs a next step.** If the analyst's only possible response is "hmm," it's a dashboard panel, not an alert. This is the same discipline as [[devops/10-observability/01-observability-fundamentals|actionable alerting]] in DevOps, and it fails the same way.
- **Test your detection by performing the attack.** Spray your own lab box ([[cybersecurity/02-ethical-hacking/05-home-lab-setup|home lab]]) and confirm the alert fires. An untested detection rule is a belief, not a control — and detections silently break when a log format changes upstream.

The uncomfortable truth of most SOCs: the rules exist, and nobody has verified since deployment that they still fire.

## Related
- [[cybersecurity/07-security-operations/03-threat-intelligence-and-hunting|Threat Intelligence & Hunting]] — turning detections into proactive searching
- [[devops/01-linux/17-logs-and-journald|Logs and journald]] — reading the raw material above on a single host
- [[devops/01-linux/20-firewalls-and-hardening|Firewalls & Hardening]] — keys-only SSH, which eliminates the attack this rule detects
- [[cybersecurity/07-security-operations/04-incident-response|Incident Response]] — what happens when an alert is real
- [[devops/10-observability/README|Observability (DevOps)]] — the same telemetry foundation for reliability
