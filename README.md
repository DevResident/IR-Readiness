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
cp ../.env.example .env   # then set ANTHROPIC_API_KEY (only needed to call the model; tests never use it)
uvicorn app.main:app --reload
# then open http://127.0.0.1:8000/docs
```

Generate a tabletop exercise:

```bash
curl -s -X POST http://127.0.0.1:8000/api/tabletop \
  -H "Content-Type: application/json" \
  -d '{"industry":"healthcare","org_size":"medium","scenario":"ransomware","audience":"executive"}'
```

## How a tabletop is generated

1. The request contains only enumerated values (industry, size, scenario, audience), so no free text reaches the prompt.
2. The prompt is built from the scenario template, the NIST SP 800-61r3 phases and a fixed list of CSF 2.0 categories.
3. Claude returns JSON constrained to the `TabletopDraft` schema (structured outputs); the SDK also validates lengths and list sizes client-side. Invalid or truncated output is retried once with the validation error as feedback.
4. Every ATT&CK technique ID is checked against the pinned v20.0 catalog: unknown IDs are dropped, revoked IDs are replaced by MITRE's official successor, and names/URLs come from the catalog. Unknown CSF categories are removed.
5. The response includes a `validation` report listing everything that was dropped, remapped or flagged.

## Regenerating the ATT&CK subset

```bash
python scripts/build_attack_subset.py --version 20.0
```

The subset in `frameworks/attack/` is generated from [mitre-attack/attack-stix-data](https://github.com/mitre-attack/attack-stix-data); its source URL and SHA-256 are recorded in the file.
