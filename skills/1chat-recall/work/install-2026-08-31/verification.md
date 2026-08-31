# Verification — installed corpus-only version 2026-08-31

## Exact version

- Version: `skills/1chat-recall/versions/installed-2026-08-31/`.
- `1skill-creation` baseline SHA-256:
  `c2ca7634a518779fd0c52da0f7bc83bcd55845f6708e86359c46fce9db17ea08`.
- Codex manifest:
  `e866b19d1971f4d869a50d1aa5ec6f5580ce4c934f7e399f909dc4c76b166e7f`.
- Claude manifest:
  `35fe050b916505cdfa538210bf403a11a8b82909089ce1af7f5a8417cc814de3`.
- Manifest — sorted SHA-256 всех runtime files без generated cache files,
  затем SHA-256 списка с package-relative paths.

## Изменение и фальсификатор

| Property | Falsifier | Evidence |
| --- | --- | --- |
| Обычный Retrieval читает только quote corpus | Retrieval contract ссылается на `chat_recall.py`, native transcript или использует их после пустого поиска | contract test запрещает обе строки в `retrieval.md`; `SKILL.md` направляет обычный поиск только в сохранённый corpus |
| Raw transcript требует отдельного owner request | Integrity доступен по внутреннему решению агента | `SKILL.md` и `integrity.md` требуют явный owner request; test фиксирует route и gap |
| Metadata-функция не потеряна | Capture не читает полную карту тем, не создаёт отсутствующую boundary или теряет два уровня контекста | прежние add/rollback/update/search tests входят в полные suites |

## Checks exact bytes

- Codex suite: `112/112`, PASS.
- Claude suite: `109/109`, PASS.
- Ruff `E,F` без style-only `E501`: PASS для обоих packages.
- `python3 -m compileall`: PASS для обоих packages.
- system `quick_validate.py`: PASS для version и installed packages.
- `md check --paths skills/1chat-recall --json`: `54` targets, `0` issues.
- Installed smoke из `/tmp`: оба `chat_capture.py --help` PASS; installed
  Codex lexical Retrieval target-ит `_ops/chat-recall` и вернул holder/topic
  candidates с date/age, не обращаясь к transcript adapter.
- Trigger `When owner speech needs attention.` не менялся; прежнее use/skip/
  near-miss evidence причинно сохраняется.

## Owner and projection parity

- Codex version = tracked owner = installed projection:
  `e866b19d1971f4d869a50d1aa5ec6f5580ce4c934f7e399f909dc4c76b166e7f`.
- Claude version = tracked owner = installed symlink target:
  `35fe050b916505cdfa538210bf403a11a8b82909089ce1af7f5a8417cc814de3`.
- Shared `chat_capture.py`, `chat_digest.py`, `recall_metadata.py` и Capture
  contract побайтно одинаковы; platform delta остаётся в frontmatter, paths и
  explicit transcript adapter.

## Review decisions

- Две разрешённые checker waves были израсходованы на предыдущем candidate;
  новые субагенты по прямому лимиту владельца не запускались. Их semantic
  evidence сохранено только для незатронутых Capture/Retrieval механизмов.
- Opus Advisor независимо поддержал corpus-only ordinary Retrieval и explicit
  owner-only raw Repair. Это мнение, не approval; root подтвердил его contract
  tests и installed smoke.
- Opus-утверждение, что off-domain запрос `борщ` возвращает topic noise,
  отклонено: точный локальный повтор вернул `selection=none`.

## Complexity and residuals

- `SKILL.md`: 11 active units; новый файл или runtime stage не добавлен.
- Снята только неявная доступность raw Repair; explicit maintenance route
  сохранён из-за невосстановимой потери literal provenance при заказанном
  backfill.
- Corpus strict validation остаётся отдельной проблемой: 49 diagnostic records,
  включая duplicate session holders. Она сохранена в
  `_ops/findings/2026-08-31-122109-34372-28894.md` и не исправлялась этой
  установкой.
