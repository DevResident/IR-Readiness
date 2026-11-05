from pathlib import Path

# backend/app/catalogs/paths.py -> repo root is three levels above "catalogs"
REPO_ROOT = Path(__file__).resolve().parents[3]
FRAMEWORKS_DIR = REPO_ROOT / "frameworks"
EXAMPLES_DIR = REPO_ROOT / "examples"
