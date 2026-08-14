"""Shared Codex runtime defaults for bridge entrypoints.

Keep this module SDK-free so dry-run validation stays cheap and does not start
or import the Codex runtime.
"""
from __future__ import annotations

from pathlib import Path

# Ярусы вызова (решение владельца 2026-08-14, дословно: «по дефолту мы будем
# использовать сол экстра хай всегда и луна только для тупых и больших
# заданий»). Это разворот его же решения 2026-07-27, снявшего xhigh с дефолта
# как слишком долгий: цена размышления снова признана оправданной.
#
#   sol + xhigh   — ДЕФОЛТ на всё. На пути ревьюера идёт диалогом, а не
#                   выстрелом: см. HEAVY_EFFORTS ниже.
#   sol + max/ultra — глубже дефолта: max — глубина одного прогона,
#                   ultra — она же плюс делегация субагентам внутри движка.
#   luna          — тупые и большие задания: много механического текста,
#                   где нужна пропускная способность, а не суждение.
#
# terra остаётся доступен явным --model (его дефолтом держит md-scout в
# md-tools), но штатным лёгким ярусом моста быть перестал.
DEFAULT_CODEX_MODEL = "gpt-5.6-sol"
DEFAULT_CODEX_EFFORT = "xhigh"

# Лёгкая модель для тупой и объёмной работы; выбирается явным --model.
LIGHT_CODEX_MODEL = "gpt-5.6-luna"

# Усилия, на которых одиночный выстрел — плохая форма: прогон длинный, читает
# много, и ценность появляется во втором-третьем обмене. На пути ревьюера они
# включают персистентный тред автоматически (`--no-dialog` снимает).
#
# xhigh ушёл отсюда вместе с переездом на него дефолта (2026-08-14): автотред
# задумывался для РЕДКОГО тяжёлого прогона, а на дефолтном ярусе он ломал
# инвариант «мост не материализует треды в общий store ~/.codex» — каждый
# обычный вызов становился бы чатом в Codex Desktop. На xhigh диалог остаётся
# по явному --dialog.
HEAVY_EFFORTS = ("max", "ultra")

# Service tier: the bridge does NOT request fast anymore (owner reversal
# 2026-07-25 of the 2026-07-20 "always fast" rule — the priority flag was
# removed). Default None → the SDK omits the param entirely (it dumps with
# exclude_none=True, openai_codex/client.py), so the engine falls back to
# ~/.codex/config.toml service_tier. The bridge likewise no longer forces the
# `features.fast_mode` gate at app-server launch. Explicit --service-tier
# (e.g. "priority"; docs alias "fast" normalizes to it in the engine's model
# catalog, both live-probed 2026-07-20) remains a deliberate per-run opt-in —
# note that without the config feature gate the tier request alone may not
# route Fast. CAVEAT (do not overclaim): the ledger + banner record the
# REQUESTED tier (built from args before the SDK call) — a self-report of
# intent, NOT proof the server applied it; billing is only visible on the
# credit dashboard.
DEFAULT_CODEX_SERVICE_TIER = None

# gpt-5.6-sol requires a newer codex binary than the SDK pins (0.1.0b3 pins
# codex-cli 0.137.0a4 → HTTP 400 "requires a newer version of Codex"). The
# ChatGPT desktop app bundles a current binary and auto-updates it, so the
# bridge prefers it and falls back to the SDK bundle only if the app is gone
# (verified live 2026-07-10: bundled 0.137.0a4 rejects the model, app binary
# 0.144.0a4 serves it).
CHATGPT_APP_CODEX_BIN = "/Applications/ChatGPT.app/Contents/Resources/codex"


def resolve_codex_bin() -> str | None:
    """Path to the preferred codex binary, or None for the SDK bundle."""
    if Path(CHATGPT_APP_CODEX_BIN).is_file():
        return CHATGPT_APP_CODEX_BIN
    return None


def codex_bin_source(codex_bin: str | None) -> str:
    """Ledger/stderr label for the engine the bridge is about to launch."""
    return "chatgpt-app" if codex_bin else "sdk-bundle"


# The fallback engine is not a silent equivalent: the default model fails on it.
SDK_BUNDLE_WARNING = (
    "[codex-bridge] ChatGPT.app не найден — запуск на бандл-бинаре SDK; "
    f"default-модель {DEFAULT_CODEX_MODEL} на нём отвечает HTTP 400 "
    "'requires a newer version of Codex' (поставь ChatGPT.app или передай "
    "--model, который старый движок ещё знает)."
)

# Floor is "low": default turn tools (web_search/image_gen) reject lower
# efforts at Codex runtime (HTTP 400), so "none"/"minimal" are cut here to fail
# fast at flag validation.
#
# The upper scale mirrors the engine's own catalogue
# (~/.codex/models_cache.json → supported_reasoning_levels), read 2026-07-27 for
# gpt-5.6-sol/terra. Its wording is the contract:
#   "max"   — "Maximum reasoning depth for the hardest problems"
#   "ultra" — "Maximum reasoning with automatic task delegation"
# So "max" is depth for ONE run and "ultra" is that depth plus internal
# sub-agent delegation. "max" used to be missing here, which left no way to ask
# for maximum depth without delegation. (luna tops out at "max".)
#
# The pinned SDK's ReasoningEffort enum stops at "xhigh"; entrypoints call
# codex_sdk_compat.harden_sdk_enums() so both our outbound values and the
# engine's inbound ones parse anyway. See README "Модель и runtime-доступ".
REASONING_EFFORTS = ("low", "medium", "high", "xhigh", "max", "ultra")

REVIEW_SANDBOX = "read_only"
REVIEW_APPROVAL_MODE = "deny_all"
WORKER_SANDBOX = "workspace_write"
WORKER_APPROVAL_MODE = "auto_review"

# Investigator: reads the whole disk; the PROJECT is not writable. cwd = its
# run_dir/out scratch. Empirically-enforced writable set under workspace_write =
# cwd (out) + system temp (/tmp, $TMPDIR); everything else — the project, run_dir
# siblings — is BLOCKED by the sandbox, not merely audited (verified: project
# write BLOCKED, read outside workspace SUCCEEDS). deny_all = no approval
# escalation; in-workspace writes still succeed. Note: this SDK sends a fixed
# per-turn policy for the Sandbox enum, so writable_roots/exclude_slash_tmp via
# config_overrides do NOT take effect — /tmp cannot be excluded here. The
# guarantee we rely on is "project unreachable", not "only out/".
INVESTIGATE_SANDBOX = "workspace_write"
INVESTIGATE_APPROVAL_MODE = "deny_all"

# Bridge threads must NOT persist into the shared ~/.codex session store. That
# store is the runtime owner (auth/config/runtime) shared with Codex Desktop,
# which renders every materialized thread as a chat. The bridge's only
# audit/debug owner is the project-local _workspace/codex-artifacts/<run_id>/.
# Passing ephemeral=True keeps the thread off disk — SDK wire schema: "should
# not be materialized on disk".
BRIDGE_THREAD_EPHEMERAL = True
