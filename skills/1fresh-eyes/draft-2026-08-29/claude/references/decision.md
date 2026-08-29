---
description: "Turn an observed Claude trigger into one decision anchor and mode."
---

# Decision

Вход: наблюдаемый trigger. Выход: decision anchor и mode.

1. Запиши вопрос, ответ на который сейчас изменит работу.
2. Запиши изменяемое решение.
3. Запиши конечный результат из GOAL/Product Frames; при их неполноте выведи professional outcome из доступного evidence.
4. Выбери `panel` для материальной траекторной развилки или `named` только для явно названного пользователем доступного specialist profile.
5. Без вопроса или decision consequence верни `not_ready` и недостающий anchor.
