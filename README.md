# IR Readiness Copilot

> Work in progress. See [docs/PLAN.md](docs/PLAN.md) for the roadmap.

An AI-assisted toolkit that helps consultants prepare an organization **before** an incident:

1. **IR Plan Readiness Assessment**: evaluates an incident response plan against a checklist derived from NIST SP 800-61 Rev. 3 and the Respond/Recover functions of NIST CSF 2.0, with evidence quotes verified against the source document.
2. **Tabletop Exercise Generator**: builds scenario narratives, injects, and facilitator guides, with every inject mapped to MITRE ATT&CK techniques that are validated against an official, pinned ATT&CK release.
3. **After-Action Report**: turns exercise notes into a structured AAR with prioritized recommendations.

## Core design principle

The LLM suggests; deterministic code verifies. Framework identifiers (ATT&CK technique IDs, CSF subcategories) and evidence quotes are always checked against local data or the uploaded document before they are shown to the user.

## Running the backend (current state)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python -m pytest -q
uvicorn app.main:app --reload
# then open http://127.0.0.1:8000/docs
```

## Regenerating the ATT&CK subset

```bash
python scripts/build_attack_subset.py --version 20.0
```

The subset in `frameworks/attack/` is generated from [mitre-attack/attack-stix-data](https://github.com/mitre-attack/attack-stix-data); its source URL and SHA-256 are recorded in the file.
