# Ransomware with Data Extortion Executive Tabletop: Harbor Valley Community Health System

**Industry:** healthcare · **Size:** medium · **Scenario:** ransomware · **Audience:** executive · **Duration:** 90 min

## Narrative

Harbor Valley Community Health System is a fictional nonprofit provider operating two hospitals, four outpatient clinics and a shared services center, with about 1,100 employees and a five-person security team. On a Monday morning, a billing specialist reports a phishing email with an attachment that she opened the previous Friday, and an endpoint alert shows a script running on her workstation. Over the next several hours, the attacker uses stolen credentials to move between servers, copies patient billing and scheduling data to an outside cloud storage account, and then disables security tools, deletes backups and encrypts file servers and the electronic scheduling system. A ransom note demands payment within 72 hours and threatens to publish stolen records. Participants must decide when to declare an incident, how far to isolate the network, whether to engage law enforcement, outside counsel and a forensics firm, whether to pay, what to restore first, and how to tell patients, staff, regulators, the media and the insurer what is happening.

## Objectives

- Confirm who has authority to declare an incident, activate the response plan and approve isolation decisions that cause clinical or business downtime
- Decide whether to isolate individual systems or the whole network, and state the business trade-offs leadership would accept
- Agree on engagement of outside counsel, a forensics firm, the cyber insurance carrier and law enforcement, including the order and purpose of each
- Test the organization's position on ransom payment, including legal constraints, sanctions screening and the leadership decision process
- Set restoration priorities for clinical systems and confirm how backup integrity will be verified before restore
- Identify notification obligations under HIPAA, state breach laws and contractual terms, and test the communication plan for patients, staff, regulators and the media

## Roles

**Chief Executive Officer**

- Make or ratify final decisions on network isolation, ransom position and public statements
- Balance patient safety, financial exposure and reputational risk
- Chair the executive crisis decision meetings

**Incident Response Lead (CISO)**

- Declare incident severity and recommend containment options
- Coordinate technical responders, the forensics firm and the security team
- Report status and options to executive leadership on a fixed cadence

**IT Operations Director**

- Estimate downtime and effort for isolating, rebuilding and restoring systems
- Confirm which backups exist, where they are stored and their last known good dates
- Direct infrastructure staff in executing containment and recovery steps

**Chief Medical Officer and Clinical Operations Lead**

- Assess patient safety impact of EHR, scheduling and imaging outages
- Decide on diversion, manual downtime procedures and clinic closures
- Advise on priority order for clinical system restoration

**General Counsel (with outside breach counsel)**

- Advise on breach notification duties under HIPAA and state laws and their deadlines
- Advise on the legal and sanctions implications of any ransom payment
- Direct privilege over the investigation and coordinate with law enforcement

**Communications and PR Director**

- Draft holding statements for media, patients and staff
- Manage media inquiries and monitor public reporting
- Coordinate message consistency with legal and regulatory communications

**Business Continuity Owner**

- Activate downtime procedures across hospitals and clinics
- Track recovery time objectives and recovery priorities for each service
- Report operational status to executives and the board

**Cyber Insurance Carrier Representative (advisory)**

- Confirm policy notice requirements and approved vendor panel
- Explain coverage limits, retentions and consent requirements for ransom and vendor costs
- Advise on expectations for documentation and forensic reporting

## Injects

### 1. Suspicious Attachment Reported and Script Activity Detected

*T+0h · Phase: Detect*

At 07:40 Monday, a billing specialist calls the help desk. She says she opened an invoice attachment on Friday afternoon from a sender claiming to be a major supplier, and her computer has been slow since. The endpoint security console shows a script launched from her profile that attempted to contact an unfamiliar external address. The security analyst on duty has isolated the workstation but has not yet determined whether other accounts received the same email. Leadership has not yet been told.

**ATT&CK:** [T1566.001 Spearphishing Attachment](https://attack.mitre.org/techniques/T1566/001), [T1059.001 PowerShell](https://attack.mitre.org/techniques/T1059/001)

**Expected actions:**

- Decide whether this is a security event, an incident, or still under review, and who makes that call
- Ask whether other mailboxes received the same email and who checks mail logs
- Determine whether the analyst can escalate without waiting for executive approval
- Decide when the CEO and General Counsel are informed

### 2. Credential Theft and Odd-Hour Administrator Logins

*T+2h · Phase: Detect*

At 09:30 the security team finds that a service account with broad file server rights was used from the billing workstation's segment. Endpoint alerts show a process accessing credential storage on two servers. Two administrator accounts were used overnight to log in to servers outside normal change windows. The analyst believes an attacker may hold valid credentials for several systems, including the scheduling server that supports clinic operations this week.

**ATT&CK:** [T1003.001 LSASS Memory](https://attack.mitre.org/techniques/T1003/001), [T1078 Valid Accounts](https://attack.mitre.org/techniques/T1078)

**Expected actions:**

- Decide whether to reset privileged credentials now or wait for forensic confirmation
- Assess the effect of disabling the service account on clinic and billing operations
- Decide whether to bring in the forensics firm and what authority it needs
- Confirm who notifies the cyber insurance carrier and whether notice has been given

### 3. Lateral Movement to Clinical Servers

*T+4h · Phase: Respond*

At 11:15 the IT operations team reports unusual remote desktop sessions between servers that do not normally communicate, including the file server and the scheduling system. The team estimates that isolating the scheduling system will stop clinic appointment check-in and lab order routing for up to six hours. Isolating the entire clinical network would stop all EHR access at both hospitals. The forensics firm says it cannot yet confirm which systems are compromised and estimates three to five more hours to determine scope.

**ATT&CK:** [T1021.001 Remote Desktop Protocol](https://attack.mitre.org/techniques/T1021/001)

**Expected actions:**

- Choose between isolating the scheduling system, isolating the clinical network, or continuing to monitor
- Decide who approves the business downtime and what patient safety checks are required first
- Confirm activation of manual downtime procedures at hospitals and clinics
- Decide whether to notify the board chair and when

### 4. Data Found in Outside Cloud Storage

*T+6h · Phase: Respond*

At 13:20 the forensics team reports that outbound traffic logs show several gigabytes uploaded over the past three days to an external cloud storage account. Preliminary review suggests the upload contains billing exports and patient scheduling records, including names, dates of birth, insurance identifiers and appointment reasons. The forensics lead says this is confirmed exfiltration but the full data set is not yet known. A reporter from a regional newspaper emails the communications office asking about a possible cyberattack at the hospital.

**ATT&CK:** [T1567.002 Exfiltration to Cloud Storage](https://attack.mitre.org/techniques/T1567/002)

**Expected actions:**

- Decide whether the breach of patient information is treated as a presumed breach for notification purposes
- Engage outside breach counsel and confirm privilege over the investigation
- Decide what the holding statement says, and whether it confirms or declines to comment on the incident
- Determine who answers the reporter and who contacts the cyber insurance carrier about the potential breach

### 5. Encryption and Backup Deletion Across File and Scheduling Servers

*T+8h · Phase: Respond*

At 16:45 staff across both hospitals report that files cannot be opened. The forensics team confirms that security agents were disabled on several servers, that backup catalogs show deletion of recent restore points, and that file servers and the scheduling system are encrypted. A ransom note appears on affected servers, demanding payment in bitcoin within 72 hours and threatening to publish stolen patient data on a leak site. The note includes a sample file of billing records. Clinic operations are on paper downtime procedures, and the emergency department reports that some lab and imaging results cannot be retrieved.

**ATT&CK:** [T1685 Disable or Modify Tools](https://attack.mitre.org/techniques/T1685), [T1490 Inhibit System Recovery](https://attack.mitre.org/techniques/T1490), [T1486 Data Encrypted for Impact](https://attack.mitre.org/techniques/T1486)

**Expected actions:**

- Decide whether to formally declare a major incident and activate the full crisis team
- Confirm whether patient safety escalation to the CMO is required for the emergency department
- Decide whether to pause all payments and sanctions screening work pending a ransom decision
- Determine the notification plan to staff tonight, given possible public disclosure

### 6. Ransom Deadline Approaches and Leadership Must Decide

*Day 2, 09:00 · Phase: Respond*

Thirty-six hours later, the attacker's leak site lists Harbor Valley by name and shows a preview of 2,000 patient records. The forensics firm now estimates that 280,000 patient records were copied. The cyber insurer's panel vendor says a negotiator is available, and it recommends obtaining sanctions and legal review before any contact. A local television station has asked for an interview with the CEO. Two regulators have sent informal inquiries after reading the leak site listing. The board chair asks for a written recommendation on whether to pay by the end of the day.

**Expected actions:**

- Decide whether the organization will pay, refuse, or delay, and who has final authority
- Confirm whether a payment would be legal under sanctions rules and whether law enforcement has been consulted
- Decide whether the CEO gives an interview, and what can be said without confirming details
- Decide what is communicated to affected patients now, and what is held until notification counsel advises

### 7. Restoration Trade-offs and Backup Integrity Doubts

*Day 3, 14:00 · Phase: Recover*

The IT operations director reports that the most recent clean backup of the scheduling system is nine days old, and that some backups from the last two weeks may contain the attacker's tools. Rebuilding the scheduling and EHR interface servers from clean images is estimated at four to six days. Clinical leaders want the EHR restored first, but the business continuity owner notes that billing and payroll systems have payment deadlines and that patient registration has missed sync for two days. The cyber insurer requires documented restoration steps before it will approve vendor costs. Leadership must set the order of restoration and decide how to certify that restored data is clean.

**Expected actions:**

- Set restoration priority across clinical, billing and payroll systems, and confirm the rationale
- Decide how backup integrity will be verified and who signs off that systems are clean
- Decide whether to accept a data loss gap for scheduling records and how patients are informed
- Confirm regulator and patient notification timelines against the restoration status and the data copy findings

## Discussion questions

### Detect

1. What specific facts would have caused you to declare an incident at T+0h, and who should be called first if the analyst is unsure? *(RS.MA)*
1. Who is authorized to take a critical service offline without first getting executive approval, and is that written in the plan? *(GV.RR)*
1. How would you know whether the same phishing email reached other staff, and how long would that take to confirm? *(DE.CM)*
1. What signals would convince you that the investigation has moved from a single workstation to privileged accounts, and who needs to hear that message? *(DE.AE)*

### Respond

1. Given the downtime cost and patient safety risk, what is your decision threshold for isolating the scheduling system versus the whole clinical network? *(RS.MI)*
1. When should outside counsel, the forensics firm and the cyber insurer be engaged, and what does each one need to do first? *(RS.MA)*
1. If the data copy is confirmed, what are your legal obligations for notifying patients, regulators and the media, and which deadlines start running? *(RS.CO)*
1. Would the organization pay the ransom? Which factors would you weigh, including legal restrictions, patient harm and the likelihood that data is published anyway? *(GV.RR)*
1. What would you say to the press and to staff in the first hour, and who approves each statement? *(RS.CO)*

### Recover

1. Which systems must be restored first to keep patients safe, and how do you balance that against billing and payroll deadlines? *(RC.RP)*
1. How will you verify that a backup is clean before restoring it, and who is accountable for signing off? *(RC.RP)*
1. If the most recent clean backup is nine days old, what data loss can the business accept, and how will that be explained to patients and clinicians? *(RC.CO)*
1. What promises will you make to staff, patients and regulators about recovery timelines, and how will you avoid promising more than you can deliver? *(RC.CO)*

### Improve (ID.IM)

1. Which decisions in this exercise took too long, and what authority or information was missing when they were made? *(ID.IM)*
1. Which parts of the incident response plan did participants not know existed, and how will those be trained before the next exercise? *(ID.IM)*
1. What contract or insurance terms would you change now to reduce the cost and delay of a future ransomware response, including vendor panel access? *(GV.SC)*
1. Which backup and recovery assumptions were tested today, and which should be validated with a technical restore test within 90 days? *(ID.IM)*

## Facilitator guide

### Preparation

- Confirm the executive attendee list, including the CEO, General Counsel, CMO, CFO and board chair representative, and obtain commitment for the full 90 minutes
- Give participants the pre-read covering the organization profile, current incident response plan, and the decision-making authority matrix
- Brief the General Counsel and communications lead on the fictional leak site and newspaper scenario so they can rehearse responses
- Prepare printed injects with timestamps and a visible clock or timer in the room
- Prepare a decision log template capturing each decision, owner, time and rationale for use in the improvement session
- Prepare a simple timeline board showing the 72-hour ransom deadline and the regulator notification clocks
- Confirm which real contacts for the cyber insurer, outside breach counsel and forensics firm will be referenced as fictional placeholders
- Assign a neutral note-taker who is not in the decision chain
- Review the injects with the CISO so the technical facts are plausible without deep technical detail
- Agree with the CEO that no real operational or sanctions decisions will be made during the exercise

### Agenda

- 0 to 10 minutes: Opening, ground rules, scenario overview and decision log introduction
- 10 to 20 minutes: Inject 1, suspicious attachment and script activity, with discussion of declaration and escalation
- 20 to 30 minutes: Inject 2, credential theft and privileged account use, with discussion of containment and insurer notice
- 30 to 40 minutes: Inject 3, lateral movement and the isolation decision
- 40 to 50 minutes: Inject 4, data found in outside cloud storage, with discussion of breach presumption and public inquiries
- 50 to 60 minutes: Inject 5, encryption, backup deletion and patient safety escalation
- 60 to 70 minutes: Inject 6, ransom deadline and the payment decision with media and regulator pressure
- 70 to 80 minutes: Inject 7, restoration priorities and backup integrity
- 80 to 85 minutes: Discussion questions for improvement, focusing on decision delays and missing authority
- 85 to 90 minutes: Closing summary of decisions made, open issues and owners for follow-up

### Facilitation tips

- Ask each executive to state their decision and its rationale aloud, then have the note-taker record it before moving on
- Interrupt when the room drifts into technical detail and ask what the executive decision is and who owns it
- Use the clock: tell participants that time has passed and that new information has arrived between injects
- Make the ransom discussion concrete by asking what the payment decision would be today, not in principle, and by asking who would sign the wire approval
- Ask the General Counsel to speak to notification clocks as if they were real, and ask the communications lead to read the holding statement aloud
- Do not let anyone claim that backups are clean without naming the evidence and the person who verified it
- Watch for executives assuming that the insurer will decide for them, and ask what the policy actually requires
- Keep the conversation on patient safety and business impact, not on attacker methods
- If the group reaches consensus quickly, introduce a complication such as a second regulator inquiry or a clinic reporting a medication dispensing error
- Close by asking each participant which single decision they would change in the real plan

### Expected gaps

- No clear single authority to declare a major incident after hours, or confusion between the CISO and IT operations director
- Downtime isolation decisions made without a documented patient safety threshold or CMO sign-off
- Unclear legal position on ransom payment, sanctions screening and whether law enforcement has been consulted before any payment decision
- No pre-approved holding statements for media, patients and staff, leading to inconsistent messages
- Notification clocks under HIPAA and state law not mapped to incident timelines, and presumption of breach not defined
- Insurer notice requirements and approved vendor panel not known to the executive team, creating risk of uncovered costs
- Backup integrity testing not defined, with no owner for certifying clean restores and no known last-good backup date
- Restoration priorities not agreed in advance across clinical, billing and payroll systems
- Manual downtime procedures not rehearsed for clinics and the emergency department
- Executive decision log and follow-up ownership not established, delaying lessons learned

## Validation report

- ATT&CK version: Enterprise v20.0
- Techniques accepted: 9
- Techniques remapped: 0
- References rejected: 0

*Fictional scenario for training purposes. Generated with IR Readiness Copilot.*
