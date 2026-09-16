from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from archive_original_resume import archive_original_resume, sha256_file  # noqa: E402


class ArchiveOriginalResumeTests(unittest.TestCase):
    def test_archives_bytes_unchanged_and_reuses_identical_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / "workspace"
            source = root / "resume.pdf"
            source.write_bytes(b"%PDF-1.4\nfictional-test-bytes\n")

            first = archive_original_resume(workspace, source)
            archived = workspace / first["path"]
            self.assertEqual(first["status"], "archived")
            self.assertEqual(source.read_bytes(), archived.read_bytes())
            self.assertEqual(first["sha256"], sha256_file(archived))

            second = archive_original_resume(workspace, source)
            self.assertEqual(second["status"], "already_archived")
            self.assertEqual(second["path"], first["path"])

    def test_does_not_overwrite_different_same_named_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / "workspace"
            first_dir = root / "first"
            second_dir = root / "second"
            first_dir.mkdir()
            second_dir.mkdir()
            first = first_dir / "resume.pdf"
            second = second_dir / "resume.pdf"
            first.write_bytes(b"first")
            second.write_bytes(b"second")

            first_result = archive_original_resume(workspace, first)
            second_result = archive_original_resume(workspace, second)
            self.assertEqual(first_result["path"], "profile/original-resumes/resume.pdf")
            self.assertEqual(second_result["path"], "profile/original-resumes/resume-2.pdf")


if __name__ == "__main__":
    unittest.main()
