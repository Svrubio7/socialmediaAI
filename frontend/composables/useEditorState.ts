import { computed, ref } from 'vue'

export type EditorTrackType = 'video' | 'graphics' | 'audio' | 'layer'
export type EditorClipType = 'video' | 'text' | 'image' | 'shape' | 'audio'
export type EditorLayerGroup = 'video' | 'graphics' | 'audio'
export type EditorFitMode = 'fit' | 'fill' | 'stretch'
export type EditorTransitionName = 'Cross fade' | 'Hard wipe'
export type EditorShapeType = 'square' | 'circle' | 'outline' | 'arrow'

export interface EditorClip {
  id: string
  type: EditorClipType
  label: string
  startTime: number
  duration: number
  layer?: number
  layerGroup?: EditorLayerGroup
  sourceId?: string
  sourceUrl?: string
  posterUrl?: string
  trimStart?: number
  trimEnd?: number
  crop?: { x: number; y: number; width: number; height: number } // normalized source crop (0..1)
  aspectRatio?: string
  fitMode?: EditorFitMode
  effects?: {
    fadeIn?: number
    fadeOut?: number
    transition?: EditorTransitionName
    transitionDuration?: number
    transitionWith?: string
    audioFadeIn?: number
    audioFadeOut?: number
    speed?: number
    filter?: string
    brightness?: number
    contrast?: number
    saturation?: number
    gamma?: number
    hue?: number
    blur?: number
    opacity?: number
    volume?: number
    blendMode?: string
    overlayColor?: string
    overlayOpacity?: number
    overlayBlend?: string
  }
  position?: { x: number; y: number } // % of canvas (0..100)
  size?: { width: number; height: number } // % of canvas (0..100)
  rotation?: number
  lockAspectRatio?: boolean
  text?: string
  style?: {
    color?: string
    outline?: boolean
    opacity?: number
    shapeType?: EditorShapeType
  }
  keyframes?: Array<{
    time: number
    position?: { x: number; y: number }
    size?: { width: number; height: number }
    rotation?: number
    opacity?: number
  }>
}

export interface EditorTrack {
  id: string
  type: EditorTrackType
  label: string
  clips: EditorClip[]
  layer?: number
  group?: EditorLayerGroup
  isHeader?: boolean
}

interface EditorSnapshot {
  projectName: string
  tracks: EditorTrack[]
  transitions?: Array<Record<string, any>>
  selectedClipId: string | null
  playheadTime: number
  timelineZoom: number
}

interface EditorHistoryCommand {
  undo: () => void
  redo: () => void
}

const MIN_DURATION = 0.1
const HISTORY_LIMIT = 240
let clipCounter = 0
const SUPPORTED_TRANSITIONS: EditorTransitionName[] = ['Cross fade', 'Hard wipe']

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value))
}

function deepClone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T
}

function normalizeTransitionName(value?: string): EditorTransitionName | undefined {
  if (!value) return undefined
  if (SUPPORTED_TRANSITIONS.includes(value as EditorTransitionName)) {
    return value as EditorTransitionName
  }
  const key = value.trim().toLowerCase()
  if (!key || key === 'none' || key === 'cut') return undefined
  if (key === 'crossfade' || key === 'fade') return 'Cross fade'
  if (key.includes('wipe')) return 'Hard wipe'
  return undefined
}

function normalizeCrop(input?: { x?: number; y?: number; width?: number; height?: number }) {
  if (!input) return { x: 0, y: 0, width: 1, height: 1 }
  const x = clamp(Number(input.x ?? 0), 0, 1)
  const y = clamp(Number(input.y ?? 0), 0, 1)
  const width = clamp(Number(input.width ?? 1), 0.05, 1)
  const height = clamp(Number(input.height ?? 1), 0.05, 1)
  const clampedWidth = Math.min(width, 1 - x)
  const clampedHeight = Math.min(height, 1 - y)
  return {
    x,
    y,
    width: Math.max(0.05, clampedWidth),
    height: Math.max(0.05, clampedHeight),
  }
}

function normalizeShapeType(value?: string): EditorShapeType {
  const next = (value ?? '').trim().toLowerCase()
  if (next === 'circle') return 'circle'
  if (next === 'outline') return 'outline'
  if (next === 'arrow') return 'arrow'
  return 'square'
}

function createInitialTracks(): EditorTrack[] {
  return [
    { id: 'track-video', type: 'video', label: 'Video', clips: [] },
    { id: 'track-graphics', type: 'graphics', label: 'Graphics', clips: [] },
    { id: 'track-audio', type: 'audio', label: 'Audio', clips: [] },
  ]
}

function nextClipId(prefix: string = 'clip') {
  clipCounter += 1
  return `${prefix}-${Date.now()}-${clipCounter}`
}

function findClip(tracks: EditorTrack[], clipId: string) {
  for (const track of tracks) {
    const index = track.clips.findIndex((clip) => clip.id === clipId)
    if (index !== -1) return { track, index, clip: track.clips[index] }
  }
  return null
}

export function useEditorState() {
  const projectName = ref('Untitled project')
  const tracks = ref<EditorTrack[]>(createInitialTracks())
  const transitions = ref<Array<Record<string, any>>>([])
  const selectedClipId = ref<string | null>(null)
  const playheadTime = ref(0)
  const timelineZoom = ref(1)
  const undoStack = ref<EditorHistoryCommand[]>([])
  const redoStack = ref<EditorHistoryCommand[]>([])

  const clips = computed(() => tracks.value.flatMap((track) => track.clips))

  const duration = computed(() => {
    return clips.value.reduce((max, clip) => {
      return Math.max(max, clip.startTime + clip.duration)
    }, 0)
  })

  const selectedClip = computed(() => {
    if (!selectedClipId.value) return null
    return clips.value.find((clip) => clip.id === selectedClipId.value) ?? null
  })

  const canUndo = computed(() => undoStack.value.length > 0)
  const canRedo = computed(() => redoStack.value.length > 0)

  function snapshot(): EditorSnapshot {
    return {
      projectName: projectName.value,
      tracks: deepClone(tracks.value),
      transitions: deepClone(transitions.value),
      selectedClipId: selectedClipId.value,
      playheadTime: playheadTime.value,
      timelineZoom: timelineZoom.value,
    }
  }

  function clearHistory() {
    undoStack.value = []
    redoStack.value = []
  }

  function pushUndoCommand(command: EditorHistoryCommand) {
    undoStack.value.push(command)
    if (undoStack.value.length > HISTORY_LIMIT) undoStack.value.shift()
    redoStack.value = []
  }

  function executeCommand(command: EditorHistoryCommand) {
    command.redo()
    pushUndoCommand(command)
  }

  function findTrackById(trackId: string) {
    return tracks.value.find((track) => track.id === trackId)
  }

  function replaceClipInTrack(trackId: string, clipId: string, clip: EditorClip) {
    const track = findTrackById(trackId)
    if (!track) return false
    const index = track.clips.findIndex((entry) => entry.id === clipId)
    if (index === -1) return false
    track.clips.splice(index, 1, deepClone(clip))
    sortTrackClips(track)
    return true
  }

  function removeClipFromTrack(trackId: string, clipId: string) {
    const track = findTrackById(trackId)
    if (!track) return null
    const index = track.clips.findIndex((entry) => entry.id === clipId)
    if (index === -1) return null
    const [removed] = track.clips.splice(index, 1)
    return { track, index, clip: removed }
  }

  function upsertClipOnTrack(trackId: string, clip: EditorClip) {
    const track = findTrackById(trackId)
    if (!track) return false
    const index = track.clips.findIndex((entry) => entry.id === clip.id)
    if (index === -1) {
      track.clips.push(deepClone(clip))
    } else {
      track.clips.splice(index, 1, deepClone(clip))
    }
    sortTrackClips(track)
    return true
  }

  function buildUpdatedClip(current: EditorClip, patch: Partial<EditorClip>) {
    const nextType = (patch.type ?? current.type) as EditorClipType
    const nextClip: EditorClip = {
      ...current,
      ...patch,
      effects: patch.effects
        ? {
            ...current.effects,
            ...patch.effects,
            transition: normalizeTransitionName(
              patch.effects.transition ?? current.effects?.transition
            ),
          }
        : current.effects,
      crop: patch.crop ? normalizeCrop(patch.crop) : current.crop,
      position: patch.position
        ? { ...current.position, ...patch.position }
        : current.position,
      size: patch.size ? { ...current.size, ...patch.size } : current.size,
      style: patch.style
        ? {
            ...current.style,
            ...patch.style,
            ...(nextType === 'shape'
              ? {
                  shapeType: normalizeShapeType(
                    patch.style.shapeType ??
                      current.style?.shapeType ??
                      current.label
                  ),
                }
              : {}),
          }
        : current.style,
    }

    nextClip.startTime = Math.max(0, nextClip.startTime)
    nextClip.duration = Math.max(MIN_DURATION, nextClip.duration)
    const clipLayerGroup = nextClip.layerGroup ?? inferLayerGroup(nextClip.type)
    const clipLayer = nextClip.layer ?? 1
    nextClip.startTime = clampStartInLayer(
      clipLayerGroup,
      clipLayer,
      nextClip.id,
      nextClip.startTime,
      nextClip.duration
    )
    if (nextClip.effects && !nextClip.effects.transition) {
      nextClip.effects.transitionDuration = undefined
      nextClip.effects.transitionWith = undefined
    }
    return nextClip
  }

  function restoreSnapshot(state: EditorSnapshot) {
    projectName.value = state.projectName
    tracks.value = deepClone(state.tracks)
    transitions.value = deepClone(state.transitions ?? [])
    selectedClipId.value = state.selectedClipId
    playheadTime.value = state.playheadTime
    timelineZoom.value = state.timelineZoom
  }

  function inferLayerGroup(type: EditorClipType): EditorLayerGroup {
    if (type === 'audio') return 'audio'
    if (type === 'video') return 'video'
    return 'graphics'
  }

  function nextLayerIndex(group: EditorLayerGroup) {
    const maxLayer = tracks.value
      .flatMap((track) => track.clips)
      .filter((clip) => (clip.layerGroup ?? inferLayerGroup(clip.type)) === group)
      .reduce((max, clip) => Math.max(max, clip.layer ?? 0), 0)
    return maxLayer + 1
  }

  function sortTrackClips(track: EditorTrack) {
    track.clips.sort((a, b) => a.startTime - b.startTime)
  }

  function clampStartInLayer(layerGroup: EditorLayerGroup, layer: number, clipId: string | null, desiredStart: number, clipDuration: number) {
    const peers = tracks.value
      .flatMap((track) => track.clips)
      .filter((clip) => {
        const group = clip.layerGroup ?? inferLayerGroup(clip.type)
        const sameLayer = (clip.layer ?? 1) === layer
        if (clipId && clip.id === clipId) return false
        return group === layerGroup && sameLayer
      })
      .slice()
      .sort((a, b) => a.startTime - b.startTime)
    const desired = Math.max(0, desiredStart)
    const prev = peers.filter((clip) => clip.startTime + clip.duration <= desired).pop()
    const next = peers.find((clip) => clip.startTime >= desired)
    const minStart = prev ? prev.startTime + prev.duration : 0
    const maxStart = next ? next.startTime - clipDuration : Number.POSITIVE_INFINITY
    if (maxStart < minStart) return minStart
    return clamp(desired, minStart, maxStart)
  }

  function setProjectName(value: string) {
    projectName.value = value.trim() || 'Untitled project'
  }

  function exportState(): EditorSnapshot {
    return snapshot()
  }

  function loadState(state: Partial<EditorSnapshot>) {
    projectName.value = state.projectName ?? projectName.value
    const loadedTracks = state.tracks ? deepClone(state.tracks) : createInitialTracks()
    tracks.value = loadedTracks.map((track) => ({
      ...track,
      clips: (track.clips ?? []).map((clip) => {
        const effects = clip.effects ?? {}
        return {
          ...clip,
          crop: normalizeCrop(clip.crop),
          effects: {
            ...effects,
            transition: normalizeTransitionName(effects.transition),
            transitionDuration: normalizeTransitionName(effects.transition) ? effects.transitionDuration : undefined,
            transitionWith: normalizeTransitionName(effects.transition) ? effects.transitionWith : undefined,
          },
          style: clip.style
            ? {
                ...clip.style,
                ...(clip.type === 'shape'
                  ? { shapeType: normalizeShapeType(clip.style.shapeType || clip.label) }
                  : {}),
              }
            : (clip.type === 'shape' ? { shapeType: 'square' } : undefined),
        }
      }),
    }))
    transitions.value = deepClone((state.transitions as Array<Record<string, any>> | undefined) ?? [])
    selectedClipId.value = state.selectedClipId ?? null
    playheadTime.value = state.playheadTime ?? 0
    timelineZoom.value = state.timelineZoom ?? 1
    clearHistory()
  }

  function resetState() {
    loadState({
      projectName: projectName.value,
      tracks: createInitialTracks(),
      selectedClipId: null,
      playheadTime: 0,
      timelineZoom: 1,
    })
  }

  function setSourceVideoClip(payload: {
    sourceId: string
    sourceUrl?: string
    posterUrl?: string
    label: string
    duration: number
    aspectRatio?: string
  }) {
    const videoClip: EditorClip = {
      id: nextClipId('video'),
      type: 'video',
      label: payload.label || 'Video clip',
      startTime: 0,
      duration: Math.max(MIN_DURATION, payload.duration || 1),
      layer: 1,
      layerGroup: 'video',
      position: { x: 0, y: 0 },
      size: { width: 100, height: 100 },
      sourceId: payload.sourceId,
      sourceUrl: payload.sourceUrl,
      posterUrl: payload.posterUrl,
      trimStart: 0,
      trimEnd: Math.max(MIN_DURATION, payload.duration || 1),
      aspectRatio: payload.aspectRatio ?? '16:9',
      fitMode: 'fit',
      effects: {
        fadeIn: 0,
        fadeOut: 0,
        transition: undefined,
        transitionDuration: undefined,
        transitionWith: undefined,
        audioFadeIn: 0,
        audioFadeOut: 0,
        speed: 1,
        filter: 'None',
        brightness: 0,
        contrast: 1,
        saturation: 1,
        gamma: 1,
        hue: 0,
        blur: 0,
        opacity: 1,
        volume: 1,
        blendMode: 'normal',
        overlayColor: 'transparent',
        overlayOpacity: 0,
        overlayBlend: 'soft-light',
      },
    }

    const audioClip: EditorClip = {
      id: nextClipId('audio'),
      type: 'audio',
      label: 'Source audio',
      startTime: 0,
      duration: Math.max(MIN_DURATION, payload.duration || 1),
      layer: 1,
      layerGroup: 'audio',
      sourceId: payload.sourceId,
    }

    const nextTracks = createInitialTracks()
    nextTracks.find((track) => track.type === 'video')!.clips = [videoClip]
    nextTracks.find((track) => track.type === 'audio')!.clips = [audioClip]

    const previousState = snapshot()
    const nextState: EditorSnapshot = {
      projectName: projectName.value,
      tracks: nextTracks,
      selectedClipId: videoClip.id,
      playheadTime: 0,
      timelineZoom: timelineZoom.value,
    }

    executeCommand({
      undo() {
        restoreSnapshot(previousState)
      },
      redo() {
        restoreSnapshot(nextState)
      },
    })
  }

  function addClip(trackType: EditorTrackType, clipInput: Partial<EditorClip>) {
    const track = tracks.value.find((item) => item.type === trackType)
    if (!track) return null

    const baseEffects = {
      fadeIn: 0,
      fadeOut: 0,
      transition: undefined,
      transitionDuration: undefined,
      transitionWith: undefined,
      audioFadeIn: 0,
      audioFadeOut: 0,
      speed: 1,
      filter: 'None',
      brightness: 0,
      contrast: 1,
      saturation: 1,
      gamma: 1,
      hue: 0,
      blur: 0,
      opacity: 1,
      volume: 1,
      blendMode: 'normal',
      overlayColor: 'transparent',
      overlayOpacity: 0,
      overlayBlend: 'soft-light',
    }

    const resolvedType = (clipInput.type ?? (trackType === 'audio' ? 'audio' : trackType === 'video' ? 'video' : 'shape')) as EditorClipType
    const resolvedGroup = clipInput.layerGroup ?? inferLayerGroup(resolvedType)

    const clip: EditorClip = {
      id: clipInput.id ?? nextClipId(trackType),
      type: resolvedType,
      label: clipInput.label ?? 'Clip',
      startTime: Math.max(0, clipInput.startTime ?? playheadTime.value),
      duration: Math.max(MIN_DURATION, clipInput.duration ?? 3),
      layer: clipInput.layer ?? nextLayerIndex(resolvedGroup),
      layerGroup: resolvedGroup,
      sourceId: clipInput.sourceId,
      sourceUrl: clipInput.sourceUrl,
      posterUrl: clipInput.posterUrl,
      trimStart: clipInput.trimStart,
      trimEnd: clipInput.trimEnd,
      crop: clipInput.type === 'video' || resolvedType === 'video' ? normalizeCrop(clipInput.crop) : undefined,
      aspectRatio: clipInput.aspectRatio,
      fitMode: clipInput.fitMode ?? 'fit',
      effects: clipInput.effects
        ? {
            ...baseEffects,
            ...clipInput.effects,
            transition: normalizeTransitionName(clipInput.effects.transition),
          }
        : { ...baseEffects },
      position: clipInput.position ? { ...clipInput.position } : undefined,
      size: clipInput.size ? { ...clipInput.size } : undefined,
      rotation: clipInput.rotation ?? 0,
      lockAspectRatio: clipInput.lockAspectRatio ?? true,
      text: clipInput.text,
      style: clipInput.style
        ? {
            ...clipInput.style,
            ...(resolvedType === 'shape'
              ? { shapeType: normalizeShapeType(clipInput.style.shapeType || clipInput.label) }
              : {}),
          }
        : (resolvedType === 'shape' ? { shapeType: normalizeShapeType(clipInput.label) } : undefined),
    }

    if (clip.effects && !clip.effects.transition) {
      clip.effects.transitionDuration = undefined
      clip.effects.transitionWith = undefined
    }

    clip.startTime = clampStartInLayer(resolvedGroup, clip.layer ?? 1, null, clip.startTime, clip.duration)
    const trackId = track.id
    const previousSelectedClipId = selectedClipId.value

    executeCommand({
      undo() {
        removeClipFromTrack(trackId, clip.id)
        selectedClipId.value = previousSelectedClipId
      },
      redo() {
        upsertClipOnTrack(trackId, clip)
        selectedClipId.value = clip.id
      },
    })

    return deepClone(clip)
  }

  function updateClip(clipId: string, patch: Partial<EditorClip>, options?: { recordHistory?: boolean }) {
    const found = findClip(tracks.value, clipId)
    if (!found) return false
    const trackId = found.track.id
    const beforeClip = deepClone(found.clip)
    const afterClip = buildUpdatedClip(found.clip, patch)

    if (options?.recordHistory === false) {
      return replaceClipInTrack(trackId, clipId, afterClip)
    }

    executeCommand({
      undo() {
        replaceClipInTrack(trackId, clipId, beforeClip)
      },
      redo() {
        replaceClipInTrack(trackId, clipId, afterClip)
      },
    })
    return true
  }

  function selectClip(clipId: string | null) {
    selectedClipId.value = clipId
  }

  function removeSelectedClip() {
    if (!selectedClipId.value) return false
    const found = findClip(tracks.value, selectedClipId.value)
    if (!found) return false

    const trackId = found.track.id
    const removedClip = deepClone(found.clip)
    const previousSelectedClipId = selectedClipId.value

    executeCommand({
      undo() {
        upsertClipOnTrack(trackId, removedClip)
        selectedClipId.value = previousSelectedClipId
      },
      redo() {
        removeClipFromTrack(trackId, removedClip.id)
        selectedClipId.value = null
      },
    })

    return true
  }

  function removeClip(clipId: string) {
    const found = findClip(tracks.value, clipId)
    if (!found) return false

    const trackId = found.track.id
    const removedClip = deepClone(found.clip)
    const previousSelectedClipId = selectedClipId.value

    executeCommand({
      undo() {
        upsertClipOnTrack(trackId, removedClip)
        selectedClipId.value = previousSelectedClipId
      },
      redo() {
        removeClipFromTrack(trackId, removedClip.id)
        if (previousSelectedClipId === removedClip.id) {
          selectedClipId.value = null
        }
      },
    })

    return true
  }

  function removeLayerClips(group: EditorLayerGroup, layer: number) {
    const removedByTrack = tracks.value
      .map((track) => {
        const removed = track.clips
          .filter((clip) => {
            const clipGroup = clip.layerGroup ?? inferLayerGroup(clip.type)
            const clipLayer = clip.layer ?? 1
            return clipGroup === group && clipLayer === layer
          })
          .map((clip) => deepClone(clip))
        return {
          trackId: track.id,
          clips: removed,
        }
      })
      .filter((entry) => entry.clips.length > 0)

    if (!removedByTrack.length) return 0

    const removedIds = new Set(
      removedByTrack.flatMap((entry) => entry.clips.map((clip) => clip.id))
    )
    const previousSelectedClipId = selectedClipId.value
    let removed = 0
    for (const entry of removedByTrack) {
      removed += entry.clips.length
    }

    executeCommand({
      undo() {
        for (const entry of removedByTrack) {
          const track = findTrackById(entry.trackId)
          if (!track) continue
          for (const clip of entry.clips) {
            const exists = track.clips.some((current) => current.id === clip.id)
            if (!exists) track.clips.push(deepClone(clip))
          }
          sortTrackClips(track)
        }
        selectedClipId.value = previousSelectedClipId
      },
      redo() {
        for (const track of tracks.value) {
          track.clips = track.clips.filter((clip) => !removedIds.has(clip.id))
        }
        if (selectedClipId.value && removedIds.has(selectedClipId.value)) {
          selectedClipId.value = null
        }
      },
    })

    return removed
  }

  function duplicateSelectedClip() {
    if (!selectedClip.value) return null
    const clip = deepClone(selectedClip.value)
    clip.id = nextClipId('dup')
    if (clip.effects) {
      clip.effects.transition = undefined
      clip.effects.transitionDuration = undefined
      clip.effects.transitionWith = undefined
    }
    const group = clip.layerGroup ?? inferLayerGroup(clip.type)
    clip.layerGroup = group
    clip.layer = selectedClip.value?.layer ?? clip.layer ?? nextLayerIndex(group)
    const layer = clip.layer ?? 1
    const siblings = tracks.value
      .flatMap((track) => track.clips)
      .filter((entry) => (entry.layerGroup ?? inferLayerGroup(entry.type)) === group && (entry.layer ?? 1) === layer && entry.id !== clip.id)
      .slice()
      .sort((a, b) => a.startTime - b.startTime)
    let nextStart = (selectedClip.value?.startTime ?? clip.startTime) + clip.duration
    for (const sibling of siblings) {
      const siblingStart = sibling.startTime
      const siblingEnd = sibling.startTime + sibling.duration
      if (nextStart + clip.duration <= siblingStart) break
      if (nextStart >= siblingEnd) continue
      nextStart = siblingEnd
    }
    clip.startTime = nextStart

    const track = tracks.value.find((item) => {
      if (clip.type === 'audio') return item.type === 'audio'
      if (clip.type === 'video') return item.type === 'video'
      return item.type === 'graphics'
    })
    if (!track) return null

    const trackId = track.id
    const previousSelectedClipId = selectedClipId.value
    executeCommand({
      undo() {
        removeClipFromTrack(trackId, clip.id)
        selectedClipId.value = previousSelectedClipId
      },
      redo() {
        upsertClipOnTrack(trackId, clip)
        selectedClipId.value = clip.id
      },
    })
    return deepClone(clip)
  }

  function splitSelectedClip(atTime?: number) {
    const clip = selectedClip.value
    if (!clip) return false

    const splitAt = atTime ?? playheadTime.value
    const clipStart = clip.startTime
    const clipEnd = clip.startTime + clip.duration
    if (splitAt <= clipStart + MIN_DURATION || splitAt >= clipEnd - MIN_DURATION) return false

    const found = findClip(tracks.value, clip.id)
    if (!found) return false

    const leftDuration = splitAt - clipStart
    const rightDuration = clipEnd - splitAt
    const trimStart = clip.trimStart ?? 0
    const leftTrimEnd = trimStart + leftDuration
    const rightTrimStart = leftTrimEnd
    const rightTrimEnd = clip.trimEnd ?? (rightTrimStart + rightDuration)
    const originalClip = deepClone(clip)
    const leftClip: EditorClip = {
      ...deepClone(clip),
      duration: leftDuration,
      trimStart,
      trimEnd: Math.max(trimStart + MIN_DURATION, leftTrimEnd),
      label: `${clip.label} (1)`,
      effects: {
        ...clip.effects,
        transition: undefined,
        transitionDuration: undefined,
        transitionWith: undefined,
      },
    }
    const rightClip: EditorClip = {
      ...deepClone(clip),
      id: nextClipId('split'),
      startTime: splitAt,
      duration: rightDuration,
      trimStart: rightTrimStart,
      trimEnd: Math.max(rightTrimStart + MIN_DURATION, rightTrimEnd),
      label: `${clip.label} (2)`,
      effects: {
        ...clip.effects,
        transition: undefined,
        transitionDuration: undefined,
        transitionWith: undefined,
      },
    }
    const trackId = found.track.id
    const previousSelectedClipId = selectedClipId.value

    executeCommand({
      undo() {
        const track = findTrackById(trackId)
        if (!track) return
        const rightIndex = track.clips.findIndex(
          (entry) => entry.id === rightClip.id
        )
        if (rightIndex !== -1) track.clips.splice(rightIndex, 1)
        const leftIndex = track.clips.findIndex(
          (entry) => entry.id === originalClip.id
        )
        if (leftIndex === -1) {
          track.clips.push(deepClone(originalClip))
        } else {
          track.clips.splice(leftIndex, 1, deepClone(originalClip))
        }
        sortTrackClips(track)
        selectedClipId.value = previousSelectedClipId
      },
      redo() {
        const track = findTrackById(trackId)
        if (!track) return
        const originalIndex = track.clips.findIndex(
          (entry) => entry.id === originalClip.id
        )
        if (originalIndex === -1) return
        track.clips.splice(
          originalIndex,
          1,
          deepClone(leftClip),
          deepClone(rightClip)
        )
        sortTrackClips(track)
        selectedClipId.value = rightClip.id
      },
    })

    return true
  }

  function updateSelectedClipTrim(startTime: number, durationValue: number) {
    if (!selectedClip.value) return false
    return updateClip(selectedClip.value.id, {
      startTime: Math.max(0, startTime),
      duration: Math.max(MIN_DURATION, durationValue),
    })
  }

  function setPlayhead(value: number) {
    playheadTime.value = clamp(value, 0, Math.max(duration.value, MIN_DURATION))
  }

  function setTimelineZoom(value: number) {
    timelineZoom.value = clamp(value, 0.1, 4)
  }

  function undo() {
    if (!undoStack.value.length) return false
    const command = undoStack.value.pop()!
    command.undo()
    redoStack.value.push(command)
    if (redoStack.value.length > HISTORY_LIMIT) redoStack.value.shift()
    return true
  }

  function redo() {
    if (!redoStack.value.length) return false
    const command = redoStack.value.pop()!
    command.redo()
    undoStack.value.push(command)
    if (undoStack.value.length > HISTORY_LIMIT) undoStack.value.shift()
    return true
  }

  return {
    projectName,
    tracks,
    clips,
    selectedClipId,
    selectedClip,
    playheadTime,
    timelineZoom,
    duration,
    canUndo,
    canRedo,
    setProjectName,
    exportState,
    loadState,
    resetState,
    transitions,
    setSourceVideoClip,
    addClip,
    updateClip,
    selectClip,
    removeSelectedClip,
    removeClip,
    removeLayerClips,
    duplicateSelectedClip,
    splitSelectedClip,
    updateSelectedClipTrim,
    setPlayhead,
    setTimelineZoom,
    undo,
    redo,
  }
}
