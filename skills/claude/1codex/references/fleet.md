# Флот воркеров — Codex пишет файлы ПРОЕКТА

Читай это перед запуском пишущего флота. Контракт волны — `1orchestration`;
ты — оркестратор, здесь только bridge-дельты. Воркеры Codex правят
файлы в guarded shared-worktree `workspace-write` параллельно. (Артефакты «себе,
не в проект» — это исследователь `codex_investigate.py`, не флот.) Default
model/effort закреплён backend-ом (`gpt-5.6-sol` + `xhigh` — дефолт,
см. «Ярус вызова» в `SKILL.md`); фоновый флот — см. «Фон» в `SKILL.md`.

1. **Разрежь работу на file-disjoint задачи** — два воркера не правят один
   файл. Footprint должен быть известен заранее точными путями: не знаешь набор
   файлов → это ещё не задача флота, сперва discovery (исследователь/чтение).
2. Собери JSON-массив: `[{"id","prompt","files":[...]}]`. `prompt` и `files`
   обязательны; `files` — exact file paths, не папочные scopes; `cwd` в задаче
   запрещён; для нового файла добавь `allow_create: true`.
3. Запусти пул:

```bash
B=/Users/triton/Documents/GitHub/agentic-research/experiments/codex-bridge
echo '[{"id":"t1","prompt":"...","files":["a.md"]}]' \
  | $B/.venv/bin/python $B/codex_orchestrate.py --concurrency 4 --project "$PWD"
# большой список — через файл: --tasks tasks.json ; сухой план запуска: --dry-run
# default model/effort: --model gpt-5.6-sol --effort xhigh
# тупая и объёмная правка по файлам: --model gpt-5.6-luna
# long-run: --run-dir "$RUN_DIR" --summary-stdout --heartbeat-sec 120
# проверка после воркеров: --verify "pytest ..."
```

`--concurrency N` = сколько воркеров одновременно (50 задач идут волнами).
Выход — JSON object с `worker_status`, `scope_status`, `verification_status`,
`fully_verified`, `ok`, `run_dir` и результатами воркеров.

**Пока флот идёт** — `codex_progress.py "$RUN_DIR"`: активность помечена id
воркера, пульс несёт `active` и `stalest` (кто молчит дольше всех). Это ответ
на «второй час, и непонятно, движется ли»: видно, какой именно воркер встал и
на каком шаге. По умолчанию скрыто — смотри по подозрению, не по расписанию.

## Контракт (нарушишь — потеряешь правки)

- **File-disjoint enforced.** Backend reject-ит overlap до запуска Codex.
- **Prompt-обещания ⊆ files.** Каждый путь, который prompt задачи называет к
  записи («положи в X», «файл в твоём списке»), проверь в `files` до запуска:
  воркер вне списка писать не может — смысл потеряется молча, а верификатор
  найдёт это кругом позже (реальный случай: протокол вынесли из memo, а его
  новый дом в `files` не положили).
- **Strict backend preflight.** Unknown keys, не-bool `allow_create`, не-string
  `id`, absolute paths, `..`, пустые `files` и overlap падают до запуска Codex.
- **Git/scope guardrails.** Реальный write-run требует git worktree. Если dirty
  files пересекаются с `files`, запуск блокируется; override только осознанно:
  `--allow-dirty-overlap`. Backend fingerprint-ит initial dirty files и после
  воркеров валит `scope_status`, если изменился non-allowlisted файл или `HEAD`.
- **Max-safe permissions.** Default не `full-access`: такой режим может менять
  файлы вне project/git scope, а backend не сможет доказать allowlist. Для v1
  максимум — `workspace-write` внутри проекта + backend guardrails.
- **Postflight scope-check.** Changed files должны входить в union `files`;
  per-worker attribution shared-worktree НЕ доказывает (воркер A может задеть
  файл воркера B — union-чек пройдёт). Кто что правил — устанавливай финальным
  `git diff`.
- **`scope_status=failed` остаётся failure.** Читай `out_of_scope_files`, diff
  и provenance; объяснение «это watcher» не доказывает ownership и не разрешает
  commit. Легитимный deterministic side effect объяви в footprint до следующего
  запуска либо прими отдельным owner-решением после diff.
- **Коммить волну до следующего запуска.** Вотчеры пачкают дерево; dirty
  overlap заблокирует следующий флот, а чистый baseline нужен для честного
  `git diff` атрибуции.
- **Перепроверь сам.** `worker_status=completed` не равно done. Перед доверием к
  результату нужен `--verify`, `git diff`, тесты или профиль 1 по изменениям.
  Самоотчёт воркера («сделал») доказательством не считается.
