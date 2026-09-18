---
name: implement
description: Execute a well-specified ticket with focused TDD and minimal orchestration.
---

# Implement Lite

Implement the requested ticket or specification.

## 1. Validate the handoff

Read the ticket/spec and only the directly relevant code.

Briefly verify that:

- the ticket is internally consistent;
- referenced code still exists;
- the requested approach still fits the current repository.

If the ticket is materially ambiguous, stale, contradictory, or blocked:

STOP and ask for clarification.

Do not otherwise reopen planning or redesign the feature.

## 2. Implement

- Prefer the smallest correct change.
- Reuse existing code before adding abstractions or dependencies.
- Do not modify unrelated code.
- Do not perform unrelated refactoring.

Where the requested behavior benefits from regression coverage, invoke the `tdd` skill at the relevant test seam.

Follow the TDD workflow:

- RED: add the smallest failing test for the requested behavior.
- GREEN: implement the smallest change that makes it pass.
- REFACTOR: clean up only when useful.

If TDD is not appropriate for the task, implement directly.

## 3. Verify

During implementation:

- run only tests relevant to the current feature;
- run focused typechecking or linting when relevant.

Do NOT run the entire repository test suite unless the user explicitly requests it.

Do not repeatedly run unrelated tests.

## 4. Boundaries

Do NOT:

- invoke `code-review` automatically;
- launch review subagents;
- perform a broad architecture review;
- commit or push unless explicitly requested.

When a dispatcher assigns an isolated worktree, stay in that worktree and do not switch branches or move the task to another checkout. Leave the validated changes and a concise PR-ready completion summary there. The dispatcher owns committing, pushing, and opening the pull request; it must still never merge.

## 5. Completion

Report briefly:

- files changed;
- relevant tests run and their results;
- typecheck/lint result, if run;
- unresolved issues, if any.
