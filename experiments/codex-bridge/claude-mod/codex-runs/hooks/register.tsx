import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { CodexRun } from '../types'
import { activity, COLOR, hiddenEnded, LABEL, MARK, meta, rowTime, summary, transition, visible } from './view'

// Панель для владельца, а не для Claude: ни одна строка отсюда не начинает ход
// и не попадает в контекст агента. Будит Claude по-прежнему только завершение
// фоновой карточки запуска.
const BRIDGE = '/Users/triton/Documents/GitHub/agentic-research/experiments/codex-bridge'
const PYTHON = `${BRIDGE}/.venv/bin/python`
const WATCH = `${BRIDGE}/codex_watch.py`
const PANE = 'codex-runs'
const POLL_MS = 5000
// Мост отдаёт закончившиеся за два часа; сколько из них видно, решает панель.
const RECENT_MIN = '120'

const runs = atom({ plugin: 'codex-runs', key: 'runs' } as const, [] as CodexRun[])
const polledAt = atom({ plugin: 'codex-runs', key: 'polledAt' } as const, 0)
const error = atom({ plugin: 'codex-runs', key: 'error' } as const, '')
const isPaneOpen = atom({ plugin: 'codex-runs', key: 'isPaneOpen' } as const, false)
const showEnded = atom({ plugin: 'codex-runs', key: 'showEnded' } as const, false)

export const register: Register = on => {
  // Состояние модуля начинается заново при каждой перезагрузке мода: первый
  // опрос только запоминает картину, чтобы не сыпать тостами о старом.
  let seen = new Map<string, CodexRun['state']>()
  let primed = false
  let busy = false
  let opened = false

  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'codex-runs',
      description: 'Панель прогонов Codex: кто жив, модель, время, последние слова',
    })
    const cwd = await $.session.cwd()

    const poll = async () => {
      if (busy) return
      busy = true
      try {
        const r = await $.process.run([PYTHON, WATCH, 'look', '--json', '--recent-min', RECENT_MIN, cwd], { timeoutMs: 15000 })
        if (r.exitCode !== 0) {
          await update($, error, () => (r.stderr.trim().split('\n').pop() || `код ${r.exitCode}`))
          return
        }
        const data = JSON.parse(r.stdout) as { now: number; runs?: CodexRun[] }
        const list = data.runs ?? []
        await update($, runs, () => list)
        await update($, polledAt, () => data.now)
        await update($, error, () => '')

        const current = new Map(list.map(run => [run.name, run.state] as const))
        if (primed) {
          for (const run of list) {
            const said = transition(run.name, seen.get(run.name), run)
            if (said) $.ui.toast(said, { timeoutMs: 8000 })
          }
        }
        seen = current
        primed = true

        const active = list.filter(run => run.state === 'live' || run.state === 'lost')
        $.ui.status(active.length ? `Codex: ${summary(active)}` : undefined)
        if (active.some(run => run.state === 'live') && !opened) {
          opened = true
          const shown = await $.ui.open({ id: PANE, title: 'Codex' })
          await update($, isPaneOpen, () => shown.isPlaced)
        }
        if (!active.length) opened = false
      } catch (err) {
        await update($, error, () => String((err as Error)?.message ?? err))
      } finally {
        busy = false
      }
    }

    void poll()
    $.clock.every(POLL_MS, () => void poll())
    return next(e)
  })

  on('command.run', { command: 'codex-runs' }, async $ => {
    opened = true
    const shown = await $.ui.open({ id: PANE, title: 'Codex' })
    await update($, isPaneOpen, () => shown.isPlaced)
    return {}
  })

  // Закрытую панель сам не открываем заново — это выбор владельца; вместо
  // этого над полем ввода стоит кнопка, пока есть что показать.
  on('ui.close', async ($, e, next) => {
    if (e.id === PANE) await update($, isPaneOpen, () => false)
    return next(e)
  }).catch(($, e, next) => (next.called ? undefined : next(e)))

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const now = await read($, polledAt)
    const list = visible(await read($, runs), now, false)
    if (e.props.hasSurvey || list.length === 0 || (await read($, isPaneOpen))) return next(e)
    const { Box, Button, Text } = $.ui.resolve(e)
    return (
      <Box>
        <Text dimColor>{`Codex: ${summary(list)} `}</Text>
        <Button
          key="show-codex"
          label="Показать Codex"
          onPress={async () => {
            opened = true
            const shown = await $.ui.open({ id: PANE, title: 'Codex' })
            await update($, isPaneOpen, () => shown.isPlaced)
          }}
        />
      </Box>
    )
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Button, Text } = $.ui.resolve(e)
    const all = await read($, runs)
    const now = await read($, polledAt)
    const isShowingEnded = await read($, showEnded)
    const problem = await read($, error)
    const list = visible(all, now, isShowingEnded)
    const hidden = hiddenEnded(all, now)

    return (
      <Box flexDirection="column">
        <Box flexDirection="row" marginBottom={1}>
          <Box flexGrow={1}>
            <Text bold wrap="truncate-end">{summary(list) || 'Прогонов Codex нет'}</Text>
          </Box>
          {(hidden > 0 || isShowingEnded) && (
            <Button
              key="toggle-ended"
              label={isShowingEnded ? 'скрыть законченные' : `законченные (${hidden})`}
              onPress={() => update($, showEnded, value => !value)}
            />
          )}
        </Box>
        {problem !== '' && <Text color="error" wrap="truncate-end">мост не ответил: {problem}</Text>}
        {list.map(run => (
          <Box key={run.name} flexDirection="column" marginBottom={1}>
            <Box flexDirection="row">
              <Box flexGrow={1}>
                <Text color={COLOR[run.state]} bold={run.state !== 'ok'} wrap="truncate-end">
                  {MARK[run.state]} {run.name}
                </Text>
              </Box>
              <Text dimColor>{` ${LABEL[run.state]} · ${rowTime(run, now)}`}</Text>
            </Box>
            <Text wrap="truncate-end">{`  ${activity(run)}`}</Text>
            <Text dimColor wrap="truncate-end">{`  ${meta(run)}`}</Text>
          </Box>
        ))}
      </Box>
    )
  })
}
