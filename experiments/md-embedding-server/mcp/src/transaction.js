// Edit transaction tokens for mutating md-mcp tools.
//
// Phase 2: closes the TOCTOU between dry_run preview and confirm:true live
// run. Dry-run captures a content fingerprint of the affected file set;
// confirm requires the matching transaction_id and re-verifies that no file
// changed between the two calls.
//
// In-memory only — single MCP server instance per session. 5-minute TTL is a
// safety belt; the agent normally consumes a transaction within seconds.

import { createHash, randomBytes } from "node:crypto";
import { readFile } from "node:fs/promises";

const TXN_TTL_MS = 5 * 60_000;
const _txns = new Map();

function _gc() {
  const cutoff = Date.now() - TXN_TTL_MS;
  for (const [id, txn] of _txns) {
    if (txn.created_at < cutoff) _txns.delete(id);
  }
}

export async function computeFingerprint(filePaths) {
  const items = [];
  for (const p of filePaths) {
    let hash;
    try {
      const content = await readFile(p, "utf-8");
      hash = createHash("sha256").update(content).digest("hex").slice(0, 16);
    } catch (e) {
      hash = e && e.code === "ENOENT" ? "MISSING" : "UNREADABLE";
    }
    items.push({ path: p, hash });
  }
  items.sort((a, b) => a.path.localeCompare(b.path));
  const combined = items.map((i) => `${i.path}:${i.hash}`).join("\n");
  return {
    fingerprint: createHash("sha256").update(combined).digest("hex").slice(0, 32),
    files: items
  };
}

export function createTransaction({ tool, args, fingerprint, files }) {
  _gc();
  const id = `txn_${randomBytes(8).toString("hex")}`;
  _txns.set(id, {
    id,
    tool,
    args,
    fingerprint,
    files,
    created_at: Date.now()
  });
  return {
    id,
    expires_at: new Date(Date.now() + TXN_TTL_MS).toISOString()
  };
}

export function getTransaction(id) {
  _gc();
  return _txns.get(id) || null;
}

export async function verifyTransaction(id, expectedTool) {
  const txn = getTransaction(id);
  if (!txn) {
    return { ok: false, reason: "unknown_or_expired" };
  }
  if (txn.tool !== expectedTool) {
    return {
      ok: false,
      reason: "tool_mismatch",
      expected: expectedTool,
      got: txn.tool
    };
  }
  const { fingerprint: currentFp } = await computeFingerprint(txn.files.map((f) => f.path));
  if (currentFp !== txn.fingerprint) {
    return {
      ok: false,
      reason: "drift_detected",
      original_fingerprint: txn.fingerprint,
      current_fingerprint: currentFp,
      original_files: txn.files
    };
  }
  return { ok: true, txn };
}

export function consumeTransaction(id) {
  _txns.delete(id);
}
