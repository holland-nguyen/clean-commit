---
description: Commit staged changes as a 1.0 hygiene-score Conventional Commit with no Claude trailer
---

Create a git commit for the currently staged changes, following the clean-commit rules.

1. Run `git status` and `git diff --staged` to see exactly what is staged. Do NOT run `git add` — commit only what the user has already staged. If nothing is staged, tell the user to stage first and stop.
2. Invoke the `clean-commit` skill and follow its rules.
3. Compose the message to score a perfect 1.0:
   - Subject: `Prefix(scope): Imperative subject` — capitalize the first letter of the prefix (e.g. `Feat`, `Fix`), include a scope in parentheses, keep the whole subject 10–72 characters, and start the description with a base-form verb (Add/Fix/Update — never Adding/Fixed/Creation).
   - A blank line.
   - One short line of real "why" context — never restate the diff.
4. Commit using a heredoc so the message is passed verbatim, with NO `Co-Authored-By` and NO `🤖 Generated with` trailer:

   ```bash
   git commit -F - <<'CLEAN_COMMIT_MSG'
   Feat(scope): Add the change concisely

   Why this change matters, in one line.
   CLEAN_COMMIT_MSG
   ```

5. Run `git log -1 --stat` to confirm the commit landed.
