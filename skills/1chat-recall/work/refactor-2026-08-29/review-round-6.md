# Review round 6 — русский runtime и установка

Дата: 2026-08-29.

## Решения владельца

- Удалено прежнее решение делать весь `1chat-recall` английским; действующая
  граница — русские `SKILL.md` и references, короткий trigger-only
  `description` по-английски:
  `_ops/chat-recall/2026-08-29-150002-codex-01a04cf3.md:22` и
  `_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md:19-20`.
- Сначала поведение выражается через `Цели` и `Уникальный контекст`; procedure
  хранит только невыводимую механику, интерфейсы, safety, критичный порядок и
  acceptance: `_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md:21`.

## Commander-intent pass

В `Цели` и `Уникальный контекст` перенесены:

- гейт самостоятельной существенной реплики;
- pure assent против содержательного `selection`;
- различие `quote` / `selection` / `note` / `raw`;
- модель «датированное свидетельство, не текущая правда»;
- причина выбирать тему и поисковые ключи именно в момент Capture.

Из Capture и Repair удалены повторы этих правил. Оставлены hard lines, которые
нельзя безопасно вывести: полный read `topics.md`, exact CLI и schema fields,
timestamp/provenance, `supersedes`/`contested`, terminal receipts, backups,
strict validation и integrity proof.

## Закрытые дефекты

- Repair завершает missing-session-context случай квитанцией
  `capture-needed`; следующий Capture выбирается только body-router-ом.
- Codex Repair `read/search/show` передаёт `--include-current-turn`.
- Claude Repair передаёт `--all --include-current-turn`.
- Каждый Claude reference command имеет self-contained fallback
  `${CLAUDE_SKILL_DIR:-$HOME/.claude/skills/1chat-recall}`.
- Старые doc-characterization tests перенесены с длинного body к настоящим
  владельцам инвариантов: body, Capture, Retrieval и Repair.

## Evidence точной версии

- `quick_validate.py`: Codex и Claude — valid до и после установки.
- YAML и все ссылки обоих candidate-пакетов — valid.
- Trigger — наблюдение чистого исполнителя, не deterministic machine-check:
  `Запомни это правило для следующих решений` → `1chat-recall`;
  `Да, продолжай выполнять текущую команду` → skip;
  `Найди ошибку, которую я видел на экране` → `chronicle` near-miss.
- Воспроизводимый clean corpus остаётся в
  `/tmp/chat-recall-final-EbIeLX`. Capture helper записал непрозрачное «да» как
  `selection` после полного чтения двух границ тем:

  ```text
  2026-08-29-183000-codex-33333333.md:15
  kind: selection · topic: skill-trigger-routing
  context-note: вариант A; consequential owner speech; candidate 1chat-recall;
  trigger routing; future decisions
  ```

  Проверка обычного Retrieval воспроизводится так:

  ```bash
  uv run --locked --script skills/codex/1chat-recall/scripts/chat_digest.py \
    /tmp/chat-recall-final-EbIeLX/_ops/chat-recall \
    --query 'activate skill for consequential owner speech affecting future decisions' \
    --json
  ```

  Наблюдаемый результат: `matched=1`, `returned=1`, `truncated=false`,
  `retrieval=hybrid`, точный адрес
  `2026-08-29-183000-codex-33333333.md:15`.
- Repair-fixture:
  `/tmp/chat-recall-final-EbIeLX/repair-fixture/_ops/chat-recall/2026-08-29-184000-codex-55555555.md:14`.
  В holder отсутствует только `session-context`; strict validator возвращает
  `OK: 1 записей без diagnostics`. По installed Repair это терминальная
  квитанция
  `capture-needed · 2026-08-29-184000-codex-55555555.md:14 · missing session-context`;
  installed body затем маршрутизирует Capture без reference-цепочки.
- Claude fallback проверен literal command с unset-переменной:

  ```bash
  env -u CLAUDE_SKILL_DIR zsh -c '
  root="${CLAUDE_SKILL_DIR:-$HOME/.claude/skills/1chat-recall}"
  python3 "$root/scripts/chat_recall.py" \
    --session-id ffffffff-ffff-4fff-8fff-ffffffffffff \
    --all --include-current-turn
  '
  ```

  Аргументы прошли parser; единственный результат — ожидаемый lookup-error:
  `expected one transcript ... found 0`.
- Независимый acceptance-аудит exact candidate: pass, blockers none.
  Техническая критика: `implementation_route_holds` после исправления
  transcript flags и Claude fallback. Эти вердикты — консультации; evidence
  выше и checks ниже проверяются отдельно.
- Полные suites: Codex `101 passed, 12 subtests passed`; Claude
  `100 passed, 12 subtests passed`.
- Functional manifest исключает только `.pytest_cache`, `__pycache__`, `*.pyc`
  и `.DS_Store`. Для каждого root он построен одной командой:

  ```bash
  (cd "$root" && find . -type f \
    ! -path '*/.pytest_cache/*' ! -path '*/__pycache__/*' \
    ! -name '*.pyc' ! -name '.DS_Store' -print0 | sort -z | \
    xargs -0 shasum -a 256) | shasum -a 256
  ```

  Functional manifest SHA-256:
  - Codex tracked/live:
    `725994fec249c272e4ca482e12e54bb71bb2fc259e62229029f275cba7790f56`;
  - Claude tracked/live:
    `6d71ee6e24a3fe6133c37918f82572daafc12f52a5e36c764951e71ee3c73162`.

## Честный остаток

Консервативный atomic active-set остаётся выше ориентира 20. Он не стал
release blocker: владелец запретил вредное микродробление, свежая панель не
нашла причин открывать topology заново, а matched clean-runs не показали потери
Capture, Retrieval или Repair. Если будущий clean-run свяжет перегрузку с
конкретно пропущенным обязательством, контракт пересматривается по этому
сбою, а не по счётчику сам по себе.
