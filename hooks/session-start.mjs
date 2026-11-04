// Nudge the agent to restore knowledge when this repo has some. Silent otherwise.
import { execFileSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { homedir } from 'node:os';
import { basename, join } from 'node:path';

let top;
try {
  top = execFileSync('git', ['rev-parse', '--show-toplevel'], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
} catch {
  process.exit(0); // not a git repo, or git missing
}
const dir = join(homedir(), '.knowledge', basename(top));
if (existsSync(join(dir, 'index.md'))) {
  console.log(`fresh-context: project knowledge for this repo exists at ${dir}. Before exploring the codebase, run the restore-context skill (fresh-context plugin).`);
}
