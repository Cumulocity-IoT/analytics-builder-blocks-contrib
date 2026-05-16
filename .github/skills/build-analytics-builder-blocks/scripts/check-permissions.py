#!/usr/bin/env python3
"""
PreToolUse hook for the build-analytics-builder-blocks skill.

- Auto-approves safe, local-only build workflow commands.
- Requires explicit user approval for any command that deploys to a
  Cumulocity tenant (--cumulocity_url) or restarts a microservice (--restart).
- Passes through silently for everything else (no output, exit 0).
"""

import json
import re
import sys

data = json.load(sys.stdin)

tool = data.get("tool_name", "") or data.get("tool", "")
params = data.get("tool_input", {}) or data.get("input", {})
command = params.get("command", "") or params.get("cmd", "")

# Only act on terminal / shell tool calls
if tool not in ("run_in_terminal", "Bash", "bash"):
    sys.exit(0)

# --- Deployment commands: always require explicit user approval ---
if "--cumulocity_url" in command or "--restart" in command:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": (
                "This command deploys to a live Cumulocity tenant and will restart "
                "the Apama microservice. Explicit approval is required."
            ),
        }
    }))
    sys.exit(0)

# --- Safe build-workflow patterns: auto-approve ---
SAFE_PATTERNS = [
    # Discovery and file reading (read-only)
    r"\bfind\b",
    r"\bls\b",
    r"\bgrep\b",
    r"\bwc\b",
    r"\bunzip\s+-l\b",
    r"\bcat\b",
    r"\bsed\b",
    r"\bhead\b",
    r"\btail\b",
    # Local directory creation
    r"\bmkdir\s+-p\s+(temp-|\S*release-artifacts)",
    # Copying block source files into a temp dir
    r"\bcp\b.*\.mon\b.*\btemp-",
    r"\bcp\b.*\.(yaml|properties)\b.*\btemp-",
    # Copying companion files via shell loop (ext in yaml properties)
    r"\bfor\s+ext\s+in\s+(yaml|properties)",
    # Running PySys tests
    r"\bpysys\s+run\b",
    # Building an extension bundle (no deployment flags)
    # Note: the binary path is often quoted: "$ANALYTICS_BUILDER_SDK/analytics_builder" build extension
    # so we allow an optional trailing quote character before the whitespace.
    r"\banalytics_builder[\"']*\s+build\s+extension\b",
    # Removing only the temporary staging directory created by the workflow
    r"\brm\s+-rf\s+\S*temp-\S*",
    # Removing generated PySys test output directories (safe — fully regenerated on each run)
    r"\brm\s+-rf\s+tests/[^/]+/Output\b",
    r"\brm\s+-rf\s+\S+/Output(/linux)?\b",
]

for pattern in SAFE_PATTERNS:
    if re.search(pattern, command):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "permissionDecisionReason": "Approved: safe Analytics Builder block build workflow command.",
            }
        }))
        sys.exit(0)

# Everything else: pass through to default approval flow
sys.exit(0)
