import { defineStore } from 'pinia'

export type EditorSaveState = 'saved' | 'saving' | 'error'

interface EditorRuntimeState {
  projectId: string | null
  projectName: string
  schemaVersion: number
  revision: number
  saveState: EditorSaveState
}

export const useEditorRuntimeStore = defineStore('editorRuntime', {
  state: (): EditorRuntimeState => ({
    projectId: null,
    projectName: 'Untitled project',
    schemaVersion: 2,
    revision: 0,
    saveState: 'saved',
  }),
  actions: {
    setProjectMeta(payload: {
      projectId?: string | null
      projectName?: string
      schemaVersion?: number
      revision?: number
    }) {
      if (payload.projectId !== undefined) this.projectId = payload.projectId
      if (payload.projectName !== undefined) this.projectName = payload.projectName
      if (payload.schemaVersion !== undefined) this.schemaVersion = payload.schemaVersion
      if (payload.revision !== undefined) this.revision = payload.revision
    },
    setSaveState(saveState: EditorSaveState) {
      this.saveState = saveState
    },
  },
})

