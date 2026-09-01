---
description: "Red flags и IA smells для audit mode: evidence, risk, smallest repair."
read-when: "Red flag / smell требует deeper evidence-to-repair mapping; не для обычного design mode."
---

# IA Smell Catalog

Читай, когда быстрый IA verdict не держится без более точной карты запахов или
красный флаг требует evidence. Это reference для judgment, не список причин
автоматически всё переписать.

## Правило Чтения

`signal/count -> candidate smell -> body/context check -> owner-registry check ->
IA judgment -> smallest repair`.

Если evidence нет, verdict = `unknown`, а не вкус. Подтверждённый и
неустранённый red flag требует `risky` или `fail`; назвать owner, repair или
handoff недостаточно. `Pass` возможен только когда smell опровергнут body/context
check-ом либо repair применён и проверен. `Template defect` — diagnosis/mechanism,
не пятый verdict.

## Красные Флаги

`Duplicate truth` — одна umbrella family. Для одного decision/mechanism выпускай
один finding; location, topology, relation и representation записывай как
совместимые diagnosis attributes, а не конкурирующие subtypes.

| Red flag | Evidence | Риск | Smallest repair |
|---|---|---|---|
| **Duplicate truth** | Один durable decision/contract имеет несколько independently editable statements или representations; body/context + owner-registry check подтверждает повтор, а не pointer, example, deprecated alias или local consequence. | Drift: будущая правка обновит одно место и оставит другое stale. | Назначить один confirmed home/normative representation; остальные occurrences → удалить, pointer + local consequence или explicit derived/generated view. Diagnosis attributes и special repairs — ниже. |
| **Ownerless container** | Папка/файл не отвечает, кто владеет смыслом, quality gate и будущими правками. | Контейнер копит мусор, потому что в него можно положить всё похожее. | Cohesion/split/merge/move одного существующего container/folder остаются у `1ia-audit`. System-wide zone/default home/folder-axis/type/catalog/template → `1document-system`; durable `AGENTS.md`/`CLAUDE.md`/path-rule chain → `1instruction-shaping`; `1md-graph` только при graph risk. |
| **View стал truth** | Index, MOC, generated report, audit packet или dashboard содержит уникальные rules/decisions. | View начнёт конкурировать с owner truth; generated/temporary слой станет canon. | Перенести уникальный смысл в owner-файл; view оставить ссылочной сборкой. |
| **Blind atomization** | Файл дробят на главы ради context assembly, но у новых файлов нет отдельных readers, owners, checks или самостоятельного смысла. | Человек теряет цельную мысль; агент получает много мелких слабых truth surfaces. | Оставить секцией; усилить headings/frontmatter/links; split только для самостоятельных частей. |
| **Taxonomy aesthetics** | Папки симметричны или “красивы”, но future edit path не становится короче. | Структура выглядит аккуратно и всё равно ведёт не туда. | Выбирать форму по cohesion/retrieval, а не по симметрии. |
| **Speculative scaffolding** | Папка/файл создан “на будущее”; сейчас нет 2+ однотипных файлов, owner-а или отдельного workflow. | Future-proof превращается в drift-point. | Не создавать; вернуться к секции/одному файлу до реального роста. |
| **Mixed functions** | Один файл держит canon, tasks, criteria, examples, notes или generated view одновременно. | Будущий читатель не знает, что тут truth, а что временный материал. | Развести по существующим owner-файлам; не создавать side-doc, если owner уже есть. |
| **Retrieval gap** | Название, description, headings или hub не выводят будущего человека/агента к подтверждённому owner truth; search не даёт устойчивого handle. | Новая сессия отвечает из случайного файла или создаёт дубль. | Улучшить retrieval surface или добавить hub pointer; rank не выбирает semantic owner. |
| **Жанровый наполнитель** | Секция, колонка или оговорка существует потому, что её требует жанр шаблона, и не несёт различающей информации: колонка с одним значением во всех строках, защитная оговорка на возражение, которого нет в файле, TOC внутри короткого документа. | Контекстный налог растёт, корпоративная норма полноты вытесняет decision-density; конфликтная поверхность ширится без новых решений. | Удалить либо заменить на pointer или `SECTION-STATUS`. Если наполнитель обязателен по template, diagnosis = `template defect`, handoff `1document-system`; verdict остаётся `risky|fail` до проверенного repair. |
| **Metrics-as-verdict** | Длина, heading count, link count, similarity или folder size названы причиной без чтения содержания. | Аудит чинит форму ради метрики и ломает owner truth. | Читать file evidence; метрику держать только как smell signal. |

## Duplicate Truth Diagnosis

После подтверждения umbrella smell запиши совместимые attributes:

- `location = inside-file | cross-file`;
- `topology = project-domain | other | not-applicable`;
- `relation = owner-echo | peer-duplicate | competing-owners`;
- `representation = near-mirror | paraphrase | prose-table-machine`.

`grep -c`, 3+ совпадений, similarity и cluster — только candidate generators.
Прочитай каждый context и отличи owner statement от pointer, example,
deprecated alias и local consequence. Один decision/mechanism остаётся одним
finding даже при нескольких attributes.

Repair уточняется attributes:

- `inside-file` → один home-section/representation со stable ID; остальные
  sections ссылаются без пересказа;
- `owner-echo` → owner anchor + только нужное local consequence;
- `project-domain` → default удалить дубль или оставить pointer; Truth + view
  (hub/MOC/Base) разрешён только при evidence регулярного второго reading path;
- `competing-owners` → не выбирать по rank/quality; authority остаётся
  unresolved до owner decision;
- `prose-table-machine` → одна normative representation и явное направление
  derived/generated/conformance.

Если duplicate производит section/template contract, diagnosis =
`template defect`, handoff `1document-system`; verdict остаётся `risky|fail` до
применённого и проверенного repair.

## Дополнительные Smells

- **Form-task mismatch** — section grammar не поддерживает reader task или
  agent operation trace; проверяй по friction/validation, не по title.
- **Template monoculture** — разные reader jobs/lifecycles/checks насильно
  уложены в одинаковые H2/H3; повтор headings сам по себе остаётся только signal.
- **Cluster/folder mismatch** — topic cluster топологически живёт не там, где
  лежат файлы.
- **Изобретённый словарь** — термин закрытого словаря (статус, состояние,
  режим) вне реестра владельца; для эмбеддинга синоним — похожесть, не
  конфликт, semantic probe его не флагует. Детект: передай `1cli-tools` термины
  файла, реестр владельца и corpus scope для exact occurrence packet
  (одиночное вхождение — только candidate); затем прочитай context и сверь
  термин с закрытым owner-registry. Только отсутствующий там самостоятельный
  термин подтверждает smell; лечение — термин владельца со ссылкой на реестр.
- **Невысказанный инвариант владельца** — owner держит правило только как
  выводимое следствие, не проговаривая его словами использования; поиск по
  формулировке нарушения поднимает чужую проекцию, и она становится de-facto
  retrieval/answer surface; semantic authority остаётся у подтверждённого
  owner-а либо `owner unresolved`. Лечение — явная строка инварианта у owner-а.
- **Родовой retrieval surface** — description / title / heading точны, но звучат
  как общее, уже-известное знание; не различают файл от семантических соседей,
  top-1 плоский, answer surface de-facto размыт (retrieval вероятностный,
  ранжирует по близости — не точному совпадению). Не путать с weak description
  (неточность)
  и smeared truth (дубль смысла): тут surface верен, но не несёт различающую
  дельту. Детект: retrieval sweep даёт плоский top-3, хотя direct owner contract
  подтверждает один файл; answer surface de-facto размыт, но authority не
  меняется. Лечение — переписать surface под то, чего нет у соседей, не менять
  authority по rank.
