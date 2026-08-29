# Launch и барьер

Вход: собственная launch map и briefs готовы. Выход: mandatory packets получены
либо назван terminal blocker; зависимый ход до барьера не начат.

1. Следуй live runtime owner-у: только независимое выполняется параллельно, а
   overlapping writes сериализуются.
2. Не пересекай обязательный барьер до return или terminal blocker.
3. До пересечения барьера append recovery-bearing transition в state owner.
4. Scope change инвалидирует contract и возвращает тело к cognitive stages.
