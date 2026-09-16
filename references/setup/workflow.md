# Setup Workflow

Setup creates a reusable user workspace. It should be resumable, minimally invasive, and separate candidate-specific data from the public Skill.

## 1. Preconditions

Before setup, verify the runtime can support the intended workflow:

- the current Python interpreter is version 3.11 or later;
- packages in `requirements.txt` are importable in that interpreter;
- `pdflatex` is available if LaTeX output will be used;
- Notion is connected/authorized if the user wants Notion integration;
- the runtime can reach the upload endpoint returned by Notion when file sync is required.

Use `scripts/validate_workspace.py --check-tools` when a workspace already exists. If Python packages are missing, report an installation command based on the current interpreter, equivalent to:

```text
<current-python> -m pip install -r <skill-root>/requirements.txt
```

Do not install dependencies, modify system configuration or connect Notion without user authorization. Missing capabilities should be reported before generating large amounts of material.

## 2. Create the workspace

Create the standard structure:

```text
<workspace>/
├── easy-apply.yaml
├── profile/
│   ├── profile.md
│   ├── original-resumes/
│   ├── resume-layout.tex
│   └── resume-templates/
├── sources/
├── artefacts/
│   ├── resume/
│   ├── resume-pdf/
│   ├── cover-letter/
│   ├── cover-letter-pdf/
│   └── archive/
└── state/
    ├── setup.json
    ├── seen-jobs.jsonl
    └── runs/
```

Copy `workspace-scaffold/easy-apply.yaml`, `workspace-scaffold/profile.md`, `workspace-scaffold/resume-layout.tex` and `workspace-scaffold/setup.json` into their canonical workspace locations.

The user may upload resume files directly in the current conversation. Do not require the user to place them in the workspace first. For every authorized uploaded source resume:

1. use `scripts/archive_original_resume.py` to copy it into `profile/original-resumes/`;
2. preserve the file bytes and verify the SHA-256 reported by the script;
3. retain the original filename when safe and available;
4. never overwrite a different file with the same name;
5. record only the archived relative path, hash and status in `state/setup.json`.

Uploaded and archived resumes are factual source material. They are not automatically approved layouts or role-family content templates.

Use `state/setup.json` to record completed setup steps so an interrupted setup can resume without repeating completed work. Track `profile`, `resume_layout`, `notion`, attachment archival results, and each role family independently under `role_family_templates`. Do not collapse multiple directions into one `resume_template: complete` flag.

Example:

```json
{
  "schema_version": 1,
  "attachments": {},
  "profile": "confirmed",
  "resume_layout": "confirmed",
  "role_family_templates": {
    "software_development": "confirmed",
    "digital_marketing": "pending_review"
  },
  "notion": "skipped"
}
```

## 3. Collect minimum user configuration

Use `interview.md`.

Write:

- search keywords/location to `easy-apply.yaml`;
- explicit work-rights facts to `eligibility.work_rights`;
- the explicitly answered resume page target to `resume.pages`;
- the explicit Notion choice to `notion.enabled`;
- persistent exclusions/preferences only when explicitly requested.

The resume page target must be asked. Do not infer it from uploaded resume length. Do not ask for job platforms or posting-time range during initial setup.

## 4. Build the candidate profile

Extract factual information from the uploaded resumes into `profile/profile.md`.

Rules:

- preserve uncertainty when source resumes conflict;
- do not infer missing technologies, dates, metrics or responsibilities;
- keep useful boundaries/clarifications, not only polished bullet text;
- let the user correct the profile before relying on disputed facts.

The profile becomes the factual source of truth for later material generation. It must retain the complete confirmed candidate history even when a one-page resume cannot show every fact. Page limits constrain generated resumes, not `profile.md`.

## 5. Confirm one canonical resume layout

`profile/resume-layout.tex` is the user's single canonical resume format. It controls document class, fonts, colors, margins, section styling and shared presentation macros, but does not contain role-specific experience selection.

Start from a usable uploaded LaTeX layout when the user wants to preserve it; otherwise customize the copied scaffold. Compile and visually review the layout with representative grounded content, then mark `resume_layout` as `confirmed` in `state/setup.json` only after user approval.

Do not store the user's confirmed layout in the Skill folder. It belongs to the workspace and may contain user-specific presentation choices.

## 6. Create role-family content templates

For each target role family:

1. create one distinct content template under `profile/resume-templates/`;
2. load the canonical format with `\input{resume-layout.tex}`;
3. select the profile facts, summary, skill order, experiences and projects most relevant to that direction;
4. compile it with `scripts/build_pdf.py --workspace <workspace>` and visually review it;
5. iterate with the user until the direction-specific content is accepted;
6. register the role-family key and unique filename in `easy-apply.yaml`;
7. mark only that role family as `confirmed` in `state/setup.json`.

N target role families require N distinct content template files. They share `profile/resume-layout.tex`; they do not share one content template. Templates contain selected real baseline content and are not alternative factual sources. A one-page template may omit lower-relevance facts without removing them from `profile.md`.

Do not create one template per employer.

## 7. Cover-letter layout

If the user has no preferred letter layout, copy `workspace-scaffold/cover-letter-layout.tex` to `profile/cover-letter-layout.tex` and customize only presentation/contact placeholders. Letter body content is generated per job and is never a generic reusable story.

## 8. Configure Notion

If `notion.enabled` is `false`, set the setup state to `skipped`, do not require a data-source ID, and do not call Notion. Job search may still run and maintain local seen-job state, but remote tracking and material sync are disabled.

If `notion.enabled` is `true`, create or connect the Job Tracker using `references/notion/schema.md`.

Store the resulting data-source ID in:

```yaml
notion:
  enabled: true
  data_source_id: ...
```

Only the Notion integration layer should depend on exact property names. Mark Notion setup `confirmed` only after connector-side reachability and schema validation pass.

## 9. Validate

Run `scripts/validate_workspace.py` for deterministic local checks, then perform connector-side Notion reachability/schema checks that cannot be performed by a local script.

Setup is complete only when:

- configuration parses and uses a supported schema version;
- `profile/profile.md` exists;
- `profile/resume-layout.tex` exists and is confirmed;
- every configured role family has its own template, loads the canonical layout, and is independently confirmed;
- `resume.pages` contains the user's explicit positive-integer answer;
- required workspace directories exist;
- Notion is either explicitly disabled with setup state `skipped`, or enabled with a configured data source and successful connector-side schema validation.

## 10. Later changes

Do not rerun all setup for ordinary updates.

- new/corrected candidate facts -> update `profile.md`;
- format change -> update and reconfirm the single canonical `profile/resume-layout.tex`;
- new role family -> create and confirm one new content template, then update `role_families`;
- new platform -> use the job-search platform setup flow and `_adapter-spec.md`;
- persistent writing preference -> update profile/config only when the user explicitly asks for a general rule.

## 11. Migrate a schema-version 1 workspace

Do not silently reinterpret a version 1 workspace as version 2. During an authorized setup update:

1. ask for the resume page target if there is no recorded explicit answer;
2. ask whether the user wants Notion and write `notion.enabled`;
3. extract one confirmed canonical format into `profile/resume-layout.tex`;
4. make every role-family content template distinct and load the canonical layout;
5. create `state/setup.json` with independent confirmation states;
6. validate and visually review every direction before setting `schema_version: 2`.

Preserve candidate facts, original attachments, generated artefacts and user-managed Notion state throughout migration.
