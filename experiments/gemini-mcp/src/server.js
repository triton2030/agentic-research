#!/usr/bin/env node
import { execFile } from "node:child_process";
import { existsSync } from "node:fs";
import { homedir } from "node:os";
import path from "node:path";
import { promisify } from "node:util";
import { GoogleGenAI } from "@google/genai";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const DEFAULT_MODEL = "gemini-3.1-pro-preview";
const DEFAULT_THINKING_LEVEL = "high";
const THINKING_LEVELS = ["minimal", "low", "medium", "high"];
const BACKENDS = ["auto", "sdk", "vertex", "cli"];
const execFileAsync = promisify(execFile);

const server = new McpServer({
  name: "gemini-mcp",
  version: "0.1.0"
});

function textResult(value, options = {}) {
  return {
    content: [
      {
        type: "text",
        text: typeof value === "string" ? value : JSON.stringify(value, null, 2)
      }
    ],
    ...options
  };
}

function apiKeySource() {
  if (process.env.GOOGLE_API_KEY) {
    return "GOOGLE_API_KEY";
  }
  if (process.env.GEMINI_API_KEY) {
    return "GEMINI_API_KEY";
  }
  return null;
}

function apiKey() {
  const source = apiKeySource();
  return source ? process.env[source] : null;
}

function envFlag(name) {
  return ["1", "true", "yes"].includes(
    (process.env[name] || "").trim().toLowerCase()
  );
}

function requestedBackend() {
  const backend = process.env.GEMINI_MCP_BACKEND || "auto";
  if (!BACKENDS.includes(backend)) {
    throw new Error(`GEMINI_MCP_BACKEND must be one of: ${BACKENDS.join(", ")}.`);
  }
  return backend;
}

function vertexConfig() {
  return {
    useVertex: envFlag("GOOGLE_GENAI_USE_VERTEXAI"),
    project: process.env.GOOGLE_CLOUD_PROJECT || null,
    location: process.env.GOOGLE_CLOUD_LOCATION || "global",
    adcEnv: process.env.GOOGLE_APPLICATION_CREDENTIALS || null,
    adcFilePresent: existsSync(
      path.join(homedir(), ".config", "gcloud", "application_default_credentials.json")
    )
  };
}

function geminiCliConfig() {
  return {
    command: process.env.GEMINI_CLI_PATH || "gemini",
    oauthFilePresent: existsSync(path.join(homedir(), ".gemini", "oauth_creds.json"))
  };
}

async function geminiCliVersion() {
  try {
    const { stdout } = await execFileAsync(geminiCliConfig().command, ["--version"], {
      timeout: 5000
    });
    return stdout.trim() || "unknown";
  } catch {
    return null;
  }
}

function inferBackend() {
  const requested = requestedBackend();
  const key = apiKey();
  const vertex = vertexConfig();
  const cli = geminiCliConfig();
  const hasVertexAdc = Boolean(vertex.adcEnv || vertex.adcFilePresent);
  const hasVertexConfig = Boolean(vertex.project && (vertex.useVertex || hasVertexAdc));

  if (requested === "sdk") {
    return key ? "gemini-api-key" : null;
  }
  if (requested === "vertex") {
    return vertex.project || key ? "vertex-ai" : null;
  }
  if (requested === "cli") {
    return "gemini-cli";
  }
  if (vertex.useVertex && (vertex.project || key)) {
    return "vertex-ai";
  }
  if (key) {
    return "gemini-api-key";
  }
  if (hasVertexConfig) {
    return "vertex-ai";
  }
  if (cli.oauthFilePresent) {
    return "gemini-cli";
  }
  return null;
}

function defaultModel() {
  return process.env.GEMINI_MODEL || DEFAULT_MODEL;
}

function defaultThinkingLevel() {
  return process.env.GEMINI_THINKING_LEVEL || DEFAULT_THINKING_LEVEL;
}

function validateThinkingLevel(value) {
  if (!THINKING_LEVELS.includes(value)) {
    throw new Error(
      `thinkingLevel must be one of: ${THINKING_LEVELS.join(", ")}.`
    );
  }
  return value;
}

function createSdkClient(backend) {
  const key = apiKey();
  const vertex = vertexConfig();

  if (backend === "vertex-ai") {
    if (key && !vertex.project) {
      return new GoogleGenAI({ vertexai: true, apiKey: key });
    }
    if (!vertex.project) {
      throw new Error(
        "Set GOOGLE_CLOUD_PROJECT for Vertex ADC, or set GOOGLE_API_KEY for Vertex express mode."
      );
    }
    return new GoogleGenAI({
      vertexai: true,
      project: vertex.project,
      location: vertex.location
    });
  }

  if (!key) {
    throw new Error("Set GEMINI_API_KEY or GOOGLE_API_KEY for the Gemini API backend.");
  }
  return new GoogleGenAI({ apiKey: key });
}

function trimText(value, limit = 4000) {
  if (!value || value.length <= limit) {
    return value || "";
  }
  return `${value.slice(0, limit)}\n...[truncated]`;
}

function summarizeCliStderr(stderr) {
  const value = stderr.trim();
  if (!value) {
    return null;
  }
  const firstLine = value.split(/\r?\n/u).find(Boolean);
  const status = value.match(/"status":\s*"([^"]+)"/u)?.[1];
  const message = value.match(/"message":\s*"([^"]+)"/u)?.[1];
  return trimText(
    [firstLine, status && `status=${status}`, message && `message=${message}`]
      .filter(Boolean)
      .join(" | "),
    600
  );
}

function buildCliPrompt(prompt, systemInstruction) {
  if (!systemInstruction) {
    return prompt;
  }
  return `System instruction:\n${systemInstruction}\n\nUser prompt:\n${prompt}`;
}

function parseCliResponse(stdout) {
  const text = stdout.trim();
  if (!text) {
    return "";
  }
  const jsonStart = text.lastIndexOf("\n{");
  const candidate = jsonStart >= 0 ? text.slice(jsonStart + 1) : text;
  try {
    const parsed = JSON.parse(candidate);
    if (typeof parsed.response === "string") {
      return parsed.response;
    }
  } catch {
    // Fall through to plain text output.
  }
  return text;
}

async function askViaCli({
  prompt,
  model,
  systemInstruction,
  thinkingLevel,
  temperature,
  maxOutputTokens
}) {
  const selectedModel = model || defaultModel();
  const selectedThinkingLevel = validateThinkingLevel(
    thinkingLevel || defaultThinkingLevel()
  );
  const unsupported = [];
  if (temperature !== undefined) {
    unsupported.push("temperature");
  }
  if (maxOutputTokens !== undefined) {
    unsupported.push("maxOutputTokens");
  }
  unsupported.push("thinkingLevel");

  const args = [
    "-m",
    selectedModel,
    "-p",
    buildCliPrompt(prompt, systemInstruction),
    "--approval-mode",
    "plan",
    "--output-format",
    "json"
  ];
  const { stdout, stderr } = await execFileAsync(geminiCliConfig().command, args, {
    maxBuffer: 1024 * 1024 * 8,
    timeout: Number(process.env.GEMINI_CLI_TIMEOUT_MS || 50000)
  });

  return {
    backend: "gemini-cli",
    authMode: "gemini-cli-oauth",
    model: selectedModel,
    thinkingLevel: selectedThinkingLevel,
    text: parseCliResponse(stdout),
    usageMetadata: null,
    warnings: [
      `Gemini CLI backend does not expose first-class MCP controls for: ${unsupported.join(", ")}.`,
      ...(summarizeCliStderr(stderr) ? [`gemini stderr: ${summarizeCliStderr(stderr)}`] : [])
    ]
  };
}

async function askViaSdk({
  backend,
  prompt,
  model,
  systemInstruction,
  thinkingLevel,
  temperature,
  maxOutputTokens
}) {
  const ai = createSdkClient(backend);
  const selectedModel = model || defaultModel();
  const selectedThinkingLevel = validateThinkingLevel(
    thinkingLevel || defaultThinkingLevel()
  );
  const config = {
    thinkingConfig: {
      thinkingLevel: selectedThinkingLevel
    }
  };
  if (systemInstruction) {
    config.systemInstruction = systemInstruction;
  }
  if (temperature !== undefined) {
    config.temperature = temperature;
  }
  if (maxOutputTokens !== undefined) {
    config.maxOutputTokens = maxOutputTokens;
  }

  const response = await ai.models.generateContent({
    model: selectedModel,
    contents: prompt,
    config
  });

  return {
    backend,
    authMode: backend === "vertex-ai" ? "vertex-ai" : "api-key",
    model: selectedModel,
    thinkingLevel: selectedThinkingLevel,
    text: response.text || "",
    usageMetadata: response.usageMetadata || null,
    warnings: []
  };
}

function registerTool(name, description, inputSchema, handler) {
  server.registerTool(
    name,
    {
      title: name,
      description,
      inputSchema
    },
    async (args) => {
      try {
        return textResult(await handler(args));
      } catch (error) {
        return textResult(
          {
            error: error instanceof Error ? error.message : String(error)
          },
          { isError: true }
        );
      }
    }
  );
}

registerTool(
  "gemini_status",
  "Report Gemini MCP configuration without making a network call.",
  {},
  async () => {
    const cli = geminiCliConfig();
    const vertex = vertexConfig();
    return {
      ok: true,
      requested_backend: requestedBackend(),
      effective_backend: inferBackend(),
      available_auth: {
        api_key: Boolean(apiKey()),
        api_key_source: apiKeySource(),
        vertex_ai: Boolean(vertex.project || apiKey()),
        vertex_project: vertex.project,
        vertex_location: vertex.location,
        vertex_flag: vertex.useVertex,
        adc_env_present: Boolean(vertex.adcEnv),
        adc_file_present: vertex.adcFilePresent,
        gemini_cli_command: cli.command,
        gemini_cli_version: await geminiCliVersion(),
        gemini_cli_oauth_file_present: cli.oauthFilePresent
      },
      default_model: defaultModel(),
      default_thinking_level: validateThinkingLevel(defaultThinkingLevel()),
      node: process.version
    };
  }
);

registerTool(
  "gemini_ask",
  "Send a one-shot prompt to Gemini 3.1 Pro with high thinking by default and return text plus usage metadata.",
  {
    prompt: z.string().min(1),
    model: z.string().min(1).optional(),
    systemInstruction: z.string().min(1).optional(),
    thinkingLevel: z.enum(THINKING_LEVELS).optional(),
    temperature: z.number().min(0).max(2).optional(),
    maxOutputTokens: z.number().int().positive().optional()
  },
  async ({ prompt, model, systemInstruction, thinkingLevel, temperature, maxOutputTokens }) => {
    const backend = inferBackend();
    if (!backend) {
      throw new Error(
        "No Gemini auth backend is available. Use GEMINI_API_KEY/GOOGLE_API_KEY, Vertex AI with GOOGLE_GENAI_USE_VERTEXAI=true and GOOGLE_CLOUD_PROJECT, or GEMINI_MCP_BACKEND=cli with an authenticated Gemini CLI."
      );
    }
    if (backend === "gemini-cli") {
      return askViaCli({
        prompt,
        model,
        systemInstruction,
        thinkingLevel,
        temperature,
        maxOutputTokens
      });
    }
    return askViaSdk({
      backend,
      prompt,
      model,
      systemInstruction,
      thinkingLevel,
      temperature,
      maxOutputTokens
    });
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
