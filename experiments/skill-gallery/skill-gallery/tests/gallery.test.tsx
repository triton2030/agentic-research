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

// Every section open, for tests that look at the rows.
const ALL_OPEN = ['Избранное', 'Мои', 'Команды', 'Агенты', 'Остальное']

test('a skill button puts /name into the prompt box', async ($, on) => {
  mock.store(on, { expanded: ALL_OPEN })
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
    expect((await ui.find({ type: 'Text', text: /skills/ }))?.text).toBe('3 skills · 1 commands · 0 agents')
    expect((await ui.find({ key: 'skill:help' }))?.text).toBe('help')
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
  held.set('expanded', ALL_OPEN)
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
  mock.store(on, { favorites: ['alpha'], expanded: ALL_OPEN })
  on('command.register', () => ({ value: { command: 'skill-gallery' } }))
  on('command.list', () => ({ value: COMMANDS }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
  expect((await ui.find({ key: 'fav:alpha' }))?.text).toBe('★')
  await ui.unmount()
})

const BAND = {
  plugin: 'skill-gallery',
  component: 'AbovePrompt',
  props: {
    hasSurvey: false,
    isWorking: false,
    maxRows: 20,
    bodyColumns: 80,
    scroll: { offset: 0, bodyRows: 19 },
    view: {},
  },
} as const

test('the row above the prompt has a dropdown per folder; a pick inserts and starts over', async ($, on) => {
  // Favorites no longer leave their folder in the row.
  mock.store(on, { favorites: ['zeta'] })
  const fills: string[] = []
  on('command.register', () => ({ value: { command: 'skill-gallery' } }))
  on('command.list', () => ({ value: COMMANDS }))
  on('prompt.fill', (_, e) => {
    fills.push(e.text)
    return { isFilled: true }
  })
  on('session.start', (_, e) => ({ cwd: e.cwd }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ ...BAND, surface })
    expect(await ui.find({ key: 'folder:Мои:0' })).toBeDefined()
    expect(await ui.find({ key: 'folder:Команды:0' })).toBeDefined()
    expect(await ui.find({ key: 'folder:Избранное:0' })).toBeUndefined()
    // Kept out of the row for good.
    expect(await ui.find({ key: 'folder:Остальное:0' })).toBeUndefined()
    expect(await ui.find({ key: 'folder:Агенты:0' })).toBeUndefined()
    await ui.unmount()
  }

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.select({ key: 'folder:Мои:0', value: 'zeta' })
  // Each pick draws fresh dropdowns, back on the folders' titles.
  expect(await ui.find({ key: 'folder:Мои:1' })).toBeDefined()
  await ui.select({ key: 'folder:Команды:1', value: 'help' })
  await ui.unmount()
  expect(fills).toEqual(['/zeta ', '/help '])
})

test('a plugin folder drops -skills from its name in the row', async ($, on) => {
  mock.store(on)
  const big = ['a', 'b', 'c', 'd', 'e'].map(x => ({
    name: `big-skills:${x}`,
    description: x,
    source: 'plugin',
  }))
  on('command.register', () => ({ value: { command: 'skill-gallery' } }))
  on('command.list', () => ({ value: big }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  const found = await ui.find({ key: 'folder:big-skills:0' })
  const options = found?.props.options as { value: string; label?: string }[]
  expect(options[0]).toEqual({ value: '', label: 'big 5' })
  expect(options[1]).toEqual({ value: 'big-skills:a', label: 'a' })
  await ui.unmount()
})

test('the pane no longer opens by itself', async ($, on) => {
  mock.store(on)
  let opens = 0
  on('command.register', () => ({ value: { command: 'skill-gallery' } }))
  on('command.list', () => ({ value: COMMANDS }))
  on('ui.open', () => {
    opens += 1
    return { value: { isPlaced: true } }
  })
  on('session.start', (_, e) => ({ cwd: e.cwd }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  expect(opens).toBe(0)
})

test('sections start folded, small ones go under Остальное, a title click opens', async ($, on) => {
  const held = new Map<string, unknown>()
  on('store.get', (_, e) => ({ value: held.get(e.key) }))
  on('store.set', (_, e) => {
    held.set(e.key, e.value)
    return { value: undefined }
  })
  // A plugin with five skills keeps its section; pk (one) and alpha go to Остальное.
  const big = ['a', 'b', 'c', 'd', 'e'].map(x => ({
    name: `big:${x}`,
    description: x,
    source: 'plugin',
  }))
  on('command.register', () => ({ value: { command: 'skill-gallery' } }))
  on('command.list', () => ({ value: [...COMMANDS, ...big] }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ ...PANE, surface })
    expect((await ui.find({ key: 'sec:Мои' }))?.text).toBe('▸ Мои 1')
    expect((await ui.find({ key: 'sec:Команды' }))?.text).toBe('▸ Команды 1')
    expect((await ui.find({ key: 'sec:big' }))?.text).toBe('▸ big 5')
    expect((await ui.find({ key: 'sec:Остальное' }))?.text).toBe('▸ Остальное 2')
    expect(await ui.find({ key: 'sec:pk' })).toBeUndefined()
    expect(await ui.find({ key: 'sec:Плагины' })).toBeUndefined()
    expect(await ui.find({ key: 'skill:big:a' })).toBeUndefined()
    await ui.unmount()
  }

  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
  await ui.press({ key: 'sec:big' })
  expect((await ui.find({ key: 'sec:big' }))?.text).toBe('▾ big 5')
  // A plugin's skill is listed by its short name in its own section...
  expect((await ui.find({ key: 'skill:big:a' }))?.text).toBe('a')
  await ui.press({ key: 'sec:Остальное' })
  // ...and by its full name under Остальное.
  expect((await ui.find({ key: 'skill:pk:beta' }))?.text).toBe('pk:beta')
  expect(held.get('expanded')).toEqual(['big', 'Остальное'])
  await ui.unmount()
})

test('agents the engine offers get their section and insert as @agent-name', async ($, on) => {
  const held = new Map<string, unknown>()
  held.set('expanded', ALL_OPEN)
  on('store.get', (_, e) => ({ value: held.get(e.key) }))
  on('store.set', (_, e) => {
    held.set(e.key, e.value)
    return { value: undefined }
  })
  const fills: string[] = []
  on('command.register', () => ({ value: { command: 'skill-gallery' } }))
  on('command.list', () => ({ value: COMMANDS }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('agent.offer', () => ({ isOffered: true }))
  on('prompt.fill', (_, e) => {
    fills.push(e.text)
    return { isFilled: true }
  })
  on('session.start', (_, e) => ({ cwd: e.cwd }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const provider = { plugin: 'engine', tier: 'core' } as const
  await $.agent.offer({ agent: 'Explore', description: 'x', source: 'built-in', provider })
  await $.agent.offer({ agent: 'Explore', description: 'x', source: 'built-in', provider })

  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
  expect((await ui.find({ key: 'sec:Агенты' }))?.text).toBe('▾ Агенты 1')
  expect((await ui.find({ key: 'skill:@agent-Explore' }))?.text).toBe('Explore')
  await ui.press({ key: 'skill:@agent-Explore' })
  await ui.press({ key: 'fav:@agent-Explore' })
  await ui.unmount()

  expect(held.get('favorites')).toEqual(['@agent-Explore'])
  expect(held.get('agents')).toEqual([
    { name: 'Explore', description: 'x', source: 'built-in' },
  ])

  const band = await $.ui.mount({ ...BAND, surface: 'desktop' })
  // Agents stay out of the row above the prompt.
  expect(await band.find({ key: 'folder:Агенты:0' })).toBeUndefined()
  await band.unmount()
  expect(fills).toEqual(['@agent-Explore '])
})

test('a star keeps what another session added meanwhile', async ($, on) => {
  const held = new Map<string, unknown>()
  held.set('expanded', ALL_OPEN)
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
  // Another session stars a skill after this one started.
  held.set('favorites', ['alpha'])

  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
  await ui.press({ key: 'fav:zeta' })
  expect(held.get('favorites')).toEqual(['alpha', 'zeta'])
  expect((await ui.find({ key: 'fav:alpha' }))?.text).toBe('★')
  await ui.unmount()
})
