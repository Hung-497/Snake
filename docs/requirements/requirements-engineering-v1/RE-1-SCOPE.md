# RE-1 — Scope

[Package index](index.md) · [Review state](review-state.md)

## Purpose

Specify what Snake AI must do and how well, so that existing behaviour can be
checked against acceptance criteria and new features can be traced to the
requirements they add or change. Source: [product definition](../product-definition.md)
§1–4.

## Agreed scope

The whole current product, as described in the product definition §6:

- The game rules (Game Engine).
- Human Play and Bot play in the app.
- Settings, Records, and Replays.
- Training of the learning Bot Modes, in the app and in the terminal.
- Evaluate in the app, Bot Experiments in the terminal, and Bot Reports.

There is one release boundary: the product as built at commit `07c9afe`.
Requirements that describe behaviour the product does not have yet are marked
**Proposed** in their source and basis.

## Exclusions

From the product definition §11:

- Online play, multiplayer, accounts, or leaderboards.
- GPU training.
- An installer or published package.
- Mobile or web versions.

## Deferrals

| Deferred capability | Decision | Would change |
| --- | --- | --- |
| Let Continue raise the game limit of a finished training, instead of starting over. Workaround today: choose limit Off, then Evaluate and Continue as often as wanted. | DEC-014 (Q-10) | REQ-025 |

Owner decisions are listed in
[RE-9](RE-9-GAPS-CONFLICTS-PRIORITIES-OPEN-QUESTIONS.md).
