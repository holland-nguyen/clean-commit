---
description: Commit staged changes as a clean Conventional Commit (0.90 hygiene score) with no Claude trailer
---

Create a git commit for the currently staged changes, following the clean-commit rules.

1. Run `git status` and `git diff --staged` to see exactly what is staged. Do NOT run `git add` — commit only what the user has already staged. If nothing is staged, tell the user to stage first and stop.
2. Invoke the `clean-commit` skill and follow its rules.
3. Compose the message as three paragraphs, **each separated by a blank line**:
   - Subject: `type(scope): Description` — use a **lowercase** conventional type (`feat`, `fix`, `refactor`, …), include a scope in parentheses, keep the whole subject 10–72 characters, and start the description with a base-form verb (Add/Fix/Update — never Adding/Fixed/Creation).
   - A blank line, then a *reason* sentence tailored to the type (feat → what it enables; fix → what was broken; refactor → why restructure).
   - A blank line, then a short *detail* sentence on what the change does. Capitalize the first letter of each sentence; never restate the diff.
4. Commit using a heredoc so the message is passed verbatim, with NO `Co-Authored-By` and NO `🤖 Generated with` trailer:

   ```bash
   git commit -F - <<'CLEAN_COMMIT_MSG'
   fix(auth): Refresh the token before each authenticated request

   Sessions were expiring mid-request and logging users out.

   Add an automatic refresh check so the session stays valid.
   CLEAN_COMMIT_MSG
   ```

5. Run `git log -1 --stat` to confirm the commit landed.
