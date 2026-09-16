# Easy Apply Architecture

Easy Apply is one reusable Skill with internally modular references, deterministic scripts, and a separate per-user workspace.

## Separation of concerns

```text
Skill      -> reusable workflow/rules/scripts
Runtime    -> web/browser/Notion/file execution capabilities
Workspace  -> candidate facts, preferences, templates, parameters, state, artefacts
```

Personalization should normally change the workspace, not the Skill.

## Runtime modules

```text
setup
job-search
resume
cover-letter
notion sync
common grounding
```

Business modules may use `references/notion/` and `references/common/`. They should not read each other's business rules.

Only the Notion module owns exact Notion property names.

## Job-search flow

```text
resolve request
-> web discovery
-> requested platform discovery
-> normalize to JobRecord
-> deduplicate
-> verify required evidence
-> keep / reject / needs_verification
-> assign priority to kept jobs
-> persist kept jobs to Notion
-> persist all evaluated jobs to seen-jobs
-> report coverage
```

Platform adapters contain stable platform behavior: filters, IDs/URLs, result enumeration, browser quirks and completion/failure signals. They do not contain candidate-specific screening thresholds.

## Application-material flow

Resume:

```text
confirm live job
-> load canonical workspace resume layout
-> select approved role-family template
-> make targeted grounded edits
-> build
-> deterministic checks
-> AI semantic/visual review
-> save locally
-> sync complete local PDF set when Notion is enabled
```

Cover letter:

```text
confirm live job
-> identify 3–5 grounded match points
-> ask user per-letter questions
-> draft grounded narrative
-> build/check/review
-> save locally
-> sync complete local PDF set when Notion is enabled
```

## Identity and storage

- `job_key` is the default cross-platform job dedupe key.
- `source + source_job_id` is the strongest same-platform identity.
- `file_slug` is a stable persisted material identifier.
- `state/seen-jobs.jsonl` stores compact history for all evaluated jobs.
- Notion stores kept jobs and user application lifecycle.
- Local generated PDFs are the source of truth for Submitted Materials.
- User-confirmed layouts and role-family content templates live in the workspace, never in the reusable Skill.

## Human control

When Notion is enabled, job search may create a row with initial `Status = Not Applied`. After creation, application Status and Apply date are user-owned. When Notion is disabled, Easy Apply performs no Notion mutations. Easy Apply prepares materials but does not automatically submit applications.

## Testing

- `tests/` covers deterministic scripts.
- `evals/` stores AI regression cases extracted from historical feedback loops.
- `validate_workspace.py` checks local workspace contract.
- live Notion reachability/schema validation is performed by the authorized runtime connector.
