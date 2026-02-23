import type { EditorActionId } from '../stores/editorKeybindings'

export type EditorActionHandler = () => void

export const EDITOR_ACTION_LABELS: Record<EditorActionId, string> = {
  'toggle-play': 'Play / Pause',
  'seek-forward': 'Seek forward',
  'seek-backward': 'Seek backward',
  split: 'Split selected clip',
  'delete-selected': 'Delete selected',
  'copy-selected': 'Copy selected',
  'paste-copied': 'Paste',
  'duplicate-selected': 'Duplicate selected',
  'toggle-snapping': 'Toggle snapping',
  'toggle-bookmark': 'Toggle bookmark',
  undo: 'Undo',
  redo: 'Redo',
}

export function createEditorActionDispatcher() {
  const handlers = new Map<EditorActionId, EditorActionHandler>()
  return {
    register(action: EditorActionId, handler: EditorActionHandler) {
      handlers.set(action, handler)
    },
    unregister(action: EditorActionId) {
      handlers.delete(action)
    },
    dispatch(action: EditorActionId) {
      handlers.get(action)?.()
    },
  }
}

