import { expect, mock, test } from 'claude-code/testing'

import type { CodexRun } from '../types'

const NOW = 100_000
const run = (name: string, state: CodexRun['state'], over: Partial<CodexRun> = {}): CodexRun => ({
  name, run_dir: `/x/${name}`, work: 'w', tier: 'gpt-6-luna/max', task: 'задача',
  state, started: NOW - 75, elapsed_s: 75, quiet_s: 30, steps: 3, last_words: 'читаю журнал', ...over,
})
const BRIDGE_ANSWER = JSON.stringify({
  now: NOW,
  runs: [
    run('a-live', 'live'),
    run('b-done', 'ok', { started: NOW - 200, elapsed_s: 100 }),
    run('c-old', 'ok', { started: NOW - 7200, elapsed_s: 100 }),
  ],
})

for (const surface of ['terminal', 'desktop'] as const) {
  test(`панель рисуется на ${surface}: сводка, строки, переключатель`, async ($, on) => {
    mock.clock(on)
    on('session.start', () => ({ cwd: '/project' }) as never)
    on('session.cwd', () => ({ value: '/project' }) as never)
    on('command.register', () => ({ value: undefined }) as never)
    on('process.run', () => ({ value: { exitCode: 0, stdout: BRIDGE_ANSWER, stderr: '' } }) as never)
    on('ui.open', () => ({ value: { isPlaced: true } }) as never)
    on('ui.status', () => ({ value: undefined }) as never)
    on('ui.toast', () => ({ value: undefined }) as never)
    await $.session.start({ cwd: '/project', surface, isInteractive: true } as never)

    const ui = await $.ui.mount({
      plugin: 'codex-runs', surface, component: 'Pane', requestId: 'codex-runs',
      props: { title: 'Codex', isFocused: false, bodyColumns: 70, placement: 'dock', scroll: 0 } as never,
    })
    expect(await ui.find({ text: '◐ 1 в работе · ● 1 готово' })).toBeDefined()
    expect(await ui.find({ text: '  читаю журнал' })).toBeDefined()
    expect(await ui.find({ key: 'toggle-ended' })).toBeDefined()
    expect(await ui.find({ text: '● c-old' })).toBeUndefined()
    await ui.press({ key: 'toggle-ended' })
    expect(await ui.find({ text: '● c-old' })).toBeDefined()
  })
}
