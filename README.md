# fresh-context

Project knowledge for AI coding agents that knows when it's stale. Works with Claude Code, Codex, GitHub Copilot CLI, Gemini CLI, and any agent that supports `SKILL.md` skills.

Every new session re-explores your repo: architecture, where things live, how modules connect. When revisions to a task arrive days later, the agent also has to rebuild *why* things were done the way they were. You pay for both in tokens and rate limits, even though almost nothing changed.

`fresh-context` keeps that knowledge in plain Markdown outside your repo and loads only what the current task needs. Before trusting a note it checks git for changes to the files that note describes, so stale knowledge is corrected from the diff instead of misleading the agent.

## Install

**Claude Code**
```
/plugin marketplace add Deliveos/fresh-context
/plugin install fresh-context@fresh-context
```

**Codex**
```bash
codex plugin marketplace add Deliveos/fresh-context
codex plugin add fresh-context@fresh-context
```
Then open `/hooks` in `codex` and trust the session-start hook.

**GitHub Copilot CLI**
```bash
copilot plugin marketplace add Deliveos/fresh-context
copilot plugin install fresh-context@fresh-context
```

**Gemini CLI** (also Qwen Code)
```bash
gemini extensions install https://github.com/Deliveos/fresh-context
```

**Any other agent with skills** (Cursor, OpenCode, Cline, Goose, Amp, ...)
```bash
npx skills add Deliveos/fresh-context
```

Optional, for semantic search: [uv](https://docs.astral.sh/uv/). Without it, search falls back to `rg`.

> Tested end to end in Claude Code. The Codex, Copilot and Gemini manifests follow each tool's documented plugin format but have not been tested yet. Issues and PRs welcome.

## Use

- **End of a task:** run the `save-context` skill with the task ID (`/fresh-context:save-context PROJ-142` in Claude Code). It writes what was done, decisions, rejected alternatives, test results, and any architecture the agent had to figure out.
- **Start of a session:** run `restore-context`, with a task ID when you are revising an earlier task. In Claude Code and Codex, a session-start hook reminds the agent to do this whenever the repo has saved knowledge. Gemini CLI gets the same rule from the extension's `AGENTS.md`. For other agents, paste [`AGENTS.md`](AGENTS.md) into your global or project instructions.

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

**Freshness.** Each architecture/decision note records the `paths` it describes and the commit it was `verified_at`. On `restore-context`:

```
git log <verified_at>..<base> -- <paths>
```

No commits means the note is trusted and that code isn't re-read. If there are commits, the agent reads only that diff, fixes the note and bumps the sha. A diff is far cheaper than re-exploring.

**Selection.** `restore-context` reads the short `index.md`, plus a local semantic search (`fastembed`, `intfloat/multilingual-e5-large` on CPU, vectors in SQLite). It finds the right note even when the task's wording differs from the note's, across languages. Nothing leaves your machine.

**Revisions.** `tasks/<ID>.md` keeps the brief, the implementation and each later revision. When changes to an old task come in, the agent reads that file plus `git diff <base>...HEAD` instead of redoing the interview and the exploration.

Knowledge lives outside the repo, so it never ends up in a team repo, survives `git clean`, and doesn't depend on which branch is checked out.

## Notes

- **Windows:** supported. Claude Code runs the skills' shell commands in Git Bash, which it already requires on Windows.
- **The session-start reminder needs `node` on your PATH.** Without it the skills still work; you just run `restore-context` yourself.
- **First semantic search downloads the model (~2 GB)** to `~/.cache/fastembed`; later calls take about a second. For a smaller model, set `FRESH_CONTEXT_MODEL` (any [fastembed text model](https://qdrant.github.io/fastembed/examples/Supported_Models/)), e.g. `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- **Background / auto-mode Claude Code sessions** need write access outside the repo. Add this to your user settings: `~/.claude/settings.json` on Linux and macOS, `%USERPROFILE%\.claude\settings.json` on Windows.
  ```json
  { "permissions": { "additionalDirectories": ["~/.knowledge"] } }
  ```
  If `~` isn't expanded on your system, use the absolute path instead:

  | OS | Value |
  | --- | --- |
  | Linux | `"/home/<you>/.knowledge"` |
  | macOS | `"/Users/<you>/.knowledge"` |
  | Windows | `"C:/Users/<you>/.knowledge"` (forward slashes, or escape each backslash: `"C:\\Users\\<you>\\.knowledge"`) |

- **Base branch.** `index.md` starts with `base: <ref>`, auto-detected from `origin/HEAD`. Edit it if your team integrates elsewhere (e.g. `origin/develop`).
- **With your own orchestrator / task runner:** if one session interviews and another implements, have the first one save the brief to `~/.knowledge/<repo>/tasks/<ID>.md` under `## Brief`. Put `restore-context <ID>` as the first step and `save-context <ID>` as the last step of the implementer's brief.

## Privacy

Everything stays on your machine; nothing is sent anywhere. See [PRIVACY.md](PRIVACY.md).

## License

MIT
