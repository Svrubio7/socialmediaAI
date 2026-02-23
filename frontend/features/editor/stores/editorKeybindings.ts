import { defineStore } from 'pinia'

export type EditorActionId =
  | 'toggle-play'
  | 'seek-forward'
  | 'seek-backward'
  | 'split'
  | 'delete-selected'
  | 'copy-selected'
  | 'paste-copied'
  | 'duplicate-selected'
  | 'toggle-snapping'
  | 'toggle-bookmark'
  | 'undo'
  | 'redo'

type KeybindingMap = Record<string, EditorActionId>

const DEFAULT_KEYBINDINGS: KeybindingMap = {
  space: 'toggle-play',
  arrowright: 'seek-forward',
  arrowleft: 'seek-backward',
  s: 'split',
  delete: 'delete-selected',
  backspace: 'delete-selected',
  'ctrl+c': 'copy-selected',
  'meta+c': 'copy-selected',
  'ctrl+v': 'paste-copied',
  'meta+v': 'paste-copied',
  'ctrl+d': 'duplicate-selected',
  'meta+d': 'duplicate-selected',
  n: 'toggle-snapping',
  b: 'toggle-bookmark',
  'ctrl+z': 'undo',
  'meta+z': 'undo',
  'ctrl+shift+z': 'redo',
  'meta+shift+z': 'redo',
}

interface EditorKeybindingState {
  version: number
  enabled: boolean
  keybindings: KeybindingMap
}

const STORAGE_KEY = 'editor-keybindings-v1'

export const useEditorKeybindingsStore = defineStore('editorKeybindings', {
  state: (): EditorKeybindingState => ({
    version: 1,
    enabled: true,
    keybindings: { ...DEFAULT_KEYBINDINGS },
  }),
  actions: {
    hydrate() {
      if (!process.client) return
      try {
        const raw = localStorage.getItem(STORAGE_KEY)
        if (!raw) return
        const parsed = JSON.parse(raw)
        if (!parsed || typeof parsed !== 'object') return
        this.version = Number(parsed.version || 1)
        this.enabled = parsed.enabled !== false
        this.keybindings = {
          ...DEFAULT_KEYBINDINGS,
          ...(parsed.keybindings || {}),
        }
      } catch {
        this.resetToDefaults()
      }
    },
    persist() {
      if (!process.client) return
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          version: this.version,
          enabled: this.enabled,
          keybindings: this.keybindings,
        })
      )
    },
    resetToDefaults() {
      this.version = 1
      this.enabled = true
      this.keybindings = { ...DEFAULT_KEYBINDINGS }
      this.persist()
    },
    setBinding(keyCombo: string, action: EditorActionId) {
      this.keybindings[keyCombo.toLowerCase()] = action
      this.persist()
    },
    removeBinding(keyCombo: string) {
      delete this.keybindings[keyCombo.toLowerCase()]
      this.persist()
    },
    setEnabled(enabled: boolean) {
      this.enabled = enabled
      this.persist()
    },
  },
})

