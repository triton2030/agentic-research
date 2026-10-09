import type { CodexRun } from '../types'

type State = CodexRun['state']

// Живому прогону хватает одной метки: подробности — во второй строке, а не в
// цвете. Различаются только состояния, требующие решения, и итоги.
export const MARK: Record<State, string> = { live: '◐', lost: '⚠', ok: '●', failed: '✗' }
export const LABEL: Record<State, string> = { live: 'в работе', lost: 'без связи', ok: 'готово', failed: 'ошибка' }
export const COLOR = { live: 'claude', lost: 'warning', ok: 'success', failed: 'error' } as const
// Сначала то, что требует внимания, потом идущее, потом итоги.
const RANK: Record<State, number> = { lost: 0, live: 1, failed: 2, ok: 3 }

/** Сколько минут закончившийся прогон остаётся на виду без переключателя. */
export const KEEP_ENDED_MIN = 15

export function dur(seconds: number | null): string {
  if (seconds === null || seconds < 0) return '?'
  const s = Math.round(seconds)
  if (s < 60) return `${s}с`
  if (s < 3600) return `${Math.floor(s / 60)}м${String(s % 60).padStart(2, '0')}с`
  return `${Math.floor(s / 3600)}ч${String(Math.floor((s % 3600) / 60)).padStart(2, '0')}м`
}

const isEnded = (run: CodexRun) => run.state === 'ok' || run.state === 'failed'
const endedAt = (run: CodexRun) => run.started + (run.elapsed_s ?? 0)

/** «◐ 2 в работе · ⚠ 1 без связи · ● 3 готово»; нулевые группы не пишутся. */
export function summary(list: readonly CodexRun[]): string {
  const order: State[] = ['live', 'lost', 'ok', 'failed']
  return order
    .map(state => [state, list.filter(run => run.state === state).length] as const)
    .filter(([, n]) => n > 0)
    .map(([state, n]) => `${MARK[state]} ${n} ${LABEL[state]}`)
    .join(' · ')
}

const isStale = (run: CodexRun, now: number, mine: ReadonlySet<string>) =>
  isEnded(run) && !mine.has(run.name) && now - endedAt(run) > KEEP_ENDED_MIN * 60

/**
 * Строки панели: идущие всегда, прогоны этой сессии всегда, чужие
 * закончившиеся — недавние или по переключателю.
 */
export function visible(
  list: readonly CodexRun[], now: number, showEnded: boolean, mine: ReadonlySet<string> = new Set(),
): CodexRun[] {
  return list
    .filter(run => showEnded || !isStale(run, now, mine))
    .sort((a, b) => RANK[a.state] - RANK[b.state] || b.started - a.started)
}

export function hiddenEnded(list: readonly CodexRun[], now: number, mine: ReadonlySet<string> = new Set()): number {
  return list.filter(run => isStale(run, now, mine)).length
}

/**
 * Каталоги прогонов, запущенных командами `codex_launch.py`: последнее звено
 * пути `--run-dir`. Звено с невычисленной переменной (`$RUN`) не угадываем.
 */
export function launchedRunNames(commands: readonly string[]): string[] {
  const names: string[] = []
  for (const command of commands) {
    if (!command.includes('codex_launch.py')) continue
    const found = /--run-dir[= ]+(?:"([^"]+)"|'([^']+)'|(\S+))/.exec(command)
    const path = found?.[1] ?? found?.[2] ?? found?.[3]
    const name = path?.replace(/\/+$/, '').split('/').pop()
    if (name && !name.includes('$') && !names.includes(name)) names.push(name)
  }
  return names
}

/** Правый край первой строки: сколько идёт или как давно кончился. */
export function rowTime(run: CodexRun, now: number): string {
  return isEnded(run) ? `${dur(now - endedAt(run))} назад` : dur(run.elapsed_s)
}

/** Вторая строка: что прогон делает сейчас или чем кончился. */
export function activity(run: CodexRun): string {
  if (run.state === 'lost') return `нет событий ${dur(run.quiet_s)} — процесс, похоже, умер`
  if (run.state === 'failed') return run.last_words ? `ошибка: ${run.last_words}` : 'ошибка'
  if (run.state === 'ok') return run.last_words || 'готово'
  return run.last_words || run.task || 'думает…'
}

/** Третья строка: модель, шаги, работа и тишина живого прогона. */
export function meta(run: CodexRun): string {
  const quiet = run.state === 'live' && run.quiet_s !== null && run.quiet_s >= 60 ? `тихо ${dur(run.quiet_s)}` : ''
  return [run.tier || '?', `${run.steps}ш`, run.work, quiet].filter(Boolean).join(' · ')
}

/** Что сказать владельцу о смене состояния прогона; null — молчать. */
export function transition(name: string, before: State | undefined, run: CodexRun): string | null {
  if (before === run.state || before === undefined) return null
  if (run.state === 'ok') return `Codex ${name}: готово · ${dur(run.elapsed_s)} · ${run.steps}ш`
  if (run.state === 'failed') return `Codex ${name}: провал · ${dur(run.elapsed_s)}`
  if (run.state === 'lost') return `Codex ${name}: нет событий ${dur(run.quiet_s)} — процесс, похоже, умер`
  return null
}
