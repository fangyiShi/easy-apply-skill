from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from seen_jobs import add_seen_job, find_seen_job, latest_records, read_events  # noqa: E402


class SeenJobsTests(unittest.TestCase):
    def test_append_only_history_and_latest_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first = add_seen_job(
                tmp,
                job_key="example|support engineer|central city",
                source="linkedin",
                source_job_id="123",
                decision="needs_verification",
            )
            second = add_seen_job(
                tmp,
                job_key="example|support engineer|central city",
                source="linkedin",
                source_job_id="123",
                decision="keep",
            )

            self.assertEqual(len(read_events(tmp)), 2)
            self.assertEqual(len(latest_records(tmp)), 1)
            self.assertEqual(second["first_seen"], first["first_seen"])
            self.assertEqual(latest_records(tmp)[0]["decision"], "keep")

    def test_find_prefers_source_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            add_seen_job(
                tmp,
                job_key="example|developer|remote",
                source="jora",
                source_job_id="A1",
                decision="reject",
            )
            record = find_seen_job(tmp, source="jora", source_job_id="A1")
            self.assertIsNotNone(record)
            self.assertEqual(record["decision"], "reject")


if __name__ == "__main__":
    unittest.main()
