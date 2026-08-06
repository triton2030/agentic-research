# Gate 6b — Докажи Delta

Продолжение `gate6-bypass.md`; нумерация оттуда.

5. Для малой low-risk правки counterfactual walkthrough — design-time proxy.
   Для material/global/risky surface используй чистый cold-start with/without,
   previous-version или абляцию на непоказанном case.
6. Claim «нужная траектория стала вероятнее» требует matched runs на том же
   resolved model/settings и частоты target first act; один удачный run
   доказывает возможность, не probability shift.
7. Self-report, пересказ правила, lint и заполненный output template не являются
   behavioral evidence. Same-model critique, debate или второй проход могут
   помочь построить candidate, но не становятся независимой проверкой без
   external verifier/tool, live owner evidence либо наблюдаемого outcome.
8. Named target-model failure сверяй с
   `divergences-contract.md`; не превращай
   недатированную интуицию в постоянное свойство модели.
9. Если proof требует exact, semantic или graph evidence за пределами уже
   прочитанных instruction files, маршрутизируй его через
   `cli-recipes.md`, не дублируя чужой runbook.
10. В audit mode верни exact proposed text/delete/move и probe без edits. В
    change mode после применения проверь direct read/diff, effective chain,
    metadata/resources и smallest evidence, соответствующее реальному риску.

**Результат gate:** `predicted bypass + discriminating probe + run/proxy
evidence + claim strength + unresolved risk`. Недоступен behavioral run → назови
gap; не повышай design-time proxy до доказательства эффективности.

Далее: `output-stop.md`.
