import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { SkillEntry } from '../types'

const PANE = 'skill-gallery'
const COMMAND = 'skill-gallery'
const TITLE = 'Skills'
// These outlive the session in $.store under these keys.
const FAVORITES_KEY = 'favorites'
const COLLAPSED_KEY = 'collapsed'

const FAVORITES = 'Избранное'
const MINE = 'Мои'
const OTHER_PLUGINS = 'Плагины'

// Change a tag when that value's form changes: old stored values are then ignored.
const skills = atom({ plugin: 'skill-gallery', key: 'skills' } as const, [], {
  shape: 'skills-2',
})
const favorites = atom({ plugin: 'skill-gallery', key: 'favorites' } as const, [], {
  shape: 'favorites-1',
})
const collapsed = atom({ plugin: 'skill-gallery', key: 'collapsed' } as const, [], {
  shape: 'collapsed-1',
})
const isOpen = atom({ plugin: 'skill-gallery', key: 'isOpen' } as const, false)

// Skills and plugin commands; built-in commands and MCP prompts are left out.
async function refresh($: EngineInterface) {
  const all = await $.command.list()
  const list: SkillEntry[] = all
    .filter(c => c.source === 'user' || c.source === 'plugin')
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

async function loadSaved($: EngineInterface) {
  const favs = await loadList($, FAVORITES_KEY)
  const folded = await loadList($, COLLAPSED_KEY)
  await update($, favorites, () => favs)
  await update($, collapsed, () => folded)
}

function toggled(list: string[], item: string) {
  return list.includes(item) ? list.filter(x => x !== item) : [...list, item]
}

async function toggleFavorite($: EngineInterface, name: string) {
  const next = await update($, favorites, list => toggled(list, name))
  await $.store.set(FAVORITES_KEY, next)
}

async function toggleSection($: EngineInterface, title: string) {
  const next = await update($, collapsed, list => toggled(list, title))
  await $.store.set(COLLAPSED_KEY, next)
}

// An open pane may wait undrawn (no window attached yet, as right after a
// reload); it is still open. Only ui.close marks it closed.
async function openPane($: EngineInterface) {
  await $.ui.open({ id: PANE, title: TITLE })
  await update($, isOpen, () => true)
}

async function insertSkill($: EngineInterface, name: string) {
  await $.prompt.fill({ text: `/${name} `, mode: 'insert' })
}

// "plugin:skill" goes under its plugin; the rest under Мои or Плагины.
function sectionOf(skill: SkillEntry) {
  const colon = skill.name.indexOf(':')
  if (colon > 0) return skill.name.slice(0, colon)

  return skill.source === 'user' ? MINE : OTHER_PLUGINS
}

function shortName(name: string) {
  const colon = name.indexOf(':')

  return colon > 0 ? name.slice(colon + 1) : name
}

type Section = { title: string; names: string[]; isPlugin: boolean }

function sectionsOf(list: SkillEntry[], favs: string[]): Section[] {
  const groups = new Map<string, string[]>()
  for (const skill of list) {
    if (favs.includes(skill.name)) continue
    const title = sectionOf(skill)
    groups.set(title, [...(groups.get(title) ?? []), skill.name])
  }
  const rank = (t: string) => (t === MINE ? 0 : t === OTHER_PLUGINS ? 2 : 1)
  const titles = [...groups.keys()].sort(
    (a, b) => rank(a) - rank(b) || a.localeCompare(b),
  )
  const result: Section[] = titles.map(title => ({
    title,
    names: groups.get(title) ?? [],
    isPlugin: title !== MINE && title !== OTHER_PLUGINS,
  }))
  if (favs.length > 0) {
    result.unshift({ title: FAVORITES, names: favs, isPlugin: false })
  }

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
    await refresh($)
    await openPane($)

    return { text: 'Skill gallery opened.' }
  })

  on('ui.close', async ($, e, next) => {
    const result = await next(e)
    if (e.id === PANE) await update($, isOpen, () => false)

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
            label={shortName(name)}
            onPress={() => insertSkill($, name)}
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
    const folded = await read($, collapsed)
    const sections = sectionsOf(list, favs)

    const row = (name: string, label: string, isFav: boolean) => (
      <Box key={`row:${name}`} flexDirection="row" gap="sm" paddingY="xs">
        <Button
          key={`fav:${name}`}
          plain
          dimColor={!isFav}
          label={isFav ? '★' : '☆'}
          onPress={() => toggleFavorite($, name)}
        >
          <Text size="heading">{isFav ? '★' : '☆'}</Text>
        </Button>
        <Button
          key={`skill:${name}`}
          plain
          label={label}
          onPress={() => insertSkill($, name)}
        >
          <Text size="heading">{label}</Text>
        </Button>
      </Box>
    )

    return (
      <Box flexDirection="column" gap="lg">
        <Box flexDirection="row" gap={1}>
          <Text dimColor>{list.length} skills</Text>
          <Button key="refresh" plain dimColor onPress={() => refresh($)}>
            refresh
          </Button>
        </Box>
        {sections.map(section => {
          const isFolded = folded.includes(section.title)

          return (
            <Box
              key={`section:${section.title}`}
              flexDirection="column"
              gap="xs"
            >
              <Button
                key={`sec:${section.title}`}
                plain
                onPress={() => toggleSection($, section.title)}
              >
                <Text size="title" weight="bold">
                  {isFolded ? '▸ ' : '▾ '}
                  {section.title}
                </Text>
                <Text size="body" dimColor> {section.names.length}</Text>
              </Button>
              {!isFolded &&
                section.names.map(name =>
                  row(
                    name,
                    section.isPlugin ? shortName(name) : name,
                    section.title === FAVORITES,
                  ),
                )}
            </Box>
          )
        })}
      </Box>
    )
  })
}
