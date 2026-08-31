# Чем проверено — 1orchestration

## v13 (2026-08-31, цель как поверхность управления)

- **Чистая комната:** исполнителю ушли только Уникальный контекст, три цели и
  момент вызова плюс один разрешённый внешний файл
  `science/how-to-command-agents-with-text.md`. Он вернул 13 единиц и сам
  раскрыл единственную утечку: список скилов среды показывал ему однострочный
  `description` живого пакета. Тело старого пакета не открывалось.
- **Две волны проверки, обе израсходованы.** Первая по кандидату v1
  (`4ed6c3a9…`, 18 нумерованных единиц): 5 находок траекторного проверяющего и
  12 буквального. Вторая по кандидату v2 (`8ad37145…`, три блока): 7 и 10.
  Все 34 находки приняты, ни одна не отклонена.
- **Что нашли волны и чего без них не было бы:** потерянный барьер перед
  зависимой работой; относительная проверка набора вместо абсолютной;
  отсутствие предохранителя «волевое решение надо проверить отдельным
  возвратом»; подмена критерия цены у реестра его примером; выпавшее
  доказательство на каждый критерий; строка «честный отказ — тоже успех» без
  источника в словах владельца; смещённые на две строки якоря корпуса;
  превышение бюджета владельца вдвое.
- **Проверка потерь проведена дважды:** `preservation.md` против v1 и
  `preservation-v2.md` против v2 — семнадцать механизмов v10 поштучно. Второй
  проход потребовался потому, что v2 заменил весь слой поведения.
- **Механические проверки перед установкой:** пакет
  `83db2e5dda2fb64aedb220ad04c31e9291f9b57b53b5d9719016c97cd682f744`,
  `SKILL.md 018693ff…`, `openai.yaml 179adf85…`; `description` 198 знаков и
  побайтовая parity с `short_description`; ноль путей и имён проектов; ноль
  нумерованных инструкций.
- **Установка:** одна неизменённая версия в шести поверхностях, хэши сверены
  после записи; внутренних ссылок в пакете нет.
- **Не проверено:** живой прогон волны под v13. Заявление ограничено
  структурой, сохранностью смыслов и находками четырёх чистых окон, а не
  поведением в бою. Собственное мерило скила при этом им же нарушено: читатель
  удерживает около 31 вещи при объявленном пороге около 20 — принятый владельцем
  риск.

## v1–v2 (2026-08-10, mavo-short2)

- **Круг трёх Opus-ревью 2026-08-10** (до записи, на v1):
  1) практики интернета (Anthropic multi-agent, Cognition, Google
  research, Cloudflare, OpenAI HITL, arxiv) — скелет подтверждён,
  принесены возвраты-файлами, кросс-семейная проверка, лестница
  усилий; 2) Брукс (структура) — 11 findings, главные: двойник
  Continuity, захват ядра 1fresh-eyes, неисполнимый порог;
  3) аудитор по контрактам 1skill-shaping/1instruction-shaping —
  34 дефекта, главный: опасный коммит чужих правок. Все принятые
  находки вошли в v2; отклонённые — в cut.md.
- **Замеры из памяти проекта**: волны 2026-08-01/02 (порядок и
  барьеры исполнены целиком); авария «ретранслятор с потерями»
  2026-08-06 (указатель на первоисточник); находки линз приёмки не
  пересекаются (business-critic против шести техно-линз).
- **Прогон голой фразой 2026-08-10** («раздели эту работу между
  субагентами и организуй…», свежий агент, без подсказки про скилл):
  скилл поднялся; агент применил порог, правило одного писателя,
  барьер траектории закрыл строкой-причиной, состав волны >4 окон
  объявил явно, предполётом поймал реальный грязный git. Отличие от
  baseline (одно окно «тупило») наблюдаемо. Контролируемого A/B не
  было: baseline — прежний живой прогон другой сессии.
- **Живой прогон волной с принудительным обрывом**: НЕ ПРОВЕДЁН.

## v3 (2026-08-10, agentic-research, сессия a0af5c40)

- **Аудит тремя независимыми линзами** (architecture-critic, auditor,
  LLM-behavior): статус candidate, 5 блокирующих дефектов; все пять
  закрыты в v3 (owner-контур: shared owner создан; runtime-хэндлы:
  мостовые скилы обеих семей; носители ephemeral/durable разведены
  по весу и режиму; root возвращён к синтезу; поведенческий пробел —
  честно открыт, см. ниже).
- **Сверка с первичкой владельца**: 5 параллельных извлекателей по
  recall-корпусам двух проектов + ручная перепроверка двух решающих
  цитат в native-записях (`ca5aea87`, `019fe70a`). Побочный замер:
  2 из 5 дешёвых извлекателей имели слепую зону → правило перекрытия.
- **Когнитивный аудит черновика v3** по `1skill-shaping`: допуск
  (цепочка естественный ход → ход директора → различие) предъявлен
  до черновика; «да» владельца получено на полный текст + 4 вставки
  (wording, хранитель, реестр) 2026-08-10.
- **Ревью-волна v3 → v3.1 (2026-08-10)**: auditor (fail: 6 fail /
  6 pass / 3 unknown) + Брукс (структура не принята, 4 находки);
  материальные находки сверены с первоисточниками. Все приняты и
  закрыты правкой v3.1: прецеденс планового режима, операция фокуса
  «что предъявить» вместо «прислушиваться», дедуп ядер по
  владельцам, стоп-условие «посильно», линза копии мозга →
  `1use-principles` (роль «копия мозга» в каталоге 1fresh-eyes не
  существует), порог сверх постоянного слоя, ссылки только в карте
  сбоев, строка разрешения с корнем, шов 1codex (три текста волны →
  один владелец + указатели).
- **Прогоны v3.1 голыми фразами (2026-08-10, Fable)**: near-miss
  «оркестрация в микросервисах» (haiku) — не поднялся, верно;
  use-фраза со скиллом — 4 окна, непересекающиеся зоны, «пакеты
  приму дословно», отчёт волны обещан: поведение по контракту.
  Baseline «без скилла» в owner-репо НЕВАЛИДЕН: агент нашёл tracked
  owner в рабочем дереве и исполнил его правила (сам зафиксировал
  отсутствие installed-копии как находку). Чистый with/without
  возможен только в чужом проекте.
- **Matched-батарея 4 сценария × 3 условия**: НЕ ПРОВЕДЕНА;
  владелец предпочитает когнитивный аудит полным прогонам
  (2026-08-08), interruption-прогон рекомендован первым живым
  применением: проверяет папку волны, контекст-файл, реестр и
  respawn одним тестом.
- Открытые непроверенные конкретизации: порог «3+ инструкционных
  владельца» (число агентское), `.gitignore` при создании папки
  волны, форма отчёта на волнах из 2–3 агентов.

## v4 (2026-08-10, зонтики)

- **Осиротевший когнитивный аудит v3.1** (audit.md, операции 1–9,
  окно вне сессии): 14 дефектов; матрица приёмки recall дня —
  11/11 реализовано. Триаж: 13 принято, Д14 отклонён (самоотчёты
  «корпус не читал» / «пакеты дословно» — след дороже пользы;
  поведение судит внешнее окно траектории). Известная цена.
- **Закрытие перекройкой, не заплатками**: три зонтика (след /
  момент окна / владелец формы) по доктрине владельца «сжатие =
  замена общими инструкциями»; тело ~180 → ~125 строк, правил
  меньше, чем в v3.1; лимиты параллельности восстановлены (Д1,
  делегированы delegation.md:21).
- **Прогонов v4 нет**: текст заморожен до interruption-прогона на
  живой задаче — он проверит папку волны, контекст-файл с
  переходом, реестр, прецеденс плана и respawn одним тестом.

## v4.1 (2026-08-10, две P1-правки)

- Владелец одобрил только прямое root-чтение и durable no-plan
  manifest; переписывание и расширение запретил.
- Обе проекции и live installs совпадают с owner; `quick_validate`,
  `qv-skill` и локальный `md check` прошли.
- Fresh dry-run остановлен без возврата; forced-crash behavior не
  доказан.

## v4.3 (2026-08-22, no-delta terminal)

- Comparator: task `01a0236d-cbaf-72e1-95dd-0832b58fd23b` под прежним
  контрактом повторял bounded waits после отсутствующих terminal packets и
  принимал writer progress-report без owner-файлов. Это исторический живой
  baseline, не matched A/B.
- Codex clean-window falsifier прочитал installed projection и на первом
  no-delta wait выбрал один read-only probe → `UNKNOWN`/blocker → стоп только
  зависимой ветки без нового окна. Точная модель subagent packet-ом не
  экспонирована; harness — Codex collaboration, локальные read-only tools.
- Claude clean-window falsifier: `claude-opus-5`, `xhigh`, blocking
  `claude_ask`, local read-only tools, `warnings=[]`; installed Claude
  projection дал ту же последовательность и отказался немедленно создавать
  новое окно.
- Locator-pass: и Codex, и Claude разрешили `1instruction-shaping` → его
  `references/wording.md` в единственный installed файл своей семьи.
- Distribution: `sync_simple_projections.py 1orchestration --check` подтвердил
  shared owner, tracked Codex/Claude и обе installed projections.
- Не проверено: forced live interruption реальной волны; claim ограничен
  clean-window decision, locator и distribution.

## v5 (2026-08-25, внимательный рефактор)

- **Comparator:** portable package до правки — `SKILL.md` 147 строк и три
  reference-файла, всего 219 строк. Candidate — `SKILL.md` 103 строки и два
  reference-файла, всего 168 строк. Удаление — не самостоятельный критерий:
  оно принято только после obligation map и source check.
- **Obligation map:** около 20 прежних карточек сведены к 14 decision-bearing
  карточкам: routing; root usefulness/trajectory/direct owners; admission;
  parallel против staged handoff; outcome/owner split; instruction focus;
  map/brief/return; write isolation; barrier/evidence; conditional acceptance;
  root conflict+synthesis+report; carrier/state seam; repair; completion.
  Снятые карточки и причины перечислены в `cut.md`.
- **Owner evidence:** текущий запрос захвачен в recall и сверен с исходными
  требованиями владельца: work + instruction-load allocation, root как CTO,
  прямое owner-чтение, chat map/report, durable decisions и pause-point copy.
  Числового порога, обязательного verifier-а и статической instruction-cost
  таблицы в словах владельца не найдено.
- **Current external check:** OpenAI Subagents поддерживает независимые
  потоки, изоляцию шумного контекста, summary-return и осторожность с
  параллельными writes; Claude Opus 5 prompting отдельно предупреждает не
  делегировать малые задачи, держать число subagents низким и не создавать
  их только для общей перепроверки. Это источник для admission boundary, не
  для локальной формы skill-а.
- **Независимый structural re-audit:** пять прежних finding-ов закрыты —
  instruction load, staged handoff, specialized-owner exclusions,
  `1planning` repair seam и pause point. Итог: `architecture_ok`.
- **Независимый acceptance re-audit:** B1–B4 и A1–A3 pass по прямому
  evidence. B5 оставлен unknown до clean-window routing-прогона: чтение
  metadata не доказывает runtime selection.
- **Первый clean-window two-plus run:** без имени скила агент открыл два
  независимых read-only потока и root-синтез, то есть положительная routing
  граница сработала. Один поток нашёл новый seam-дефект: terminal после
  второго repair не был назван, а потеря worker-а смешивалась с recovery
  root-session. Candidate исправлен: replacement считается repair, второй
  неуспех даёт final blocker, session break отдаётся recovery всей волны.
- **Near-miss one worker / one critic:** оба чистых запроса открыли ровно одно
  требуемое окно, не общую orchestration-wave. Critic нашёл двусмысленность:
  цель звучала безусловно, хотя admission законно оставляет работу у root.
  Цель и completion уточнены как два успешных исхода: полезная запущенная
  волна или мотивированный no-launch.
- **Specialized-owner near-misses:** запрос `1fresh-eyes` применил только его
  trajectory route. Запрос deep agents отдал controller, три framework-stream
  и synthesis владельцу `1deep-agents`; `1orchestration` не применялся, но
  его live body было прочитано ради seam. Это оставило лишнюю instruction
  load, поэтому отрицательная граница вынесена в начало description, а
  положительный trigger ограничен general wave без другого controller-а.
- **Post-reorder deep-agent probe:** чистое окно открыло только
  `1chat-recall` и `1deep-agents`; `1orchestration` больше не загружался.
- **Staged contrast:** phase-name-only цепочка на тех же источниках и критерии
  осталась в одном окне. General extraction → writer case выбрал staged
  handoff и назвал material delta — clean writer context + новое write
  ownership — вместе с ценой передачи. Независимая acceptance ушла к своему
  специализированному владельцу `1fresh-eyes`.
- **Финальный независимый acceptance re-audit:** repair R1–R4, goal/completion
  G1–G3, description D1–D4, positive routing B1 и staged S1–S3 — pass;
  blocking findings нет.
- **Semantic edge review status for live `1orchestration` seams:** outgoing
  `SKILL → wave-folder/repair`, `wave-folder → repair`, `1planning →
  wait/probe/repair owner` и `1codex → general wave contract` прочитаны с
  обеих сторон и остаются верными. Exact search нашёл два stale body claims в
  `skills/claude/1codex/references/fleet.md`: старый cap `3–4/>4` и preflight
  attribution. Они исправлены локальной дельтой holder-а и установлены;
  непрочитанного остатка в зафиксированном scope нет. Исторические упоминания
  удалённых references не менялись: они описывают происхождение и снятие.
- **Статическая проверка candidate:** `quick_validate.py` — valid;
  `git diff --check` — clean; удалённые reference-адреса в shared owner не
  остались.
- **Distribution:** `sync_simple_projections.py 1orchestration --check`
  подтвердил shared owner, tracked Codex/Claude и обе installed projection;
  `1codex --check` подтвердил Claude runtime owner и installed package.
- **Остаточный риск после этой версии:** forced live interruption настоящей
  волны по-прежнему не проведён; repair доказан как decision contract, не как
  fault-injection run.
