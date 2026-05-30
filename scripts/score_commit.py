#!/usr/bin/env python3
"""Commit-message hygiene scorer.

Single source of truth for clean-commit scoring. Importable, and runnable:
    score_commit.py "<message>"      (or pipe the message on stdin)
"""
import sys

CONVENTIONAL = (
    "feat", "fix", "chore", "docs", "style", "refactor",
    "test", "perf", "ci", "build", "revert",
)


def _first_line(message):
    lines = message.splitlines()
    return lines[0] if lines else ""


def _byte_len(s):
    return len(s.encode("utf-8"))


def _has_prefix(lower):
    return any(lower.startswith(p + ":") or lower.startswith(p + "(")
               for p in CONVENTIONAL)


def _first_word(lower, has_prefix):
    if has_prefix:
        parts = lower.split(":")
        if len(parts) < 2:
            return ""
        toks = parts[1].split()
        return toks[0] if toks else ""
    toks = lower.split()
    return toks[0] if toks else ""


def analyze(message):
    """Return (score, breakdown). breakdown is a list of dicts:
    {key, label, points, got (bool), fix}."""
    first_line = _first_line(message)
    trimmed = first_line.strip()

    if trimmed == "":
        return 0.0, [{"key": "empty", "label": "non-empty subject",
                      "points": 0.0, "got": False,
                      "fix": "write a subject line"}]

    lower = trimmed.lower()

    if (lower.startswith("merge branch") or lower.startswith("merge remote")
            or lower.startswith("merge pull")):
        return 0.0, [{"key": "merge", "label": "not a merge commit",
                      "points": 0.0, "got": False,
                      "fix": "merge commits always score 0; rebase instead"}]

    score = 0.0
    breakdown = []

    # Length (10..72 ideal)
    n = _byte_len(trimmed)
    if 10 <= n <= 72:
        pts = 0.25
    elif 5 <= n <= 100:
        pts = 0.10
    else:
        pts = 0.0
    score += pts
    breakdown.append({"key": "length", "label": "subject length 10-72",
                      "points": pts, "got": pts == 0.25,
                      "fix": "subject is %d chars; aim for 10-72" % n})

    # Conventional prefix
    has_prefix = _has_prefix(lower)
    pts = 0.30 if has_prefix else 0.0
    score += pts
    breakdown.append({"key": "prefix", "label": "conventional prefix",
                      "points": pts, "got": has_prefix,
                      "fix": "start with feat/fix/chore/docs/style/refactor/"
                             "test/perf/ci/build/revert + ':' or '('"})

    # Scope
    has_scope = ("(" in lower) and ("):" in lower)
    pts = 0.05 if has_scope else 0.0
    score += pts
    breakdown.append({"key": "scope", "label": "scope (...)",
                      "points": pts, "got": has_scope,
                      "fix": "add a scope, e.g. Feat(auth): ..."})

    # Starts with capital letter
    cap = trimmed[0].isupper()
    pts = 0.10 if cap else 0.0
    score += pts
    breakdown.append({"key": "capital", "label": "subject starts uppercase",
                      "points": pts, "got": cap,
                      "fix": "capitalize the first char; with a prefix write "
                             "'Feat(' not 'feat('"})

    # Imperative mood
    fw = _first_word(lower, has_prefix)
    imperative = not (fw.endswith("ing") or fw.endswith("ed")
                      or fw.endswith("tion"))
    pts = 0.10 if imperative else 0.0
    score += pts
    breakdown.append({"key": "imperative", "label": "imperative verb",
                      "points": pts, "got": imperative,
                      "fix": "use Add/Fix/Update, not Adding/Fixed/Creation"})

    # Body bonus
    line_count = len(message.splitlines())
    if line_count > 2:
        pts = 0.20
    elif line_count > 1:
        pts = 0.10
    else:
        pts = 0.0
    score += pts
    breakdown.append({"key": "body", "label": "body (>=3 lines)",
                      "points": pts, "got": pts == 0.20,
                      "fix": "add a blank line + 1 short body line for +0.20"})

    # Penalty: wip / fixup! / squash!
    if ("wip" in lower) or ("fixup!" in lower) or ("squash!" in lower):
        score -= 0.30
        breakdown.append({"key": "wip", "label": "no wip/fixup!/squash!",
                          "points": -0.30, "got": False,
                          "fix": "remove wip/fixup!/squash! — 'wip' also matches "
                                 "inside words like 'swipe'"})

    # Penalty: ALL CAPS
    if (_byte_len(trimmed) > 5 and trimmed == trimmed.upper()
            and any(c.isalpha() for c in trimmed)):
        score -= 0.15
        breakdown.append({"key": "allcaps", "label": "not ALL CAPS",
                          "points": -0.15, "got": False,
                          "fix": "use sentence case, not ALL CAPS"})

    score = max(0.0, min(1.0, score))
    return score, breakdown


def score_commit_message(message):
    return analyze(message)[0]


def _main(argv):
    message = argv[1] if len(argv) > 1 else sys.stdin.read()
    score, breakdown = analyze(message)
    print("score: %.2f" % score)
    for b in breakdown:
        mark = "ok " if b["got"] else "MISS"
        print("  [%s] %-26s %+.2f" % (mark, b["label"], b["points"]))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
