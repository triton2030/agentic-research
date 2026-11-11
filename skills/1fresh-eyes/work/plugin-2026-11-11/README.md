# Линзы Claude в папке скила — 2026-11-11

Адресная правка по решению владельца FE-10
([принципы](../../../claude/1fresh-eyes/product-frame.principles.md)).

## Что было

Профили `ladder`, `solvent`, `prospector`, `premortem` жили только в
`~/.claude/agents/` и владельца в мастерской не имели. `expansionist` лежал
у владельца и в двух установленных копиях; копия внутри установленного скила
отстала (`model: opus` против `sonnet`), потому что Claude Code папку `agents/`
обычного скила не читает.

## Что сделано

- Владельцу добавлен `.claude-plugin/plugin.json`: папка скила под
  `~/.claude/skills/` с таким файлом грузится как плагин, и её `agents/`
  регистрируются сами[^docs].
- Четыре профиля скопированы из `~/.claude/agents/` во владельца байт в байт;
  пять файлов из `~/.claude/agents/` удалены после сверки `cmp`.
- Имена профилей получили приставку плагина. В `SKILL.md` добавлен абзац
  с пятью именами, в `references/premortem.md` и `references/steering.md`
  `premortem` заменён на `1fresh-eyes:premortem`.
- Во владельца внесён абзац `references/packet.md` от 2026-11-06 о том, что
  линзы читают только файлы: прежде он был только в установленной копии.

Тексты линз, состав панели и Codex-пакет не менялись. Продуктовая пара
по-прежнему не устанавливается.

## Чем проверено

- `claude plugin validate` на владельце: проходит, одно предупреждение
  об отсутствии `author`.
- `claude plugin list --json`: `1fresh-eyes@skills-dir`, `enabled: true`.
- Свежая сессия `claude -p` на Haiku после удаления старых файлов назвала
  агентов `1fresh-eyes:expansionist`, `1fresh-eyes:ladder`,
  `1fresh-eyes:premortem`, `1fresh-eyes:prospector`, `1fresh-eyes:solvent`
  и скил `1fresh-eyes`; имён без приставки нет.

## Что не проверено

- Настоящий прогон линзы и полной панели под новыми именами.
- Загрузка в приложении Claude на компьютере владельца.

## Что знать дальше

- Сессия, открытая до правки, старых имён уже не найдёт, а новые увидит после
  `/reload-plugins` или перезапуска.
- У профиля внутри плагина Claude Code не читает поля `hooks`, `mcpServers`
  и `permissionMode`[^docs]; хук для линз ставится в `hooks/hooks.json` плагина.

[^docs]: Claude Code 2.1.322, документация от 2026-11-11:
    <https://code.claude.com/docs/en/plugins/create> (раздел «Make a plugin load
    in every session») и <https://code.claude.com/docs/en/sub-agents> (раздел
    «Choose the subagent scope»).
