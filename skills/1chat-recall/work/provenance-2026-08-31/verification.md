# Verification — deletion-only provenance version 2026-08-31

## Exact installed version

- Version: `skills/1chat-recall/versions/installed-2026-08-31-provenance/`.
- `1skill-creation` baseline SHA-256:
  `1831f5d21ef22ca9618a8211bb999f3c37bf663db805d08dc3732edfda15c7de`.
- Codex manifest, 20 files:
  `98178a355044e37d1b135b291dbd771eee3b113846177c9d4bf621074ec54806`.
- Claude manifest, 21 files:
  `36c65ed0c62ad698bda856761fb4f56c6ab7fd28d9e56942518e430788ed9ff9`.
- Manifest: sorted SHA-256 всех runtime files без generated caches, затем
  SHA-256 списка с package-relative paths.

## Изменённое поведение

| Property | Falsifier | Evidence |
| --- | --- | --- |
| Цитата сокращается только удалением | contract разрешает paraphrase, reorder или additions | Capture contract anchors + CLI help test |
| Пасты не становятся owner speech | документ, разговор или слова другого агента предписано сохранить целиком | Capture contract test |
| Legacy Codex carrier fail-closed | delegation/controller record возвращается как message | paired legacy test |
| Claude tool follow-up fail-closed | plain-text record с `sourceToolAssistantUUID` возвращается | characterization test |
| Terminal wording честно описывает seam | extractor называет candidates owner evidence или helper обещает сам доказать authorship | help tests обоих runtimes |
| Topic creation остаётся исполнимым | reference требует отсутствующий flag | `--new-topic-boundary` запрещён test-ом; фактический `--new-topic <BOUNDARY>` сохранён |

## Checks exact bytes

- Codex full suite: `114/114`, PASS.
- Claude full suite: `111/111`, PASS.
- Ruff `E,F` без style-only `E501`: PASS.
- `python3 -m compileall`: PASS.
- system `quick_validate.py`: PASS для tracked и installed packages.
- `md check`: product/history `65/0`; Codex runtime `4/0`; Claude runtime
  `4/0` targets/issues.
- Shared `capture.md`, `chat_capture.py`, `chat_digest.py`, lock,
  `recall_metadata.py` и digest tests побайтно одинаковы; transcript adapters и
  runtime paths остаются намеренной platform delta.

## Current-runtime provenance probe

На реальном transcript этой сессии installed Codex adapter с
`--include-current-turn` дал:

- query по controller-тексту «Автор этого сообщения — корневой оркестратор»:
  `returned=0`, `total=0`;
- query по прямой текущей реплике владельца «Тут важно понимать…»:
  `returned=1`, `total=1`;
- `17` известных carrier-сообщений отфильтрованы warnings.

Это проверяет текущую `response_item.message` форму, а unit test отдельно
закрывает старый `event_msg.user_message`.

## Installation and parity

- Codex version = tracked owner = installed projection:
  `98178a355044e37d1b135b291dbd771eee3b113846177c9d4bf621074ec54806`.
- Claude version = tracked owner = installed symlink target:
  `36c65ed0c62ad698bda856761fb4f56c6ab7fd28d9e56942518e430788ed9ff9`.
- Установлена frozen version; generated caches в manifest не входят.

## Complexity and residuals

- Новый runtime file, stage, source store или interface не добавлен.
- Capture получил четыре невыводимые границы: message provenance не равно span
  authorship; known agent carriers исключаются; pasted foreign content
  исключается; surviving span меняется только удалением.
- Helper намеренно не может механически доказать deletion-only без полного
  исходного сообщения. Это agent-owned semantic boundary, явно названная в
  contract и CLI; при сомнении требуется gap.
- Carrier без wrapper и без какого-либо provenance marker неотличим от legacy
  прямого ввода. Известные наблюдаемые схемы закрыты; неизвестную схему нельзя
  объявлять доказанной при Repair.
- Новые checker-субагенты не запускались: владелец исчерпал разрешённые две
  волны ранее. Exact bytes проверены root-тестами и current-runtime probe.
