"""Deterministic validation for generated Easy Apply cover letters."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from lib.config import load_workspace_config
from lib.pdf_utils import PdfInspectionError, extract_text, page_count
from lib.text_scan import find_excluded_terms


PLACEHOLDER_RE = re.compile(r"<[^>\n]+>")


def check_letter(workspace: str | Path, tex_file: str | Path, pdf_file: str | Path) -> dict[str, object]:
    config = load_workspace_config(workspace)
    tex_path = Path(tex_file).expanduser().resolve()
    pdf_path = Path(pdf_file).expanduser().resolve()
    tex = tex_path.read_text(encoding="utf-8")

    errors: list[str] = []
    warnings: list[str] = []

    if "% Tailored for:" not in tex:
        warnings.append("Missing `% Tailored for:` metadata comment")
    if "% file_slug:" not in tex:
        warnings.append("Missing `% file_slug:` metadata comment")

    placeholders = sorted(set(PLACEHOLDER_RE.findall(tex)))
    if placeholders:
        errors.append(f"Unresolved placeholders: {', '.join(placeholders[:10])}")

    resume_cfg = config.get("resume") if isinstance(config.get("resume"), dict) else {}
    excluded = resume_cfg.get("exclude", []) if isinstance(resume_cfg, dict) else []
    excluded = [str(value) for value in excluded if str(value).strip()]
    hits = find_excluded_terms(tex, excluded)
    if hits:
        errors.append(f"Excluded terms found: {', '.join(hits)}")

    try:
        pages = page_count(pdf_path)
        if pages > 1:
            warnings.append(f"Cover letter is {pages} pages; review whether the length is intentional")
    except PdfInspectionError as exc:
        errors.append(str(exc))
        pages = None

    try:
        pdf_text = extract_text(pdf_path)
        if len(pdf_text.strip()) < 100:
            errors.append("PDF contains too little selectable text; inspect rendering")
    except PdfInspectionError as exc:
        warnings.append(str(exc))

    # Style preferences such as dash use or paragraph count are user-specific and
    # intentionally not enforced here. AI semantic review handles truth/narrative.
    return {"ok": not errors, "errors": errors, "warnings": warnings, "pages": pages}


def main() -> int:
    parser = argparse.ArgumentParser(description="Check an Easy Apply cover letter")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--tex", required=True)
    parser.add_argument("--pdf", required=True)
    args = parser.parse_args()
    try:
        result = check_letter(args.workspace, args.tex, args.pdf)
    except Exception as exc:
        result = {"ok": False, "errors": [str(exc)], "warnings": []}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
