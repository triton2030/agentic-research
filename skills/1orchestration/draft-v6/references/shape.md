# Выбрать форму и actor-а

Вход: каждый candidate actor получил verdict. Выход: `no-delegation`,
`controller-handoff` или собственная минимальная topology.

1. Выбери cheapest topology, сохраняющую manageable sets: root, один staged
   actor или несколько actors.
2. Назначай outcome только actor-у с доказанной достаточной способностью; exact
   implementation выбирает live runtime owner.
3. Existing specialized controller-у верни contracts и verdicts, не создавая
   свою topology.
