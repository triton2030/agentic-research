"""Витрина фоновых прогонов Codex: карточка показывает ход, снимок — по запросу.

Два режима:

- `watch` — stdout карточки запуска (`codex_launch.py` ставит `watch --pulse`):
  заголовок с заданием, слова Codex по мере работы и финал прогона.
- `look` — одноразовый снимок по всем живым прогонам, по запросу владельца
  «глянь, над чем они там». Печатает и выходит. `look --json` — те же данные
  плюс недавно закончившиеся прогоны для панели-мода Claude Code
  (`claude-mod/codex-runs/`), которую видит владелец, а не контекст агента.
- `story RUN_DIR` — история одного прогона для той же панели: задание, слова и
  мысли Codex по времени, сбои и итоговый отчёт.

Два свойства, купленные ценой кода, и каждое лечит известный отказ:

1. **Читаем по байтовому offset.** `events.jsonl` строго append-only
   (`codex_run_ledger.append_jsonl`), поэтому прирост даёт каждое событие ровно
   один раз — без дублей и без повторного разбора мегабайтного журнала.
2. **Молчание не считается успехом.** Любой отказ самого наблюдателя —
   пропавший каталог, нечитаемый журнал, потолок по времени — печатается
   строкой. Тихо умереть он не имеет права: тишина здесь означает ровно одно —
   «идёт и не кончилось».

Стандартная библиотека и ничего больше: наблюдатель обязан пережить окружение,
в котором сам мост уже сломан.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Iterator

POLL_SEC = 20
MAX_HOURS = 6
DETAIL_LIMIT = 60

# Шаги хода считаем по границам завершённых item-ов: `item/started` без пары
# посчитал бы незаконченную работу дважды.
STEP_METHOD = "item/completed"
FAILURE_METHODS = frozenset({"error", "turn/failed"})

def _short(text: Any, limit: int = DETAIL_LIMIT) -> str:
    value = " ".join(str(text or "").split())
    return value[:limit] if len(value) <= limit else value[: limit - 1] + "…"


def _dur(seconds: float) -> str:
    seconds = int(max(seconds, 0))
    if seconds < 60:
        return f"{seconds}с"
    if seconds < 3600:
        return f"{seconds // 60}м"
    return f"{seconds // 3600}ч{(seconds % 3600) // 60:02d}м"


def _ts(value: Any) -> float:
    """ISO-8601 с точностью до секунды → epoch. Мусор не роняет наблюдателя."""
    try:
        from datetime import datetime

        return datetime.fromisoformat(str(value)).timestamp()
    except Exception:  # noqa: BLE001
        return 0.0


def emit(line: str) -> None:
    """Одна строка = одна нотификация. Без flush она осядет в буфере пайпа."""
    print(line, flush=True)


class Journal:
    """Приростное чтение append-only журнала по байтовому offset."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.offset = 0

    def new_events(self) -> Iterator[dict[str, Any]]:
        if not self.path.is_file():
            return
        try:
            with self.path.open("rb") as handle:
                handle.seek(self.offset)
                raw_chunk = handle.read()
            # Хвостовая неполная строка: писатель мог не дописать её (или
            # дописать полсимвола UTF-8) в этот момент. Режем по байтам ДО
            # декодирования и оставляем хвост следующему кругу (аудит Astra
            # 2026-09-19: decode всего хвоста падал на разорванном символе).
            cut = raw_chunk.rfind(b"\n")
            if cut == -1:
                return
            body = raw_chunk[: cut + 1].decode("utf-8", errors="replace")
            self.offset += cut + 1
        except OSError as err:
            emit(f"НАБЛЮДЕНИЕ СЛОМАНО: журнал не читается — {err}")
            return
        for raw in body.splitlines():
            try:
                yield json.loads(raw)
            except Exception:  # noqa: BLE001
                continue


def _failure_text(detail: str) -> str:
    """Сбой движка словами для человека; сырой текст — только если не узнали."""
    if "stream disconnected" in detail:
        return "обрыв связи с сервером — движок переподключается сам"
    return _short(detail, 200)


class Run:
    """Состояние одного прогона, собранное только из его журнала."""

    # Шаги, которые видны владельцу как «ход работы»; reasoning и userMessage —
    # шум для ленты (первый молчит минутами, второй — сам запрос).
    PULSE_KINDS = frozenset({
        "commandExecution", "fileChange", "mcpToolCall", "dynamicToolCall",
        "webSearch", "agentMessage", "reasoning", "subAgentActivity", "imageGeneration",
    })
    WORD_KINDS = frozenset({"agentMessage", "reasoning"})

    READ_CMDS = frozenset({
        "cat", "sed", "nl", "rg", "grep", "ls", "head", "tail", "wc", "find", "fd",
        "git", "less", "stat", "file", "tree", "python3 -c", "jq", "diff",
    })

    @staticmethod
    def _bare_command(text: str) -> str:
        """Снять обёртку движка `/bin/zsh -lc '…'` и внешние кавычки."""
        cmd = text.strip()
        for prefix in ("/bin/zsh -lc ", "/bin/bash -lc ", "bash -lc ", "zsh -lc ", "sh -c "):
            if cmd.startswith(prefix):
                cmd = cmd[len(prefix):].strip()
                break
        # Ledger режет команду до 200 символов, закрывающей кавычки может не быть.
        if cmd and cmd[0] in "'\"":
            quote = cmd[0]
            cmd = cmd[1:]
            if cmd.endswith(quote):
                cmd = cmd[:-1]
        return " ".join(cmd.split())

    def pulse_line(self, kind: str, detail: str) -> str | None:
        """Одна строка витрины: время от старта, значок шага, суть без обёрток."""
        span = _dur(self.last_ts - self.run_start) if self.run_start and self.last_ts else "?"
        if self.words_only and kind not in self.WORD_KINDS:
            return None
        if kind == "reasoning":
            text = detail.split(": ", 1)[1] if ": " in detail else ""
            if not text:
                return None  # старый журнал без текста сводки или пустая сводка
            icon, body = "…", _short(text, 360)
            return f"{span:>5} {icon} {body}".rstrip()
        if kind == "commandExecution":
            cmd = self._bare_command(detail)
            first = cmd.split(" ", 1)[0] if cmd else ""
            icon = "📖" if first in self.READ_CMDS else "⌘"
            body = _short(cmd, 110)
        elif kind == "fileChange":
            names = [Path(x.strip()).name for x in detail.split(",") if x.strip()]
            icon, body = "✎", _short(", ".join(names), 110)
        elif kind == "agentMessage":
            text = detail.split(": ", 1)[1] if ": " in detail else detail
            icon, body = "💬", _short(text, 360)
        elif kind == "mcpToolCall" or kind == "dynamicToolCall":
            icon, body = "🔧", _short(detail, 110)
        elif kind == "webSearch":
            icon, body = "🌐", _short(detail, 110)
        elif kind == "subAgentActivity":
            icon, body = "🤖", _short(detail, 110)
        elif kind == "imageGeneration":
            icon, body = "🖼", _short(detail, 110)
        else:
            return None
        if self.words_only:
            return f"{span:>5} {body}".rstrip()
        return f"{span:>5} {icon} {body}".rstrip()

    def task(self) -> str:
        """Первая содержательная строка задания из prompt.md."""
        prompt = self.dir / "prompt.md"
        if not prompt.is_file():
            return ""
        try:
            lines = [ln.strip() for ln in prompt.read_text(encoding="utf-8").splitlines()]
        except OSError:
            return ""
        # Мост кладёт преамбулу роли, потом «===== ЗАДАНИЕ =====»: показываем задание.
        start = 0
        for i, ln in enumerate(lines):
            if "ЗАДАНИЕ" in ln and ln.startswith("="):
                start = i + 1
                break
        return next((ln for ln in lines[start:] if ln and not ln.startswith(("#", "="))), "")

    def task_text(self, limit: int = 3000) -> str:
        """Всё задание из prompt.md — после строки «===== ЗАДАНИЕ =====»."""
        prompt = self.dir / "prompt.md"
        if not prompt.is_file():
            return ""
        try:
            text = prompt.read_text(encoding="utf-8")
        except OSError:
            return ""
        marker = text.find("ЗАДАНИЕ")
        if marker != -1:
            text = text[text.find("\n", marker) + 1:]
        text = text.strip()
        return text if len(text) <= limit else text[:limit].rstrip() + "…"

    def tier(self) -> str:
        """`модель/усилие` из manifest.json; пусто, если манифест молчит."""
        manifest = self.dir / "manifest.json"
        if not manifest.is_file():
            return ""
        try:
            m = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return ""
        codex = m.get("codex") if isinstance(m.get("codex"), dict) else m
        model, effort = codex.get("model"), codex.get("effort")
        if not model:
            return ""
        return f"{model}" + (f"/{effort}" if effort else "")

    def header_line(self) -> str:
        """Первая строка витрины: чем занят прогон, по prompt.md."""
        task, tier = self.task(), self.tier()
        return (f"▶ {self.dir.name}" + (f" · {tier}" if tier else "")
                + (f" · {_short(task, 100)}" if task else ""))

    def __init__(self, run_dir: Path, pulse: bool = False, words_only: bool = True) -> None:
        self.dir = run_dir
        self.pulse = pulse
        # Владелец 2026-09-18: «мне нравится что я вижу его мысли, но можно не
        # показывать всякие команды, ссылки, код — чисто его текстовые слова».
        self.words_only = words_only
        self.journal = Journal(run_dir / "events.jsonl")
        self.steps = 0
        self.last_seen = 0.0
        self.last_kind = "?"
        self.run_start = 0.0
        self.last_ts = 0.0
        self.finished = False
        self.last_words = ""
        # История для панели: слова и мысли Codex и сбои, со временем от старта.
        self.story: list[dict[str, Any]] = []

    def absorb(self, event: dict[str, Any]) -> Iterator[str]:
        """Событие журнала → ноль или одна строка витрины."""
        kind = event.get("event")
        stamp = _ts(event.get("ts"))
        if stamp:
            self.last_ts = stamp
            if not self.run_start:
                self.run_start = stamp

        if kind == "codex":
            if stamp:
                self.last_seen = stamp
            if event.get("kind"):
                self.last_kind = str(event["kind"])
            if event.get("method") == STEP_METHOD:
                self.steps += 1
                if event.get("kind") in self.WORD_KINDS:
                    detail = str(event.get("detail") or "")
                    words = detail.split(": ", 1)[1] if ": " in detail else ""
                    if words:
                        self.last_words = words
                        self.story.append({
                            "t": round(stamp - self.run_start) if stamp else None,
                            "kind": "thought" if event.get("kind") == "reasoning" else "words",
                            "text": words,
                        })
                if self.pulse and event.get("kind") in self.PULSE_KINDS:
                    line = self.pulse_line(
                        str(event["kind"]), str(event.get("detail") or ""),
                    )
                    if line:
                        yield line
            elif event.get("method") in FAILURE_METHODS:
                detail = str(event.get("detail") or event["method"])
                self.story.append({
                    "t": round(stamp - self.run_start) if stamp else None,
                    "kind": "fail",
                    "text": _failure_text(detail),
                })
                yield f"СБОЙ {_short(detail)}"
            return
        if kind == "done":
            self.finished = True

    def closing_lines(self) -> Iterator[str]:
        """Прогон кончился — договорить то, чего журнал не сказал сам."""
        result = self.dir / "result.json"
        if not result.is_file():
            yield f"КОНЕЦ {self.dir.name} · без result.json"
            return
        try:
            data = json.loads(result.read_text(encoding="utf-8"))
        except Exception as err:  # noqa: BLE001
            yield f"КОНЕЦ {self.dir.name} · result.json нечитаем — {err}"
            return
        state = "OK" if data.get("ok") else "ПРОВАЛ"
        span = _dur(self.last_ts - self.run_start) if self.run_start else "?"
        yield f"{state} {self.dir.name} · {span} · {self.steps}ш"


WAIT_SEC = 180


def _result_is_final(run_dir: Path) -> bool:
    """`result.json` считается финалом, только если он не provisional: обработчик
    сигнала пишет provisional-запись ДО interrupt, и витрина уходила раньше
    подтверждённого конца (аудит Astra 2026-09-19)."""
    path = run_dir / "result.json"
    if not path.is_file():
        return False
    try:
        return not json.loads(path.read_text(encoding="utf-8")).get("provisional")
    except (OSError, ValueError):
        return True  # нечитаемый файл — закрывающие строки сами это скажут


def _pid_alive(pid: int | None) -> bool:
    if not pid:
        return True
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def watch(
    run_dir: Path, poll: int, max_hours: float, wait_sec: int = WAIT_SEC,
    pulse: bool = False, words_only: bool = True, pid: int | None = None,
) -> int:
    # Monitor ставится в момент запуска прогона, на заранее выбранный
    # `--run-dir`, — каталог появится, когда мост создаст его. Ждём ограниченно:
    # прогон, не стартовавший за wait_sec, — отказ запуска, а не тишина.
    waited = 0
    while not run_dir.is_dir():
        if waited >= wait_sec:
            emit(f"НАБЛЮДЕНИЕ НЕ ВСТАЛО: каталог {run_dir} не появился за {wait_sec}с")
            return 2
        time.sleep(min(2, max(0, wait_sec - waited)) or 1)
        waited += 2
    if waited:
        emit(f"НАБЛЮДЕНИЕ ВСТАЛО: {run_dir.name} появился через ~{waited}с")
    if pulse:
        time.sleep(1)  # prompt.md пишется сразу после создания каталога
        emit(Run(run_dir).header_line())

    run = Run(run_dir, pulse=pulse, words_only=words_only)
    deadline = time.time() + max_hours * 3600
    while True:
        for event in run.journal.new_events():
            for line in run.absorb(event):
                emit(line)

        backend_gone = not _pid_alive(pid)
        if run.finished or _result_is_final(run_dir) or backend_gone:
            # Ещё круг чтения: `done` и `result.json` могли обогнать хвост журнала.
            if backend_gone and not (run.finished or _result_is_final(run_dir)):
                emit(f"ПРОЦЕСС ПРОГОНА ЗАВЕРШИЛСЯ без result.json — {run_dir.name}")
            time.sleep(1)
            for event in run.journal.new_events():
                for line in run.absorb(event):
                    emit(line)
            for line in run.closing_lines():
                emit(line)
            return 0

        if time.time() > deadline:
            emit(f"НАБЛЮДЕНИЕ ВЫШЛО ПО ПОТОЛКУ: {run_dir.name} · {max_hours}ч")
            return 0
        time.sleep(poll)


def look(project: Path, limit: int = 12) -> int:
    """Снимок по запросу: над чем сейчас работает каждый живой агент."""
    root = project / "_workspace" / "work-artifacts"
    if not root.is_dir():
        emit(f"прогонов нет: {root} не существует")
        return 0

    now = time.time()
    shown = 0
    runs = sorted(
        (p for p in root.glob("*/agents/codex-artifacts/*") if p.is_dir()),
        key=lambda p: (p.name, str(p)), reverse=True,
    )
    for run_dir in runs:
        # Каталог артефактов копит и чужие папки. Прогон опознаём по манифесту:
        # ledger пишет его первым, поэтому он есть даже у прогона без единого
        # события. Без этого фильтра мусорная папка выглядит вечно живой.
        if not (run_dir / "manifest.json").is_file():
            continue
        if (run_dir / "result.json").is_file():
            continue
        run = Run(run_dir)
        for event in run.journal.new_events():
            list(run.absorb(event))

        span = _dur(now - run.run_start) if run.run_start else "?"
        emit(f"{run_dir.name} · идёт {span}")
        quiet = _dur(now - run.last_seen) if run.last_seen else "?"
        emit(f"  одиночный · {run.steps}ш · тихо {quiet} · {run.last_kind}")
        shown += 1
        if shown >= limit:
            break

    if not shown:
        emit(f"живых прогонов нет: {root}")
    return 0


RECENT_MIN = 30
# Живой прогон пишет heartbeat раз в `runtime.heartbeat_sec`; три пропуска
# подряд — процесс, скорее всего, умер без result.json.
LOST_HEARTBEATS = 3


def _run_state(run_dir: Path, run: Run, final: bool, now: float) -> str:
    """live · lost (нет событий дольше трёх heartbeat) · ok · failed."""
    if final:
        try:
            ok = bool(json.loads((run_dir / "result.json").read_text(encoding="utf-8")).get("ok"))
        except (OSError, ValueError):
            ok = False
        return "ok" if ok else "failed"
    try:
        runtime = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8")).get("runtime") or {}
        beat = float(runtime.get("heartbeat_sec") or 0)
    except (OSError, ValueError, AttributeError):
        beat = 0.0
    silent = now - run.last_ts if run.last_ts else 0.0
    return "lost" if beat and silent > LOST_HEARTBEATS * beat else "live"


STORY_LIMIT = 300
FINAL_LIMIT = 6000
_MD_LINK = re.compile(r"\]\(\s*<?([^)>]+?)>?\s*\)")


def _linked_report(run_dir: Path, answer: str) -> str:
    """Текст отчёта, на который ссылается final.md, если он внутри прогона:
    проверяющие и советники кладут ответ в `out/`, а в final.md — только ссылку."""
    root = run_dir.resolve()
    for target in _MD_LINK.findall(answer):
        path = Path(target.split("#", 1)[0].strip()).expanduser()
        if not path.is_absolute():
            path = run_dir / path
        try:
            path = path.resolve()
        except OSError:
            continue
        if root in path.parents and path.is_file() and path.suffix in {".md", ".txt"}:
            try:
                text = path.read_text(encoding="utf-8").strip()
            except OSError:
                continue
            return text if len(text) <= FINAL_LIMIT else text[:FINAL_LIMIT].rstrip() + "…"
    return ""


def story_json(run_dir: Path, limit: int = STORY_LIMIT) -> dict[str, Any]:
    """История одного прогона для панели: задание, слова и мысли Codex по
    времени, сбои и итоговый ответ. Только то, что уже лежит в `run_dir`."""
    run = Run(run_dir)
    for event in run.journal.new_events():
        list(run.absorb(event))
    now = time.time()
    final = _result_is_final(run_dir)
    answer = ""
    if (run_dir / "final.md").is_file():
        try:
            answer = (run_dir / "final.md").read_text(encoding="utf-8").strip()
        except OSError:
            answer = ""
        if len(answer) > FINAL_LIMIT:
            answer = answer[:FINAL_LIMIT].rstrip() + "…"
    end = run.last_ts if final else now
    return {
        "name": run_dir.name,
        "run_dir": str(run_dir),
        "tier": run.tier(),
        "task": run.task_text(),
        "report": _linked_report(run_dir, answer),
        "state": _run_state(run_dir, run, final, now) if (run_dir / "manifest.json").is_file() else "lost",
        "started": run.run_start,
        "elapsed_s": round(end - run.run_start) if run.run_start else None,
        "steps": run.steps,
        "items": run.story[-limit:],
        "dropped": max(0, len(run.story) - limit),
        "final": answer,
    }


def look_json(project: Path, recent_min: int = RECENT_MIN, names: frozenset[str] = frozenset()) -> dict[str, Any]:
    """Данные для панели-мода: живые прогоны, закончившиеся за `recent_min` и
    закончившиеся прогоны из `names` — запущенные этой сессией Claude — за любое
    время.

    Панель рисует это владельцу и в контекст Claude не попадает, поэтому здесь
    нет решения «будить ли агента»: только факты журнала, манифеста и result.json.
    """
    root = project / "_workspace" / "work-artifacts"
    out: dict[str, Any] = {"project": str(project), "now": time.time(), "runs": []}
    if not root.is_dir():
        return out
    now = time.time()
    for run_dir in root.glob("*/agents/codex-artifacts/*"):
        manifest = run_dir / "manifest.json"
        if not run_dir.is_dir() or not manifest.is_file():
            continue
        final = _result_is_final(run_dir)
        result_path = run_dir / "result.json"
        if final and run_dir.name not in names and now - result_path.stat().st_mtime > recent_min * 60:
            continue
        run = Run(run_dir)
        for event in run.journal.new_events():
            list(run.absorb(event))
        state = _run_state(run_dir, run, final, now)
        end = run.last_ts if final else now
        out["runs"].append({
            "name": run_dir.name,
            "run_dir": str(run_dir),
            "work": run_dir.parents[2].name,
            "tier": run.tier(),
            "task": _short(run.task(), 160),
            "state": state,
            "started": run.run_start,
            "elapsed_s": round(end - run.run_start) if run.run_start else None,
            "quiet_s": round(now - run.last_seen) if run.last_seen and not final else None,
            "steps": run.steps,
            "last_words": _short(run.last_words, 240),
        })
    out["runs"].sort(key=lambda r: (r["state"] not in ("live", "lost"), -(r["started"] or 0)))
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Витрина Codex-прогонов: watch — поток завершений для Monitor,"
        " look — снимок живых агентов по запросу."
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    watcher = sub.add_parser("watch", help="поток строк о завершении агентов")
    watcher.add_argument("run_dir")
    watcher.add_argument("--poll", type=int, default=POLL_SEC)
    watcher.add_argument("--max-hours", type=float, default=MAX_HOURS)
    watcher.add_argument(
        "--pulse", action="store_true",
        help="ход прогона в карточке: слова Codex по мере работы (его сообщения), "
        "без команд, путей и кода; без флага — только завершения",
    )
    watcher.add_argument(
        "--pulse-all", action="store_true",
        help="с --pulse: показывать и команды, файлы, инструменты (для отладки моста)",
    )
    watcher.add_argument(
        "--pid", type=int, help="pid процесса прогона: его смерть без result.json закрывает витрину",
    )
    watcher.add_argument(
        "--wait-sec", type=int, default=WAIT_SEC,
        help="сколько ждать появления run_dir, если Monitor поставлен раньше прогона",
    )

    snapshot = sub.add_parser("look", help="снимок живых агентов и их шагов")
    snapshot.add_argument("project", nargs="?", default=".")
    snapshot.add_argument(
        "--json", action="store_true",
        help="данные для панели-мода Claude Code: живые и недавно закончившиеся прогоны",
    )
    snapshot.add_argument(
        "--recent-min", type=int, default=RECENT_MIN,
        help="с --json: сколько минут показывать закончившийся прогон",
    )
    snapshot.add_argument(
        "--names", default="",
        help="с --json: имена каталогов прогонов через запятую — их отдавать за любое время",
    )

    story = sub.add_parser("story", help="история одного прогона для панели-мода (JSON)")
    story.add_argument("run_dir")

    args = parser.parse_args(argv)
    if args.mode == "story":
        print(json.dumps(story_json(Path(args.run_dir).expanduser().resolve()), ensure_ascii=False))
        return 0
    if args.mode == "watch":
        return watch(
            Path(args.run_dir), args.poll, args.max_hours, args.wait_sec,
            args.pulse or args.pulse_all, words_only=not args.pulse_all, pid=args.pid,
        )
    if args.json:
        names = frozenset(n for n in args.names.split(",") if n)
        print(json.dumps(look_json(Path(args.project).resolve(), args.recent_min, names), ensure_ascii=False))
        return 0
    return look(Path(args.project))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        emit("НАБЛЮДЕНИЕ ПРЕРВАНО вручную")
        sys.exit(130)
    except Exception as err:  # noqa: BLE001
        # Наблюдатель, упавший молча, неотличим от наблюдателя, которому нечего
        # сказать. Стек уходит в stderr, а Monitor stderr не показывает вовсе.
        emit(f"НАБЛЮДЕНИЕ УПАЛО: {type(err).__name__}: {err}")
        sys.exit(1)
