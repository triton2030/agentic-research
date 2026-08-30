# Реалистичная проба v4 · раунд 1

Чистый исполнитель получил только полный `draft-2026-08-30-v4/SKILL.md` и case
про обновление `2release-note` в проекте Atlas; старые versions, history и
выводы checker-ов ему были запрещены.

## Case

Root registry задавал существующего владельца, Claude/Codex-проекции и один
механизм синхронизации. Общая поверхность состояла из `SKILL.md` и
`scripts/check.sh`; Codex `agents/openai.yaml` был явно runtime-owned metadata.
Глобальные и корневые инструкции запрещали вывод секретов, а пользовательская
функция добавляла напоминание о проверке секретов перед публикацией release
note. До запуска точного утверждения не было.

## Фактическая траектория

1. Исполнитель разрешил три поверхности и механизм owner→projections из
   registry до `$1skill-creation`.
2. В `$1skill-creation` он передал один проект, имя `2release-note`, оба runtime,
   security constraints и границу общей поверхности.
3. До точного утверждения он остановил любые записи owner/projections.
4. После условного точного утверждения он связал approval с неизменёнными bytes
   кандидата и сопоставил весь пакет с инструкциями Claude, Codex и root.
5. При успехе он выбрал одну установку `$1skill-creation` через существующий
   sync; независимые записи в проекции не планировал.
6. В parity он включил `SKILL.md` и `scripts/check.sh`, а project-declared
   `agents/openai.yaml` сохранил вне общей поверхности.
7. В квитанцию он включил topology source, instruction sources, approval,
   manifest/hashes, conflict result и таблицу owner↔Claude↔Codex.

## Сравнение с intent

Траектория совпала с локальной дельтой: content-authoring остался у
`$1skill-creation`, а `1local-rules` изменил topology resolution, conflict gate,
portable boundary и terminal proof. Без скила исполнитель мог бы сравнить
целые деревья, удалить runtime metadata или принять установку без parity.

Проба честно не заявляет фактические post-install hashes: candidate bytes и
write authority не предоставлялись. Это доказательство траектории, а не
установка.
