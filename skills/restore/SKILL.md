---
name: restore
description: Restore what is already known about this repo and task from ~/.knowledge/<repo>/ (architecture notes, decisions, task history) before exploring code, and verify each note against git so stale knowledge is never trusted. Use at the start of work in a repo that has ~/.knowledge/<repo>/, when a session-start reminder or a brief says so, or when the user asks to restore context. Optional argument - task ID.
---

# Restore context

Goal: do not re-explore what is already known. Read the notes, trust each one exactly as far as git confirms it, and explore code only where knowledge is missing or stale.

## Steps

1. **Locate the knowledge base.**
   ```bash
   repo=$(basename "$(git rev-parse --show-toplevel)"); K=~/.knowledge/$repo
   ```
   If `$K` does not exist, say "no saved knowledge for this repo" and stop. Work as usual; the `save` skill will create it at the end.

2. **Read `$K/index.md`.** Its first line `base: <ref>` is the branch notes are verified against (for example `origin/main`).

3. **Task.** Task ID = the argument, otherwise the current branch name if it looks like a ticket (`[A-Z]+-\d+`). If `$K/tasks/<ID>.md` exists, read it fully: brief, implementation, earlier revisions. Then look at the work already done: `git diff <base>...HEAD --stat` and `git status --short`. Read the diff of a specific file only when the current change needs it.

4. **Find relevant notes.** Semantic search (needs `uv`; `kb.py` sits next to this SKILL.md in the skill's base directory):
   ```bash
   uv run --script "<this skill's base directory>/kb.py" search "<the task in your own words>" -k 8
   ```
   Add `--all` when the task touches a neighbouring repo/service. The first run downloads the embedding model (~2 GB) and may take a few minutes; later runs take about a second.
   If `uv` is missing or the search fails, fall back to `rg -il '<keyword>|<keyword>' "$K"`.
   Merge the results with whatever in `index.md` obviously relates to the task. Keep only what is relevant. e5 scores are high for everything (0.75+), so judge by the gap from the rest and by the heading, not by the absolute number.

5. **Verify freshness** of every selected `architecture/*` and `decisions/*` note (front matter `paths`, `verified_at`):
   ```bash
   git log --oneline <verified_at>..<base> -- <paths...>
   ```
   - Empty: trust the note; do not read code under those paths just to understand it.
   - Commits listed: read `git diff <verified_at>..<base> -- <paths...>`, fix the note to match, set `verified_at: $(git rev-parse <base>)`.
   - Unknown sha (`git cat-file -e <sha>` fails): `git fetch`; if still unknown, re-check the note against the code and update the sha.

6. **Commit note fixes**, if any:
   ```bash
   git -C ~/.knowledge add -A && git -C ~/.knowledge commit -qm "<repo>: refresh <notes>"
   ```

7. **Summarize for yourself** (short, not a retelling):
   - what is known and verified (with note paths);
   - what was corrected;
   - **what is not covered**: explore those areas normally and remember what you learn, so `save` can store it at the end.

Never echo secrets if they ended up in a note.
