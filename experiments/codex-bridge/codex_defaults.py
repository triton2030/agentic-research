"""Shared Codex runtime defaults for bridge entrypoints.

Keep this module SDK-free so dry-run validation stays cheap and does not start
or import the Codex runtime.
"""
from __future__ import annotations

from pathlib import Path

# Ярусы вызова (решение владельца 2026-09-06, дословно: «Луна Макс для
# большого количества тупой работы, сол медиум для средней работы и Astro Medium
# для суперумной работы. Но это как дефолты» —
# _ops/chat-recall/2026-09-06-170311-claude-557afe59.md#L16). Заменяет
# «sol + xhigh на всё» от 2026-08-14. Три дефолта по роду работы, не по входу:
#
#   sol   + medium — ДЕФОЛТ моста: средняя работа. Тред — только по явному --dialog.
#   luna  + max    — большая тупая работа: механика, где нужна пропускная
#                    способность, а не суждение. Владелец: «отличный исполнитель
#                    чёткой воли… но никак не продумыватель систем сложных».
#   astra + medium — суперумная работа: развилка маршрута, архитектура,
#                    стратегия, независимое суждение. gpt-6-astra — «Our most
#                    capable model for complex, demanding work» (каталог движка),
#                    живой пробник 2026-09-06 под ChatGPT-биллингом: completed.
#
# Поколение ярусов — 6: luna и sol переехали с 5.6 на gpt-6-* (владелец
# 2026-09-23: «теперь будем использавть луна 6 и сол 6 и астру» —
# _ops/chat-recall/2026-09-23-051553-claude-483a304e.md#recall-9805fef9e16041928ddf6a675d7d952d).
#
# Каталог не блокируется (там же, #L17): --model и --effort — выбор по ситуации,
# terra, gpt-5.6-*, gpt-5.5, max/ultra и прочее остаются доступны явным флагом.
DEFAULT_CODEX_MODEL = "gpt-6-sol"
DEFAULT_CODEX_EFFORT = "medium"

# Лёгкий ярус для тупой и объёмной работы; выбирается явным --model/--effort.
LIGHT_CODEX_MODEL = "gpt-6-luna"
LIGHT_CODEX_EFFORT = "max"

# Умный ярус для суперумной работы; выбирается явным --model.
SMART_CODEX_MODEL = "gpt-6-astra"
SMART_CODEX_EFFORT = "medium"


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

# The ChatGPT desktop app bundles a current codex binary and auto-updates it,
# so the bridge prefers it and falls back to the SDK bundle only if the app is
# gone. History of why: the old pin (SDK 0.1.0b3 → codex-cli 0.137.0a4) answered
# HTTP 400 "requires a newer version of Codex" on gpt-5.6-sol (verified live
# 2026-07-10). Pins now track 0.144.4, still behind the app engine
# (0.148.0-alpha.9 on 2026-08-14), so the preference stays. On 2026-09-26 the app
# moved the engine to codex-cli/bin/ (0.158.0-alpha.2.1); the old path vanished and
# the SDK-bundle fallback answered gpt-6-sol with HTTP 400 for a ChatGPT account.
CHATGPT_APP_CODEX_BIN = "/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex"


def resolve_codex_bin() -> str | None:
    """Path to the preferred codex binary, or None for the SDK bundle."""
    if Path(CHATGPT_APP_CODEX_BIN).is_file():
        return CHATGPT_APP_CODEX_BIN
    return None


def codex_bin_source(codex_bin: str | None) -> str:
    """Ledger/stderr label for the engine the bridge is about to launch."""
    return "chatgpt-app" if codex_bin else "sdk-bundle"


# The fallback engine is not a silent equivalent: it lags the app engine, and
# old bundles answered newer models with HTTP 400 (verified for gpt-5.6-sol on
# 0.137.0a4; the current default on the current bundle is not probed).
SDK_BUNDLE_WARNING = (
    "[codex-bridge] движок ChatGPT.app не найден по CHATGPT_APP_CODEX_BIN "
    "(приложение могло перенести его: 2026-09-26 он переехал в codex-cli/bin/; "
    "найди `find /Applications/ChatGPT.app -name codex -type f` и поправь "
    "codex_defaults.py) — запуск на бандл-бинаре SDK; "
    f"default-модель {DEFAULT_CODEX_MODEL} на нём может не работать: старые "
    "бинари отвечали на новые модели HTTP 400 'requires a newer version of "
    "Codex' (поставь ChatGPT.app или передай --model, который старый движок "
    "ещё знает)."
)

# Floor is "low": default turn tools (web_search/image_gen) reject lower
# efforts at Codex runtime (HTTP 400), so "none"/"minimal" are cut here to fail
# fast at flag validation.
#
# The upper scale mirrors the engine's own catalogue
# (~/.codex/models_cache.json → supported_reasoning_levels), read 2026-07-27 for
# gpt-5.6-sol/terra and re-read 2026-09-23 for gpt-6-sol/astra/luna — the same
# scale. Its wording is the contract:
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
# Проверяющий с `--scratch` пишет в свою копию проекта (codex_scratch.py):
# тесты и сборки идут делом, исходник недостижим для записи.
REVIEW_SCRATCH_SANDBOX = "workspace_write"
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

# Полный доступ — явный флаг исследователя на один прогон (`--full-access`),
# не дефолт ни одного профиля. Владелец 2026-09-23 выбрал больше пользы от
# Codex ценой меньшей безопасности: «Все три и дать доступ в интеренет, кодекс
# очень умная модель она ничего плохо делать не будет»
# (_ops/chat-recall/2026-09-23-051553-claude-483a304e.md#recall-94036c7a45b24ae2aa0cbdeaa094b974).
# Нужен задачам вне git-проекта: поставить пакет, настроить домашнюю папку.
# Цена: запись вне проекта мост не видит и не откатывает — scope-check
# остаётся наблюдением и успех не роняет.
FULL_ACCESS_SANDBOX = "full_access"

# Bridge threads must NOT persist into the shared ~/.codex session store. That
# store is the runtime owner (auth/config/runtime) shared with Codex Desktop,
# which renders every materialized thread as a chat. The bridge's only
# audit/debug owner is the project-local _workspace/codex-artifacts/<run_id>/.
# Passing ephemeral=True keeps the thread off disk — SDK wire schema: "should
# not be materialized on disk".
BRIDGE_THREAD_EPHEMERAL = True

# Воркеры флота — санкционированное исключение (владелец, 2026-08-14: «при
# большой работе создаваемые треды я видел в кодексе тоже… через приложение
# кодекс могу также видеть прогресс работы самих агентов»). Материализованный
# тред воркера = живой монитор его прогресса в Codex Desktop; audit-владельцем
# прогона остаётся run_dir, thread_id каждого воркера пишется в results.jsonl.
FLEET_THREAD_EPHEMERAL = False
