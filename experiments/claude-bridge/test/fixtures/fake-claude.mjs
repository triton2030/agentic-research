#!/usr/bin/env node
import fs from "node:fs";

if (process.argv.slice(2).join(" ") !== "auth status") process.exit(64);
if (process.env.FAKE_AUTH_PID_FILE) fs.writeFileSync(process.env.FAKE_AUTH_PID_FILE, String(process.pid));
if (process.env.FAKE_AUTH_ENV_FILE) {
  fs.writeFileSync(process.env.FAKE_AUTH_ENV_FILE, JSON.stringify({
    ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY || null,
    CLAUDE_CODE_USE_VERTEX: process.env.CLAUDE_CODE_USE_VERTEX || null,
    CLAUDE_CONFIG_DIR: process.env.CLAUDE_CONFIG_DIR || null
  }));
}

const barrierDir = process.env.FAKE_AUTH_BARRIER_DIR;
if (barrierDir) {
  fs.mkdirSync(barrierDir, { recursive: true });
  fs.writeFileSync(`${barrierDir}/${process.pid}`, "ready");
  const deadline = Date.now() + 2000;
  while (fs.readdirSync(barrierDir).length < 2 && Date.now() < deadline) {
    await new Promise((resolve) => setTimeout(resolve, 10));
  }
  if (fs.readdirSync(barrierDir).length < 2) process.exit(65);
}

const delayMs = Number(process.env.FAKE_AUTH_DELAY_MS || 0);
if (delayMs) await new Promise((resolve) => setTimeout(resolve, delayMs));
process.stdout.write(process.env.FAKE_AUTH_JSON || JSON.stringify({
  loggedIn: true,
  authMethod: "claude.ai",
  apiProvider: "firstParty",
  subscriptionType: "max"
}));
