---
name: clean-commit
description: Use when writing any git commit message or running git commit — produces human, concise, standard Conventional Commits that score 0.90 on the bundled hygiene scorer and never include the Claude co-author trailer.
---

# clean-commit

Write every commit as a clean, standard Conventional Commit that scores 0.90 on
the bundled hygiene scorer (`scripts/score_commit.py`), while staying human and
concise.

## The format

Three paragraphs, **each separated by a blank line**:

```
feat(scope): Add an imperative subject in the 10-72 char band

The reason for the change — what was missing, broken, or unclear.

Add the detail that explains how this change addresses it.
```

1. **Subject** — `type(scope): Description`.
2. *(blank line)*
3. **Reason** — one sentence on *why*, tailored to the type.
4. *(blank line)*
5. **Detail** — one sentence on *what* the change does.

Capitalize the first letter of each sentence. The whole message is at least
3 lines (it's 5 with the blank separators), which earns the body bonus.

Example:

```
fix(auth): Refresh the token before each authenticated request

Sessions were expiring mid-request and logging users out.

Add an automatic refresh check so the session stays valid.
```

## Lowercase the prefix

Use a **lowercase** conventional type — `feat(`, `fix(`, `refactor(` — exactly as
the Conventional Commits standard specifies. (The scorer also has an "uppercase
first character" bonus, but we deliberately do **not** chase it by capitalizing
the type; a standard lowercase commit caps at 0.90, and that is the target.)

## Tailor the reason paragraph to the type

The reason paragraph states *why*, phrased to fit the change:

- **feat** — what was missing or what the feature now enables.
- **fix** — what was broken (the symptom or root cause).
- **refactor** — why the restructure (what was hard to read/extend before).
- **docs / chore / test / perf** — the gap the change closes.

## Rules (each maps to points)

- **Conventional prefix (+0.30).** Use one of `feat fix chore docs style refactor
  test perf ci build revert`, lowercase, followed by `(scope):`.
- **Scope in parentheses (+0.05).** Always include `(scope)`, e.g. `fix(db):`.
- **Imperative verb (+0.10).** First word of the description must be a base-form
  verb: Add, Fix, Update, Remove, Refactor. Never `Adding`, `Fixed`, `Creation`
  (no `-ing`, `-ed`, `-tion` endings).
- **Subject length 10-72 chars (+0.25).** Not shorter than 10, not longer than 72.
- **Body, at least 3 lines total (+0.20).** A reason paragraph and a detail
  paragraph, each on its own line and separated from the subject and from each
  other by a blank line. Keep each to one short sentence — do NOT restate the diff
  or list every change.

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
