import { defineStore } from 'pinia'

interface EditorTimelineUiState {
  snappingEnabled: boolean
  rippleEditingEnabled: boolean
  clipboardClipIds: string[]
}

export const useEditorTimelineUiStore = defineStore('editorTimelineUi', {
  state: (): EditorTimelineUiState => ({
    snappingEnabled: true,
    rippleEditingEnabled: false,
    clipboardClipIds: [],
  }),
  actions: {
    toggleSnapping() {
      this.snappingEnabled = !this.snappingEnabled
    },
    toggleRippleEditing() {
      this.rippleEditingEnabled = !this.rippleEditingEnabled
    },
    setClipboardClipIds(ids: string[]) {
      this.clipboardClipIds = [...ids]
    },
    clearClipboard() {
      this.clipboardClipIds = []
    },
  },
})

