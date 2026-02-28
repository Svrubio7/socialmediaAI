import { computed } from 'vue'

type EditorEngine = 'legacy' | 'elevo-editor'

export const useEditorRouting = () => {
  const isForkEnabledForUser = computed(() => true)

  const legacyProjectPath = (projectId: string): string => `/editor-legacy/${projectId}`
  const forkProjectPath = (projectId: string): string => `/editor/${projectId}`

  const projectPathForEngine = (projectId: string, editorEngine?: string | null): string => {
    if (editorEngine === 'legacy') return legacyProjectPath(projectId)
    return forkProjectPath(projectId)
  }

  const projectPath = (
    projectId: string,
    options: { forceLegacy?: boolean; forceFork?: boolean; editorEngine?: EditorEngine } = {}
  ): string => {
    if (options.editorEngine) {
      return projectPathForEngine(projectId, options.editorEngine)
    }
    if (options.forceLegacy) return legacyProjectPath(projectId)
    return forkProjectPath(projectId)
  }

  return {
    editorForkEnabled: computed(() => true),
    rolloutPercent: computed(() => 100),
    isForkEnabledForUser,
    projectPath,
    projectPathForEngine,
    legacyProjectPath,
    forkProjectPath,
  }
}
