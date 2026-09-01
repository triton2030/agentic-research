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

Вторая восстановимая причина отказа старта — АРХИВНЫЙ тред: мост сам архивирует
треды воркеров на закрытии волны (`archive_orphaned_threads`), симметричного
подъёма перед `thread_resume` не было, и штатный ремонтный круг умирал
`session ... is archived` до начала работы. `resume_thread[_async]` поднимает
тред и повторяет старт один раз.
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


# -32600 = InvalidRequestError: движок отверг СОСТОЯНИЕ запроса, а не его форму.
# Сегодня архивный тред приходит именно так ("session ... is archived"), но текст
# движка не контракт, поэтому предикат широкий: код ИЛИ подстрока. Цена ложного
# срабатывания — один лишний `thread_unarchive` на уже провалившемся старте
# (например, тред открыт в Codex Desktop: тот же -32600 про занятую запись).
# Цена пропуска — потерянная задача ремонтного круга.
ARCHIVED_RPC_CODE = -32600


def is_archived_error(exc: BaseException) -> bool:
    """True, если старт отвергнут из-за архивного треда (или похоже на это)."""
    if "archiv" in str(exc).lower():
        return True
    return getattr(exc, "code", None) == ARCHIVED_RPC_CODE


def resume_thread(
    codex: Any,
    thread_id: str,
    op: Callable[[], T],
    *,
    run_dir: Any | None,
    fields: dict[str, Any] | None = None,
    max_attempts: int = MAX_START_ATTEMPTS,
) -> tuple[T, bool]:
    """`thread_resume` c подъёмом архивного треда. Возвращает (тред, поднимали ли).

    Флаг нужен вызывающему: у ревьюера доска моста знает свои треды поимённо и
    без события `unarchive` продолжит звать поднятый тред архивным.
    """
    def start() -> T:
        return retry_start(
            op, run_dir=run_dir, operation="thread_resume",
            max_attempts=max_attempts, fields=fields,
        )

    try:
        return start(), False
    except Exception as exc:
        if not is_archived_error(exc):
            raise
        try:
            codex.thread_unarchive(thread_id)
        except Exception as unarchive_exc:
            _log_unarchive_failed(run_dir, thread_id, unarchive_exc, fields)
            # Наружу идёт ошибка resume, а не подъёма: воркер умер на ней.
            raise exc from unarchive_exc
        _log_unarchived(run_dir, thread_id, exc, fields)
        return start(), True


async def resume_thread_async(
    codex: Any,
    thread_id: str,
    op: Callable[[], Awaitable[T]],
    *,
    run_dir: Any | None,
    fields: dict[str, Any] | None = None,
    max_attempts: int = MAX_START_ATTEMPTS,
) -> tuple[T, bool]:
    """Async-зеркало `resume_thread` для флота."""
    async def start() -> T:
        return await retry_start_async(
            op, run_dir=run_dir, operation="thread_resume",
            max_attempts=max_attempts, fields=fields,
        )

    try:
        return await start(), False
    except Exception as exc:
        if not is_archived_error(exc):
            raise
        try:
            await codex.thread_unarchive(thread_id)
        except Exception as unarchive_exc:
            _log_unarchive_failed(run_dir, thread_id, unarchive_exc, fields)
            raise exc from unarchive_exc
        _log_unarchived(run_dir, thread_id, exc, fields)
        return await start(), True


def _log_unarchived(
    run_dir: Any | None, thread_id: str, exc: BaseException,
    fields: dict[str, Any] | None,
) -> None:
    if run_dir is None:
        return
    append_event(
        run_dir, "thread_unarchived",
        thread_id=thread_id, after=str(exc), **(fields or {}),
    )


def _log_unarchive_failed(
    run_dir: Any | None, thread_id: str, exc: BaseException,
    fields: dict[str, Any] | None,
) -> None:
    if run_dir is None:
        return
    append_event(
        run_dir, "thread_unarchive_failed",
        thread_id=thread_id, error=str(exc), **(fields or {}),
    )
