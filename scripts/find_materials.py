"""Locate the complete current PDF material set for one Easy Apply job."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate_file_slug(file_slug: str) -> str:
    value = file_slug.strip()
    if not _SLUG_RE.fullmatch(value):
        raise ValueError(
            "file_slug must be lowercase letters/numbers separated by hyphens; "
            f"received: {file_slug!r}"
        )
    return value


def find_materials(workspace: str | Path, file_slug: str) -> list[Path]:
    root = Path(workspace).expanduser().resolve()
    slug = validate_file_slug(file_slug)

    candidates = [
        root / "artefacts" / "resume-pdf" / f"resume-{slug}.pdf",
        root / "artefacts" / "cover-letter-pdf" / f"cover-letter-{slug}.pdf",
    ]
    return [path for path in candidates if path.is_file() and path.stat().st_size > 0]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Find current Easy Apply PDFs for one file_slug")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--file-slug", required=True)
    parser.add_argument(
        "--require",
        choices=["any", "resume", "resume-and-letter"],
        default="any",
        help="Fail when the requested material set is incomplete.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        slug = validate_file_slug(args.file_slug)
        materials = find_materials(args.workspace, slug)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    names = {path.name for path in materials}
    resume_name = f"resume-{slug}.pdf"
    letter_name = f"cover-letter-{slug}.pdf"

    requirement_met = bool(materials)
    if args.require == "resume":
        requirement_met = resume_name in names
    elif args.require == "resume-and-letter":
        requirement_met = resume_name in names and letter_name in names

    payload = {
        "ok": requirement_met,
        "file_slug": slug,
        "materials": [str(path) for path in materials],
    }
    if not requirement_met:
        payload["error"] = f"Required material set not found: {args.require}"

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if requirement_met else 1


if __name__ == "__main__":
    raise SystemExit(main())
