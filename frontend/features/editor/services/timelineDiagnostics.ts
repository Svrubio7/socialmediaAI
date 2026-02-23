import type { EditorClip, EditorTrack } from '~/composables/useEditorState'
import {
  clipRangeFrames,
  durationSecondsToFrames,
  gapOverlapFrames,
  normalizeFps,
  toFrame,
  toSec,
} from '~/features/editor/services/timelineFrameMath'

export interface TimelineClipDiagnostic {
  clipId: string
  label: string
  type: string
  group: string
  layer: number
  startFrame: number
  endFrame: number
  durationFrames: number
  startSeconds: number
  endSeconds: number
}

export interface TimelineAdjacencyDiagnostic {
  group: string
  layer: number
  fromClipId: string
  toClipId: string
  gapFrames: number
  gapSeconds: number
  isAdjacent: boolean
  isGap: boolean
  isOverlap: boolean
}

export interface TimelineTransitionDiagnostic {
  fromClipId: string
  toClipId: string
  name: string
  durationFrames: number
  durationSeconds: number
  startFrame: number
  endFrame: number
  validAdjacency: boolean
}

export interface TimelineDiagnosticsPayload {
  fps: number
  clips: TimelineClipDiagnostic[]
  adjacency: TimelineAdjacencyDiagnostic[]
  transitions: TimelineTransitionDiagnostic[]
  drag?: {
    clipId: string
    desiredStartFrame: number
    resolvedStartFrame: number
    layer: number
    group: string
    reason: string
    snapTargetFrame?: number
  } | null
}

export interface PlaybackDiagnosticsPayload {
  fps: number
  currentTime: number
  currentFrame: number
  activeClipIds: string[]
  activeTransition: {
    fromClipId: string
    toClipId: string
    name: string
    startFrame: number
    endFrame: number
    mode?: string
  } | null
  renderOrder: string[]
  sampleWindows: Array<{
    clipId: string
    timelineFrame: number
    mediaTime: number
    mediaFrame: number
  }>
}

function clipGroup(clip: EditorClip): string {
  if (clip.layerGroup) return clip.layerGroup
  if (clip.type === 'audio') return 'audio'
  if (clip.type === 'video') return 'video'
  return 'graphics'
}

function sortClipsByRange(left: TimelineClipDiagnostic, right: TimelineClipDiagnostic): number {
  if (left.group !== right.group) return left.group.localeCompare(right.group)
  if (left.layer !== right.layer) return left.layer - right.layer
  if (left.startFrame !== right.startFrame) return left.startFrame - right.startFrame
  return left.clipId.localeCompare(right.clipId)
}

export function buildTimelineDiagnostics(
  tracks: EditorTrack[],
  fpsInput: number,
  geometryOverrides?: Record<string, { startTime: number; duration: number }>,
  dragPayload?: TimelineDiagnosticsPayload['drag']
): TimelineDiagnosticsPayload {
  const fps = normalizeFps(fpsInput)
  const clips: TimelineClipDiagnostic[] = []

  for (const track of tracks) {
    for (const clip of track.clips ?? []) {
      const geometry = geometryOverrides?.[clip.id] ?? {
        startTime: clip.startTime,
        duration: clip.duration,
      }
      const range = clipRangeFrames(geometry.startTime, geometry.duration, fps)
      clips.push({
        clipId: clip.id,
        label: clip.label,
        type: clip.type,
        group: clipGroup(clip),
        layer: clip.layer ?? 1,
        startFrame: range.startFrame,
        endFrame: range.endFrame,
        durationFrames: range.durationFrames,
        startSeconds: toSec(range.startFrame, fps),
        endSeconds: toSec(range.endFrame, fps),
      })
    }
  }

  clips.sort(sortClipsByRange)

  const adjacency: TimelineAdjacencyDiagnostic[] = []
  const transitions: TimelineTransitionDiagnostic[] = []

  const byLane = new Map<string, TimelineClipDiagnostic[]>()
  clips.forEach((clip) => {
    const key = `${clip.group}:${clip.layer}`
    const lane = byLane.get(key) ?? []
    lane.push(clip)
    byLane.set(key, lane)
  })

  byLane.forEach((lane) => {
    lane.sort((left, right) => left.startFrame - right.startFrame)
    for (let index = 0; index < lane.length - 1; index += 1) {
      const fromClip = lane[index]
      const toClip = lane[index + 1]
      const gap = gapOverlapFrames(fromClip, toClip, fps)
      adjacency.push({
        group: fromClip.group,
        layer: fromClip.layer,
        fromClipId: fromClip.clipId,
        toClipId: toClip.clipId,
        gapFrames: gap.gapFrames,
        gapSeconds: gap.gapSeconds,
        isAdjacent: gap.isAdjacent,
        isGap: gap.isGap,
        isOverlap: gap.isOverlap,
      })
    }
  })

  const byId = new Map<string, EditorClip>()
  tracks.forEach((track) => {
    track.clips.forEach((clip) => byId.set(clip.id, clip))
  })

  adjacency.forEach((entry) => {
    const fromClip = byId.get(entry.fromClipId)
    if (!fromClip) return
    const transitionName = fromClip.effects?.transition
    const transitionWith = fromClip.effects?.transitionWith
    const requestedDurationSeconds = Number(fromClip.effects?.transitionDuration ?? 0)
    if (!transitionName || !transitionWith || requestedDurationSeconds <= 0) return
    if (transitionWith !== entry.toClipId) return

    const durationFrames = durationSecondsToFrames(requestedDurationSeconds, fps)
    const cutFrame = clips.find((clip) => clip.clipId === entry.toClipId)?.startFrame ?? 0
    const half = Math.floor(durationFrames / 2)
    const startFrame = Math.max(0, cutFrame - half)
    const endFrame = startFrame + durationFrames

    transitions.push({
      fromClipId: entry.fromClipId,
      toClipId: entry.toClipId,
      name: transitionName,
      durationFrames,
      durationSeconds: toSec(durationFrames, fps),
      startFrame,
      endFrame,
      validAdjacency: entry.isAdjacent,
    })
  })

  return {
    fps,
    clips,
    adjacency,
    transitions,
    drag: dragPayload ?? null,
  }
}

export function buildPlaybackDiagnostics(payload: {
  fps: number
  currentTime: number
  activeClips: EditorClip[]
  renderClips: EditorClip[]
  activeTransition: {
    fromId: string
    toId: string
    name: string
    t0: number
    t1: number
    mode?: string
  } | null
  sampleWindows?: Array<{ clipId: string; mediaTime: number }>
}): PlaybackDiagnosticsPayload {
  const fps = normalizeFps(payload.fps)
  const currentFrame = toFrame(payload.currentTime, fps)
  const sampleWindows = (payload.sampleWindows ?? []).map((entry) => ({
    clipId: entry.clipId,
    mediaTime: entry.mediaTime,
    mediaFrame: toFrame(entry.mediaTime, fps),
    timelineFrame: currentFrame,
  }))

  return {
    fps,
    currentTime: payload.currentTime,
    currentFrame,
    activeClipIds: payload.activeClips.map((clip) => clip.id),
    activeTransition: payload.activeTransition
      ? {
          fromClipId: payload.activeTransition.fromId,
          toClipId: payload.activeTransition.toId,
          name: payload.activeTransition.name,
          startFrame: toFrame(payload.activeTransition.t0, fps),
          endFrame: toFrame(payload.activeTransition.t1, fps),
          mode: payload.activeTransition.mode,
        }
      : null,
    renderOrder: payload.renderClips.map((clip) => clip.id),
    sampleWindows,
  }
}
