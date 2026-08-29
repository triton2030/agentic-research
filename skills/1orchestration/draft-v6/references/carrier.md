# Durable carrier без живого плана

Вход: собственная launch map не имеет живого state owner-а, а cold loss дороже
переиздания. Выход: до launch создан адресуемый recovery ledger.

1. Используй объявленный project-local state owner либо создай узкий ignored
   carrier и назови его адрес.
2. Carrier адресует launch map и принимает каждый recovery-bearing transition
   до следующего зависимого хода.
3. Branch-changing decision является transition с basis и evidence.
