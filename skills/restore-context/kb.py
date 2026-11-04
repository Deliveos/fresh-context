#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = ["fastembed", "numpy"]
# ///
"""Semantic search over ~/.knowledge notes (local, CPU, no daemon).

  kb.py search "<text>" [--repo R | --all] [-k 8]
  kb.py selftest
"""
import argparse, hashlib, os, sqlite3, subprocess, sys, tempfile
from pathlib import Path

import numpy as np

ROOT = Path(os.environ.get("KB_ROOT", Path.home() / ".knowledge"))
# Multilingual so notes and queries may mix languages.
MODEL = os.environ.get("FRESH_CONTEXT_MODEL", "intfloat/multilingual-e5-large")
_model = None


def embed(texts, prefix):
    global _model
    if _model is None:
        from fastembed import TextEmbedding
        _model = TextEmbedding(MODEL, cache_dir=str(Path.home() / ".cache/fastembed"))
    v = np.array(list(_model.embed([prefix + t for t in texts])), dtype=np.float32)
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def chunks(text):
    """Split on '## ' headings; front matter and the part before the first ## form one chunk."""
    parts, title, buf = [], "", []
    for line in text.splitlines():
        if line.startswith("## "):
            if "".join(buf).strip():
                parts.append((title, "\n".join(buf)))
            title, buf = line[3:].strip(), [line]
        else:
            buf.append(line)
    if "".join(buf).strip():
        parts.append((title, "\n".join(buf)))
    return parts


def reindex(db):
    db.execute("create table if not exists files(path text primary key, sha text)")
    db.execute("create table if not exists chunks(path text, section text, body text, vec blob)")
    known = dict(db.execute("select path, sha from files"))
    seen = set()
    for f in ROOT.rglob("*.md"):
        rel = str(f.relative_to(ROOT))
        if rel.startswith("."):
            continue
        seen.add(rel)
        text = f.read_text(errors="replace")
        sha = hashlib.sha1(text.encode()).hexdigest()
        if known.get(rel) == sha:
            continue
        db.execute("delete from chunks where path=?", (rel,))
        parts = chunks(text)
        if parts:
            vecs = embed([f"{rel}\n{body}" for _, body in parts], "passage: ")
            db.executemany("insert into chunks values(?,?,?,?)",
                           [(rel, t, b, v.tobytes()) for (t, b), v in zip(parts, vecs)])
        db.execute("insert or replace into files values(?,?)", (rel, sha))
    for rel in set(known) - seen:
        db.execute("delete from chunks where path=?", (rel,))
        db.execute("delete from files where path=?", (rel,))
    db.commit()


def search(query, repo=None, k=8):
    db = sqlite3.connect(ROOT / ".index.sqlite")
    reindex(db)
    sql, args = "select path, section, body, vec from chunks", ()
    if repo:
        sql, args = sql + " where path like ?", (repo + "/%",)
    rows = db.execute(sql, args).fetchall()
    if not rows:
        return []
    m = np.stack([np.frombuffer(r[3], dtype=np.float32) for r in rows])
    scores = m @ embed([query], "query: ")[0]
    return [(float(scores[i]), *rows[i][:3]) for i in np.argsort(-scores)[:k]]


def current_repo():
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True)
        return Path(top.stdout.strip()).name
    except subprocess.CalledProcessError:
        return None


def selftest():
    global ROOT
    with tempfile.TemporaryDirectory() as d:
        ROOT = Path(d)
        (ROOT / "r/architecture").mkdir(parents=True)
        (ROOT / "r/architecture/auth.md").write_text(
            "## Purpose\nIssues JWT access tokens and refreshes them when the API returns 401.\n")
        (ROOT / "r/architecture/pdf.md").write_text(
            "## Purpose\nRenders invoices to PDF files and stores them in S3.\n")
        top = search("how is the auth token refreshed", repo="r", k=1)
        assert top[0][1] == "r/architecture/auth.md", top
        (ROOT / "r/architecture/pdf.md").unlink()
        assert all(p != "r/architecture/pdf.md" for _, p, *_ in search("PDF", k=5)), "deleted file is still in the index"
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--repo")
    s.add_argument("--all", action="store_true")
    s.add_argument("-k", type=int, default=8)
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    repo = None if a.all else (a.repo or current_repo())
    if not a.all and not repo:
        sys.exit("not in a git repo: pass --repo or --all")
    for score, path, section, body in search(a.query, repo, a.k):
        first = next((l for l in body.splitlines() if l.strip() and not l.startswith("#")), "")
        print(f"{score:.3f}  {path}#{section}  {first[:100]}")


if __name__ == "__main__":
    main()
