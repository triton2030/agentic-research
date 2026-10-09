import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { CodexRun } from '../types'

// Панель для владельца, а не для Claude: ни одна строка отсюда не начинает ход
// и не попадает в контекст агента. Будит Claude по-прежнему только завершение
// фоновой карточки запуска (решение владельца 2026-08-24).
const BRIDGE = '/Users/triton/Documents/GitHub/agentic-research/experiments/codex-bridge'
const PYTHON = `${BRIDGE}/.venv/bin/python`
const WATCH = `${BRIDGE}/codex_watch.py`
const PANE = 'codex-runs'
const POLL_MS = 5000

const runs = atom({ plugin: 'codex-runs', key: 'runs' } as const, [] as CodexRun[])
const error = atom({ plugin: 'codex-runs', key: 'error' } as const, '')
const isPaneOpen = atom({ plugin: 'codex-runs', key: 'isPaneOpen' } as const, false)

const ICON: Record<CodexRun['state'], string> = { live: '▶', lost: '⚠', ok: '✓', failed: '✗' }
const COLOR = { live: 'claude', lost: 'warning', ok: 'success', failed: 'error' } as const

export function dur(seconds: number | null): string {
  if (seconds === null || seconds < 0) return '?'
  const s = Math.round(seconds)
  if (s < 60) return `${s}с`
  if (s < 3600) return `${Math.floor(s / 60)}м${String(s % 60).padStart(2, '0')}с`
  return `${Math.floor(s / 3600)}ч${String(Math.floor((s % 3600) / 60)).padStart(2, '0')}м`
}

/** Что сказать владельцу о смене состояния прогона; null — молчать. */
export function transition(name: string, before: CodexRun['state'] | undefined, run: CodexRun): string | null {
  if (before === run.state || before === undefined) return null
  if (run.state === 'ok') return `Codex ${name}: готово · ${dur(run.elapsed_s)} · ${run.steps}ш`
  if (run.state === 'failed') return `Codex ${name}: провал · ${dur(run.elapsed_s)}`
  if (run.state === 'lost') return `Codex ${name}: нет событий ${dur(run.quiet_s)} — процесс, похоже, умер`
  return null
}

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
        const r = await $.process.run([PYTHON, WATCH, 'look', '--json', cwd], { timeoutMs: 15000 })
        if (r.exitCode !== 0) {
          await update($, error, () => (r.stderr.trim().split('\n').pop() || `код ${r.exitCode}`))
          return
        }
        const list = (JSON.parse(r.stdout).runs ?? []) as CodexRun[]
        await update($, runs, () => list)
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

        const live = list.filter(run => run.state === 'live').length
        const lost = list.filter(run => run.state === 'lost').length
        $.ui.status(live || lost ? `Codex: ${live} идёт` + (lost ? ` · ${lost} пропал` : '') : undefined)
        if (live && !opened) {
          opened = true
          const shown = await $.ui.open({ id: PANE, title: 'Codex' })
          await update($, isPaneOpen, () => shown.isPlaced)
        }
        if (!live && !lost) opened = false
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
    const list = await read($, runs)
    if (e.props.hasSurvey || list.length === 0 || (await read($, isPaneOpen))) return next(e)
    const live = list.filter(run => run.state === 'live').length
    const { Box, Button, Text } = $.ui.resolve(e)
    return (
      <Box>
        <Text dimColor>{live ? `Codex: ${live} идёт ` : 'Codex: прогоны закончились '}</Text>
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
    const { Box, Text } = $.ui.resolve(e)
    const list = await read($, runs)
    const problem = await read($, error)

    return (
      <Box flexDirection="column">
        {problem !== '' && <Text color="error">мост не ответил: {problem}</Text>}
        {list.length === 0 && <Text dimColor>Прогонов Codex нет — ни живых, ни за последние 30 минут.</Text>}
        {list.map(run => (
          <Box key={run.name} flexDirection="column" marginBottom={1}>
            <Text color={COLOR[run.state]} bold={run.state === 'live'} wrap="truncate-end">
              {ICON[run.state]} {run.name} · {run.tier || '?'} · {dur(run.elapsed_s)} · {run.steps}ш
              {run.state === 'live' && run.quiet_s !== null && run.quiet_s >= 60 ? ` · тихо ${dur(run.quiet_s)}` : ''}
            </Text>
            {run.task !== '' && <Text dimColor wrap="truncate-end">  {run.task}</Text>}
            {run.last_words !== '' && <Text wrap="wrap">  {run.last_words}</Text>}
          </Box>
        ))}
      </Box>
    )
  })
}
