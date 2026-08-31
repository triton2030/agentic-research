Итог: пакет v3 пока не готов к показу владельцу как версия для утверждения. Прежние №7–9 закрыты, но бюджет, карта рефактора, самодостаточность пары и финальная проверка текущей версии остаются незакрытыми; дополнительно обнаружены четыре материальные потери при «поглощении» и три нарушения архитектуры стадий.

## Статус прежних девяти нарушений

| № | Статус | Проверка |
|---|---|---|
| 1 | **Не закрыто** | Заявленный счёт снова считает составные контейнеры единицами. В [SKILL.md](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/draft-2026-08-28/SKILL.md:34) определение зоны содержит несколько независимо нарушимых требований; две развилки также склеены в одном абзаце на [строке 58](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/draft-2026-08-28/SKILL.md:58). |
| 2 | **Закрыто частично** | В [reviews.md](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/checks-2026-08-28/reviews.md:203) появились суммы active-set, но они уже равны 25–38 строкам и превышают потолок 20; продолжающие действовать обязательства прошлых стадий не посчитаны. |
| 3 | **Закрыто частично** | Таблица v3 появилась на [reviews.md:186](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/checks-2026-08-28/reviews.md:186), но не является плоской картой всех прежних единиц, содержит ложные absorbed-claims и по-прежнему не называет для новых ограничений `провал → вытесненная свобода`, как требует [refactor.md](/Users/triton/.claude/skills/1skill-creation/references/refactor.md:18). |
| 4 | **Закрыто частично** | Третий пункт цели стал полным предложением, граф назван в [SKILL.md:26](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/draft-2026-08-28/SKILL.md:26). Но пара всё ещё ссылается на неназванную «форму» и сама не сообщает 500/20, Goal/Context и критерий `Нерушимо:`; удержав только пару, точную форму вывести нельзя. |
| 5 | **Не закрыто, но исключено из вердикта** | Product Frame по-прежнему отсутствует и назван открытым вопросом на [reviews.md:211](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/checks-2026-08-28/reviews.md:211). По прямой границе задания это не находка. |
| 6 | **Не закрыто** | После появления v3 на [reviews.md:174](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/checks-2026-08-28/reviews.md:174) нет полного прогона точной версии двумя проверяющими и исполнителем. Последний `coursely` использовал удалённые `interview` и `knowledge-out`: [trial-coursely.md:9](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/checks-2026-08-28/trial-coursely.md:9). Текущий аудит закрывает только буквальную Codex-проверку, не trajectory и trial. |
| 7 | **Закрыто** | Поздние решения о невырезании, честном счёте, стадиях, моменте проверяющих, Codex-аудите, веере и связях зон внесены в [user-said.md](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/user-said.md:9) и адресуют полный дословный holder. |
| 8 | **Закрыто формально** | Все шесть references имеют явные `Вход` и `Выход`; прямых ссылок reference→reference нет. Однако осталась новая проблема вложенного переключения между references — ниже. |
| 9 | **Закрыто** | Корень теперь создаётся после разведки и сверки, последним: [assembly.md:18](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/draft-2026-08-28/references/assembly.md:18). Обратной зависимости прежней версии нет. |

## Проверка таблицы поглощений v3

| Строка таблицы | Вердикт | Что установлено |
|---|---|---|
| `interview.md целиком → intent 1–2, 6` | **Ложно** | Из `git 5fc9f475:.../interview.md:7–20` пропали метрика цели, доказательство, не-цель, цена ошибки, аппетит, official local Delta, запрет общих best practices, fallback «лёгкая ориентировка / owner / отсутствие инструкции» и критерий «самоотчёт не различие». Из [intent.md](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/draft-2026-08-28/references/intent.md:5) они не выводятся. |
| `значение → owner; адрес при изменении действия` | **Истинно** | Сохранено в [assembly.md:11](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/draft-2026-08-28/references/assembly.md:11). |
| `таблица классов и голый список выводимы` | **Частично** | Частота ориентировки сохранилась в `placement`, но не по заявленному адресу. Полностью исчезли `дорогой найденный маршрут → INDEX.md` и критерий, что восстановимый listing-ом список не ориентирует. |
| `старые шаги 1–2 → intent 1, 3–5` | **Частично** | Старый шаг 1 сохранён. Корень-роутер старого шага 2 находится фактически в `assembly 7`, а не в `intent`; точный триггер «редактируешь папку → прочти инструкцию» стал лишь выводимым из рёбер. |
| `старый шаг 3 → assembly 4, 6, 7` | **Истинно** | Корень только cross-zone, overflow-map и корень последним сохранены. |
| `старый шаг 4 → zones + assembly` | **Частично** | Адрес вместо пересказа, закрывающая строка и доставка связкой сохранены. Явная достаточность цепочки пропала; прежний критерий получателя файла не поглощён, а фактически заменён новой моделью рёбер. |
| `старый шаг 5 → probe` | **Истинно** | Сохранён и развёрнут в [probe.md](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/draft-2026-08-28/references/probe.md:5). |
| `Форма файла — без изменений` | **Ложно** | Из старой формы исчезли: цель зоны не пересказывает корень; определение единицы как инструкции/ограничения/факта; связка считается одной единицей; запрет повторов; admission-тест «эффект строки дороже вытеснения внимания»; «подозрение, что уведёт, — причина не писать». Текущая форма — [SKILL.md:62](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/draft-2026-08-28/SKILL.md:62). |
| `Соседи → description` | **Частично** | Негативные границы сохранены, но положительные маршруты к `1context-refactor` и `1skill-creation` исчезли. |
| `Codex №9` | **Истинно** | Обратная зависимость снята. |
| `Codex №4` | **Частично** | Предложение исправлено, граф назван; остальная форма в паре не названа. |
| `Codex №8` | **Истинно** | Входы и выходы добавлены всем references. |

## Новые находки

1. Требование владельца: «инструкции мы не можем вырезать… можем объединять… если частности выводятся» ([user-said.md:9](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/user-said.md:9)). Таблица [reviews.md:190](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/checks-2026-08-28/reviews.md:190) ложно объявляет полностью поглощёнными `interview`, классы знания и форму. Минимальная починка: восстановить перечисленные смыслы в самодостаточных стадиях либо пометить каждый как superseded/cut и получить отдельное решение владельца; затем исправить таблицу.

2. Требование тела: «выход — вход следующей» ([SKILL.md:41](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/draft-2026-08-28/SKILL.md:41)). `zones` возвращает вопросы владельцу ([zones.md:25](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/draft-2026-08-28/references/zones.md:25)), а `assembly` требует уже ответы ([assembly.md:3](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/draft-2026-08-28/references/assembly.md:3)); шага получения ответов нет. Минимальная починка: сделать предъявление вопросов и получение ответов терминальным переходом стадии 2 либо разрешить `assembly` принимать нерешённые вопросы как candidate.

3. Требование: «референс-файл не требует и не запускает чтение другого» ([reference-files.md:17](/Users/triton/.claude/skills/1skill-creation/references/reference-files.md:17)). Во время `assembly` или `zones` спор о поверхности/формулировке маршрутизируется к `placement`/`wording` до выхода текущей стадии ([SKILL.md:58](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/draft-2026-08-28/SKILL.md:58)). Минимальная починка: оформить обе развилки самостоятельными переходами с собственным выходом перед возобновлением стадии либо перенести необходимые критерии в текущую стадию.

4. Внутренний конфликт: `zones` безусловно требует каждому зонному субагенту собрать файл зоны ([zones.md:19](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/draft-2026-08-28/references/zones.md:19)), а `assembly` запрещает отдельный файл папке-складу ([assembly.md:14](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/draft-2026-08-28/references/assembly.md:14)). Минимальная починка: разведка возвращает сначала рёбра и классификацию; файл собирается только после решения `zone-file / warehouse`.

5. Требование протокола: в теле остаются общие правила и условия чтения, локальная логика — в reference ([reference-files.md:13](/Users/triton/.claude/skills/1skill-creation/references/reference-files.md:13)). Тело дублирует локальные операции — веер, двустороннюю сверку, дедупликацию, корень последним и пробник через входной файл — из [zones.md](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/draft-2026-08-28/references/zones.md:7), [assembly.md](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/draft-2026-08-28/references/assembly.md:6) и [probe.md](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/draft-2026-08-28/references/probe.md:5). Минимальная починка: оставить в теле порядок, вход/выход и ссылку; детали исполнения — только в стадии.

## Счёты

Метод предикатов: отдельно считается условие, действие или запрет, который можно выполнить/нарушить независимо; примеры и чистые пояснения не дробятся.

| Файл | Заявлено строк-единиц | Фактические Markdown-контейнеры | Независимые предикаты |
|---|---:|---:|---:|
| `SKILL.md` | 20 | **17** | **69** |
| `intent.md` | 6 | 6 | **21** |
| `zones.md` | 8 | 8 | **23** |
| `assembly.md` | 7 | 7 | **21** |
| `probe.md` | 5 | 5 | **14** |
| `placement.md` | 18 | 18 | **37** |
| `wording.md` | 6 | 6 | **16** |

Число 20 для тела получается только если мысленно разделить один абзац «Что такое файл зоны» на три единицы и единый абзац развилок на две. Они не записаны отдельными строками; более того, собственная раскладка журнала на [reviews.md:203](/Users/triton/Documents/GitHub/agentic-research/skills/1instruction-authoring/checks-2026-08-28/reviews.md:203) арифметически даёт 19.

Минимальный loaded-set `тело + один reference`, ещё без обязательств прошлых стадий:

| Режим | По заявленному body=20 | По фактическим контейнерам | Минимум предикатов |
|---|---:|---:|---:|
| intent | 26 | 23 | ≥66 |
| zones | 28 | 25 | ≥68 |
| assembly | 27 | 24 | ≥66 |
| probe | 25 | 22 | ≥58 |
| сдача | 20 | 17 | ≥48 |
| placement | 38 | 35 | ≥79 |
| wording | 26 | 23 | ≥58 |

Продолжающие обязательства и содержимое артефактов прошлых стадий увеличат эти числа. Следовательно, потолок активного набора не доказан ни для одной стадии.

## Вердикт

Архитектурный замысел владельца узнаваем и в главном сохранён, но пакет нельзя показывать как готовую к утверждению точную версию: поглощение неполно, active-set существенно превышает протокол, переходы стадий имеют разрыв и вложенные reference-моменты, а v3 не прошла полный финальный check-approve. Все шесть внутренних ссылок существуют; прямых reference→reference ссылок нет; аудит read-only, файлы пакета не изменялись.