"""Small deterministic scanners used by resume and cover-letter validators."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping


def _contains_term(text: str, term: str) -> bool:
    """Case-insensitive term match with conservative token boundaries.

    Terms such as ``React.js`` or ``Microsoft 365`` are matched literally while
    avoiding obvious substring false positives such as matching ``Go`` inside
    ``Google``.
    """

    clean_term = term.strip()
    if not clean_term:
        return False
    pattern = rf"(?<!\w){re.escape(clean_term)}(?!\w)"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def find_excluded_terms(text: str, excluded_terms: Iterable[str]) -> list[str]:
    """Return configured excluded terms that appear in generated material."""

    return [term for term in excluded_terms if _contains_term(text, term)]


def find_skill_terms(
    text: str,
    skills: Iterable[str],
    aliases: Mapping[str, Iterable[str]] | None = None,
) -> list[str]:
    """Return canonical skills found in text.

    ``aliases`` maps a canonical skill to accepted textual variants, e.g.
    ``{"React": ["React.js"]}``. The canonical term itself is always checked.
    """

    alias_map = aliases or {}
    found: list[str] = []

    for skill in skills:
        candidates = [skill, *alias_map.get(skill, [])]
        if any(_contains_term(text, candidate) for candidate in candidates):
            found.append(skill)

    return found
