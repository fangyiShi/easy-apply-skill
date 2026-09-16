# LinkedIn Jobs Source Adapter

This file describes only LinkedIn-specific discovery behavior. Shared screening belongs in `../rules.md`; shared identity and deduplication belong in `../job-record.md`.

User-specific keywords, locations, target levels, role families, skills, and exclusions must come from the workspace/current request.

---

## 1. Search behavior

Build a LinkedIn Jobs search using the current run's requested/configured:

```text
keyword
location
posting-time range
experience level, when configured
employment type or other explicit filters
```

Do not hard-code one user's keyword, geography, or target level.

LinkedIn may preserve UI/session state in parameters that are not true search policy. Keep intended search filters separate from transient state such as selected-job or tracking parameters.

---

## 2. Date filter semantics

LinkedIn commonly represents recent-posting filters with:

```text
f_TPR=r<seconds>
```

This is a rolling time window, not a calendar-date range.

For a requested natural-date interval:

1. choose a rolling window broad enough to include the earliest requested boundary;
2. preserve the other intended search filters;
3. verify displayed posting/reposting time against the user's actual requested interval;
4. post-filter items outside the exact interval.

Do not treat `f_TPR` alone as final evidence. Reposted, promoted, recommended, or cached results may still need date verification.

---

## 3. Stable identity and links

LinkedIn job ID is the preferred source identity.

It is often available in forms such as:

```text
/jobs/view/<job_id>/
currentJobId=<job_id>
job-card/detail links
```

Store only the raw job ID in `source_job_id`; the shared layer namespaces it with `source = linkedin`.

Prefer a stable `/jobs/view/<job_id>/` detail URL for persistence when available.

Do not use search-result position as identity.

---

## 4. Result enumeration

LinkedIn result lists may be virtualized, dynamically loaded, and reordered.

For each accessible page/loading batch:

1. collect stable job IDs from reachable cards before opening details;
2. continue loading/scrolling until the current batch stops producing new IDs;
3. freeze the discovered ID set conceptually;
4. normalize and deduplicate cards;
5. open only jobs that still need detail evidence;
6. if the list changes after detail inspection, reconcile newly appeared IDs before moving on.

Completeness should be judged by stable IDs, not click count or card order.

The exact clicks, coordinates, and scroll distances are intentionally left to Computer Use at runtime.

---

## 5. Card versus detail evidence

Cards commonly provide some of:

```text
title
company
location
posting age/reposted label
job ID/detail link
short level or description hints
```

Use card evidence for cheap triage only when explicit.

Open the detail panel/page when needed to resolve:

```text
ambiguous posting/reposting time
experience/seniority
work-rights/citizenship wording
security-clearance wording
actual responsibilities and hard skills
employment type
cover-letter/application instructions
application status and application URL
```

When the detail panel updates in place, confirm the selected job ID/title before extracting evidence.

---

## 6. Application behavior

LinkedIn listings may use:

```text
Easy Apply
Apply
Apply on company site
external ATS/employer redirect
```

Job discovery must not submit an application.

For current availability, an authoritative employer/ATS page should override a stale LinkedIn listing when they conflict.

A LinkedIn page that still loads is not sufficient proof that the role is actively accepting applications.

---

## 7. Reposted, promoted, and recommended results

LinkedIn may insert:

```text
Reposted jobs
Promoted/Sponsored jobs
Recommended jobs
The same job under multiple keyword searches
```

These remain subject to shared date, relevance, eligibility, and deduplication rules.

When `Reposted` is displayed, preserve that fact when useful and evaluate the displayed reposting time according to the current run's date policy.

Process the same LinkedIn job ID once per run.

---

## 8. Known browser quirks

Keep these platform-specific constraints:

- result lists may be virtualized, so off-screen cards may unload;
- opening a job can update a side panel without conventional navigation;
- promoted/recommended cards can change ordering;
- a list may load more jobs while scrolling;
- search filters can be lost or changed after redirects/login transitions;
- transient parameters such as `currentJobId` should not be mistaken for search filters.

Therefore:

- inventory stable IDs before relying on the current visual layout;
- verify selected job identity before extracting detail fields;
- verify search/filter state after navigation changes;
- compare ID sets to determine whether new results actually loaded.

Do not encode card ordinals, pixel positions, or a fixed sequence of UI clicks.

---

## 9. Completion and failure

LinkedIn search is complete for this source when all accessible results under the current filters have been enumerated according to the observable pagination/loading behavior, or when a configured run-depth limit is reached.

Verify movement between result pages/batches using at least one stable signal such as:

```text
page/offset change
first job ID change
result ID set change
```

If login walls, CAPTCHA, rate limits, bot protection, inaccessible pagination, or UI failures prevent further access:

- do not bypass the restriction;
- preserve already discovered results;
- use web search/employer pages to verify specific jobs when useful;
- continue other configured sources where possible;
- report LinkedIn coverage as incomplete.

Never claim exhaustive coverage when access was partial.

---

## 10. Adapter invariants

1. LinkedIn mechanics stay here; screening policy does not.
2. User-specific preferences come from workspace/current request.
3. Stable job ID is preferred over card position.
4. `f_TPR` is a recall filter, not final date proof.
5. Virtualized/dynamic lists require ID-based accounting.
6. Employer/ATS evidence wins when current application availability conflicts.
7. Browser instructions describe durable constraints and quirks, not brittle click-by-click scripts.
