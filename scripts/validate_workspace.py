"""Validate an Easy Apply user workspace without mutating it."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from lib.config import ConfigError, load_workspace_config
from lib.profile import read_profile


SUPPORTED_SCHEMA_VERSIONS = {1}
REQUIRED_PROFILE_HEADINGS = {
    "## Basic Information",
    "## Job Search Background",
    "## Work Experience",
    "## Projects",
    "## Education",
    "## Skills",
    "## Certifications",
    "## Writing and Application Preferences",
}
REQUIRED_WORKSPACE_DIRS = (
    "profile/original-resumes",
    "profile/resume-templates",
    "sources",
    "artefacts/resume",
    "artefacts/resume-pdf",
    "artefacts/cover-letter",
    "artefacts/cover-letter-pdf",
    "artefacts/archive",
    "state/runs",
)
REQUIRED_NOTION_PROPERTIES = {
    "Position": "title",
    "Company": "rich_text",
    "Location": "rich_text",
    "URL": "url",
    "Platform": "multi_select",
    "Priority": "select",
    "Cover Letter": "checkbox",
    "Appendix": "rich_text",
    "File Slug": "rich_text",
    "Status": "status",
    "Submitted Materials": "files",
}


def _normalize_type(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def validate_notion_schema_snapshot(path: str | Path) -> tuple[list[str], list[str]]:
    """Validate a connector-exported schema snapshot.

    Accepted shape is either ``{"properties": {name: {"type": ...}}}`` or a
    direct mapping ``{name: "type"}``. This keeps the local validator connector-
    agnostic while allowing the runtime to export its observed schema for checks.
    """

    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    properties = raw.get("properties", raw) if isinstance(raw, dict) else {}
    errors: list[str] = []
    warnings: list[str] = []

    for name, expected_type in REQUIRED_NOTION_PROPERTIES.items():
        if name not in properties:
            errors.append(f"Notion property missing: {name}")
            continue
        value = properties[name]
        if isinstance(value, dict):
            actual = value.get("type")
        else:
            actual = value
        if not isinstance(actual, str):
            warnings.append(f"Could not determine Notion type for property: {name}")
            continue
        if _normalize_type(actual) != expected_type:
            errors.append(f"Notion property {name!r} has type {actual!r}; expected {expected_type!r}")

    return errors, warnings


def validate_workspace(
    workspace: str | Path,
    *,
    skill_root: str | Path | None = None,
    notion_schema_json: str | Path | None = None,
    allow_no_notion: bool = False,
    check_tools: bool = False,
) -> dict[str, Any]:
    root = Path(workspace).expanduser().resolve()
    skill = Path(skill_root).expanduser().resolve() if skill_root else Path(__file__).resolve().parents[1]
    errors: list[str] = []
    warnings: list[str] = []
    external_checks: list[str] = []

    try:
        config = load_workspace_config(root)
    except ConfigError as exc:
        return {"ok": False, "errors": [str(exc)], "warnings": [], "external_checks": []}

    version = config.get("schema_version")
    if version not in SUPPORTED_SCHEMA_VERSIONS:
        errors.append(f"Unsupported schema_version: {version!r}; supported: {sorted(SUPPORTED_SCHEMA_VERSIONS)}")

    for relative in REQUIRED_WORKSPACE_DIRS:
        if not (root / relative).is_dir():
            errors.append(f"Required workspace directory missing: {relative}")

    try:
        profile_text = read_profile(root)
        for heading in REQUIRED_PROFILE_HEADINGS:
            if heading not in profile_text:
                errors.append(f"Required profile section missing: {heading}")
    except FileNotFoundError as exc:
        errors.append(str(exc))

    role_families = config.get("role_families", {})
    if not isinstance(role_families, dict) or not role_families:
        errors.append("At least one `role_families` template mapping is required")
    else:
        for role, filename in role_families.items():
            if not isinstance(filename, str) or not filename.strip():
                errors.append(f"Invalid template filename for role family {role!r}")
                continue
            template = root / "profile" / "resume-templates" / filename
            if not template.is_file():
                errors.append(f"Configured resume template not found for {role!r}: {template}")

    search = config.get("search", {})
    if not isinstance(search, dict):
        errors.append("`search` must be a mapping")
    else:
        keywords = search.get("keywords")
        if not isinstance(keywords, list) or not any(str(item).strip() for item in keywords):
            errors.append("`search.keywords` must contain at least one keyword")

        configured_sources = search.get("configured_sources", {})
        if not isinstance(configured_sources, dict):
            errors.append("`search.configured_sources` must be a mapping")
        else:
            for source in configured_sources:
                source_name = str(source).strip().lower()
                workspace_adapter = root / "sources" / f"{source_name}.md"
                builtin_adapter = skill / "references" / "job-search" / "sources" / f"{source_name}.md"
                if not workspace_adapter.is_file() and not builtin_adapter.is_file():
                    errors.append(f"Configured source has no adapter: {source_name}")

    notion = config.get("notion", {})
    notion_id = notion.get("data_source_id") if isinstance(notion, dict) else None
    if not notion_id:
        if allow_no_notion:
            warnings.append("Notion data_source_id is not configured")
        else:
            errors.append("Notion data_source_id is not configured")

    if notion_schema_json:
        schema_errors, schema_warnings = validate_notion_schema_snapshot(notion_schema_json)
        errors.extend(schema_errors)
        warnings.extend(schema_warnings)
    elif notion_id:
        external_checks.append(
            "Runtime must verify the configured Notion data source is reachable and matches references/notion/schema.md."
        )

    if check_tools:
        if shutil.which("pdflatex") is None:
            errors.append("pdflatex is not available on PATH")
        if shutil.which("python") is None and shutil.which("py") is None:
            warnings.append("Could not locate a standard Python launcher on PATH")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "external_checks": external_checks,
        "workspace": str(root),
        "schema_version": version,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Easy Apply workspace")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--skill-root")
    parser.add_argument("--notion-schema-json")
    parser.add_argument("--allow-no-notion", action="store_true")
    parser.add_argument("--check-tools", action="store_true")
    args = parser.parse_args()

    try:
        result = validate_workspace(
            args.workspace,
            skill_root=args.skill_root,
            notion_schema_json=args.notion_schema_json,
            allow_no_notion=args.allow_no_notion,
            check_tools=args.check_tools,
        )
    except Exception as exc:
        result = {"ok": False, "errors": [str(exc)], "warnings": [], "external_checks": []}

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
