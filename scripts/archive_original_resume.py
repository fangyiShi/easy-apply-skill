"""Archive an uploaded source resume into an Easy Apply workspace unchanged."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def archive_original_resume(workspace: str | Path, source_file: str | Path) -> dict[str, str]:
    root = Path(workspace).expanduser().resolve()
    source = Path(source_file).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Missing uploaded resume: {source}")

    destination_dir = root / "profile" / "original-resumes"
    destination_dir.mkdir(parents=True, exist_ok=True)
    source_hash = sha256_file(source)
    destination = destination_dir / source.name

    if destination.exists() and sha256_file(destination) == source_hash:
        status = "already_archived"
    else:
        if destination.exists():
            counter = 2
            while True:
                candidate = destination_dir / f"{source.stem}-{counter}{source.suffix}"
                if not candidate.exists():
                    destination = candidate
                    break
                if sha256_file(candidate) == source_hash:
                    destination = candidate
                    status = "already_archived"
                    break
                counter += 1
            else:  # pragma: no cover - loop always exits via break
                raise RuntimeError("Could not choose an archive filename")

        if not destination.exists():
            shutil.copy2(source, destination)
            if sha256_file(destination) != source_hash:
                destination.unlink(missing_ok=True)
                raise RuntimeError("Archived resume failed SHA-256 verification")
            status = "archived"

    return {
        "status": status,
        "source_name": source.name,
        "path": destination.relative_to(root).as_posix(),
        "sha256": source_hash,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive one uploaded resume without changing its bytes")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--file", required=True)
    args = parser.parse_args()
    try:
        result = archive_original_resume(args.workspace, args.file)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"ok": True, **result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
