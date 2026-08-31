# Evidence — 1codex-bg-threads

## Accepted candidate — exact final repeat 2026-08-30

- Exact runtime manifest:
  `10c8e8776634ac1058e7a442811e45986828d11a54a8c316567f5ea35c97e7e4`.
- Runtime composition: `SKILL.md`, `agents/openai.yaml`,
  `references/receiver-message.md`, `references/codex-native.md`.
- `quick_validate.py`, frontmatter/YAML, обе внутренние ссылки, локальные
  `## Цель`, русский instructional body/references и English trigger-only
  descriptions прошли.
- Final clean literal checker: `NO_FINDINGS`; core `5`, receiver active set
  `19`, native active sets `13–20`.
- Final clean trajectory checker: `NO_FINDINGS`.
- Новый clean-window probe прочитал только четыре runtime-файла и дал
  `BEHAVIOR_OK`: Luna/max + Local по умолчанию, evidence-gated Sol/xhigh,
  owner-launched ordinary message, archived refresh, queued readiness,
  writer-check и persisted lifecycle выполнены без recursive controller role.
- Первый formal repeat нашёл Sol reachability, owner-session identity,
  archived discovery, queued readiness и optimistic count; все пять классов
  исправлены одним semantic pass, после чего полный final repeat пройден.
- Candidate готова к exact owner approval, но не установлена. Existing live
  Codex package не изменялся; tracked owner и Claude package не создавались.

Receipts exact final repeat:

- [`receipts-2026-08-30/exact10-literal.md`](receipts-2026-08-30/exact10-literal.md)
- [`receipts-2026-08-30/exact10-trajectory.md`](receipts-2026-08-30/exact10-trajectory.md)
- [`receipts-2026-08-30/exact10-clean-probe.md`](receipts-2026-08-30/exact10-clean-probe.md)

## Superseded previous cycle — 2026-08-30

Этот раздел фиксирует прежний blocked hash и не описывает terminal candidate.

- Effective baseline `1skill-creation`:
  `9bf11f64b436d313d979cba822b684f502e8e40e5f15a12f78cbd914ca29a518`.
- Clean-room semantic создан до чтения old/live package; старый пакет затем
  использован только как loss oracle.
- После owner correction receiver-message пересобран как Markdown
  `# Контекст` → `# Цель` с ситуационными границами. Typed `THREAD_CARD`,
  `THREAD_DONE`, predicate machine и recursive controller invocation сняты.
- Exact candidate package содержит четыре runtime-файла: `SKILL.md`,
  `agents/openai.yaml`, `references/codex-native.md` и
  `references/receiver-message.md`.
- Manifest SHA-256 exact candidate:
  `c4152786d04537e376e985fd89bb2e8919dbbd8e7627f3c26d08efd336a58249`.
- `quick_validate.py`, YAML/frontmatter, две локальные ссылки, локальные цели
  references, русский instructional text, exact English trigger surfaces,
  отсутствие recursive launch-string/typed machinery и `git diff --check`
  прошли.
- Final trajectory checker: `NO_FINDINGS`.
- Final behavioral probe exact hash: `BEHAVIOR_OK`; create, fork follow-up и
  retained follow-up правильно передали роль без controller-skill. Из-за
  исчерпанного agent-thread limit использован существующий слот, поэтому новый
  clean-window не доказан.
- Final literal checker оставил один blocker: минимум `23` одновременно
  действующих core-предиката против бюджета `≤20`.
- Два checker repeats исчерпаны. Exact candidate имеет статус `NOT APPROVED`:
  predicate budget и новый clean-window остаются residual gaps; candidate не
  установлена.
- Существующий live Codex package не изменён; его наблюдаемый manifest SHA-256
  остаётся
  `359aa60342c3a777f04328c79e63be148448f5bef9959c563c6b5bc521d68ef2`.
- Tracked owner и Claude package по-прежнему отсутствуют и не создавались.

Финальные receipts:

- [`receipts-2026-08-30/final-literal.md`](receipts-2026-08-30/final-literal.md)
- [`receipts-2026-08-30/final-trajectory.md`](receipts-2026-08-30/final-trajectory.md)
- [`receipts-2026-08-30/final-clean-probe.md`](receipts-2026-08-30/final-clean-probe.md)

Ниже сохранено evidence прежнего refactor/install; оно историческое и не
утверждает текущую candidate.

## Принятые источники

- Live package полностью прочитан: `SKILL.md`, четыре файла `references/`,
  `agents/openai.yaml`, `origin.md`, `cut.md`, `evidence.md`.
- Owner evidence прочитано по адресам из [`origin.md`](origin.md); повторный
  retrieval с `--limit 80` вернул 68/68 holders, `truncated=false`.
- Более поздняя проверка от 2026-08-26 не нашла отмены продуктовой функции.
- Live owner и callable schema сохраняют приоритет над датированным runtime
  snapshot.
- Owner correction о technical-director role, model routing и writer-check
  находится в `_ops/chat-recall/2026-08-29-203235-codex-01a04e23.md:17-25`.
- `1orchestration/references/verify.md` уже владеет формой проверки: каждый
  `done_when` требует адресуемого evidence, а независимый проверяющий не может
  быть автором. Этот skill добавляет live risk-condition: mutable output
  фонового автора всегда требует такого проверяющего.
- Официальная OpenAI документация на 2026-08-29 подтверждает App Server
  lifecycle `thread/start|resume|fork`, active `turn/steer`, persisted goal,
  pin metadata и archive; model guide называет Luna efficient high-volume
  моделью, а Sol — flagship. Точные адреса сохранены в draft `runtime.md`.

## Baseline

Live package сообщает 65 самостоятельных актов: 31 в `SKILL.md` и 34 в
references. Этот счёт принят только как baseline той же гранулярности; число
строк само по себе качеством не является.

## Кандидат

Черновик сохраняет четыре mode-specific references, потому что native thread
lifecycle, межконтекстные packet schemas и retained re-entry не выводятся из
одного commander intent надёжно. Body хранит технического директора как
центральную модель, три цели, role dispatch, model/write-verification rules и
routes к этим владельцам.

## Непроверено

- Два разрешённых checker repeats завершены; последний repeat нашёл три
  reachability seams и спорный predicate-level budget. Reachability seams
  исправлены; независимый post-fix behavioral probe сохранил CTO, Luna/Sol,
  Local, verification и lifecycle trajectory. Новый checker repeat не запущен:
  лимит `check-approve.md` исчерпан.
- Predicate-level instruction budget остаётся спорным residual risk.
- Tracked owner отсутствует; второй source tree и Claude projection не созданы.

## Установка прежней версии — superseded evidence

- Standing-решение владельца об установке зафиксировано в
  `_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md:19,23`.
- Перед установкой `agents/openai.yaml` исправлен до короткого English
  trigger-only `Use when offloading work to visible Codex threads`.
- Exact package установлен только в существующий live Codex
  `/Users/triton/.codex/skills/1codex-bg-threads`.
- Candidate и live имеют одинаковые восемь instructional files и одинаковый
  aggregate SHA-256
  `9b7af950ef9fdc967f77a2ef8c02b289be2c056e8579945b4a3b21911213da65`.
- `quick_validate.py` прошёл для candidate и live; внутренние ссылки,
  русский instructional body/references, English trigger surfaces,
  composition/content parity и `git diff --check` прошли.

## Routing candidate

- Use: «Используй фоновые треды для этой работы».
- Skip: «Запусти обычных субагентов параллельно».
- Near-miss: «Продолжай работать в этом же основном треде».
- `description` остаётся коротким английским trigger-only контрактом; clean
  behavioral probes активировали visible-thread route и не спутали его с
  same-thread subagents.
