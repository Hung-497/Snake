# CONTEXT.md Format

`CONTEXT.md` is a compact project glossary.

It is not:
- a feature specification;
- a scratchpad;
- an implementation document;
- a development diary;
- a decision log;
- a ticket list.

## Format

```md
# <Context Name>

<One or two sentences describing this project/domain context.>

## Language

**Canonical Term**:
One or two sentences defining what the term means in this project.
_Avoid_: confusing synonym, another synonym

**Another Term**:
One or two sentences defining the term.
_Avoid_: alternative wording
```

## Rules

- Include only project/domain-specific terms.
- Do not include general programming concepts.
- Prefer one canonical term for one concept.
- Keep each definition to 1–2 sentences.
- Define what the concept is, not how it is implemented.
- Use `_Avoid_` only when competing terminology could cause confusion.
- Preserve existing terminology unless the discussion intentionally changes it.
- Do not duplicate terms.
- Replace obsolete definitions instead of keeping historical versions.
- Do not record feature requirements.
- Do not record implementation details.
- Do not record discussion history.
- Keep the file compact.

## Updating

Do not rewrite `CONTEXT.md` after every answer.
Collect glossary changes during a question round.
Update the file once after the round or once at the end of the grilling session when practical.
If no project-specific terminology changed, do not modify `CONTEXT.md`.
