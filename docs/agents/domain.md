# Domain Docs

This repository uses a single-context layout.

## Before exploring

- Read CONTEXT.md at the repository root if present.
- Read decisions in docs/adr/ that concern the area being changed.

If these files do not exist, proceed silently. Do not suggest
creating them upfront. `grill-with-docs` creates or updates domain documentation lazily as project terminology and significant architectural decisions are resolved.

## Layout

- CONTEXT.md: shared domain vocabulary and context.
- docs/adr/: numbered architecture decision records.

This convention does not require moving existing Python files.

## Use the glossary's vocabulary

Use terms defined in CONTEXT.md in issue titles, proposals,
and tests. Avoid synonyms that the glossary explicitly excludes.

If a concept is missing, reconsider the terminology or note the gap for the next `grill-with-docs` session.

## Flag decision conflicts

If a proposal contradicts an existing architecture decision
record, identify the record and explain why it should be revisited
instead of silently overriding it.
