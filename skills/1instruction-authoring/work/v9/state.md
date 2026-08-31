# Состояние рефактора — 1instruction-authoring v9

## Текущее состояние

`готов полный черновик`

Заменено 2026-08-31 после прохождения `refactor.md` «После нового намерения» и
гейта `behavior-protocol.md`. Возвращает работу в `refactor.md`, раздел «После
полного черновика», на проверку потерь.

Цепь израсходованных состояний: `нужен новый commander's intent` →
`готово новое намерение` (`work/v9/commander-intent.md`) →
`ожидается смысловой черновик` → `нужен полный авторский черновик`
(`work/v9/semantic-draft.md`) → `готов полный черновик`
(`work/v9/draft/`, решения допуска — `work/v9/decisions.md`).

Отступление, влияющее на доверие: чистого окна у исполнителя не было, гарантия
clean-room не выполнена. Причина и компенсация — в `work/v9/semantic-draft.md`.
Прежнего сохранённого состояния не существовало: папка `work/` в истории скила
отсутствовала.

## Проверка потерь

Пройдена 2026-08-31, карта — `work/v9/loss-map.md`. Потерь уровня результата
или конечного состояния не найдено; требуемых владельцем способов не потеряно,
поэтому возврата к гейту `behavior-protocol.md` не потребовалось. Карта
провизорная: `check-approve.md` не запускался, и в `cut.md` она попадёт только
финальным текстом после находок проверки. Состояние `рефактор завершён` не
ставится.

## Источники старого пакета

Владелец пакета по реестру `skills/shared/README.md:16` —
`skills/shared/1instruction-authoring/portable/`, а не установленная проекция.

- `skills/shared/1instruction-authoring/portable/SKILL.md` — 36 строк, разделы
  Уникальный контекст · Цель пользователя · Границы решений (6 пунктов)
- `skills/shared/1instruction-authoring/portable/agents/zone-scout.md` — 33
  строки, контракт чистого разведчика внешней правды
- `skills/shared/1instruction-authoring/portable/references/verification.md` —
  32 строки, причинная проверка кандидата и условная установка
- `skills/shared/1instruction-authoring/platforms/codex/agents/openai.yaml` —
  7 строк, обязательная Codex UI metadata

История: `origin.md` (функция и две переделки), `cut.md` (карта потерь шести
версий), `user-said.md` (дословные цитаты), `evidence.md` (проверки v7 и
установка по v11).

## Отпечаток старого пакета

Зафиксирован в `work/v9/old-package-fingerprint.txt`.
