---
name: clean-commit
description: Use when writing any git commit message or running git commit — produces human, concise Conventional Commits that score a perfect 1.0 on the bundled hygiene scorer and never include the Claude co-author trailer.
---

# clean-commit

Write every commit to score the maximum 1.0 on the bundled hygiene scorer
(`scripts/score_commit.py`), while staying human and concise.

## The format that scores 1.0

```
Prefix(scope): Imperative subject in the 10-72 char band

One short line of real "why" context.
```

Example: `Feat(auth): Add token refresh on session expiry` + a blank line + one body line.

## Rules (each maps to points)

- **Capitalized conventional prefix (+0.30 and +0.10).** Use one of `feat fix
  chore docs style refactor test perf ci build revert`, followed by `(scope):`.
  **Capitalize the first letter** — `Feat(`, `Fix(` — not `feat(`. The scorer
  detects the prefix case-insensitively but separately awards +0.10 for an
  uppercase first character, so `Feat(` earns both; `feat(` loses the +0.10 and
  caps at 0.90.
- **Scope in parentheses (+0.05).** Always include `(scope)`, e.g. `Fix(db):`.
- **Imperative verb (+0.10).** First word of the description must be a base-form
  verb: Add, Fix, Update, Remove, Refactor. Never `Adding`, `Fixed`, `Creation`
  (no `-ing`, `-ed`, `-tion` endings).
- **Subject length 10-72 chars (+0.25).** Not shorter than 10, not longer than 72.
- **Short body (+0.20).** Add a blank line and at least one body line so the full
  message is at least 3 lines. Keep it to 1-2 lines of "why" — do NOT restate the
  diff or list every change.

## Penalties to avoid

- **Never write `wip`, `fixup!`, or `squash!`** (−0.30). The scorer matches `wip`
  as a substring, so it also fires inside ordinary words — `swipe`, `wipe`,
  `wiper`. Rephrase to avoid the letters `wip` in sequence.
- **Never write the subject in ALL CAPS** (−0.15 when the subject is longer than
  5 chars). Use sentence case.
- **Avoid merge commits** — any subject starting with `merge branch/remote/pull`
  scores 0. Prefer rebase.

## Never add the Claude trailer

Do not append `Co-Authored-By: Claude ...` or `🤖 Generated with [Claude Code]`.
The hook strips them anyway, but write clean from the start.

## Pick the most accurate prefix

Choose the prefix that truly describes the change (`feat` for a feature, `fix` for
a bugfix, `docs` for documentation, and so on). Don't mislabel — an accurate type
makes the history readable.
