import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from score_commit import score_commit_message, analyze  # noqa: E402


class TestRustParity(unittest.TestCase):
    """Mirrors du-quest src/scoring.rs::tests::test_score_commit_message."""

    def test_parity_assertions(self):
        self.assertGreater(score_commit_message("feat: add user authentication"), 0.5)
        self.assertGreater(score_commit_message("feat(auth): add login flow"), 0.6)
        self.assertLess(score_commit_message("wip"), 0.3)
        self.assertEqual(score_commit_message(""), 0.0)
        self.assertEqual(score_commit_message("Merge branch 'dev'"), 0.0)
        self.assertGreater(
            score_commit_message(
                "Fix login bug when session expires\n\n"
                "The session token was not being refreshed."
            ),
            0.5,
        )


class TestExactValues(unittest.TestCase):
    def test_lowercase_prefix_no_body(self):
        # 0.25 len + 0.30 prefix + 0.10 imperative
        self.assertAlmostEqual(score_commit_message("feat: add user authentication"), 0.65)

    def test_lowercase_prefix_scope_no_body(self):
        # 0.25 + 0.30 + 0.05 scope + 0.10 imperative
        self.assertAlmostEqual(score_commit_message("feat(auth): add login flow"), 0.70)

    def test_wip_clamps_to_zero(self):
        self.assertAlmostEqual(score_commit_message("wip"), 0.0)

    def test_perfect_capitalized_prefix(self):
        msg = "Feat(auth): Add login flow\n\nRefresh token before expiry."
        self.assertAlmostEqual(score_commit_message(msg), 1.0)

    def test_lowercase_prefix_caps_at_090(self):
        msg = "feat(auth): Add login flow\n\nRefresh token before expiry."
        self.assertAlmostEqual(score_commit_message(msg), 0.90)

    def test_wip_substring_trap(self):
        # "swipe" contains "wip" -> -0.30 penalty
        self.assertAlmostEqual(score_commit_message("Fix swipe gesture handler"), 0.15)

    def test_all_caps_penalty(self):
        self.assertAlmostEqual(score_commit_message("FIX THE LOGIN BUG NOW"), 0.30)


class TestBreakdown(unittest.TestCase):
    def test_breakdown_flags_missing_capital(self):
        _, breakdown = analyze("feat(auth): Add login flow\n\nbody line.")
        by_key = {b["key"]: b for b in breakdown}
        self.assertTrue(by_key["prefix"]["got"])
        self.assertTrue(by_key["scope"]["got"])
        self.assertFalse(by_key["capital"]["got"])
        self.assertTrue(by_key["body"]["got"])


if __name__ == "__main__":
    unittest.main()
