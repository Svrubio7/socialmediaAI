import { defineStore } from 'pinia'

interface EditorDiagnosticsState {
  enabled: boolean
  showTimelineOverlay: boolean
  showPlaybackOverlay: boolean
  logToConsole: boolean
  activeFixtureId: string | null
}

function toFlag(value: unknown): boolean {
  const raw = String(value ?? '').trim().toLowerCase()
  return raw === '1' || raw === 'true' || raw === 'yes' || raw === 'on'
}

export const useEditorDiagnosticsStore = defineStore('editorDiagnostics', {
  state: (): EditorDiagnosticsState => ({
    enabled: false,
    showTimelineOverlay: false,
    showPlaybackOverlay: false,
    logToConsole: false,
    activeFixtureId: null,
  }),
  actions: {
    bootstrapFromQuery(query: Record<string, unknown>) {
      const enabled = toFlag(query.diag)
      this.enabled = enabled
      if (enabled) {
        this.showTimelineOverlay = true
        this.showPlaybackOverlay = true
      }
      this.logToConsole = toFlag(query.diagLog)
      const fixture = String(query.fixture ?? '').trim()
      this.activeFixtureId = fixture || null
    },
    setEnabled(next: boolean) {
      this.enabled = Boolean(next)
      if (this.enabled && !this.showTimelineOverlay && !this.showPlaybackOverlay) {
        this.showTimelineOverlay = true
        this.showPlaybackOverlay = true
      }
    },
    setOverlayVisibility(payload: { timeline?: boolean; playback?: boolean }) {
      if (payload.timeline !== undefined) this.showTimelineOverlay = Boolean(payload.timeline)
      if (payload.playback !== undefined) this.showPlaybackOverlay = Boolean(payload.playback)
    },
    setFixture(fixtureId: string | null) {
      const trimmed = String(fixtureId ?? '').trim()
      this.activeFixtureId = trimmed || null
    },
    setLogToConsole(next: boolean) {
      this.logToConsole = Boolean(next)
    },
  },
})
