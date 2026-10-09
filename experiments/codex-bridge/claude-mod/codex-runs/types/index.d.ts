export type CodexRun = {
  name: string
  run_dir: string
  work: string
  tier: string
  task: string
  /** live — идёт; lost — нет событий дольше трёх heartbeat; ok / failed — закончился */
  state: 'live' | 'lost' | 'ok' | 'failed'
  started: number
  elapsed_s: number | null
  quiet_s: number | null
  steps: number
  last_words: string
}

declare module 'claude-code' {
  interface PluginState {
    'codex-runs': { runs: CodexRun[]; error: string }
  }
}
