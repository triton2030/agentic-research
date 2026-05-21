import { existsSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));

function firstExisting(candidates) {
  for (const candidate of candidates) {
    if (candidate && existsSync(candidate)) return candidate;
  }
  return null;
}

export function resolveNavigatorScript() {
  const fromEnv = process.env.MD_NAVIGATOR_SCRIPT;
  const inRepo = resolve(here, "..", "..", "scripts", "md_navigator.py");
  const claudeSkill = resolve(homedir(), ".claude", "skills", "1md-navigator", "scripts", "md_navigator.py");
  const found = firstExisting([fromEnv, inRepo, claudeSkill]);
  if (!found) {
    throw new Error(
      `md_navigator.py not found. Set MD_NAVIGATOR_SCRIPT, or check ${inRepo} or ${claudeSkill}.`
    );
  }
  return found;
}

export function resolveGraphScript() {
  const fromEnv = process.env.MD_GRAPH_SCRIPT;
  const claudeSkill = resolve(homedir(), ".claude", "skills", "1md-graph", "scripts", "md_graph.py");
  const codexSkill = resolve(homedir(), ".codex", "skills", "1md-graph", "scripts", "md_graph.py");
  const found = firstExisting([fromEnv, claudeSkill, codexSkill]);
  if (!found) {
    throw new Error(
      `md_graph.py not found. Set MD_GRAPH_SCRIPT, or check ${claudeSkill} or ${codexSkill}.`
    );
  }
  return found;
}
