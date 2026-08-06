# Продукт И Мера

`1instruction-layer` превращает устойчивую local truth или повторяющийся провал
в одну поддерживаемую intervention для будущего агента. Проверь три product job
и чини только проваленные:

1. **Load:** нужный текст реально входит в effective chain в нужный момент и
   ведёт к одному owner-у.
2. **Steer:** на representative развилке он меняет первый наблюдаемый акт или
   decision rule, а не только словарь ответа.
3. **Prove / enforce:** проверка различает старую и новую траектории; то, что не
   может зависеть от reasoning, передано внешнему gate-у.

Мера продукта — меньше повторных коррекций и неверных веток при минимальном
prompt- и maintenance-cost. Способность пересказать правило, гладкость wording
и заполненный шаблон доказывают только видимость текста, не steering.

- **Audit/review/diagnose:** findings, evidence и exact proposed repair без edits.
- **Change/fix:** scoped repair и проверка изменённого контракта.

Instruction prose не исполняется как код: она делает одни продолжения
правдоподобнее других. Дорогой или необратимый invariant должен опираться на
permission, hook, validator, test или approval у runtime owner-а.

Далее: `controller.md`, затем `gate0-admission.md`.
