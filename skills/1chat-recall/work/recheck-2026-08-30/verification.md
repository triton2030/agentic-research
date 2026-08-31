# Verification receipt — metadata-route candidate 2026-08-31

## Exact candidate

- Scope: `skills/1chat-recall/versions/candidate-2026-08-31/**`;
  official/tracked/live
  packages не менялись.
- Полностью прочитанный baseline `1skill-creation`:
  `/Users/triton/.codex/skills/1skill-creation/SKILL.md`, SHA-256
  `11e82449797be9615b92976f2fe33f8677f74429a10fc2564a91b7a09fae344e`.
- Codex manifest, 20 runtime files:
  `14c7d18fcbb73d069711ba700bcd5267adf2c605ac3c21e849a9a5f77a22f913`.
- Claude manifest, 21 runtime files:
  `503e0500dd5c0cacfa65a3f386249689cdfc1191c41e3f23e17b8d3ce3b78daf`.
- Manifest rule: рекурсивный sorted SHA-256 всех runtime files, исключая
  `__pycache__`, `.pytest_cache`, `.ruff_cache`, `*.pyc` и `.DS_Store`, затем
  SHA-256 полученного списка.
- Runtime topology не выросла: те же Capture, Retrieval и Integrity, без новых
  references, stages или per-topic файлов.

## Изменённое свойство и фальсификаторы

| Property | Falsifier | Exact evidence |
| --- | --- | --- |
| `topics.md` снова участвует в Retrieval | query совпадает только с topic description, но route пуст либо выдаёт quote | `test_topic_description_is_a_separate_route_not_owner_evidence` |
| topic и holder scores не смешиваются | один объект или один rank выдаётся за оба слоя | `test_holder_and_topic_routes_can_both_answer_without_score_mixing` |
| retired boundary не возвращается | retired-only token допускает topic | `test_retired_topic_is_not_a_retrieval_candidate` |
| пустой lexical match остаётся честным `none` | dense произвольно допускает ближайшую тему | `test_bounded_json_and_zero_result`; topic dense только re-ranks lexical admission |
| Capture читает всю карту, создаёт отсутствующую тему атомарно | неизвестная тема пишется без map compare либо остаётся partial row | существующие add/rollback/missing-map tests |
| `session-context` и `context-note` имеют разные масштабы | новая реплика заменяет session card либо context становится пересказом | Capture contract anchors + update/search tests |
| выбранный holder читается целиком | runtime instruction разрешает применить snippet | `test_retrieval_contract_keeps_metadata_routes_and_full_holder_read` |
| topic route не становится вторым owner | description называется position/evidence | separate `topic_candidates` envelope и прямой запрет в Retrieval |

## Checks

- Codex full suite: `112 tests`, `OK`.
- Claude full suite: `109 tests`, `OK`.
- Focused Ruff `E,F`, `py_compile` и system `quick_validate.py`: PASS для обоих
  runtime packages.
- Frontmatter, Codex `openai.yaml` и 14 relative Markdown links: PASS.
- Shared Capture/digest/metadata scripts и Capture reference byte-identical
  между Codex и Claude; runtime-specific frontmatter, paths и fixtures остаются
  намеренными различиями.
- Trigger surface не менялась: `When owner speech needs attention.` остаётся
  коротким English trigger-only description; body и references — русские.

## Реалистичная clean probe на текущем корпусе

Corpus snapshot: 1785 records / 270 session holders.

- Lexical query `жизненный` вернул `selection=holders+topic_candidates`: два
  независимых topic candidates из единственного `topics.md`
  (`codex-background-threads`, `chat-recall-corpus`) и два holders. Topic cards
  не содержат quote/address и имеют свой `topic_rank`.
- Follow-up `--query chat-recall-corpus --topic chat-recall-corpus` вернул 32
  matching holders и ровно topic `chat-recall-corpus`; это наблюдаемый переход
  topic description → handle → session holders.
- Запрос без lexical topic match не получает произвольный dense topic: dense
  только переупорядочивает уже допущенные lexical boundaries.

## Active sets

Смысловой recount считает самостоятельные решения, а не строки и не скрывает
их переименованием:

| Runtime | Capture | capture-needed | Retrieval warm / topic follow-up / background | Cold recovery | Validation | Repair read-only / mutation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Codex | 20 | 22 | 20 / 22 / 23 | 22 | 10 | 17 / 20 |
| Claude | 20 | 22 | 20 / 22 / 23 | 22 | 10 | 17 / 20 |

Условный excess оправдан конкретным вредом: topic follow-up предотвращает
потерю цитаты за другой лексикой; background branch ограничен одним поиском и
не блокирует работу; cold recovery сохраняет исполняемый hybrid/lexical seam;
`capture-needed` переносит native provenance. Новые files/stages ради числа не
создавались.

## Residuals

- Две разрешённые checker waves были израсходованы на предыдущих exact bytes.
  По прямому лимиту владельца новые субагенты не запускались; изменённый
  metadata-route проверен root-агентом tests, falsifying probes и exact-byte
  checks. Старые checker verdicts не выдаются за проверку новых manifests.
- Текущий корпус не переписывался: 133 legacy quote/selection записей всё ещё
  без `context-note`, 18 records используют topic вне live map; все 270 session
  holders имеют `session-context`. Raw load даёт 41 diagnostic record. Это
  отдельный backfill/Repair scope, не скрытая часть установки скила.
- Candidate не установлен. Любая правка меняет manifests; official/projection/
  live запись требует безусловного approval именно этих exact manifests.
