// Nudge the agent to restore knowledge when this repo has some. Silent otherwise.
// Finds the git root by walking up to the nearest .git (dir, or file in worktrees),
// without spawning git, so the hook stays a single readable file.
import { existsSync } from 'node:fs';
import { homedir } from 'node:os';
import { basename, dirname, join } from 'node:path';

let dir = process.cwd();
while (!existsSync(join(dir, '.git'))) {
  const up = dirname(dir);
  if (up === dir) process.exit(0); // not inside a git repo
  dir = up;
}
const knowledge = join(homedir(), '.knowledge', basename(dir));
if (existsSync(join(knowledge, 'index.md'))) {
  console.log(`fresh-context: project knowledge for this repo exists at ${knowledge}. Before exploring the codebase, run the restore-context skill (fresh-context plugin).`);
}
