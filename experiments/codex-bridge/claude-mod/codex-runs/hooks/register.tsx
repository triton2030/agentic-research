import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { CodexRun, CodexStory } from '../types'
import {
  activity, COLOR, docLines, hiddenEnded, launchedRunNames, MARK, meta, plural, rowTime, shortName, storyLine, summary,
  summaryParts, tierLabel, took, transition, visible, workLabel,
} from './view'

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
// Каталоги прогонов, запущенных этой сессией: состояние сессии переживает
// перезагрузку мода, а история сессии даёт и те, что были до его загрузки.
const sessionRuns = atom({ plugin: 'codex-runs', key: 'sessionRuns' } as const, [] as string[])
// Открытая история: каталог прогона и то, что о нём отдал мост.
const selected = atom({ plugin: 'codex-runs', key: 'selected' } as const, '')
const story = atom({ plugin: 'codex-runs', key: 'story' } as const, null as CodexStory | null)
const showFullTask = atom({ plugin: 'codex-runs', key: 'showFullTask' } as const, false)
const TASK_PREVIEW_LINES = 6

async function remember($: EngineInterface, names: readonly string[]) {
  if (!names.length) return
  await update($, sessionRuns, known => [...known, ...names.filter(name => !known.includes(name))])
}

async function loadStory($: EngineInterface, runDir: string) {
  if (!runDir) return
  const r = await $.process.run([PYTHON, WATCH, 'story', runDir], { timeoutMs: 15000 })
  if (r.exitCode !== 0) {
    await update($, error, () => (r.stderr.trim().split('\n').pop() || `код ${r.exitCode}`))
    return
  }
  await update($, story, () => JSON.parse(r.stdout) as CodexStory)
}

async function openStory($: EngineInterface, runDir: string) {
  await update($, selected, () => runDir)
  await update($, showFullTask, () => false)
  await update($, story, () => null)
  await loadStory($, runDir)
}

async function showPane($: EngineInterface) {
  const shown = await $.ui.open({ id: PANE, title: 'Codex' })
  await update($, isPaneOpen, () => shown.isPlaced)
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
    const history = await $.session.messages()
    if (Array.isArray(history)) {
      const commands = history.flatMap(message =>
        message.toolUses.filter(use => use.tool === 'Bash').map(use => String(use.input.command ?? '')))
      await remember($, launchedRunNames(commands))
    }

    const poll = async () => {
      if (busy) return
      busy = true
      try {
        const mine = await read($, sessionRuns)
        const r = await $.process.run(
          [PYTHON, WATCH, 'look', '--json', '--recent-min', RECENT_MIN, '--names', mine.join(','), cwd],
          { timeoutMs: 15000 },
        )
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

        const open = await read($, selected)
        if (open) await loadStory($, open)

        const active = list.filter(run => run.state === 'live' || run.state === 'lost')
        $.ui.status(active.length ? `Codex: ${summary(active)}` : undefined)
        if (active.some(run => run.state === 'live') && !opened) {
          opened = true
          await showPane($)
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
    await showPane($)
    return {}
  })

  // Новый запуск запоминаем сразу, не дожидаясь, пока он появится в истории.
  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    if (e.command.includes('codex_launch.py')) await remember($, launchedRunNames([e.command]))
    return next(e)
  }).catch(($, e, next) => (next.called ? undefined : next(e)))

  // Маленькая кнопка справа в нижней строке под полем ввода: панель открывается
  // в любой момент, даже когда Codex сейчас не работает.
  on('ui.render', { component: 'SessionMode' }, async ($, e, next) => {
    const mine = await read($, sessionRuns)
    const live = (await read($, runs)).filter(run => run.state === 'live').length
    if (!mine.length && !live) return next(e)
    const { Box, Button, Text } = $.ui.resolve(e)
    return (
      <Box flexDirection="row">
        {e.props.modes.length > 0 && <Text dimColor>{`${e.props.modes.join(' & ')} · `}</Text>}
        <Button key="codex-footer" label={live ? `Codex ◐${live}` : `Codex ${mine.length}`} onPress={async () => {
          opened = true
          await showPane($)
        }} />
      </Box>
    )
  })

  // Закрытую панель сам не открываем заново — это выбор владельца; открыть её
  // снова можно кнопкой в нижней строке или командой /codex-runs.
  on('ui.close', async ($, e, next) => {
    if (e.id === PANE) await update($, isPaneOpen, () => false)
    return next(e)
  }).catch(($, e, next) => (next.called ? undefined : next(e)))

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Button, Text } = $.ui.resolve(e)
    const problem = await read($, error)
    const open = await read($, selected)

    if (open) {
      const shown = await read($, story)
      const isFullTask = await read($, showFullTask)
      const task = shown ? docLines(shown.task) : []
      const result = shown ? docLines(shown.report || shown.final) : []
      return (
        <Box flexDirection="column">
          <Box flexDirection="row" marginBottom={1}>
            <Button key="back" label="← все прогоны" dimColor onPress={() => update($, selected, () => '')} />
          </Box>
          {problem !== '' && <Text color="error" wrap="truncate-end">{`мост не ответил: ${problem}`}</Text>}
          {!shown && <Text dimColor>Загружаю историю…</Text>}
          {shown && (
            <Box flexDirection="column">
              <Box flexDirection="row">
                <Box flexShrink={0}><Text color={COLOR[shown.state]}>{`${MARK[shown.state]} `}</Text></Box>
                <Box flexGrow={1} flexShrink={1}><Text bold wrap="truncate-end">{shortName(shown.name)}</Text></Box>
                <Box flexShrink={0}><Text dimColor>{` ${took(shown.elapsed_s)}`}</Text></Box>
              </Box>
              <Text dimColor wrap="truncate-end">{`  ${tierLabel(shown.tier)} · ${plural(shown.steps, "шаг", "шага", "шагов")} · ${workLabel(shown.run_dir.split('/').slice(-4, -3)[0] ?? '')}`}</Text>

              <Box marginTop={1}><Text bold>Задание</Text></Box>
              {(isFullTask ? task : task.slice(0, TASK_PREVIEW_LINES)).map((line, i) => (
                <Text key={`task-${i}`} bold={line.heading} dimColor={!line.heading} wrap="wrap">{line.text || ' '}</Text>
              ))}
              {task.length > TASK_PREVIEW_LINES && (
                <Button
                  key="task-more"
                  label={isFullTask ? 'свернуть задание' : `всё задание · ещё ${task.length - TASK_PREVIEW_LINES} стр.`}
                  dimColor
                  onPress={() => update($, showFullTask, value => !value)}
                />
              )}

              <Box marginTop={1}><Text bold>Ход работы</Text></Box>
              {shown.dropped > 0 && <Text dimColor>{`  …ещё ${shown.dropped} записей раньше`}</Text>}
              {shown.items.length === 0 && <Text dimColor>  Codex пока ничего не сказал</Text>}
              {shown.items.map((item, i) => {
                const line = storyLine(item)
                return (
                  <Box key={`item-${i}`} flexDirection="row">
                    <Box flexShrink={0} width={8}><Text dimColor>{line.time.padStart(7)}</Text></Box>
                    <Box flexGrow={1} flexShrink={1}>
                      <Text
                        wrap="wrap"
                        dimColor={line.kind === 'thought'}
                        italic={line.kind === 'thought'}
                        color={line.kind === 'fail' ? 'warning' : undefined}
                      >
                        {line.text}
                      </Text>
                    </Box>
                  </Box>
                )
              })}

              {result.length > 0 && (
                <Box flexDirection="column" marginTop={1}>
                  <Text bold>{shown.report ? 'Отчёт' : 'Итог'}</Text>
                  {result.map((line, i) => (
                    <Text key={`result-${i}`} bold={line.heading} wrap="wrap">{line.text || ' '}</Text>
                  ))}
                </Box>
              )}
            </Box>
          )}
        </Box>
      )
    }

    const all = await read($, runs)
    const now = await read($, polledAt)
    const isShowingEnded = await read($, showEnded)
    const mine = new Set(await read($, sessionRuns))
    const list = visible(all, now, isShowingEnded, mine)
    const hidden = hiddenEnded(all, now, mine)
    // Одна работа на всех — пишем её один раз под сводкой, а не в каждой строке.
    const works = [...new Set(list.map(run => run.work))]
    const sharedWork = works.length === 1 ? workLabel(works[0] ?? '') : ''

    return (
      <Box flexDirection="column">
        <Box flexDirection="row">
          <Box flexGrow={1} flexShrink={1} flexDirection="row" flexWrap="wrap">
            {list.length === 0 && <Text dimColor>Прогонов Codex нет</Text>}
            {summaryParts(list).map((part, i) => (
              <Text key={part.state}>
                {i > 0 && <Text dimColor>{'  '}</Text>}
                <Text color={COLOR[part.state]}>{MARK[part.state]}</Text>
                <Text bold>{` ${part.text}`}</Text>
              </Text>
            ))}
          </Box>
          {(hidden > 0 || isShowingEnded) && (
            <Box flexShrink={0}>
              <Button
                key="toggle-ended"
                label={isShowingEnded ? 'скрыть старые' : `старые · ${hidden}`}
                dimColor
                onPress={() => update($, showEnded, value => !value)}
              />
            </Box>
          )}
        </Box>
        {sharedWork !== '' && <Text dimColor wrap="truncate-end">{sharedWork}</Text>}
        {problem !== '' && <Text color="error" wrap="truncate-end">{`мост не ответил: ${problem}`}</Text>}
        <Box flexDirection="column" marginTop={1}>
          {list.map(run => (
            <Box key={run.name} flexDirection="column" marginBottom={1}>
              <Box flexDirection="row">
                <Box flexShrink={0}>
                  <Text color={COLOR[run.state]}>{`${MARK[run.state]} `}</Text>
                </Box>
                <Box flexGrow={1} flexShrink={1}>
                  <Text bold={run.state !== 'ok'} wrap="truncate-end">{shortName(run.name)}</Text>
                </Box>
                <Box flexShrink={0} flexDirection="row">
                  <Text dimColor wrap="truncate">{` ${rowTime(run, now)} `}</Text>
                  <Button key={`open-${run.name}`} label="›" plain onPress={() => openStory($, run.run_dir)} />
                </Box>
              </Box>
              <Text wrap="truncate-end">{`  ${activity(run)}`}</Text>
              <Text dimColor wrap="truncate-end">{`  ${meta(run, sharedWork === '')}`}</Text>
            </Box>
          ))}
        </Box>
      </Box>
    )
  })
}
