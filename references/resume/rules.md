# Resume Rules

This file defines shared resume-writing rules. Candidate truth comes from `../common/grounding.md`; execution order is defined in `workflow.md`.

The goal is a resume that is truthful, clearly targeted to the job, ATS-readable, and still recognizably based on the user's approved template.

---

## 1. Tailor from evidence, not from keywords alone

Use the JD to decide what to emphasize, not what to invent.

A strong tailored resume should reflect the job's:

- primary responsibilities;
- core hard skills/tools;
- recurring terminology;
- seniority/level;
- domain context when relevant.

Only use JD wording when the underlying claim is already supported by candidate evidence.

---

## 2. Preserve the approved template

The selected role-family template is the baseline for structure and presentation.

Prefer targeted edits to:

```text
summary/profile
skills
section/item ordering
individual bullets
```

Do not rewrite the entire resume just to make it look more tailored. Large structural changes should have a clear reason.

Do not create a new template merely because one job uses different wording.

---

## 3. Summary / profile

Keep the opening summary concise and role-focused.

It should communicate:

- the candidate's relevant professional direction;
- the strongest evidence for this job;
- important technical/domain context when supported.

Avoid generic claims such as `highly motivated`, `passionate`, or `excellent communicator` unless the surrounding evidence makes them useful.

Do not turn aspirations into experience claims.

---

## 4. Skills

Skills sections should contain actual capabilities, tools, technologies, methods or clearly defined domain knowledge.

If the template contains a technical-skills section, do not fill it with process phrases that belong in experience bullets, such as generic escalation, documentation, ticket triage or stakeholder communication, unless the template intentionally has a separate operational/process category.

Rules:

- prioritize skills relevant to the JD;
- preserve important confirmed skills even if the JD uses a synonym;
- use aliases carefully without implying broader experience;
- do not add a skill just because it appears in the JD;
- do not list user-excluded items.

---

## 5. Experience and project bullets

Bullets should describe concrete work, not keyword lists.

Prefer this shape when the facts support it:

```text
action + object/context + meaningful technical detail + outcome/purpose
```

A bullet does not need a numeric metric if no real metric exists.

Allowed tailoring includes:

- choosing the most relevant true details;
- moving relevant bullets/items earlier;
- replacing vague language with precise supported terminology;
- combining overlapping supported facts for clarity.

Not allowed:

- inventing metrics;
- upgrading participation into ownership/leadership;
- converting lab/course/personal work into production employment;
- claiming tools not actually used;
- changing the scale, user base, environment or responsibility level without evidence.

---

## 6. Ordering

Order content for relevance while preserving chronology where the template relies on it.

Within flexible sections:

- put the most relevant skills first;
- put the most relevant projects/experience higher when the template allows it;
- emphasize evidence that directly supports the job's primary work.

Do not reorder purely to imitate the JD's keyword sequence.

---

## 7. ATS readability

Unless the user's confirmed template intentionally requires otherwise, prefer:

- single-column reading order;
- standard section headings;
- selectable PDF text;
- plain text for important content rather than images/icons;
- no decorative tables that can break extraction;
- conventional dates and employer/role labels;
- job-relevant terminology used naturally.

ATS optimization must never override factual accuracy or basic human readability.

---

## 8. Length and density

Respect the page target configured in `easy-apply.yaml` or intentionally defined by the selected template.

When the resume slightly overflows:

1. remove redundancy;
2. tighten wording;
3. use reasonable layout/spacing adjustments;
4. remove lower-value content only when necessary.

Do not truncate a useful sentence merely to force a page count.

When the document is visibly underfilled, first check whether relevant supported content was omitted before artificially increasing spacing or font size.

There is no universal required number of bullets per role. Use enough content to show the strongest relevant evidence without filler.

---

## 9. JD terminology

Mirroring employer terminology can improve clarity and ATS matching when it refers to the same real capability.

Examples of safe adaptation:

```text
Azure AD -> Microsoft Entra ID / Azure AD, when supported
service desk -> service desk, when the candidate actually performed comparable work
automated testing -> only when testing was actually automated
```

Do not perform semantic substitution that changes the fact.

Examples of unsafe adaptation:

```text
used one ticketing system -> claim a different named ticketing system
built a lab -> claim production administration
assisted a team -> claim led the team
course project -> claim commercial deployment
```

---

## 10. Candidate-specific preferences

Reusable resume rules must not contain one person's:

- exact role families;
- certifications to include/exclude;
- tools they do or do not know;
- licence/working availability details;
- preferred industries;
- personal page-count exceptions.

Those belong in `profile.md`, `easy-apply.yaml`, or the confirmed role-family templates.

---

## 11. Quality gate

A resume is ready only when all are true:

```text
truthful and grounded
clearly tailored to this JD
uses the correct persisted file_slug
builds successfully
meets intended page/layout constraints
ATS-readable
contains no accidental cross-job content
has passed a final semantic review
```

If the document looks polished but fails grounding, it is not ready.