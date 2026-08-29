---
description: "Handoff <timestamp>: <одна строка о том, что в пакете>"
model: <идентификатор фактически работающей модели>
date: <тот же timestamp, YYYY-MM-DD-HHMMSS>
---

1. Read this file in full.
2. Live files and runtime state override this dated snapshot.
3. First state the next action and why, then compare the recorded HEAD with
   `git log`.

<Веты, блокеры и непроверённое состояние, меняющие продолжение.>

## Terrain Model

<Причинная модель предмета. Форма каждой цепочки:
`исходная модель или действие -> evidence или результат -> получившаяся модель`>

### <Одна независимая поправка местности — свой адресуемый блок>

<исходная модель или действие -> evidence или результат -> получившаяся модель>

## Where We Are

<Где работа остановилась. Ярлыки claim-а:
`knowledge`: <наблюдение | unverified> · `consequence`: <none | accepted
assumption | blocker | reframe>>

## Next Step

<Одно следующее действие и причина, по которой именно оно верное.>

## Anchors

- HEAD: <sha на момент записи пакета>
- recall: <captured | no qualifying evidence | blocked — и причина, если blocked>
- no recall address: <предмет позиции владельца, закрываемая развилка, последствие>
- cleanup: <названные изменения | nothing to clean | handed off>
- предыдущий полученный хендоф: <путь, если эта сессия его унаследовала>
- <точные живые адреса: файл, строка, чем важен>

## Incidents

<Гейт: новый evidence обесценил уже начатую работу или сменил маршрут.>

### <Один инцидент — свой адресуемый блок>

- прежняя модель: <во что верили до>
- триггер: <что показало, что это неверно>
- оплаченная цена: <измеренное время | unknown>
- почему нашлось поздно: <причина | unknown>
- durable исход уборки: <что изменено и где>

## Advice to the Next Agent

<Гейт: у этой сессии есть новые наблюдения, привязанные к файлу или роду
работ.>

### <Одно наблюдение — свой адресуемый блок>
