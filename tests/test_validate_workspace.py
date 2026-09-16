from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_workspace import validate_workspace  # noqa: E402


class ValidateWorkspaceTests(unittest.TestCase):
    def test_fictional_example_workspace_is_locally_valid(self) -> None:
        result = validate_workspace(ROOT / "examples" / "it-graduate", skill_root=ROOT)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["errors"], [])
        self.assertTrue(result["external_checks"])


if __name__ == "__main__":
    unittest.main()
