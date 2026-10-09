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
    let opened = 0
    on('session.start', () => ({ cwd: '/project' }) as never)
    on('session.messages', () => ({ value: [{ role: 'assistant', text: '', toolUses: [{
      tool_use_id: 't1', tool: 'Bash',
      input: { command: 'python codex_launch.py agent --name x --run-dir /w/agents/codex-artifacts/c-old' },
    }] }] }) as never)
    on('session.cwd', () => ({ value: '/project' }) as never)
    on('command.register', () => ({ value: undefined }) as never)
    on('process.run', () => ({ value: { exitCode: 0, stdout: BRIDGE_ANSWER, stderr: '' } }) as never)
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
    // c-old кончился давно, но запущен этой сессией — виден без переключателя
    expect(await ui.find({ text: 'c-old' })).toBeDefined()

    const footer = await $.ui.mount({
      plugin: 'codex-runs', surface, component: 'SessionMode', props: { modes: ['focus'] } as never,
    })
    expect(await footer.find({ key: 'codex-footer' })).toBeDefined()
    const before = opened
    await footer.press({ key: 'codex-footer' })
    expect(opened).toBe(before + 1)
  })
}
