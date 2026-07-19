export const MODEL = "opus";

const commonStreamFlags = [
  "--output-format",
  "stream-json",
  "--verbose",
  "--include-partial-messages",
  "--include-hook-events"
];

function fullPowerFlags(model = MODEL, effort = "xhigh") {
  return [
    "--model",
    model,
    "--effort",
    effort,
    "--dangerously-skip-permissions",
    ...commonStreamFlags
  ];
}

function advisorFlags(model = MODEL, effort = "xhigh") {
  return [
    "--model",
    model,
    "--effort",
    effort,
    "--permission-mode",
    "plan",
    "--disallowedTools",
    "Bash,Edit,Write,NotebookEdit",
    ...commonStreamFlags
  ];
}

function workerFlags(model = MODEL, effort = "xhigh") {
  return [
    "--model",
    model,
    "--effort",
    effort,
    "--permission-mode",
    "auto",
    ...commonStreamFlags
  ];
}

export const PROFILES = {
  unrestricted: {
    description: "Explicit full-power Opus run with permission bypass. Use only when the user authorized an unrestricted Claude worker.",
    flags: fullPowerFlags(),
    unsupported: false
  },
  normal: {
    description: "Compatibility alias for the safe Opus advisor profile.",
    flags: advisorFlags(),
    unsupported: false
  },
  advisor: {
    description: "Default persistent/read-only Opus advisor with plan mode and write-capable tools removed.",
    flags: advisorFlags(),
    unsupported: false
  },
  "fable-advisor": {
    description: "Fable 5 super-advisor for the hardest long-horizon decisions; read-only and xhigh effort.",
    flags: advisorFlags("fable", "xhigh"),
    unsupported: false
  },
  worker: {
    description: "Opus worker with auto permissions. Use only for an explicitly authorized write task.",
    flags: workerFlags(),
    unsupported: false
  },
  "no-memory": {
    description: "Read-only Opus advisor with Claude auto memory disabled via CLAUDE_CODE_DISABLE_AUTO_MEMORY=1.",
    flags: advisorFlags(),
    unsupported: false,
    env: {
      CLAUDE_CODE_DISABLE_AUTO_MEMORY: "1"
    }
  },
  "no-skills": {
    description: "Read-only Opus advisor with slash-command skills disabled.",
    flags: [...advisorFlags(), "--disable-slash-commands"],
    unsupported: false
  },
  "read-only": {
    description: "Read-oriented planning run. This is the main exception to dangerous permissions.",
    flags: [
      "--model",
      MODEL,
      "--effort",
      "xhigh",
      "--permission-mode",
      "plan",
      "--disallowedTools",
      "Bash,Edit,Write,NotebookEdit",
      ...commonStreamFlags
    ],
    unsupported: false
  },
  turbo: {
    description: "Compatibility alias for the safe Opus advisor profile.",
    flags: advisorFlags(),
    unsupported: false
  },
  "skill-audit": {
    description: "Audit whether Claude actually reads a target skill/context file.",
    flags: [
      ...advisorFlags(),
      "--append-system-prompt",
      "You are being audited for context use. Read the requested skill or context with tools before answering. Do not claim you read it unless a tool read happened."
    ],
    unsupported: false
  },
  "streaming-observe": {
    description: "Read-only Opus advisor profile for long observable runs.",
    flags: advisorFlags(),
    unsupported: false
  }
};

export function getProfile(name = "advisor") {
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
