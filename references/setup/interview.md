# Setup Interview

This file defines the minimum information Easy Apply should collect during initial setup.

Ask only for information needed to build the workspace. Do not turn setup into a long career interview. Candidate facts should primarily come from uploaded resumes and explicit corrections.

## Required questions

Collect:

1. **Target role families** — the main kinds of jobs the user wants to pursue. Use short internal keys later, but let the user describe them naturally first.
2. **Search location** — the user's general preferred location/region. Platform-specific locations are configured only when that platform is first used.
3. **Work-rights facts relevant to screening** — record only what the user explicitly states. Do not infer citizenship, visa type, sponsorship needs, or clearance eligibility.
4. **Resume page target** — normally one integer target used as a default. A confirmed role-family template may intentionally differ.
5. **Search keywords** — the core discovery terms the user wants Easy Apply to use.

## Optional questions

Ask only when needed:

- preferred name/sign-off if unclear from uploaded material;
- persistent writing preferences the user wants applied to all future materials;
- facts that conflict across uploaded resumes;
- whether a real skill/fact should be excluded from generated materials generally.

## Do not ask during initial setup

Do not ask for:

- a default posting-time range; confirm it per search run;
- every future job platform; configure a platform on first use;
- detailed screening thresholds unless the user explicitly wants persistent thresholds;
- cover-letter stories; ask those for each cover letter;
- facts already clear and consistent in uploaded source material.

## Recording answers

Write configurable parameters to `easy-apply.yaml` and factual candidate information to `profile/profile.md`.

Persistent preferences should be stored only when the user clearly asks for a general/default rule. One-off edits for one application must not silently become global preferences.
