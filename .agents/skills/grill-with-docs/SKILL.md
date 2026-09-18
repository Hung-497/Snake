---
name: grill-with-docs
description: A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go.
---

Clarify a feature or design until it is ready to become a specification.

Optimize for:

- important product and architecture decisions;
- minimal repository exploration;
- low token usage;
- preserving decisions already made;
- concise durable documentation.

Do NOT invoke other skills automatically.

Do NOT launch subagents unless the user explicitly requests them.

## 1. Start from existing knowledge

Read the user's request.

If a handoff, existing spec, issue, ADR, or other planning artifact is supplied,
read it first.

Treat decisions explicitly recorded there as settled.

Do NOT ask the user to decide the same thing again unless:

- the existing decision contradicts the current repository;
- the user changed the requirement;
- the decision is genuinely ambiguous.

If `CONTEXT.md` exists, use it for established project vocabulary.

If `CONTEXT.md` is large, search for terms relevant to the current feature
instead of repeatedly reading the whole file.

## 2. Inspect the repository narrowly

Inspect only enough repository state to understand the feature and identify
the next important decisions.

Prefer:

1. targeted search;
2. directly relevant files;
3. directly relevant tests;
4. directly relevant configuration.

Do NOT begin with a broad repository survey.

Do NOT:

- launch exploration subagents;
- recursively read large directories;
- inspect unrelated modules;
- inspect git history unless directly relevant;
- run the whole test suite;
- perform broad architecture analysis;
- investigate hypothetical future needs.

If a repository fact is needed for the current decision:

1. investigate it yourself;
2. use a small targeted search/read;
3. return to the decision immediately.

If answering a question would require substantial repository exploration,
ask the user before expanding scope.

## 3. Build the decision frontier

Identify unresolved decisions that materially affect the specification.

Prioritize:

- user-visible behavior;
- feature scope;
- boundaries and ownership;
- persistence or data model choices;
- API contracts;
- important edge cases;
- error and failure behavior;
- compatibility;
- security-sensitive behavior;
- architectural choices expensive to reverse.

Do NOT grill the user about:

- facts quickly verifiable from code;
- trivial implementation details;
- formatting;
- minor naming;
- choices safely left to implementation;
- speculative future requirements;
- unnecessary abstractions.

The goal is not to enumerate every possible decision.

The goal is to remove enough ambiguity that `to-spec` can produce an
implementation-ready specification.

## 4. Grill in focused rounds

Ask no more than 4 questions per round.

Only ask questions whose prerequisites are already settled.

Use this format:

❓ **Q1 — <short title>**

<Concise explanation. Include options when useful.>

➡️ **Recommendation:** <recommended answer and short reason>

Ask the current decision frontier, up to 4 questions.

Then STOP and wait for the user's answers.

After the answers:

1. mark those decisions settled;
2. determine which important decisions are now unblocked;
3. investigate only facts required for those decisions;
4. ask the next focused round.

Do not attempt to exhaust every theoretically possible branch.

## 5. Maintain project vocabulary

`CONTEXT.md` is a compact project glossary.

Follow `CONTEXT-FORMAT.md`.

Only update `CONTEXT.md` when project-specific terminology is resolved or
meaningfully changed.

Do not rewrite it after every individual answer.

Collect glossary changes during the round and update it once after the round
or at the end of the grilling session.

Do not modify `CONTEXT.md` if no relevant terminology changed.

## 6. Record architectural decisions

Use ADRs only for significant architectural decisions.

Follow `ADR-FORMAT.md`.

Do not create an ADR for ordinary feature behavior or implementation details.

If no decision satisfies the ADR criteria, create no ADR.

## 7. Know when to stop

Finish grilling when all decisions that materially affect the specification
are settled.

Do not keep inventing questions merely because more questions are possible.

A feature is ready when a fresh agent could write a clear specification
without guessing about important behavior.

At that point, say:

**Ready for `to-spec`.**

This means the decisions are ready to become a parent planning issue. It does not mean the feature or parent issue is `ready-for-agent`; only the child tickets later created by `to-tickets` are implementation units.

Do NOT implement the feature.

## 8. Token and exploration budget

Default behavior:

- main agent only;
- no subagents;
- no parallel exploration;
- no broad scans;
- no full test suite;
- no code review;
- no implementation;
- no speculative research.

Before expensive investigation, ask the user first.

Use already-discovered repository facts instead of rediscovering them.

## 9. Completion report

When grilling is complete, report briefly:

### Settled
- important decisions made

### Unresolved
- genuinely unresolved decisions, if any

### Documentation
- `CONTEXT.md` terms added or changed, if any
- ADRs created, if any

### Status
- Ready for `to-spec`: Yes / No

Do not provide an implementation plan unless requested.
