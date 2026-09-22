## Приёмочный результат по семи прежним находкам

Пять tool calls, всё read-only кроме `/tmp`. Полных наборов в этом круге не запускал.

| # | Находка | Статус | Чем закрыта (наблюдение этого круга) |
|---|---|---|---|
| 1 | Доставка в Codex не состоялась | **Закрыта** | `~/.codex/skills/1chat-recall` ↔ `skills/codex/1chat-recall`: 24/24, missing/extra/differs — пусто. `~/.claude/…` — symlink на owner-а, 25/25. `accepted-candidate-sha256.json` — 49 записей, 0 расхождений с исходниками. Прямая проба в `/tmp`: installed Codex принял `--source-ref`, повтор дал `already-present` с тем же anchor, второй «да» того же сообщения записан отдельной `#recall-a95269d1…`. То же на installed Claude (`#recall-fbe86c39…`) |
| 2 | Installed Codex отвергал `#recall-` адреса | **Закрыта как следствие 1** | Тот же байтовый состав, что и у принятого кандидата. Отдельную пробу `--supersedes '<file>.md#recall-…'` на installed Codex в этом круге не повторял |
| 3 | Момент предъявления называл только новую форму | **Закрыта** | `references/retrieval.md:90-92`: «устойчивый `address` из выдачи (`<файл>.md#recall-<id>`), **а для старой записи без него — ссылка на файл по правилу legacy выше**». Блок побайтово одинаков в обоих рантаймах |
| 4 | `--show` не принимал полный адрес | **Закрыта** | Прямая проба в обоих installed: `--show '<file>.md#recall-<id>'` → `matched:1`; `--show 'recall-<id>'` → `matched:1`. Красный `show-address-red.log`: 3 FAIL, включая `test_show_rejects_duplicate_stable_address_and_record_id`; зелёные `show-address-green-{codex,claude}.log` — `Ran 3 … OK` |
| 5 | Манифест и логи не относились к поставляемым байтам | **Закрыта** | `accepted-candidate-sha256.json` + `installed.json` сходятся с текущими байтами; `tests-accepted-codex.txt` — `Ran 160 … OK`, `tests-accepted-claude.txt` — `Ran 157 … OK`. Прежние `red-runtime.log` (10:49), `green-codex.log` (10:57) и `candidate-sha256.json` (11:02) сохранены с исходными mtime — история не переписана |
| 6 | Красная база покрывала 8 из 18 | **Закрыта** | `five-regressions-before-codex.log`: 5 FAIL с именами ровно тех пяти тестов, которые я называл (`two_yes_answers…`, `exact_timestamp_fallback…`, `date_only_without_source_ref…`, `relations_keep_target_after_manual_insertion…`, `failed_transaction_cannot_rollback…`); claude-вариант — `Ran 5 … FAILED (failures=5)` |
| 7 | В живых документах MAVO остались `#L` мимо цели | **Закрыта** | В трёх названных мной файлах `#L` в эти два holder-а больше нет: `_ops/handoffs/2026-09-22-103915-claude-fable-5-1.md` (строки 14, 18, 58 и далее) и `_workspace/orchestration/2026-09-19-catalogue-metadata/{state.md:17, price-acceptance.md:5}` несут `#recall-…`. Попутно виден и исправленный ранее неверный target: `price-acceptance.md` ушёл с `#L18` (заголовок файла) на `#recall-5bf67d92…`. `remaining-legacy-links.json` — 115 записей, `link-migration-continuations.json` — 24 |

## Границы выполненных прямых проверок

Проверил сам в этом круге: побайтовое совпадение обеих installed-проекций с владельцами; по одной пробе capture на каждый installed runtime во временном проекте (`--source-ref`, идемпотентный повтор, второй «да» из того же сообщения) и `--show` полного адреса и голого id; текст момента предъявления в обоих `retrieval.md`; наличие и строки итогов в accepted/regression/show-логах; адреса в трёх ранее помеченных документах MAVO.

Принял по вашим артефактам, не проверяя самостоятельно: цифры 160/157 (логи читал, наборы в этом круге не запускал — в прошлом круге я сам получил 157/154 на тогдашних байтах); разбивку 115 = 6 архивных + 109 backup и поэлементную верность 115 и 24 записей; отказ `--show` по неоднозначности (видел красный тест по имени и зелёный набор, своей пробы неоднозначности не делал); приёмку независимого auditor-а по D1–D5.

Непроверенным остаётся то же, что и раньше: семантический/hybrid маршрут (все мои запросы шли `--lexical`), `--check --strict` по реальному корпусу, конкуренция сверх тестовых 12 процессов и надёжность при ручных редакторах.
