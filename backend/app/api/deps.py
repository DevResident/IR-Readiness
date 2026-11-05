"""FastAPI dependencies. Tests override ``get_llm`` with a fake model."""

from functools import lru_cache

from app.catalogs.attack import get_catalog
from app.catalogs.checklists import get_checklist
from app.catalogs.csf import get_csf
from app.catalogs.ir_lifecycle import get_ir_lifecycle
from app.catalogs.scenarios import get_scenarios
from app.core.config import get_settings
from app.llm.base import StructuredLLM
from app.llm.claude import ClaudeStructuredLLM
from app.llm.demo import DemoStructuredLLM, load_demo_plan, load_demo_tabletop
from app.modules.assessment.service import AssessmentService
from app.modules.tabletop.service import TabletopService


@lru_cache(maxsize=1)
def get_llm() -> StructuredLLM:
    settings = get_settings()
    if settings.llm_provider == "demo":
        return DemoStructuredLLM.default()
    return ClaudeStructuredLLM.from_settings(settings)


class _LazyLLM:
    """Creates the real client on first use, so a missing API key only fails the
    requests that actually need the model (and only after input validation)."""

    def generate(self, *, system, prompt, schema):
        return get_llm().generate(system=system, prompt=prompt, schema=schema)


DEMO_NOTICE = (
    "Demo mode: this is a pre-generated example. Your form inputs were not used; "
    "the request shown is the one this example was generated for."
)


def get_tabletop_service() -> TabletopService:
    if get_settings().llm_provider == "demo":
        return TabletopService(
            _LazyLLM(), get_catalog(), get_ir_lifecycle(), get_scenarios(),
            notice=DEMO_NOTICE, fixed_request=_demo_request(),
        )
    return TabletopService(_LazyLLM(), get_catalog(), get_ir_lifecycle(), get_scenarios())


@lru_cache(maxsize=1)
def _demo_request():
    return load_demo_tabletop().request


DEMO_ASSESSMENT_NOTICE = (
    "Demo mode: this is a pre-generated assessment of the fictional Meridian Freight Logistics plan "
    "in examples/. Your uploaded file was validated but not assessed."
)


def get_assessment_service() -> AssessmentService:
    if get_settings().llm_provider == "demo":
        return AssessmentService(
            _LazyLLM(), get_checklist(), get_csf(),
            notice=DEMO_ASSESSMENT_NOTICE, fixed_document=_demo_plan(),
        )
    return AssessmentService(_LazyLLM(), get_checklist(), get_csf())


@lru_cache(maxsize=1)
def _demo_plan():
    return load_demo_plan()
