# Adjacent Skill Not Activated

## Observation

В momentum design feature внутри одного скила модель **не активирует**
знание про соседние скилы, даже когда они visible в skill list и владеют
сигналом, нужным для текущего решения. Скил-as-frame становится attention
потолком: всё внутри = в фокусе, всё снаружи = метаданные, неактивно — даже
если соседний skill уже владеет половиной решения.

Pattern combo: **frame lock** (skill description как потолок) +
**streetlight effect** (только что прочитанный код в активной памяти,
соседний скил в виде заголовка) + **Einstellung** (задача пахнет привычно
«улучшить X» → engineering внутри X, вместо «может другой Y уже это
делает»).

User ловит это до меня и подсказывает («эмбединги тут помогут», «в
`1md-navigator` это уже есть»). Цена — user-correct ход и первый раунд
design выкидывается.

## Counter

- 2026-05-20 [Claude Opus 4.7]: blast-radius на секцию `[[file#heading]]`
  в MAVO/Анализ. Engineering-ил три варианта внутри `1md-graph` (keep,
  pass-through anchors, heading-as-node), измерял frequency, делал
  adversarial round. Не активировал знание что `1md-navigator search`
  уже владеет section-level semantic layer (BM25F + dense), а индекс
  корпуса физически живёт в `.md-navigator/index.sqlite`. User вызвал
  `1step-back` с подсказкой «эмбединги могут помочь» — reframe показал
  что blast-radius на секцию — hybrid (hard layer = explicit wikilinks
  с anchor + soft layer = semantic neighbours в соседнем скиле). Hard
  alone — false confidence на cross-referenced корпусе.

## Possible upgrade

Перед содержательной design-работой внутри одного скила — обязательный
вопрос: «какой соседний skill уже владеет смежным сигналом для этой
задачи»? Не «есть ли он» (по skill list бесполезно — это just metadata),
а «он мог бы закрыть часть моего вопроса до того, как я строю feature».

Конкретные примеры пары для MD-работы:

- blast-radius / dependency на секцию → `1md-graph` (hard) +
  `1md-navigator` (soft), не один.
- IA / structural smells → `1ia-audit` + `1md-navigator overlaps` +
  `1md-graph cycles`.
- Cold-start orientation в коде → `1repo-map`, не Read + Glob.

Default frame должен быть «какие два-три скила вместе закрывают задачу»,
не «как улучшить тот, что в фокусе».
