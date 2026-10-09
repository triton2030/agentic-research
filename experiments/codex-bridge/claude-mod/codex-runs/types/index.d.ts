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

export type StoryItem = { t: number | null; kind: 'words' | 'thought' | 'fail'; text: string }

/** История одного прогона — `codex_watch.py story RUN_DIR`. */
export type CodexStory = {
  name: string
  run_dir: string
  tier: string
  task: string
  report: string
  state: CodexRun['state']
  started: number
  elapsed_s: number | null
  steps: number
  items: StoryItem[]
  dropped: number
  final: string
}

declare module 'claude-code' {
  interface PluginState {
    'codex-runs': { runs: CodexRun[]; polledAt: number; error: string; isPaneOpen: boolean; showEnded: boolean; sessionRuns: string[]; selected: string; story: CodexStory | null; showFullTask: boolean }
  }
}
