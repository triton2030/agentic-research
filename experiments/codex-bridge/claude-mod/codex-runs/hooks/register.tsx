import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { CodexRun, CodexStory } from '../types'
import {
  activity, clock, COLOR, hiddenEnded, MARK, meta, plural, rowTime, shortName, summary,
  summaryParts, tierLabel, took, transition, visible, workLabel,
} from './view'

// Панель для владельца, а не для Claude: ни одна строка отсюда не начинает ход
// и не попадает в контекст агента. Будит Claude по-прежнему только завершение
// фоновой карточки запуска.
//
// Данные — только из команд моста (`codex_watch.py look --json`, `story`);
// их поля сверяет с `types/index.d.ts` тест моста test_json_fields_match_mod_types.
// Путь к мосту зашит: установленный плагин живёт копией в кеше и не может
// вычислить репо относительно себя.
const BRIDGE = '/Users/triton/Documents/GitHub/agentic-research/experiments/codex-bridge'
const PYTHON = `${BRIDGE}/.venv/bin/python`
const WATCH = `${BRIDGE}/codex_watch.py`
const PANE = 'codex-runs'
const POLL_MS = 5000
// Мост отдаёт закончившиеся за два часа; сколько из них видно, решает панель.
const RECENT_MIN = '120'
// Разрыв между опросами больше этого — Mac спал: тосты о смене состояния
// на этом круге ложные, их не показываем.
const SLEEP_GAP_S = 60

const runs = atom({ plugin: 'codex-runs', key: 'runs' } as const, [] as CodexRun[])
const polledAt = atom({ plugin: 'codex-runs', key: 'polledAt' } as const, 0)
const error = atom({ plugin: 'codex-runs', key: 'error' } as const, '')
const isPaneOpen = atom({ plugin: 'codex-runs', key: 'isPaneOpen' } as const, false)
// Владелец сам закрыл панель — заново её не открываем, даже после перезагрузки мода.
const closedByOwner = atom({ plugin: 'codex-runs', key: 'closedByOwner' } as const, false)
const showEnded = atom({ plugin: 'codex-runs', key: 'showEnded' } as const, false)
// Открытая история: каталог прогона и то, что о нём отдал мост.
const selected = atom({ plugin: 'codex-runs', key: 'selected' } as const, '')
const story = atom({ plugin: 'codex-runs', key: 'story' } as const, null as CodexStory | null)
const showFullTask = atom({ plugin: 'codex-runs', key: 'showFullTask' } as const, false)
const TASK_PREVIEW_LINES = 6

/** Что сказал мост при отказе: последняя строка stderr, иначе stdout — туда он пишет свои падения. */
function failureOf(r: { exitCode: number; stdout: string; stderr: string }): string {
  const last = (text: string) => text.trim().split('\n').pop() ?? ''
  return last(r.stderr) || last(r.stdout) || `код ${r.exitCode}`
}

async function loadStory($: EngineInterface, runDir: string) {
  if (!runDir) return
  const r = await $.process.run([PYTHON, WATCH, 'story', runDir], { timeoutMs: 15000 })
  if (r.exitCode !== 0) {
    await update($, error, () => failureOf(r))
    return
  }
  const loaded = JSON.parse(r.stdout) as CodexStory
  // Пока шёл опрос, владелец мог открыть другой прогон — чужую историю не кладём.
  if ((await read($, selected)) === runDir) await update($, story, () => loaded)
}

async function openStory($: EngineInterface, runDir: string) {
  await update($, selected, () => runDir)
  await update($, showFullTask, () => false)
  await update($, story, () => null)
  await loadStory($, runDir)
}

async function showPane($: EngineInterface) {
  await update($, closedByOwner, () => false)
  const shown = await $.ui.open({ id: PANE, title: 'Codex' })
  await update($, isPaneOpen, () => shown.isPlaced)
}

export const register: Register = on => {
  // Состояние модуля начинается заново при каждой перезагрузке мода: первый
  // опрос только запоминает картину, чтобы не сыпать тостами о старом.
  let seen = new Map<string, CodexRun['state']>()
  let primed = false
  let busy = false
  let lastNow = 0

  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'codex-runs',
      description: 'Панель прогонов Codex: кто жив, модель, время, последние слова',
    })
    const cwd = await $.session.cwd()
    // Прогоны этой сессии мост находит по manifest.claude_session — без
    // угадывания по тексту команд.
    const sessionId = await $.session.id()

    const poll = async () => {
      if (busy) return
      busy = true
      try {
        const r = await $.process.run(
          [PYTHON, WATCH, 'look', '--json', '--recent-min', RECENT_MIN, `--session=${sessionId}`, cwd],
          { timeoutMs: 15000 },
        )
        if (r.exitCode !== 0) {
          await update($, error, () => failureOf(r))
          return
        }
        const data = JSON.parse(r.stdout) as { now: number; runs?: CodexRun[]; skipped?: number }
        const list = data.runs ?? []
        await update($, runs, () => list)
        await update($, polledAt, () => data.now)
        await update($, error, () => (data.skipped ? `не прочитано каталогов прогонов: ${data.skipped}` : ''))

        const woke = lastNow > 0 && data.now - lastNow > SLEEP_GAP_S
        lastNow = data.now
        if (primed && !woke) {
          for (const run of list) {
            const said = transition(run.name, seen.get(run.name), run)
            if (said) $.ui.toast(said, { timeoutMs: 8000 })
          }
        }
        seen = new Map(list.map(run => [run.name, run.state] as const))
        primed = true

        const open = await read($, selected)
        if (open) await loadStory($, open)

        const active = list.filter(run => run.state === 'live' || run.state === 'lost')
        $.ui.status(active.length ? `Codex: ${summary(active)}` : undefined)
        const shouldOpen = active.some(run => run.state === 'live')
          && !(await read($, isPaneOpen)) && !(await read($, closedByOwner))
        if (shouldOpen) await showPane($)
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
    await showPane($)
    return {}
  })

  // Маленькая кнопка справа в нижней строке под полем ввода: панель открывается
  // в любой момент, даже когда Codex сейчас не работает.
  on('ui.render', { component: 'SessionMode' }, async ($, e, next) => {
    const all = await read($, runs)
    const mine = all.filter(run => run.mine).length
    const live = all.filter(run => run.state === 'live').length
    if (!mine && !live) return next(e)
    const { Box, Button, Text } = $.ui.resolve(e)
    return (
      <Box flexDirection="row">
        {e.props.modes.length > 0 && <Text dimColor>{`${e.props.modes.join(' & ')} · `}</Text>}
        <Button key="codex-footer" label={live ? `Codex ◐${live}` : `Codex ${mine}`} onPress={() => showPane($)} />
      </Box>
    )
  })

  // Закрытую владельцем панель сам не открываем заново; открыть её снова можно
  // кнопкой в нижней строке или командой /codex-runs.
  on('ui.close', async ($, e, next) => {
    if (e.id === PANE) {
      await update($, isPaneOpen, () => false)
      if (e.origin.kind === 'person') await update($, closedByOwner, () => true)
    }
    return next(e)
  }).catch(($, e, next) => (next.called ? undefined : next(e)))

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Button, Markdown, Text } = $.ui.resolve(e)
    const problem = await read($, error)
    const open = await read($, selected)

    if (open) {
      const shown = await read($, story)
      const isFullTask = await read($, showFullTask)
      const taskLines = shown ? shown.task.split('\n') : []
      const task = isFullTask ? shown?.task ?? '' : taskLines.slice(0, TASK_PREVIEW_LINES).join('\n')
      const result = shown ? shown.report || shown.final : ''
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
              {task !== '' && <Markdown key="task" text={task} dimColor />}
              {taskLines.length > TASK_PREVIEW_LINES && (
                <Button
                  key="task-more"
                  label={isFullTask ? 'свернуть задание' : `всё задание · ещё ${taskLines.length - TASK_PREVIEW_LINES} стр.`}
                  dimColor
                  onPress={() => update($, showFullTask, value => !value)}
                />
              )}

              <Box marginTop={1}><Text bold>Ход работы</Text></Box>
              {shown.dropped > 0 && <Text dimColor>{`  …ещё ${shown.dropped} записей раньше`}</Text>}
              {shown.items.length === 0 && <Text dimColor>  Codex пока ничего не сказал</Text>}
              {shown.items.map((item, i) => (
                <Box key={`item-${i}`} flexDirection="row">
                  <Box flexShrink={0} width={8}><Text dimColor>{clock(item.t).padStart(7)}</Text></Box>
                  <Box flexGrow={1} flexShrink={1}>
                    {item.kind === 'fail'
                      ? <Text color="warning" wrap="wrap">{`⚠ ${item.text}`}</Text>
                      : <Markdown key={`item-md-${i}`} text={item.text} dimColor={item.kind === 'thought'} />}
                  </Box>
                </Box>
              ))}

              {result !== '' && (
                <Box flexDirection="column" marginTop={1}>
                  <Text bold>{shown.report ? 'Отчёт' : 'Итог'}</Text>
                  <Markdown key="result" text={result} />
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
    const list = visible(all, now, isShowingEnded)
    const hidden = hiddenEnded(all, now)
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
