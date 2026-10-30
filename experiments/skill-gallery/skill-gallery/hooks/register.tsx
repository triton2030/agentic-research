import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { SkillEntry } from '../types'

const PANE = 'skill-gallery'
const COMMAND = 'skill-gallery'
const TITLE = 'Skills'
// These outlive the session in $.store under these keys.
const FAVORITES_KEY = 'favorites'
// Sections are folded unless listed here.
const EXPANDED_KEY = 'expanded'
// The agent types last offered to the model, so a new session lists them
// before its first request.
const AGENTS_KEY = 'agents'
// A plugin section smaller than this goes under Остальное.
const MIN_SECTION = 5
// Favorites and rows name an agent by the mention that invokes it.
const AGENT_PREFIX = '@agent-'

const FAVORITES = 'Избранное'
const MINE = 'Мои'
const OTHER_PLUGINS = 'Плагины'
const COMMANDS = 'Команды'
const AGENTS = 'Агенты'
const REST = 'Остальное'

// Change a tag when that value's form changes: old stored values are then ignored.
const skills = atom({ plugin: 'skill-gallery', key: 'skills' } as const, [], {
  shape: 'skills-2',
})
const favorites = atom({ plugin: 'skill-gallery', key: 'favorites' } as const, [], {
  shape: 'favorites-1',
})
const expanded = atom({ plugin: 'skill-gallery', key: 'expanded' } as const, [], {
  shape: 'expanded-1',
})
const agents = atom({ plugin: 'skill-gallery', key: 'agents' } as const, [], {
  shape: 'agents-1',
})
const isOpen = atom({ plugin: 'skill-gallery', key: 'isOpen' } as const, false)

// Skills, plugin commands and built-in commands; MCP prompts are left out.
async function refresh($: EngineInterface) {
  const all = await $.command.list()
  const list: SkillEntry[] = all
    .filter(c => c.source !== 'mcp')
    .filter(c => c.name !== COMMAND)
    .map(c => ({ name: c.name, description: c.description, source: c.source }))
    .sort((a, b) => a.name.localeCompare(b.name))
  await update($, skills, () => list)
}

async function loadList($: EngineInterface, key: string) {
  const stored = await $.store.get(key)

  return Array.isArray(stored)
    ? stored.filter((x): x is string => typeof x === 'string')
    : []
}

async function loadAgents($: EngineInterface): Promise<SkillEntry[]> {
  const stored = await $.store.get(AGENTS_KEY)
  if (!Array.isArray(stored)) return []

  return stored.filter(
    (x): x is SkillEntry =>
      typeof x === 'object' &&
      x !== null &&
      typeof (x as SkillEntry).name === 'string' &&
      typeof (x as SkillEntry).description === 'string' &&
      typeof (x as SkillEntry).source === 'string',
  )
}

async function loadSaved($: EngineInterface) {
  const favs = await loadList($, FAVORITES_KEY)
  const opened = await loadList($, EXPANDED_KEY)
  const known = await loadAgents($)
  await update($, favorites, () => favs)
  await update($, expanded, () => opened)
  await update($, agents, () => known)
}

// Keeps an agent type the engine offered; writes only when it is new.
async function noteAgent($: EngineInterface, entry: SkillEntry) {
  const seen = await read($, agents)
  if (seen.some(a => a.name === entry.name)) return
  const stored = await loadAgents($)
  const next = [...stored.filter(a => a.name !== entry.name), entry].sort(
    (a, b) => a.name.localeCompare(b.name),
  )
  await $.store.set(AGENTS_KEY, next)
  await update($, agents, () => next)
}

function toggled(list: string[], item: string) {
  return list.includes(item) ? list.filter(x => x !== item) : [...list, item]
}

// Toggle against the store, not this session's copy: other open sessions
// may have changed it since this one started.
async function toggleFavorite($: EngineInterface, name: string) {
  const next = toggled(await loadList($, FAVORITES_KEY), name)
  await $.store.set(FAVORITES_KEY, next)
  await update($, favorites, () => next)
}

async function toggleSection($: EngineInterface, title: string) {
  const next = toggled(await loadList($, EXPANDED_KEY), title)
  await $.store.set(EXPANDED_KEY, next)
  await update($, expanded, () => next)
}

async function refreshAll($: EngineInterface) {
  await loadSaved($)
  await refresh($)
}

// An open pane may wait undrawn (no window attached yet, as right after a
// reload); it is still open. Only ui.close marks it closed.
async function openPane($: EngineInterface) {
  await $.ui.open({ id: PANE, title: TITLE })
  await update($, isOpen, () => true)
}

// A skill or command goes in as /name, an agent as its @agent-name mention.
async function insertItem($: EngineInterface, id: string) {
  const text = id.startsWith(AGENT_PREFIX) ? `${id} ` : `/${id} `
  await $.prompt.fill({ text, mode: 'insert' })
}

// "plugin:skill" goes under its plugin; the rest under Мои or Плагины.
function sectionOf(skill: SkillEntry) {
  const colon = skill.name.indexOf(':')
  if (colon > 0) return skill.name.slice(0, colon)

  if (skill.source === 'builtin') return COMMANDS

  return skill.source === 'user' ? MINE : OTHER_PLUGINS
}

function shortName(name: string) {
  const colon = name.indexOf(':')

  return colon > 0 ? name.slice(colon + 1) : name
}

function agentName(id: string) {
  return id.startsWith(AGENT_PREFIX) ? id.slice(AGENT_PREFIX.length) : id
}

type Item = { id: string; label: string }
type Section = { title: string; items: Item[] }

function sectionsOf(
  list: SkillEntry[],
  agentList: SkillEntry[],
  favs: string[],
): Section[] {
  const groups = new Map<string, Item[]>()
  const add = (title: string, item: Item) =>
    groups.set(title, [...(groups.get(title) ?? []), item])

  for (const skill of list) {
    if (favs.includes(skill.name)) continue
    const title = sectionOf(skill)
    const isPlugin = title !== MINE && title !== COMMANDS && title !== OTHER_PLUGINS
    add(title, { id: skill.name, label: isPlugin ? shortName(skill.name) : skill.name })
  }

  // Small plugin sections and loose plugin commands go under Остальное.
  const rest: Item[] = []
  for (const [title, items] of [...groups.entries()]) {
    const isCore = title === MINE || title === COMMANDS
    if (isCore || (title !== OTHER_PLUGINS && items.length >= MIN_SECTION)) continue
    rest.push(...items.map(item => ({ id: item.id, label: item.id })))
    groups.delete(title)
  }

  const agentItems = agentList
    .map(a => `${AGENT_PREFIX}${a.name}`)
    .filter(id => !favs.includes(id))
    .map(id => ({ id, label: agentName(id) }))

  const pluginTitles = [...groups.keys()]
    .filter(t => t !== MINE && t !== COMMANDS)
    .sort((a, b) => a.localeCompare(b))

  const result: Section[] = []
  const push = (title: string, items: Item[] | undefined) => {
    if (items && items.length > 0) result.push({ title, items })
  }
  push(FAVORITES, favs.map(id => ({ id, label: agentName(id) })))
  push(MINE, groups.get(MINE))
  push(COMMANDS, groups.get(COMMANDS))
  push(AGENTS, agentItems)
  for (const title of pluginTitles) push(title, groups.get(title))
  push(REST, rest.sort((a, b) => a.label.localeCompare(b.label)))

  return result
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: COMMAND,
      description: 'Open the skill gallery pane',
    })
    const result = await next(e)
    await loadSaved($)
    await refresh($)
    await openPane($)

    return result
  })

  on('command.run', { command: COMMAND }, async $ => {
    await refreshAll($)
    await openPane($)

    return { text: 'Skill gallery opened.' }
  })

  on('ui.close', async ($, e, next) => {
    const result = await next(e)
    if (e.id === PANE) await update($, isOpen, () => false)

    return result
  })

  on('agent.offer', async ($, e, next) => {
    const result = await next(e)
    await noteAgent($, { name: e.agent, description: e.description, source: e.source })

    return result
  })

  // The row above the prompt: favorites to click, and a tiny reopen button
  // while the pane is closed.
  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey) return next(e)
    const favs = await read($, favorites)
    const isClosed = !(await read($, isOpen))
    if (favs.length === 0 && !isClosed) return next(e)
    const { Box, Button, Text } = $.ui.resolve(e)

    return (
      <Box flexDirection="row" flexWrap="wrap" columnGap={2}>
        {favs.length > 0 && <Text dimColor>★</Text>}
        {favs.map(name => (
          <Button
            key={`band:${name}`}
            plain
            label={shortName(agentName(name))}
            onPress={() => insertItem($, name)}
          />
        ))}
        {isClosed && (
          <Button key="reopen" plain dimColor onPress={() => openPane($)}>
            ☆ skills
          </Button>
        )}
      </Box>
    )
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text, Button } = $.ui.resolve(e)
    const list = await read($, skills)
    const favs = await read($, favorites)
    const opened = await read($, expanded)
    // Section titles in a dark gray on the desktop; the terminal's dim elsewhere.
    const titleColor =
      e.surface === 'desktop' ? 'rgba(255, 255, 255, 0.42)' : undefined
    const agentList = await read($, agents)
    const sections = sectionsOf(list, agentList, favs)

    const row = (item: Item, isFav: boolean) => (
      <Box key={`row:${item.id}`} flexDirection="row" gap={1}>
        <Button
          key={`fav:${item.id}`}
          plain
          dimColor={!isFav}
          label={isFav ? '★' : '☆'}
          onPress={() => toggleFavorite($, item.id)}
        />
        <Button
          key={`skill:${item.id}`}
          plain
          label={item.label}
          onPress={() => insertItem($, item.id)}
        />
      </Box>
    )

    return (
      <Box flexDirection="column" gap="md">
        <Box flexDirection="row" gap={1}>
          <Text dimColor>
            {list.filter(s => s.source !== 'builtin').length} skills ·{' '}
            {list.filter(s => s.source === 'builtin').length} commands ·{' '}
            {agentList.length} agents
          </Text>
          <Button key="refresh" plain dimColor onPress={() => refreshAll($)}>
            refresh
          </Button>
        </Box>
        {sections.map(section => {
          const isFolded = !opened.includes(section.title)

          return (
            <Box
              key={`section:${section.title}`}
              flexDirection="column"
              gap="xs"
            >
              {/* The whole title row is one button that folds the section. */}
              <Button
                key={`sec:${section.title}`}
                plain
                onPress={() => toggleSection($, section.title)}
              >
                <Text bold color={titleColor} dimColor={!titleColor}>
                  {isFolded ? '▸ ' : '▾ '}
                  {section.title}
                </Text>
                <Text color={titleColor} dimColor={!titleColor}>
                  {' '}
                  {section.items.length}
                </Text>
              </Button>
              {!isFolded &&
                section.items.map(item => row(item, section.title === FAVORITES))}
            </Box>
          )
        })}
      </Box>
    )
  })
}
