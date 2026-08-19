# Evidence

## Support Envelope

- Target: Codex `gpt-5.6-sol`, reasoning `high` or stronger.
- Harness: Codex skill catalog and same-thread named subagents.
- Required tools: skill discovery, `business-growth-analyst`, project-document
  reading, `1chat-recall` Retrieval, optional web research.
- Required isolation: отдельный субагент в чистом окне.

## Acceptance

- `qv-skill` passed on the installed package; `rumdl` reported no Markdown
  issues; Python `tomllib` parsed the custom-agent configuration.
- Tracked owner and installed projections are byte-identical
  (`sync_simple_projections.py --check`); the installed custom-agent TOML is
  byte-identical to its tracked owner.
- Direct activation, Codex CLI `0.148.0-alpha.9`, `gpt-5.6-sol`, 2026-08-14:
  the bare prompt `Какую цену поставить новому тарифу?` autonomously opened
  the skill — earned by the **pre-2026-08-14-evening** description.

## Not claimed (2026-08-14 evening rewrite)

- The rewritten description has NOT been re-run on Codex. Codex acceptance
  above belongs to the previous text.
- Named-agent behavior on Codex still unclaimed: the desktop thread that
  installed the agent predates the catalog reload.
- The seven-section rewrite of `developer_instructions` (family parity with the
  ten live Codex critics) is a structural change only — no behavioral run.

## Проверка 2026-08-19

- Явный вызов с открытой trial-развилкой сформулировал задачу из текущей работы
  и вызвал отдельного `business-growth-analyst`; Root получил его
  `FINAL_ANSWER` и предъявил вердикт.
- Конкретные имена инструментов и поля их ответов удалены из runtime-контракта:
  скил владеет требованием вызвать субагента, а не API оркестратора.

## Candidate 2026-08-19 — прогноз последствий

- Product intent и runtime переписаны с data-gated ближайшей экономики на
  прогноз реакций и взаимодействий людей от запуска до лет.
- Automatic case без имени скила, Codex CLI `0.148.0-alpha.15`,
  `gpt-5.6-sol`, reasoning high: развилка auto/manual trial/paywall без метрик
  подняла скил, вызвала отдельного `business-growth-analyst` и вернула условный
  прогноз человеческих и долгосрочных последствий вместо
  `недостаточно данных`.
- Near-miss в том же harness: внутреннее переименование переменной без смены
  поведения, интерфейса и данных не подняло скил и не вызвало субагента.
- Claim нового поведения: при отсутствии данных агент выпускает условные
  причинные прогнозы вместо `недостаточно данных`, сохраняет активное чтение
  owner-history и не выдаёт priors за факты.
- Не проверены: широкий вопрос `куда дальше`; атака маршрута; прогноз уже
  выбранного маршрута; reuse существующей карты; конфликт двух цепочек.
- Global custom-agent TOML и tracked owner byte-identical после установки,
  SHA-256 `cffb523e...31a2a2`.

## Candidate 2026-08-19 — вход в незнакомую компанию

- Owner-коррекция сняла «конкретное решение» как единицу анализа: локальная
  задача теперь входной сигнал; вопрос ставит впервые нанятый аналитик после
  самостоятельного погружения в бизнес-ситуацию.
- Professional basis: IIBA BACCM связывает need, change, value, stakeholder,
  solution и context; IIBA Strategic Business Analysis ставит understanding
  business context and internal/external environment до framing need/outcome;
  IIBA Starting Business Analysis Work описывает первый вход через выяснение
  роли, stakeholders, планов, подхода и связей BACCM. URLs — в `origin.md`.
- Два независимых cognitive audit после исправлений — PASS: явный и
  автоматический пути вызывают отдельного аналитика; automatic trigger требует
  уже наблюдаемый business trace; reuse обязан покрывать текущий повод;
  нематериальная деталь не вынуждает выдумывать вопрос; методы предъявляются
  только вместе с влиянием на постановку или прогноз.
- Read-only forward test в чистом окне
  `/root/forward_test_business_entry` вызвал ровно один named subagent
  `/root/forward_test_business_entry/business_button_analysis`. На поводе
  «синяя или зелёная кнопка» аналитик восстановил фактический контекст
  `agentic-research`, признал цвет нематериальной рамкой и самостоятельно
  поставил вопрос о кросс-проектной ценности стратегического делегирования.
- Отчёт сохранил условный checkout-сценарий только как отдельную premise,
  различил факты и priors и предъявил влияние business-model mapping,
  actor/incentive map и funnel analysis. Файлы не менялись.
- Отдельный non-ephemeral `codex exec` прочитал новый skill, но завис на
  `wait` без receiver id; процесс остановлен. Этот прогон не считается
  доказательством handoff или результата.
- После установки tracked и global Codex agent byte-identical, SHA-256
  `f28484a1...1cc31`.
