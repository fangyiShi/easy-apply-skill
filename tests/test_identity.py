from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lib.identity import (  # noqa: E402
    build_file_slug,
    build_job_key,
    build_source_identity,
    normalize_location,
)


class IdentityTests(unittest.TestCase):
    def test_job_key_is_deterministic(self) -> None:
        self.assertEqual(
            build_job_key("Example & Co.", "Support Engineer", "Central City"),
            "example and co|support engineer|central city",
        )

    def test_location_normalization_does_not_assume_geography(self) -> None:
        self.assertEqual(normalize_location("Central City Region"), "central city region")

    def test_source_identity_is_namespaced(self) -> None:
        self.assertEqual(build_source_identity("LinkedIn", "123"), "linkedin:123")
        self.assertEqual(build_source_identity("Jora", "123"), "jora:123")

    def test_file_slug_contains_company_and_job(self) -> None:
        self.assertEqual(
            build_file_slug("Example Systems", "Junior Application Support Engineer"),
            "example-systems-junior-application-support-engineer",
        )


if __name__ == "__main__":
    unittest.main()
