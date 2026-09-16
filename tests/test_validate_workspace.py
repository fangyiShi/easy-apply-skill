from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_workspace import validate_workspace  # noqa: E402


class ValidateWorkspaceTests(unittest.TestCase):
    def copy_example(self, destination: Path) -> Path:
        workspace = destination / "workspace"
        shutil.copytree(ROOT / "examples" / "it-graduate", workspace)
        return workspace

    def update_config(self, workspace: Path, update) -> None:
        path = workspace / "easy-apply.yaml"
        config = yaml.safe_load(path.read_text(encoding="utf-8"))
        update(config)
        path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    def test_fictional_example_workspace_is_locally_valid(self) -> None:
        result = validate_workspace(ROOT / "examples" / "it-graduate", skill_root=ROOT)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["errors"], [])
        self.assertTrue(result["external_checks"])

    def test_page_target_must_be_explicit_positive_integer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = self.copy_example(Path(tmp))
            self.update_config(workspace, lambda config: config["resume"].update({"pages": None}))
            result = validate_workspace(workspace, skill_root=ROOT)
            self.assertFalse(result["ok"])
            self.assertTrue(any("resume.pages" in item for item in result["errors"]), result)

    def test_role_families_require_distinct_content_templates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = self.copy_example(Path(tmp))
            self.update_config(
                workspace,
                lambda config: config["role_families"].update({"dev": "resume-support.tex"}),
            )
            result = validate_workspace(workspace, skill_root=ROOT)
            self.assertFalse(result["ok"])
            self.assertTrue(any("share template" in item for item in result["errors"]), result)

    def test_role_template_must_load_canonical_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = self.copy_example(Path(tmp))
            template = workspace / "profile" / "resume-templates" / "resume-dev.tex"
            template.write_text(
                template.read_text(encoding="utf-8").replace(r"\input{resume-layout.tex}", ""),
                encoding="utf-8",
            )
            result = validate_workspace(workspace, skill_root=ROOT)
            self.assertFalse(result["ok"])
            self.assertTrue(any("canonical layout" in item for item in result["errors"]), result)

    def test_notion_can_be_explicitly_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = self.copy_example(Path(tmp))
            self.update_config(
                workspace,
                lambda config: config["notion"].update({"enabled": False, "data_source_id": None}),
            )
            setup_path = workspace / "state" / "setup.json"
            setup = json.loads(setup_path.read_text(encoding="utf-8"))
            setup["notion"] = "skipped"
            setup_path.write_text(json.dumps(setup, indent=2), encoding="utf-8")
            result = validate_workspace(workspace, skill_root=ROOT)
            self.assertTrue(result["ok"], result)
            self.assertEqual(result["external_checks"], [])

    def test_enabled_notion_requires_data_source_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = self.copy_example(Path(tmp))
            self.update_config(
                workspace,
                lambda config: config["notion"].update({"enabled": True, "data_source_id": None}),
            )
            result = validate_workspace(workspace, skill_root=ROOT)
            self.assertFalse(result["ok"])
            self.assertTrue(any("data_source_id" in item for item in result["errors"]), result)

    def test_each_role_family_has_independent_confirmation_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = self.copy_example(Path(tmp))
            setup_path = workspace / "state" / "setup.json"
            setup = json.loads(setup_path.read_text(encoding="utf-8"))
            setup["role_family_templates"]["dev"] = "pending_review"
            setup_path.write_text(json.dumps(setup, indent=2), encoding="utf-8")
            result = validate_workspace(workspace, skill_root=ROOT)
            self.assertFalse(result["ok"])
            self.assertTrue(any("dev" in item and "not confirmed" in item for item in result["errors"]), result)

    def test_check_tools_uses_current_interpreter(self) -> None:
        result = validate_workspace(
            ROOT / "examples" / "it-graduate",
            skill_root=ROOT,
            check_tools=True,
        )
        self.assertEqual(result["python_executable"], sys.executable)
        self.assertFalse(any("launcher" in item.lower() for item in result["warnings"]), result)


if __name__ == "__main__":
    unittest.main()
