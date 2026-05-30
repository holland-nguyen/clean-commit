import importlib.util
import os
import sys
import unittest

HERE = os.path.dirname(__file__)
HOOK_PATH = os.path.join(HERE, "..", "scripts", "clean-commit-hook.py")

spec = importlib.util.spec_from_file_location("clean_commit_hook", HOOK_PATH)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


class TestStripTrailer(unittest.TestCase):
    def test_strips_claude_coauthor_line_in_heredoc(self):
        cmd = (
            "git commit -F - <<'EOF'\n"
            "Feat(auth): Add token refresh\n\n"
            "Why it matters.\n\n"
            "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>\n"
            "EOF"
        )
        out = hook.strip_trailer(cmd)
        self.assertNotIn("Co-Authored-By", out)
        self.assertIn("Feat(auth): Add token refresh", out)

    def test_strips_generated_with_line(self):
        cmd = "git commit -m 'x'\n\n🤖 Generated with [Claude Code]\n"
        self.assertNotIn("Generated with", hook.strip_trailer(cmd))

    def test_keeps_human_coauthor(self):
        cmd = (
            "git commit -F - <<'EOF'\n"
            "Feat(x): Add y\n\nbody\n\n"
            "Co-Authored-By: Jane Doe <jane@example.com>\n"
            "EOF"
        )
        self.assertIn("Jane Doe", hook.strip_trailer(cmd))

    def test_keeps_human_named_claude(self):
        # A human co-author named Claude (non-Anthropic email) must survive.
        cmd = (
            "git commit -F - <<'EOF'\n"
            "Feat(x): Add y\n\nbody\n\n"
            "Co-Authored-By: Claude Doe <claude.doe@example.com>\n"
            "EOF"
        )
        self.assertIn("Claude Doe", hook.strip_trailer(cmd))

    def test_strips_trailer_m_arg(self):
        cmd = (
            'git commit -m "Feat(x): Add y" '
            '-m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"'
        )
        out = hook.strip_trailer(cmd)
        self.assertNotIn("Co-Authored-By", out)
        self.assertIn("Feat(x): Add y", out)


class TestExtractMessage(unittest.TestCase):
    def test_extract_heredoc(self):
        cmd = (
            "git commit -F - <<'EOF'\n"
            "Feat(auth): Add token refresh\n\n"
            "Why it matters.\n"
            "EOF"
        )
        self.assertEqual(
            hook.extract_message(cmd),
            "Feat(auth): Add token refresh\n\nWhy it matters.",
        )

    def test_extract_single_m(self):
        self.assertEqual(
            hook.extract_message('git commit -m "Feat(x): Add y"'),
            "Feat(x): Add y",
        )

    def test_extract_multiple_m(self):
        cmd = 'git commit -m "Feat(x): Add y" -m "Why it matters."'
        self.assertEqual(hook.extract_message(cmd), "Feat(x): Add y\n\nWhy it matters.")

    def test_extract_none_when_no_message(self):
        self.assertIsNone(hook.extract_message("git commit --amend --no-edit"))


import json as _json
import subprocess


def run_hook(command, env=None):
    payload = _json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    e = dict(os.environ)
    if env:
        e.update(env)
    p = subprocess.run(
        [sys.executable, HOOK_PATH], input=payload,
        capture_output=True, text=True, env=e,
    )
    out = p.stdout.strip()
    return _json.loads(out) if out else None


class TestHookIO(unittest.TestCase):
    PERFECT = (
        "git commit -F - <<'EOF'\n"
        "Feat(auth): Add token refresh on session expiry\n\n"
        "Why it matters in one line.\n"
        "EOF"
    )

    def test_passthrough_non_commit(self):
        self.assertIsNone(run_hook("ls -la"))

    def test_perfect_commit_no_trailer_passes_silently(self):
        self.assertIsNone(run_hook(self.PERFECT))

    def test_strips_trailer_and_allows(self):
        cmd = (
            "git commit -F - <<'EOF'\n"
            "Feat(auth): Add token refresh on session expiry\n\n"
            "Why it matters in one line.\n\n"
            "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>\n"
            "EOF"
        )
        out = run_hook(cmd)
        self.assertIsNotNone(out)
        hso = out["hookSpecificOutput"]
        self.assertEqual(hso["permissionDecision"], "allow")
        self.assertNotIn("Co-Authored-By", hso["updatedInput"]["command"])

    def test_keeps_human_coauthor_when_passing(self):
        # Human co-author present but message scores 1.0 -> nothing to strip/deny.
        cmd = (
            "git commit -F - <<'EOF'\n"
            "Feat(auth): Add token refresh on session expiry\n\n"
            "Why it matters in one line.\n\n"
            "Co-Authored-By: Jane Doe <jane@example.com>\n"
            "EOF"
        )
        self.assertIsNone(run_hook(cmd))

    def test_denies_low_score(self):
        out = run_hook('git commit -m "fix bug"')
        self.assertIsNotNone(out)
        hso = out["hookSpecificOutput"]
        self.assertEqual(hso["permissionDecision"], "deny")
        self.assertIn("0.20", hso["permissionDecisionReason"])

    def test_fail_open_on_bad_json(self):
        p = subprocess.run(
            [sys.executable, HOOK_PATH], input="not json",
            capture_output=True, text=True,
        )
        self.assertEqual(p.stdout.strip(), "")

    def test_threshold_env_allows_below_default(self):
        out = run_hook(
            'git commit -m "feat: add user authentication"',
            env={"CLEAN_COMMIT_MIN_SCORE": "0.5"},
        )
        self.assertIsNone(out)  # 0.65 >= 0.5 and no trailer -> silent

    def test_default_threshold_denies_same_message(self):
        out = run_hook('git commit -m "feat: add user authentication"')
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")


if __name__ == "__main__":
    unittest.main()
