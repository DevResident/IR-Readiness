#!/usr/bin/env python3
"""Build a compact, local subset of MITRE ATT&CK Enterprise from the official STIX bundle.

Why this exists
---------------
The tabletop generator asks an LLM to map each inject to ATT&CK techniques. LLMs
sometimes produce IDs that do not exist, or that MITRE has revoked or deprecated.
We never trust those IDs: every ID is checked against this local file, which is
generated *only* from MITRE's official data, never written by hand.

Source: https://github.com/mitre-attack/attack-stix-data (official MITRE repo)

Usage
-----
    python scripts/build_attack_subset.py --version 20.0
    python scripts/build_attack_subset.py --version 20.0 --input path/to/enterprise-attack-20.0.json

Only the Python standard library is used, so the script runs without a virtualenv.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = REPO_ROOT / ".cache"
OUTPUT_DIR = REPO_ROOT / "frameworks" / "attack"
URL_TEMPLATE = (
    "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/"
    "enterprise-attack/enterprise-attack-{version}.json"
)


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {url} ...", file=sys.stderr)
    with urllib.request.urlopen(url, timeout=120) as resp, open(dest, "wb") as out:
        while chunk := resp.read(1 << 20):
            out.write(chunk)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def attack_id(obj: dict) -> str | None:
    """Return the ATT&CK ID (e.g. 'T1486') from a STIX object's external references."""
    for ref in obj.get("external_references", []):
        if ref.get("source_name") == "mitre-attack":
            return ref.get("external_id")
    return None


def attack_url(obj: dict) -> str | None:
    for ref in obj.get("external_references", []):
        if ref.get("source_name") == "mitre-attack":
            return ref.get("url")
    return None


def build_subset(bundle: dict) -> dict:
    objects = bundle["objects"]
    by_stix_id = {o["id"]: o for o in objects}

    tactics = {
        o["x_mitre_shortname"]: {"id": attack_id(o), "name": o["name"]}
        for o in objects
        if o["type"] == "x-mitre-tactic"
    }

    # MITRE records "technique A was replaced by technique B" as a relationship.
    revoked_by: dict[str, str] = {}
    for rel in objects:
        if rel["type"] == "relationship" and rel.get("relationship_type") == "revoked-by":
            src = by_stix_id.get(rel["source_ref"])
            dst = by_stix_id.get(rel["target_ref"])
            if src and dst and src["type"] == "attack-pattern":
                revoked_by[attack_id(src)] = attack_id(dst)

    techniques: dict[str, dict] = {}
    revoked: dict[str, dict] = {}
    deprecated: dict[str, dict] = {}

    for o in objects:
        if o["type"] != "attack-pattern":
            continue
        tid = attack_id(o)
        if not tid:
            continue
        if o.get("revoked"):
            revoked[tid] = {"name": o["name"], "revoked_by": revoked_by.get(tid)}
            continue
        if o.get("x_mitre_deprecated"):
            deprecated[tid] = {"name": o["name"]}
            continue
        techniques[tid] = {
            "name": o["name"],
            "tactics": sorted(p["phase_name"] for p in o.get("kill_chain_phases", [])),
            "is_subtechnique": bool(o.get("x_mitre_is_subtechnique")),
            "platforms": sorted(o.get("x_mitre_platforms", [])),
            "url": attack_url(o),
        }

    return {
        "tactics": dict(sorted(tactics.items())),
        "techniques": dict(sorted(techniques.items())),
        "revoked": dict(sorted(revoked.items())),
        "deprecated": dict(sorted(deprecated.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", required=True, help="ATT&CK release, e.g. 20.0")
    parser.add_argument("--input", type=Path, help="Use a local STIX bundle instead of downloading")
    args = parser.parse_args()

    url = URL_TEMPLATE.format(version=args.version)
    src = args.input or CACHE_DIR / f"enterprise-attack-{args.version}.json"
    if not src.exists():
        download(url, src)

    with open(src, encoding="utf-8") as f:
        bundle = json.load(f)

    subset = build_subset(bundle)
    output = {
        "source": {
            "name": "MITRE ATT&CK Enterprise",
            "version": args.version,
            "url": url,
            "sha256": sha256_of(src),
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        **subset,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"enterprise-attack-v{args.version}-subset.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=1, ensure_ascii=False)
        f.write("\n")

    print(
        f"Wrote {out_path.relative_to(REPO_ROOT)}: "
        f"{len(subset['techniques'])} active techniques, "
        f"{len(subset['revoked'])} revoked, {len(subset['deprecated'])} deprecated",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
