# Notion Job Tracker Schema Contract

This file defines the Notion database contract used by Easy Apply.

When enabled, Notion is the user's application tracker and the mirror for generated application materials. It is **not** the source of truth for candidate facts, job-search history, or local files. A workspace may explicitly disable Notion.

Only the Notion integration layer should depend on the exact property names defined here. Other Easy Apply modules should work with `JobRecord`, workspace configuration, or local file paths instead of hard-coding Notion field names.

---

## 1. Database purpose

The Job Tracker stores jobs that passed Easy Apply screening and are useful for the user's application workflow.

It does not store every job discovered during search. Rejected jobs remain in `state/seen-jobs.jsonl`.

The default database name is:

```text
Job Tracker
```

When Notion is enabled, its user-specific data source ID must be stored in the workspace configuration:

```yaml
notion:
  enabled: true
  data_source_id: collection://...
```

Do not hard-code a user's data source ID inside the Skill.

`enabled: false` means the user explicitly opted out. In that state, do not require a data-source ID and do not make connector/API calls. A missing or null `enabled` value means setup has not yet captured the user's choice.

---

## 2. Required properties

The following property names and types are part of the Easy Apply contract.

| Property | Notion type | Required | Written by | Purpose |
|---|---|---:|---|---|
| `Position` | Title | yes | job-search | Human-readable job title |
| `Company` | Rich text | yes | job-search | Employer name |
| `Location` | Rich text | yes | job-search | Human-readable location |
| `URL` | URL | yes | job-search | Canonical job/application URL used to reopen the live listing |
| `Platform` | Multi-select | yes | job-search | Source platform(s) associated with the kept job |
| `Type` | Select | no | job-search | Employment type |
| `Priority` | Select | yes | job-search | `P1`, `P2`, or `P3` |
| `Cover Letter` | Checkbox | yes | job-search | Whether the listing/application mentions a cover letter |
| `Appendix` | Rich text | yes | job-search | Compact screening rationale and requirement summary |
| `File Slug` | Rich text | yes | job-search | Stable identifier used to find local application materials |
| `Status` | Status | yes | job-search on creation; user afterwards | Application lifecycle |
| `Apply date` | Date | no | user | Date the user applied |
| `Submitted Materials` | Files | no | notion/sync | Resume and cover-letter PDFs mirrored from local files |

Property names are exact. Runtime code must not silently guess renamed fields.

---

## 3. JobRecord to Notion mapping

The job-search workflow converts source listings into `JobRecord` before writing anything to Notion.

Use this mapping:

| JobRecord field | Notion property | Notes |
|---|---|---|
| `title` | `Position` | Preserve human-readable title |
| `company` | `Company` | Preserve human-readable company |
| `location` | `Location` | Preserve human-readable location |
| `canonical_url` or `application_url` | `URL` | Prefer the most stable URL that opens the live job/application path |
| `source` | `Platform` | Add the source as a multi-select value |
| `employment_type` | `Type` | Map only when confidently known |
| `priority` | `Priority` | Must be `P1`, `P2`, or `P3` for kept jobs |
| `cover_letter` | `Cover Letter` | Boolean; optional cover letter still means `true` |
| screening summary | `Appendix` | Built from normalized requirement/evaluation fields; see section 5 |
| `file_slug` | `File Slug` | Persist once; never regenerate from later Notion edits |
| — | `Status` | Set to `Not Applied` only when creating a new job row |
| — | `Apply date` | User-owned; Easy Apply does not write it |
| local PDFs | `Submitted Materials` | Written only by `notion/sync` |

`job_key` is intentionally not stored in Notion in the MVP. It belongs to search/deduplication state.

---

## 4. Select and status values

### 4.1 Platform

`Platform` is a multi-select property because the same kept job may be discovered through more than one source.

At minimum, setup may create:

```text
LinkedIn
```

When a new platform is configured for the first time, Easy Apply may add its display name as a new option, for example:

```text
Jora
SEEK
Indeed
```

The source adapter uses a normalized internal source name such as `linkedin` or `jora`; the Notion integration converts it to the human-readable Platform option.

Do not require all future platforms to be known during setup.

### 4.2 Type

Default options:

```text
Full time
Part time
Casual
Contract
Internship
```

If a listing's employment type is unclear, leave `Type` empty rather than guessing.

### 4.3 Priority

Allowed values:

```text
P1
P2
P3
```

Meanings are defined by `references/job-search/rules.md`, not by this schema file.

### 4.4 Status

Default groups and values:

| Group | Status | Meaning |
|---|---|---|
| To-do | `Not Applied` | Kept by search and not yet applied |
| In progress | `Applied` | Application submitted |
| In progress | `Assessment` | Online test, recorded response, take-home task, or similar |
| In progress | `Interview` | Phone screen, HR call, or interview |
| In progress | `Offer` | Offer received and still under consideration |
| Complete | `Accepted` | Offer accepted |
| Complete | `Rejected` | Employer rejected the application |
| Complete | `Withdrawn` | User stopped the process or declined an offer |
| Complete | `No Response` | User considers the process inactive after no response |

Easy Apply may set `Status = Not Applied` when it **creates** a new row. After creation, application status is user-controlled and must not be automatically changed by job-search, resume, cover-letter, or sync workflows.

---

## 5. Appendix format

`Appendix` is a compact human-readable summary of why the job was kept and what the user should know before applying.

Default structure:

```text
Experience: <requirement or not specified>. Core match: <most relevant hard skills>. Work rights: <conclusion>. Notes: <priority reason, boundary condition, or risk>.
```

Keep it concise. Do not copy the full JD into Notion.

The exact wording may be localized to the user's language, but the information should cover the same four concepts when relevant:

1. experience requirement;
2. core skill match;
3. work-rights / citizenship / clearance conclusion;
4. reason for the priority or any important caveat.

Do not place application lifecycle notes in `Appendix`; those belong to `Status` and user-managed notes if the user later adds them.

---

## 6. URL rule

`URL` should point to the most useful stable live listing/application page available at the time of search.

Preference order:

1. direct company/ATS job page when it clearly represents the same active job;
2. clean canonical source listing URL;
3. stable platform job URL.

Avoid search-result URLs and temporary tracking URLs when a stable job URL is available.

When querying this property through a connector/API that exposes the user-defined URL field as `userDefined:URL`, use the connector's required field name. `URL` remains the canonical Notion property name.

---

## 7. File Slug rule

`File Slug` is created by the JobRecord layer and persisted into Notion with the new job row.

Example:

```text
aws-cloud-support-engineer
```

It maps to local files such as:

```text
resume-aws-cloud-support-engineer.tex
resume-aws-cloud-support-engineer.pdf
cover-letter-aws-cloud-support-engineer.tex
cover-letter-aws-cloud-support-engineer.pdf
```

Once persisted, `File Slug` is stable. If the user later edits `Company` or `Position` in Notion, Easy Apply must continue using the stored `File Slug` rather than generating a new one.

Do not use Notion row titles as local file identity.

---

## 8. Submitted Materials ownership

`Submitted Materials` mirrors local PDFs. Local files are the source of truth.

Only `notion/sync` writes this property.

The property is a file list and updates replace the list rather than append to it. Therefore sync must:

1. find all current PDFs for the row's `File Slug`;
2. upload every file required for the new list;
3. wait until all required uploads succeed;
4. update `Submitted Materials` once with the complete list.

Example:

```text
Local:
resume-aws-cloud-support-engineer.pdf
cover-letter-aws-cloud-support-engineer.pdf

Notion Submitted Materials after sync:
[resume-aws-cloud-support-engineer.pdf, cover-letter-aws-cloud-support-engineer.pdf]
```

Never update the property with only the newly created file if other current local materials already exist.

If any required upload fails, do not replace `Submitted Materials` with a partial list.

---

## 9. Write ownership and overwrite rules

The following ownership rules prevent modules from overwriting user state or each other's data.

### job-search may

- create a new kept job row;
- write `Position`, `Company`, `Location`, `URL`, `Platform`, `Type`, `Priority`, `Cover Letter`, `Appendix`, `File Slug`;
- set the initial `Status` to `Not Applied`.

### job-search must not

- change the Status of an existing row;
- write `Apply date`;
- write or clear `Submitted Materials`;
- overwrite a user's existing application lifecycle data when encountering a duplicate job.

### resume and cover-letter may

- read job fields needed to prepare materials;
- trigger `notion/sync` after successful local generation.

They must not directly mutate Job Tracker fields outside sync.

### notion/sync may

- replace `Submitted Materials` with the complete local PDF set for the specified `File Slug`.

It must not change any other property.

### user owns

- `Status` after creation;
- `Apply date`;
- manual deletion of jobs they do not want to pursue;
- any extra Notion properties they add outside the required Easy Apply schema.

---

## 10. Duplicate rows and existing records

Job deduplication is primarily handled before Notion persistence by JobRecord + seen-jobs logic.

If job-search nevertheless finds that a matching row already exists in Notion:

- do not create a second row;
- do not reset `Status` to `Not Applied`;
- do not clear `Submitted Materials` or `Apply date`;
- only fill missing search-owned metadata when doing so is safe and does not overwrite user-managed state.

A duplicate detection implementation may use stable URL, File Slug, and known job metadata as supporting checks, but the canonical deduplication rules belong in `references/job-search/job-record.md`.

---

## 11. Setup and validation

During setup, first ask whether the user wants Notion. If disabled, record `enabled: false`, mark Notion setup as `skipped`, and perform no Notion operations. If enabled, create or connect a Job Tracker with the required properties and default options above, then store its data source ID in `easy-apply.yaml`.

When Notion is enabled, `validate_workspace.py` and connector-side validation must verify at minimum:

- a Notion data source ID is configured;
- the data source is reachable;
- all required properties exist with the expected names;
- property types are compatible with this contract;
- required Priority and Status values exist;
- `File Slug` exists before resume/sync workflows run.

When Notion is disabled, local validation must accept a missing data-source ID and skip connector-side checks.

Do not silently repair destructive schema mismatches during ordinary job-search or resume execution. Report the mismatch and require validation/setup repair.

Adding a missing non-destructive Platform option during first-time platform configuration is allowed.

---

## 12. Schema evolution

This schema is part of the Easy Apply workspace contract.

Rules:

1. Adding an optional property may be backward-compatible.
2. Renaming/removing a required property or changing its type is a breaking change.
3. Breaking workspace/schema changes require an explicit migration path and a `schema_version` change in `easy-apply.yaml`.
4. Runtime workflows must not invent ad-hoc alternative property names when validation fails.
5. User-added unrelated Notion properties must be preserved and ignored by Easy Apply unless explicitly supported later.

---

## 13. Invariants

The implementation must preserve these invariants:

1. Only kept jobs are created in the Job Tracker.
2. Every Easy Apply-created row has a stable `File Slug`.
3. New rows start as `Not Applied`; existing Status values are never automatically changed.
4. `Apply date` is never automatically written by Easy Apply.
5. `Submitted Materials` is owned exclusively by sync and mirrors the complete current local PDF set.
6. A failed multi-file upload must not replace `Submitted Materials` with a partial set.
7. Exact Notion property names are isolated to the Notion integration layer.
8. Job-search does not erase application state when it encounters an existing job.
9. Notion does not replace `seen-jobs.jsonl` as search history.
10. Local application files remain the source of truth for generated materials.
