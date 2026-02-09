import { computed, ref } from 'vue'

export type EditorTrackType = 'video' | 'graphics' | 'audio' | 'layer'
export type EditorClipType = 'video' | 'text' | 'image' | 'shape' | 'audio'
export type EditorLayerGroup = 'video' | 'graphics' | 'audio'
export type EditorFitMode = 'fit' | 'fill' | 'stretch'

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
  aspectRatio?: string
  fitMode?: EditorFitMode
  effects?: {
    fadeIn?: number
    fadeOut?: number
    transition?: string
    transitionDuration?: number
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
  selectedClipId: string | null
  playheadTime: number
  timelineZoom: number
}

const MIN_DURATION = 0.1
let clipCounter = 0

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value))
}

function deepClone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T
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
  const selectedClipId = ref<string | null>(null)
  const playheadTime = ref(0)
  const timelineZoom = ref(1)
  const undoStack = ref<EditorSnapshot[]>([])
  const redoStack = ref<EditorSnapshot[]>([])

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
      selectedClipId: selectedClipId.value,
      playheadTime: playheadTime.value,
      timelineZoom: timelineZoom.value,
    }
  }

  function restore(state: EditorSnapshot) {
    projectName.value = state.projectName
    tracks.value = deepClone(state.tracks)
    selectedClipId.value = state.selectedClipId
    playheadTime.value = state.playheadTime
    timelineZoom.value = state.timelineZoom
  }

  function commitHistory() {
    undoStack.value.push(snapshot())
    if (undoStack.value.length > 80) undoStack.value.shift()
    redoStack.value = []
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

  function setProjectName(value: string) {
    projectName.value = value.trim() || 'Untitled project'
  }

  function exportState(): EditorSnapshot {
    return snapshot()
  }

  function loadState(state: Partial<EditorSnapshot>) {
    projectName.value = state.projectName ?? projectName.value
    tracks.value = state.tracks ? deepClone(state.tracks) : createInitialTracks()
    selectedClipId.value = state.selectedClipId ?? null
    playheadTime.value = state.playheadTime ?? 0
    timelineZoom.value = state.timelineZoom ?? 1
    undoStack.value = []
    redoStack.value = []
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
    commitHistory()

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

    tracks.value = createInitialTracks()
    tracks.value.find((track) => track.type === 'video')!.clips = [videoClip]
    tracks.value.find((track) => track.type === 'audio')!.clips = [audioClip]
    selectedClipId.value = videoClip.id
    playheadTime.value = 0
  }

  function addClip(trackType: EditorTrackType, clipInput: Partial<EditorClip>) {
    commitHistory()
    const track = tracks.value.find((item) => item.type === trackType)
    if (!track) return null

    const baseEffects = {
      fadeIn: 0,
      fadeOut: 0,
      transition: undefined,
      transitionDuration: undefined,
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
      aspectRatio: clipInput.aspectRatio,
      fitMode: clipInput.fitMode ?? 'fit',
      effects: clipInput.effects ? { ...baseEffects, ...clipInput.effects } : { ...baseEffects },
      position: clipInput.position ? { ...clipInput.position } : undefined,
      size: clipInput.size ? { ...clipInput.size } : undefined,
      rotation: clipInput.rotation ?? 0,
      lockAspectRatio: clipInput.lockAspectRatio ?? true,
      text: clipInput.text,
      style: clipInput.style ? { ...clipInput.style } : undefined,
    }

    track.clips.push(clip)
    sortTrackClips(track)
    selectedClipId.value = clip.id
    return clip
  }

  function updateClip(clipId: string, patch: Partial<EditorClip>, options?: { recordHistory?: boolean }) {
    if (options?.recordHistory !== false) commitHistory()
    const found = findClip(tracks.value, clipId)
    if (!found) return false

    const nextClip = {
      ...found.clip,
      ...patch,
      effects: patch.effects ? { ...found.clip.effects, ...patch.effects } : found.clip.effects,
      position: patch.position ? { ...found.clip.position, ...patch.position } : found.clip.position,
      size: patch.size ? { ...found.clip.size, ...patch.size } : found.clip.size,
      style: patch.style ? { ...found.clip.style, ...patch.style } : found.clip.style,
    }

    nextClip.startTime = Math.max(0, nextClip.startTime)
    nextClip.duration = Math.max(MIN_DURATION, nextClip.duration)
    found.track.clips.splice(found.index, 1, nextClip)
    sortTrackClips(found.track)
    return true
  }

  function selectClip(clipId: string | null) {
    selectedClipId.value = clipId
  }

  function removeSelectedClip() {
    if (!selectedClipId.value) return false
    const found = findClip(tracks.value, selectedClipId.value)
    if (!found) return false

    commitHistory()
    found.track.clips.splice(found.index, 1)
    selectedClipId.value = null
    return true
  }

  function duplicateSelectedClip() {
    if (!selectedClip.value) return null
    commitHistory()
    const clip = deepClone(selectedClip.value)
    clip.id = nextClipId('dup')
    clip.startTime = clip.startTime + 0.35
    const group = clip.layerGroup ?? inferLayerGroup(clip.type)
    clip.layerGroup = group
    clip.layer = selectedClip.value?.layer ?? clip.layer ?? nextLayerIndex(group)

    const track = tracks.value.find((item) => {
      if (clip.type === 'audio') return item.type === 'audio'
      if (clip.type === 'video') return item.type === 'video'
      return item.type === 'graphics'
    })
    if (!track) return null

    track.clips.push(clip)
    sortTrackClips(track)
    selectedClipId.value = clip.id
    return clip
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

    commitHistory()

    const leftDuration = splitAt - clipStart
    const rightDuration = clipEnd - splitAt
    const trimStart = clip.trimStart ?? 0
    const leftTrimEnd = trimStart + leftDuration
    const rightTrimStart = leftTrimEnd
    const rightTrimEnd = clip.trimEnd ?? (rightTrimStart + rightDuration)
    const rightClip: EditorClip = {
      ...deepClone(clip),
      id: nextClipId('split'),
      startTime: splitAt,
      duration: rightDuration,
      trimStart: rightTrimStart,
      trimEnd: Math.max(rightTrimStart + MIN_DURATION, rightTrimEnd),
      label: `${clip.label} (2)`,
    }

    found.track.clips.splice(found.index, 1, {
      ...clip,
      duration: leftDuration,
      trimStart,
      trimEnd: Math.max(trimStart + MIN_DURATION, leftTrimEnd),
      label: `${clip.label} (1)`,
    }, rightClip)

    sortTrackClips(found.track)
    selectedClipId.value = rightClip.id
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
    const current = snapshot()
    const prev = undoStack.value.pop()!
    redoStack.value.push(current)
    restore(prev)
    return true
  }

  function redo() {
    if (!redoStack.value.length) return false
    const current = snapshot()
    const next = redoStack.value.pop()!
    undoStack.value.push(current)
    restore(next)
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
    setSourceVideoClip,
    addClip,
    updateClip,
    selectClip,
    removeSelectedClip,
    duplicateSelectedClip,
    splitSelectedClip,
    updateSelectedClipTrim,
    setPlayhead,
    setTimelineZoom,
    undo,
    redo,
  }
}
