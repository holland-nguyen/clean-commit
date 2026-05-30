---
description: Stage everything (git add .) then commit as a 1.0 hygiene-score Conventional Commit with no Claude trailer
---

Stage all changes in the current directory and create a clean-commit for them.

1. Run `git add .` to stage every change in the current directory tree. `.gitignore` is respected, so ignored files (e.g. `*.local.json`) stay out.
2. Run `git status` and `git diff --staged` to show the user exactly what is now staged. If nothing is staged (nothing to commit), tell the user and stop — do NOT create an empty commit.
3. Invoke the `clean-commit` skill and follow its rules.
4. Compose the message to score a perfect 1.0:
   - Subject: `Prefix(scope): Imperative subject` — capitalize the first letter of the prefix (e.g. `Feat`, `Fix`), include a scope in parentheses, keep the whole subject 10–72 characters, and start the description with a base-form verb (Add/Fix/Update — never Adding/Fixed/Creation).
   - A blank line.
   - One short line of real "why" context — never restate the diff.
5. Commit using a heredoc so the message is passed verbatim, with NO `Co-Authored-By` and NO `🤖 Generated with` trailer:

   ```bash
   git commit -F - <<'CLEAN_COMMIT_MSG'
   Feat(scope): Add the change concisely

   Why this change matters, in one line.
   CLEAN_COMMIT_MSG
   ```

6. Run `git log -1 --stat` to confirm the commit landed.
