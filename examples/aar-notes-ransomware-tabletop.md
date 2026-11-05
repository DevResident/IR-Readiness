Facilitator notes: Harbor Valley Community Health System, executive ransomware tabletop
Date: 2026-11-04. Duration: 90 minutes. Scenario: examples/tabletop-ransomware-healthcare-executive.json
Participants: CEO, CISO (IR lead), IT Operations Director, CMO, General Counsel, Communications Director, Business Continuity Owner, insurer representative (role-played by the facilitator). Fictional organization.

Inject 1 (T+0h, phishing report and script alert)
- CISO said the analyst would treat it as a security event and escalate only if a second host showed activity. No written criteria for declaring an incident; CISO and IT Ops Director disagreed on who declares.
- Help desk would call the security on-call phone. Good: everyone knew the on-call number.
- Nobody knew how quickly mail logs could be searched for the same email. IT Ops estimated "half a day".

Inject 2 (T+2h, credential theft, odd-hour admin logins)
- CISO wanted to reset all privileged credentials immediately. IT Ops warned the billing service account would break overnight claims processing. Decision took 12 minutes and ended with "reset admins now, service account after hours".
- General Counsel asked whether the insurer had been notified. Nobody knew the policy's notice deadline. Finance holds the policy and was not in the room.
- Forensics retainer: CISO believes there is one through the insurer panel but could not name the firm.

Inject 3 (T+4h, lateral movement, isolation decision)
- Strongest discussion of the day. CMO asked for 30 minutes to move clinics to downtime procedures before isolating the scheduling system. CEO approved isolating the scheduling system but not the whole clinical network.
- No one could say who has the authority to take a clinical system offline after hours if the CEO cannot be reached.
- Downtime procedures exist for the EHR but the clinic managers have not practiced them this year.

Inject 4 (T+6h, data in outside cloud storage, reporter email)
- Communications Director drafted a holding statement in the room in about 10 minutes. Legal edited it. Good teamwork.
- General Counsel said HIPAA breach notification "has a 60-day clock" but was not sure when the clock starts or which state laws apply. No notification matrix exists.
- No one owned the reporter's email until the CEO assigned it to Communications.

Inject 5 (T+8h, encryption and backup deletion)
- IT Ops said backups are "immutable" but then said the last restore test was "before the migration", about 14 months ago.
- CMO escalated ED patient safety immediately and proposed diversion criteria. Good.
- The team did not agree on whether this was now a "major incident"; the plan has no severity levels.

Inject 6 (Day 2, ransom deadline, leak site)
- CEO said "we don't pay" but General Counsel pointed out there is no board-approved position and no process for sanctions screening. The group agreed the decision would go to the board chair, but there is no documented path to reach the board quickly.
- Law enforcement: nobody knew who the contact at the FBI field office is.

Inject 7 (Day 3, restoration trade-offs)
- Restoration priority was debated for 15 minutes. Clinical wanted EHR interfaces first, Finance (by proxy) wanted billing. No pre-agreed restoration order exists.
- IT Ops could not say who signs off that a restored system is clean.

Hot wash
- What went well: fast escalation from the help desk, CMO's patient safety leadership, quick holding statement.
- What to fix: decision authority after hours, notification deadlines, restore testing, restoration priorities, insurer and forensics contacts.
