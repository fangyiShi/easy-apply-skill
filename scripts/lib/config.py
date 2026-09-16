"""Workspace configuration loading helpers.

The public configuration contract lives in workspace-scaffold/easy-apply.yaml.
This module intentionally performs only lightweight loading and top-level checks;
full validation belongs in validate_workspace.py.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class ConfigError(ValueError):
    """Raised when the Easy Apply workspace configuration cannot be loaded."""


def load_workspace_config(workspace: str | Path) -> dict[str, Any]:
    """Load ``easy-apply.yaml`` from a workspace directory.

    PyYAML is deliberately treated as a runtime dependency rather than silently
    implementing a partial YAML parser. A clear error is raised when it is not
    available.
    """

    workspace_path = Path(workspace).expanduser().resolve()
    config_path = workspace_path / "easy-apply.yaml"

    if not config_path.is_file():
        raise ConfigError(f"Missing workspace config: {config_path}")

    try:
        import yaml  # type: ignore
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise ConfigError(
            "PyYAML is required to read easy-apply.yaml. Install it with `pip install pyyaml`."
        ) from exc

    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except Exception as exc:  # PyYAML exposes several parser exception types
        raise ConfigError(f"Could not parse {config_path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ConfigError(f"Workspace config must be a YAML mapping: {config_path}")

    schema_version = raw.get("schema_version")
    if not isinstance(schema_version, int):
        raise ConfigError("easy-apply.yaml must contain an integer `schema_version`.")

    return raw
