export const CURRENT_PROJECT_SCHEMA_VERSION = 2

type AnyRecord = Record<string, any>

const DEFAULT_OUTPUT_SETTINGS = {
  width: 1920,
  height: 1080,
  fps: 30,
  bitrate: '8M',
}

function asRecord(value: unknown): AnyRecord {
  return value && typeof value === 'object' ? (value as AnyRecord) : {}
}

function asArray<T = any>(value: unknown): T[] {
  return Array.isArray(value) ? (value as T[]) : []
}

function buildDefaultState(projectName: string): AnyRecord {
  return {
    version: CURRENT_PROJECT_SCHEMA_VERSION,
    metadata: { name: projectName },
    settings: {
      fps: 30,
      canvas: { width: 1080, height: 1920 },
      background: { type: 'color', value: '#000000' },
    },
    currentSceneId: 'scene_main',
    scenes: [
      {
        id: 'scene_main',
        name: 'Scene 1',
        isMain: true,
        bookmarks: [],
        tracks: [],
      },
    ],
    timelineViewState: { zoomLevel: 1, scrollLeft: 0, playheadTime: 0 },
    projectName,
    tracks: [],
    transitions: [],
    selectedClipId: null,
    playheadTime: 0,
    timelineZoom: 1,
    outputSettings: { ...DEFAULT_OUTPUT_SETTINGS },
  }
}

export function ensureProjectStateV2(raw: unknown, projectName: string): AnyRecord {
  const state = asRecord(raw)
  if (!Object.keys(state).length) return buildDefaultState(projectName)

  const scenes = asArray<AnyRecord>(state.scenes)
  const normalizedScenes = scenes
    .filter((scene) => scene && typeof scene === 'object')
    .map((scene, index) => ({
      ...scene,
      id: String(scene.id || `scene_${index + 1}`),
      tracks: asArray(scene.tracks),
      bookmarks: asArray(scene.bookmarks),
    }))

  const currentSceneId = String(state.currentSceneId || normalizedScenes[0]?.id || 'scene_main')
  const activeScene = normalizedScenes.find((scene) => scene.id === currentSceneId) || normalizedScenes[0]
  const mainTracks = activeScene ? asArray(activeScene.tracks) : asArray(state.tracks)
  const transitions = asArray(state.transitions)
  const timelineViewState = asRecord(state.timelineViewState)
  const outputSettings = { ...DEFAULT_OUTPUT_SETTINGS, ...asRecord(state.outputSettings) }

  const normalized: AnyRecord = {
    ...state,
    version: CURRENT_PROJECT_SCHEMA_VERSION,
    metadata: { ...asRecord(state.metadata), name: asRecord(state.metadata).name || state.projectName || projectName },
    settings: {
      ...asRecord(state.settings),
      fps: Number(asRecord(state.settings).fps || DEFAULT_OUTPUT_SETTINGS.fps),
      canvas: {
        width: Number(asRecord(asRecord(state.settings).canvas).width || 1080),
        height: Number(asRecord(asRecord(state.settings).canvas).height || 1920),
      },
      background: {
        type: String(asRecord(asRecord(state.settings).background).type || 'color'),
        value: String(asRecord(asRecord(state.settings).background).value || '#000000'),
      },
    },
    currentSceneId,
    scenes: normalizedScenes.length
      ? normalizedScenes
      : [
          {
            id: 'scene_main',
            name: 'Scene 1',
            isMain: true,
            bookmarks: [],
            tracks: mainTracks,
          },
        ],
    timelineViewState: {
      zoomLevel: Number(timelineViewState.zoomLevel || state.timelineZoom || 1),
      scrollLeft: Number(timelineViewState.scrollLeft || 0),
      playheadTime: Number(timelineViewState.playheadTime || state.playheadTime || 0),
    },
    projectName: String(state.projectName || projectName),
    tracks: mainTracks,
    transitions,
    selectedClipId: state.selectedClipId ?? null,
    playheadTime: Number(state.playheadTime || timelineViewState.playheadTime || 0),
    timelineZoom: Number(state.timelineZoom || timelineViewState.zoomLevel || 1),
    outputSettings,
  }

  return normalized
}

export function extractLegacyEditorState(raw: unknown, projectName: string): AnyRecord {
  const state = ensureProjectStateV2(raw, projectName)
  return {
    projectName: String(state.projectName || projectName),
    tracks: asArray(state.tracks),
    transitions: asArray(state.transitions),
    selectedClipId: state.selectedClipId ?? null,
    playheadTime: Number(state.playheadTime || 0),
    timelineZoom: Number(state.timelineZoom || 1),
    outputSettings: { ...DEFAULT_OUTPUT_SETTINGS, ...asRecord(state.outputSettings) },
  }
}

export function buildPersistedProjectState(
  legacyEditorState: AnyRecord,
  projectName: string,
  outputSettings: AnyRecord
): AnyRecord {
  const normalizedLegacy = asRecord(legacyEditorState)
  const state = ensureProjectStateV2(normalizedLegacy, projectName)
  const tracks = asArray(normalizedLegacy.tracks)
  const transitions = asArray(normalizedLegacy.transitions)

  const currentSceneId = String(state.currentSceneId || state.scenes?.[0]?.id || 'scene_main')
  const scenes = asArray<AnyRecord>(state.scenes).map((scene) => {
    if (String(scene.id) !== currentSceneId) return scene
    return { ...scene, tracks }
  })

  return {
    ...state,
    version: CURRENT_PROJECT_SCHEMA_VERSION,
    metadata: { ...asRecord(state.metadata), name: projectName },
    projectName,
    tracks,
    transitions,
    scenes,
    currentSceneId,
    selectedClipId: normalizedLegacy.selectedClipId ?? state.selectedClipId ?? null,
    playheadTime: Number(normalizedLegacy.playheadTime ?? state.playheadTime ?? 0),
    timelineZoom: Number(normalizedLegacy.timelineZoom ?? state.timelineZoom ?? 1),
    timelineViewState: {
      ...asRecord(state.timelineViewState),
      playheadTime: Number(normalizedLegacy.playheadTime ?? state.playheadTime ?? 0),
      zoomLevel: Number(normalizedLegacy.timelineZoom ?? state.timelineZoom ?? 1),
    },
    outputSettings: { ...DEFAULT_OUTPUT_SETTINGS, ...asRecord(outputSettings) },
  }
}
