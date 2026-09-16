# Setup Workflow

Setup creates a reusable user workspace. It should be resumable, minimally invasive, and separate candidate-specific data from the public Skill.

## 1. Preconditions

Before setup, verify the runtime can support the intended workflow:

- Python is available;
- `pdflatex` is available if LaTeX output will be used;
- Notion is connected/authorized if the user wants Notion integration;
- the runtime can reach the upload endpoint returned by Notion when file sync is required.

Missing capabilities should be reported before generating large amounts of material.

## 2. Create the workspace

Create the standard structure:

```text
<workspace>/
├── easy-apply.yaml
├── profile/
│   ├── profile.md
│   ├── original-resumes/
│   └── resume-templates/
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

Copy `workspace-scaffold/easy-apply.yaml` and the profile scaffold into their canonical locations. Keep uploaded original resumes unchanged under `profile/original-resumes/`.

Use `state/setup.json` to record completed setup steps so an interrupted setup can resume without repeating completed work.

## 3. Collect minimum user configuration

Use `interview.md`.

Write:

- search keywords/location to `easy-apply.yaml`;
- explicit work-rights facts to `eligibility.work_rights`;
- resume page target to `resume.pages`;
- persistent exclusions/preferences only when explicitly requested.

Do not ask for job platforms or posting-time range during initial setup.

## 4. Build the candidate profile

Extract factual information from the uploaded resumes into `profile/profile.md`.

Rules:

- preserve uncertainty when source resumes conflict;
- do not infer missing technologies, dates, metrics or responsibilities;
- keep useful boundaries/clarifications, not only polished bullet text;
- let the user correct the profile before relying on disputed facts.

The profile becomes the factual source of truth for later material generation.

## 5. Create role-family resume templates

For each target role family:

1. start from the user's existing LaTeX resume when usable; otherwise use `workspace-scaffold/resume-layout.tex`;
2. create one reusable template under `profile/resume-templates/`;
3. compile and visually review it;
4. iterate with the user until the template is accepted;
5. register the role-family key and filename in `easy-apply.yaml`.

Templates should contain the user's real baseline content. They are presentation/content baselines, not alternative factual sources.

Do not create one template per employer.

## 6. Cover-letter layout

If the user has no preferred letter layout, copy `workspace-scaffold/cover-letter-layout.tex` to `profile/cover-letter-layout.tex` and customize only presentation/contact placeholders. Letter body content is generated per job and is never a generic reusable story.

## 7. Create/connect the Notion Job Tracker

Use `references/notion/schema.md` to create or validate the Job Tracker.

Store the resulting data-source ID in:

```yaml
notion:
  data_source_id: ...
```

Only the Notion integration layer should depend on exact property names.

## 8. Validate

Run `scripts/validate_workspace.py` for deterministic local checks, then perform connector-side Notion reachability/schema checks that cannot be performed by a local script.

Setup is complete only when:

- configuration parses and uses a supported schema version;
- `profile/profile.md` exists;
- configured role-family templates exist;
- required workspace directories exist;
- the Notion data source is configured and connector-side schema validation passes when Notion is enabled.

## 9. Later changes

Do not rerun all setup for ordinary updates.

- new/corrected candidate facts -> update `profile.md`;
- new role family -> create and confirm one new resume template, then update `role_families`;
- new platform -> use the job-search platform setup flow and `_adapter-spec.md`;
- persistent writing preference -> update profile/config only when the user explicitly asks for a general rule.
