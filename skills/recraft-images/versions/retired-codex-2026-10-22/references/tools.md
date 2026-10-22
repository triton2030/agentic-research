# Recraft MCP: выбор инструмента

Проверено 2026-08-13 по живой схеме нового Codex-процесса. Опубликованная
[MCP-страница Recraft](https://www.recraft.ai/docs/mcp-reference/tools) пока
перечисляет 9 базовых операций, а подключённый remote MCP открывает 21.
Параметры и enum бери из живой схемы; назначение и совместимость сверяй с
официальной документацией.

## Быстрый выбор

| Задача | Tool | Главные входы |
| --- | --- | --- |
| Из текста в изображение | `generate_image` | `prompt`; опционально `image_size`, `model`, `n` |
| Свободное редактирование | `image_edit` | `input_image_urls`, `prompt` |
| Ремикс с контролем сходства | `image_to_image` | `input_image_url`, `prompt`, `strength` |
| Вариации без нового prompt | `variate_image` | `input_image_url`, `image_size`; опционально `n` |
| Удалить фон | `remove_background` | `input_image_url` |
| Полностью заменить фон | `replace_background` | `input_image_url`, `prompt` |
| Сгенерировать фон в маске | `generate_background` | image URL, mask URL, `prompt` |
| Перерисовать область маски | `inpaint_image` | image URL, mask URL, `prompt` |
| Стереть объект/область | `erase_region` | image URL, mask URL |
| Увеличить без смены содержания | `crisp_upscale` | `input_image_url` |
| Увеличить с дорисовкой деталей | `creative_upscale` | `input_image_url` |
| Raster → editable vector | `vectorize_image` | `input_image_url` |

`crisp_upscale` сохраняет содержание; `creative_upscale` регенерирует детали и
может изменить мелкие формы. Для точного товара, текста или лица предпочитай
crisp; creative — только когда новая детализация желательна.

## Design Agent

- `call_agent(message, chat_id?, input_image_urls?)` — пошаговый чат с Design
  Agent для согласованного набора digital-product assets. Первый ответ может
  вернуть `chat_id`; передавай его в продолжениях того же набора.
- Это не замена точечному `generate_image`: используй, когда владелец просит
  систему/набор активов или прямо Design Agent.
- Каждый ход, создавший asset, считается image-producing operation: сохрани
  output и затем вызови `get_user`.

## Custom styles

| Tool | Назначение |
| --- | --- |
| `create_style` | Создать стиль из URL/base64 референсов и типа изображения |
| `list_styles` | Получить список style ids текущего пользователя |
| `get_style` | Прочитать один стиль по `style_id` |
| `delete_style` | Удалить стиль по точному id; только явная просьба |

Типы `create_style`: `realistic_image`, `digital_illustration`,
`vector_illustration`, `icon`. Официальная
[таблица styles](https://www.recraft.ai/docs/api-reference/styles) говорит, что
V4/V4.1, включая Pro/Utility/Vector, styles не поддерживают. Для применения
custom style используй только совместимую V2/V3 модель и тот же model/base type,
с которым стиль создан.

## Служебные и read-only tools

| Tool | Назначение |
| --- | --- |
| `request_upload_url` | Временный URL для загрузки локального PNG/JPEG/WEBP |
| `suggest_model` | Рекомендация модели по текстовому описанию задачи |
| `get_user` | Аккаунт и живой остаток кредитов |
| `subscription_plans` | Доступные планы, refill и pricing identifiers |

`suggest_model` не отменяет owner-default `recraftv4_1`: вызывай его, только
если владелец попросил подобрать модель или текущая задача прямо требует иной
режим. `subscription_plans` ничего не покупает; покупка/смена плана не входит в
этот skill.

## Живая model enum на 2026-08-13

`generate_image` сейчас принимает:

```text
recraftv4_1_pro
recraftv4_1
recraftv3
recraftv2
nano_banana_pro
nano_banana_2
gemini_25_flash_image
flux1_kontext_pro
flux1_kontext_max
flux2_pro
gpt_image_1_high
gpt_image_1_medium
bytedance-seedreamv4
bytedance_seedreamv5_pro
qwen_image
```

Официальное семейство V4.1 также включает Utility и Vector варианты, но их id
нет в текущей live enum. Не передавай предполагаемый id. Сначала перечитай
живую схему: remote MCP может обновиться.

Поддерживаемые live `image_size`: `1:1`, `2:1`, `1:2`, `3:2`, `2:3`, `4:3`,
`3:4`, `5:4`, `4:5`, `6:10`, `14:10`, `10:14`, `16:9`, `9:16`.

## Источники

- [Recraft MCP tools](https://www.recraft.ai/docs/mcp-reference/tools)
- [Recraft V4.1 family](https://www.recraft.ai/docs/recraft-models/recraft-v4-1)
- [Recraft API styles](https://www.recraft.ai/docs/api-reference/styles)
- Live Recraft MCP schema probe, fresh Codex process, 2026-08-13.
