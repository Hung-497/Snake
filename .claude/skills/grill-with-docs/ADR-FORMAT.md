# ADR Format

ADRs record important architectural decisions and why they were made.

## When to create an ADR

Create or propose an ADR only when ALL THREE are true:

1. **Hard to reverse**
   - changing the decision later would be meaningfully expensive;

2. **Surprising without context**
   - a future engineer could reasonably wonder why this approach was chosen;

3. **Real trade-off**
   - genuine alternatives existed and one was chosen for a reason.

Do not create ADRs for:
- normal feature behavior;
- small implementation details;
- obvious choices;
- easily reversible decisions;
- ordinary library usage;
- naming;
- temporary implementation choices without long-term consequences.

## Location

Store ADRs in:

```text
docs/adr/
```

Use sequential filenames:

```text
0001-short-title.md
0002-short-title.md
0003-short-title.md
```

Create `docs/adr/` only when the first ADR is actually needed.

## Format

Keep ADRs short.

Preferred format:

```md
# <Decision title>

<1–3 sentences explaining the context, what was decided, and why.>
```

Optional sections may be added only when they genuinely help:

```md
## Considered Options

...

## Consequences

...
```

Do not add sections merely to fill a template.

## Principle

Prefer fewer, high-value ADRs over documenting every decision.
