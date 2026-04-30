import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const serverPath = path.join(root, "src", "server.js");
const smokeHome = fs.mkdtempSync(path.join(os.tmpdir(), "gemini-mcp-home-"));

function baseEnv() {
  const env = Object.fromEntries(
    Object.entries(process.env).filter(([, value]) => value !== undefined)
  );
  delete env.GEMINI_API_KEY;
  delete env.GOOGLE_API_KEY;
  delete env.GEMINI_MODEL;
  delete env.GEMINI_THINKING_LEVEL;
  delete env.GEMINI_MCP_BACKEND;
  delete env.GEMINI_CLI_PATH;
  delete env.GOOGLE_GENAI_USE_VERTEXAI;
  delete env.GOOGLE_CLOUD_PROJECT;
  delete env.GOOGLE_CLOUD_LOCATION;
  delete env.GOOGLE_APPLICATION_CREDENTIALS;
  env.HOME = smokeHome;
  return env;
}

async function withClient(env, callback) {
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [serverPath],
    env
  });
  const client = new Client({ name: "gemini-mcp-smoke", version: "0.1.0" });
  await client.connect(transport);
  try {
    return await callback(client);
  } finally {
    await client.close();
  }
}

await withClient({ ...baseEnv(), PATH: "" }, async (client) => {
  const tools = await client.listTools();
  const toolNames = tools.tools.map((tool) => tool.name);
  assert.deepEqual(toolNames.sort(), ["gemini_ask", "gemini_status"]);

  const status = await client.callTool({ name: "gemini_status", arguments: {} });
  const statusPayload = JSON.parse(status.content[0].text);
  assert.equal(statusPayload.ok, true);
  assert.equal(statusPayload.effective_backend, null);
  assert.equal(statusPayload.available_auth.api_key, false);
  assert.equal(statusPayload.default_model, "gemini-3.1-pro-preview");
  assert.equal(statusPayload.default_thinking_level, "high");

  const ask = await client.callTool({
    name: "gemini_ask",
    arguments: {
      prompt: "Return exactly GEMINI_MCP_OK."
    }
  });
  assert.equal(ask.isError, true);
  assert.match(ask.content[0].text, /Vertex AI|GEMINI_MCP_BACKEND=cli/u);
});

const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "gemini-mcp-smoke-"));
const fakeGemini = path.join(tempDir, "gemini");
fs.writeFileSync(
  fakeGemini,
  `#!/usr/bin/env node
const args = process.argv.slice(2);
if (args.includes("--version")) {
  console.log("fake-gemini 0.0.0");
  process.exit(0);
}
console.log(JSON.stringify({ session_id: "fake", response: "GEMINI_MCP_OK", stats: {} }));
`
);
fs.chmodSync(fakeGemini, 0o755);

await withClient(
  {
    ...baseEnv(),
    GEMINI_MCP_BACKEND: "cli",
    GEMINI_CLI_PATH: fakeGemini
  },
  async (client) => {
    const status = await client.callTool({ name: "gemini_status", arguments: {} });
    const statusPayload = JSON.parse(status.content[0].text);
    assert.equal(statusPayload.effective_backend, "gemini-cli");
    assert.equal(statusPayload.available_auth.gemini_cli_version, "fake-gemini 0.0.0");

    const ask = await client.callTool({
      name: "gemini_ask",
      arguments: {
        prompt: "Return exactly GEMINI_MCP_OK."
      }
    });
    assert.equal(ask.isError, undefined);
    const payload = JSON.parse(ask.content[0].text);
    assert.equal(payload.backend, "gemini-cli");
    assert.equal(payload.text, "GEMINI_MCP_OK");
  }
);

process.stdout.write("gemini-mcp smoke ok\n");
