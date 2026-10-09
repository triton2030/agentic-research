import { expect, test } from 'claude-code/testing'

import { activity, dur, hiddenEnded, meta, rowTime, summary, transition, visible } from '../hooks/view'
import type { CodexRun } from '../types'

const NOW = 100_000
const run = (name: string, state: CodexRun['state'], over: Partial<CodexRun> = {}): CodexRun => ({
  name, run_dir: `/x/${name}`, work: 'w', tier: 'gpt-6-luna/max', task: 'задача',
  state, started: NOW - 75, elapsed_s: 75, quiet_s: 400, steps: 3, last_words: 'читаю', ...over,
})

test('длительность пишется по-русски коротко', () => {
  expect(dur(null)).toBe('?')
  expect(dur(42)).toBe('42с')
  expect(dur(75)).toBe('1м15с')
  expect(dur(3725)).toBe('1ч02м')
})

test('тост только при смене состояния и не при первом знакомстве', () => {
  expect(transition('r1', undefined, run('r1', 'ok'))).toBe(null)
  expect(transition('r1', 'live', run('r1', 'live'))).toBe(null)
  expect(transition('r1', 'live', run('r1', 'ok'))).toBe('Codex r1: готово · 1м15с · 3ш')
  expect(transition('r1', 'live', run('r1', 'lost'))).toBe('Codex r1: нет событий 6м40с — процесс, похоже, умер')
})

test('сводка пропускает пустые группы', () => {
  expect(summary([])).toBe('')
  expect(summary([run('a', 'live'), run('b', 'live'), run('c', 'ok')])).toBe('◐ 2 в работе · ● 1 готово')
})

test('законченные старше 15 минут прячутся, внимание — наверх', () => {
  const old = run('old', 'ok', { started: NOW - 3600, elapsed_s: 60 })
  const fresh = run('fresh', 'failed', { started: NOW - 120, elapsed_s: 60 })
  const live = run('live', 'live', { started: NOW - 50 })
  const lost = run('lost', 'lost', { started: NOW - 5000 })
  const list = [old, fresh, live, lost]
  expect(visible(list, NOW, false).map(r => r.name)).toEqual(['lost', 'live', 'fresh'])
  expect(visible(list, NOW, true).map(r => r.name)).toEqual(['lost', 'live', 'fresh', 'old'])
  expect(hiddenEnded(list, NOW)).toBe(1)
})

test('строка одной формы: время, действие, сведения', () => {
  expect(rowTime(run('a', 'live'), NOW)).toBe('1м15с')
  expect(rowTime(run('a', 'ok', { started: NOW - 700, elapsed_s: 100 }), NOW)).toBe('10м00с назад')
  expect(activity(run('a', 'live', { last_words: '' }))).toBe('задача')
  expect(activity(run('a', 'failed', { last_words: '' }))).toBe('ошибка')
  expect(meta(run('a', 'live'))).toBe('gpt-6-luna/max · 3ш · w · тихо 6м40с')
  expect(meta(run('a', 'ok'))).toBe('gpt-6-luna/max · 3ш · w')
})
