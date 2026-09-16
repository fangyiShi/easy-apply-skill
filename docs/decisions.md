# Key Design Decisions

This document records the major current decisions behind Easy Apply. Runtime rules live in `SKILL.md` and `references/`; this file explains why the architecture looks the way it does.

## One Skill, modular references

Easy Apply remains one Skill for now. Search, resume, cover-letter and sync are separate reference modules so the runtime can load only relevant context without forcing users to install/manage multiple Skills.

## User-specific behavior belongs in the workspace

Role targets, locations, work-rights facts, search keywords, exclusions, skills, resume templates and writing preferences are not hard-coded into the reusable Skill.

Historical personal prompts remain useful as feedback/evaluation sources, not as public runtime rules.

## Platform adapters describe constraints, not click scripts

Adapters preserve stable browser knowledge such as IDs, URL/filter semantics, virtualized lists, redirects and stop/failure conditions. They avoid brittle instructions like fixed screen positions or pixel scrolling.

## Job identity stays intentionally simple

Same-platform identity prefers `source + source_job_id`; clean URLs are secondary evidence; cross-platform dedupe defaults to normalized `company|title|location`.

The system does not attempt to solve global job identity perfectly before a real failure requires more complexity.

## seen-jobs is compact history, not active-job truth

`seen-jobs.jsonl` may grow over time. Fixed seven-day deletion was rejected because compact history is useful for dedupe/debugging and cheap to retain. Live availability must still be verified when it matters.

## No historical JD snapshot for applying to closed jobs

Easy Apply does not use an old saved JD to prepare a new application after the live role has closed. The live job/application path is rechecked before generating new material.

## Resume templates are approved baselines

Tailoring starts from a user-confirmed role-family template and makes targeted changes. Whole-document regeneration is avoided because it costs more context/output, destabilizes layout and increases factual drift.

Resume format and role-family content are separate. One canonical layout in the user workspace controls shared presentation, while each target role family has its own confirmed content template. The public Skill contains only a generic layout scaffold.

## Resume length does not limit candidate truth

Setup explicitly asks for the resume page target; it is never inferred from an uploaded file. `profile.md` retains the complete confirmed candidate history, while each role-family or job-specific resume selects only the most relevant subset.

## Notion is an explicit workspace choice

`notion.enabled` distinguishes an intentional opt-out from an incomplete connection. Disabled workspaces do not call Notion; enabled workspaces require a validated data source before Notion-dependent operations.

## profile.md is candidate truth

Candidate claims must come from `profile/profile.md` or explicit current-session user information. Role-family templates are content/structure baselines, not independent evidence sources.

## Cover letters require a human checkpoint

Every cover letter asks the user for role/company connection, usable story and preferred angle before drafting. A previous letter for a similar role does not remove this requirement.

## Local PDFs are the source of truth for Notion materials

When Notion is enabled, Submitted Materials is replaced as a complete list. If a cover letter is added later, the current resume and cover letter are both uploaded again before one property replacement. Partial upload failure must not create partial remote state.

## Regression cases replace prompt accretion

When a feedback loop exposes a recurring failure, prefer adding a concise general rule plus a regression case rather than continuously appending highly specific historical patches to the runtime prompt.
