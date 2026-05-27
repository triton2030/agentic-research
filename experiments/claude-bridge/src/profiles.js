export const MODEL = "opus";

const commonStreamFlags = [
  "--model",
  MODEL,
  "--effort",
  "max",
  "--dangerously-skip-permissions",
  "--output-format",
  "stream-json",
  "--verbose",
  "--include-partial-messages",
  "--include-hook-events"
];

export const PROFILES = {
  normal: {
    description: "Default full-power Opus run with max effort, dangerous permissions, and stream-json logs.",
    flags: [...commonStreamFlags],
    unsupported: false
  },
  "no-memory": {
    description: "Full-power Opus run with Claude auto memory disabled via CLAUDE_CODE_DISABLE_AUTO_MEMORY=1.",
    flags: [...commonStreamFlags],
    unsupported: false,
    env: {
      CLAUDE_CODE_DISABLE_AUTO_MEMORY: "1"
    }
  },
  "no-skills": {
    description: "Full-power Opus run with slash-command skills disabled.",
    flags: [...commonStreamFlags, "--disable-slash-commands"],
    unsupported: false
  },
  "read-only": {
    description: "Read-oriented planning run. This is the main exception to dangerous permissions.",
    flags: [
      "--model",
      MODEL,
      "--effort",
      "max",
      "--permission-mode",
      "plan",
      "--tools",
      "Read,Bash",
      "--output-format",
      "stream-json",
      "--verbose",
      "--include-partial-messages",
      "--include-hook-events"
    ],
    unsupported: false
  },
  turbo: {
    description: "Compatibility alias for the full-power default Opus run.",
    flags: [...commonStreamFlags],
    unsupported: false
  },
  "skill-audit": {
    description: "Audit whether Claude actually reads a target skill/context file.",
    flags: [
      ...commonStreamFlags,
      "--append-system-prompt",
      "You are being audited for context use. Read the requested skill or context with tools before answering. Do not claim you read it unless a tool read happened."
    ],
    unsupported: false
  },
  "streaming-observe": {
    description: "Full-power verbose observation profile for long runs.",
    flags: [...commonStreamFlags],
    unsupported: false
  }
};

export function getProfile(name = "normal") {
  const profile = PROFILES[name];
  if (!profile) {
    throw new Error(`Unknown Claude bridge profile: ${name}`);
  }
  return profile;
}

export function listProfiles() {
  return Object.entries(PROFILES).map(([name, profile]) => ({
    name,
    description: profile.description,
    flags: profile.flags,
    unsupported: profile.unsupported
  }));
}
