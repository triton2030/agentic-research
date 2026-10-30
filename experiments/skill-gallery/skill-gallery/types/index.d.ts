export type SkillEntry = { name: string; description: string; source: string }

declare module 'claude-code' {
  interface PluginState {
    'skill-gallery': {
      skills: Shaped<SkillEntry[]>
      favorites: Shaped<string[]>
      expanded: Shaped<string[]>
      agents: Shaped<SkillEntry[]>
      isOpen: boolean
    }
  }
}
