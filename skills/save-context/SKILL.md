---
name: save-context
description: Save what this task taught the agent into ~/.knowledge/<repo>/ - implementation, decisions, rejected alternatives, test results and any architecture it had to figure out - so the next session does not re-explore the project. Use at the end of a task before the final report, when a brief says so, or when the user asks to save context. Argument - task ID.
---

# Save context

Write only what saves the next session work. No conversation retelling, no raw logs, no secrets, tokens or passwords. Do not duplicate CLAUDE.md, AGENTS.md or the repo's own docs; link to them.

## Steps

1. **Knowledge base.**
   ```bash
   repo=$(basename "$(git rev-parse --show-toplevel)"); K=~/.knowledge/$repo
   ```
   If `~/.knowledge/.git` does not exist: `git -C ~/.knowledge init -q` (create the folder first), and write `~/.knowledge/.gitignore` with `.index.sqlite`.
   If `$K/index.md` does not exist, create it:
   ```markdown
   base: <ref>
   # <repo>
   ```
   `<ref>` = the branch work is merged into: `git symbolic-ref --short refs/remotes/origin/HEAD` (for example `origin/main`); no remote → the local main branch. If the user's team integrates into another branch (`origin/develop`, ...), use that.

2. **Task: `$K/tasks/<ID>.md`.** ID = the argument, otherwise the current branch if it looks like a ticket (`[A-Z]+-\d+`), otherwise `YYYY-MM-DD-<slug>`. If the file is missing, create it with `# <ID>: <title>` and, if no brief was saved before, a `## Brief` section with the requirements and decisions you were given. Append:
   - `## Implementation` (first time) or `## Revision <YYYY-MM-DD>` (when `## Implementation` already exists):
     - **Done**: 2-5 bullets;
     - **Files**: changed paths, one line each, "path: what changed";
     - **Decisions**: what was chosen and why; **rejected**: alternative and reason;
     - **Verification**: tests/commands run and their result;
     - **Open**: anything unresolved, what to look at in later revisions.
   Do not rewrite an existing `## Brief`.

3. **Architecture: `$K/architecture/<area>.md`.** One per area you had to explore in this task and where you learned something non-obvious (not what a file name tells in five seconds). Update an existing note rather than adding a duplicate. Format, at most ~80 lines:
   ```markdown
   ---
   paths: [src/auth/, src/middleware/token.rs]
   verified_at: <sha>
   ---
   # <Area>
   ## Purpose
   ## Where things are
   ## Connections
   ## Gotchas
   ```
   `verified_at` = `git merge-base HEAD <base>`. `paths` = only what the note actually describes.

4. **Decisions: `$K/decisions/NNNN-<slug>.md`**, only for a rule future tasks must follow ("all validators are built this way"). One-off decisions stay in the task file. Format: context, decision, why, rejected.

5. **Index.** `$K/index.md` holds one line per file: `- [path] - what it covers, one phrase`. Update lines of changed files, add new ones. For tasks, end the line with a status (`implemented`, `revised YYYY-MM-DD`).

6. **Commit** (to the knowledge repo only; the work repo's commit rules are unaffected):
   ```bash
   git -C ~/.knowledge add -A && git -C ~/.knowledge commit -qm "<repo> <ID>: <summary>"
   ```

The search index rebuilds itself on the next `restore-context`.
