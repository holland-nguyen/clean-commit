# clean-commit

A personal [Claude Code](https://claude.com/claude-code) plugin that makes every
commit **human, concise, and high-scoring** — and quietly strips the
`Co-Authored-By: Claude …` / `🤖 Generated with [Claude Code]` trailers.

It exists to solve two everyday annoyances:

1. Claude writes commit messages that are **too long and machine-like**.
2. Claude appends a **`Co-Authored-By: Claude` trailer** you don't want.

On top of that, it guarantees every commit scores a perfect **1.0** on a
bundled commit-hygiene scorer.

---

## Install

### Option A — from GitHub via the plugin marketplace (recommended)

Inside Claude Code, add this repo as a marketplace and install the plugin:

```text
/plugin marketplace add holland-nguyen/clean-commit
/plugin install clean-commit@clean-commit
```

(`clean-commit@clean-commit` is `<plugin>@<marketplace>` — both happen to be named
`clean-commit`.) Restart Claude Code if prompted, then confirm `/clean-commit:commit` appears in
the slash-command list.

### Option B — clone and load locally

```bash
git clone https://github.com/holland-nguyen/clean-commit.git
cd clean-commit
claude --plugin-dir .
```

### Option C — persistent local install

Clone the repo, then add to `~/.claude/settings.json` (use the **absolute** path to
your clone). Register the clone as a local marketplace with `extraKnownMarketplaces`,
then enable the plugin by its `plugin@marketplace` id:

```json
{
  "enabledPlugins": { "clean-commit@clean-commit": true },
  "extraKnownMarketplaces": {
    "clean-commit": {
      "source": { "source": "directory", "path": "/Users/you/clean-commit" }
    }
  }
}
```

The `directory` path must point at the repo root (the folder containing
`.claude-plugin/marketplace.json`). Restart Claude Code so it picks up the plugin,
then confirm `/clean-commit:commit` shows up in the slash-command list.

> **There is no `plugins` settings field.** Claude Code installs plugins via a
> marketplace (`extraKnownMarketplaces` or `/plugin marketplace add`) and enables
> them through `enabledPlugins` keyed by `plugin@marketplace`. A bare
> `"plugins": { ... }` block is silently ignored / rejected — that's the most
> common reason install "does nothing".
>
> You can put this config in `~/.claude/settings.json` (every project) or in a
> repo's `.claude/settings.json` / `.claude/settings.local.json` (just that repo —
> `extraKnownMarketplaces` is designed for repo settings). Use `settings.local.json`
> for a personal, git-ignored config when the `directory` path is machine-specific.

---

## Requirements

- `python3` on your `PATH` (standard on macOS via the Command Line Tools).
- Claude Code.

---

## How it works

Three cooperating pieces, backed by one shared scorer:

| Piece | What it does |
| --- | --- |
| **Hook** (`hooks/hooks.json` → `scripts/clean-commit-hook.py`) | Runs on **every** `git commit`. Strips the Claude trailer, scores the message, and **blocks** anything below `CLEAN_COMMIT_MIN_SCORE` (default `1.0`) with a per-rule fix list. Deterministic — works even when you never type a command. |
| **`/clean-commit:commit` command** (`commands/commit.md`) | Writes a 1.0 commit for your **already-staged** changes. Never runs `git add`. |
| **`/clean-commit:add-and-commit` command** (`commands/add-and-commit.md`) | Runs `git add .`, shows you the staged diff, then writes a 1.0 commit — for committing everything in one step. |
| **`clean-commit` skill** (`skills/clean-commit/SKILL.md`) | The rule set. Auto-activates whenever Claude is about to commit, so good messages get written in the first place. |
| **Scorer** (`scripts/score_commit.py`) | A self-contained commit-message hygiene scorer. Single source of truth; also runnable on its own. |

The hook **never touches `git add`** — staging stays entirely under your control.

---

## Troubleshooting

### `/clean-commit:commit` doesn't appear after install

1. **Wrong settings file or wrong field.** The `enabledPlugins` /
   `extraKnownMarketplaces` config must live in `~/.claude/settings.json` (user
   settings) — **not** a project's `.claude/settings.json` — and there is **no
   `plugins` field** (see Option C). Confirm it registered: clean-commit should
   appear in `~/.claude/plugins/known_marketplaces.json` and resolve via
   `enabledPlugins` as `clean-commit@clean-commit`.
2. **Didn't restart.** Plugin slash commands don't hot-load — fully restart
   Claude Code after installing.
3. **Looking for the wrong name.** Plugin commands are namespaced as
   `/<plugin>:<command>` — type `/clean-commit:commit`, not `/commit`. The bare
   `/clean-commit` you may see is the *skill*, not the commit command.
4. **Wrong path (Option C).** The `directory` `path` must be the **absolute** path
   to your clone, e.g. `/Users/you/clean-commit`.

### The hook doesn't strip the trailer or block bad commits

- Check `python3` is on your `PATH` (`python3 --version`).
- The hook **fails open**: on any error it stays silent so it can't wedge a
  commit. Run it directly to see real output:
  ```bash
  echo '{"tool_input":{"command":"git commit -m \"wip\""}}' \
    | python3 scripts/clean-commit-hook.py
  ```

---

## Usage

> **Command names are namespaced by the plugin.** Claude Code exposes a plugin's
> commands as `/<plugin>:<command>`, so the commands below are `/clean-commit:commit`
> and `/clean-commit:add-and-commit` — there is no bare `/commit`.

### Active: `/clean-commit:commit`

You control staging. Stage what you want, then run the command:

```text
git add -p                   # stage your changes however you like
/clean-commit:commit         # Claude writes a 1.0 message and commits the staged diff
```

Claude reviews `git diff --staged`, writes a capitalized `Prefix(scope):`
message with a one-line body, and commits — no trailer. It never runs `git add`.

### Active: `/clean-commit:add-and-commit`

Convenience shortcut when you want to commit *everything* in one step:

```text
/clean-commit:add-and-commit  # runs `git add .`, shows you what got staged, then commits at 1.0
```

It runs `git add .` for you (respecting `.gitignore`), shows the staged diff so
you can see exactly what's included, then writes the same 1.0 message — no trailer.
Prefer `/clean-commit:commit` when you want tight control over what goes in.

### Passive: just commit

You don't have to use either command. Whenever Claude runs `git commit` on its own,
the hook still:

- removes any `Co-Authored-By: Claude …` / `🤖 Generated with` line, and
- blocks the commit if the message scores below the threshold, handing Claude an
  exact fix list so it rewrites and retries.

So the *outcome* is always a clean, high-scoring commit.

---

## Configuration

| Env var | Default | Effect |
| --- | --- | --- |
| `CLEAN_COMMIT_MIN_SCORE` | `1.0` | Minimum hygiene score required to allow a commit. Lower it (e.g. `0.8`) to be less strict. |

Set it in your shell profile, e.g.:

```bash
export CLEAN_COMMIT_MIN_SCORE=0.9
```

---

## Score a message by hand

The scorer runs standalone — handy for checking a message before you commit:

```bash
python3 scripts/score_commit.py "Feat(auth): Add token refresh on expiry

Why it matters."
```

```text
score: 1.00
  [ok ] subject length 10-72
  [ok ] conventional prefix
  [ok ] scope (...)
  [ok ] subject starts uppercase
  [ok ] imperative verb
  [ok ] body (>=3 lines)
```

You can also pipe a message in on stdin:

```bash
git log -1 --pretty=%B | python3 scripts/score_commit.py
```

---

## What a blocked commit looks like

If Claude tries `git commit -m "fix bug"`, the hook denies it and explains exactly
what to fix and what each fix is worth:

```text
clean-commit: message scores 0.20 (need 1.00).
  - subject length 10-72: subject is 7 chars; aim for 10-72
  - conventional prefix: start with feat/fix/... + ':' or '('
  - scope (...): add a scope, e.g. Feat(auth): ...
  - subject starts uppercase: capitalize the first char; write 'Feat(' not 'feat('
  - body (>=3 lines): add a blank line + 1 short body line
Rewrite the commit message and try again.
```

---

## Development

Run the test suite (stdlib `unittest`, no dependencies):

```bash
python3 -m unittest discover -s tests -v
```

Layout:

```
clean-commit/
├── .claude-plugin/
│   ├── plugin.json                # plugin manifest
│   └── marketplace.json           # lets `/plugin marketplace add` install it
├── commands/
│   ├── commit.md                  # /clean-commit:commit (commit staged changes)
│   └── add-and-commit.md          # /clean-commit:add-and-commit (git add . + commit)
├── skills/clean-commit/SKILL.md   # commit-style rules (auto-activates)
├── hooks/hooks.json               # registers the PreToolUse/Bash hook
├── scripts/
│   ├── score_commit.py            # the scorer (single source of truth)
│   └── clean-commit-hook.py       # the hook: strip trailer, score, allow/deny
└── tests/                         # golden scorer tests + hook I/O tests
```

The hook **fails open**: any malformed input or unexpected error produces no
output, so it can never wedge a commit.

---

## License

Personal tool — use it however you like.
