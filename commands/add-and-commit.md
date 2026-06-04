---
description: Stage everything (git add .) then commit as a clean Conventional Commit (0.90 hygiene score) with no Claude trailer
---

Stage all changes in the current directory and create a clean-commit for them.

1. Run `git add .` to stage every change in the current directory tree. `.gitignore` is respected, so ignored files (e.g. `*.local.json`) stay out.
2. Run `git status` and `git diff --staged` to show the user exactly what is now staged. If nothing is staged (nothing to commit), tell the user and stop — do NOT create an empty commit.
3. Invoke the `clean-commit` skill and follow its rules.
4. Compose the message as three paragraphs, **each separated by a blank line**:
   - Subject: `type(scope): Description` — use a **lowercase** conventional type (`feat`, `fix`, `refactor`, …), include a scope in parentheses, keep the whole subject 10–72 characters, and start the description with a base-form verb (Add/Fix/Update — never Adding/Fixed/Creation).
   - A blank line, then a *reason* sentence tailored to the type (feat → what it enables; fix → what was broken; refactor → why restructure).
   - A blank line, then a short *detail* sentence on what the change does. Capitalize the first letter of each sentence; never restate the diff.
5. Commit using a heredoc so the message is passed verbatim, with NO `Co-Authored-By` and NO `🤖 Generated with` trailer:

   ```bash
   git commit -F - <<'CLEAN_COMMIT_MSG'
   fix(auth): Refresh the token before each authenticated request

   Sessions were expiring mid-request and logging users out.

   Add an automatic refresh check so the session stays valid.
   CLEAN_COMMIT_MSG
   ```

6. Run `git log -1 --stat` to confirm the commit landed.
