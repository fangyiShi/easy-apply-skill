"""Markdown profile helpers used by deterministic material checks."""

from __future__ import annotations

import re
from pathlib import Path


_SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_SUBSECTION_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
_BULLET_RE = re.compile(r"^[ \t]*[-*][ \t]+(.+?)[ \t]*$", re.MULTILINE)


def profile_path(workspace: str | Path) -> Path:
    return Path(workspace).expanduser().resolve() / "profile" / "profile.md"


def read_profile(workspace: str | Path) -> str:
    path = profile_path(workspace)
    if not path.is_file():
        raise FileNotFoundError(f"Missing candidate profile: {path}")
    return path.read_text(encoding="utf-8")


def markdown_section(text: str, heading: str) -> str:
    """Return the body of a level-2 Markdown section, or an empty string."""

    matches = list(_SECTION_RE.finditer(text))
    target = heading.strip().casefold()
    for index, match in enumerate(matches):
        if match.group(1).strip().casefold() != target:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        return text[start:end].strip()
    return ""


def extract_profile_skills(text: str) -> list[str]:
    """Extract canonical skills listed as bullets inside ``## Skills``.

    Category headings are ignored. Empty scaffold bullets are ignored. A bullet may
    contain comma-separated skills; those are split conservatively.
    """

    section = markdown_section(text, "Skills")
    if not section:
        return []

    # Remove subsection headings so their labels do not become candidate skills.
    section = _SUBSECTION_RE.sub("", section)
    values: list[str] = []
    seen: set[str] = set()

    for bullet in _BULLET_RE.findall(section):
        clean = bullet.strip()
        if not clean or clean in {"-", "<skill>"}:
            continue
        for part in re.split(r"\s*[,;|]\s*", clean):
            skill = part.strip().strip(".`")
            if not skill:
                continue
            key = skill.casefold()
            if key not in seen:
                seen.add(key)
                values.append(skill)
    return values


def extract_profile_skills_from_workspace(workspace: str | Path) -> list[str]:
    return extract_profile_skills(read_profile(workspace))
