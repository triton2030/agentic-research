import { expect, mock, test } from 'claude-code/testing'

const PANE = {
  plugin: 'skill-gallery',
  component: 'Pane',
  requestId: 'skill-gallery',
  props: {
    title: 'Skills',
    isFocused: false,
    bodyColumns: 60,
    placement: 'dock',
    scroll: { offset: 0, bodyRows: 30 },
    view: {},
  },
} as const

const COMMANDS = [
  { name: 'help', description: 'Help', source: 'builtin' },
  { name: 'zeta', description: 'Z skill', source: 'user' },
  { name: 'alpha', description: 'A skill', source: 'plugin' },
  { name: 'pk:beta', description: 'B skill', source: 'plugin' },
  { name: 'skill-gallery', description: 'self', source: 'plugin' },
]

test('a skill button puts /name into the prompt box', async ($, on) => {
  mock.store(on)
  const fills: { text: string; mode?: string }[] = []
  on('command.register', () => ({ value: { command: 'skill-gallery' } }))
  on('command.list', () => ({ value: COMMANDS }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('prompt.fill', (_, e) => {
    fills.push({ text: e.text, mode: e.mode })
    return { isFilled: true }
  })

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ ...PANE, surface })
    expect((await ui.find({ type: 'Text', text: /skills/ }))?.text).toBe('3 skills')
    expect(await ui.find({ key: 'skill:help' })).toBeUndefined()
    expect(await ui.find({ key: 'skill:skill-gallery' })).toBeUndefined()
    await ui.press({ key: 'skill:zeta' })
    await ui.unmount()
  }

  expect(fills).toEqual([
    { text: '/zeta ', mode: 'insert' },
    { text: '/zeta ', mode: 'insert' },
  ])
})

test('a star adds and removes a favorite, kept in the store', async ($, on) => {
  const held = new Map<string, unknown>()
  on('store.get', (_, e) => ({ value: held.get(e.key) }))
  on('store.set', (_, e) => {
    held.set(e.key, e.value)
    return { value: undefined }
  })
  on('command.register', () => ({ value: { command: 'skill-gallery' } }))
  on('command.list', () => ({ value: COMMANDS }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })

  expect(await ui.find({ type: 'Text', text: 'Избранное' })).toBeUndefined()
  await ui.press({ key: 'fav:zeta' })
  expect(await ui.find({ type: 'Text', text: 'Избранное' })).toBeDefined()
  expect((await ui.find({ key: 'fav:zeta' }))?.text).toBe('★')
  expect(held.get('favorites')).toEqual(['zeta'])

  await ui.press({ key: 'fav:zeta' })
  expect((await ui.find({ key: 'fav:zeta' }))?.text).toBe('☆')
  expect(held.get('favorites')).toEqual([])
  await ui.unmount()
})

test('favorites from an earlier session come back', async ($, on) => {
  mock.store(on, { favorites: ['alpha'] })
  on('command.register', () => ({ value: { command: 'skill-gallery' } }))
  on('command.list', () => ({ value: COMMANDS }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
  expect((await ui.find({ key: 'fav:alpha' }))?.text).toBe('★')
  await ui.unmount()
})

test('a pane that is not up leaves a reopen button above the prompt', async ($, on) => {
  mock.store(on)
  let opens = 0
  on('command.register', () => ({ value: { command: 'skill-gallery' } }))
  on('command.list', () => ({ value: COMMANDS }))
  // The first open is not placed (as after a close); the reopen press is.
  on('ui.open', () => {
    opens += 1
    return { value: { isPlaced: opens > 1 } }
  })
  on('ui.render', ($, e) => {
    const { Text } = $.ui.resolve(e)
    return <Text>engine</Text>
  })
  on('session.start', (_, e) => ({ cwd: e.cwd }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({
    plugin: 'skill-gallery',
    component: 'AbovePrompt',
    surface: 'desktop',
    props: {},
  } as const)

  expect((await ui.find({ key: 'reopen' }))?.text).toBe('☆ skills')
  await ui.press({ key: 'reopen' })
  expect(opens).toBe(2)
  expect(await ui.find({ key: 'reopen' })).toBeUndefined()
  expect(await ui.find({ type: 'Text', text: 'engine' })).toBeDefined()
  await ui.unmount()
})

test('skills sit in sections that fold and remember it', async ($, on) => {
  const held = new Map<string, unknown>()
  on('store.get', (_, e) => ({ value: held.get(e.key) }))
  on('store.set', (_, e) => {
    held.set(e.key, e.value)
    return { value: undefined }
  })
  on('command.register', () => ({ value: { command: 'skill-gallery' } }))
  on('command.list', () => ({ value: COMMANDS }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ ...PANE, surface })
    expect((await ui.find({ key: 'sec:Мои' }))?.text).toBe('▾ Мои 1')
    expect((await ui.find({ key: 'sec:pk' }))?.text).toBe('▾ pk 1')
    expect((await ui.find({ key: 'sec:Плагины' }))?.text).toBe('▾ Плагины 1')
    // A plugin's skill is listed by its short name, inserted by its full one.
    expect((await ui.find({ key: 'skill:pk:beta' }))?.text).toBe('beta')
    await ui.unmount()
  }

  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
  await ui.press({ key: 'sec:pk' })
  expect((await ui.find({ key: 'sec:pk' }))?.text).toBe('▸ pk 1')
  expect(await ui.find({ key: 'skill:pk:beta' })).toBeUndefined()
  expect(held.get('collapsed')).toEqual(['pk'])
  await ui.unmount()
})
