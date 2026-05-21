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
  if (!args || typeof args !== "object") return null;
  const candidate = args.corpus || args.scan || args.path;
  if (!candidate || typeof candidate !== "string") return null;
  try {
    return resolve(candidate);
  } catch {
    return null;
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

  const envelope = {
    version: ENVELOPE_VERSION,
    tool: toolName || null,
    corpus_root: corpusRoot,
    corpus_state: corpusState,
    lock,
    cost: getCostSnapshot(),
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
