# Проверки 1orchestration v8

Status: `terminal no-change candidate; exact approval не получен`.

Предшествующий exact v7 `d87dd4e574b71a9063d967c10aec986cd6483d0f18f7d2e1ed22d945ee1f32bc`
дал literal `PASS` и clean-run без наблюдаемых gaps, но trajectory оставил два
residue: смена выбранного actor-а не требовала re-estimate, а слово `delta`
смешивало upstream invalidation с ordinary rework. v8 поглощает первый шов в
шаг 4, а второй разделяет на upstream task-input в шаге 6 и missing-only
rework в шаге 5.

После этого владелец добавил criterion against overcomplication, поэтому v7
служит evidence, но не финальной формой.

## Первый check-approve v8

Trajectory checker: `PASS`, материальных находок нет.

Clean-run подтвердил один runtime-файл без reference-workflow: direct actor
`18`, root acceptance `11`; split отклонён, потому что не снимал source units;
смена capability вызвала re-estimate, слабый return не открыл dependency,
upstream-change пересчитал только затронутое. Два наблюдаемых пробела не
приняты как runtime-находки:

- универсальный stopping boundary source-discovery принадлежит task/project
  owners; общий stop-rule либо пропустит канон, либо создаст бесконечный поиск;
- точная нормализация cognitive units противоречит owner-слову
  «приблизительно» и soft nature `20`; небольшая вариативность допустима, пока
  выбор формы от одного спорного пункта не зависит.

Literal checker нашёл три дефекта:

1. Принято: `delta` теперь явно ограничивает отсутствием в `read` и сведения, и
   границы решений.
2. Принято удалением: impact-map, discovery-gap, explicit rework route,
   повторные shape/acceptance clauses сняты; оставшиеся самостоятельные
   инструкции записаны отдельными строками без новых стадий/references.
3. Принято: укрупнённый счёт `18` сначала заменён консервативным `20`, а второй
   checker обнаружил отдельно действующий evidence gate; финальный пересчёт
   ниже исправляет active set до `21`. Metadata отдельно содержит четыре
   декларации.

## Второй check-approve v8

Проверенная версия: exact manifest
`faea1a13830f0a02fddbd3b7e030ab3975ab0e8c604031c3f51df96b0cf74c1b`.

- Trajectory checker: `PASS`, материальных находок нет.
- Clean-run: direct actor `16`, root `8`, root-work `21`; split не снимал
  source units. Capability-change вызвал re-estimate; слабый return был
  отклонён прямо из goals + `done_when/evidence`; explicit accept/rework stage
  не понадобилась.
- Literal checker подтвердил manifest, но нашёл пять literal gaps.

Решения:

1. Goal-зонтики переписаны как три единых desired states; independently
   violable mechanics вынесены в отдельные строки. Evidence check и all-pass
   barrier считаются отдельно.
2. Неоднозначный `resident-набор/форма root` заменён одной определённой
   выбранной конфигурацией: actor с текущим active set либо способ root.
3. Upstream-currentness теперь требует пересобрать затронутые brief/оценки и
   повторить затронутую приёмку до dependency.
4. Counterfactual map развёрнута до полного пятичастного agent-default chain
   для каждой runtime-добавки; metadata обоснована отдельно.
5. Exact clean-run `faea…` сохранён в `clean-run-v8-round2.md`.

После честного пересчёта active set равен `21`, а не `20`. Единица сверх soft
ориентира оставлена сознательно: удаление открыло бы доказанный вред, а новый
reference не уменьшил бы одновременно применимый набор.

Следующий повтор — второй и последний; новый residue не запускает ещё один
design-cycle.

## Терминальный check-approve v8

Exact manifest:
`304feb88f1842b04fbe93af4cddf859df28c17620383941e5399cbaa51390074`.

- Literal checker: `PASS`, findings `[]`.
- Clean-run: manifest совпал; direct actor `21`, root `10`; связный набор на
  единицу выше soft `20` не делился, потому что split повторял owners и добавлял
  merge. Weak return с `4/5 pass` не открыл dependency. Upstream change
  пересобрал затронутые brief/estimates/acceptance.
- Trajectory checker: один material residue — `done_when` не привязывает
  полноту к общей цели, каждому влияющему `source/input` из `read` и `delta`.
  Неполный список способен получить all-pass.

Residue принят: он опирается на прямое owner-требование сохранить все критерии
и на реалистичный путь all-pass неполного списка. Minimum correction — одна
семантическая правка поля `done_when`, без возврата impact-map или reference.

Clean-run также отметил неявный recovery после fail. Он сознательно не принят
как runtime-находка: failed criterion уже является адресом недостающего, а
отдельная rework-строка повторит выводимое поведение и увеличит набор.

Это второй terminal repeat. Candidate не изменён после verdicts; следующий
repair требует нового exact-version check cycle. Official/projections/live не
менялись и approval не запрашивался для этих bytes ранее.

## Fresh Eyes и адресный no-edit probe

Длинная работа достигла траекторной развилки: принять residue как новую
runtime-инструкцию либо остановить накопление проверочной бюрократии. Четыре
независимые линзы дали разные маршруты:

- Premortem предупредил, что формула «каждый source/input и delta» возвращает
  неявную impact-map и самореферентную полноту prompt-а.
- Solvent выбрал `unchanged`, пока путь побега не наблюдён.
- Ladder и Prospector сочли completeness-gate оправданным только если clean
  executor действительно пропускает найденный owner-критерий.

Синтез: сначала один no-edit adversarial probe; одна строка ремонта допустима
только при наблюдаемом escape. Первый запуск оказался `probe_invalid`, потому
что root ошибочно запретил clean actor-у читать актуальный `1skill-creation` и
не передал platform metadata. Тот же actor получил только исправление фактов,
без history, reviews или желаемого вывода.

Исправленный запуск на manifest
`304feb88f1842b04fbe93af4cddf859df28c17620383941e5399cbaa51390074`
вернул `no_escape_observed`. Малозаметный owner-критерий «русский body и
короткие English trigger-only descriptions» вошёл в отдельный `done_when`;
его нарушение не могло пройти all-pass. Это наблюдаемо опровергло необходимость
добавочной completeness-line.

Решение: exact candidate остаётся неизменным. Предыдущий trajectory residue
переклассифицирован в отвергнутую гипотезу; official/tracked/live остаются
заморожены до безусловного approval этих exact bytes.

## Финальная статическая проверка

- `quick_validate.py`: `Skill is valid!`.
- `openai.yaml`: YAML parse `pass`.
- Candidate manifest: два файла, ноль references,
  `304feb88f1842b04fbe93af4cddf859df28c17620383941e5399cbaa51390074`.
- Frontmatter `description` и Codex `short_description` совпадают побайтно:
  `Use before assigning a subagent or splitting overloaded cognitive work.`
- Внутренних Markdown-ссылок нет; broken-link surface отсутствует.
- Instructional body и `default_prompt` русские; устойчивые interface/schema
  keys и trigger description оставлены английскими.
- Trigger use: «Поручи субагенту проверить пакет» — `use`.
- Trigger skip: «Исправь известную опечатку сам» — `skip`.
- Trigger near-miss: «Составь checklist без поручения и без разделения
  перегруза» — `skip`; соседняя planning/instruction-задача не становится
  оркестрацией только из-за списка.
- Tracked shared owner, tracked Codex projection и installed Codex projection
  совпадают на прежнем normalized manifest
  `46c9e154e00a7f3a1ce49c67f6ec9bf66fbb3b3429162bf8f721f7067999a780`.
  Candidate туда не записан.
