# OpenAI Image API: официальные факты на 2026-10-30

Все страницы открыты 2026-10-30. Markdown-версии страниц docs получены добавлением `.md` к URL. Сокращения источников:

- **[guide]** https://developers.openai.com/api/docs/guides/image-generation
- **[tool]** https://developers.openai.com/api/docs/guides/tools-image-generation
- **[prompting]** https://developers.openai.com/api/docs/guides/image-prompting
- **[ref-gen]** https://developers.openai.com/api/reference/resources/images/methods/generate
- **[ref-edit]** https://developers.openai.com/api/reference/resources/images/methods/edit
- **[ref-resp]** https://developers.openai.com/api/reference/resources/responses/methods/create (схема `ImageGeneration`)
- **[pricing]** https://developers.openai.com/api/docs/pricing (раздел Image generation models)
- **[changelog]** https://developers.openai.com/api/docs/changelog
- **[deprec]** https://developers.openai.com/api/docs/deprecations
- **[m-flare]**, **[m-sun]**, **[m-2]**: https://developers.openai.com/api/docs/models/gpt-image-2.5-flare, `.../gpt-image-2.5-sunburst`, `.../gpt-image-2`
- **[calc-js]** JS калькулятора токенов на странице [guide]: `/_astro/GptImageTokenCalculator.react.BteB_hCX.js`

## 1. gpt-image-2.5-flare и gpt-image-2.5-sunburst

Документированы официально. Выпущены 2026-09-08 для Image API и инструмента `image_generation` в Responses [changelog, запись Sep 8].

| | Flare | Sunburst |
| --- | --- | --- |
| Позиция | «small model, optimized for speed», качество сравнимо с gpt-image-2 [prompting] | «base model, optimized for quality», качество выше gpt-image-2 [prompting] |
| Описание на карточке | «fastest model for high-quality, everyday image generation» [m-flare] | «Our most capable model for image generation and editing» [m-sun] |
| Когда брать | скорость важнее; GPT Image 2 уже устраивает по качеству [prompting] | сложный случай, где GPT Image 2 не дотягивает; точность правок [prompting], [guide] |
| Snapshot | `gpt-image-2.5-flare-2026-09-08` | `gpt-image-2.5-sunburst-2026-09-08` |

Общее для обоих:

- Оба улучшены в точных правках и сохранении объекта [prompting].
- `quality`: `low`, `medium`, `high`, `xhigh`, `max`, `auto` (по умолчанию `auto`). `xhigh` и `max` есть только у 2.5 [guide], [ref-gen].
- `background`: `transparent` поддержан полностью, не preview [ref-gen], [ref-edit], [prompting]: «Both models support image generation, editing, and transparent backgrounds».
- Размеры: как у gpt-image-2, см. раздел 2 [guide].
- Endpoints: `v1/images/generations`, `v1/images/edits`, `v1/batch`; в Responses — только как `model` инструмента `image_generation`, не top-level (карточки ставят Responses в «not supported») [m-flare], [m-sun], [tool].
- Rate limits одинаковы с gpt-image-2: Build 250k TPM / 20 IPM, Launch 3M / 150, Grow 8M / 250 [m-flare], [m-sun], [m-2].
- Новый параметр edits `markup`: прозрачный PNG поверх первого изображения, тех же размеров; несовместим с `mask`. В справке: «Supports GPT Image 2.5 and 2.6» [ref-edit]. Модель 2.6 нигде больше не найдена.
- Скорость: OpenAI не публикует фиксированный выигрыш; велит мерить на своей нагрузке [prompting]. Цифра «до 50% меньше задержка» встречается только у третьих сторон (apiyi, CometAPI). В первоисточниках не найдена.
- Рекомендуемый порядок выбора [prompting]: сначала добиться качества на Sunburst, затем проверить Flare на тех же промптах; брать Flare, если качество держится и задержка падает. `xhigh`/`max` — только если они закрывают невыполненное требование к качеству.

## 2. Параметры gpt-image-2 (и где 2.5 отличается)

| Параметр | gpt-image-2 | 2.5 Flare / Sunburst | Источник |
| --- | --- | --- | --- |
| `size` | `auto` (по умолч.) или `WxH`: обе стороны кратны 16, макс. сторона ≤ 3840, соотношение ≤ 3:1, пикселей 655 360…8 294 400; выше `2560x1440` — experimental | то же | [guide] (Earlier GPT Image models), [ref-gen] |
| Популярные размеры | 1024², 1536x1024, 1024x1536, 2048², 2048x1152, 3840x2160, 2160x3840 | те же | [guide], [prompting] |
| `quality` | `low`, `medium`, `high`, `auto` | + `xhigh`, `max` | [guide], [ref-gen] |
| `background=transparent` | **поддержан в preview с 2026-08-20** (Images API и Responses tool); только `png`/`webp` | поддержан | [changelog, Aug 20], [ref-gen], [tool], [prompting] |
| `output_format` | `png` (по умолч.), `jpeg`, `webp`; `jpeg` быстрее `png` | то же | [guide] |
| `output_compression` | 0–100, только `jpeg`/`webp` | то же | [guide], [ref-edit] |
| `moderation` | `auto` (по умолч.) или `low` | то же | [guide] |
| `n` | 1–10 | то же | [ref-gen], [ref-edit] |
| Входные изображения (edits) | до 16 (`maxItems: 16`) | то же | [ref-edit] |
| `prompt` | до 32 000 знаков | то же | [ref-gen], [ref-edit] |
| `input_fidelity` | не передавать: всегда high, API не даёт менять; входные токены дороже | в справке упомянут только для 1.5 и 1-mini | [guide], [ref-edit] |
| `partial_images` | 0–3; каждый частичный кадр +100 output-токенов; финал может прийти раньше | то же | [guide], [ref-edit] |
| `response_format`, `style` | не поддержаны (legacy DALL·E); ответ всегда base64 | то же | [ref-gen] |
| `safety_identifier` | рекомендован, ≤ 128 знаков, хешированный; `user` устарел | то же | [guide] |

Маска [guide]:

- Изображение и маска одного формата и размера, каждое < 50 МБ; маска обязана иметь альфа-канал.
- При нескольких входных изображениях маска применяется к первому.
- Маска — подсказка, а не трафарет: модель может не повторить её форму точно.
- В Responses маска передаётся как `input_image_mask` (`file_id` или `image_url`) [ref-resp].

Рамка опроса «gpt-image-2 не поддерживает transparent» **опровергнута**. Она верна только для состояния до 2026-08-20. Локальный `~/.codex/skills/.system/imagegen/scripts/image_gen.py` (строки 194–198) жёстко запрещает `transparent` для `gpt-image-2` и отправляет на `gpt-image-1.5`. Этот запрет устарел.

Ограничения [guide]: сложный промпт до 2 минут; текст и точная раскладка ещё бывают неточны; персонажи и бренд дрейфуют между генерациями.

## 3. Images API или Responses `image_generation` для итеративных правок

| | Images API (`/v1/images/generations`, `/edits`) | Responses + tool `image_generation` |
| --- | --- | --- |
| Модель | `model` = модель изображения напрямую. generations: модель обязательна; edits: по умолчанию `gpt-image-2.5-sunburst` | top-level — mainline (`gpt-5.x`, `gpt-6-*`), модель изображения — в `tools[].model`; по умолчанию у инструмента `gpt-image-2` |
| Многоходовость | нет: каждый шаг заново передаёт картинку в edits | `previous_response_id` или элемент `{"type":"image_generation_call","id":...}` во входе |
| Входы | `images[]`: `file_id` или `image_url` (URL/base64 data URL), до 16 | URL, base64 data URL, `file_id` |
| `action` | — | `auto` (по умолч.) / `generate` / `edit`; `edit` без картинки в контексте — ошибка |
| Промпт | идёт как есть | mainline переписывает его; итог в `revised_prompt` |
| Цена | только токены изображения | + токены mainline; **cached input** для GPT Image 2 и 2.5 действует **только** здесь, не в Images API и не в edits |
| Стриминг | да, `partial_images` 0–3 | да |

Источники: [guide] (Overview, Multi-turn, Cached input pricing), [tool], [ref-edit], [ref-resp].

Что рекомендует OpenAI [guide]: Images API — для одного изображения из одного промпта; Responses — для разговорных, редактируемых сценариев. При этом [prompting] для итераций предлагает другой ход: передать прошлый результат как вход следующей правки, просить одно изменение и повторять список того, что сохранить. Это работает и через edits.

Для скила:

- edits проще, детерминированнее (промпт не переписывается) и не требует mainline.
- Responses дешевле на длинной серии правок за счёт кеша, но добавляет токены mainline и переписывание промпта.
- Для строго неизменной области OpenAI советует композитить одобренную правку в оригинал, а не полагаться на промпт [prompting].
- Совет [tool]: просить «edit the first image by adding this element from the second image», а не «combine/merge».

## 4. Цены

Токены, $ за 1M [pricing]:

| Модель | Image in | Image cached | Image out | Text in | Text cached | Batch: image in / out |
| --- | --- | --- | --- | --- | --- | --- |
| gpt-image-2.5-sunburst | 8.00 | 2.00 | 30.00 | 5.00 | 1.25 | 4.00 / 15.00 |
| gpt-image-2.5-flare | 8.00 | 2.00 | 30.00 | 5.00 | 1.25 | 4.00 / 15.00 |
| gpt-image-2 | 8.00 | 2.00 | 30.00 | 5.00 | 1.25 | 4.00 / 15.00 |
| gpt-image-1.5 | 8.00 | 2.00 | 32.00 | 5.00 | 1.25 | 4.00 / 16.00 |
| chatgpt-image-latest | 8.00 | 2.00 | 32.00 | 5.00 | 1.25 | 4.00 / 16.00 |
| gpt-image-1-mini | 2.50 | 0.25 | 8.00 | 2.00 | 0.20 | 1.25 / 4.00 |

Цена за картинку gpt-image-2, только output, опубликованная таблица [guide] (Calculating costs):

| quality | 1024x1024 | 1024x1536 | 1536x1024 |
| --- | --- | --- | --- |
| low | $0.006 | $0.005 | $0.005 |
| medium | $0.053 | $0.041 | $0.041 |
| high | $0.211 | $0.165 | $0.165 |

Для 2.5 OpenAI таблицы за картинку не публикует. Есть только калькулятор, общий для «GPT Image 2.5 (Sunburst and Flare)». Ниже — вывод из формулы [calc-js] при $30/1M. Формула воспроизводит таблицу gpt-image-2 выше; это мой расчёт, а не опубликованная цена.

| quality (2.5) | 1024² | 1536x1024 / 1024x1536 | 2048² | 3840x2160 |
| --- | --- | --- | --- | --- |
| low | 196 ток. ≈ $0.006 | 158 ≈ $0.005 | 397 ≈ $0.012 | 371 ≈ $0.011 |
| medium | 439 ≈ $0.013 | 343 ≈ $0.010 | 892 ≈ $0.027 | 865 ≈ $0.026 |
| high | 1756 ≈ $0.053 | 1372 ≈ $0.041 | 3568 ≈ $0.107 | 3336 ≈ $0.100 |
| xhigh | 3122 ≈ $0.094 | 2459 ≈ $0.074 | 6343 ≈ $0.190 | 5930 ≈ $0.178 |
| max | 7024 ≈ $0.211 | 5488 ≈ $0.165 | 14272 ≈ $0.428 | 13342 ≈ $0.400 |

- По формуле `high` у 2.5 стоит как `medium` у gpt-image-2, `medium` у 2.5 — примерно вчетверо дешевле, а `max` у 2.5 равен `high` у gpt-image-2. Калькулятор даёт базу на квадрат: gpt-image-2 low/medium/high = 16/48/96; 2.5 low/medium/high/xhigh/max = 16/24/48/64/96.
- Противоречие: [guide] предупреждает, что расход токенов при равных ставках «can differ by model and quality setting» и что одна метка quality не значит одинакового качества [prompting]. Калькулятор же не различает Flare и Sunburst. Реальный расход смотреть в `usage` ответа.
- Входные токены и цена правок с референсами здесь не учтены. gpt-image-2 всегда читает вход в high fidelity, поэтому edits с референсами дороже [guide].

## 5. Официальное руководство по промптам

Действующее — **«GPT Image 2.5 prompting guide»** [prompting]: примеры в нём сделаны на Flare и Sunburst. Cookbook-версия для gpt-image-2 (https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide) помечена как архивная: «This recipe is archived and may reference outdated models». В [prompting] есть вкладка «GPT Image 2 reference» со ссылкой на закреплённый ноутбук.

Правила [prompting] (Prompting fundamentals, пересказ):

- **Структура:** назвать предмет и назначение (фото товара, реклама, диаграмма), композицию, формат, расстановку. Сложное — разделами «scene, subject, details, constraints».
- **Формат:** короткий текст, абзацы, JSON-подобный вид и теги равноценны. Брать тот, который легче читать и править; особый синтаксис не нужен.
- **Длина:** длинные промпты работают, но отлаживать легче с чистой базы и с правками по одному изменению (cookbook-версия).
- **Стиль и детали:** материалы, свет, цвет, медиум. Для фотореализма прямо писать «photorealistic» или «real photograph». Параметры камеры — намёк на вид, а не физика.
- **Люди:** кадрирование тела, масштаб, взгляд, взаимодействие с предметами.
- **Текст:** нужные слова в кавычках, место и типографика. Редкие слова — по буквам. Просить «no extra text» и указывать, сколько раз текст должен появиться. Мелкий или плотный текст — `medium`/`high`; слайды и графики — `high`.
- **Правки с инвариантами:** «change only X» плюс список того, что сохранить (идентичность, геометрия, раскладка, свет, подписи). При точечной правке отдельно назвать насыщенность, контраст, стрелки, ракурс и окружение. Список сохранения повторять на каждой итерации. Пиксельную неизменность даёт только композитинг в оригинал.
- **Несколько референсов:** каждому вход — номер и роль (subject, style, clothing, background), плюс что куда переносится.
- **UI-макеты:** описывать продукт так, будто он уже выпущен: раскладка, иерархия, отступы, реальные элементы. Без языка концепт-арта.
- **Прозрачность:** `background="transparent"` в API и изолированный объект в промпте. Только PNG или WebP; для PNG не передавать `output_compression`. Исключить фон, подложку, шахматку и тень; нарисованная шахматка — не прозрачность. В последующих правках повторять «preserve the transparent background». Проверять альфа-канал декодированного файла: волосы, стекло, тени, края. Не конвертировать RGBA в RGB (cookbook).
- **Проверка результата:** текст точен; объект и подписи целы; изменено только запрошенное; прозрачность — настоящий альфа-канал.

Примеры промптов из [prompting] (дословно):

**Текст в изображении** (`1024x1536`, `medium`):

```text
Give me a cool in culture ad / fashion shot for a brand called Thread.
It's a hip young street brand. The ad shows a group of friends hanging out together with the tagline "Yours to Create."
Make it feel like a polished campaign image for a youth streetwear audience: stylish, contemporary, energetic, and tasteful.
Use clean composition, strong color direction, natural poses, and premium fashion photography cues.
Render the tagline exactly once, clearly and legibly, integrated into the ad layout.
No extra text, no watermarks, no unrelated logos.
```

**UI-макет** (`1024x1536`, `medium`):

```text
Create a realistic mobile app UI mockup for a local farmers market.
Show today’s market with a simple header, a short list of vendors with small photos and categories, a small “Today’s specials” section, and basic information for location and hours.
Design it to be practical, and easy to use. White background, subtle natural accent colors, clear typography, and minimal decoration.
It should look like a real, well-designed, beautiful app for a small local market.
Place the UI mockup in an iPhone frame.
```

**Правка с инвариантом:**

```text
Translate the text in the infographic to Spanish. Do not change any other aspect of the image.
```

```text
Remove the flower from man's hand. Do not change anything else.
```

**Несколько референсов** (сцена — image 1, собака — image 2):

```text
Place the dog from the second image into the setting of image 1, right next to the woman, use the same style of lighting, composition and background. Do not change anything else.
```

**Прозрачная вырезка** (edit, `1024x1536`, `medium`, `background="transparent"`, `output_format="png"`):

```text
Extract the product from the input image and isolate it on a fully transparent background.
Output: centered product, crisp silhouette, no halos/fringing.
Preserve product geometry and label legibility exactly.
Add only light polishing. Do not add a solid backdrop, checkerboard, scenery, or shadow.
Do not restyle the product; remove the background and preserve clean alpha transparency.
```

**Прозрачный логотип** (`background="transparent"`, `png`), хвост промпта:

```text
Fully transparent background. Deliver a single centered logo with generous padding, clean alpha edges, and no solid backdrop, scenery, checkerboard, or watermark.
```

**Итерация по одному условию** (прошлый результат подаётся как вход):

```text
Make it look like a winter evening with snowfall.
```

Отдельный рецепт прозрачных ассетов (https://developers.openai.com/cookbook/examples/multimodal/transparent-image-assets-for-campaigns-and-presentations): `gpt-image-2.5-flare` с `quality="high"`, после генерации — программная проверка альфа-канала (Pillow). Хвост его промптов: «Output an isolated object on actual fully transparent alpha; no backdrop, no rectangle, no plinth, no cast shadow…».

## 6. Скил `imagegen` в GitHub и его установка

- Опубликован в https://github.com/openai/skills по пути `skills/.system/imagegen/` (`SKILL.md`, `scripts/image_gen.py`, `references/{cli,codex-network,image-api,prompting,sample-prompts}.md`). Последний коммит по этому пути — `e6afb0d7`, 2026-04-15 (проверено `gh api`).
- **Репозиторий объявлен устаревшим** (коммит `778b0e61`, 2026-06-22). README отсылает к https://github.com/openai/plugins; в нём скила `imagegen` нет (проверено деревом файлов 2026-10-30).
- Маршрут установки по README: `.system`-скилы ставятся автоматически с последней версией Codex; curated и experimental — через `$skill-installer` внутри Codex. Маршрута для агентов вне Codex (в том числе `npx skills add openai/skills -s imagegen`) OpenAI не описывает. Сам `npx skills` к OpenAI не относится, и его работа с этим репо не проверена.
- **Версии расходятся:**

| | GitHub `openai/skills` (2026-04-15) | Локальная копия Codex (файлы от 2026-10-24) | Документация (2026-10-30) |
| --- | --- | --- | --- |
| `DEFAULT_MODEL` | `gpt-image-1.5` | `gpt-image-2` | — |
| transparent у gpt-image-2 | не запрещён | запрещён в коде, отправляет на 1.5 | preview с 2026-08-20 |
| `remove_chroma_key.py` | нет | есть | — |
| `xhigh`/`max` | нет | нет (`ALLOWED_QUALITIES` = low/medium/high/auto) | есть у 2.5 |
| Размеры 2.5 | — | для любой модели, кроме ровно `gpt-image-2`, разрешены только 1024², 1536x1024, 1024x1536, auto | 2.5 принимает произвольные `WxH` |

  Значит, локальный `image_gen.py` формально пропустит `--model gpt-image-2.5-sunburst --background transparent`, но без `xhigh`/`max` и без нестандартных размеров. Snapshot `gpt-image-2-2026-04-21` минует его проверки gpt-image-2 (сравнение по точной строке).
- Официальная альтернатива скрипту — **OpenAI CLI** на Go (https://developers.openai.com/api/docs/libraries/openai-cli): `brew install openai/tools/openai`, последний релиз `v1.46.0` от 2026-10-29 (`gh api repos/openai/openai-cli/releases/latest`). Команды `openai images generate|edit`; своего `--output` нет, base64 разбирается через `--transform 'data.0.b64_json' | base64 --decode`. Документ подтверждает transparent у gpt-image-2 в preview.

## Сроки моделей из GET /v1/models владельца

| Модель | Статус | Источник |
| --- | --- | --- |
| `gpt-image-1` | **выключена 2026-10-23**, замена — 2.5 Sunburst/Flare (в `/v1/models` может ещё значиться) | [deprec], [ref-gen] |
| `gpt-image-1.5`, `gpt-image-1-mini`, `chatgpt-image-latest` | выключение 2026-12-01 | [deprec] (2026-06-02: GPT Image model deprecations) |
| `gpt-image-2` | живая, объявлений о выключении не найдено; в [guide] вынесена в «Earlier GPT Image models» | [guide], [deprec] |
| `gpt-image-2.5-flare`, `gpt-image-2.5-sunburst` | текущие рекомендуемые; для новых интеграций OpenAI велит брать 2.5 | [guide] |

## Не найдено

- Официальная цифра скорости Flare относительно Sunburst или gpt-image-2. Есть только качественная формулировка и совет мерить самому [prompting].
- Опубликованная таблица цены за картинку для 2.5. Есть только калькулятор; расчёт выше выведен из его кода.
- Отдельный лимит `n` или числа входных изображений для 2.5, отличный от общего (1–10 и 16).
- Модель «GPT Image 2.6»: упомянута одной строкой в описании `markup` [ref-edit], больше нигде.
- Официальный маршрут установки `imagegen` для агентов вне Codex.
