"""Export an AfterActionReport as Markdown or DOCX. Only validated reports are exported."""

from __future__ import annotations

import io

from docx import Document
from docx.shared import Pt

from app.modules.aar.schemas import AfterActionReport, Observation

FOOTER = "Generated with IR Readiness Copilot. Review before distribution."


def _meta(report: AfterActionReport) -> str:
    kind = "Tabletop exercise" if report.event_type == "tabletop" else "Incident"
    return f"{kind}" + (f" · {report.event_date.isoformat()}" if report.event_date else "")


def _obs_line(o: Observation) -> str:
    csf = f" · CSF {o.csf_category} ({o.csf_title})" if o.csf_category else ""
    return f"Phase: {o.phase}{csf}"


def to_markdown(report: AfterActionReport) -> str:
    lines = [f"# {report.title}", "", f"*{_meta(report)}*", "", "## Executive summary", "", report.executive_summary,
             "", "## Scope", "", report.scope, ""]
    for heading, items in (("Strengths", report.strengths), ("Areas for improvement", report.areas_for_improvement)):
        lines += [f"## {heading}", ""]
        for o in items:
            lines += [f"### {o.id}. {o.title}", "", f"*{_obs_line(o)}*", "", o.detail, ""]
            if o.evidence_quote:
                flag = "" if o.evidence_verified else " **(UNVERIFIED: not found in the notes)**"
                lines += [f"> {o.evidence_quote}{flag}", ""]
    lines += ["## Gaps", "", *[f"- {g}" for g in report.gaps], "", "## Recommendations", "",
              "| # | Recommendation | Priority | Timeframe | Suggested owner | Addresses |",
              "|---|---|---|---|---|---|"]
    for r in report.recommendations:
        cell = f"**{r.title}**: {r.action}".replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {r.rank} | {cell} | {r.priority} | {r.timeframe} | {r.suggested_owner} | "
                     f"{', '.join(r.addresses) or '-'} |")
    lines += ["", f"*{FOOTER}*", ""]
    return "\n".join(lines)


def to_docx(report: AfterActionReport) -> bytes:
    doc = Document()
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(11)
    doc.add_heading(report.title, level=0)
    doc.add_paragraph(_meta(report)).runs[0].italic = True
    doc.add_heading("Executive summary", level=1)
    doc.add_paragraph(report.executive_summary)
    doc.add_heading("Scope", level=1)
    doc.add_paragraph(report.scope)
    for heading, items in (("Strengths", report.strengths), ("Areas for improvement", report.areas_for_improvement)):
        doc.add_heading(heading, level=1)
        for o in items:
            doc.add_heading(f"{o.id}. {o.title}", level=2)
            doc.add_paragraph(_obs_line(o)).runs[0].italic = True
            doc.add_paragraph(o.detail)
            if o.evidence_quote:
                p = doc.add_paragraph(style="Intense Quote")
                p.add_run(o.evidence_quote)
                if not o.evidence_verified:
                    p.add_run("  (UNVERIFIED: not found in the notes)").bold = True
    doc.add_heading("Gaps", level=1)
    for g in report.gaps:
        doc.add_paragraph(g, style="List Bullet")
    doc.add_heading("Recommendations", level=1)
    table = doc.add_table(rows=1, cols=6)
    table.style = "Light Grid Accent 1"
    for cell, text in zip(table.rows[0].cells, ["#", "Recommendation", "Priority", "Timeframe", "Owner", "Addresses"]):
        cell.text = text
    for r in report.recommendations:
        cells = table.add_row().cells
        cells[0].text = str(r.rank)
        cells[1].text = f"{r.title}: {r.action}"
        cells[2].text = r.priority
        cells[3].text = r.timeframe
        cells[4].text = r.suggested_owner
        cells[5].text = ", ".join(r.addresses) or "-"
    doc.add_paragraph()
    doc.add_paragraph(FOOTER).runs[0].italic = True
    out = io.BytesIO()
    doc.save(out)
    return out.getvalue()
