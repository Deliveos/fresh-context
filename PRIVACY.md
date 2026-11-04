# Privacy policy

fresh-context has no server, account, analytics or telemetry. It does not send your data anywhere.

## What it stores, and where

Everything stays on your machine:

- `~/.knowledge/<repo>/` — Markdown notes the agent writes about your projects: architecture notes, decisions, and task history (brief, implementation, revisions). The `save-context` skill instructs the agent never to write secrets, tokens, passwords or raw logs into these notes.
- `~/.knowledge/.git` — a local git repository versioning those notes. No remote is configured.
- `~/.knowledge/.index.sqlite` — a local cache of text embeddings for semantic search over the notes.
- `~/.cache/fastembed/` — the downloaded embedding model.

The plugin does not collect personal data. Notes contain only what the agent writes about your code and tasks.

## Network access

The plugin itself sends no data. On the first semantic search, it downloads:

- the embedding model (`intfloat/multilingual-e5-large` by default) from Hugging Face;
- the Python packages `fastembed` and `numpy` through `uv` from PyPI.

These are downloads only; none of your notes, code or prompts are uploaded. Embeddings are computed locally on the CPU.

The coding agent you use (Claude Code, Codex, etc.) reads these notes as part of its context, under that agent's own privacy policy.

## Code that runs

- `hooks/session-start.mjs` (Node.js) at session start: checks whether `~/.knowledge/<repo>/index.md` exists and prints a one-line reminder. It reads no file contents and makes no network calls.
- `skills/restore-context/kb.py` (Python, via `uv`) when the agent searches notes.
- `git` commands on your repository and on `~/.knowledge`, run by the agent as described in the skills.

All of it is in this repository and can be reviewed.

## Deleting your data

```bash
rm -rf ~/.knowledge ~/.cache/fastembed
```

## Contact

Open an issue at https://github.com/Deliveos/fresh-context/issues.
