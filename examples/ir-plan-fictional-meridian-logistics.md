# Meridian Freight Logistics — Incident Response Plan

**Version:** 2.1 · **Owner:** Director of Information Security · **Approved by:** Chief Operating Officer, March 2026

> Fictional document created for IR Readiness Copilot examples. Meridian Freight Logistics, its people and vendors do not exist. The plan is intentionally incomplete in places so the assessment has gaps to find.

## 1. Purpose and scope

This plan describes how Meridian Freight Logistics detects, responds to and recovers from cybersecurity incidents. It applies to all corporate IT systems, the warehouse management system (WMS), the fleet tracking platform and the customer shipping portal. It does not cover physical security incidents at warehouses, which are handled by the Facilities team.

## 2. Definitions

A **security event** is any observable occurrence in a system or network, such as an alert from the endpoint protection tool or a user reporting a suspicious email. A **security incident** is an event that actually or potentially compromises the confidentiality, integrity or availability of Meridian systems or data, or violates the acceptable use policy.

The Incident Manager declares an incident when an event is confirmed to involve unauthorized access, malware execution, data exposure or an outage of a critical system caused by malicious activity.

## 3. Roles and responsibilities

| Role | Primary | Backup | Responsibilities |
|---|---|---|---|
| Incident Manager | Director of Information Security | Senior Security Engineer | Declares incidents, sets severity, coordinates the response team and reports to leadership. |
| Technical Lead | IT Infrastructure Manager | Senior Systems Administrator | Directs containment, eradication and recovery of systems. |
| Communications Lead | VP Marketing | Customer Success Director | Drafts internal and customer communications. |
| Legal Advisor | General Counsel | — | Advises on legal obligations and contracts. |
| Executive Sponsor | Chief Operating Officer | Chief Financial Officer | Approves major business decisions during an incident. |

The Executive Sponsor must approve any action that stops warehouse operations or the customer shipping portal for more than two hours.

## 4. Severity levels

| Severity | Criteria | Response |
|---|---|---|
| SEV1 — Critical | Ransomware or destructive malware, confirmed theft of customer or employee personal data, or an outage of the WMS or fleet tracking platform | Incident Manager engaged within 15 minutes, Executive Sponsor notified within 30 minutes, response team works continuously |
| SEV2 — High | Compromise of a privileged account, malware on multiple endpoints, or suspected data exposure | Incident Manager engaged within 1 hour, Executive Sponsor notified within 4 hours |
| SEV3 — Medium | Malware on a single endpoint, or a compromised standard user account | Handled by the security team during business hours |
| SEV4 — Low | Policy violations and unsuccessful attacks | Logged and reviewed weekly |

## 5. Reporting and escalation

Employees report suspected incidents to the IT Service Desk at extension 4400 or through the "Report Phishing" button in email. The Service Desk creates a ticket in the security queue. The on-call security engineer reviews new tickets within 30 minutes during business hours and confirms whether the report is a real event.

Escalation follows the severity table in Section 4. Outside business hours, the Service Desk calls the on-call security engineer, who escalates SEV1 and SEV2 incidents to the Incident Manager by phone.

## 6. Contacts

The Incident Manager maintains the incident contact list in the shared drive folder "Security / IR Contacts". It includes the response team, the executive team, and the following external parties:

- Cyber insurance: Harborline Mutual, policy number on file with Finance
- Managed detection and response provider: Sentinel Grid
- Outside counsel: to be confirmed

## 7. Response procedures

### 7.1 Analysis

The security team reviews endpoint, email and firewall logs to understand what happened, which systems are affected and how the attacker gained access.

### 7.2 Evidence

Before rebuilding a compromised system, the Technical Lead makes sure relevant logs are exported.

### 7.3 Containment

Containment options include isolating endpoints through the endpoint protection console, disabling compromised accounts, resetting passwords and blocking malicious IP addresses and domains at the firewall. The Incident Manager chooses the containment option. If containment would stop warehouse operations or the shipping portal for more than two hours, the Executive Sponsor must approve it first.

### 7.4 Eradication

The Technical Lead removes malware, closes the access path the attacker used and resets credentials for affected accounts. Systems with confirmed malware are rebuilt from a known-good image rather than cleaned.

### 7.5 Recovery

Systems are restored in this order: identity services (Active Directory), WMS, fleet tracking platform, customer shipping portal, then other business systems. Backups are taken nightly and stored in a separate cloud account.

## 8. Communication

The Communications Lead prepares updates for employees and, when customers are affected, a customer notice. All external statements are approved by the Incident Manager and the General Counsel before release. Media inquiries are directed to the VP Marketing.

## 9. After an incident

Within ten business days after a SEV1 or SEV2 incident is closed, the Incident Manager runs a lessons learned meeting with the response team. Action items are recorded in the security team's tracker with an owner and a due date.

## 10. Plan maintenance

This plan is reviewed every year by the Director of Information Security, and after any SEV1 incident.
