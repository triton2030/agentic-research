---
description: "Как gpt-image-2.5-sunburst-2026-09-08 читает слова брифа: какая фраза какой эффект дала, с чем стояла рядом и сколько раз проверена."
aliases: ["кодекс имдж", "codex image", "Sunburst", "уроки промптинга картинок"]
---

# gpt-image-2.5-sunburst-2026-09-08

Единственная модель картинок владельца. Снимок на 3 ноября 2026; качество `high`, без входной картинки, если не сказано иное.
Как запускать модель и писать бриф, держит скил `1codex-image`; здесь — уроки о том, как она отвечает на слова.

## Как с ней работать

Это думающая модель: ей дают цель, а не инструкцию рисования, и управляют ею как агентом.
Бриф собирается из модулей — задача (что это, для чего, что обязано быть), стиль (утверждённый абзац), инварианты владельца; порядок, размеры, акценты, карточки и цвета она решает сама[^owner-agent].
Каждое слово тянет за собой смысл, поэтому инвариант пересобирает формулировки брифа, а не дописывается к ним: сначала найди слова, которые тянут против него[^owner-words].
Дизайны страниц и интерфейсов — генератор идей: выдуманные подписи и неверный цвет текста ожидаемы. Точный текст и правдивость проверяются там, где картинка уходит в публикацию.

## Общие закономерности

1. Модель думает жанрами: по самым сильным словам выбирает самый типичный образ жанра и заполняет всё неназванное его штампами (v1, v3–v7, v13–v17).
2. Существительное решает материал и форму, прилагательное настраивает, запрет весит меньше всего.
3. Читает буквально: сравнение рисует свой образ (`like an ember` → уголь внутри), метафора и абстракция (`the ice holds the fire`, `no drama`) ничего видимого не меняют.
4. Самое сильное слово растекается по всей картинке (`crack` — трещины во всём льду, `dark` — драма всей сцены).
5. Настроение несёт цвет главного акцента: угрозу давала красно-оранжевая лава, а не темнота и свет (v24 против v25).
6. Строка, задающая кадр прямо, перевешивает жанровую фразу (v22, v23 против v19).
7. Сильная строка воспроизводится в разных брифах (жар v16 — в v16, v18–v20; жар v13 — в v13, v21–v23). При одном и том же брифе держатся эффекты названных фраз, а гуляют выравнивание текста, путь трещины и мелочи фона (v26, v56, v58 — по три прогона).
8. Абзац стиля переносится на другое содержание целиком, и то, что в нём названо, становится мотивом и там; предмет из списка содержания сам не переносится (посадочная страница A, B).
9. Пустой текстовый слот она заполняет правдоподобной выдумкой: обещаниями о продукте, знаком логотипа, иконками у пунктов списка.
10. Точный текст в кавычках выходит без ошибок (все версии серии); стилизованная буква может потерять деталь — A без перекладины (v4).

## Уроки по тому, чем управляет фраза

Колонка «Где» — версия серии PERMAFROST и число прогонов, если их больше одного; брифы и картинки — в журнале серии[^permafrost].

### Качество и общее впечатление

| Фраза | Эффект | Где |
| --- | --- | --- |
| `Make it beautiful:` перед `a calm, premium corporate look. Minimal and quiet, very few details.` | Убрать её — детализация не меняется; детали несла строка жара | v26 против v30 (2 и 2) |
| Добавить к удачному брифу `facets`, `refracts`, `frost`, `vapor` и снять `almost no texture` | Хуже: каждое новое явление нарисовано деталями, лёд потерял гладкость | v37–v42 против v34 |
| Сократить бриф 164 → 121 слово, сняв слова без работы и оставив держащие строки | Спокойнее и чище исходного | v43 против v34 |
| Сократить до 73 и 53 слов, сняв `almost no texture`, `minimal`, `seen up close` | Возвращаются фактура, куб, камни и драма | v44, v45 |
| Тот же бриф v26 трижды | Композиция, палитра и трещина близки во всех трёх | v26, v26-r2, v26-r3 (3) |

### Свет и яркость

| Фраза | Эффект | Где |
| --- | --- | --- |
| (нет слова о свете) | Светлый день | v1 |
| `Dark and atmospheric` | Темно; рядом с `hot`, `crack` — драма: скалы, волны, закат | v2, v13–v17 |
| `soft grey and pale turquoise` + `dense fog` без слова о темноте | Белёсый туманный день | v8–v12 |
| `Softly lit, calm and atmospheric` | Светлее и воздушнее, угрозы меньше | v26 |
| `Soft, even light with no harsh shadows.` | Почти без эффекта | v25 |

### Палитра и туман

| Фраза | Эффект | Где |
| --- | --- | --- |
| `deep slate grey and muted turquoise` | Тёмная серо-бирюзовая гамма | v13–v23 |
| `cool steel blue and soft turquoise` | Синее и холоднее | v24–v26 |
| `fading into soft mist` | Лёгкая дымка, фон остаётся резким | v1 |
| `in dense fog` | Туман по краям, деталей в центре не меньше | v21–v23 |
| `wrapped in thick soft fog` | Много тумана, но клубами, как облака | v24–v26 |
| `in a thin, even haze that softens everything behind the ice` | Ровная дымка в фоне; у края ещё клубится | v31 |
| `with low, flat ground fog lying still around its base` | Плоский туман только у подножия; выше ясно, фон детальнее | v32 |
| `veiled in a smooth, uniform mist, with no billowing clouds` | Ровная мгла без клубов; спокойствие перешло и на акцент — трещина тише | v33 |

### Материал и форма предмета

| Фраза | Эффект | Где |
| --- | --- | --- |
| `block`, `cube`, `monolith` + `translucent`, `crystal-clear` | Предмет изо льда | v11, v14, v16, v17 |
| `iceberg`, `glacier`, `wall`, `towering over a vast frozen plain` | Пейзаж, лёд похож на скалу | v8–v10, v15 |
| `the size of a mountain, seen from low` | Скалистая гора | v6 |
| `architectural and silent` | Тёмный обелиск, похож на камень | v4 |
| `a giant block of clear translucent ice seen up close, filling most of the frame` | Глыба вплотную, обрезана кадром — не куб и не гора | v13, v21–v26 |
| Убрать `seen up close`, оставив `filling most of the frame` | Глыба целиком, плита, не куб; деталей не меньше, в фоне горы | v35 против v33 |
| `a giant softly rounded slab of clear ice` | Самая простая форма — гладкая скруглённая плита; с инеем и паром поверхность шершавеет | v39, v40 |
| `a few large, clean, smooth facets` | Грани крупнее, но форма всё ещё сложная | v37, v38 |
| `Clear ice that bends and refracts the light, with a thin white frost along its edges` | Преломления и белая изморозь по краям; лёд остаётся гладким | v37, v39, v41 |
| `its surface lightly dusted with frost, cold vapor drifting off it` | Иней и пар — холод читается сильнее всего, но фактуры больше | v38, v40, v42 |
| `one compact standalone object` | Куб; пустое место — горы и озеро | v27 |
| `its faces cut into large flat planes with clean straight edges` | Брус с ровной гранью | v21 |

### Сила и цвет акцента

| Фраза | Эффект | Где |
| --- | --- | --- |
| `barely visible` | Тепла почти нет | v9 |
| `quiet ember-orange glow near its base` | Спокойное свечение у подножия | v10 |
| `visible only through one narrow crack` | Тонкая сдержанная линия | v4, v8 |
| `seam` | Длинная светящаяся линия | v12, v15 |
| `glowing hot red-orange`, `molten` | Лава с тёмным камнем; угроза | v3, v6, v13 |
| `as if a fire burns at its core` | Золото по всей толще, не красное | v14 |
| `like an ember frozen in the ice` | Раскалённое ядро внутри | v17 |
| `a single thin crack` вместо `a deep crack` | Одна тонкая трещина, лавы и камня меньше — картинка проще | v36 против v33 |
| Убрать `, lighting the ice from within` после строки трещины | Почти без эффекта | v34 против v33 |
| `warm amber and red light pouring from a narrow crack in its heart` | Центральная янтарно-красная трещина | v16, v18–v20 (4) |
| `glowing bright golden-amber` | Золотые жилы, тепло без угрозы | v24 |
| `energy` без цвета | Голубые молнии | v7 |

### Жанр и сцена

| Фраза | Эффект | Где |
| --- | --- | --- |
| `Shot like a premium product photograph: one object, soft studio light, a seamless dark background` | Пустой фон, студийный свет, предмет по центру | v19 |
| `premium tech brand key visual`, `A clean minimalist 3D render.` рядом с прямым кадром | Почти без эффекта | v22, v23 |
| `A clean minimalist Cinema 4D render with simple shapes.` рядом с тем же кадром | Заметно: прямые рёбра, чистый блок, тонкая трещина — имя программы сильнее слова «3D» | v41, v42 |
| `the calm key visual of a modern fintech brand` вместо `a calm, premium corporate look` | Почти без изменений: чуть темнее и контрастнее | v46 |
| `calm and restrained like a slide from an Apple keynote` | Светлее и воздушнее | v47 |
| `corporate design discipline — generous negative space, strict alignment, …` | Меняет раскладку: строгая левая сетка текста | v48 |
| `the calm, premium look of a private bank's investor presentation` | Меняет шрифт на узкий, в духе DIN | v49 |
| `the cover of a Swiss bank's annual report, calm and premium` | Светлый редакционный вид, много пустого места, мелкий аккуратный подзаголовок | v50 |
| `Swiss`, `Geneva`, `Zurich` в фразе стиля | Рисует буквально: заснеженные Альпы в фоне | v56 (3 из 3), v57, v59, v60 |
| `the restraint of Swiss private banking — one monumental image, vast empty space, small precise typography, muted colors` | Самый сдержанный и чистый вид, мелкий подзаголовок, горы едва видны | v58 (3 из 3) |
| `an expensive, award-winning annual report design` | Драматичнее: ярче трещина, крупнее заголовок | v60 |
| `Create a social post image for X` против `Create an image` | Почти одинаково при основе v26: драмы от «поста» не видно | v26 против v55 |
| `Create the cover of an annual report` | Светлый редакционный вид, много пустого места, мелкие подписи — как у `annual report` в фразе стиля | v53; v50 (2) |
| `Create a poster` | Заголовок крупнее и шире | v54 |
| `Create a key visual` | Сама добавляет иконки к пунктам | v51 |
| `Create a hero image for a fintech website` | Почти как v26 | v52 |
| `Nothing else in the scene: no rocks, no mountains, only the ice in an empty dark misty space.` | Пустой тёмный фон | v18 |
| `The restraint of a premium tech brand campaign … no drama` | Без эффекта | v20 |

### Текст и шрифт

| Фраза | Эффект | Где |
| --- | --- | --- |
| (нет строки о шрифте) | Ледяные «игровые» буквы | v3–v7 |
| `elegant wide-spaced white sans-serif capitals` | Строгий шрифт с разрядкой, стабильно | v1, v2, v8–v29 |
| `the text set large on the left` | Текст не крупнее | v28 |

### Композиция

| Фраза | Эффект | Где |
| --- | --- | --- |
| `Composition: all text on the left …` без слов о фоне | Сама сдвигает предмет вправо и кладёт туман за текст | v27–v29 |
| Пункты списком | Сама добавляет иконки или акцентные черты | v7, v27–v29 |
| `a calm empty corner for a logo` | Обычно оставляет спокойный угол | v1–v26 |

> [!question] Что пока не проверено
> Все уроки — из одной серии с ледяной глыбой: перенос на другие предметы не проверен.
> Почти все строки — один прогон; повтор есть только у строк с числом прогонов.
> Не проверены: даёт ли `low` ту же композицию, что `high`; что добавляет `max`; появляется ли через API зерно в тёмных туманных кадрах, о котором пишут практики[^sources].

[^owner-agent]: Слова владельца 2026-11-03, `_ops/chat-recall/2026-11-03-124247-claude-f2fffc87.md#recall-256e3198252d4f16b3f24dd3c416c66f`.
[^owner-words]: Слова владельца 2026-11-03, `_ops/chat-recall/2026-11-03-124247-claude-f2fffc87.md#recall-fe6350099c734beca06fe445eb370e92`.
[^permafrost]: Проект subfrost, `_workspace/codex-image/2026-11-03/журнал-промптов-permafrost.md` (ветка `claude/permafrost-upgrades-banner-cdeae4`), серия 2026-11-03.
[^sources]: Там же, `research-openai-docs.md` и `research-community.md` — обзоры документации OpenAI и опыта практиков, 2026-11-03.
