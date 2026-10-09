import { expect, test } from 'claude-code/testing'

import {
  activity, ago, clock, docLines, dur, hiddenEnded, launchedRunNames, meta, plainText, plural, rowTime, shortName, summary, tierLabel,
  transition, visible, workLabel,
} from '../hooks/view'
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
  expect(rowTime(run('a', 'ok', { started: NOW - 700, elapsed_s: 100 }), NOW)).toBe('10 мин назад')
  expect(activity(run('a', 'live', { last_words: '' }))).toBe('задача')
  expect(activity(run('a', 'failed', { last_words: '' }))).toBe('ошибка')
  expect(meta(run('a', 'live'))).toBe('luna 6 · max · 3 шага · тихо 7 мин')
  expect(meta(run('a', 'ok', { elapsed_s: 190 }), true)).toBe('luna 6 · max · 3 шага · 3 мин · w')
})

test('слова и имена для человека', () => {
  expect(plainText('[Отчёт сохранён в out/](</Users/a b/x.md>) и **жирный** `код`')).toBe('Отчёт сохранён в out/ и жирный код')
  expect(plainText('[Отчёт]( /Users/x/out/r.md)')).toBe('Отчёт')
  expect(shortName('20261009T1400-check-intent')).toBe('check-intent')
  expect(shortName('20261008T190301Z-4e12f560')).toBe('20261008T190301Z-4e12f560')
  expect(workLabel('2026-10-09-codex-claude-updates')).toBe('codex-claude-updates')
  expect(tierLabel('gpt-6.1-sol/medium')).toBe('sol 6.1 · medium')
  expect(tierLabel('')).toBe('?')
  expect([1, 2, 5, 11, 21, 43].map(n => plural(n, 'шаг', 'шага', 'шагов'))).toEqual(
    ['1 шаг', '2 шага', '5 шагов', '11 шагов', '21 шаг', '43 шага'])
  expect([30, 600, 7200, 200000].map(ago)).toEqual(['только что', '10 мин назад', '2 ч назад', '2 дн назад'])
})

test('из команд запуска берётся каталог прогона, переменная в имени — нет', () => {
  expect(launchedRunNames([
    'B=/x; $B/.venv/bin/python $B/codex_launch.py agent --name a --run-dir $W/codex-artifacts/20261009T1400-check-intent --prompt-file p.md',
    `python codex_launch.py agent --run-dir "/w/agents/codex-artifacts/20261009T1500-two/" --name b`,
    'python codex_launch.py agent --run-dir=$RUN --name c',
    'git status --run-dir /not/a/launch',
    'python codex_launch.py agent --run-dir $W/codex-artifacts/20261009T1400-check-intent',
  ])).toEqual(['20261009T1400-check-intent', '20261009T1500-two'])
})

test('прогон этой сессии виден и через час после конца', () => {
  const old = run('old', 'ok', { started: NOW - 3600, elapsed_s: 60 })
  expect(visible([old], NOW, false, new Set(['old'])).map(r => r.name)).toEqual(['old'])
  expect(hiddenEnded([old], NOW, new Set(['old']))).toBe(0)
})

test('история: время от старта и строки документа', () => {
  expect([null, 9, 276, 3723].map(clock)).toEqual(['  ?', '0:09', '4:36', '1:02:03'])
  expect(docLines('# Вердикт\n\n\nТекст [ссылка](x.md)\n- пункт\n  - вложенный')).toEqual([
    { heading: true, text: 'Вердикт' },
    { heading: false, text: '' },
    { heading: false, text: 'Текст ссылка' },
    { heading: false, text: '• пункт' },
    { heading: false, text: '  • вложенный' },
  ])
})
