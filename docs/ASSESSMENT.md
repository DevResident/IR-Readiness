# IR Plan Readiness Assessment: method

Module 1 checks an uploaded incident response plan against
[`frameworks/checklists/ir-plan-readiness.json`](../frameworks/checklists/ir-plan-readiness.json):
23 controls, each with concrete elements to look for, a priority, and the CSF 2.0 Subcategories
and SP 800-61r3 table it relates to. The Subcategory text is stored verbatim in
[`frameworks/nist/csf-2.0-subcategories-subset.json`](../frameworks/nist/csf-2.0-subcategories-subset.json).

## Mapping caveat

The `IRP-xx` IDs belong to this project. Mapping a control to a CSF Subcategory is this project's
judgment, not an official NIST crosswalk. Only the CSF IDs and the SP 800-61r3 table references are
framework identifiers, and tests check that every one of them exists in the stored subset.

## Per-control result

| Status | Meaning |
|---|---|
| `met` | The plan addresses all the elements in `look_for`. |
| `partial` | The plan addresses some elements, or mentions the topic without enough detail to act on. |
| `missing` | The plan does not address the control. |

`met` and `partial` need a quote from the plan. The quote is checked against the extracted document
text by deterministic code. If it is not found, the evidence is marked `UNVERIFIED` and the control
is downgraded one level (`met` → `partial`, `partial` → `missing`), because a claim with no
verifiable evidence must not raise the score.

## Score

Each priority has a weight: critical = 3, high = 2, medium = 1. Each status earns credit:
met = 1, partial = 0.5, missing = 0.

```
score    = 100 × Σ(weight × credit) / Σ(weight)
coverage = 100 × (controls that are met or partial) / (all controls)
```

The score answers "how ready is the plan, with critical gaps counting more". Coverage answers
"how much of the checklist the plan touches at all". A plan can have high coverage and a low score
when it mentions many topics only superficially.

## Upload handling

`POST /api/assessment/document` accepts PDF, DOCX, Markdown or plain text, up to 5 MB.

| Threat | Defense |
|---|---|
| Huge request bodies | `BodySizeLimitMiddleware` rejects them by Content-Length before parsing (413), and rejects uploads without a declared length (411). |
| Renamed files (`malware.exe` → `plan.pdf`) | The extension must be allowed and the content must match it (`%PDF-`, ZIP header, no NUL bytes in text). |
| DOCX zip bombs | Entry count and total uncompressed size are checked before decompressing. |
| XML entity attacks in DOCX | `word/document.xml` is parsed with `defusedxml`. |
| Very long PDFs or texts | At most 150 pages are read and 400,000 characters are kept; the response says when the text was truncated. |
| Sensitive data at rest or in logs | The file is processed in memory and discarded when the request ends. Logs record only the exception type, never document content (a test uploads a canary string and checks the logs). |

Scanned PDFs without a text layer are rejected with a clear message. OCR is out of scope.
