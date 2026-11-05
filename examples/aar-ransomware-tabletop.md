# Harbor Valley Community Health System Executive Ransomware Tabletop After-Action Report

*Tabletop exercise*

## Executive summary

The executive ransomware tabletop on 2026-11-04 showed that Harbor Valley can escalate quickly, protect patient safety, and issue a clear public holding statement. It also exposed gaps that would slow a real response: no written criteria for declaring an incident or severity levels, no clear after-hours authority to take clinical systems offline, no known insurer notice deadline or forensics firm, no notification matrix, no board path for the ransom decision, unpracticed clinic downtime procedures, and backup restore testing last done about 14 months ago. Priority actions are to set declaration and severity criteria, define decision authority including after hours, build a notification and contact matrix, test backup restores, and agree restoration priorities. Most high-priority fixes can be completed within 30 days.

## Scope

Facilitated 90-minute executive tabletop exercise for a fictional healthcare organization. Participants: CEO, CISO (IR lead), IT Operations Director, CMO, General Counsel, Communications Director, Business Continuity Owner, and an insurer representative role-played by the facilitator. The scenario covered seven injects from initial phishing and credential theft through lateral movement, data exfiltration, encryption and backup deletion, ransom and leak-site demands, and restoration on Day 3. Findings are based on facilitator notes and the hot wash; no technical forensic validation was performed.

## Strengths

### O2. Help desk escalation to on-call worked

*Phase: detect · CSF RS.MA (Incident Management)*

The help desk would call the security on-call phone, and everyone knew the on-call number. This gave a fast path from frontline staff to security.

> Good: everyone knew the on-call number.

### O8. Containment balanced with clinical operations

*Phase: respond · CSF RS.MI (Incident Mitigation)*

The CMO asked for time to move clinics to downtime procedures before isolating the scheduling system. The CEO then approved isolating the scheduling system without isolating the whole clinical network. This was the strongest discussion of the day and showed good trade-off thinking.

> CMO asked for 30 minutes to move clinics to downtime procedures before isolating the scheduling system

### O10. Fast, reviewed holding statement

*Phase: respond · CSF RS.CO (Incident Response Reporting and Communication)*

The Communications Director drafted a holding statement in the room in about 10 minutes, and Legal edited it. This showed effective cross-functional teamwork on external communication.

> Communications Director drafted a holding statement in the room in about 10 minutes.

### O14. Immediate patient safety escalation

*Phase: respond · CSF RS.MA (Incident Management)*

The CMO escalated ED patient safety immediately and proposed diversion criteria. This put patient care at the center of the response.

> CMO escalated ED patient safety immediately and proposed diversion criteria.

## Areas for improvement

### O1. No written criteria for declaring an incident

*Phase: detect · CSF GV.RR (Roles, Responsibilities, and Authorities)*

The team had no written criteria for declaring an incident. The CISO and IT Operations Director disagreed on who declares, and the initial alert was to be handled as a security event with escalation only if a second host showed activity. This delays a unified response.

> No written criteria for declaring an incident

### O3. Mail log search speed unknown

*Phase: detect · CSF DE.AE (Adverse Event Analysis)*

No one knew how quickly mail logs could be searched for the same email. IT Operations estimated half a day. Without a tested capability, scoping of phishing spread is uncertain during the first hours.

> Nobody knew how quickly mail logs could be searched for the same email.

### O4. Credential reset decision lacked impact check

*Phase: respond · CSF RS.MI (Incident Mitigation)*

The team decided to reset privileged credentials quickly. IT Operations warned the billing service account would break overnight claims processing, and the decision took 12 minutes, ending with a split approach: reset admins now and the service account after hours. The team lacked a pre-built dependency list to judge such trade-offs.

> IT Ops warned the billing service account would break overnight claims processing.

### O5. Insurer notice deadline unknown

*Phase: respond · CSF RS.CO (Incident Response Reporting and Communication)*

General Counsel asked whether the insurer had been notified, and no one knew the policy notice deadline. Finance holds the policy and was not in the room, which delays a time-critical obligation.

> Nobody knew the policy's notice deadline.

### O6. Forensics retainer not confirmed

*Phase: prepare · CSF RS.MA (Incident Management)*

The CISO believes a forensics retainer exists through the insurer panel but could not name the firm. Without a confirmed provider and contact, engagement during an active incident would be delayed.

> CISO believes there is one through the insurer panel but could not name the firm.

### O7. After-hours authority to take clinical systems offline unclear

*Phase: respond · CSF GV.RR (Roles, Responsibilities, and Authorities)*

No one could say who has authority to take a clinical system offline after hours if the CEO cannot be reached. This is a critical gap for patient-safety-affecting containment decisions.

> No one could say who has the authority to take a clinical system offline after hours if the CEO cannot be reached.

### O9. Clinic downtime procedures not practiced

*Phase: prepare · CSF PR.IR (Technology Infrastructure Resilience)*

Downtime procedures exist for the EHR, but clinic managers have not practiced them this year. Untested procedures risk slow or error-prone care during an outage.

> Downtime procedures exist for the EHR but the clinic managers have not practiced them this year.

### O11. Breach notification clock and laws unclear

*Phase: respond · CSF RS.CO (Incident Response Reporting and Communication)*

General Counsel said HIPAA breach notification has a 60-day clock but was not sure when the clock starts or which state laws apply. No notification matrix exists, which creates legal exposure and deadline risk.

> but was not sure when the clock starts or which state laws apply

### O12. Ownership of reporter inquiry delayed

*Phase: respond · CSF GV.RR (Roles, Responsibilities, and Authorities)*

No one owned the reporter's email until the CEO assigned it to Communications. Unowned inbound inquiries risk inconsistent or late responses.

> No one owned the reporter's email until the CEO assigned it to Communications.

### O13. Backup immutability claimed but restore untested

*Phase: recover · CSF RC.RP (Incident Recovery Plan Execution)*

IT Operations said backups are immutable, but the last restore test was before the migration, about 14 months ago. The immutability claim was not supported by recent restore evidence, so recovery confidence is unverified.

> about 14 months ago

### O15. No severity levels or major incident definition

*Phase: respond · CSF RS.MA (Incident Management)*

The team did not agree on whether the event was now a major incident. The plan has no severity levels, so escalation, resourcing, and executive involvement are decided ad hoc.

> the plan has no severity levels

### O16. No board-approved ransom position or sanctions process

*Phase: respond · CSF GV.PO (Policy)*

The CEO said the organization does not pay, but there is no board-approved position and no process for sanctions screening. The group agreed the decision would go to the board chair, but no documented path exists to reach the board quickly.

> there is no board-approved position and no process for sanctions screening

### O17. Law enforcement contact unknown

*Phase: respond · CSF RS.CO (Incident Response Reporting and Communication)*

Nobody knew who the contact at the FBI field office is. Without a known contact, early reporting and coordination would be slower.

> nobody knew who the contact at the FBI field office is

### O18. No pre-agreed restoration order

*Phase: recover · CSF RC.RP (Incident Recovery Plan Execution)*

Restoration priority was debated for 15 minutes. Clinical wanted EHR interfaces first and Finance, by proxy, wanted billing. No pre-agreed restoration order exists, so restoration decisions are made under pressure.

> No pre-agreed restoration order exists.

### O19. No clean-system sign-off owner

*Phase: recover · CSF RC.RP (Incident Recovery Plan Execution)*

IT Operations could not say who signs off that a restored system is clean. Without a named approver, restored systems may return to service without a clear security validation.

> IT Ops could not say who signs off that a restored system is clean.

## Gaps

- No written criteria or severity levels for declaring and escalating an incident
- No defined decision authority for after-hours clinical system isolation or credential resets
- No notification matrix for HIPAA, state laws, and insurer notice deadlines
- Insurer policy notice deadline not known by incident team; policy held by Finance
- Forensics retainer not confirmed and provider not named
- No documented contact path to FBI field office
- No board-approved ransom payment position or sanctions screening process
- No documented path to reach the board chair quickly
- Backup restore testing not performed recently; immutability unverified
- Clinic managers have not practiced EHR downtime procedures this year
- No pre-agreed restoration priority order
- No named owner for signing off that restored systems are clean

## Recommendations

| # | Recommendation | Priority | Timeframe | Suggested owner | Addresses |
|---|---|---|---|---|---|
| 1 | **Define incident declaration criteria and severity levels**: Write and approve criteria for declaring an incident, a single declaring authority, and severity levels with escalation triggers and executive notification rules. Add these to the IR plan and test them in the next exercise. | high | 30 days | Chief Information Security Officer | O1, O15 |
| 2 | **Set after-hours decision authority for clinical systems**: Approve a delegation charter naming who can isolate clinical systems, reset privileged credentials, and approve downtime when the CEO cannot be reached. Include named alternates and a contact method for each. | high | 30 days | Chief Executive Officer | O7 |
| 3 | **Build a notification and deadline matrix**: Create a matrix covering HIPAA breach notification timing, state breach laws, insurer notice requirements, and law enforcement reporting. Define when each clock starts, who owns each notice, and the required evidence. Confirm the insurer notice deadline from the policy now. | high | 30 days | General Counsel | O5, O11 |
| 4 | **Confirm forensics retainer and key external contacts**: Verify the forensics retainer through the insurer panel and record the firm, contact, and activation process. Record the FBI field office contact and the insurer claims contact in a single, tested contact sheet. | high | 30 days | Chief Information Security Officer | O6, O17, O5 |
| 5 | **Test backup restores and verify immutability**: Perform a full restore test of critical systems from immutable backups and document the results. Verify immutability settings and set a recurring restore test schedule, at least quarterly. | high | 30 days | IT Operations Director | O13 |
| 6 | **Establish a board-approved ransom decision position**: Obtain board approval for a ransom payment position and document the sanctions screening process. Define the escalation path to the board chair, including backup contacts and the time limit for a decision. | high | 90 days | General Counsel | O16 |
| 7 | **Map service account dependencies before credential resets**: Document critical service accounts, their business processes, and the outage impact of resetting them. Include overnight claims processing. Use this map to make pre-approved reset sequencing decisions. | medium | 90 days | IT Operations Director | O4 |
| 8 | **Measure mail log search speed for phishing scoping**: Run a timed test of searching mail logs for a phishing email across all mailboxes. Set a target response time and document the steps and tools needed to meet it. | medium | 90 days | Security Operations Manager | O3 |
| 9 | **Agree restoration priorities and clean-system sign-off**: Agree a restoration order for clinical and business systems with clinical, finance, and IT input. Name a single approver who confirms restored systems are clean before reconnection. | medium | 90 days | Business Continuity Owner | O18, O19 |
| 10 | **Run EHR downtime drills for clinic managers**: Schedule downtime drills for all clinic managers and clinical leads covering EHR downtime procedures. Record gaps and update the procedures after each drill. | medium | 90 days | Business Continuity Owner | O9 |
| 11 | **Assign owner for inbound reporter and public inquiries**: Define who owns inbound media and reporter inquiries during an incident, with a rule for routing them to Communications within a set time. Include this in the communications plan. | medium | 90 days | Communications Director | O12 |
| 12 | **Preserve and document what worked**: Capture the help desk escalation path, the patient safety escalation pattern, and the holding statement process as standard playbook steps. Reuse them in future exercises to protect these strengths. | low | 180 days | Incident Response Lead | O2, O8, O10, O14 |

*Generated with IR Readiness Copilot. Review before distribution.*
