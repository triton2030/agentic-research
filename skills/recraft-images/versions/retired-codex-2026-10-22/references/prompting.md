# Полный промпт для Recraft

Локальное правило владельца строже документации: Recraft V4.1 умеет работать с
короткими prompts, но оплачиваемый workflow не использует 3–6 слов для
исследования. Перед вызовом формулируй намеренный, самодостаточный brief.

## Сначала скомпилируй намерение

Owner brief — источник цели, не готовая строка для модели. До написания prompt
переведи каждое аналитическое требование в наблюдаемые свойства изображения.

| Намерение владельца | В prompt или tool |
| --- | --- |
| Предмет занимает большую часть кадра | dominant subject, tight framing, narrow surrounding margin, edges close to frame |
| Много свободного места | generous negative space, small isolated subject, quiet background |
| Размер или пропорция output | `image_size` tool parameter, не текст prompt |
| Повышенное разрешение | Pro model/size, не magic quality token |
| Точное число объектов | semantic count словами, если количество должно быть видно |
| Текст, который должен быть изображён | точная строка в кавычках |

Не копируй в prompt проценты, координаты, pixel dimensions, значения слайдеров
или номера вариантов, если они не должны стать видимым содержимым. Проверка:
можно ли наблюдать нужный эффект, не зная исходного числа? Если да, опиши эти
визуальные признаки и убери число.

## Сборка от общего к частному

Включай только релевантные слои, но закрой все решения, от которых зависит
пригодность результата:

1. **Результат и субъект** — что именно изображено, действие, количество.
2. **Композиция** — кадр, ракурс, положение, масштаб, negative space, связи.
3. **Контекст** — фон, место, эпоха, соседние объекты.
4. **Визуальный формат** — photo, illustration, vector, poster, logo, 3D.
5. **Art direction** — конкретная эстетика и степень выразительности.
6. **Свет и цвет** — направление/жёсткость света, палитра, контраст.
7. **Материал и детали** — фактура, поверхность, оптически важные признаки.
8. **Текст и layout** — точная строка в кавычках, иерархия, место, размер.
9. **Ограничения** — только проверяемые визуальные запреты, без boilerplate.

Пиши для новой image model, которая не знает чат: никаких «как выше», «по нашей
идее», причин выбора или метаинструкций Codex. Не добавляй факты, меняющие
смысл заказа. Достраивай art direction, а не новую концепцию.

## Photo и product shot

Укажи субъект и действие; крупность и угол камеры; среду; поведение света;
материалы/кожу/поверхности; глубину резкости; нужную степень editorial или
documentary realism. Для каталожного товара явно зафиксируй ориентацию,
нейтральность фона, видимые грани, тени и отсутствие лишнего реквизита.

Не используй «8K», «masterpiece» и похожие magic tokens вместо наблюдаемых
свойств. Если высокое разрешение действительно нужно, это выбор Pro model, а
не слово в prompt.

## Vector, logo и icon set

Определи:

1. graphic type — logo, mark, icon set, pictogram system;
2. shape logic — геометрия, силуэт, симметрия/асимметрия;
3. palette — точное число цветов или конкретные цвета;
4. line discipline — толщина, окончания, outline/fill;
5. layout — centered lockup, grid, spacing, visual weight;
6. constraints — flat fills, no gradients/shadows/texture, если это нужно.

Для набора зафиксируй общие corner radius, stroke weight, сетку, масштаб и
optical weight. Не смешивай vector brief с photographic texture, depth of field
и сложным реализмом. Нативный SVG сохраняй как SVG.

## Poster, cover и изображение с текстом

Следуй структуре Recraft:

1. format/scale;
2. background или visual layer A;
3. graphic/image layer B;
4. typography hierarchy — что крупнейшее;
5. точный текст и placement logic;
6. contrast между слоями;
7. grid, overlap, crop и общий compositional mechanism.

Каждую видимую строку пиши дословно в кавычках. Длинный мелкий текст — плохой
кандидат на генерацию; оставь место под ручную вёрстку, если точность важнее
синтетического текста.

## Image-to-image и edits

- Опиши, что должно сохраниться: identity, pose, silhouette, product geometry,
  camera, layout.
- Затем назови только изменяемые свойства и желаемый конечный вид.
- `strength` — часть tool contract, не прячь её в prompt; не выдумывай диапазон,
  которого нет в live schema.
- Для inpaint/background prompt описывает содержимое результата внутри маски,
  а не действие «замени».
- Для `image_edit` явно раздели сохраняемое и изменяемое в самом prompt.

## Финальная проверка до кредита

- Один главный субъект/система, нет противоречащих требований.
- Количество объектов, текст и palette заданы точно, если они важны.
- Aspect ratio соответствует месту использования.
- Служебные числа переведены в tool parameters или видимые свойства кадра.
- Prompt самодостаточен и не содержит агентной кухни.
- Model/tool существуют в live schema.
- По умолчанию `n=1`.

## Источники

- [Prompting with Recraft V4](https://www.recraft.ai/docs/prompt-engineering-guide/prompting-with-recraft-v4)
- [Universal prompt template](https://www.recraft.ai/docs/prompt-engineering-guide/prompt-templates/universal)
- [Photorealism](https://www.recraft.ai/docs/prompt-engineering-guide/visual-formats/photorealism)
- [Vector art](https://www.recraft.ai/docs/prompt-engineering-guide/visual-formats/vector-art)
- [Graphic design](https://www.recraft.ai/docs/prompt-engineering-guide/visual-formats/graphic-design)
- [Logos and icons](https://www.recraft.ai/docs/prompt-engineering-guide/visual-formats/logos-and-icons)
- Field evidence, не канон:
  [Ropewalk — 30+ vector tests, June 2026](https://ropewalk.ai/blog/recraft-v4-pro-svg-guide-2026).
  Полезны только наблюдения о limited palette, simple composition и
  consistency; product/model claims не переносить.
