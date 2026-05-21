// Response envelope for md-mcp tools.
//
// Wraps every tool reply with a uniform metadata layer so consuming skills
// always see corpus_state, lock, cost and structured next_step alongside the
// tool-specific result. Backward-compatible: the original result keys remain
// at the top level — `_envelope` is additive.
//
// Phase 1 scope (current): next_step derivation from error patterns, cost
// ledger placeholder, corpus_root resolution from args. Phase 1.2 will fill
// corpus_state via fast SQLite meta read. Phase 4 will fill lock via the
// holder-identity contract.

import { resolve } from "node:path";

const ENVELOPE_VERSION = 1;
const CORPUS_STATE_TTL_MS = 30_000;
const CORPUS_STATE_TIMEOUT_MS = 10_000;

const _ledger = {
  turn_usd: 0,
  session_usd: 0,
  turn_started_at: Date.now()
};

export function recordCost(usd) {
  if (typeof usd !== "number" || !Number.isFinite(usd) || usd <= 0) return;
  _ledger.turn_usd += usd;
  _ledger.session_usd += usd;
}

export function resetTurn() {
  _ledger.turn_usd = 0;
  _ledger.turn_started_at = Date.now();
}

export function getCostSnapshot() {
  return {
    turn_usd: round4(_ledger.turn_usd),
    session_usd: round4(_ledger.session_usd)
  };
}

function round4(n) {
  return Math.round(n * 10000) / 10000;
}

function resolveCorpusRoot(args) {
  // Only resolve from explicit corpus-shaped args. `args.path` is usually a
  // single file (md_preflight, md_impact, md_read_related), not a corpus —
  // running status on it would mis-classify state. `args.scan` is a corpus
  // scope for graph tools; `args.corpus` is the explicit navigator arg.
  if (!args || typeof args !== "object") return null;
  const candidate = args.corpus || args.scan;
  if (!candidate || typeof candidate !== "string") return null;
  try {
    return resolve(candidate);
  } catch {
    return null;
  }
}

const _corpusStateCache = new Map();

export async function quickCorpusState(corpusRoot) {
  if (!corpusRoot) return null;

  const cached = _corpusStateCache.get(corpusRoot);
  if (cached && Date.now() - cached.fetched_at < CORPUS_STATE_TTL_MS) {
    return cached.state;
  }

  try {
    const { resolveNavigatorScript } = await import("./paths.js");
    const { spawnPython, tryParseJson } = await import("./subprocess.js");
    const script = resolveNavigatorScript();
    const { code, stdout } = await spawnPython(
      script,
      ["status", corpusRoot, "--json"],
      { timeoutMs: CORPUS_STATE_TIMEOUT_MS }
    );
    // Exit 0 = success; exit 1 = "no markdown files" — both produce valid
    // state JSON. Exit 2/3 (path/dependency errors) we treat as null.
    if (code === 0 || code === 1) {
      const parsed = tryParseJson(stdout);
      if (parsed && typeof parsed === "object") {
        const slim = {
          state: parsed.state ?? null,
          model: parsed.model ?? null,
          index_exists: parsed.index_exists ?? false,
          last_touched: parsed.last_touched ?? null,
          added_sections: parsed.added_sections ?? 0,
          removed_sections: parsed.removed_sections ?? 0,
          pending_chunks: parsed.pending_chunks ?? 0,
          drift_count: parsed.drift_count ?? 0,
          metadata_mismatch: parsed.metadata_mismatch ?? false,
          delta_too_large: parsed.delta_too_large ?? false,
          recommended_action: parsed.recommended_action ?? null
        };
        _corpusStateCache.set(corpusRoot, { state: slim, fetched_at: Date.now() });
        return slim;
      }
    }
  } catch {
    // Silent fail — corpus_state stays null. We do not want a broken status
    // probe to break the underlying tool reply that the agent actually asked
    // for. Diagnose via md_ping or direct CLI.
  }
  return null;
}

export function invalidateCorpusStateCache(corpusRoot) {
  // Phase 2 mutating tools (md_index, md_init, md_strip confirm:true) should
  // call this after a successful run so the next reply sees fresh state.
  if (corpusRoot) {
    _corpusStateCache.delete(corpusRoot);
  } else {
    _corpusStateCache.clear();
  }
}

function deriveNextStep(result, { toolName, args, corpusRoot }) {
  if (!result || typeof result !== "object") return [];

  // index_warmup: tool refused to embed too many new chunks.
  // Replaces the prose self_repair string with two structured directives.
  if (result.error === "index_warmup_required") {
    const out = [];
    if (corpusRoot) {
      out.push({
        tool: "md_index",
        args: { corpus: corpusRoot, dry_run: true },
        reason: "Preview embedding cost before warming the index."
      });
      out.push({
        tool: "md_index",
        args: { corpus: corpusRoot, confirm: true },
        reason: "After reviewing the dry-run, embed pending chunks."
      });
    }
    if (toolName && args) {
      out.push({
        tool: toolName,
        args,
        reason: "Retry the original call once the index is warm."
      });
    }
    return out;
  }

  // confirm_required: mutating tool was called without confirm:true.
  // Surface the dry-run preview as the first directive.
  if (result.error === "confirm_required") {
    if (!toolName || !args) return [];
    const dryArgs = { ...args };
    delete dryArgs.confirm;
    dryArgs.dry_run = true;
    const confirmArgs = { ...args };
    delete confirmArgs.dry_run;
    confirmArgs.confirm = true;
    return [
      {
        tool: toolName,
        args: dryArgs,
        reason: "Preview affected files before mutation."
      },
      {
        tool: toolName,
        args: confirmArgs,
        reason: "After reviewing the dry-run, apply with confirm:true."
      }
    ];
  }

  // empty: tool ran but returned nothing useful. Hint at scope widening.
  if (result.empty === true) {
    if (toolName !== "md_search" || !args) return [];
    const broaderArgs = { ...args, scope: "descriptions" };
    return [
      {
        tool: "md_search",
        args: broaderArgs,
        reason: "Retry with scope='descriptions' for higher-level matching."
      }
    ];
  }

  return [];
}

// Fields the agent typically iterates. Counting them across known names lets
// us report items_returned without per-tool knowledge.
const COUNTABLE_LIST_FIELDS = [
  "results", "files", "items", "pairs", "proposals", "sections",
  "concepts", "headings", "cycles", "orphans", "hubs", "anchors",
  "issues", "corpora", "unindexed_with_md", "must_read", "must_update",
  "cascade_breaks", "reference_breaks", "body_wikilink_refs",
  "body_markdown_refs", "modified", "changes", "topics", "candidates",
  "folder_breakdown", "scopes"
];

// Soft threshold for "this reply is heavy on attention budget". Surfaces a
// warning so the agent can switch to a narrower path (`top: 5`, scope,
// path_include, or future verbose:false default).
const LARGE_REPLY_BYTES = 10_000;

function computeSizeEstimate(result) {
  if (!result || typeof result !== "object") return null;

  let bytes = null;
  try {
    bytes = JSON.stringify(result).length;
  } catch {}

  let items_returned = 0;
  let counted_fields = [];
  for (const field of COUNTABLE_LIST_FIELDS) {
    const v = result[field];
    if (Array.isArray(v) && v.length > 0) {
      items_returned += v.length;
      counted_fields.push({ field, count: v.length });
    }
  }

  const out = { bytes, items_returned };
  if (counted_fields.length > 0) out.counted_fields = counted_fields;
  if (bytes !== null && bytes > LARGE_REPLY_BYTES) {
    out.large_reply = true;
  }
  return out;
}

/**
 * Wrap a tool result in the standard md-mcp envelope.
 *
 * The original result keys are preserved at the top level so existing callers
 * see no change. The `_envelope` key is additive metadata for newer consumers.
 *
 * @param {*} result - The tool's raw return value (object, string or null).
 * @param {object} options
 * @param {string} options.toolName - The md_* tool name (for next_step).
 * @param {object} [options.args] - Original tool args (for next_step retries).
 * @param {object} [options.lock] - Lock holder info (Phase 4).
 * @param {object} [options.corpusState] - Index/model state (Phase 1.2).
 * @returns {object} Wrapped result with `_envelope` field.
 */
export function wrap(result, { toolName, args, lock = null, corpusState = null } = {}) {
  const corpusRoot = resolveCorpusRoot(args);
  const nextStep = deriveNextStep(result, { toolName, args, corpusRoot });
  const size_estimate = computeSizeEstimate(result);

  const envelope = {
    version: ENVELOPE_VERSION,
    tool: toolName || null,
    corpus_root: corpusRoot,
    corpus_state: corpusState,
    lock,
    cost: getCostSnapshot(),
    size_estimate,
    next_step: nextStep
  };

  if (result === null || result === undefined) {
    return { _envelope: envelope };
  }
  if (typeof result !== "object" || Array.isArray(result)) {
    return { value: result, _envelope: envelope };
  }
  if ("_envelope" in result) {
    // Already wrapped (composite case); merge instead of double-wrapping.
    return result;
  }
  return { ...result, _envelope: envelope };
}
