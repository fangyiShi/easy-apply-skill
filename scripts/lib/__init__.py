"""Shared deterministic helpers for Easy Apply scripts."""

from .config import ConfigError, load_workspace_config
from .identity import (
    build_file_slug,
    build_job_key,
    build_source_identity,
    normalize_company,
    normalize_location,
    normalize_title,
    slugify,
)
from .profile import extract_profile_skills, extract_profile_skills_from_workspace, read_profile
from .text_scan import find_excluded_terms, find_skill_terms

__all__ = [
    "ConfigError",
    "load_workspace_config",
    "build_file_slug",
    "build_job_key",
    "build_source_identity",
    "normalize_company",
    "normalize_location",
    "normalize_title",
    "slugify",
    "read_profile",
    "extract_profile_skills",
    "extract_profile_skills_from_workspace",
    "find_excluded_terms",
    "find_skill_terms",
]
