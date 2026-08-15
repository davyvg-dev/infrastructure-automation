# VS Code keyboard workflow

Open this file anytime: `Cmd+P` → type `vscode`.

## Core shortcuts

| Keys          | What                                                                        |
| ------------- | --------------------------------------------------------------------------- |
| `Cmd+P`       | Quick Open — fuzzy file jump, no Explorer needed                            |
| `Cmd+Shift+P` | Command Palette — every VS Code action by name (`>` in Cmd+P does the same) |
| `` Ctrl+` ``  | Focus terminal (Claude Code)                                                |
| `Cmd+1`       | Focus back to editor                                                        |
| `Cmd+B`       | Toggle sidebar — keep it collapsed, Cmd+P replaces it                       |
| `Cmd+K V`     | Markdown preview to the side                                                |

Inside `Cmd+P`: `@` jumps to a heading/symbol in the file, `:42` jumps to line 42.

## Cmd+P targets in this repo

| Type                     | Opens                                    | When                    |
| ------------------------ | ---------------------------------------- | ----------------------- |
| `todo`                   | `TODO.md`                                | daily — where are we    |
| `master`                 | `docs/00-MASTER-PLAN.md`                 | weekly — still on plan? |
| `offerte`                | live deals (DRS, Cool Global) + template | any deal follow-up      |
| `playbook` / `objection` | cold-call playbook, objection handling   | before every sales call |
| `sequences`              | cold-email sequences                     | before a send wave      |

`ai-receptionist` is part of the workspace too — Cmd+P reaches both apps
(`evals`, `pipeline`, `rdw`, …). Open the whole thing via
`klantkraan.code-workspace` in the repo root.

## Command Palette (`Cmd+Shift+P`) — the pro five

- **Git: Open All Changes** — diff every modified file; the way to review what Claude Code just did.
- **Markdown: Open Preview to the Side** — read offertes rendered, the way a prospect will.
- **File: Copy Relative Path of Active File** — paste into Claude Code prompts for precise instructions.
- **File: Reveal Active File in Explorer View** — manual reveal (auto-reveal is off on purpose).
- **Developer: Reload Window** — first fix for any weird UI/extension state.

80% of the review-and-sell loop: `Cmd+P` → `offerte`, and `>Git: Open All Changes`.
