# Jora Source Adapter

This file describes only Jora-specific discovery behavior. Shared screening belongs in `../rules.md`; shared identity and deduplication belong in `../job-record.md`.

User-specific keywords, locations, target roles, experience limits, skill preferences, and exclusions must come from the workspace/current request.

---

## 1. Search behavior

Use the Jora regional site appropriate to the configured search.

Map the current run's:

```text
keyword
location
radius, when configured
posting-time range
employment type or other explicitly requested filters
```

onto Jora's available controls.

Do not hard-code one user's search terms, location, radius, or freshness window.

Jora date filters may be coarser than the user's requested range. Use the smallest available window that still covers the requested period, then verify the displayed posting time against the real requested boundary.

---

## 2. Stable identity and links

Prefer, in order:

```text
1. Jora source job ID when exposed
2. stable Jora job-detail URL
3. shared job_key fallback
```

Store only the raw platform ID in `source_job_id`; the shared layer namespaces it with `source = jora`.

Prefer a clean stable detail URL over tracking-heavy URLs. Temporary parameters may be removed only when the resulting URL has been verified to open the same listing.

Never use visual card position as job identity.

---

## 3. Result enumeration

Jora is normally processed page by page.

For each accessible page:

1. inventory the reachable job cards before opening details;
2. capture stable ID/link plus basic card fields;
3. normalize them into partial JobRecords;
4. deduplicate before opening details;
5. inspect details only when shared workflow/rules require more evidence;
6. move on only after discovered cards have been accounted for.

The exact clicks and scroll amounts are intentionally not specified. Computer Use should adapt to the current UI.

---

## 4. Card versus detail evidence

Cards commonly provide some of:

```text
title
company
location
posting age/date
short snippet
stable detail link
```

Treat snippets as partial evidence only. They may be truncated or aggregator-generated.

Open the detail page when needed to resolve fields such as:

```text
experience/seniority
work-rights or citizenship wording
security-clearance wording
actual responsibilities and hard skills
employment type
cover-letter mention
application status/application URL
ambiguous posting date
```

Do not copy the whole JD into the working context when targeted evidence is enough.

---

## 5. Aggregator and application behavior

Jora may aggregate or repost listings from employers, recruiters, or other job sources.

When Jora conflicts with a current employer/ATS page, prefer the employer/ATS for:

```text
current requirements
application availability
role-specific apply URL
```

A visible Jora page does not by itself prove that applications are still open.

Do not submit an application during job discovery.

---

## 6. Known browser quirks

Keep these Jora-specific reliability rules:

- preserve stable IDs/links before navigating away from the result page;
- after returning from a detail page, verify the expected keyword/filter/page state is still active;
- duplicate or reposted listings may appear under multiple searches;
- a detail/apply link may redirect through another source before reaching the employer/ATS;
- freshness filters may contain items that still need explicit posting-date verification.

Do not encode pixel positions, card ordinals, or fragile click sequences.

---

## 7. Completion and failure

Search is complete for this source when the observable end of accessible results is reached, or when the current run's configured search-depth condition is satisfied.

Do not permanently hard-code historical values such as "15 pages" or "3 empty pages" into this adapter. Those are search-strategy settings, not Jora platform facts.

If pagination, login, bot protection, Cloudflare, broken filters, or other access problems prevent completion:

- do not bypass the restriction;
- preserve already discovered results;
- use an authoritative employer page or web search for a specific listing when useful;
- continue other configured sources where possible;
- report Jora coverage as incomplete.

Never fabricate missing fields or claim exhaustive coverage after an access failure.

---

## 8. Adapter invariants

1. Jora-specific mechanics stay here; screening policy does not.
2. User-specific search preferences are read from workspace/current request.
3. Stable IDs/links are preferred over visual position.
4. Jora freshness filters are not final proof of posting date.
5. Employer/ATS evidence wins when a current application state conflicts with an aggregator listing.
6. Browser instructions describe stable constraints and quirks, not brittle step-by-step UI scripts.
