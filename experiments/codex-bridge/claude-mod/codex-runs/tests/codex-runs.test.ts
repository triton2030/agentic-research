import { expect, test } from 'claude-code/testing'

import { dur, transition } from '../hooks/register'
import type { CodexRun } from '../types'

const run = (state: CodexRun['state']): CodexRun => ({
  name: 'r1', run_dir: '/x/r1', work: 'w', tier: 'gpt-6-luna/max', task: 'задача',
  state, started: 0, elapsed_s: 75, quiet_s: 400, steps: 3, last_words: 'читаю',
})

test('длительность пишется по-русски коротко', () => {
  expect(dur(null)).toBe('?')
  expect(dur(42)).toBe('42с')
  expect(dur(75)).toBe('1м15с')
  expect(dur(3725)).toBe('1ч02м')
})

test('тост только при смене состояния и не при первом знакомстве', () => {
  expect(transition('r1', undefined, run('ok'))).toBe(null)
  expect(transition('r1', 'live', run('live'))).toBe(null)
  expect(transition('r1', 'live', run('ok'))).toBe('Codex r1: готово · 1м15с · 3ш')
  expect(transition('r1', 'live', run('failed'))).toBe('Codex r1: провал · 1м15с')
  expect(transition('r1', 'live', run('lost'))).toBe('Codex r1: нет событий 6м40с — процесс, похоже, умер')
  expect(transition('r1', 'lost', run('live'))).toBe(null)
})
