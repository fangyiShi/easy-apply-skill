from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from build_pdf import latex_environment  # noqa: E402


class BuildPdfTests(unittest.TestCase):
    def test_workspace_profile_is_added_to_texinputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            profile = workspace / "profile"
            profile.mkdir()
            (profile / "resume-layout.tex").write_text("% test layout\n", encoding="utf-8")
            with patch.dict(os.environ, {"TEXINPUTS": "existing-search-path"}, clear=False):
                environment = latex_environment(workspace)
            entries = environment["TEXINPUTS"].split(os.pathsep)
            self.assertEqual(entries[0], str(profile.resolve()))
            self.assertIn("existing-search-path", entries)
            self.assertEqual(entries[-1], "")


if __name__ == "__main__":
    unittest.main()
