# Easy Apply Skill

Easy Apply is a reusable, human-in-the-loop workflow for:

- setting up a job-search workspace from a user's resume/profile;
- discovering and screening jobs across supported platforms;
- tracking kept jobs in Notion;
- tailoring grounded LaTeX resumes;
- drafting cover letters with a required human-input checkpoint;
- mirroring current local PDFs into Notion Submitted Materials.

It does **not** auto-submit job applications. The user decides what to apply for and controls application Status after a job row is created.

## Design

The repository contains public/reusable behavior only. Candidate-specific facts, role targets, search parameters, preferences, templates and generated materials belong in the user's workspace.

```text
Skill = how the workflow works
Workspace = who the user is and what they want
Runtime/tools = how web, browser, Notion and local files are accessed
```

See `SKILL.md` for runtime routing and global rules.

## Main structure

```text
references/        Runtime instructions by module
scripts/           Deterministic local helpers
workspace-scaffold/Starting files for new workspaces
tests/             Python unit tests
evals/             AI regression cases
examples/          Fictional example workspace
docs/              Human-facing design notes
```

## Workspace shape

```text
my-job-search/
├── easy-apply.yaml
├── profile/
│   ├── profile.md
│   ├── original-resumes/
│   ├── resume-templates/
│   └── cover-letter-layout.tex
├── sources/
├── artefacts/
│   ├── resume/
│   ├── resume-pdf/
│   ├── cover-letter/
│   ├── cover-letter-pdf/
│   └── archive/
└── state/
    ├── seen-jobs.jsonl
    └── runs/
```

## Runtime dependencies

Python helpers are written for Python 3.11+.

Required for normal YAML/PDF checks:

```text
PyYAML
pypdf
```

LaTeX generation requires `pdflatex` on PATH. PyMuPDF is optional and enables a rough last-page whitespace diagnostic.

Install Python dependencies with:

```bash
python -m pip install -r requirements.txt
```

On Windows, use `py -3` instead of `python` when the WindowsApps Python stub is first on PATH.

## Quick validation

Run unit tests from the repository root:

```bash
py -3 -m unittest discover -s tests -v
```

Validate a configured user workspace:

```bash
py -3 scripts/validate_workspace.py --workspace <path>
```

Notion reachability and live schema checks require the runtime's authorized Notion connector/API. `validate_workspace.py` can validate a connector-exported schema snapshot but does not store or manage Notion credentials.

## Key principles

- `profile/profile.md` is the factual source of truth for candidate claims.
- Role-family resume templates are approved baselines, not new fact sources.
- Job descriptions decide what to emphasize, never what to invent.
- Search rules are general; candidate-specific thresholds/preferences live in the workspace.
- Platform adapters describe stable platform behavior and browser quirks, not brittle click-by-click scripts.
- `seen-jobs.jsonl` contains compact search history; Notion contains kept/application-tracking jobs.
- Generated local PDFs are the source of truth for Submitted Materials.
- A failed multi-file sync must never replace Notion with a partial file list.

## Historical source material

This reusable skill was distilled from an earlier private job-search workflow and its feedback loops. Personal data, private workspace paths, and generated artefacts should not be copied into this repository.
