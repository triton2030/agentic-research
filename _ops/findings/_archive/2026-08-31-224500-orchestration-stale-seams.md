# Находка — 2026-08-31 — запись:224500-orchestration-stale-seams

- 22:45 — `skills/1orchestration/README.md` называет два внешних шва, которых
  больше нет: `skills/claude/1codex/references/{orchestration,fleet}.md`
  (пакет `1codex` перекроен коммитом `79d31675`, теперь у него
  `advise/arbitrate/audit/delegate/threads/watch`) и
  `skills/shared/1planning/portable/references/delegation.md` (файла нет,
  planning-семья раскроена; упоминание осталось только в
  `skills/shared/1planning/cut.md`) | обнаружено при разборе механики v10 на
  стадии рефактора `1orchestration` | README папки-истории правится в этом же
  круге, отдельного прохода не требует.
- 22:45 — `skills/claude/1codex/references/delegate.md:80` утверждает: «Два
  воркера не правят один файл… это runtime-исполнение общего правила
  `1orchestration`». В живом `1orchestration` v10 такого правила нет — правило
  одного писателя снято начиная с v5. Сосед ссылается на несуществующее общее
  правило | обнаружено там же | развилка принадлежит стадии поведения этого
  рефактора: либо правило одного писателя возвращается в `1orchestration`, либо
  строку в `1codex` правит владелец того пакета.
