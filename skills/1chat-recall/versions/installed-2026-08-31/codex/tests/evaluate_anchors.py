#!/usr/bin/env python3
"""Приёмка retrieval по якорям: знаменатель берётся вне корпуса.

Прежний порог считался на кейсах, отобранных из самого корпуса, и потому не мог
провалиться по причине покрытия. Здесь набор строится из долговечных документов
репозитория, которые ссылаются на адрес цитаты как на своё основание: принципы,
origin-файлы скилов, хендофы, планы. У такого якоря присутствие записи в корпусе
доказано ссылкой, а формулировка запроса берётся из прозы самого документа —
то есть из слов будущего читателя, а не из слов владельца.

Проверяемое утверждение узкое: если долговечный документ обосновал себя цитатой,
штатный поиск обязан вернуть тот же holder на вопрос, заданный языком этого
документа. Что владелец никогда не говорил, здесь не проверяется — retrieval за
это не отвечает.

Единица продукта — **сессия целиком**, а не цитата: агент восстанавливает
историю по цепочке реплик одного разговора, поэтому приёмочное число здесь
одно — `found@10`, попал ли нужный holder в карту. `found@5` считается только
как справка о позиции в ранге; выдача показывается newest-first, десятка по
контракту — карта, а не очередь, и глубину чтения агент выбирает по смыслу.
Порогом `found@5` не является.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).parents[1] / "scripts" / "chat_digest.py"
CITATION = re.compile(
    r"`?_ops/chat-recall/(?P<file>\d{4}-\d{2}-\d{2}-\d{6}-[a-z]+-[a-z0-9]+\.md)"
    r"(?::[\d,\-]+)?`?"
)
SKIP_DIRS = {"_ops/chat-recall", "_workspace", "node_modules", ".venv", ".git"}
# Жанр источника: цитата приводится как основание утверждения, а не как опись.
# Хендофы и планы ссылаются на адреса инвентарём — там перед ссылкой стоит
# состояние файла, а не вопрос, который стал бы задавать читатель.
CLAIM_GENRES = ("principles", "origin.md", "product-frame", "evidence.md", "cut.md")
JUNK = re.compile(r"(?:^|\s)(?:--?[a-z-]{2,}|[~./][\w./-]{6,}|\d{2}:\d{2})")
NOISE = re.compile(r"(Источник|Цитаты|Основание[а-я ]*|Бриф и выборы)\s*:?\s*$", re.IGNORECASE)
# Служебные метки принципов: перед ссылкой часто стоит не проза, а метаданные.
LABEL = re.compile(
    r"^(Источник|Commitment|Статус|Текущий статус|Влияет на|Снимает|"
    r"Пересмотреть[а-я, ]*|Утверждение текста)\b.*", re.IGNORECASE | re.DOTALL
)
HEADING = re.compile(r"^#{2,4}\s+(.+)$", re.MULTILINE)
MARKUP = re.compile(r"[`*\[\]]|\((?:https?|/)[^)]*\)")


def _claim_before(text: str, start: int, *, budget: int = 260) -> str:
    """Проза документа перед ссылкой — тот вопрос, каким его задаст читатель.

    Абзац прямо над ссылкой часто оказывается служебной меткой принципа
    (`Источник`, `Commitment`). Тогда берётся ближайший заголовок раздела плюс
    первый содержательный абзац под ним: именно они формулируют утверждение.
    """
    head = text[max(0, start - 2500):start]
    blocks = [
        " ".join(MARKUP.sub(" ", raw).split())
        for raw in re.split(r"\n\s*\n", head)
    ]
    prose = [
        NOISE.sub("", block).strip(" :;,—-")
        for block in blocks
        if block and not LABEL.match(block)
    ]
    prose = [block for block in prose if len(block) >= 40]
    headings = HEADING.findall(head)
    parts: list[str] = []
    if headings:
        parts.append(re.sub(r"^[A-ZА-Я]-\d+\s*[·.]\s*", "", headings[-1]).strip())
    if prose:
        parts.append(prose[-1])
    claim = " — ".join(parts).strip(" :;,—-")
    if len(claim) > budget:
        claim = claim[:budget]
        claim = claim[: claim.rfind(" ")]
    return claim


def collect_anchors(root: Path) -> list[dict[str, Any]]:
    anchors: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        if any(rel.startswith(skip) or f"/{skip}/" in f"/{rel}" for skip in SKIP_DIRS):
            continue
        if not any(genre in rel for genre in CLAIM_GENRES):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for match in CITATION.finditer(text):
            claim = _claim_before(text, match.start())
            if len(claim) < 40:
                continue
            if "_ops/chat-recall/" in claim or "chat-recall/2026" in claim:
                # Перед ссылкой стоит другая ссылка: это перечень адресов,
                # а не утверждение, которое читатель стал бы искать.
                continue
            if JUNK.search(claim):
                # Путь, флаг команды или время в тексте: это строка состояния,
                # а не утверждение о позиции владельца.
                continue
            key = (match.group("file"), claim[:80])
            if key in seen:
                continue
            seen.add(key)
            anchors.append({"source": rel, "holder": match.group("file"), "claim": claim})
    return anchors


def _search(corpus: Path, query: str) -> dict[str, Any]:
    result = subprocess.run(
        [
            "uv", "run", "--offline", "--locked", "--script", str(SCRIPT),
            str(corpus), "--query", query, "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return {"error": result.stderr[-200:]}
    return json.loads(result.stdout)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="корень репозитория")
    parser.add_argument("--corpus", type=Path, default=None)
    parser.add_argument("--min-found", type=float, default=None)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    corpus = args.corpus or (args.root / "_ops" / "chat-recall")

    anchors = collect_anchors(args.root)
    if args.limit:
        anchors = anchors[: args.limit]
    if not anchors:
        print(json.dumps({"error": "якорей не найдено"}, ensure_ascii=False))
        return 2

    hit10 = hit5 = 0
    misses: list[dict[str, Any]] = []
    orphans: list[dict[str, Any]] = []
    for anchor in anchors:
        if not (corpus / anchor["holder"]).exists():
            orphans.append(anchor)
            continue
        payload = _search(corpus, anchor["claim"])
        if "error" in payload:
            misses.append({**anchor, "reason": payload["error"]})
            continue
        files = [holder["file"] for holder in payload.get("holders") or []]
        if anchor["holder"] in files:
            rank = files.index(anchor["holder"]) + 1
            hit10 += 1
            if rank <= 5:
                hit5 += 1
        else:
            misses.append(
                {
                    "source": anchor["source"],
                    "holder": anchor["holder"],
                    "claim": anchor["claim"][:110],
                    "query_domain": payload.get("query_domain"),
                }
            )

    scored = len(anchors) - len(orphans)
    report = {
        "anchors": len(anchors),
        "sources": len({anchor["source"] for anchor in anchors}),
        "orphan_holders": [
            {"source": item["source"], "holder": item["holder"]} for item in orphans
        ],
        "scored": scored,
        "found_at_10": round(hit10 / scored, 3) if scored else 0.0,
        "found_at_5_rank_only": round(hit5 / scored, 3) if scored else 0.0,
        "misses": misses,
    }
    if args.min_found is not None:
        report["threshold"] = {"min_found_at_10": args.min_found}
        report["passed"] = report["found_at_10"] >= args.min_found
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("passed", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
