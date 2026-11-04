#!/bin/sh
# Nudge the agent to restore knowledge when this repo has some. Silent otherwise.
top=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
dir="$HOME/.knowledge/$(basename "$top")"
[ -f "$dir/index.md" ] || exit 0
echo "fresh-context: project knowledge for this repo exists at $dir. Before exploring the codebase, invoke the fresh-context:restore skill."
