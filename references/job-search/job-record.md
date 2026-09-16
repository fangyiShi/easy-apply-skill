# JobRecord Contract

This file defines the normalized job data contract used by Easy Apply job search.

The goal is simple: every supported job source must convert a discovered listing into the same `JobRecord` shape before screening, deduplication, Notion persistence, or resume generation.

Platform-specific behavior belongs in `sources/<platform>.md`. Screening policy belongs in `rules.md`. This file only defines data, identity, naming, deduplication order, and persistence boundaries.

---

## 1. JobRecord fields

A JobRecord may contain unknown values while discovery is still in progress. A job may only be written to Notion after the fields required by the screening workflow have been resolved.

| Group | Field | Type | Purpose |
|---|---|---|---|
| Identity | `job_key` | string | Cross-platform deduplication key |
| Identity | `file_slug` | string | Stable human-readable identifier used in material filenames |
| Identity | `source` | string | Platform that produced this record, e.g. `linkedin`, `jora` |
| Identity | `source_job_id` | string/null | Stable platform job ID when available |
| Identity | `canonical_url` | string/null | Clean stable listing URL |
| Identity | `application_url` | string/null | Direct application URL when available |
| Job | `company` | string | Employer name |
| Job | `title` | string | Job title |
| Job | `location` | string | Human-readable location |
| Job | `employment_type` | string/null | Full time, part time, casual, contract, internship, etc. |
| Job | `posted_at` | string/null | Platform-reported posting date/time in normalized form when known |
| Requirements | `experience_requirement` | string/null | Compact normalized experience requirement |
| Requirements | `work_rights_requirement` | string/null | Compact work-rights / citizenship requirement |
| Requirements | `clearance_requirement` | string/null | Compact security-clearance requirement |
| Requirements | `core_skills` | array[string] | Skills needed for matching; do not store the full JD |
| Requirements | `cover_letter` | boolean | `true` when the JD or application page mentions a cover letter, including optional |
| Evaluation | `date_status` | enum | `in_range`, `out_of_range`, `unknown` |
| Evaluation | `application_status` | enum | `active`, `closed`, `unknown` |
| Evaluation | `decision` | enum | `keep`, `reject`, `needs_verification` |
| Evaluation | `priority` | enum/null | `P1`, `P2`, `P3`; only used after `decision = keep` |
| Evaluation | `reason` | string | Compact explanation supporting the decision/priority |
| Tracking | `first_seen` | datetime | First time Easy Apply encountered this job |
| Tracking | `last_seen` | datetime | Most recent time Easy Apply encountered this job |

Do not add platform-specific fields to JobRecord unless they are required by downstream Easy Apply workflows. Platform-only details remain inside the source adapter during extraction.

---

## 2. Normalization rules

Normalization is used only for deterministic matching and naming. Preserve the original human-readable `company`, `title`, and `location` values in the JobRecord.

For normalized matching values:

- convert to lowercase;
- trim leading/trailing whitespace;
- collapse repeated whitespace;
- normalize `&` and `and` consistently;
- remove punctuation that does not change meaning;
- do not hard-code country-specific geography rules into the shared normalizer;
- do not aggressively rewrite titles into different job families.

Examples:

```text
"IT & AI Analyst Intern" -> "it ai analyst intern"
"Central City"           -> "central city"
"Amazon Web Services"    -> "amazon web services"
```

When two platforms use genuinely equivalent but textually different location labels, canonicalize them only when the runtime has reliable context. Do not guess geographic equivalence from string shape alone.

Normalization must be implemented deterministically in `scripts/lib/` so the same input always produces the same key.

---

## 3. `job_key`

`job_key` is the default cross-platform deduplication key.

```text
job_key = normalized_company + "|" + normalized_title + "|" + normalized_location
```

Example:

```text
example systems|support engineer|example city
```

If LinkedIn and Jora produce the same normalized company, title, and location, Easy Apply treats them as the same job by default.

This is intentionally simple. Easy Apply does not try to build a perfect global job identity system. If a future real-world case proves this rule is insufficient, the deduplication policy can be extended then.

`job_key` is generated when the JobRecord is created and must not be recomputed from later user edits in Notion.

---

## 4. Same-platform identity

When a source exposes a stable job ID, combine the source namespace with the platform job ID for exact same-platform matching:

```text
source_identity = source + ":" + source_job_id
```

Examples:

```text
linkedin:4281930172
jora:abc123
```

A raw `source_job_id` must never be compared across platforms because different platforms may use overlapping ID formats.

If `source_job_id` is unavailable, use `canonical_url` as the strongest same-platform identifier before falling back to `job_key`.

`source_identity` is a derived comparison value; it does not need to be stored as a separate JobRecord field unless implementation later benefits from it.

---

## 5. `file_slug`

`file_slug` is used for local filenames and the Notion `File Slug` property.

Format:

```text
<company>-<job>
```

Rules:

- lowercase;
- ASCII-friendly where practical;
- words separated with `-`;
- remove punctuation that is unsafe or noisy in filenames;
- use a concise but recognizable job title, normally 2–4 meaningful title words;
- do not use only the company name;
- once written to Notion, do not regenerate it from later Position/Company edits.

Examples:

```text
example-systems-support-engineer
northstar-labs-software-engineer
acme-cloud-platform-engineer
```

Generated material filenames:

```text
resume-<file_slug>.tex
resume-<file_slug>.pdf
cover-letter-<file_slug>.tex
cover-letter-<file_slug>.pdf
```

If a real filename collision occurs, append the smallest stable disambiguator needed, preferably location and then source job ID.

Example:

```text
resume-northstar-software-engineer-example-city.pdf
```

Do not add complexity before an actual collision exists.

---

## 6. Deduplication order

Deduplication happens after a source result has been normalized into a JobRecord.

Use this order:

1. **Same source + same `source_job_id`** -> duplicate.
2. **Same canonical/application URL** -> duplicate.
3. **Same `job_key`** -> duplicate by default, including across platforms.
4. Otherwise -> treat as a new job.

When duplicates are found across platforms, keep one canonical JobRecord for downstream processing. Prefer the version with the clearest active application path and the most reliable/complete information.

Do not open an already sufficiently verified duplicate listing merely to repeat the same evaluation.

---

## 7. `seen-jobs.jsonl`

`state/seen-jobs.jsonl` stores a compact history of all jobs Easy Apply has already evaluated, including rejected jobs. Its purpose is to prevent repeated browser work and repeated screening across search runs.

Each stored record should contain only the fields needed for future matching and reuse:

```json
{
  "job_key": "example systems|support engineer|example city",
  "source": "linkedin",
  "source_job_id": "4281930172",
  "canonical_url": "https://...",
  "decision": "keep",
  "first_seen": "2026-09-16T10:20:00+10:00",
  "last_seen": "2026-09-16T10:20:00+10:00"
}
```

`first_seen` records when Easy Apply first encountered the job. `last_seen` records the most recent encounter. These timestamps are lifecycle/debug metadata; they are not used to decide whether the job is currently open.

Do not delete seen jobs on a fixed 7-day schedule. The records are intentionally compact. Add archival or compaction only if file size becomes a real problem.

When the same job is encountered again, `seen_jobs.py` is responsible for returning the existing decision and updating the latest seen metadata according to its implementation. The workflow should not manually parse the JSONL file.

---

## 8. Live listing rule

`seen-jobs` does not prove that a job is still available.

Before a job enters the final shortlist, and again before resume generation when necessary, Easy Apply must confirm that the live listing/application path is still active.

If the listing has expired, closed, or no longer has a valid application path:

```text
application_status = closed
```

Do not generate new application materials for a closed job unless the user explicitly asks for them for another purpose.

Easy Apply does not keep a historical JD snapshot for the purpose of applying after a listing has closed.

---

## 9. Persistence boundaries

### Notion

Notion stores only jobs that pass screening (`decision = keep`) and are useful for the user's application workflow.

The JobRecord-to-Notion mapping is defined in `references/notion/schema.md`, not here.

### seen-jobs

`seen-jobs.jsonl` stores every evaluated job, including `keep` and `reject`, so future searches can avoid repeated work.

### Local artefacts

Application material filenames use `file_slug`. They do not use `job_key` because `job_key` is for machine matching and contains characters that are not intended for user-facing filenames.

---

## 10. Invariants

The implementation must preserve these invariants:

1. Every normalized job has a `job_key` and `file_slug` before it is written to Notion.
2. `job_key` is derived deterministically from normalized company, title, and location.
3. Same `source + source_job_id` means the same platform listing.
4. Same `job_key` is treated as the same job by default for cross-platform deduplication.
5. `file_slug` remains stable after persistence, even if the user later edits Company or Position in Notion.
6. Notion contains kept jobs; `seen-jobs` contains all evaluated jobs.
7. `seen-jobs` is an optimization/history mechanism, not evidence that a listing is still active.
8. Resume/cover-letter filenames are derived from the persisted `file_slug`, never rebuilt ad hoc from Company or Position.
9. JobRecord does not store full JD text.
10. Platform-specific extraction rules do not leak into this contract.
