# Проверяемая адресная правка

Пользователь заказал добавить в 1folder-tree терминальный инструмент: gpt-5.6-sol low, дерево имён + полный скилл, свежая проверка понятности и соответствия, доступная Claude и Codex. Точные слова — intent.md и /Users/triton/Documents/My_projects/mavo3/_ops/chat-recall/2026-09-12-181341-codex-01a095bf.md.

Объект: /Users/triton/Documents/GitHub/agentic-research/skills/shared/1folder-tree/portable, байты в version.json. Исходный пакет в before/. Применимый контракт: /Users/triton/.codex/skills/1skill-creation/SKILL.md и references/refactor.md, behavior-protocol.md, check-approve.md; /Users/triton/.codex/skills/1agent-steering/SKILL.md и references/steering-science.md.

Граница: добавление одного режима и команды; старое тело/description/references не меняются. Product-specific AGENTS не передаётся; это проверка только имён и скилла. Базовый контекст Codex не заявляется отсутствующим. Требования: файлы базы не читать/не изменять; не следовать симлинкам; аргументы без shell interpolation; не выдавать усечённый/ошибочный/tool-using прогон за успешный. Результат и exact inputs сохраняются вне базы.

Evidence: test_check_tree.py и tests.txt; live-run/{run.json,events.jsonl,report.md,prompt.txt,tree.json,skill.md} после завершения прогона. Самоотчёт не заменяет чтение evidence. По одному прогону не заявляется вероятностное улучшение.

Допустимая работа: read-only review исходников и безопасные пробы в собственной временной папке. Исходники не менять, субагентов не запускать. Отчёт запиши только в указанный вызывающим файл reviews/. Верни существенные находки с адресами, отделив pass/fail/unknown для своей области. Выводы других проверяющих не читать.
