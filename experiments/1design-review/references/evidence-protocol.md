# Screenshot Evidence Protocol

Этот reference читается при создании или отладке evidence. Он владеет
машинным входом и преобразованиями; SKILL.md владеет визуальным решением.

## Sources и plan

Один run использует plan version 2 и один или несколько named sources:

~~~json
{
  "version": 2,
  "sources": [
    {"id": "page", "type": "url", "url": "http://localhost:3000"}
  ],
  "evidence": [],
  "tasks": []
}
~~~

Обычный review использует один source. Before/after использует два image
sources либо два явно названных states одного URL source. Каждый evidence
artifact имеет sourceId.

Image source использует полный image как viewport без дополнительного rect.
Block требует один explicit pixel rect; family требует explicit member rects.
Text-density и spacing без DOM завершаются unsupported, а не имитируются. URL
source разрешает DOM selectors и все evidence kinds.

Task содержит id, один непустой question, ровно один evidence id в evidenceIds
и decision. Один reviewer-eligible evidence id используется ровно одним task.
Viewport — root-only orientation artifact и task на него ссылаться не может.
Один artifact не может иметь два diagnostic kinds.

## Evidence kinds

- viewport — root-only orientation для композиции или state; clean reviewer его
  не получает. Канонический desktop-fhd: 1920×1080, DPR 1. Не создавай tall
  full-page artifact.
- transition — узкая горизонтальная полоса, где граница двух заданных соседних
  sections помещена около центра. Она рендерится из fresh viewport, но полный
  viewport reviewer-у не передаётся. Boundary равен середине между концом before
  и началом after; при overlap используется начало after; scrollY clamp-ится
  документом. Высота полосы не больше 35% viewport и не больше 420 px.
- block — один semantic target или видимая relationship двух соседних targets:
  например heading + subheading или copy + image. Selector/rect или общий rect
  двух targets расширяется на 10% target width слева/справа и 10% target height
  сверху/снизу, затем clamp-ится source. Manifest хранит requested и actual
  context. Огромный target, который не изолирует вопрос, отклоняется и требует
  более узкого target; итоговый crop не может занимать больше 50% площади
  viewport.
- family — collage из 1–4 элементов одной семьи и одного state/profile:
  buttons, headings, body styles, fields, cards или icons. Root явно выбирает
  members; совпадений больше четырёх нельзя молча обрезать. Каждый member
  получает 10% context; collage использует 1×1, 2×1 или 2×2 и один общий scale
  без независимого растягивания cells.
- text-density — DOM-only белое изображение, где каждый видимый text-line rect
  внутри target заменён сплошным красным прямоугольником. Ни glyphs, ни images,
  ни decoration, ни spacing colors не сохраняются. Manifest пишет union
  occupiedRatio, rect count и warnings для canvas text, closed shadow DOM,
  generated content или cross-origin iframe.
- spacing — DOM-only карта одного root-selected semantic subtree. Text, icons,
  images, backgrounds, borders и shadows удаляются; content boxes белые,
  outlines серые, padding и gap каждого явно выбранного nested container имеют
  отдельный deterministic hue, overlap — magenta. Text-density primitives сюда
  не передаются. Manifest перечисляет containers, computed geometry и warnings
  для collapsed margins, transforms и absolute positioning.

## Capture gate

Перед screenshot дождись DOM, fonts и images; отключи animations и включи
reduced motion. Каждый derived artifact строится из fresh source state, не из
уже уменьшенного PNG.

Manifest для каждого artifact хранит id, kind, file, source state, viewport,
target/context rects, selected members или containers, algorithmVersion,
warnings и kind-specific stats. Capture считается failed, если selector не
найден или неоднозначен, файл отсутствует, context обрезан без записи, family
содержит больше четырёх members, diagnostic смешан с другим kind или task
ссылается на failed evidence.

Root открывает каждый reviewer PNG и подтверждает target, state, context и
читаемость через `scripts/approve-design-evidence.mjs`. Скрипт сохраняет
`root-approval.json` с SHA-256 текущего manifest и для каждого approved PNG —
canonical path, SHA-256 bytes, byte size и dimensions. Изменившийся или
отсутствующий approval не допускает fanout. Структурно valid manifest без этого
visual gate недостаточен.
Fanout может содержать десятки tasks, но runner держит максимум три активных
reviewer-процесса глобально, не допускает второй runner даже для другого run и
завершает всю очередь до root synthesis. Clean process получает task-local
копию attachment, а OS sandbox запрещает чтение общего run-dir: sibling crops,
root-only viewport и чужие reports недоступны.
