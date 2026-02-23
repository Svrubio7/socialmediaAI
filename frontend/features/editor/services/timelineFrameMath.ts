export interface FrameRange {
  startFrame: number
  endFrame: number
  durationFrames: number
}

export interface GapOverlapFrames {
  gapFrames: number
  gapSeconds: number
  isAdjacent: boolean
  isGap: boolean
  isOverlap: boolean
}

const DEFAULT_FPS = 30

export function normalizeFps(fps?: number | null): number {
  const parsed = Number(fps)
  if (!Number.isFinite(parsed) || parsed <= 0) return DEFAULT_FPS
  return parsed
}

export function toFrame(seconds: number, fps?: number | null): number {
  const safeFps = normalizeFps(fps)
  const safeSeconds = Number(seconds)
  if (!Number.isFinite(safeSeconds)) return 0
  return Math.round(safeSeconds * safeFps)
}

export function toSec(frame: number, fps?: number | null): number {
  const safeFps = normalizeFps(fps)
  const safeFrame = Number(frame)
  if (!Number.isFinite(safeFrame)) return 0
  return safeFrame / safeFps
}

export function snapFrame(seconds: number, fps?: number | null): number {
  return toFrame(seconds, fps)
}

export function durationSecondsToFrames(durationSeconds: number, fps?: number | null): number {
  const frames = toFrame(durationSeconds, fps)
  return Math.max(1, frames)
}

export function durationFramesToSeconds(durationFrames: number, fps?: number | null): number {
  const safeFrames = Math.max(1, Math.round(Number(durationFrames) || 0))
  return toSec(safeFrames, fps)
}

export function clipRangeFrames(startSeconds: number, durationSeconds: number, fps?: number | null): FrameRange {
  const startFrame = Math.max(0, toFrame(startSeconds, fps))
  const durationFrames = durationSecondsToFrames(durationSeconds, fps)
  return {
    startFrame,
    durationFrames,
    endFrame: startFrame + durationFrames,
  }
}

export function rangeFromFrames(startFrameRaw: number, durationFramesRaw: number): FrameRange {
  const startFrame = Math.max(0, Math.round(Number(startFrameRaw) || 0))
  const durationFrames = Math.max(1, Math.round(Number(durationFramesRaw) || 0))
  return {
    startFrame,
    durationFrames,
    endFrame: startFrame + durationFrames,
  }
}

export function adjacencyFrames(fromRange: FrameRange, toRange: FrameRange): number {
  return toRange.startFrame - fromRange.endFrame
}

export function gapOverlapFrames(fromRange: FrameRange, toRange: FrameRange, fps?: number | null): GapOverlapFrames {
  const gapFrames = adjacencyFrames(fromRange, toRange)
  return {
    gapFrames,
    gapSeconds: toSec(gapFrames, fps),
    isAdjacent: gapFrames === 0,
    isGap: gapFrames > 0,
    isOverlap: gapFrames < 0,
  }
}

export function isAdjacentFrames(fromRange: FrameRange, toRange: FrameRange): boolean {
  return adjacencyFrames(fromRange, toRange) === 0
}

export function pxToFrame(px: number, pxPerSecond: number, fps?: number | null): number {
  if (!Number.isFinite(pxPerSecond) || pxPerSecond <= 0) return 0
  return toFrame(px / pxPerSecond, fps)
}

export function frameToPx(frame: number, pxPerSecond: number, fps?: number | null): number {
  if (!Number.isFinite(pxPerSecond) || pxPerSecond <= 0) return 0
  return toSec(frame, fps) * pxPerSecond
}

export function formatFrameSeconds(frame: number, fps?: number | null): string {
  return `${frame}f (${toSec(frame, fps).toFixed(3)}s)`
}
