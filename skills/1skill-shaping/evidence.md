# Чем проверен

## Lifecycle

`candidate → проверен поведением → спроецирован глобально`

Текущий статус: **candidate** — установлен глобально до поведенческой
проверки (осознанное решение кампании 2026-08-08, риск назван Codex-ревью).
Утверждение текста: «да» владельца в сессии 2026-08-08, дословные решения —
`_ops/chat-recall/2026-08-08-135005-claude-dfa9fb5c.md`.

## Support envelope

Проектировался под `Claude Opus 5` и `GPT-5.6` в Claude Code / Codex,
инструменты чтения-записи файлов, длинная автономия не предполагается —
скил по конструкции останавливается на владельце.

## Статус проверок — 2026-08-08

| Что | Как проверено | Статус |
|---|---|---|
| Текст соответствует собственным правилам (жанр, причины, стоп-условия) | аудит по `references/audit.md`, применён к своему черновику | сделано |
| Активация: голая фраза 5–10 слов поднимает скил | — | **не прогонялось** |
| Негативы near-miss не поднимают скил | — | **не прогонялось** |
| Применение: решение агента отличается от прогона без скила | — | **не прогонялось** |
| Сравнение с прежним `1skill-architect` на одной реальной задаче | — | **не прогонялось** |

**Ничего из поведения не измерено.** Всё, что выше сделано, — чтение и
конструкция. По собственному правилу скила это означает: чтение не доказывает
работу.

## Ближайшая проверка

Взять один реальный скил, переписать его прежним `1skill-architect` (снят в
`skills/1skill-architect/live-claude-2026-08-08/`) и новым, вслепую, и сравнить
принятые решения, а не тексты.

## Точечная правка момента — 2026-08-11

Owner и проекции:

- `qv-skill` для installed Claude и Codex — pass;
- `sync_simple_projections.py 1skill-shaping --check` — tracked и installed
  Claude/Codex byte-identical shared owner-у;
- независимый Claude Opus 5 review (`xhigh`) отклонил отдельный
  `trigger-moment.md`: universal default принадлежит существующему
  `references/description.md`.

Codex smoke: свежий `default` subagent получил запрос исправить description
UI-review skill, который должен сработать только после завершения реализации и
запуска приложения. Он автоматически прочитал installed `1skill-shaping` и
`references/description.md`, вернул:

- момент: реализация завершена, live UI доступен для осмотра;
- «ещё рано»: реализация продолжается или live UI недоступен;
- первую фразу с phase, evidence и capability.

Статус: application possibility — **pass**. Exact resolved model collaboration
API не предъявил; no-skill comparator, matched repeats и late-trigger
probability не проверялись. Один smoke не переводит общий lifecycle из
`candidate` в «проверен поведением».

## Полный preflight аудиторов — 2026-08-14

- Два независимых read-only аудитора до записи вернули покрытие 20/20 файлов
  каждый; оба нашли и закрыли дешёвый выход «неприменимо» без причины.
- `qv-skill` и system `quick_validate.py` для installed Codex/Claude — pass.
- `md check` для shared owner и папки истории — issues `[]`.
- `sync_simple_projections.py 1skill-shaping --check` — tracked и installed
  Codex/Claude совпадают с shared owner; SHA-256 пяти `SKILL.md` одинаков.

Дополнительный post-install smoke остановлен по коррекции владельца как
избыточный для точечной правки; поведенческий uplift не заявляется, lifecycle
остаётся `candidate`.

## Deletion-first controller revision — 2026-08-17

**Claim.** Controller больше не навязывает создаваемому skill фиксированную
форму и self-conformance; он выводит форму через `Поглощение` и `Момент
решения`, сохраняя невыводимые исключения и evidence по claim.

**Matched downstream pilot.** Два чистых Codex-окна получили одну задачу:
pre-draft refactor `1orchestration`. A полностью читал installed controller,
byte-identical `HEAD`; B — текущий tracked draft. Оба полностью прочитали обе
controller-пары, все references, target и его историю.

- A сохранил обязательные `Контекст → Цель` и оставил часть removal-решений
  новыми вопросами владельцу.
- B отказался от fixed template, собрал target по функциям и выдал материально
  отличающуюся карту; его `delete`-рекомендации приняты синтезом только как
  `delete_candidate`.
- Независимый acceptance-аудитор подтвердил decision delta. Один paired sample
  не доказывает вероятностный uplift; causal behavior на других models/targets
  остаётся `unknown`.
- Рискованные B-кандидаты (`3+ instruction owners`, два дешёвых readers)
  получили named loss risk и остановились до comparator и owner curation.
  Проверка подтвердила, что действующий exception/candidate gate не даёт
  распространить их как принятые удаления.

**Fresh Eyes.** Ladder подтвердил цепочку к массовой переработке корпуса и
поставил следующий рубеж на bounded pilot; Solvent отверг принятие controller-а
как непроверенного prerequisite; Prospector показал, что Matt держит test plan
у migration slice, не внутри вечного authoring ritual. Claude Opus 5 premortem
нашёл дешёвый выход через «названо непроверенным»; он закрыт статусом
`candidate`, не распространяемым как принятый. Claude session
`8306b40c-7d64-4cf5-bfdb-8abd341e88f7`, `resolved_model=claude-opus-5`;
warning `permission_denied:Bash`, поэтому локальные claims проверены Codex
напрямую.

**Структура и distribution.** `quick_validate.py` и `qv-skill` — pass для
shared, installed Codex и installed Claude; `md check` — `issues: []` для
portable owner и history; `sync_simple_projections.py ... --check` — все
tracked/installed проекции совпадают. SHA-256 пяти `SKILL.md`:
`5ab3ad2035579c2f6e24cbde8b0c40c407d1a1d58b6928959536723d51240aea`.
`md deps/impact` не нашёл declared dependents; body-ссылки ведут только из
исторических `_workspace/codex-artifacts/**` и сохранённого Matt-report, их
исторический смысл не переписывался.

Статус: **candidate с одним matched decision-map pilot**. Доказано изменение
решения на одном downstream case; систематическое улучшение target models и
безопасность будущей массовой волны не заявляются.

## Goal-owned compression — 2026-08-24

**Claim.** Главный controller теперь держит один semantic owner результата —
`Goal`. Отдельные заголовки `Критерии успеха`, `Инварианты`, `Дельта` и
`Завершение` сняты; невыводимые смыслы остались в автономной границе, трёх
правилах, failure map и conditional references. Объём `SKILL.md` сократился с
204 строк / 1 454 слов / 17 883 байт до 121 / 768 / 9 722.

**Owner evidence.** Владелец назвал дублирование Goal с criteria/invariants и
выбрал полный автономный refactor, затем снял обязательные повторные вопросы и
approval перед редактированием и записью:
`_ops/chat-recall/raw/2026-08-24-201459-codex-01a03446.md:16-18`. Owner review
теперь обратная связь, не lifecycle gate; `candidate` сохраняется из-за
ограниченного behavioral evidence.

**Loss/excess audit.** Два независимых окна прочитали по 20/20 файлов обеих
live shaping-пар и их references. Первый проход вернул шесть потерь с одной
новой двусмысленностью и шесть дублей/излишков. После отмены approval-гейтов
оба окна снова дали 20/20: excess нашёл три seam/duplicate-дефекта, loss — риск
возврата ритуала соседним пакетом. Финальные recheck-и закрыли всё. Сохранены
provenance, material owner-only escalation, admission, независимый audit,
claim-specific evidence, loss controls и distinction
criterion/invariant/non-goal.

**Matched decision-map probe.** На одном prompt старый `HEAD` controller
рекомендовал обязательную последовательность `Context → Goal → Criteria →
Invariants → Failure map → Completion`, owner curation и точное «да» перед
записью. Текущий controller поглощает выводимые criteria/invariants, не
спрашивает разрешения на draft/edit/write и эскалирует только невыводимый
материальный выбор. Оба сохраняют admission и audit. Это доказывает нужную
разницу решения на одном случае, но не вероятностный uplift.

**Structure and distribution.** `quick_validate.py` и `qv-skill` прошли на
10 shared/tracked/installed пакетах `1skill-shaping` и
`1instruction-shaping`; `md check` вернул ноль issues для всех изменённых
Markdown-зон; `sync_simple_projections.py 1skill-shaping
1instruction-shaping --check` подтвердил parity. SHA-256 пяти runtime/tracked
`1skill-shaping/SKILL.md` одинаков: `d753add632b632ded60e1d4f3b5fae7bdefc690de49bd5cf3b53c3e3ab46c2ac`.
`md deps/impact` не нашёл declared dependents; 11 body edges = шесть
датированных `_workspace/codex-artifacts/**`, два датированных research
snapshot-а и три current internal-ссылки из `audit.md`, `interview.md` и
`refactor.md` на owner автономной границы. Исторические утверждения и
downstream-owner ссылки остаются валидны, поэтому они не переписывались;
внутренние edges проверены `md check`.

Статус: **candidate с двумя matched decision-map pilots**. Сжатие и сохранение
известных уникальных смыслов проверены; переносимость результата на другие
targets/models остаётся `unknown`.

## 2026-08-25 — рефактор «аудит отмен + флип зеркал»

Support envelope: Claude Fable 5 (главное окно) + general-purpose субагенты;
рабочий набор моделей по `_ops/GOAL.md`.

Comparator (реальный случай, bounded pilot): заказ «сократи 1interview-tool»
через старую пару (git HEAD, чистое окно) и новую (чистое окно). Обе версии
дали верный маршрут и честный потолок автономии. Различия в пользу новой:
(1) каждая карточка карты смыслов несёт заполненное поле «что закрывает» —
у старой пары этого измерения нет вовсе; (2) новая пересобирает от оригинала
и отказывается итерировать от сокращения 2026-08-23 (защита от потери
поколения) — агент старой пары рационализировал итерацию от предыдущего
упрощения. Деградации от сжатия зеркал в дельты не наблюдалось: агент новой
пары корректно сложил источник `1instruction-shaping` с дельтами.

Аудит черновика: две независимые линзы (лишнее / потерянное-выдуманное),
каждая прочла оба пакета целиком; 12 + 9 находок с цитатами, все закрыты
правками либо осознанно приняты (no-op строки раздела «Контекст» — решение
владельца о философии «не навредить»). Счёт: нумерованные операции пары
61 → 39; строки 1732 → 1637; sync-check проекций зелёный.
