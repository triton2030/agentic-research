#!/usr/bin/env python3
"""Готовность волны и язык её ответов — один предикат на всех потребителей.

Два бортика, оба куплены ошибками 2026-08-24:

1. **Готовность — предикат, а не файловая система.** Пустая квитанция прогона
   весит те же ~1769 байт, что и короткий честный ответ, поэтому `ls | wc -l`
   и `wc -c` врут одинаково правдоподобно. За одну сессию счёт собранных тем
   был объявлен владельцу неверно дважды.
2. **Язык вывода обязан совпадать с языком материала.** Тема `html-artifacts`
   пришла целиком по-английски при русском корпусе, прошла приёмку по `ok` и
   якорям и была поймана случайно. Гейт сравнивает долю кириллицы в ответе с
   долей в его же материале: порог не абсолютный, потому что корпус может быть
   любым, а вот расхождение с собственным материалом — всегда дефект.

    python3 wave_ready.py <папка заданий> <папка ответов> [<ещё папка>...]

Папок ответов может быть несколько, и это не удобство: принятое переносится в
`good/`, а `runs/` — проходящая, её файл затирается следующей попыткой той же
темы. Счёт по одной папке занижает результат ровно так же уверенно, как счёт
по размеру файла его завышал.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wave import strip_fence

CYR = re.compile(r"[а-яА-ЯёЁ]")
LAT = re.compile(r"[A-Za-z]")
SHORT = re.compile(r"L(\d+)")
FULL = re.compile(r"([0-9]{4}-[0-9]{2}-[0-9]{2}-[^\s#\],)]+\.md)#L(\d+)")
ACCOUNTING_RE = re.compile(
    r"\n<!-- TOPIC_ANCHOR_ACCOUNTING\n(?P<data>\{.*?\})\n-->\s*$",
    re.S,
)
TOMBSTONE_HEADING = re.compile(
    r"^[ \t]{0,3}#{1,6}[ \t]+отменено(?:[ \t]+#+)?[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)

MIN_RESPONSE = 500
LANGUAGE_FLOOR = 0.5

_material: dict[str, str] = {}


def material_gap(flat: str, names: list[str]) -> str | None:
    missing = [
        name for name in names if not os.path.isfile(os.path.join(flat, name))
    ]
    if missing:
        return f"входной материал отсутствует: {', '.join(missing)}"
    return None


def read_flat(flat: str, name: str) -> str:
    path = os.path.join(flat, name)
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    if path not in _material:
        _material[path] = open(path, encoding="utf-8").read()
    return _material[path]


def topic_files(flat: str) -> dict[str, list[str]]:
    """Карта тема -> её сжатые файлы; лежит рядом с папкой flat."""
    path = os.path.join(os.path.dirname(flat.rstrip("/")), "topics.json")
    return {t["id"]: t["files"] for t in json.load(open(path, encoding="utf-8"))["topics"]}


def flat_anchors(flat: str, names: list[str]) -> set[tuple[str, str]]:
    """Якоря, которые обязаны доехать: короткие `[L21]` плюс имя из поля source."""
    want: set[tuple[str, str]] = set()
    for name in names:
        text = read_flat(flat, name)
        if not text:
            continue
        source = (re.search(r"^source:\s*(\S+)", text, re.M) or [None, name])[1]
        for line in text.splitlines():
            if line.startswith("- "):
                want |= {(source, n) for n in SHORT.findall(line)}
    return want


def flat_text(flat: str, names: list[str]) -> str:
    return "\n".join(read_flat(flat, n) for n in names)


ANCHOR = re.compile(r"\[[^\]]*#?L\d+[^\]]*\]")
BRACKET = re.compile(r"\[([^\]]*)\]")


def normal(text: str) -> str:
    return re.sub(r"\s+", " ", ANCHOR.sub("", text)).strip(" .;·—-").strip()


def raw_bullets(text: str) -> list[str]:
    """Пункты как единицы, целиком и без разбора: многострочный пункт — один."""
    out: list[str] = []
    current: list[str] = []
    for line in text.splitlines() + ["- "]:
        if line.startswith("- "):
            if current:
                out.append(" ".join(current))
            current = [line[2:]]
        elif current and line.strip() and not line.startswith("#"):
            current.append(line.strip())
        elif current:
            out.append(" ".join(current))
            current = []
    return out


def bullets(text: str) -> list[tuple[list[tuple[str, str]], str]]:
    """Пункт темы: его полные якоря и его текст без них."""
    return [(FULL.findall(b), normal(b)) for b in raw_bullets(text)]


def material_items(flat: str, names: list[str]) -> dict[tuple[str, str], list[str]]:
    """(источник, строка) -> тексты пунктов материала. Список, а не строка:
    одна запись разговора даёт несколько сухих пунктов под одним якорем."""
    items: dict[tuple[str, str], list[str]] = {}
    for name in names:
        text = read_flat(flat, name)
        if not text:
            continue
        source = (re.search(r"^source:\s*(\S+)", text, re.M) or [None, name])[1]
        for body in raw_bullets(text):
            # Якоря материала бывают групповыми: `[L30, L31]` — одна запись
            # разговора, давшая один сухой пункт. Разбор «ровно [L21]» терял
            # каждый третий и объявлял выдуманными полсотни настоящих якорей.
            for span in BRACKET.findall(body):
                for num in SHORT.findall(span):
                    items.setdefault((source, num), []).append(normal(body))
    return items


def accounting_gap(
    accounting: dict[str, object] | None,
    want: set[tuple[str, str]],
    got: set[tuple[str, str]],
) -> str | None:
    """Validate missing-anchor accounting kept in the run receipt.

    A merge may remove a superseded claim from the reader-facing topic, but the
    omission must be declared in the accepted response that produced it. This
    deliberately uses the existing run JSON response as the evidence carrier;
    it does not create a second topic-side store.
    """
    value = {"superseded": []} if accounting is None else accounting
    if not isinstance(value, dict) or set(value) not in (
        {"superseded"},
        {"superseded", "unresolved"},
    ):
        return "учёт якорей имеет лишние или отсутствующие поля"
    entries = value["superseded"]
    unresolved_entries = value.get("unresolved", [])
    if not isinstance(entries, list) or not isinstance(unresolved_entries, list):
        return "учёт якорей: superseded должен быть массивом"

    declared: set[tuple[str, str]] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"anchor", "by"}:
            return "учёт якорей: запись должна содержать только anchor и by"
        anchor, by = entry.get("anchor"), entry.get("by")
        if not isinstance(anchor, str) or not FULL.fullmatch(anchor):
            return "учёт якорей: anchor имеет неверный формат"
        if not isinstance(by, str) or not FULL.fullmatch(by):
            return "учёт якорей: by имеет неверный формат"
        anchor_match = FULL.fullmatch(anchor)
        by_match = FULL.fullmatch(by)
        if anchor_match is None or by_match is None:
            return "учёт якорей: anchor/by имеет неверный формат"
        anchor_key, by_key = anchor_match.groups(), by_match.groups()
        if anchor_key in declared:
            return f"учёт якорей: anchor повторяется {anchor}"
        if anchor_key not in want:
            return f"учёт якорей: anchor отсутствует во входе {anchor}"
        if by_key not in want or by_key not in got:
            return f"учёт якорей: surviving by не стоит в текущей теме {by}"
        declared.add(anchor_key)

    for entry in unresolved_entries:
        if not isinstance(entry, dict) or set(entry) != {"anchor", "reason"}:
            return "учёт якорей: unresolved должен содержать anchor и reason"
        anchor, reason = entry.get("anchor"), entry.get("reason")
        if not isinstance(anchor, str) or not FULL.fullmatch(anchor):
            return "учёт якорей: unresolved anchor имеет неверный формат"
        if not isinstance(reason, str) or not reason.strip():
            return "учёт якорей: unresolved reason не должен быть пустым"
        anchor_match = FULL.fullmatch(anchor)
        if anchor_match is None:
            return "учёт якорей: unresolved anchor имеет неверный формат"
        anchor_key = anchor_match.groups()
        if anchor_key in declared:
            return f"учёт якорей: anchor повторяется {anchor}"
        if anchor_key not in want:
            return f"учёт якорей: unresolved anchor отсутствует во входе {anchor}"
        if anchor_key in got:
            return f"учёт якорей: unresolved anchor попал в topic {anchor}"
        declared.add(anchor_key)

    fake = got - want
    if fake:
        return f"якоря не сходятся — лишних {len(fake)}"
    missing = want - got
    if declared != missing:
        return (
            "учёт якорей не сходится — необъявленных исчезнувших: "
            f"{len(missing - declared)}, лишних объявлений: {len(declared - missing)}"
        )
    return None


def parse_answer(text: str) -> tuple[str, dict[str, object], str | None]:
    """Split reader-facing topic text from its run-receipt accounting footer."""
    body = strip_fence(text)
    match = ACCOUNTING_RE.search(body)
    if match is None:
        if "TOPIC_ANCHOR_ACCOUNTING" in body:
            return "", {}, "учёт якорей повреждён или не стоит в конце ответа"
        return body, {"superseded": []}, None
    try:
        value = json.loads(match.group("data"))
    except json.JSONDecodeError:
        return "", {}, "учёт якорей не является JSON"
    return body[: match.start()].rstrip(), value, None


def unresolved_marker_gap(
    body: str,
    accounting: dict[str, object] | None,
) -> str | None:
    """Allow one neutral unresolved marker, never both conflicting claims."""
    entries = (
        accounting.get("unresolved", [])
        if isinstance(accounting, dict)
        else []
    )
    has_heading = bool(re.search(r"^## Не разрешено\s*$", body, re.M))
    if not entries:
        return (
            "topic содержит ## Не разрешено без внешнего unresolved-учёта"
            if has_heading
            else None
        )
    if not has_heading:
        return "unresolved-учёт требует нейтральный раздел ## Не разрешено"
    match = re.search(
        r"^## Не разрешено\s*$([\s\S]*?)(?=^## |\Z)",
        body,
        re.M,
    )
    section = match.group(1) if match else ""
    lines = [line for line in section.splitlines() if line.startswith("- ")]
    if len(lines) != 1:
        return "## Не разрешено должен содержать ровно один neutral abstain marker"
    if FULL.findall(section):
        return "neutral unresolved marker не должен публиковать raw anchors"
    neutral_words = (
        "не разреш",
        "unresolved",
        "abstain",
        "сверить raw",
        "consult raw",
    )
    if not any(word in section.casefold() for word in neutral_words):
        return "## Не разрешено должен назвать текущую позицию unresolved"
    return None


def coverage_gap(
    body: str,
    flat: str,
    names: list[str],
    accounting: dict[str, object] | None = None,
) -> str | None:
    """Каждый пункт материала обязан присутствовать целиком — вот инвариант.

    Прежняя редакция сравнивала множества якорей, и Codex показал, чем за это
    платят: 83 якоря из 1586 несут по нескольку пунктов, поэтому удаление
    одного из них множество не меняет. Подмена тезиса на противоположный при
    сохранённом якоре тоже проходила. Считать надо пункты, а не подписи.
    """

    excused = {
        FULL.fullmatch(entry["anchor"]).groups()
        for entry in (
            list((accounting or {}).get("superseded", []))
            + list((accounting or {}).get("unresolved", []))
        )
        if isinstance(entry, dict)
        and isinstance(entry.get("anchor"), str)
        and FULL.fullmatch(entry["anchor"])
    }
    holders: dict[tuple[str, str], list[str]] = {}
    for anchors, text in bullets(body):
        if len(set(anchors)) > 1:
            # Пункт с несколькими якорями — законное схлопывание дублей из
            # разных разговоров: контракт даёт ему одну формулировку и все
            # источники, поэтому дословного вхождения каждого требовать нельзя.
            excused |= set(anchors)
            continue
        for anchor in anchors:
            holders.setdefault(anchor, []).append(text)
    items = material_items(flat, names)
    lost = [key for key, texts in items.items()
            if key not in excused
            and any(not any(t in h for h in holders.get(key, [])) for t in texts)]
    # Встречное направление обязательно. Сторона материала спрашивает «всё ли
    # доехало» и молчит, когда пункт подменён: якорь на месте, а тезис чужой —
    # именно так подмена на противоположный проходила гейт. Сторона темы
    # спрашивает «откуда это взялось» и подмену видит.
    drift = [key for key, texts in holders.items()
             if items.get(key)
             and any(t not in items[key] and not all(o in t for o in items[key])
                     for t in texts)]
    invented = sorted(set(FULL.findall(body)) - set(items))
    if lost or drift or invented:
        parts_out = []
        if lost:
            parts_out.append(f"пункты материала не доехали: {len(lost)}")
        if drift:
            parts_out.append(f"текст разошёлся с источником: {len(drift)}")
        if invented:
            parts_out.append(f"выдуманных якорей: {len(invented)}")
        return " · ".join(parts_out)
    return None


def theme_gap(
    body: str,
    flat: str,
    names: list[str],
    accounting: dict[str, object] | None = None,
) -> str | None:
    """Единственный владелец слова «готова» для темы: форма, язык, происхождение.

    Раздельные проверки уже дважды разошлись между собой: доска считала тему
    готовой по непустому ответу, а раскладка отвергала её по якорям — счёт
    владельцу назывался на четыре темы больше настоящего.
    """
    if not body.startswith("---"):
        return "ответ не похож на файл темы"
    if TOMBSTONE_HEADING.search(body):
        return "reader-facing topic содержит запрещённый раздел ## Отменено"
    gap = material_gap(flat, names)
    if gap:
        return gap
    try:
        gap = language_gap(body, flat_text(flat, names))
        if gap:
            return gap
        want, got = flat_anchors(flat, names), set(FULL.findall(body))
        gap = accounting_gap(accounting, want, got)
        if gap:
            return gap
        gap = unresolved_marker_gap(body, accounting)
        if gap:
            return gap
        return coverage_gap(body, flat, names, accounting)
    except FileNotFoundError as error:
        return f"входной материал исчез: {error.filename or error}"


def cyr_share(text: str) -> float:
    """Доля кириллицы среди букв: 1.0 — чистый русский, 0.0 — чистая латиница."""
    cyr, lat = len(CYR.findall(text)), len(LAT.findall(text))
    return cyr / (cyr + lat) if cyr + lat else 0.0


def language_gap(body: str, material: str) -> str | None:
    """Причина отказа по языку либо None. Нерусский материал гейт не судит."""
    want = cyr_share(material)
    if want < LANGUAGE_FLOOR:
        return None
    got = cyr_share(body)
    if got < want * LANGUAGE_FLOOR:
        return (f"язык разошёлся с материалом: кириллицы {got:.0%} в ответе "
                f"против {want:.0%} в материале")
    return None


def run_verdict(path: str) -> tuple[dict | None, str]:
    """Принят ли прогон. Первый элемент — payload, второй — причина отказа."""
    try:
        payload = json.load(open(path, encoding="utf-8"))
    except Exception as error:
        return None, f"нет JSON ({error.__class__.__name__})"
    if not payload.get("ok"):
        return None, "прогон не принят обёрткой"
    body = payload.get("response") or ""
    if len(body) < MIN_RESPONSE:
        return None, f"ответ пуст или короток ({len(body)} симв)"
    return payload, ""


def read_answer(path: str) -> tuple[str | None, str]:
    """Ответ темы, кем бы он ни был сделан: квитанция волны или файл субагента.

    Производителей у слоя два, а судья должен остаться один — иначе счёт снова
    разойдётся с раскладкой, как разошёлся 2026-08-25 на четырёх темах.
    """
    body, _, why = answer_details(path)
    return body, why


def answer_details(path: str) -> tuple[str | None, dict[str, object], str]:
    """Read a response and retain its non-reader-facing accounting footer."""
    if path.endswith(".md"):
        raw = open(path, encoding="utf-8").read()
        if len(raw) < MIN_RESPONSE:
            return None, {}, f"ответ пуст или короток ({len(raw)} симв)"
    else:
        payload, why = run_verdict(path)
        if payload is None:
            return None, {}, why
        raw = payload.get("response") or ""
    body, accounting, why = parse_answer(raw)
    if why:
        return None, {}, why
    return body, accounting, ""


def answers_in(folder: str) -> list[str]:
    return sorted(glob.glob(os.path.join(folder, "*.json"))
                  + glob.glob(os.path.join(folder, "*.md")))


def survey(tasks: str, answers: tuple[str, ...], flat: str | None
           ) -> tuple[list[str], dict[str, str], dict[str, str]]:
    """Что заказано, что готово и почему остальное — нет. Одна правда на всех."""
    wanted = sorted(os.path.basename(p)[:-4]
                    for p in glob.glob(os.path.join(tasks, "*.txt")))
    files = topic_files(flat) if flat else {}
    ready: dict[str, str] = {}
    refused: dict[str, str] = {}
    for folder in answers:
        for path in answers_in(folder):
            name = os.path.splitext(os.path.basename(path))[0]
            body, accounting, why = answer_details(path)
            if body is None:
                refused.setdefault(name, why)
                continue
            gap = (
                theme_gap(body, flat, files.get(name, []), accounting)
                if flat
                else None
            )
            if gap:
                refused[name] = gap
                continue
            refused.pop(name, None)
            ready[name] = f"{len(body) // 1000}к · {cyr_share(body):.0%} рус"
    return wanted, ready, refused


def main(tasks: str, *rest: str) -> int:
    answers = tuple(a for a in rest if not a.startswith("--"))
    flat = next((a.split("=", 1)[1] for a in rest if a.startswith("--flat=")), None)
    wanted, ready, refused = survey(tasks, answers, flat)
    for name in wanted:
        if name in ready:
            print(f"  {name}: готов · {ready[name]}")
        else:
            print(f"  {name}: {refused.get(name, 'ответа нет')}")
    print(f"готово: {len(set(wanted) & set(ready))} из {len(wanted)}")
    return 0 if wanted and all(name in ready for name in wanted) else 1


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:]))
