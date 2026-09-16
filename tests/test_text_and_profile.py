from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lib.profile import extract_profile_skills  # noqa: E402
from lib.text_scan import find_excluded_terms, find_skill_terms  # noqa: E402


class TextAndProfileTests(unittest.TestCase):
    def test_term_boundary_does_not_match_go_inside_google(self) -> None:
        self.assertEqual(find_skill_terms("Google Cloud", ["Go"]), [])
        self.assertEqual(find_skill_terms("Built a Go service", ["Go"]), ["Go"])

    def test_alias_returns_canonical_skill(self) -> None:
        found = find_skill_terms("Built UI with React.js", ["React"], {"React": ["React.js"]})
        self.assertEqual(found, ["React"])

    def test_excluded_terms(self) -> None:
        self.assertEqual(
            find_excluded_terms("Certificate A and Tool B", ["Certificate A", "Certificate C"]),
            ["Certificate A"],
        )

    def test_extract_skills_from_profile_section_only(self) -> None:
        profile = """
## Work Experience
- Used SecretTool

## Skills
### Languages
- Python, Java
### Empty Category
-
### Frameworks / Libraries
- React
- SQL, Git

## Certifications
- Example
"""
        self.assertEqual(extract_profile_skills(profile), ["Python", "Java", "React", "SQL", "Git"])


if __name__ == "__main__":
    unittest.main()
