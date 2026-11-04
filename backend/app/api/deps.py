"""FastAPI dependencies. Tests override ``get_llm`` with a fake model."""

from functools import lru_cache

from app.catalogs.attack import get_catalog
from app.catalogs.ir_lifecycle import get_ir_lifecycle
from app.catalogs.scenarios import get_scenarios
from app.core.config import get_settings
from app.llm.base import StructuredLLM
from app.llm.claude import ClaudeStructuredLLM
from app.modules.tabletop.service import TabletopService


@lru_cache(maxsize=1)
def get_llm() -> StructuredLLM:
    return ClaudeStructuredLLM.from_settings(get_settings())


class _LazyLLM:
    """Creates the real client on first use, so a missing API key only fails the
    requests that actually need the model (and only after input validation)."""

    def generate(self, *, system, prompt, schema):
        return get_llm().generate(system=system, prompt=prompt, schema=schema)


def get_tabletop_service() -> TabletopService:
    return TabletopService(_LazyLLM(), get_catalog(), get_ir_lifecycle(), get_scenarios())
