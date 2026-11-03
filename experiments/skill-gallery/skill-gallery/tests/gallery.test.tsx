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

test('the row above the prompt shows folders; a click lists the folder and inserts', async ($, on) => {
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
    expect((await ui.find({ key: 'folder:Команды' }))?.text).toBe('Команды 1')
    expect((await ui.find({ key: 'folder:Остальное' }))?.text).toBe('Остальное 2')
    expect(await ui.find({ key: 'folder:Избранное' })).toBeUndefined()
    expect(await ui.find({ key: 'item:zeta' })).toBeUndefined()

    await ui.press({ key: 'folder:Остальное' })
    expect((await ui.find({ key: 'folder:Остальное' }))?.text).toBe('▾ Остальное 2')
    expect((await ui.find({ key: 'item:pk:beta' }))?.text).toBe('pk:beta  B skill')
    await ui.press({ key: 'item:pk:beta' })
    // A pick closes the folder.
    expect(await ui.find({ key: 'item:pk:beta' })).toBeUndefined()
    await ui.unmount()
  }
  expect(fills).toEqual(['/pk:beta ', '/pk:beta '])
})

test('the Мои folder is a dropdown: a pick inserts and the dropdown starts over', async ($, on) => {
  mock.store(on)
  const fills: string[] = []
  on('command.register', () => ({ value: { command: 'skill-gallery' } }))
  on('command.list', () => ({ value: COMMANDS }))
  on('prompt.fill', (_, e) => {
    fills.push(e.text)
    return { isFilled: true }
  })
  on('session.start', (_, e) => ({ cwd: e.cwd }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  expect(await ui.find({ key: 'folder:Мои' })).toBeUndefined()
  await ui.select({ key: 'select:Мои:0', value: 'zeta' })
  // Each pick draws a fresh dropdown, back on the folder's title.
  expect(await ui.find({ key: 'select:Мои:1' })).toBeDefined()
  await ui.select({ key: 'select:Мои:1', value: 'zeta' })
  await ui.unmount()
  expect(fills).toEqual(['/zeta ', '/zeta '])
})

test('a second click on the open folder closes it', async ($, on) => {
  mock.store(on)
  on('command.register', () => ({ value: { command: 'skill-gallery' } }))
  on('command.list', () => ({ value: COMMANDS }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'folder:Остальное' })
  expect((await ui.find({ key: 'item:pk:beta' }))?.text).toBe('pk:beta  B skill')
  await ui.press({ key: 'folder:Остальное' })
  expect(await ui.find({ key: 'item:pk:beta' })).toBeUndefined()
  await ui.unmount()
})

test('a long folder lists every item, for the band to scroll', async ($, on) => {
  mock.store(on)
  const many = Array.from({ length: 20 }, (_, i) => ({
    name: `big:s${String(i).padStart(2, '0')}`,
    description: '',
    source: 'plugin',
  }))
  on('command.register', () => ({ value: { command: 'skill-gallery' } }))
  on('command.list', () => ({ value: many }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'folder:big' })
  expect((await ui.find({ key: 'item:big:s00' }))?.text).toBe('s00')
  expect(await ui.find({ key: 'item:big:s19' })).toBeDefined()
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

  expect(fills).toEqual(['@agent-Explore '])
  expect(held.get('favorites')).toEqual(['@agent-Explore'])
  expect(held.get('agents')).toEqual([
    { name: 'Explore', description: 'x', source: 'built-in' },
  ])

  const band = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await band.press({ key: 'folder:Агенты' })
  expect((await band.find({ key: 'item:@agent-Explore' }))?.text).toBe('Explore  x')
  await band.unmount()
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
