# 1md-search — Setup И Runtime Recovery

Открывай только при `md` spawn failure, missing dependency/key или backend
error. Обычный search route не перечитывает setup.

## Active Runtime

Сначала проверь live owner:

```bash
command -v md
md --version
md ping --json
```

`md` обычно установлен как uv-managed CLI. Не запускай `python3 md ...`:
это обходит console entry point и создаёт import/dependency drift.

Если active binary принадлежит editable checkout, переустановка/обновление —
отдельная tooling задача. Не выполняй install только потому, что search вернул
no-hit.

## Embedding Credential

Semantic commands используют configured OpenAI-compatible embedding endpoint.
При missing-key error проверяй **наличие**, никогда не печатай значение:

```bash
test -n "${OPENROUTER_API_KEY:-}${MD_EMBEDDING_API_KEY:-}" \
  && echo "embedding key present"
test -f .openrouter.key && echo "cwd key present"
test -f ~/.openrouter.key && echo "home key present"
```

Следуй lookup paths из live error. Не копируй secret между projects молча, не
логируй его и не вставляй в prompt/tool output.

## Backend Overrides

Endpoint/model могут приходить из environment, command flags или stored index
metadata. Existing corpus обычно сохраняет stored model; explicit model override
может потребовать rebuild.

Перед изменением endpoint/model проверь live help:

```bash
md index --help
md search --help
```

Backend/network failure — runtime gap. Он не доказывает пустоту Markdown
corpus; filesystem reading остаётся независимым.
