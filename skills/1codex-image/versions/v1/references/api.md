# Прямой вызов API

Нужен, когда скрипт OpenAI не пускает параметр: у моделей 2.5 он разрешает
только размеры `1024x1024`, `1536x1024`, `1024x1536`, `auto` и качество до
`high`. Сам API у 2.5 принимает больше. Рецепты проверены 2026-10-30.

## Что принимает API

| Параметр | Значения |
|---|---|
| `size` | `auto` или `ШxВ`: обе стороны кратны 16, длинная ≤ 3840, соотношение ≤ 3:1, от 655 360 до 8 294 400 пикселей; выше 2560×1440 OpenAI называет экспериментальным |
| `quality` | `low`, `medium`, `high`, `auto`; у 2.5 ещё `xhigh`, `max` |
| `background` | `transparent` (только `png`/`webp`), `opaque`, `auto` |
| `output_format` | `png`, `jpeg`, `webp`; `output_compression` 0–100 — только `jpeg`/`webp` |
| `image[]` | до 16 входных картинок, каждая < 50 МБ |
| `mask` | PNG с альфа-каналом того же размера, что первая картинка; подсказка, а не трафарет |
| `markup` | только 2.5: прозрачный PNG с пометками поверх первой картинки, вместе с `mask` нельзя |
| `n` | 1–10 вариантов одного промпта |

`1920x1080` не делится на 16: проси `1920x1088` и обрежь, если нужен ровно Full HD.

## Генерация

```bash
K=$(cat ~/.config/openai/api-key)
jq -n --rawfile p "${DIR:?}/${NAME:?}.prompt.md" \
  '{model:"gpt-image-2.5-sunburst-2026-09-08", prompt:$p, size:"1920x1088", quality:"xhigh"}' |
  curl -s https://api.openai.com/v1/images/generations \
    -H "Authorization: Bearer $K" -H "Content-Type: application/json" -d @- > "${DIR:?}/${NAME:?}.json"
J="${DIR:?}/${NAME:?}.json"
if jq -e '.data[0].b64_json' "$J" >/dev/null; then
  jq -r '.data[0].b64_json' "$J" | base64 -d > "${DIR:?}/${NAME:?}.png"
  jq -c 'del(.data)' "$J" && rm "$J"
else
  jq -c .error "$J"
fi
```

Прозрачность — добавь в объект `background:"transparent"`.

## Правка и референсы

```bash
K=$(cat ~/.config/openai/api-key)
curl -s https://api.openai.com/v1/images/edits -H "Authorization: Bearer $K" \
  -F model=gpt-image-2.5-sunburst-2026-09-08 \
  -F "image[]=@base.png" -F "image[]=@reference.png" \
  -F size=2048x1152 -F quality=high \
  -F "prompt=<${DIR:?}/${NAME:?}.prompt.md" > "${DIR:?}/${NAME:?}.json"
```

Порядок `image[]` — это Image 1, Image 2 в промпте. Ответ разбирай так же,
как при генерации: при ошибке PNG не появится, а выведется `.error`.

Ответ несёт `usage` — по нему считай цену точно:
`output_tokens` × $30 + входные `image_tokens` × $8 + `text_tokens` × $5
за миллион.
