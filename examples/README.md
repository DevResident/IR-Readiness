# Examples

Real outputs of IR Readiness Copilot, kept unedited so reviewers can judge the actual quality.
All organizations, people and events are fictional.

| File | What it is |
|---|---|
| `tabletop-ransomware-healthcare-executive.json` | Response of `POST /api/tabletop` for `{"industry": "healthcare", "org_size": "medium", "scenario": "ransomware", "audience": "executive"}`. Generated on 2026-11-05 with Claude Haiku 5.5. 9 ATT&CK techniques accepted, 0 remapped, 0 rejected. |
| `tabletop-ransomware-healthcare-executive.md` | The same exercise rendered with `scripts/render_tabletop_markdown.py`. |
| `ir-plan-fictional-meridian-logistics.md` | A fictional IR plan for a logistics company, written for this project. It is intentionally incomplete (for example, no regulatory notification duties, no BCP/DRP link, no exercises) so the assessment has real gaps to find. |

The JSON file is also the fixture for demo mode (`LLM_PROVIDER=demo`), which lets the app run without an API key.
A test checks that the Markdown file stays in sync with the JSON.
