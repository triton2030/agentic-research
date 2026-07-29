"""Ретрай стартовых вызовов Codex под transient-перегрузкой движка.

SDK возит готовый `retry_on_overload` (`openai_codex/retry.py`) и предикат
`is_retryable_error`, но сам применяет их только внутри низкоуровневого
клиента: у моста ретраев не было вовсе, и один `server_overloaded` на старте
терял весь оплаченный ход.

Граница намеренная: **ретраится только СТАРТ** — `thread_start`,
`thread_resume` и `thread.turn` (это ещё RPC старта хода). Потребление потока
нотификаций НЕ ретраится: повтор после того, как ход пошёл, означал бы второй
оплаченный turn.

Каждая повторная попытка пишется в ledger событием `retry`: молчаливый ретрай
прятал бы нестабильность движка ровно там, где её надо видеть.
"""
from __future__ import annotations

import asyncio
import random
from typing import Any, Awaitable, Callable, TypeVar

from codex_run_ledger import append_event

T = TypeVar("T")

# Дефолты sync-хелпера SDK (openai_codex/retry.py); async-зеркало держит те же.
MAX_START_ATTEMPTS = 3
INITIAL_DELAY_S = 0.25
MAX_DELAY_S = 2.0
JITTER_RATIO = 0.2


# Хелперы грузятся по одному и лениво: sync-путь берёт у SDK весь цикл
# повторов, async-путь — только предикат, и отсутствие одного не должно молча
# отключать другой. Импорт после scrub_billing_env, как везде в мосте.
def _load_retry_on_overload() -> Callable[..., Any] | None:
    try:
        from openai_codex import retry_on_overload  # noqa: PLC0415
    except ImportError:
        return None
    return retry_on_overload


def _load_is_retryable() -> Callable[[BaseException], bool] | None:
    try:
        from openai_codex import is_retryable_error  # noqa: PLC0415
    except ImportError:
        return None
    return is_retryable_error


def _log_retry(
    run_dir: Any | None,
    operation: str,
    attempt: int,
    exc: BaseException,
    fields: dict[str, Any] | None,
) -> None:
    if run_dir is None:
        return
    append_event(
        run_dir,
        "retry",
        operation=operation,
        attempt=attempt,
        error=str(exc),
        **(fields or {}),
    )


def retry_start(
    op: Callable[[], T],
    *,
    run_dir: Any | None,
    operation: str,
    max_attempts: int = MAX_START_ATTEMPTS,
    fields: dict[str, Any] | None = None,
) -> T:
    """Синхронный стартовый вызов с ретраем на overload-ошибках."""
    retry_on_overload = _load_retry_on_overload()
    is_retryable_error = _load_is_retryable()
    if retry_on_overload is None or is_retryable_error is None:
        return op()

    attempt = 0

    def attempt_once() -> T:
        nonlocal attempt
        attempt += 1
        try:
            return op()
        except Exception as exc:
            # Условие повторяет решение retry_on_overload: событие пишем только
            # когда повтор реально будет, а не на финальном провале.
            if attempt < max_attempts and is_retryable_error(exc):
                _log_retry(run_dir, operation, attempt, exc, fields)
            raise

    return retry_on_overload(attempt_once, max_attempts=max_attempts)


async def retry_start_async(
    op: Callable[[], Awaitable[T]],
    *,
    run_dir: Any | None,
    operation: str,
    max_attempts: int = MAX_START_ATTEMPTS,
    fields: dict[str, Any] | None = None,
) -> T:
    """Async-зеркало `retry_start` для флота.

    Готового async-хелпера SDK не даёт, поэтому backoff здесь повторяет
    `openai_codex/retry.py` теми же дефолтами; общий с ним только предикат
    `is_retryable_error`. Флот стартует N тредов разом и упирается в overload
    раньше одиночных входов — цена дубля backoff-а меньше, чем цена потерянных
    воркеров.
    """
    is_retryable_error = _load_is_retryable()
    if is_retryable_error is None:
        return await op()

    delay = INITIAL_DELAY_S
    attempt = 0
    while True:
        attempt += 1
        try:
            return await op()
        except Exception as exc:
            if attempt >= max_attempts or not is_retryable_error(exc):
                raise
            _log_retry(run_dir, operation, attempt, exc, fields)
            jitter = delay * JITTER_RATIO
            sleep_for = min(MAX_DELAY_S, delay) + random.uniform(-jitter, jitter)
            if sleep_for > 0:
                await asyncio.sleep(sleep_for)
            delay = min(MAX_DELAY_S, delay * 2)
