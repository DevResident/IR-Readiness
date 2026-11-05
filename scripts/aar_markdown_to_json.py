"""Rebuild a saved AAR JSON from an exported AAR Markdown file and the notes it came from.

The AAR page originally exported only Markdown and DOCX, so the first real run was saved
as Markdown. This script parses that Markdown back into the model's draft shape and runs it
through the real ``AARService.build_report`` against the original notes, so every quote is
re-verified in code. It then checks the round trip: rendering the rebuilt report must give
back the exact same Markdown, otherwise it refuses to write anything.

What the Markdown cannot carry: a recommendation's optional CSF category (not shown in the
table), so it is left empty.

Usage (from the repo root):
    python scripts/aar_markdown_to_json.py examples/aar-ransomware-tabletop.md \
        examples/aar-notes-ransomware-tabletop.md
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.api.deps import aar_csf_categories  # noqa: E402
from app.llm.demo import DemoStructuredLLM  # noqa: E402
from app.modules.aar.export import to_markdown  # noqa: E402
from app.modules.aar.schemas import AARDraft, AARRequest  # noqa: E402
from app.modules.aar.service import AARService  # noqa: E402

UNVERIFIED_FLAG = " **(UNVERIFIED: not found in the notes)**"
OBS_HEADING = re.compile(r"^### (O\d+)\. (.+)$")
OBS_META = re.compile(r"^\*Phase: (\w+)(?: · CSF ([A-Z]{2}\.[A-Z]{2}) \(.+\))?\*$")
CELL_SPLIT = re.compile(r"(?<!\\)\|")


def sections(md: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    current = "_head"
    for line in md.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            out[current] = []
        else:
            out.setdefault(current, []).append(line)
    return out


def paragraphs(lines: list[str]) -> list[str]:
    text = "\n".join(lines).strip()
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def observations(lines: list[str], kind: str) -> list[dict]:
    blocks: list[list[str]] = []
    for line in lines:
        if OBS_HEADING.match(line):
            blocks.append([line])
        elif blocks:
            blocks[-1].append(line)
    result = []
    for block in blocks:
        oid, title = OBS_HEADING.match(block[0]).groups()
        parts = paragraphs(block[1:])
        meta = OBS_META.match(parts[0])
        if not meta:
            raise ValueError(f"{oid}: unexpected metadata line {parts[0]!r}")
        quote = None
        if parts[-1].startswith("> "):
            quote = parts.pop()[2:].removesuffix(UNVERIFIED_FLAG)
        result.append({
            "id": oid, "kind": kind, "title": title, "phase": meta.group(1), "csf_category": meta.group(2),
            "detail": "\n\n".join(parts[1:]), "evidence_quote": quote,
        })
    return result


def recommendations(lines: list[str]) -> list[dict]:
    rows = [ln for ln in lines if ln.startswith("| ") and not ln.startswith("| #")]
    result = []
    for row in rows:
        cells = [c.strip() for c in CELL_SPLIT.split(row.strip())[1:-1]]
        _, rec, priority, timeframe, owner, addresses = cells
        m = re.match(r"^\*\*(.+?)\*\*: (.+)$", rec.replace("\\|", "|"))
        result.append({
            "title": m.group(1), "action": m.group(2), "priority": priority, "timeframe": timeframe,
            "suggested_owner": owner, "addresses": [a.strip() for a in addresses.split(",") if a.strip() != "-"],
        })
    return result


def parse(md: str) -> tuple[AARDraft, str, str | None]:
    s = sections(md)
    head = [ln for ln in s["_head"] if ln.strip()]
    title = head[0].removeprefix("# ").strip()
    meta = head[1].strip("*")
    event_type = "tabletop" if meta.startswith("Tabletop") else "incident"
    event_date = meta.split(" · ")[1] if " · " in meta else None
    draft = AARDraft.model_validate({
        "title": title,
        "executive_summary": "\n\n".join(paragraphs(s["Executive summary"])),
        "scope": "\n\n".join(paragraphs(s["Scope"])),
        "observations": observations(s.get("Strengths", []), "strength")
        + observations(s.get("Areas for improvement", []), "improvement"),
        "gaps": [ln[2:] for ln in s["Gaps"] if ln.startswith("- ")],
        "recommendations": recommendations(s["Recommendations"]),
    })
    return draft, event_type, event_date


def main() -> None:
    md_path, notes_path = Path(sys.argv[1]), Path(sys.argv[2])
    md = md_path.read_text(encoding="utf-8")
    draft, event_type, event_date = parse(md)
    request = AARRequest(notes=notes_path.read_text(encoding="utf-8"), event_type=event_type, event_date=event_date)
    report = AARService(DemoStructuredLLM({}), aar_csf_categories()).build_report(request, draft)
    if to_markdown(report) != md:
        sys.exit("round trip failed: the rebuilt report does not render to the same Markdown")
    out = md_path.with_suffix(".json")
    out.write_text(report.model_dump_json(indent=2) + "\n", encoding="utf-8")
    v = report.validation
    print(f"wrote {out}: {len(report.strengths)} strengths, {len(report.areas_for_improvement)} improvements, "
          f"{len(report.recommendations)} recommendations; unverified={v.unverified_observations} "
          f"rejected_csf={v.rejected_csf_categories} dropped_links={v.dropped_links}")


if __name__ == "__main__":
    main()
