#!/usr/bin/env python3
"""PreToolUse/Bash hook for clean-commit.

On every `git commit`: strip the Claude co-author / "Generated with" trailers and
block any message scoring below CLEAN_COMMIT_MIN_SCORE (default 0.9). Fail-open:
on any error, emit nothing so the tool proceeds unchanged.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from score_commit import analyze  # noqa: E402

# Match only the Claude bot trailer, identified by its noreply@anthropic.com
# address — never a human co-author (even one whose name happens to be Claude).
TRAILER_RE = re.compile(r"(?i)^\s*co-authored-by:.*noreply@anthropic\.com")
GENERATED_RE = re.compile(r"generated with \[?claude code", re.IGNORECASE)

# Full point value of each positive scoring rule, for the deny-message fix list.
RULE_MAX = {"length": 0.25, "prefix": 0.30, "scope": 0.05,
            "capital": 0.10, "imperative": 0.10, "body": 0.20}

# Match `git commit` only at a command position — start of line, or after a shell
# separator (so `cd x && git commit` counts) — but NOT when it merely appears
# inside a quoted string (`echo "git commit"`, a Python literal, etc.).
_GIT_COMMIT_RE = re.compile(r"(?:^|[\n;&|(])\s*git\s+commit\b")


def is_trailer_line(line):
    """True if a physical line is a Claude co-author or generated-with trailer."""
    if TRAILER_RE.search(line):
        return True
    if GENERATED_RE.search(line):
        return True
    return False


_M_ARG_RE = re.compile(r"""-m\s+("[^"]*"|'[^']*')""")


def _strip_trailer_m_args(command):
    """Remove `-m "<trailer>"` arguments whose content is a Claude trailer."""
    def repl(m):
        inner = m.group(1)[1:-1]
        return "" if is_trailer_line(inner) else m.group(0)
    return _M_ARG_RE.sub(repl, command)


def strip_trailer(command):
    """Remove Claude trailers from the whole command string (both -m args and
    physical heredoc lines). Leaves human co-authors and everything else intact."""
    command = _strip_trailer_m_args(command)
    kept = [ln for ln in command.split("\n") if not is_trailer_line(ln)]
    return "\n".join(kept)


_HEREDOC_RE = re.compile(r"<<-?\s*['\"]?([A-Za-z_][A-Za-z0-9_]*)['\"]?")
_MSG_RE = re.compile(r"""-m\s+(?:"([^"]*)"|'([^']*)')""")


def extract_message(command):
    """Best-effort extraction of the commit message for scoring. None if unsure."""
    m = _HEREDOC_RE.search(command)
    if m:
        delim = m.group(1)
        rest = command[m.end():].split("\n")
        body = []
        for i, ln in enumerate(rest):
            if i == 0:
                continue  # remainder of the heredoc-opening physical line
            if ln.strip() == delim:
                return "\n".join(body)
            body.append(ln)
        return None  # no terminator -> unsure
    parts = []
    for mm in _MSG_RE.finditer(command):
        parts.append(mm.group(1) if mm.group(1) is not None else mm.group(2))
    if parts:
        return "\n\n".join(parts)
    return None


def build_output(decision, reason=None, updated_command=None):
    hso = {"hookEventName": "PreToolUse", "permissionDecision": decision}
    if reason is not None:
        hso["permissionDecisionReason"] = reason
    if updated_command is not None:
        hso["updatedInput"] = {"command": updated_command}
    return {"hookSpecificOutput": hso}


# Standard lowercase Conventional Commits forgo the +0.10 "uppercase first char"
# bonus, so a complete commit tops out at 0.90. Default the gate there.
_DEFAULT_MIN_SCORE = "0.9"
# Tolerance so float rounding (e.g. 0.25+0.30+0.05+0.10+0.20) can't deny a commit
# that is exactly at the threshold.
_EPSILON = 1e-9


def _threshold():
    try:
        return float(os.environ.get("CLEAN_COMMIT_MIN_SCORE", _DEFAULT_MIN_SCORE))
    except ValueError:
        return float(_DEFAULT_MIN_SCORE)


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except Exception:
        return  # fail-open
    command = (data.get("tool_input") or {}).get("command")
    if not isinstance(command, str) or not _GIT_COMMIT_RE.search(command):
        return  # passthrough

    cleaned = strip_trailer(command)
    stripped = cleaned != command

    message = extract_message(cleaned)
    if message is None:
        # Cannot score; still remove a trailer if one was present.
        if stripped:
            print(json.dumps(build_output("allow", updated_command=cleaned)))
        return

    score, breakdown = analyze(message)
    if score < _threshold() - _EPSILON:
        # A standard lowercase commit tops out at 0.90, so when the gate is at or
        # below that, the +0.10 "uppercase first char" rule is never required —
        # don't suggest capitalizing the prefix, which we deliberately avoid.
        suppress_capital = _threshold() <= 0.90 + _EPSILON
        missing = [b for b in breakdown if not b["got"]
                   and not (suppress_capital and b["key"] == "capital")]
        lines = ["clean-commit: message scores %.2f (need %.2f)."
                 % (score, _threshold())]
        for b in missing:
            # Show the points at stake: the rule's full value for an unearned
            # bonus, or the penalty already deducted.
            worth = RULE_MAX.get(b["key"], b["points"])
            lines.append("  - %s (%+.2f): %s" % (b["label"], worth, b["fix"]))
        lines.append("Rewrite the commit message and try again.")
        print(json.dumps(build_output("deny", reason="\n".join(lines))))
        return

    if stripped:
        print(json.dumps(build_output("allow", updated_command=cleaned)))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # fail-open
