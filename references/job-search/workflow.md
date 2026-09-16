# Job Search Workflow

This file defines the reusable Easy Apply search pipeline. Platform mechanics belong in `sources/`; screening policy belongs in `rules.md`; normalized data and deduplication belong in `job-record.md`.

## 1. Resolve the search request

Use the current request plus `easy-apply.yaml` to resolve:

- keywords;
- platforms;
- location;
- posting-time range;
- any explicit per-run overrides.

If the user did not specify a posting-time range, ask before searching. Do not infer citizenship, visa status, sponsorship needs, or other eligibility facts.

## 2. Discover jobs

Use two discovery paths when available:

1. Web search for publicly indexed listings and employer/ATS pages.
2. Each requested job platform using its source adapter.

Web search does not replace platform search. Platform search may reveal listings that public web search misses.

Convert every useful result into a partial `JobRecord` as early as possible.

## 3. Deduplicate before expensive work

Before opening full job details:

- compare against jobs already found in the current run;
- query persisted seen-job state;
- apply the identity rules in `job-record.md`.

Reuse an existing decision when the same job was already evaluated and current evidence does not materially contradict it.

## 4. Verify only what is needed

Use card/search-result evidence first. Open the detail page only when required to resolve fields needed for screening.

Resolve in this order:

1. posting date;
2. hard eligibility restrictions;
3. role level / experience;
4. role relevance and skill match;
5. active application path;
6. cover-letter mention for jobs that remain viable.

Stop expensive analysis after a confirmed hard rejection.

## 5. Evaluate

Apply `rules.md` and set:

```text
decision = keep / reject / needs_verification
```

Only kept jobs receive a priority:

```text
P1 / P2 / P3
```

A job can enter the shortlist only when its posting date is in range, its application is active, no unresolved hard restriction remains, and enough evidence exists to explain the decision.

## 6. Persist

For every evaluated job:

- update seen-job state through `scripts/seen_jobs.py`.

For kept jobs only, when `notion.enabled` is true:

- create the Notion record according to `references/notion/schema.md` if it does not already exist;
- set initial Status to `Not Applied`;
- never modify an existing application Status.

When `notion.enabled` is false, do not call Notion. Keep local seen-job state and include kept jobs in the report, making clear that no remote tracker row was created.

Job search does not generate application materials or submit applications.

## 7. Report

Return a compact report containing:

- search scope and time range;
- sources attempted and whether coverage was complete;
- keep / reject / needs-verification counts;
- kept jobs grouped by configured role family and priority;
- relevant rejected jobs with short reasons;
- access failures or incomplete source coverage.

Do not dump full JDs, DOM text, or raw browser state into the report.

## 8. Context discipline

Job search should load only:

- the search request;
- search configuration;
- relevant candidate skills/eligibility facts;
- `workflow.md`, `rules.md`, `job-record.md`;
- adapters for the sources used in this run;
- seen-job state through the helper script.

Do not load resume templates, cover-letter rules, or old generated materials during search.
