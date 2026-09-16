"""Deterministic identity and filename helpers for Easy Apply jobs."""

from __future__ import annotations

import re
import unicodedata


_WHITESPACE_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[^\w\s-]", flags=re.UNICODE)
_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _basic_normalize(value: str) -> str:
    text = unicodedata.normalize("NFKC", value or "").strip().lower()
    text = text.replace("&", " and ")
    text = _PUNCT_RE.sub(" ", text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text


def normalize_company(company: str) -> str:
    return _basic_normalize(company)


def normalize_title(title: str) -> str:
    return _basic_normalize(title)


def normalize_location(location: str) -> str:
    """Normalize location text without assuming a country or geography.

    Cross-platform callers should canonicalize known equivalent location labels
    before building a JobRecord when they have reliable context. The shared helper
    intentionally limits itself to deterministic text normalization.
    """

    return _basic_normalize(location)


def build_job_key(company: str, title: str, location: str) -> str:
    """Build the cross-platform deduplication key."""

    values = (
        normalize_company(company),
        normalize_title(title),
        normalize_location(location),
    )
    if not all(values):
        raise ValueError("company, title, and location are required to build job_key")
    return "|".join(values)


def build_source_identity(source: str, source_job_id: str | None) -> str | None:
    """Build an exact same-platform identity when a stable job ID exists."""

    if source_job_id is None or not str(source_job_id).strip():
        return None
    normalized_source = _basic_normalize(source).replace(" ", "-")
    if not normalized_source:
        raise ValueError("source is required when source_job_id is provided")
    return f"{normalized_source}:{str(source_job_id).strip()}"


def slugify(value: str) -> str:
    """Create a conservative ASCII filename slug."""

    text = unicodedata.normalize("NFKD", value or "")
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    text = _SLUG_RE.sub("-", text).strip("-")
    return text


def build_file_slug(company: str, title: str, max_title_words: int = 4) -> str:
    """Build ``<company>-<job>`` for generated material filenames.

    The title keeps at most ``max_title_words`` words to remain readable. Collision
    handling is intentionally outside this helper because it needs workspace state.
    """

    company_slug = slugify(company)
    title_words = [word for word in slugify(title).split("-") if word]
    title_slug = "-".join(title_words[:max_title_words])

    if not company_slug or not title_slug:
        raise ValueError("company and title are required to build file_slug")

    return f"{company_slug}-{title_slug}"
