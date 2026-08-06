## Evidence: докажи изменение, а не послушание

Когда claim звучит как «нужная траектория стала вероятнее», используй matched
resampling: одна непоказанная ситуация, тот же resolved model и settings,
несколько прогонов with/without либо с абляцией. Считай частоту нужного первого
акта на развилке и записывай число прогонов. Один удачный run доказывает
возможность, но не сдвиг вероятности.

Для routing нужны use/skip/near-miss cases против живых соседей. Для operational
claim — точный tool output, воспроизводимый прогон или проверяемое преимущество.
Для distribution — фактический runtime и metadata/projection sync.

Сила evidence растёт вместе с широтой, частотой, риском, credential/network
effects, trigger collision и историей regressions. Не прогоняй фиксированный
ритуал всех проверок; выбирай evidence, которое различает именно заявленные
риски.

Перед добавлением нового правила проведи delete-first pass: убери obsolete
scaffolding, повторы, generic brevity и строки без action-changing Delta. Не
удаляй causal explanation или thought demonstration, если без них controller
снова превращается в произвольную команду.
