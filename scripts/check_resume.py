"""Deterministic validation for generated Easy Apply resumes."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from lib.config import load_workspace_config
from lib.pdf_utils import PdfInspectionError, bottom_whitespace_ratio, extract_text, page_count
from lib.profile import extract_profile_skills_from_workspace
from lib.text_scan import find_excluded_terms


HEADER_MARKERS = ("% Tailored for:", "% Base template:", "% Main changes:")
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>")
SECTION_RE = re.compile(r"\\section\{([^}]+)\}")


def _strip_latex(value: str) -> str:
    value = re.sub(r"\\textbf\{([^}]*)\}", r"\1", value)
    value = re.sub(r"\\[A-Za-z]+(?:\[[^]]*\])?\{([^}]*)\}", r"\1", value)
    value = value.replace("\\", " ")
    value = re.sub(r"[{}]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def _skills_section(tex: str) -> str:
    match = re.search(r"\\section\{SKILLS\}(.*?)(?=\\section\{|\\end\{document\})", tex, re.DOTALL | re.IGNORECASE)
    return match.group(1) if match else ""


def _listed_skills(tex: str) -> list[str]:
    section = _skills_section(tex)
    if not section:
        return []
    values: list[str] = []
    for raw_line in section.splitlines():
        line = _strip_latex(raw_line)
        if not line or line.startswith("%"):
            continue
        if ":" in line:
            line = line.split(":", 1)[1]
        for part in re.split(r"\s*[,;|]\s*", line):
            item = part.strip(" .")
            if item:
                values.append(item)
    return values


def _supported_skill(item: str, skills: list[str], aliases: dict[str, list[str]]) -> bool:
    key = item.casefold()
    for skill in skills:
        if key == skill.casefold():
            return True
        for alias in aliases.get(skill, []):
            if key == str(alias).casefold():
                return True
    return False


def check_resume(workspace: str | Path, tex_file: str | Path, pdf_file: str | Path) -> dict[str, object]:
    config = load_workspace_config(workspace)
    tex_path = Path(tex_file).expanduser().resolve()
    pdf_path = Path(pdf_file).expanduser().resolve()
    tex = tex_path.read_text(encoding="utf-8")

    errors: list[str] = []
    warnings: list[str] = []

    for marker in HEADER_MARKERS:
        if marker not in tex:
            errors.append(f"Missing resume header marker: {marker}")

    placeholders = sorted(set(PLACEHOLDER_RE.findall(tex)))
    if placeholders:
        errors.append(f"Unresolved placeholders: {', '.join(placeholders[:10])}")

    sections = {name.strip().upper() for name in SECTION_RE.findall(tex)}
    for required in ("SKILLS", "WORK EXPERIENCE", "PROJECTS", "EDUCATION"):
        if required not in sections:
            warnings.append(f"Standard section not found: {required}")

    resume_cfg = config.get("resume") if isinstance(config.get("resume"), dict) else {}
    excluded = resume_cfg.get("exclude", []) if isinstance(resume_cfg, dict) else []
    excluded = [str(value) for value in excluded if str(value).strip()]
    excluded_hits = find_excluded_terms(tex, excluded)
    if excluded_hits:
        errors.append(f"Excluded terms found: {', '.join(excluded_hits)}")

    skills = extract_profile_skills_from_workspace(workspace)
    aliases_raw = resume_cfg.get("skill_aliases", {}) if isinstance(resume_cfg, dict) else {}
    aliases = {
        str(key): [str(item) for item in value]
        for key, value in aliases_raw.items()
        if isinstance(value, list)
    } if isinstance(aliases_raw, dict) else {}
    listed = _listed_skills(tex)
    unsupported = [item for item in listed if not _supported_skill(item, skills, aliases)]
    if unsupported:
        warnings.append(
            "Skills-section entries not found in profile Skills/aliases; semantic review required: "
            + ", ".join(unsupported[:20])
        )

    target_pages = resume_cfg.get("pages") if isinstance(resume_cfg, dict) else None
    if not isinstance(target_pages, int) or isinstance(target_pages, bool) or target_pages < 1:
        errors.append("`resume.pages` must be a positive integer explicitly confirmed by the user")
    try:
        pages = page_count(pdf_path)
        if isinstance(target_pages, int) and pages != target_pages:
            errors.append(f"PDF page count is {pages}; configured target is {target_pages}")
    except PdfInspectionError as exc:
        errors.append(str(exc))
        pages = None

    try:
        pdf_text = extract_text(pdf_path)
        if len(pdf_text.strip()) < 100:
            errors.append("PDF contains too little selectable text; inspect rendering/ATS readability")
    except PdfInspectionError as exc:
        warnings.append(str(exc))

    whitespace = bottom_whitespace_ratio(pdf_path)
    if whitespace is not None and whitespace > 0.20:
        warnings.append(f"Last-page trailing whitespace is about {whitespace:.0%}; visually review document density")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "pages": pages,
        "bottom_whitespace_ratio": whitespace,
        "listed_skills": listed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check an Easy Apply resume")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--tex", required=True)
    parser.add_argument("--pdf", required=True)
    args = parser.parse_args()
    try:
        result = check_resume(args.workspace, args.tex, args.pdf)
    except Exception as exc:
        result = {"ok": False, "errors": [str(exc)], "warnings": []}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
