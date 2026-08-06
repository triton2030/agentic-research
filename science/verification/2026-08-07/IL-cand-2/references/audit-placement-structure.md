---
description: "Deep audit root/subtree instruction topology: owner, duplicate, placement и hot path."
read-when: "Спорны root vs subtree, duplicate/drift или структура набора instruction files."
---

# Размещение И Структура Instruction Files

Playbook: каждое правило лежит у правильного owner-а, дети не повторяют корень,
а форма инструкции соответствует live runtime/repo. Это **структурный** аудит инструкций, не
смысловой (смысл и критерии — `audit-meaning-criteria.md`). Линзы качества языка
тянутся из `language-quality-audit.md`.

В audit/review mode вернуть findings и recommended repair без edits. Шаги
починки ниже исполнять только в change/fix mode.

## Что проверяет

1. **Правильная папка / owner.** Каждое правило — у того, кто реально владеет
   зоной? Папочное правило живёт в своей папке, не в корне; корневое — в корне,
   не размазано по детям. Effective chain и owner gate задаёт `SKILL.md`.
2. **Дети не повторяют корень.** Папочный `AGENTS.md` повторяет правило, которое
   уже сказано в корневом? Это второй source of truth или потраченный бюджет
   внимания. Допустимо только как **осознанная свежесть** (тот же смысл в другом
   моменте работы), не как копия в другом слое хранения.
3. **Формат, порядок, структура.** Hot-path сверху, редкое — в project-owned
   cold surface по ссылке, секции существуют только когда меняют решение.
   Runtime-specific loading и size guidance проверяй через discovery reference,
   а не превращай в универсальный Markdown law.

Протокол и выход — [`placement-protocol.md`](placement-protocol.md).

## Findings — формат

Каждая находка через именованный режим + recommendation: move к owner / сжать до
ссылки / заострить как SoT / перестроить структуру / оставить как осознанная
свежесть. «Звучит плохо» — вкус, не finding. Рекомендуй один repair; спрашивай
только при материальной развилке по risk/scope/reversibility.
