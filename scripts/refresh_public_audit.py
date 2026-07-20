#!/usr/bin/env python3
"""Refresh publication hashes without rewriting frozen experiment receipts."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "results" / "public_audit.json"


def publication_files() -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        text=True,
    )
    files = []
    for relative in output.splitlines():
        path = ROOT / relative
        if not path.is_file() or path == AUDIT_PATH or ".DS_Store" in path.parts:
            continue
        files.append(path)
    return sorted(files)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    audit = json.loads(AUDIT_PATH.read_text())
    audit["publication_refreshed_utc"] = datetime.now(timezone.utc).isoformat()
    audit["source_sha256"] = {
        str(path.relative_to(ROOT)): sha256(path) for path in publication_files()
    }
    audit["publication"].update(
        {
            "narrative": "difference_contact_return_reentry_changed_future",
            "current_pc_carrier_evidence": "locally_verified_public_bundle_pending",
        }
    )
    AUDIT_PATH.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n")
    print(f"PASS publication hashes={len(audit['source_sha256'])}")


if __name__ == "__main__":
    main()
