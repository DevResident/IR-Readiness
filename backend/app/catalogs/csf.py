"""CSF 2.0 Categories and Subcategories used by this project, with verbatim NIST text."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel

from app.catalogs.paths import FRAMEWORKS_DIR

CSF_SUBSET_FILE = FRAMEWORKS_DIR / "nist" / "csf-2.0-subcategories-subset.json"
SUBCATEGORY_RE = re.compile(r"^(GV|ID|PR|DE|RS|RC)\.[A-Z]{2}-\d{2}$")


class CsfCategory(BaseModel):
    title: str
    description: str | None


class CsfCatalog(BaseModel):
    source: dict
    categories: dict[str, CsfCategory]
    subcategories: dict[str, str]

    def subcategory_text(self, subcategory_id: str) -> str | None:
        return self.subcategories.get(subcategory_id)

    def category_of(self, subcategory_id: str) -> str:
        return subcategory_id.split("-")[0]


def load_csf(path: Path = CSF_SUBSET_FILE) -> CsfCatalog:
    return CsfCatalog.model_validate(json.loads(path.read_text(encoding="utf-8")))


@lru_cache(maxsize=1)
def get_csf() -> CsfCatalog:
    return load_csf()
