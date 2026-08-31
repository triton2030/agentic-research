# Проверки 1orchestration v11

## Wave 1

Exact manifest: `a44ca04405dd2f6b2ef1501b72ba731c4fed9324351eec621b2e7444130107e6`.

Trajectory-checker построил case `23 units → Sol direct · Luna split` и
подтвердил, что около 20 не стало hard cap, root прочитал все влияющие входы,
а bare `done` не открыл dependency. Findings: `[]`.

Literal-checker вернул четыре findings. Решения root:

1. `принять` — trigger не различал состояние до и после поручения; добавлено
   `about to` и before/after evidence для обеих ветвей.
2. `принять` — протокол сохранял смысл, но не буквальные owner-фрагменты;
   неповреждённые фрагменты встроены в порядок, `<unk>` не реконструирован.
3. `принять` — авторский счёт 15 и active 18–19 опровергнут буквальным счётом
   `23 file · 22 body-active`; цели смыслово сжаты, независимо нарушимые шаги
   разделены, reference ради счётчика не создан.
4. `принять` — «простейшая форма» не называла объект и допускала декоративную
   делегацию; возвращена явная граница, уменьшающая набор участника.

## Wave 2 input

- package: `a25d42a53027632015a5813698d7aabb49c6d1645f6360f49f8cf6b33ebbce85`
- `SKILL.md`: `60413e2db12631b9c2f1b50b863354760e4ee096501a2c827adfb814fadee442`
- `openai.yaml`: `897b2f41e124d4ab38e1ad6468378bc48c4c7a5c4729b34660cf280abb71b71f`
- structural precheck: `yaml_ok`; 2 regular files; 0 symlinks; 0 Markdown
  links; description parity and 71-character trigger confirmed.

Candidate и history заморожены до двух terminal-ответов wave 2.

## Terminal wave 2

- Literal findings: `[]`.
- Trajectory findings: `[]`.
- Реалистичная траектория: before-trigger → чтение шести влияющих sources →
  source-bound brief → 23 единицы допустимы для Sol, но меняют границу для
  Luna → прямое поручение снимает с root построчное сопоставление → bare
  `done` не открывает dependency.

После wave 2 candidate не менялся. Root самостоятельно подтвердил manifest,
оба file hashes, YAML/frontmatter, description parity, 71-character trigger,
`2 files · 0 symlinks · 0 Markdown links` и существующий v10
owner/projection/live parity.

Самостоятельный финальный счёт: `SKILL.md 21 = routing 1 + body 20`;
`openai.yaml 4`; mode-specific `direct 20 · split 20`.

Terminal verdict: `ready_exact_candidate`; установка до exact approval
запрещена текущим `1skill-creation/check-approve`.

## Pre-install check-approve rerun

Владелец безусловно утвердил exact candidate и отдельно потребовал перед
установкой снова запустить проверочный протокол:
`_ops/chat-recall/2026-08-29-152721-codex-01a04d0e.md:23`.

К этому моменту текущий `1skill-creation/SKILL.md` изменился до
`c2ca7634a518779fd0c52da0f7bc83bcd55845f6708e86359c46fce9db17ea08`:
он явно сделал цепочку `goal-context → behavior-protocol → check-approve`
обязательной, а checker-промпты явно потребовали `agent-defaults`-аудит.

Третья checker-волна не запущена: тот же `check-approve` разрешает за весь
рефактор максимум две волны и после второй запрещает новых субагентов. Вместо
обхода лимита root проверил дельту нового протокола по сохранённому trace:

- FAST, новый commander's intent, clean-room и preservation map находятся в
  `refactor-v11.md`;
- порядок пользователя записан буквальными фрагментами в
  `draft-v11/SKILL.md:27-39` после полного `behavior-protocol`;
- две независимые волны и решения по каждой finding находятся выше;
- все сформулированные агентом блоки прошли current `agent-defaults`: строки
  опираются на owner-evidence либо на наблюдаемые falsifiers unit-count и
  decorative-delegation; дублированных реактивных строк не найдено;
- active set остаётся `body 20`, references не нужны;
- exact manifest повторно равен
  `a25d42a53027632015a5813698d7aabb49c6d1645f6360f49f8cf6b33ebbce85`;
- YAML и description parity повторно прошли.

Delta finding: `[]`. Candidate после terminal wave 2 не менялся; exact
approval остаётся действительным.

## Opus acceptance audit перед установкой

- requested/resolved: `opus_advisor` → `claude-opus-5`, effort `max`;
- session: `3939fd0f-79c4-4cf6-9837-474ff290a471`;
- terminal verdict: `not_install_ready`;
- установка не выполнялась.

Решения root по материальным findings:

- `принять` — checker authority изменился с baseline `11e8244…` на
  `c2ca7634…` до owner-требования перепроверки; новые prompts применяют
  `agent-defaults` к каждой agent-authored строке, а прежние две волны этот
  контракт не проверяли;
- `принять` — третья волна в том же refactor запрещена current
  `check-approve`; root self-audit не заменяет требуемые независимые окна;
- `принять` — полный построчный `agent-defaults` ledger отсутствует;
- `принять` — прежний upstream rollback потерян: `актуального` не возвращает
  уже выполненную downstream-работу к первому устаревшему результату;
- `принять` — запись «безусловно утвердил и отдельно потребовал» неточна:
  owner approval условен выполнением предварительной проверки;
- `отклонить` — `delta` не сужена до произвольного subset: поле `read`
  адресует все влияющие sources, иначе сам brief нарушает шаги 1–2;
- `отклонить` — шаг когнитивной цены не дубль контекста: без него оценка может
  считать инструкции, но не работу и actor/model fit;
- `отклонить` — manifest gap: root повторно воспроизвёл
  `a25d42a53027632015a5813698d7aabb49c6d1645f6360f49f8cf6b33ebbce85`
  сохранённой NUL-delimited формулой;
- `не blocker` — нулевая граница бюджета и trigger wording остаются рисками,
  но сами по себе не опровергают owner-функцию.

Terminal root verdict: `not_install_ready`; нужен owner-ответ — разрешить
минимальный repair и новую bounded проверку против current authority вопреки
исчерпанному two-wave cap либо явно снять этот гейт и принять известную потерю.
