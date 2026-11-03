export type SkillEntry = { name: string; description: string; source: string }

declare module 'claude-code' {
  interface PluginState {
    'skill-gallery': {
      skills: Shaped<SkillEntry[]>
      favorites: Shaped<string[]>
      expanded: Shaped<string[]>
      agents: Shaped<SkillEntry[]>
      // Picks from the dropdowns in the row above the prompt.
      picks: number
    }
  }
}
