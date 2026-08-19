# Recovering recall coverage

Открывай только когда обычный Retrieval дал пустой, чрезмерно широкий,
конфликтующий или усечённый route либо hybrid-поиск недоступен. Этот файл даёт
bounded recovery и coverage packet; применение owner evidence остаётся в
`SKILL.md`.

## Recovery

Сначала прочитай diagnostics выдачи: `matched`, `returned`, `truncated`,
`retrieval` и уникальные holder files. Затем используй только варианты,
способные изменить candidate set:

1. Переформулируй тот же claim короткой естественной фразой о предмете, не об
   имени артефакта.
2. Сделай максимум один lexical-повтор тремя-четырьмя различающими корнями.
   Русские основы ставь отдельно со `*` после устойчивой части:
   `корнев* папочн* инструкц* ссылк*`; точные имена оставляй целиком.
3. Широкую тему разложи на материальные фасеты. Лексику следующего фасета бери
   из snippets и `session-context`; хотя бы один фасет формулируй языком задачи.
   Два фасета подряд без новых holder-ов — наблюдаемое насыщение.
4. `matched` больше `returned` втрое и более означает, что route слишком широк:
   сузь claim либо осознанно подними `--limit`.

Если локальная модель не подготовлена, один раз выполни `--prepare`. Когда
hybrid недоступен, `--lexical` сохраняет file-level BM25 и lexical
context-gate. `--timeline` разворачивает записи выбранных holder-ов.

```bash
ROOT="${CLAUDE_SKILL_DIR}"

uv run --locked --script "$ROOT/scripts/chat_digest.py" \
  _ops/chat-recall --query "<claim или корни>" --lexical --json
```

Верни в Retrieval body: названные проверенные routes, уникальные holder files,
спрошенные фасеты, truncation status и unresolved gaps. Empty recovery — тоже
результат; новых вариантов запроса без изменяемого candidate set не добавляй.

## Structural validation

```bash
python3 "$ROOT/scripts/chat_digest.py" \
  "$PWD/_ops/chat-recall" --check --strict
```

Validator проверяет структуру corpus и diagnostics, но не применимость позиции.
