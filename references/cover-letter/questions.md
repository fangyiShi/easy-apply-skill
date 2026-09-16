# Cover Letter Questions

This file defines the required user-input checkpoint before Easy Apply drafts a cover letter.

The purpose is to collect application-specific motivation and story context that cannot safely be inferred from `profile.md` or the JD.

---

## 1. Required checkpoint

Run this checkpoint for every cover letter.

Do not skip it because:

- another letter targeted a similar role;
- the resume already contains relevant experience;
- the Skill can infer a plausible motivation;
- a previous employer story sounds reusable.

The user may answer briefly. The goal is not to create an interview questionnaire; it is to avoid fabricated motivation and anecdotes.

---

## 2. What to ask

Ask only the questions needed for the current application. Cover these three areas:

### A. Real connection

Does the user have any genuine connection to the company, industry, product, problem, or type of work?

Examples of useful answers:

```text
used the product
worked in a related domain
encountered the same problem as a user/customer
heard about the company through a real event/contact
has a personal reason for caring about the domain
no specific connection
```

### B. Relevant story or evidence

Is there a particular real experience the user wants to use in the letter?

This may come from work, internship, study, projects, volunteering, customer service, or another confirmed experience.

If several profile facts could support the role, present a small set of candidate angles and let the user choose rather than assuming which one matters most.

### C. Preferred emphasis

What should the letter emphasize most?

Examples:

```text
technical capability
customer/user communication
learning ability
industry/domain interest
software development
support/troubleshooting
ownership
teamwork
career transition
another user-specified angle
```

Do not treat these examples as a fixed list.

---

## 3. Compact default question

When no special clarification is needed, one compact prompt is enough:

```text
Before I draft this cover letter: do you have any real connection to this company/industry, a specific experience or story you want me to use, and any angle you especially want to emphasize? If not, just say “no specific story — use my existing profile facts.”
```

The interaction may be split into follow-up questions only when the user's answer creates a real ambiguity.

---

## 4. If the user has no story

A response such as:

```text
No specific story. Use what is already in my profile.
```

is sufficient.

Do not pressure the user to invent something more personal.

Continue by selecting grounded evidence from `profile.md` and explaining its relevance to the role.

---

## 5. If the user gives new factual information

New facts supplied during this checkpoint may be used for the current application.

Apply the same grounding rules as any other candidate fact:

- preserve what the user actually said;
- do not inflate scope or outcomes;
- ask only when a material ambiguity prevents accurate use.

Do not automatically persist one-off application details into `profile.md` or global writing preferences. Persist them only when the user asks or when the setup/update workflow explicitly confirms they are reusable profile facts.

---

## 6. If the user chooses among suggested angles

When the Skill identifies several plausible grounded angles, present only a small number of genuinely distinct options.

For example:

```text
1. technical problem-solving from a relevant project
2. customer-facing communication from a real role
3. direct domain motivation from a confirmed experience
```

The options must already be supported by known facts. Do not offer invented stories as choices.

Once the user chooses, make that angle prominent but still use other relevant evidence when useful.

---

## 7. What not to ask repeatedly

Do not ask for information already clearly available in the current context, such as:

```text
candidate name
confirmed education
confirmed employment history
known project facts
job title/company from the active JobRecord
```

The checkpoint exists to gather missing application-specific context, not to make the user restate their profile.

---

## 8. Output of the checkpoint

Before drafting, the Skill should be able to summarize internally:

```text
real connection: <fact / none>
story/evidence preference: <fact / none>
primary emphasis: <angle / no preference>
new current-application facts: <facts / none>
```

If all three are `none`/no preference, that is still a valid result. Draft from the strongest grounded profile/JD connections without inventing additional context.