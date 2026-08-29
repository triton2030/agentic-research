---
description: "Freeze four non-leading Claude panel packets with distinct evidence zones."
---

# Panel Packet

Вход: panel decision anchor. Выход: четыре frozen packets.

1. Каждый packet фиксирует current decision/state только как source-bound факт.
2. Каждый packet фиксирует общий вопрос, decision consequence и конечный результат.
3. Каждый packet перечисляет `Main уже читал` и даёт своей линзе другую главную raw-source zone.
4. Каждый packet фиксирует source-bound facts, material gaps, in/out/read-only boundaries и `Кругов пройдено` только числом.
5. Не передавай интерпретацию main — его rationale, diagnosis, suspected cause или desired verdict.
6. Не пересказывай метод линзы: им владеет role definition.
7. Если packets взаимозаменяемы по source zone и проверяемому consequence, переразведи их до freeze.
