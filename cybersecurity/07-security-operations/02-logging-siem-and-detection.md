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

## Related
- [[cybersecurity/07-security-operations/03-threat-intelligence-and-hunting|Threat Intelligence & Hunting]] — turning detections into proactive searching
- [[cybersecurity/07-security-operations/04-incident-response|Incident Response]] — what happens when an alert is real
- [[devops/10-observability/README|Observability (DevOps)]] — the same telemetry foundation for reliability
