# Build plan

MVP in ~12 working days at 2–3 h/day. Priority: Module 2 (Tabletop Generator), then Module 1 (IR Plan Readiness Assessment), then Module 3 (After-Action Report).

## Stack

| Layer | Choice | Why |
|---|---|---|
| Backend | Python 3.12+ / FastAPI | Best ecosystem for document parsing (PDF/DOCX), first-class Anthropic SDK, Pydantic models double as LLM output schemas and API contracts. |
| LLM | Claude API (structured JSON output) | Schema-constrained output plus defensive parsing and post-validation. The model suggests, deterministic code verifies. |
| Frontend | React + Vite | Fast dev loop; no SSR needed for an internal consultant tool. |
| Frameworks | JSON files in `/frameworks` | Adding a framework is a data change, not a code change. ATT&CK is generated from MITRE's official STIX data, never hand-written. |
| Tests | pytest + FastAPI TestClient | LLM calls are mocked so tests are deterministic and free. |

## Repository layout

```
ir-readiness-copilot/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app, routes
│   │   ├── config.py          # settings from env (.env), secrets as SecretStr
│   │   ├── frameworks/        # loaders + validators for /frameworks data
│   │   ├── llm/               # Claude client wrapper, prompts, defensive JSON parsing   (day 3)
│   │   ├── tabletop/          # Module 2: schemas, service                                (days 2–3)
│   │   ├── assessment/        # Module 1: upload handling, extraction, scoring            (days 6–8)
│   │   └── aar/               # Module 3: AAR generation, PDF/DOCX export                 (days 9–10)
│   └── tests/
├── frameworks/
│   ├── attack/                # generated ATT&CK subset (pinned version)
│   ├── nist/                  # SP 800-61r3 / CSF 2.0 derived checklists and phase model
│   └── scenarios/             # tabletop scenario templates
├── frontend/                  # React + Vite                                              (day 4)
├── scripts/                   # data build scripts (e.g. build_attack_subset.py)
├── examples/                  # fictional IR plan + assessment, ransomware tabletop + AAR
└── docs/
```

## Day-by-day

| Day | Deliverable | Status |
|---|---|---|
| 1 | Repo skeleton, FastAPI health endpoint, ATT&CK v20.0 subset generated from MITRE STIX, technique validator + tests | done |
| 2 | Scenario templates (ransomware, BEC, insider, supply chain), IR phase model JSON (800-61r3 / CSF 2.0), Pydantic schemas for tabletop output | |
| 3 | Claude client wrapper (structured output, retries, defensive parsing), tabletop service with ATT&CK post-validation, `POST /api/tabletop`, tests with mocked LLM | |
| 4 | Frontend: tabletop form + rendered result, Markdown export | |
| 5 | Polish Module 2, ransomware tabletop in `/examples` | |
| 6 | Module 1: secure upload (type sniffing, size limit, delete after analysis), PDF/DOCX/MD text extraction, readiness checklist JSON | |
| 7 | Per-control evaluation, quote verification against the source text (UNVERIFIED on mismatch), scoring formula | |
| 8 | Module 1 UI, fictional IR plan + its assessment in `/examples` | |
| 9 | Module 3: notes → structured AAR with prioritized recommendations and suggested owners | |
| 10 | PDF/DOCX export, AAR example | |
| 11 | README (architecture diagram, pipeline, screenshots, limitations, roadmap), GitHub Actions CI | |
| 12 | Buffer, CV bullets, interview pitch | |
