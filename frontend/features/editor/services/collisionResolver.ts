export type CollisionOperation = 'drag' | 'insert' | 'paste' | 'trim_start' | 'trim_end' | 'split'

export type CollisionReason =
  | 'ok'
  | 'clamped_prev'
  | 'clamped_next'
  | 'moved_to_new_layer'
  | 'blocked'

export interface CollisionRange {
  clipId: string
  startFrame: number
  endFrame: number
}

export interface CollisionLane {
  group: string
  layer: number
  clips: CollisionRange[]
}

export interface SnapTarget {
  kind: 'clip_end' | 'clip_start'
  clipId: string
  frame: number
}

export interface CollisionResolverInput {
  operation: CollisionOperation
  group: string
  layer: number
  clipId?: string
  desiredStartFrame: number
  durationFrames: number
  laneClips: CollisionRange[]
  allowCreateLayer?: boolean
  alternativeLanes?: CollisionLane[]
}

export interface CollisionResolverResult {
  startFrame: number
  layer: number
  group: string
  createdLayer: boolean
  reason: CollisionReason
  snapTarget?: SnapTarget
}

interface PlacementResult {
  ok: boolean
  startFrame: number
  reason: Exclude<CollisionReason, 'moved_to_new_layer' | 'blocked'>
}

function sortRanges(ranges: CollisionRange[], excludeClipId?: string): CollisionRange[] {
  return ranges
    .filter((range) => !excludeClipId || range.clipId !== excludeClipId)
    .map((range) => ({
      clipId: range.clipId,
      startFrame: Math.max(0, Math.round(Number(range.startFrame) || 0)),
      endFrame: Math.max(0, Math.round(Number(range.endFrame) || 0)),
    }))
    .filter((range) => range.endFrame > range.startFrame)
    .sort((left, right) => left.startFrame - right.startFrame)
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value))
}

function findBestPlacement(desiredStartFrame: number, durationFrames: number, ranges: CollisionRange[]): PlacementResult {
  const desired = Math.max(0, Math.round(Number(desiredStartFrame) || 0))
  const duration = Math.max(1, Math.round(Number(durationFrames) || 0))

  if (!ranges.length) {
    return {
      ok: true,
      startFrame: desired,
      reason: 'ok',
    }
  }

  const candidates: number[] = []
  let cursor = 0

  for (const range of ranges) {
    const gapStart = cursor
    const gapEnd = range.startFrame
    const maxStart = gapEnd - duration
    if (maxStart >= gapStart) {
      candidates.push(clamp(desired, gapStart, maxStart))
    }
    cursor = Math.max(cursor, range.endFrame)
  }

  // Tail gap to infinity always fits.
  candidates.push(Math.max(cursor, desired))

  let bestStart = candidates[0]
  let bestDistance = Math.abs(bestStart - desired)

  for (const candidate of candidates.slice(1)) {
    const distance = Math.abs(candidate - desired)
    if (distance < bestDistance) {
      bestStart = candidate
      bestDistance = distance
      continue
    }
    if (distance === bestDistance && candidate < bestStart) {
      bestStart = candidate
    }
  }

  const reason: PlacementResult['reason'] = bestStart === desired
    ? 'ok'
    : (bestStart > desired ? 'clamped_prev' : 'clamped_next')

  return {
    ok: true,
    startFrame: bestStart,
    reason,
  }
}

function resolveInLane(input: CollisionResolverInput, lane: CollisionLane): PlacementResult {
  const ranges = sortRanges(lane.clips, input.clipId)
  return findBestPlacement(input.desiredStartFrame, input.durationFrames, ranges)
}

function isTrimOperation(op: CollisionOperation): boolean {
  return op === 'trim_start' || op === 'trim_end'
}

export function resolveCollision(input: CollisionResolverInput): CollisionResolverResult {
  const desiredStartFrame = Math.max(0, Math.round(Number(input.desiredStartFrame) || 0))
  const durationFrames = Math.max(1, Math.round(Number(input.durationFrames) || 0))

  const primaryLane: CollisionLane = {
    group: input.group,
    layer: input.layer,
    clips: input.laneClips,
  }
  const primary = resolveInLane(
    {
      ...input,
      desiredStartFrame,
      durationFrames,
    },
    primaryLane
  )

  if (primary.ok) {
    return {
      startFrame: primary.startFrame,
      layer: input.layer,
      group: input.group,
      createdLayer: false,
      reason: primary.reason,
    }
  }

  if (isTrimOperation(input.operation)) {
    return {
      startFrame: primary.startFrame,
      layer: input.layer,
      group: input.group,
      createdLayer: false,
      reason: 'blocked',
    }
  }

  if (input.allowCreateLayer && input.alternativeLanes?.length) {
    const ordered = input.alternativeLanes
      .slice()
      .sort((left, right) => {
        const leftDistance = Math.abs((left.layer ?? 0) - input.layer)
        const rightDistance = Math.abs((right.layer ?? 0) - input.layer)
        if (leftDistance !== rightDistance) return leftDistance - rightDistance
        return (left.layer ?? 0) - (right.layer ?? 0)
      })

    for (const lane of ordered) {
      const placement = resolveInLane(
        {
          ...input,
          desiredStartFrame,
          durationFrames,
          group: lane.group,
          layer: lane.layer,
        },
        lane
      )
      if (!placement.ok) continue
      return {
        startFrame: placement.startFrame,
        layer: lane.layer,
        group: lane.group,
        createdLayer: lane.layer !== input.layer,
        reason: 'moved_to_new_layer',
      }
    }
  }

  return {
    startFrame: desiredStartFrame,
    layer: input.layer,
    group: input.group,
    createdLayer: false,
    reason: 'blocked',
  }
}

export function hasOverlap(range: CollisionRange, others: CollisionRange[], excludeClipId?: string): boolean {
  const sorted = sortRanges(others, excludeClipId)
  return sorted.some((candidate) => range.startFrame < candidate.endFrame && range.endFrame > candidate.startFrame)
}
