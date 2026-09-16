# Job Screening Rules

This file defines reusable screening principles. Candidate-specific thresholds, target roles, locations, exclusions, and preferences belong in the user's workspace.

## 1. Evidence first

Do not make a keep/reject decision from title or keyword alone when the job could reasonably belong to a configured target role.

Use the strongest available evidence in this order:

1. employer/ATS listing;
2. full platform job detail;
3. platform card/snippet;
4. web-search snippet.

If required information is missing or ambiguous, use `needs_verification` instead of guessing.

## 2. Posting date

Every job must be classified as:

```text
in_range / out_of_range / unknown
```

- `out_of_range` -> reject for this run.
- `unknown` -> needs verification.
- platform freshness filters help narrow results but do not replace checking the displayed posting/reposting time.

Use the user's actual requested time boundary, not a hard-coded default.

## 3. Eligibility

Compare job requirements with confirmed candidate facts only. Never infer citizenship, visa status, work rights, sponsorship needs, or clearance eligibility.

Reject when the job clearly requires an eligibility condition the candidate does not meet.

General work-rights language is not automatically equivalent to citizenship or permanent residency. Read the complete requirement before deciding.

If the wording is incomplete or conflicting, keep it unresolved rather than assuming eligibility.

## 4. Role fit

A job is relevant when its actual responsibilities align with a configured target role family.

Use:

- responsibilities;
- level/seniority;
- required experience;
- core hard skills;
- explicit user exclusions/preferences.

Do not hard-code one user's experience threshold, salary threshold, technology stack, or unwanted role categories in this reusable file.

Candidate skills come from `profile.md`. Missing skills may lower fit or priority, but must never be fabricated as matches.

## 5. Application availability

A shortlisted job must have an active role-specific application path.

Mark a job closed when the authoritative listing states that applications are closed/expired or when the advertised application path no longer reaches the specific role.

When an aggregator and an employer/ATS page conflict, prefer the employer/ATS status.

If availability cannot be established, use `needs_verification`.

## 6. Cover letter

`cover_letter` is boolean.

Set `true` when the JD or visible application instructions mention a cover letter or equivalent, including when optional. Otherwise set `false` after the relevant instructions have been checked.

This field does not affect keep/reject; it controls the downstream material workflow.

## 7. Decision

### keep

Use when:

- the job is within the requested time range;
- no confirmed hard eligibility restriction excludes the candidate;
- the role is relevant to configured targets;
- the application is active;
- enough evidence exists to explain the result.

### reject

Use only for a clear reason, such as:

- outside requested time range;
- eligibility requirement the candidate cannot meet;
- clearly outside configured role scope;
- explicitly excluded by user preference;
- closed application.

### needs_verification

Use when a potentially relevant job cannot yet be classified because a required fact is unresolved.

## 8. Priority

Assign priority only after `decision = keep`.

```text
P1 = strong fit / high attention
P2 = viable with meaningful gap, uncertainty, or weaker fit
P3 = speculative but still worth retaining
```

Consider the combination of:

- role fit;
- experience/level fit;
- core skill match;
- eligibility friction;
- ambiguity;
- explicit user preferences.

Do not turn priority into a universal numeric scoring formula unless future testing demonstrates a need.

## 9. Reason / Appendix

Keep the explanation short and decision-oriented. Capture only what the user needs to understand why the job was kept, downgraded, or rejected.

For kept jobs, include:

```text
experience/level
core match
eligibility
important gap or caveat
```

Do not copy the full JD.
