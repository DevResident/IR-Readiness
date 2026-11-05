# Examples

Real outputs of IR Readiness Copilot, kept unedited so reviewers can judge the actual quality.
All organizations, people and events are fictional.

| File | What it is |
|---|---|
| `tabletop-ransomware-healthcare-executive.json` | Response of `POST /api/tabletop` for `{"industry": "healthcare", "org_size": "medium", "scenario": "ransomware", "audience": "executive"}`. Generated on 2026-11-05 with Claude Haiku 5.5. 9 ATT&CK techniques accepted, 0 remapped, 0 rejected. |
| `tabletop-ransomware-healthcare-executive.md` | The same exercise rendered with `scripts/render_tabletop_markdown.py`. |
| `aar-notes-ransomware-tabletop.md` | Fictional facilitator notes from running the ransomware tabletop above, written as realistic input for the After-Action Report generator. |
| `aar-ransomware-tabletop.md` | After-Action Report generated from those notes on 2026-11-05 with Claude Haiku 5.5, exported from the app as Markdown. 4 strengths, 15 areas for improvement, 12 gaps, 12 ranked recommendations. All 19 quotes verified against the notes; no CSF category rejected, no dangling links. |
| `aar-ransomware-tabletop.json` | The same report as `AfterActionReport` JSON, rebuilt from the Markdown with `scripts/aar_markdown_to_json.py` (the AAR page had no JSON export yet). The script re-runs the real validation against the notes and refuses to write unless the JSON renders back to the identical Markdown. The only field the Markdown cannot carry, a recommendation's optional CSF category, is empty. |
| `ir-plan-fictional-meridian-logistics.md` | A fictional IR plan for a logistics company, written for this project. It is intentionally incomplete (for example, no regulatory notification duties, no BCP/DRP link, no exercises) so the assessment has real gaps to find. |
| `ir-plan-fictional-meridian-logistics.assessment.json` | Response of `POST /api/assessment` for that plan, generated on 2026-11-05 with Claude Haiku 5.5. Score 66.3, coverage 87%: 8 met, 12 partial, 3 missing. All 20 quotes verified against the plan. |

The three JSON files are also the fixtures for demo mode (`LLM_PROVIDER=demo`), which lets the app run without an API key.
Tests check that each Markdown file stays in sync with its JSON and that the fixtures pass today's validation unchanged.
