from pathlib import Path

# backend/app/catalogs/paths.py -> repo root is three levels above "catalogs"
FRAMEWORKS_DIR = Path(__file__).resolve().parents[3] / "frameworks"
