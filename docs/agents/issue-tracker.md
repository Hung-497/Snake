# Issue tracker: GitHub

Issues and specifications live in GitHub Issues for Hung-497/Snake.
Use the gh CLI from this repository, or pass --repo Hung-497/Snake.

## Conventions

- Create: gh issue create --title "..." --body-file <file>
- Read: gh issue view <number> --comments
- Read structured details: gh issue view <number> --json title,body,labels,comments
- List: gh issue list --state open --json number,title,body,labels
- Comment: gh issue comment <number> --body-file <file>
- Add labels: gh issue edit <number> --add-label "..."
- Remove labels: gh issue edit <number> --remove-label "..."
- Close: gh issue close <number>

For multiline content, write the exact text to a temporary file
and pass it with --body-file.

"Publish to the issue tracker" means create a GitHub issue.
"Fetch the relevant ticket" means read the issue and its comments.

## Implementation dispatch contract

ready-for-agent is reserved for independently implementable child
tickets. Never apply it to parent specifications, planning issues,
or maps.

For tickets produced from a parent specification:
1. Create the child without ready-for-agent.
2. Attach it as a native GitHub sub-issue of the parent.
3. Add required native blocking relationships.
4. Apply ready-for-agent only after those relationships are complete.

If a required relationship cannot be established, leave the ticket
without ready-for-agent and report the failure. A textual
"Part of #..." reference is insufficient for automatic dispatch.

Close the parent only after all children are complete and its
aggregate acceptance criteria have been checked.

## Pull requests as a triage surface

PRs as a request surface: no.
