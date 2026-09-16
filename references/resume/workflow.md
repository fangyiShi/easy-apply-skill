# Resume Workflow

This file defines the reusable workflow for generating a tailored resume for a job. Content truth is governed by `../common/grounding.md`; resume content rules are in `rules.md`.

The workflow starts from an approved role-family template. A template is a baseline, not a finished application.

---

## 1. Inputs

For each resume, use only:

- the live job listing / application page;
- the normalized job record and persisted `file_slug`;
- `profile/profile.md` as the candidate factual source of truth;
- the closest confirmed template from `profile/resume-templates/`;
- `easy-apply.yaml` resume settings;
- current-session user facts explicitly provided for this application.

Do not use another tailored resume as a factual source.

---

## 2. Confirm the job is still active

Before generating new application material, confirm that the specific job is still open and has a usable application path.

If the listing is closed or the specific application path is gone, stop resume generation for that job unless the user explicitly wants a resume for another purpose.

Prefer the employer/ATS listing when an aggregator conflicts with it.

---

## 3. Select the baseline template

Choose the configured role-family template whose primary responsibilities are closest to the JD.

Use the work itself, not employer prestige or title alone.

If no template is a close fit:

1. start from the closest existing template;
2. make the necessary larger tailoring for this job;
3. after the application material is complete, suggest creating a new reusable role-family template only if the mismatch is likely to recur.

Do not create a new template for every job.

---

## 4. Tailor the resume

Copy the selected template to a new job-specific file and make targeted edits.

Typical tailoring areas:

```text
summary / profile
skill ordering and relevant skill selection
experience/project ordering
bullet emphasis and wording
JD terminology where factually supported
```

Tailoring means changing what is emphasized and how confirmed facts are expressed. It does not mean inventing missing experience.

Prefer localized edits over regenerating the entire document. Preserve approved layout, stable sections and unrelated content unless the JD gives a reason to change them.

---

## 5. Grounding check

Before finalizing content, apply `../common/grounding.md`.

Verify that:

- every factual claim is supported by `profile.md` or explicit current-session user information;
- no unsupported tool, responsibility, metric, seniority level or production experience has been introduced;
- user exclusions in `resume.exclude` are respected;
- JD wording has not been copied in a way that falsely upgrades candidate experience.

If an attractive JD term is not supported by candidate evidence, omit it or describe the nearest truthful capability instead.

---

## 6. Build and validate

Compile the job-specific `.tex` into PDF using the approved build path.

Validate at least:

```text
PDF builds successfully
page count respects the configured/template target
text is selectable
no section or bullet is visibly clipped
no broken characters or missing content
layout remains readable
resume is not accidentally almost empty because tailoring removed too much content
```

Automated checks catch deterministic failures. A final visual/semantic review is still required for layout quality and factual accuracy.

Do not delete useful truthful content merely to fix a small layout overflow when spacing/layout can solve it safely.

---

## 7. Save artefacts

Use the persisted JobRecord `file_slug`.

```text
artefacts/resume/resume-<file_slug>.tex
artefacts/resume-pdf/resume-<file_slug>.pdf
```

Do not regenerate the slug from later-edited Notion Company/Position values.

---

## 8. Sync

After a valid PDF exists, sync application materials according to `../notion/sync.md`.

Resume generation may upload/update material files, but it must not change an existing application `Status`.

If a cover letter is required, the cover-letter workflow runs separately and may later cause the full Submitted Materials list to be replaced with both current PDFs.

---

## 9. Batch behavior

When processing multiple reviewed jobs:

- handle each job independently;
- do not let facts or JD wording leak from one job into another;
- skip jobs whose current resume already satisfies the requested generation action unless the user asks to regenerate;
- report skipped/failed jobs explicitly rather than silently dropping them.

A batch is complete only when every selected job has one of: generated, skipped with reason, or failed with reason.

---

## 10. Human control

Easy Apply prepares application material; it does not submit applications automatically.

The user decides whether to apply and controls application Status.