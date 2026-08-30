# Review v5 · round 1

Exact reviewed candidate SHA:
`48ce6a752569625136d2b0ecc5240e5450ea7877d3a03d4fc685b7d006333607`.

## Literal checker

Checker насчитал 35 body-единиц вместо авторских 13 и нашёл compound
predicates, повтор topology lookup, неоднозначный обязательный registry,
неопределённый retire scope, шесть целей intent вместо трёх, неполные
agent-default chains и отсутствие полного literal quote block.

Все семь находок приняты.

## Trajectory checker

Единственная находка: союз «реестр и корневые инструкции» превращал optional
project source в универсально обязательный registry.

Находка принята независимо от literal checker-а.

## Решение

Candidate пересобран в 14 отдельных runtime-единиц без references.

Create/update и retire получили явный scope.

Project route теперь разрешается из применимых инструкций проекта без
универсального registry.

Intent сокращён до трёх целей, defaults chains и literal owner quotes
добавлены в history.
