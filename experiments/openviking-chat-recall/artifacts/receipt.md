# Wave-1 runtime receipt

Дата: `2026-08-21`.

Итог карточки: `stock acceptance blocked`. Представительный импорт прошёл
через stock server, но stock Compile не создал task из-за несовместимости
bundled VikingBot с единственным опубликованным SDK `0.1.8`. Для проверки
причины выполнен отдельный disposable diagnostic run с shim; его 7 страниц
сохранены в `artifacts/wiki/`, но не считаются доказательством stock
acceptance.

## Scope and source inventory

- Источник: `_ops/chat-recall`, только top-level `*.md`, без `README.md`.
- Фактический count: `182` holder-файла. Плановый текст говорил о 181; plan-файлы
  read-only и не исправлялись.
- Frozen pilot: `6` holders, SHA inventory
  `490171eae7376460a45f18fb947e4d4f6784b35db10aa8146695fc6f0448ec2e`.
- Runtime source URI: `viking://resources/chat-recall-pilot`.
- Источники не изменялись; staging находится в ignored `.runtime/pilot-source`.

Команда инвентаризации:

```bash
uv run --locked --project . python scripts/build_inventory.py \
  --source-dir ../../_ops/chat-recall \
  --inventory artifacts/source-inventory.json \
  --selection artifacts/pilot-selection.json \
  --stage-dir .runtime/pilot-source
```

## Version, license and skill inventory

- Python distribution: `openviking==0.4.16`.
- Upstream tag: `v0.4.16`, commit
  `499995f3ed2e7f551a715179c4053772c51ff819`.
- License from the tag `pyproject.toml` / `LICENSE`: `AGPL-3.0`.
- Resolved SDK: `openviking-sdk==0.1.8`; PyPI metadata exposed no newer
  published release during this run.
- CLI help reports bundled Rust CLI `OpenViking v0.4.17.dev0`, while the
  server health endpoint and Python distribution report `0.4.16`.
- Official Skill source:
  `https://github.com/volcengine/OpenViking/blob/v0.4.16/examples/compile/ov-compile-skills/llm-wiki/SKILL.md`.
- Skill SHA-256:
  `c5e379843a0af6c4574f29ae8fd6637b2b89a0481da63a76472188633f4792de`.
- Runtime Skill URI: `viking://agent/skills/llm-wiki`.
- The context commit `9042a0254f9285aeab1779cc648440a5cf3108e5` exists, but is
  after the pinned tag and was not substituted for the pinned runtime.

Commands:

```bash
uv sync --locked
uv run --locked --project . ov --help
OPENVIKING_PILOT_ROOT="$PWD" OPENVIKING_CONFIG_FILE="$PWD/config/ov.conf" \
  uv run --locked --project . ov doctor --config "$PWD/config/ov.conf"
```

Doctor receipt: all checks passed — config, Python `3.13.13`, native engine,
AGFS, dev auth, local embedding, `openai-codex/gpt-5.4` VLM via codex-cli OAuth,
VikingBot alignment and disk.

`ov --version` itself was not used as a version receipt: the CLI requires a
display-language setting and returned the language setup prompt. No global CLI
setting was written; SDK/HTTP was used for the runtime operations below.

## Stock runtime

Server command:

```bash
OPENVIKING_PILOT_ROOT="$PWD" OPENVIKING_CONFIG_FILE="$PWD/config/ov.conf" \
  uv run --locked --project . openviking-server \
  --config "$PWD/config/ov.conf" --host 127.0.0.1 --port 19331 \
  --with-bot --bot-port 18791
```

Health receipt:

```json
{"status":"ok","healthy":true,"version":"0.4.16","auth_mode":"dev"}
```

Official Skill was uploaded with the SDK and returned `status=success`,
`root_uri=viking://agent/skills/llm-wiki`, `auxiliary_files=0`, and embedding
queue `error_count=0`.

Resource import used the frozen directory and returned a result with
`file_count=6`, six `MarkdownParser` entries, `failed_files=[]`,
`unsupported_files=[]`, and `skipped_files=[]`. The persisted add-resource task
was still marked `running / processing_queue` after the parsed tree became
available; this is recorded as a task-queue caveat, not as a successful terminal
task.

The exact stock Compile request was:

```bash
curl -X POST http://127.0.0.1:19331/bot/v1/compile \
  -H 'content-type: application/json' \
  --data-binary @- <<'JSON'
{
  "from": ["viking://resources/chat-recall-pilot"],
  "to": "viking://resources/chat-recall-wiki",
  "skill": "viking://agent/skills/llm-wiki",
  "reason": "Wave-1 representative pilot only. Compile the six imported immutable chat-recall holders into an evidence-grounded LLM Wiki. Preserve source provenance, use stock English Wiki behavior, cover recurrence/change, chronology, method/process, preference, and boundary/correction signals; do not backfill the corpus or invent an ontology.",
  "runtime_timeout_seconds": 900
}
JSON
```

Stock response: HTTP `400`, code `INVALID_ARGUMENT`, message:

```text
AsyncHTTPClient.get_skill() got an unexpected keyword argument 'include_integrity'
```

Installed SDK signature has no `include_integrity` parameter, while bundled
`vikingbot` calls that keyword. The stock Compile gate therefore remains open
and no stock compile task id exists.

## Disposable diagnostic (not acceptance)

To distinguish the package mismatch from later LLM/runtime behavior, a local
ignored `.runtime/compat/sitecustomize.py` accepted and discarded that one
keyword before delegating to the published SDK. The server was restarted with:

```bash
OPENVIKING_PILOT_ROOT="$PWD" OPENVIKING_CONFIG_FILE="$PWD/config/ov.conf" \
  PYTHONPATH="$PWD/.runtime/compat" \
  uv run --locked --project . openviking-server \
  --config "$PWD/config/ov.conf" --host 127.0.0.1 --port 19331 \
  --with-bot --bot-port 18791
```

This non-stock request was accepted as
`cmp_3e13368f446f4b938f367feaefce419e` and reached `completed` in
`2026-08-21T10:31:11.199848Z`:

```json
{
  "from": ["viking://resources/chat-recall-pilot"],
  "to": "viking://resources/chat-recall-wiki",
  "skill": "viking://agent/skills/llm-wiki",
  "okf_version": "0.1",
  "created": 7,
  "updated": 0,
  "unchanged": 0,
  "page_count": 7,
  "link_count": 0,
  "warnings": []
}
```

The diagnostic tree is:

```text
viking://resources/chat-recall-wiki/
├── index.md
├── analysis/
│   ├── Chat recall pilot chronology and change signals.md
│   └── User preferences and correction patterns in the pilot corpus.md
├── concept/
│   ├── Autonomy boundary in agent execution.md
│   ├── Chat recall capture policy.md
│   └── Session-context retrieval model.md
└── method/
    └── Improving chat-recall retrieval experimentally.md
```

Runtime URI tree is also recorded verbatim in `artifacts/wiki-tree.txt`; the
seven downloaded pages total `30239` bytes under `artifacts/wiki/`.

Проверка `md check --paths README.md --json` прошла без issues. Проверка
`md check --paths artifacts --json` нашла 6 ссылок в diagnostic `index.md`:
OpenViking записал пробелы в относительных ссылках как `%20`, тогда как
локальный checker сопоставляет их с физическими именами файлов без URL
decode. Derived runtime output не переписывался; это отдельный projection
caveat для будущего retrieval/UI audit, не stock acceptance.

## Boundary and remaining gate

- This is not a full backfill and does not alter `_ops/chat-recall`, Graphiti,
  global skills, or plan files.
- The diagnostic pages are evidence of what the agent produced after the shim,
  not a quality verdict and not stock acceptance.
- Full backfill, matched retrieval comparison, Luna Max review and later audit
  remain out of this wave.
- Next required condition: rerun the exact stock Compile path after an upstream
  compatible SDK/bot package is available, without the local shim; only then can
  the pilot runtime gate be considered satisfied.
