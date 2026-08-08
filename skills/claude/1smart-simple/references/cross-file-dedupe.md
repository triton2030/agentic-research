# Cross-File Dedupe

Читай, когда задача — максимально сократить Markdown-файл, а сжатие упирается
в повторы между файлами, секциями или source-of-truth формулировками.

Это IA-способ сжатия, а не стилистический приём: сначала сориентируйся, какие
соседние файлы уже владеют темой, затем убери из текущего файла подробности,
которые лучше живут в canonical owner. В этом скилле действие ограничено
производным файлом: gist + ссылка. Перенос truth, выбор нового owner-а,
split/merge/move и аудит всей базы файлов принадлежат `1ia-audit`.

## Результат

Производный файл короче: дубли заменены на one-line gist + ссылку на
authoritative owner, если это нужно читателю. Owner truth не переехал, graph не
изменён молча, structural work передан соседнему owner-у.

## Gate

Не выбирай лёгкий путь "сжать абзацы", если файл повторяет отдельный guide,
канон, glossary, process, decision или owner truth из соседнего Markdown-файла.
Сначала ответь:

1. Current file — owner truth или derivative view?
2. Где authoritative owner, который будущий агент должен править?
3. Нужна ли текущему reader job подробность или достаточно gist + wikilink /
   Markdown link?

Если owner не находится быстро или спорен, не угадывай и не переноси текст:
handoff в `1ia-audit`.

## Evidence Path

Выбери самый узкий evidence route; само сжатие не требует
runtime/index ritual.

1. Если current file и предполагаемый owner уже известны, прочитай оба
   тела напрямую. Для literal duplicate возьми scoped exact packet у
   `1cli-tools`; verdict owner-vs-derivative остаётся здесь.
2. Если неизвестно, где живёт смысл или нужен broad duplicate search,
   передай discovery в `1md-search`. Он владеет query pack, corpus scope и
   index recovery; bounded чтение уже найденного адреса — `1md-read`. Здесь
   используй адресуемый evidence packet, а не повторяй их CLI lifecycle.
3. Exact refs/counts передавай `1cli-tools`. Graph/frontmatter/anchor или
   downstream obligations — `1md-graph` до edit.
4. После обычного prose-only сжатия проверь direct diff/read и
   owner link. Graph closeout делай только через `1md-graph`, если такой
   риск реально задет.

## Решение

1. Определи authoritative owner по прочитанным bodies. Если его место
   неизвестно — `1md-search`; если неясен сам owner/structure —
   остановись и handoff в `1ia-audit`.
2. Если есть graph/frontmatter/blast obligations, handoff в `1md-graph`.
3. Если дублирование держится папочным instruction contract или guardrail,
   handoff в `1instruction-shaping`; если держится graph/frontmatter edge,
   handoff в `1md-graph`.
4. Если повтор касается README или GOAL как strategic truth, handoff в
   `1goal`.
5. В derivative файле оставь gist + ссылку на owner. Используй wikilink, если
   корпус живёт в wikilink-стиле; иначе относительную Markdown-ссылку. Не
   переворачивай authority: owner не заменяется ссылкой на производный файл.

## Нельзя

- Не move/merge/split/delete файлы.
- Не менять frontmatter, graph edges или папочный контракт.
- Не считать `md audit` / `md refactor-candidates` разрешением на
  реорганизацию: это candidates для human review.
- Не требуй semantic index, если direct reads уже доказывают duplicate и
  owner. Если broad discovery не завершёно, назови ровно этот gap.
- Не оставлять подробный дубль "на всякий случай": если owner известен и
  reader job закрывается ссылкой, подробность здесь лишняя.
