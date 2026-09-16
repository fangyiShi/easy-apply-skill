"""Validate an Easy Apply user workspace without mutating it."""

from __future__ import annotations

import argparse
import importlib
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

from lib.config import ConfigError, load_workspace_config
from lib.profile import read_profile


SUPPORTED_SCHEMA_VERSIONS = {1, 2}
LAYOUT_INPUT_RE = re.compile(r"\\input\s*\{\s*resume-layout\.tex\s*\}")
ROLE_FAMILY_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
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


def _check_runtime_tools() -> tuple[list[str], list[str], dict[str, str]]:
    errors: list[str] = []
    warnings: list[str] = []
    details = {"python_executable": sys.executable, "python_version": sys.version.split()[0]}

    if sys.version_info < (3, 11):
        errors.append(f"Python 3.11+ is required; current interpreter is {sys.version.split()[0]}")
    if not sys.executable or not Path(sys.executable).is_file():
        errors.append(f"Current Python executable is not usable: {sys.executable!r}")
    try:
        yaml_module = importlib.import_module("yaml")
        if not hasattr(yaml_module, "safe_load"):
            raise ImportError("module does not provide safe_load")
    except ImportError:
        errors.append("PyYAML is not importable in the current Python environment")

    try:
        importlib.import_module("pypdf")
        has_pypdf = True
    except ImportError:
        has_pypdf = False
    has_pdf_fallback = shutil.which("pdfinfo") is not None and shutil.which("pdftotext") is not None
    if not has_pypdf and not has_pdf_fallback:
        errors.append("PDF inspection requires pypdf or both pdfinfo and pdftotext")
    if shutil.which("pdflatex") is None:
        errors.append("pdflatex is not available on PATH")

    return errors, warnings, details


def _validate_setup_state(
    root: Path,
    role_families: dict[str, Any],
    notion_enabled: bool,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    path = root / "state" / "setup.json"
    if not path.is_file():
        return ["Required setup state missing: state/setup.json"], warnings

    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Could not parse {path}: {exc}"], warnings
    if not isinstance(state, dict):
        return ["state/setup.json must contain a JSON object"], warnings

    if state.get("schema_version") != 1:
        errors.append("state/setup.json must use schema_version 1")
    if not isinstance(state.get("attachments"), dict):
        errors.append("Setup attachments state must be an object")

    if state.get("profile") != "confirmed":
        errors.append("Setup profile state must be `confirmed`")
    if state.get("resume_layout") != "confirmed":
        errors.append("Setup resume_layout state must be `confirmed`")

    template_states = state.get("role_family_templates")
    if not isinstance(template_states, dict):
        errors.append("Setup role_family_templates state must be an object")
    else:
        for role in role_families:
            if template_states.get(role) != "confirmed":
                errors.append(f"Role-family template is not confirmed: {role}")

    expected_notion_state = "confirmed" if notion_enabled else "skipped"
    if state.get("notion") != expected_notion_state:
        errors.append(f"Setup notion state must be `{expected_notion_state}`")

    return errors, warnings


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
    runtime_details: dict[str, str] = {}

    if check_tools:
        tool_errors, tool_warnings, runtime_details = _check_runtime_tools()
        errors.extend(tool_errors)
        warnings.extend(tool_warnings)

    try:
        config = load_workspace_config(root)
    except ConfigError as exc:
        errors.append(str(exc))
        return {
            "ok": False,
            "errors": errors,
            "warnings": warnings,
            "external_checks": external_checks,
            **runtime_details,
        }

    version = config.get("schema_version")
    if version not in SUPPORTED_SCHEMA_VERSIONS:
        errors.append(f"Unsupported schema_version: {version!r}; supported: {sorted(SUPPORTED_SCHEMA_VERSIONS)}")
    elif version == 1:
        warnings.append("schema_version 1 is deprecated; migrate the workspace to schema_version 2")

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

    if version == 2:
        layout = root / "profile" / "resume-layout.tex"
        if not layout.is_file():
            errors.append("Required canonical resume layout missing: profile/resume-layout.tex")

    role_families = config.get("role_families", {})
    if not isinstance(role_families, dict) or not role_families:
        errors.append("At least one `role_families` template mapping is required")
        role_families = {}
    else:
        used_templates: dict[str, str] = {}
        for role, filename in role_families.items():
            if not isinstance(role, str) or not ROLE_FAMILY_RE.fullmatch(role):
                errors.append(
                    f"Role-family key must use lowercase letters, numbers, hyphens or underscores: {role!r}"
                )
                continue
            if not isinstance(filename, str) or not filename.strip():
                errors.append(f"Invalid template filename for role family {role!r}")
                continue
            if Path(filename).name != filename or Path(filename).suffix.lower() != ".tex":
                errors.append(f"Role-family template must be one .tex filename for {role!r}: {filename!r}")
                continue
            filename_key = filename.casefold()
            if filename_key in used_templates:
                errors.append(
                    f"Role families {used_templates[filename_key]!r} and {role!r} share template {filename!r}; "
                    "each role family requires a distinct content template"
                )
            else:
                used_templates[filename_key] = role
            template = root / "profile" / "resume-templates" / filename
            if not template.is_file():
                errors.append(f"Configured resume template not found for {role!r}: {template}")
            elif version == 2:
                template_text = template.read_text(encoding="utf-8")
                if not LAYOUT_INPUT_RE.search(template_text):
                    errors.append(
                        f"Role-family template {filename!r} must load the canonical layout with "
                        r"\input{resume-layout.tex}"
                    )

    resume = config.get("resume", {})
    pages = resume.get("pages") if isinstance(resume, dict) else None
    if not isinstance(pages, int) or isinstance(pages, bool) or pages < 1:
        errors.append("`resume.pages` must be a positive integer explicitly confirmed by the user")

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
    if version == 2:
        notion_enabled = notion.get("enabled") if isinstance(notion, dict) else None
        if not isinstance(notion_enabled, bool):
            errors.append("`notion.enabled` must be true or false after setup asks the user")
            notion_enabled = False
        if notion_enabled and not notion_id:
            errors.append("Notion is enabled but data_source_id is not configured")
        if not notion_enabled and notion_id:
            warnings.append("Notion is disabled; configured data_source_id will not be used")
    else:
        notion_enabled = bool(notion_id)
        if not notion_id:
            if allow_no_notion:
                warnings.append("Notion data_source_id is not configured")
            else:
                errors.append("Notion data_source_id is not configured")

    if notion_enabled:
        if notion_schema_json:
            schema_errors, schema_warnings = validate_notion_schema_snapshot(notion_schema_json)
            errors.extend(schema_errors)
            warnings.extend(schema_warnings)
        elif notion_id:
            external_checks.append(
                "Runtime must verify the configured Notion data source is reachable and matches references/notion/schema.md."
            )
    elif notion_schema_json:
        warnings.append("Notion schema snapshot was provided but Notion is disabled")

    if version == 2:
        state_errors, state_warnings = _validate_setup_state(root, role_families, notion_enabled)
        errors.extend(state_errors)
        warnings.extend(state_warnings)

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "external_checks": external_checks,
        "workspace": str(root),
        "schema_version": version,
        **runtime_details,
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
