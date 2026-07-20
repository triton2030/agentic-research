import { query } from "@anthropic-ai/claude-agent-sdk";

const CLIENT_APP = "claude-bridge/1.0";
const MAX_TURNS = 24;
const ADVISOR_INSTRUCTION = [
  "Act as an independent advisor.",
  "Investigate and read whatever evidence is necessary, but do not modify files, run state-changing commands, or take external actions.",
  "Return a compact answer to the task below."
].join(" ");

function advisorPrompt(prompt) {
  return `${ADVISOR_INSTRUCTION}\n\n<task>\n${prompt}\n</task>`;
}

function collectModel(models, value) {
  if (typeof value !== "string" || !value || value === "<synthetic>") return;
  if (models.at(-1) !== value) models.push(value);
}

/** Execute one native Claude session turn and reduce typed SDK events. */
export async function runClaudeSdk(launch, options = {}) {
  const isResume = Boolean(launch.sessionId);
  const queryFactory = options.queryFactory || query;
  const handle = queryFactory({
    prompt: advisorPrompt(launch.prompt),
    options: {
      abortController: options.abortController,
      additionalDirectories: ["/"],
      cwd: launch.cwd,
      env: { ...launch.env, CLAUDE_AGENT_SDK_CLIENT_APP: CLIENT_APP },
      maxTurns: MAX_TURNS,
      pathToClaudeCodeExecutable: launch.executable,
      persistSession: true,
      resume: launch.sessionId || undefined,
      spawnClaudeCodeProcess: options.spawnClaudeCodeProcess,
      ...(!isResume ? { effort: launch.profile.effort, model: launch.profile.model } : {})
    }
  });

  let init = null;
  let result = null;
  const primaryModels = [];
  try {
    for await (const message of handle) {
      if (message.type === "system" && message.subtype === "init") {
        init = message;
        collectModel(primaryModels, message.model);
      } else if (message.type === "assistant" && message.parent_tool_use_id === null) {
        collectModel(primaryModels, message.message?.model);
      } else if (message.type === "result") {
        result = message;
      }
    }
  } finally {
    handle.close();
  }

  return {
    init,
    result,
    primaryModels,
    usageModels: Object.keys(result?.modelUsage || {})
  };
}
