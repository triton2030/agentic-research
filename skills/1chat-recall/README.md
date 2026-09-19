---
description: "Product truth, version packages, and refactor evidence for 1chat-recall."
---

# 1chat-recall

Эта папка хранит историю `1chat-recall` и evidence принятых решений, но не
является runtime package. Product owner по корневому реестру —
`skills/shared/1chat-recall/product-frame.md`. Живые runtime owners находятся в
`skills/codex/1chat-recall/` и `skills/claude/1chat-recall/`; установленные
`~/.codex/skills/1chat-recall/` и `~/.claude/skills/1chat-recall/` — их
projections.

Адресная установленная правка 2026-09-13: область действия цитат в обоих
рантаймах и глобальных инструкциях. [Проверка и границы](work/scope-2026-09-13/verification.md),
точные байты — `work/scope-2026-09-13/installed-sha256.json`.

## Топология

- `versions/<version-id>/` — самостоятельный снимок package. Если Codex и
  Claude расходятся намеренно, версия хранит отдельные `codex/` и `claude/`.
- `work/<work-id>/` — служебные материалы создания и проверки: intent, cut,
  preservation map, reviews, probes и verification.
- `product-frame.md` — историческая продуктовая рамка; действующий owner указан выше.
- `cut.md` — общая история снятых и перенесённых смыслов между версиями.

Текущая установленная версия:
`versions/installed-2026-09-14-dated-context/` — датированный контекст с
приоритетом нынешнего разговора и проверенного состояния; прежний смысловой
поиск сохранён. [Авторинг и проверка](work/dated-context-2026-09-14/verification.md).

Предыдущая версия:
`versions/installed-2026-09-14-semantic-search/` — независимый поиск цитат по
смыслу и provenance совпадений в обоих runtime. [Консультация и проверки](work/search-algorithm-2026-09-14/verification.md).

Предыдущая версия:
`versions/installed-2026-09-14-direct-quotes/` — прямой поиск и чтение рабочим
агентом в обоих runtime, без посредника. [Проверки и карта сохранности](work/direct-quotes-2026-09-14/verification.md).

Предыдущая версия:
`versions/installed-2026-09-09-answer-by-links/` — Claude: отчёт психолога ссылками,
без цитат, простые вопросы (`#L32`); Codex в руках другой сессии. Предыдущая —
`versions/installed-2026-09-08-search-notes/` — Claude-роль с блоком «Как устроен
поиск» (`#L31`); Codex без изменений. Предыдущая —
`versions/installed-2026-09-08-plain-subagent/` — Claude: психолог как обычный
субагент под каждый вопрос, без постоянной сессии (`#L30`); Codex без изменений
с `installed-2026-09-08-concise-answers/`. Предыдущая —
`versions/installed-2026-09-08-concise-answers/` — тот же механизм плюс форма
ответа психолога «по делу» (поправка владельца `#L28`). Предшествующая —
`versions/installed-2026-09-08-psychologist/` — корпус читает только
агент-психолог (`agents/psychologist.md`): в Claude повторно опрашиваемый
субагент на сессию, в Codex фоновый тред на проект; Retrieval — протокол
вызывающего; полное чтение разговора возвращено; description про понимание
владельца как личности. Утверждено владельцем 2026-09-08 («Да, устанавливай
оба варианта»). Evidence: [intent](work/owner-picture-2026-09-08/intent.md),
[verification](work/owner-picture-2026-09-08/verification.md),
[reviews](work/owner-picture-2026-09-08/reviews.md), Codex-аудиты —
`work/owner-picture-2026-09-08/codex-audit/`, байты —
`work/owner-picture-2026-09-08/installed-manifest.json`. Не проверено живьём:
проектный тред Codex (см. verification, последний раздел).

Предыдущая версия:
`versions/installed-2026-09-05-goals/` — три режима через цели и наблюдаемые
исходы, первая Capture в новом проекте, видимые конфликты и неустановленные
отмены. Evidence: [verification](work/goal-rewrite-2026-09-05/verification.md),
[состояние](work/goal-rewrite-2026-09-05/state.md),
[карта потерь](work/goal-rewrite-2026-09-05/intent.md).

Ранее: `versions/installed-2026-08-31-rewrite/`,
её intent и clean-room — `work/rewrite-2026-08-31/`.

Предшествующая установленная версия:
`versions/installed-2026-08-31-background-subagent/`.
Её намерение и terminal evidence: `work/background-subagent-2026-08-31/`.
Она делает дешёвый фоновый Retrieval-субагент обязательным и добавляет `Agent`
в `allowed-tools` Claude, без которого прежняя версия не могла выполнить
собственный шаг Retrieval 4.

Предшествовавшие установленные версии: `versions/installed-2026-08-31-provenance/`
(evidence — `work/provenance-2026-08-31/`) и `versions/installed-2026-08-31/`
(evidence — `work/install-2026-08-31/`).

Проверенные кандидаты сохранены в
`versions/candidate-background-subagent-2026-08-31/` и
`versions/candidate-2026-08-31/`, а полное evidence второго — в
`work/recheck-2026-08-30/`.

Предыдущий draft package находится в `versions/draft-2026-08-29/`, а его
review history — в `work/refactor-2026-08-29/`.

Версия не становится owner-ом после установки. Promotion всегда меняет
tracked runtime owner, после чего installed package остаётся projection.
