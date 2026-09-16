from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from find_materials import find_materials, validate_file_slug  # noqa: E402


class FindMaterialsTests(unittest.TestCase):
    def test_finds_resume_and_optional_letter_in_stable_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            resume_dir = root / "artefacts" / "resume-pdf"
            letter_dir = root / "artefacts" / "cover-letter-pdf"
            resume_dir.mkdir(parents=True)
            letter_dir.mkdir(parents=True)
            (resume_dir / "resume-example-support.pdf").write_bytes(b"resume")
            (letter_dir / "cover-letter-example-support.pdf").write_bytes(b"letter")

            paths = find_materials(root, "example-support")
            self.assertEqual(
                [path.name for path in paths],
                ["resume-example-support.pdf", "cover-letter-example-support.pdf"],
            )

    def test_rejects_unsafe_slug(self) -> None:
        with self.assertRaises(ValueError):
            validate_file_slug("../other-file")


if __name__ == "__main__":
    unittest.main()
