# Cover Letter Workflow

This file defines the workflow for generating one cover letter after a job has already been screened and selected for application preparation.

Related references:

- `rules.md` — writing and factual rules.
- `questions.md` — required user-input step before drafting.
- `../common/grounding.md` — factual grounding boundary.
- `../notion/schema.md` — persistence contract.

---

## 1. Preconditions

Generate a cover letter only when:

- the job is still active;
- the JobRecord belongs to a kept job;
- `cover_letter = true`, or the user explicitly asks for a letter;
- the current JD/application instructions are available enough to understand what the employer is asking for.

If the listing is closed, do not prepare a new application letter unless the user explicitly wants it for another purpose.

If the employer explicitly states that AI-written application content is not allowed, do not ghostwrite the letter. The Skill may still help the user understand the prompt, ask planning questions, or proofread text the user wrote.

---

## 2. Gather context

Load only the context needed for this application:

```text
JobRecord
current JD/application instructions
profile.md
selected/tailored resume when available
current user answers from questions.md
writing preferences from easy-apply.yaml when relevant
```

Do not use unrelated historical cover letters as factual sources.

Do not assume that a story or motivation used for one employer also applies to another.

---

## 3. Identify the strongest match points first

Before drafting prose, identify approximately 3–5 defensible connections between the candidate and the role.

Examples of useful match types:

```text
relevant technical capability
similar responsibility/problem type
industry/domain exposure
customer/user-facing experience
project/work evidence
motivation grounded in a real experience
```

Reject weak or forced matches before writing.

The goal is not to mention everything in the resume. Select the few facts that best answer:

```text
Why this candidate?
Why this role/employer?
```

---

## 4. Ask the user before drafting

Run the user-input step in `questions.md` for every cover letter.

At minimum, establish whether the user has:

- a real connection to the company/industry/problem;
- a specific experience or story worth using;
- a preferred angle to emphasize.

If the user has no specific story, that is acceptable. Continue using confirmed profile facts without inventing one.

Do not skip this step merely because a previous cover letter targeted a similar role.

---

## 5. Build the narrative

Connect the selected facts into a coherent argument rather than rewriting resume bullets as sentences.

A useful structure is:

1. **Opening** — who the candidate is, the role, and a genuine reason for interest when one exists.
2. **Evidence** — one or two compact sections showing the strongest relevant experience/capability.
3. **Employer connection** — why this particular role/company makes sense based on known facts, not generic praise.
4. **Close** — concise interest and appropriate closing details.

This is guidance, not a mandatory paragraph count. Prefer clarity over forcing every letter into the same shape.

When possible, use one coherent theme that connects the candidate's evidence with the role. Do not manufacture a theme when the evidence does not support one.

---

## 6. Draft with grounding constraints

Apply `rules.md` and `../common/grounding.md` while drafting.

Every factual candidate claim must come from:

- `profile.md`; or
- explicit information the user supplied for this application.

The JD may determine what to emphasize, but it must never become a source for candidate facts.

Do not invent:

```text
company interactions
incidents
leadership stories
metrics
production experience
motivation
customer outcomes
technical tools used by the candidate
```

---

## 7. Review before rendering

Review the draft for:

```text
factual grounding
role/employer specificity
non-repetition of the resume
clear reason for interest
concise structure
unsupported claims
unnecessary generic praise
company/addressee accuracy
```

If the JD and an aggregator disagree materially about the role, use the most authoritative current source and surface the conflict to the user rather than silently choosing a convenient version.

---

## 8. Render and validate

When the workspace uses PDF output:

1. save the source file using the persisted `file_slug`;
2. compile/render the letter;
3. run deterministic checks where available;
4. perform a final semantic factual check;
5. ensure the document is readable and visually complete.

Expected filename pattern:

```text
cover-letter-<file_slug>.tex
cover-letter-<file_slug>.pdf
```

Do not rebuild filenames ad hoc from later-edited Company/Position values.

---

## 9. Persist materials

Local files are the source of truth.

When `notion.enabled` is true and sync is requested, use the shared Notion sync workflow. Updating `Submitted Materials` must follow the full-list replacement rule defined in the Notion module. When Notion is disabled, keep the valid local letter and report that remote sync was skipped.

Cover-letter generation must not change the user's application `Status`.

---

## 10. Human control

The user remains the final reviewer.

A generated letter is a draft application material, not authorization to submit an application. Easy Apply does not submit, upload to an employer, or send the letter unless a separate explicitly authorized workflow supports that action.
