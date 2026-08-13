# Вырезано — с причиной

## v2 (2026-08-13)

- `1screenshot-design`, `1design-subagents` и alias
  `design-subagents` как отдельные trigger surfaces — три owner-а одного
  момента; после behavioural acceptance удаляются без compatibility wrapper.
- Декартово произведение screenshot group × восемь question lenses — один crop
  порождал восемь правдоподобных мнений вместо одного вопроса.
- Blind aggregate-agent — не видел pixels и присваивал себе решение root-а.
- Универсальный scheduler, heartbeat/progress runtime и comments-ledger route —
  лишняя orchestration-система для bounded fanout из нескольких независимых
  вопросов.
- Tall full-page screenshot как вход критика — локальные дефекты терялись в
  масштабе страницы.
- `--auto-capture` с broad scroll slices — заменял смысловую декомпозицию
  равными расстояниями.
- Автоматический `npm install playwright@latest` внутри run — плавающая
  зависимость и сетевой side effect; теперь используется только уже
  существующий project/skill/global runtime.
- Отдельные typography/spacing/color/hierarchy reviewers одного ordinary crop —
  смешение вопроса с checklist multiplication.
- Совместный text-density + spacing diagnostic — убедительная, но
  семантически нечестная картинка; modes физически разделены.
- Все пары детей как spacing gaps — live visual gate показал ложные зоны;
  renderer оставляет только соседние элементы.
- Старые design-review runs не переносятся в новую storage topology: правило
  действует на новые project runs.
