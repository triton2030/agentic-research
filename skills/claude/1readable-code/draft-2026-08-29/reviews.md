# Проверка черновика 1readable-code

## Раунд 1

Проверяемая версия: SHA-256
`4ea37c8e825c04d9b575128af191bdecf3b79cba8271ea57d58d1f0fa85f089b`.

### Буквальный аудитор

Принято и исправлено:

- активный набор был 28 единиц без `agents/openai.yaml`, а не заявленные 14;
- удалены ошибочно возвращённые `remaining structural risk` и
  unrelated-cleanup stop;
- `public contract` оставлял внутренние contract decisions внутри skill;
- `removes more … than it adds` не имело общей наблюдаемой меры;
- data-edge rule ошибочно зависел от изменения callers;
- Codex UI prompt продолжал старый six-step protocol;
- route `1codebase-design` был битым в Claude runtime;
- current description не имеет нового routing receipt;
- адрес текущих owner-слов исправлен с `:16-17` на `:18-20`.

### Проверяющий траекторию

Принято и исправлено:

- owner/falsifier gates распространены на read-only review;
- разрешён proposed private owner, пока его выбор не меняет contract;
- net-reduction gate сужен до surface, добавляемой только ради readability;
  required surface теперь не обязана выдумывать удалённую сложность.

### Behavioral probe и comparator

Одинаковый fixture: active enterprise export через API и batch без изменения
сигнатур.

- Draft: до edit назван `exporter/eligibility.py::can_export`; изменены только
  owner и тесты; `python3 -m unittest -v` — 3/3 `OK`.
- No-skill baseline: тот же owner, тот же diff shape и 3/3 `OK`.

Вердикт: probe подтверждает совместимость и наблюдаемый evidence packet, но не
улучшение решения относительно baseline. Improvement остаётся gap-ом; раунд 2
проверяет исправленный текст на новом сценарии.

## Раунд 2

Проверяемая версия: SHA-256
`ece11306a88986fdfa0363f04318b916ff8ecdf471d01039acf339226ee97975`.

### Буквальный аудитор

Принято для следующей версии:

- owner-gate должен покрывать любую нетривиальную review-claim, не только
  structural finding;
- evidence должен быть falsifier-ом каждого claim на owning boundary;
- contract stop обязан назвать runtime-соседа, а не только прекратить skill;
- readability-only condition сформулирован так, чтобы не захватывать required
  surface;
- независимые предикаты разнесены по строкам, обязательный порядок оформлен
  нумерованным protocol;
- UI prompt стал нейтрален к change/refactor/review;
- routing receipts для точного description ещё нужны;
- history-map теперь адресует navigation/safety в `Unique Context`.

Отклонено: вернуть `remaining structural risk` и unrelated-cleanup stop.
Finding возник из двусмысленного receipt раунда 1; `cut.md` фиксирует эти
правила снятыми как global-baseline дубли, нового owner-решения вернуть их нет.

### Проверяющий траекторию

Принято для следующей версии:

- data-edge read должен предшествовать owner choice, edit и нетривиальной
  review-claim;
- completion требует именно опровергающий owning-boundary check/observation;
- UI prompt не должен превращать review в edit.

### Behavioral review-probe

Read-only request: проверить CSV export против repository conventions.

- Назван owner `reporting/formatting.py::format_amount`.
- Claim: `csv_export.py` воспроизводит правило валюты и обходит owner.
- Falsifier: подмена owner до импорта не изменила CSV output; claim выдержал.
- Обычный suite остался 2/2 `OK`, поэтому он не проверял owner delegation.

Вердикт: исправленная версия породила адресуемую review-находку и
claim-specific falsifier там, где зелёный suite был недостаточен. Полезная
Delta для review наблюдалась; probabilistic improvement не доказан.

## Routing receipts перед финальным повтором

Проверялось буквальное `description` версии SHA-256
`4bfa41669d17eb4b7fc89a8918ca20ad57251ea3d5d28cd5d405422879bb5b6c`
в холодном выборе между `1readable-code`, `1codebase-design` и `none`:

- «Убери дублирование правила в трёх обработчиках» → `1readable-code`:
  нетривиальный рефактор внутри уже выбранной границы.
- «Исправь опечатку в комментарии» → `none`: механическая правка.
- «Выбери новый интерфейс адаптера…» → `1codebase-design`: решение меняет
  contract/interface seam.

Это offline routing receipt точного текста, не runtime discovery test. Реальная
активация Claude/Codex остаётся непроверенной.
