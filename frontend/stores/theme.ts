/**
 * Theme store: dark | light. Persists to localStorage and applies class to document.
 */

const STORAGE_KEY = 'elevo-theme'
const LEGACY_STORAGE_KEY = 'elevoai-theme'

type Theme = 'dark' | 'light'

export const useThemeStore = defineStore('theme', {
  state: (): { mode: Theme } => ({
    mode: 'dark',
  }),

  getters: {
    isDark: (state) => state.mode === 'dark',
    isLight: (state) => state.mode === 'light',
  },

  actions: {
    setMode(mode: Theme) {
      this.mode = mode
      if (import.meta.client) {
        try {
          localStorage.setItem(STORAGE_KEY, mode)
          localStorage.removeItem(LEGACY_STORAGE_KEY)
        } catch (_) {}
        this.applyToDocument()
      }
    },

    toggle() {
      this.setMode(this.mode === 'dark' ? 'light' : 'dark')
    },

    applyToDocument() {
      if (import.meta.client && document.documentElement) {
        if (this.mode === 'dark') {
          document.documentElement.classList.add('dark')
        } else {
          document.documentElement.classList.remove('dark')
        }
      }
    },

    initialize() {
      if (import.meta.client) {
        try {
          const stored = (localStorage.getItem(STORAGE_KEY) ||
            localStorage.getItem(LEGACY_STORAGE_KEY)) as Theme | null
          if (stored === 'dark' || stored === 'light') {
            this.mode = stored
          }
        } catch (_) {}
        this.applyToDocument()

        // Cross-tab / cross-app sync: listen for storage changes from the
        // editor app or any other tab writing to the shared key.
        window.addEventListener('storage', (e: StorageEvent) => {
          if (e.key === STORAGE_KEY && (e.newValue === 'dark' || e.newValue === 'light')) {
            this.mode = e.newValue as Theme
            this.applyToDocument()
          }
        })
      }
    },
  },
})
