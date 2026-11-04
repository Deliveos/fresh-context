# fresh-context

Project knowledge for Claude Code that knows when it's stale.

Every new session re-explores your repo: architecture, where things live, how modules connect. When revisions to a task arrive days later, the agent also has to rebuild *why* things were done the way they were. You pay for both in tokens and rate limits, even though almost nothing changed.

`fresh-context` keeps that knowledge in plain Markdown outside your repo and loads only what the current task needs. Before trusting a note it checks git for changes to the files that note describes, so stale knowledge is corrected from the diff instead of misleading the agent.

## Install

```
/plugin marketplace add Deliveos/fresh-context
/plugin install fresh-context@fresh-context
```

Optional, for semantic search: [uv](https://docs.astral.sh/uv/). Without it, search falls back to `rg`.

## Use

- **End of a task:** `/fresh-context:save <TASK-ID>` writes what was done, decisions, rejected alternatives, test results, and any architecture the agent had to figure out.
- **Start of a session:** if the repo has saved knowledge, a session-start hook reminds the agent to run `/fresh-context:restore`, so you don't have to remember. You can also run it yourself, with a task ID when you are revising an earlier task.

Nothing is scanned up front. Knowledge accumulates from real tasks, so it covers the parts of the codebase you actually work on.

## How it works

```
~/.knowledge/                 # its own local git repo: every write is a commit
├── .index.sqlite             # embeddings cache (gitignored)
└── <repo>/                   # basename of the repo's git root
    ├── index.md              # "base: origin/main" + one line per note
    ├── architecture/auth.md  # paths + verified_at sha in front matter
    ├── decisions/0001-validators.md
    └── tasks/PROJ-142.md     # brief → implementation → revisions
```

**Freshness.** Each architecture/decision note records the `paths` it describes and the commit it was `verified_at`. On restore:

```
git log <verified_at>..<base> -- <paths>
```

No commits means the note is trusted and that code isn't re-read. If there are commits, the agent reads only that diff, fixes the note and bumps the sha. A diff is far cheaper than re-exploring.

**Selection.** `restore` reads the short `index.md`, plus a local semantic search (`fastembed`, `intfloat/multilingual-e5-large` on CPU, vectors in SQLite). It finds the right note even when the task's wording differs from the note's, across languages. Nothing leaves your machine.

**Revisions.** `tasks/<ID>.md` keeps the brief, the implementation and each later revision. When changes to an old task come in, the agent reads that file plus `git diff <base>...HEAD` instead of redoing the interview and the exploration.

Knowledge lives outside the repo, so it never ends up in a team repo, survives `git clean`, and doesn't depend on which branch is checked out.

## Notes

- **First semantic search downloads the model (~2 GB)** to `~/.cache/fastembed`; later calls take about a second. For a smaller model, set `FRESH_CONTEXT_MODEL` (any [fastembed text model](https://qdrant.github.io/fastembed/examples/Supported_Models/)), e.g. `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- **Background / auto-mode sessions** need write access outside the repo. Add to `~/.claude/settings.json`:
  ```json
  { "permissions": { "additionalDirectories": ["/home/<you>/.knowledge"] } }
  ```
- **Base branch.** `index.md` starts with `base: <ref>`, auto-detected from `origin/HEAD`. Edit it if your team integrates elsewhere (e.g. `origin/develop`).
- **With your own orchestrator / task runner:** if one session interviews and another implements, have the first one save the brief to `~/.knowledge/<repo>/tasks/<ID>.md` under `## Brief`. Put `fresh-context:restore <ID>` as the first step and `fresh-context:save <ID>` as the last step of the implementer's brief.

## License

MIT
