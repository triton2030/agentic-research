# Preservation map — background subagent candidate

| Owner invariant | Candidate location | Falsifier |
| --- | --- | --- |
| Сначала собственный поиск | Retrieval step 1 → 4 | subagent запускается до primary search |
| Ровно один, только для важной темы | Retrieval step 4 | multiple/unconditional scout route |
| Дешёвый native executor | Retrieval step 4 | fixed expensive model or shell workaround |
| Нет дешёвого native executor | Retrieval step 4 | дорогая подмена вместо primary search + gap |
| Claude может вызвать executor | Claude frontmatter `allowed-tools` | `Agent` описан, но запрещён runtime |
| Main work does not wait | Retrieval step 4 | wait/join before continuing |
| Corpus-only and read-only | Retrieval step 4 + ordinary Retrieval boundary | raw transcript or write path appears |
| Root owns application | Retrieval step 4 | subagent verdict becomes position without reread |
| Returned evidence is addressable | Retrieval step 4 + step 5 | missing address/date/age/gaps |
