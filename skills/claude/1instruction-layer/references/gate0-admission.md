# Gate 0 — Допусти Durable Работу

1. Назови mode: `audit` не меняет files; `change` разрешает только scoped repair.
2. Отдели одноразовое условие задачи от правила, которое должно пережить thread.
3. Для durable candidate назови основание: stable local fact, recurring
   correction/failure или hard invariant.
4. Выпиши material premises, уже принятые request-ом, старым текстом или твоим
   подходом за истину. Если отрицание premise меняет scope, owner или repair,
   проверь её по независимому owner evidence либо пометь `unknown`; сильный
   framing, повтор и уверенность автора не являются evidence.
5. Для неизвестной необходимой premise явно выбери одно: `insufficient
   evidence`, ограниченное обратимое assumption или blocker. Не достраивай её
   правдоподобным reasoning-ом и не продолжай только потому, что задача допускает
   красивый ответ.
6. Проверь `Load`, `Steer`, `Prove / enforce` по отдельности и отметь только
   проваленные jobs; не переписывай здоровый слой по инерции.
7. Если ещё выбирается instruction text vs skill/agent/hook/config, остановись:
   surface decision принадлежит `1skill-shaping`.

**Результат gate:** `mode + one-off|durable + premise status + admitted evidence
+ failed jobs`. Неизвестна необходимая premise → явный assumption/stop; нет
durable основания или проваленного job → не добавляй правило.
