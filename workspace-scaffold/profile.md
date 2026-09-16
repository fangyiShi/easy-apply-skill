# Candidate Profile

This file is the factual source of truth for candidate-specific claims used by Easy Apply.

Only include information that comes from the user's uploaded materials or that the user has explicitly confirmed. Resume templates and generated application materials may select, reorder, or rephrase these facts, but they do not create new facts.

---

## Basic Information

- Name:
- Preferred name:
- Email:
- Phone:
- Location:
- Preferred sign-off name:

## Job Search Background

Describe the user's target direction, relevant context, and high-level boundaries that help with application writing. Do not duplicate configurable search parameters from `easy-apply.yaml` here.

## Work Experience

For each role, record factual details only.

### <Company> — <Role>

- Location:
- Employment type:
- Dates:
- Responsibilities and work actually performed:
- Tools / technologies actually used:
- Outcomes or measurable results, only when verified:
- Important boundaries or clarifications:

## Internships / Volunteering

Use the same factual structure as Work Experience when relevant.

## Projects

### <Project Name>

- Context / purpose:
- Role:
- Work actually performed:
- Tools / technologies actually used:
- Verified outcomes:
- Important boundaries or clarifications:

## Education

### <Institution> — <Qualification>

- Location:
- Dates:
- Major / field:
- Relevant factual notes:

## Skills

List skills the user genuinely possesses. Prefer normalized canonical names, with evidence available elsewhere in this profile.

### Languages

- 

### Frameworks / Libraries

- 

### Systems / Platforms

- 

### Cloud / Infrastructure

- 

### Databases / Data

- 

### Support / Administration Tools

- 

### Other Technical Skills

- 

## Certifications

- Certification:
  - Issuer:
  - Year:
  - Notes:

## Writing and Application Preferences

Only store preferences that the user has explicitly asked Easy Apply to apply generally, for example "all resumes", "from now on", "always", or "remember this preference".

Examples of valid persistent preferences:

- preferred name/sign-off;
- tone and formality;
- wording or punctuation preferences;
- information the user genuinely has but does not want emphasized generally.

Do not turn a one-off edit to a single application into a persistent preference unless the user explicitly requests it.

## Profile Maintenance Rules

1. This file is the candidate factual source of truth.
2. Do not infer or add facts from a job description.
3. Do not add unsupported years of experience, production exposure, leadership, ownership, metrics, tools, responsibilities, certifications, or qualifications.
4. When uploaded resumes conflict, ask the user or preserve the uncertainty instead of silently choosing one version.
5. When the user explicitly corrects a fact, update the canonical fact here before relying on it in future materials.
6. `easy-apply.yaml` stores configurable parameters and exclusions; do not duplicate them here unless they are also meaningful factual background.
