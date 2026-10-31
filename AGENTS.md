# tasklite

A tiny Python to-do CLI (add / list / done), managed with uv.

## Autonomous development contract

This repo is developed by both humans and coding agents. Any agent or harness
working here reads this section first and obeys it. It states repo facts, not
process doctrine — your harness supplies the process.

Machine-readable companion: `.agents/gate.json` (same commands, parseable).

### Shared agent memory

- **Read** root `MEMORY.md` (and optional `memory/`) at session start
  before mutating work.
- **Dual-write:** durable lessons go in the repo memory file, not only in a local
  runtime store.
- **No CI loop for pure memory commits:** if a commit touches **only** shared
  memory markdown (`MEMORY.md`, optional `memory/**`), do **not** run typecheck/lint/test/build and do **not**
  wait on product CI or review gates. Land the lesson on the default branch
  quickly. Mixed memory + product code uses the normal green gate.
- **Append-only** by default; rebase/pull immediately before writing; on conflict
  in dated sections keep both sides. No secrets in memory files.

### Gate commands (the definition of "green" here)
```bash
uv run mypy --strict src
uv run ruff check .
uv run pytest -q
uv build
```
All of these must pass before any **product** commit, with **zero new failures versus the
branch point**. Pre-existing failures are recorded, not inherited and not hidden.
Pure memory-only commits are exempt (see Shared agent memory above).

### Ground rules for machine contributors
1. **Never mutate the shared checkout.** One task = one branch = one git
   worktree of your own.
2. **Claim before you touch.** Put one line of the form
   `- Active-work claim: issue-N-short-name` in an open PR body
   (for example `- Active-work claim: issue-2-due-dates`) and add the
   `agent-claimed` label. Overlapping claim ⇒ stop and coordinate, never race.
3. **Never review or approve your own work.** An independent reviewer — ideally
   a different model — inspects the exact committed head, read-only.
4. **Acceptance criteria are the contract**, verified by a sensor (test, script,
   check), never by assertion.
5. **Report failures verbatim.** Never mark done what you did not verify.
6. **Clean up:** remove the worktree, delete the branch, release the claim.

### Hot files (single claimant, own PR)
| File | Rule |
|---|---|
| pyproject.toml | no casual deps; own commit |
| uv.lock | never hand-edit — run `uv lock` (or `uv add` / `uv remove`); commit it together with pyproject.toml |
| MEMORY.md | append-only lessons; pure updates skip CI |

### Framework warnings
- Use uv for everything: `uv run …`, `uv add …`. Never `pip install` into the project.
- Code must pass `mypy --strict`: every function fully typed, no bare `list`/`dict`.

### Deployment truth (verified 2026-10-31)
- No hosting. tasklite is a local CLI; merging to `main` deploys nothing.
- No preview deployments.

### Stop and ask a human for
- Money: none in this repo.
- Auth and authorization boundaries: none in this repo.
- PII / consent: the user's task file (`~/.tasklite.json`, or `TASKLITE_DB`).
  Tests must always point `TASKLITE_DB` at a temp path, never the real file.
- Security boundaries: `.agents/gate.json` and `.github/workflows/` — changing
  them can weaken the checks themselves.
- Destructive or irreversible data and schema operations: any change to the
  stored task format (the `Task` fields in `src/tasklite.py`) other than adding
  an optional field; anything that deletes or rewrites existing task files.
- Secret values, public launches, legal commitments.

### Commit and PR conventions
- Every commit signed off: `git commit -s`.
- Branch name: `feat/<issue-number>-<short-name>` for every task, including
  fixes and refactors (claim tooling depends on this exact form).
- Commit messages and PR titles start with the change type:
  `feat(#N):`, `fix(#N):`, `refactor(#N):`, `docs(#N):`, `test(#N):`, `chore(#N):`.
- Every PR has `Closes #N` and one tier label (`tier-a`, `tier-b`, `tier-c`).
- Agents never merge their own PR; `tier-c` PRs need human approval to merge.