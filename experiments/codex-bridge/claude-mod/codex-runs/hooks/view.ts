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

/** «12 мин назад»: секунды у давно закончившегося — шум. */
export function ago(seconds: number): string {
  if (seconds < 60) return 'только что'
  if (seconds < 3600) return `${Math.floor(seconds / 60)} мин назад`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)} ч назад`
  return `${Math.floor(seconds / 86400)} дн назад`
}

/** «3 мин» / «1 ч 05 мин» — сколько шёл прогон. */
export function took(seconds: number | null): string {
  if (seconds === null || seconds < 0) return '?'
  if (seconds < 60) return `${Math.round(seconds)} с`
  if (seconds < 3600) return `${Math.round(seconds / 60)} мин`
  return `${Math.floor(seconds / 3600)} ч ${String(Math.round((seconds % 3600) / 60)).padStart(2, '0')} мин`
}

export function plural(n: number, one: string, few: string, many: string): string {
  const tens = n % 100
  const units = n % 10
  if (tens >= 11 && tens <= 14) return `${n} ${many}`
  if (units === 1) return `${n} ${one}`
  if (units >= 2 && units <= 4) return `${n} ${few}`
  return `${n} ${many}`
}

/** `20261009T1400-check-intent` → `check-intent`; имя без смысла оставляем как есть. */
export function shortName(name: string): string {
  const rest = name.replace(/^\d{8}T\d{4,6}Z?-/, '')
  return rest && !/^[0-9a-f]{8}$/.test(rest) ? rest : name
}

/** `2026-10-09-codex-claude-updates` → `codex-claude-updates`. */
export function workLabel(work: string): string {
  return work.replace(/^\d{4}-\d{2}-\d{2}-/, '') || work
}

/** `gpt-6.1-sol/medium` → `sol 6.1 · medium`. */
export function tierLabel(tier: string): string {
  const [model = '', effort] = tier.split('/')
  const found = /^gpt-([\d.]+)-([a-z]+)$/.exec(model)
  const name = found ? `${found[2]} ${found[1]}` : model.replace(/^gpt-/, '')
  return [name || '?', effort].filter(Boolean).join(' · ')
}

/** Слова Codex без разметки: ссылки — их текстом, без звёздочек и обратных кавычек. */
export function plainText(text: string): string {
  return text
    .replace(/\[([^\]]*)\]\((?:<[^>]*>|[^)]*)\)/g, '$1')
    .replace(/[*_`]{1,3}/g, '')
    .replace(/\s+/g, ' ')
    .trim()
}

/** Правый край первой строки: сколько идёт или как давно кончился. */
export function rowTime(run: CodexRun, now: number): string {
  return isEnded(run) ? ago(now - endedAt(run)) : dur(run.elapsed_s)
}

/** Вторая строка: что прогон делает сейчас или чем кончился. */
export function activity(run: CodexRun): string {
  const words = plainText(run.last_words)
  if (run.state === 'lost') return `нет событий ${took(run.quiet_s)} — процесс, похоже, умер`
  if (run.state === 'failed') return words ? `ошибка: ${words}` : 'ошибка'
  if (run.state === 'ok') return words || 'готово'
  return words || plainText(run.task) || 'думает…'
}

/** Третья строка: модель, шаги, длительность или тишина, работа — если их несколько. */
export function meta(run: CodexRun, showWork = false): string {
  const quiet = run.state === 'live' && run.quiet_s !== null && run.quiet_s >= 60 ? `тихо ${took(run.quiet_s)}` : ''
  return [
    tierLabel(run.tier),
    plural(run.steps, 'шаг', 'шага', 'шагов'),
    isEnded(run) ? took(run.elapsed_s) : quiet,
    showWork ? workLabel(run.work) : '',
  ].filter(Boolean).join(' · ')
}

/** Части сводки для цветной шапки: состояние и его текст. */
export function summaryParts(list: readonly CodexRun[]): { state: State; text: string }[] {
  const order: State[] = ['live', 'lost', 'ok', 'failed']
  return order
    .map(state => ({ state, n: list.filter(run => run.state === state).length }))
    .filter(part => part.n > 0)
    .map(part => ({ state: part.state, text: `${part.n} ${LABEL[part.state]}` }))
}

/** Что сказать владельцу о смене состояния прогона; null — молчать. */
export function transition(name: string, before: State | undefined, run: CodexRun): string | null {
  if (before === run.state || before === undefined) return null
  if (run.state === 'ok') return `Codex ${name}: готово · ${dur(run.elapsed_s)} · ${run.steps}ш`
  if (run.state === 'failed') return `Codex ${name}: провал · ${dur(run.elapsed_s)}`
  if (run.state === 'lost') return `Codex ${name}: нет событий ${dur(run.quiet_s)} — процесс, похоже, умер`
  return null
}
