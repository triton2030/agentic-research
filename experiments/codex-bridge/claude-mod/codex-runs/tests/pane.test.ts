import { expect, mock, test } from 'claude-code/testing'

import type { CodexRun } from '../types'

const NOW = 100_000
const run = (name: string, state: CodexRun['state'], over: Partial<CodexRun> = {}): CodexRun => ({
  name, run_dir: `/x/${name}`, work: 'w', tier: 'gpt-6-luna/max', task: 'задача',
  state, mine: false, started: NOW - 75, elapsed_s: 75, quiet_s: 30, steps: 3, last_words: 'читаю журнал', ...over,
})
const BRIDGE_ANSWER = JSON.stringify({
  now: NOW,
  runs: [
    run('a-live', 'live'),
    run('b-done', 'ok', { started: NOW - 200, elapsed_s: 100 }),
    run('c-old', 'ok', { started: NOW - 7200, elapsed_s: 100, mine: true }),
  ],
})

const STORY_ANSWER = JSON.stringify({
  name: 'c-old', run_dir: '/w/2026-10-09-work/agents/codex-artifacts/c-old', tier: 'gpt-6.1-sol/medium',
  task: '## Контекст\nПроверь скил\n## Цель\nНайди потери', report: '# Вердикт\nРедакция держится\n- пункт один',
  state: 'ok', started: NOW - 7200, elapsed_s: 404, steps: 43, dropped: 0, final: '[Отчёт](out/r.md)',
  items: [
    { t: 10, kind: 'words', text: 'Прочитаю **роль** проверяющего' },
    { t: 39, kind: 'thought', text: 'Assessing timing' },
    { t: 276, kind: 'fail', text: 'обрыв связи с сервером — движок переподключается сам' },
  ],
})

for (const surface of ['terminal', 'desktop'] as const) {
  test(`панель рисуется на ${surface}: сводка, строки, переключатель`, async ($, on) => {
    mock.clock(on)
    let opened = 0
    on('session.start', () => ({ cwd: '/project' }) as never)
    on('session.id', () => ({ value: 'sess-1' }) as never)
    on('session.cwd', () => ({ value: '/project' }) as never)
    on('command.register', () => ({ value: undefined }) as never)
    const argvs: string[][] = []
    on('process.run', (_$, e) => {
      argvs.push([...e.argv])
      return { value: { exitCode: 0, stdout: e.argv.includes('story') ? STORY_ANSWER : BRIDGE_ANSWER, stderr: '' } } as never
    })
    on('ui.open', () => {
      opened += 1
      return { value: { isPlaced: true } } as never
    })
    on('ui.status', () => ({ value: undefined }) as never)
    on('ui.toast', () => ({ value: undefined }) as never)
    await $.session.start({ cwd: '/project', surface, isInteractive: true } as never)

    const ui = await $.ui.mount({
      plugin: 'codex-runs', surface, component: 'Pane', requestId: 'codex-runs',
      props: { title: 'Codex', isFocused: false, bodyColumns: 70, placement: 'dock', scroll: 0 } as never,
    })
    expect(await ui.find({ text: ' 1 в работе' })).toBeDefined()
    expect(await ui.find({ text: ' 2 готово' })).toBeDefined()
    expect(await ui.find({ text: '  читаю журнал' })).toBeDefined()
    // мост спрашивают про прогоны этой сессии по её id
    expect(argvs.some(argv => argv.includes('--session=sess-1'))).toBe(true)
    // c-old кончился давно, но запущен этой сессией — виден без переключателя
    expect(await ui.find({ text: 'c-old' })).toBeDefined()

    await ui.press({ key: 'open-c-old' })
    expect(await ui.find({ key: 'back' })).toBeDefined()
    expect(await ui.find({ text: 'Ход работы' })).toBeDefined()
    expect(await ui.find({ text: 'Прочитаю **роль** проверяющего' })).toBeDefined()
    expect(await ui.find({ text: '⚠ обрыв связи с сервером — движок переподключается сам' })).toBeDefined()
    expect(await ui.find({ text: 'Отчёт' })).toBeDefined()
    expect(await ui.find({ key: 'result' })).toBeDefined()
    await ui.press({ key: 'back' })
    expect(await ui.find({ key: 'open-c-old' })).toBeDefined()

    const footer = await $.ui.mount({
      plugin: 'codex-runs', surface, component: 'SessionMode', props: { modes: ['focus'] } as never,
    })
    expect(await footer.find({ key: 'codex-footer' })).toBeDefined()
    const before = opened
    await footer.press({ key: 'codex-footer' })
    expect(opened).toBe(before + 1)
  })
}
