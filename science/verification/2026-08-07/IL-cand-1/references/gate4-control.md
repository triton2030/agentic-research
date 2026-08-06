# Gate 4 — Выбери Control И Один Repair

1. Спроси, допустимо ли, чтобы соблюдение этого obligation зависело от качества
   reasoning. Чем дороже или необратимее пропуск, тем слабее prose как control.
2. Для hard invariant выбери permission, hook, validator, test или approval у
   live runtime owner-а; instruction оставляет route/объяснение, не изображает
   enforcement.
3. Для text-level delta сравни repairs по причине провала:
   - `keep` — owner, load, steering и evidence уже достаточны;
   - `delete` — устойчивой delta нет либо текст только дублирует meaning;
   - `narrow scope` — rule верен лишь для меньшего observable trigger-а;
   - `move to owner` — meaning верен, но лежит не в effective owner-е;
   - `replace with pointer` — truth уже существует у другого owner-а;
   - `rewrite exact wording` — owner/placement верны, но первый акт не меняется;
   - `handoff to enforcement` — цена пропуска несовместима с prose-only control.
4. Выбери один primary repair. Supporting edits допустимы только для удаления
   созданных им duplicates или broken routes, не для попутной уборки.
5. Procedure добавляй только когда order, lifecycle moment, completeness или
   хрупкость сами являются контрактом; иначе оставь outcome/decision rule.

**Результат gate:** `prose|enforcement + primary repair + почему меньший repair
не закрывает harm`. Не можешь отличить выбранный repair от меньшего → используй
меньший.

Далее: `gate5-wording.md`.
