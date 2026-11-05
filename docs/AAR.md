# After-Action Report: method

`POST /api/aar` turns exercise or incident notes (50 to 30,000 characters) into an After-Action Report.

| Part | How it is produced |
|---|---|
| Executive summary, scope, gaps | Written by the model from the notes. |
| Observations (strengths and areas for improvement) | Written by the model, each with an 800-61r3 phase, an optional CSF 2.0 category and a quote from the notes. Code checks the quote against the notes and flags it **UNVERIFIED** if it is not found. Unlike the plan assessment, flagged observations are kept, because an AAR is a narrative a person reviews before sharing. |
| Recommendations | Written by the model with a priority, a timeframe (30, 90 or 180 days), a suggested owner as a role, and links to the observations they address. Code drops links to observation IDs that do not exist, rejects unknown CSF categories, and ranks recommendations by priority, then timeframe. |

The notes are untrusted text: the same layered prompt-injection defenses as the assessment apply
(wrapped in `<notes>` with tags neutralized, treated as data by the system prompt, claims verified by code).

Exports: `POST /api/aar/markdown` and `POST /api/aar/docx` take a report returned by `POST /api/aar`.
For PDF, print the Markdown or DOCX, or use the browser's print dialog from the UI.
