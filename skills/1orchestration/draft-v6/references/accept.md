# Acceptance возвратов

Вход: mandatory packet или terminal blocker получен. Выход: return принят по
контракту либо зависимая ветка остановлена.

1. Pass существует, только если addressable evidence доказывает каждый
   `done_when`; progress и самоотчёт не доказывают.
2. Independent verifier нужен только по риску или live-контракту и не может
   быть автором проверяемой работы.
3. Иначе зафиксируй unknown/blocker и останови зависимую ветку.
4. До integration append acceptance transition в state owner.
