# fresh-context

Project knowledge lives outside the repo in `~/.knowledge/<repo>/`, where `<repo>` is the basename of the git root.

- **Start of work:** if `~/.knowledge/<repo>/index.md` exists, run the `restore-context` skill before exploring the codebase. Trust a note only after its git freshness check passes.
- **End of a task**, before the final report: run the `save-context` skill with the task ID.
