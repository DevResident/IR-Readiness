"""Render a saved tabletop JSON (an API response) as Markdown next to it.

Usage (from the repo root):
    python scripts/render_tabletop_markdown.py examples/tabletop-ransomware-healthcare-executive.json
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.modules.tabletop.markdown import render_markdown  # noqa: E402
from app.modules.tabletop.schemas import TabletopExercise  # noqa: E402


def main() -> None:
    for arg in sys.argv[1:]:
        src = Path(arg)
        exercise = TabletopExercise.model_validate(json.loads(src.read_text(encoding="utf-8")))
        out = src.with_suffix(".md")
        out.write_text(render_markdown(exercise), encoding="utf-8")
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
