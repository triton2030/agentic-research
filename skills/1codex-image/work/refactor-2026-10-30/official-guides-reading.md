# Чтение официальных гайдов OpenAI, 2026-10-30

Прочитаны целиком автором (не пересказ): 
- Image prompting (GPT Image 2.5) — https://developers.openai.com/api/docs/guides/image-prompting
- Image generation — https://developers.openai.com/api/docs/guides/image-generation (Limitations, Edit Images, Mask requirements)
- Cookbook «GPT Image Generation Models Prompting Guide» (архивный, gpt-image-2) — https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide

## Что меняет скил

- Язык: требования нет; все официальные примеры по-английски. Перевод надписей
  в картинке — штатный сценарий (инфографика → испанский).
- Начало промпта — `Create a …` с названием результата и назначения;
  назначение задаёт «режим» и уровень отделки (cookbook, Structure + goal).
- Интерфейс: пример OpenAI перечисляет, что на экране, и заканчивает
  «It should look like a real, well-designed, beautiful app»; позиций и
  пикселей нет. Слайды — «The slide should include:» и маркированный список.
- Раскладка — только «if layout matters» (cookbook, Composition). Раздел
  Limitations: «may have difficulty placing elements precisely in structured
  or layout-sensitive compositions».
- Фото — слово «photorealistic»; параметры камеры трактуются вольно.
- Точный текст — в кавычках, «exactly once», «Include ONLY this text
  (verbatim)», редкие слова по буквам, `medium`/`high` для мелкого текста.
- Правка — «change only X» + список сохранения, повторять на каждой итерации;
  смена условия одной фразой («Make it look like a winter evening with
  snowfall.»); пиксельная неизменность — только вклейкой в оригинал.
- Образцы — номер и описание каждого, как они взаимодействуют, что куда
  переносится.
- Логотипы и персонажи — «original, non-infringing».
- Сложные запросы — короткие сегменты с метками (Scene / Mood / Style /
  Constraints) вместо одного абзаца.

## Расхождение

Раздел UI в гайде говорит «Focus on layout, hierarchy, spacing», а его же
пример не задаёт ни одной позиции. Владелец 2026-10-30 запретил позиции и
вложенность без его слов; иерархия словами («largest element») остаётся.
