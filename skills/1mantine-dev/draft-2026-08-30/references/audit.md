# Аудит public surface Mantine

## Вход

Получай неизменный `audit_input = {packet, cohort}` только после exact cohort;
при `cohort: unknown` немедленно верни `unknown` и не строй candidate set. Literal
`packet.required_behaviors` задаёт scope, а заранее переданный candidates —
только hints, не полный список.

## Порядок

1. Сначала выведи полный relevant public candidate set из official Mantine surface
   для всех required_behaviors, сверяя installed public types; учитывай relevant
   components, hooks, forms, Styles API и package capabilities, и дай каждому
   candidate official address.
2. Затем докажи coverage каждого behavior против candidate set и верни
   `behavior → candidate → handle/residue → official_address → result/unknown`.
3. Остановись только после evidence по всем required_behaviors и candidates;
   непроверенное runtime behavior оставляй `unknown`, не выдавая routing за proof.
