# Evidence

## Shared Visual Explainer Zone 2026-08-20

Owner evidence:
`_ops/chat-recall/2026-08-19-212344-codex-01a01ad4.md` — одна общая папка
артефактов, один набор components/styles/libraries, многократное reuse разными
HTML; без лишних проверок и дополнительных шагов.

| Claim | Falsifier | Статус |
|---|---|---|
| Генератор создаёт flat page | после вызова существует directory `<slug>/` или нет `<slug>.html` + `assets/<slug>.css` | pass: `/tmp/1html-shared-zone.SJU8Jw`, `alpha` и `beta`, directories отсутствуют |
| Shared layer действительно один | две страницы получают собственные copies `lib/assets` либо используют разные runtime paths | pass: обе страницы ссылаются на root `lib/` + `assets/shared/`; runtime существует один раз |
| Folder stance одна | генератор создаёт больше одного `AGENTS.md` или дублирует полную инструкцию в каждой странице | pass: один root `AGENTS.md`; его hash после второй страницы не изменился |
| Дизайн не шаблонизирован | page scaffold содержит palette, layout, cards, header, rail, node anatomy или fixed geometry | pass: source grep пуст; scaffold содержит только semantic `main/h1` и local links |
| Обычный путь свободен от QA | `SKILL.md` требует audit/check/finish/browser/screenshot или add-on installer | pass: старые scripts/reference удалены; SKILL явно исключает QA-loop |
| Каталог понимает flat pages | созданная страница отсутствует в payload или ссылка ведёт в `<slug>/index.html` | pass: payload содержит `alpha.html` и `beta.html` |
| Legacy артефакт не ломается | каталог перестаёт видеть существующий directory artifact | pass: synthetic `legacy-page/index.html` остаётся в payload |
| Shared components/styles можно развивать | `assets/shared/components.css` отсутствует или перезаписывается при создании следующей страницы | pass: authored hash `065c0828…19a0` не изменился после `delta` |
| Zone snapshot не смешивает поколения | следующая страница берёт новый skill scaffold при старых local instructions/runtimes | pass: runtime, instructions, carrier map и оба neutral templates создаются only-if-missing; новая страница читается из local snapshot; catalog projection обновляется отдельно |
| Base icon carrier работает без skill/QA | `<i data-lucide>` остаётся пустым, потому что local runtime подключён, но не инициализирован | pass: neutral template регистрирует `DOMContentLoaded → lucide.createIcons()`; COMPONENTS называет automatic/manual boundary |
| Существующая чужая инструкция не уничтожается | генератор молча перезаписывает `AGENTS.md` без generated marker | pass: `/tmp/1html-shared-foreign.Yv4iXS`, hash до/после одинаков |
| Package не содержит старый workflow | остаются bundle/finish/audit/add-on installer/validator scripts | pass: file/name/content scan; scripts остались `new`, `rebuild`, metadata, catalog builder |
| MAVO migration сохраняет страницу | CSS или видимая шапка меняются; старый URL пропадает | pass: CSS byte-identical; прежние home-link/icon/title перенесены из runtime в static HTML; old-path directory содержит только redirect; catalog href один — `whatsapp-order-interface.html` |
| Stance меняет attractive solution | unseen nested/overlay/responsive prompt после чтения кандидата всё ещё даёт repeated cards или compensating breakpoint | pass: `../behavior-comparator.md`; control — четыре peer cards и три media blocks, treatment — physical nesting, разные carriers и один named composition breakpoint |

Package smoke: `bash -n`, `shellcheck`, `ruff --no-cache`, `node --check` всех
authored adapters, `qv-skill` и `md check` (`16` targets) — pass. На момент
acceptance: exact candidate audit — pass (`instruction_surface`,
`skill_science`, `claude-opus-5`); live projection ожидает буквального согласия
владельца.
