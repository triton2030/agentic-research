# Gate 6 — Предскажи Bypass И Докажи Delta

1. До вердикта назови самый правдоподобный способ выполнить новую форму,
   сохранив старое решение: заполнить поля, процитировать rule, добавить
   self-check или отложить нужный act до финала.
2. Если bypass проходит, вернись к недостающему operator-у или point of action;
   не лечи его ещё одним `MUST` либо полем отчёта.
3. Построй различающий probe на той же representative fork: заранее назови
   expected old first act, expected proposed first act и observable scoring.
4. Сравни old/default и proposed effective chain на одной задаче; не меняй
   одновременно case, model, settings и правило.
5. Для малой low-risk правки counterfactual walkthrough — design-time proxy.
   Для material/global/risky surface используй чистый cold-start with/without,
   previous-version или абляцию на непоказанном case.
6. Claim «нужная траектория стала вероятнее» требует matched runs на том же
   resolved model/settings и частоты target first act; один удачный run
   доказывает возможность, не probability shift.

Пункты 7–10 и результат gate — [`gate6-proof.md`](gate6-proof.md).
