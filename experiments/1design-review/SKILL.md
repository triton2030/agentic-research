---
name: 1design-review
description: >
  Use at a visual checkpoint when a rendered UI or UI screenshot needs design
  judgment: for a standalone screenshot, substantive post-implementation review,
  visual before/after, or milestone/final signoff. The root may judge one already
  isolated narrow condition directly; a substantive screen or page review uses
  focused screenshot tasks and clean reviewers. Not browser QA, causal bug
  diagnosis, UI creation, or non-UI image critique.
---

# Design Review

## Контекст

Большая картинка перегружает визуальное внимание агента: мелкий дефект исчезает
в странице, а рецензент заполняет пробелы правдоподобной критикой. Лечение —
физически разделить внимание: один clean subagent получает один маленький
вырезанный PNG и целиком тратит своё окно на этот участок. Большой исходный
кадр видит только root; reviewer никогда его не получает.

## Цель

Вернуть pixel-grounded дизайн-вердикт: что держится, что мешает signoff и
какие rendered states это доказывают.

Готово, когда root:

- осмотрел whole-frame контекст и состояния, способные изменить вердикт;
- для substantive review сделал отдельный evidence-пакет на каждый
  decision-relevant визуальный вопрос;
- для substantive review получил candidate findings из clean reviewers и
  заново проверил каждый по исходным пикселям;
- отдал короткий verdict с подтверждёнными приоритетами, ограничениями evidence
  и stop-решением.

## Границы

Внутри: standalone UI screenshots, live UI после реализации, before/after,
responsive и interaction states, milestone/final review, узкий post-fix pass.

Снаружи: создание UI до render, browser/functionality QA, причинная
диагностика CSS/DOM/code, Figma editing, OCR и non-UI image critique. Видимые
clipping, overlap, affordance и perceived-contrast risk остаются visual
findings. Фактическая clickability, runtime overflow, hidden behavior и точные
contrast, pixel или tap-target thresholds требуют отдельного
детерминированного QA/check.

## Инварианты

- Root владеет whole-frame orientation, вопросами, capture, приёмкой findings и
  финальным verdict. Clean reviewer производит кандидатов: его самоотчёт не
  доказательство.
- Один reviewer получает ровно один reviewer-eligible PNG, а один PNG получает
  ровно одного reviewer-а. Viewport/whole-frame остаётся root-only. Не
  прикладывай второй screenshot, исходную большую картинку или соседний crop
  «для контекста»: это возвращает разделённое внимание, ради устранения которого
  существует skill.
- Whole-frame composition, harmony и semantic-weight distribution важнее
  component polish. Root оценивает её по обычному viewport, но не передаёт этот
  frame reviewer-у. Section transition получает отдельную узкую полосу, любой
  локальный вопрос — crop.
- Один ordinary target/relationship и его pixels получают один open-ended
  material-defect task. Не разбивай тот же artifact на отдельные spacing,
  typography, color, hierarchy или alignment questions. Дополнительный task для
  того же target допустим только для другого captured state/relationship либо
  для одного условно вызванного diagnostic, который ordinary pixels не
  разрешили. Before/after получает два независимых state tasks по одному PNG;
  root сравнивает их после adjudication. Family получает один task и один
  collage максимум из четырёх элементов.
- Text-density и spacing diagnostics не входят в baseline review. Создавай один
  из них, только когда обычный screenshot не изолирует конкретный density или
  spacing question и результат способен изменить verdict или action. Эти
  diagnostics всегда разные изображения и разные tasks; оба по умолчанию не
  создаются.
- Pixels решают, существует ли visual finding. Source, DOM и code не входят в
  этот skill; поиск причины подтверждённого finding маршрутизируется отдельным
  technical pass.
- Claim остаётся unverified, если screenshot не показывает условие. Визуальная
  оценка не выдаёт точные размеры, цвета, ratios, contrast или невидимое
  поведение за измеренный факт; числа приходят только из детерминированного
  manifest/check.
- Fanout не стартует, пока root не открыл каждый artifact и не подтвердил
  правильный target, state, context и читаемость.

## Маршрут

1. Сначала отдели visual judgment от соседней задачи. Если render ещё нет —
   вернись к реализации; если проблема «не нажимается / ломается / медленно» —
   маршрутизируй browser QA или diagnosis. Substantive review означает verdict
   о readiness всего screen/page, сравнение нескольких independently judgeable
   regions/states либо milestone/final signoff. Narrow review означает один
   заранее названный visual condition в одном target; размер viewport сам по
   себе границу не определяет. Narrow review может закончиться root-pass и
   пропустить steps 3–6; если derived crop не нужен, supplied screenshot сам
   является evidence. Substantive review идёт через evidence tasks и clean
   reviewers.
2. Осмотри обычный rendered frame до локальных crops. Назови известные audience,
   primary action, intended character и taste constraints; неизвестное пометь
   unknown, не изобретай. Зафиксируй first impression, материальные sections,
   границы, component families и states. Не позволяй локальной аккуратности
   перевесить слабую композицию; итог пока не пиши.
3. Для substantive review сделай coverage sweep: first fold, каждый materially
   distinct semantic block, значимые переходы соседних sections, важные
   component families и те responsive/interaction states, где дизайн
   действительно меняется. Materially distinct означает: evidence может
   изменить ready-status, top actions или решение preserve. Много screenshots —
   следствие декомпозиции, не числовая квота.
4. На каждый ordinary target/relationship создай один open-ended
   material-defect task с id, question, одним evidence id и decision, который ответ
   может изменить. Запрещён whole-page вопрос «что здесь не так» и несколько
   axis-tasks на одном crop. Diagnostic получает отдельный task только по
   условию из инварианта.
5. Создай evidence по references/evidence-protocol.md. Для live UI bundled
   scripts/design-review исполняет этот contract; supplied screenshots
   используют image sources и явные rects только для derived artifacts. В
   проектной задаче держи весь run в
   `<project>/_workspace/design/1design-review/<MM-DD>/<run-id>/`: PNG, manifest,
   reviewer logs/reports и adjudication не разноси по другим папкам. Для
   projectless screenshot используй отдельный temporary run directory и верни
   его exact path. Открой manifest и каждый PNG; неверный target, state, crop
   или diagnostic исправь до fanout. После этого создай observable gate:

   ```bash
   scripts/approve-design-evidence.mjs \
     --run-dir "<absolute-run-dir>" \
     --all-reviewer-evidence
   ```

   Approval привязан к SHA-256 manifest и к canonical path, SHA-256, byte size и
   dimensions каждого PNG; изменение manifest или пикселей снова блокирует
   fanout.
6. Запусти по одной clean task на каждый независимый question. Reviewer видит
   только один назначенный PNG, question, минимальные audience, primary
   action, intended character и taste constraints и questions.md; не видит chat
   history, code, project instructions, другие findings или root interpretation.
   Runner сохраняет эту границу temporary CODEX_HOME с auth-only copy, neutral
   cwd, ignored rules/config, OS allowlist sandbox, task-local копию ровно одного
   attachment и запрет чтения общего run directory. Один глобальный runner
   не даёт двум независимым review-runs вместе превысить предел в три процесса.
   Очередь из 50–60 узких reviewers нормальна: запускай её до завершения
   ограниченными партиями, не больше трёх одновременно. Если evidence
   промахнулся, допустим один bounded repair; второй промах завершает task как
   failed.
7. Для каждого candidate finding заново открой exact pixels и заполни:
   finding id · evidence id · visible condition · user/design effect ·
   confirmed/challenged/unverified · root severity · action-if-confirmed.
   Generic taste, невидимое условие, дубликат или finding вне question
   отклоняются. Blind aggregate-agent не используется: synthesis принадлежит
   root. В run с artifacts сохрани lifecycle status
   open/fixed/rejected/deferred/routed в adjudication.json. Повторный pass
   получает только open ids и fresh evidence; fixed/rejected/deferred не
   открывает без противоречащих pixels. Routed не возвращается visual reviewer:
   root заново adjudicates его, когда названный deterministic/technical check
   вернул результат; pixel contradiction для этого не требуется.
8. Для before/after root сопоставляет два независимо проверенных state reports,
   сам открывает оба PNG, называет видимое изменение и лишь затем классифицирует
   better / worse / merely different. Difference само по себе не improvement.
9. Верни первой строкой ready / not ready / evidence-limited вместе с strongest
   visible reason. Затем: 1–3 подтверждённых приоритета с evidence ids и user
   effect; что уже держится и должно сохраниться; отклонённый шум только если он
   мог изменить решение; missing deterministic checks; один следующий gate либо
   stop. Если task failed, назови task id и log path; partial run не выдавай за
   покрытый вопрос. Остановись, когда smallest sufficient evidence поддерживает
   verdict, все полученные candidate findings adjudicated, а каждый ещё
   способный изменить verdict пробел назван как конкретный missing state или
   check.

## Известные сбои

- Пишется capture plan или неясно, какой crop/diagnostic нужен → широкий кадр
  или смешанная линза вернут перегрузку → читай
  references/evidence-protocol.md.
- Clean reviewer начал писать общий audit, хвалить страницу или угадывать code →
  root получит правдоподобный шум → используй questions.md без добавления
  общего checklist.
- Повторный проход снова открывает уже решённое → micro-polish loop повреждает
  то, что держалось → передавай только open finding ids и fresh evidence.
