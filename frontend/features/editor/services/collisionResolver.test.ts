import { describe, expect, it } from 'vitest'

import { hasOverlap, resolveCollision, type CollisionRange } from './collisionResolver'

function laneClips(...ranges: Array<[string, number, number]>): CollisionRange[] {
  return ranges.map(([clipId, startFrame, endFrame]) => ({ clipId, startFrame, endFrame }))
}

describe('collisionResolver', () => {
  it('keeps desired start when lane is free', () => {
    const result = resolveCollision({
      operation: 'drag',
      group: 'video',
      layer: 1,
      clipId: 'moving',
      desiredStartFrame: 90,
      durationFrames: 30,
      laneClips: laneClips(['a', 0, 60], ['b', 120, 180]),
    })

    expect(result.startFrame).toBe(90)
    expect(result.reason).toBe('ok')
  })

  it('clamps to previous boundary when desired start overlaps an existing clip', () => {
    const result = resolveCollision({
      operation: 'drag',
      group: 'video',
      layer: 1,
      clipId: 'moving',
      desiredStartFrame: 50,
      durationFrames: 30,
      laneClips: laneClips(['a', 0, 60], ['b', 120, 180]),
    })

    expect(result.startFrame).toBe(60)
    expect(result.reason).toBe('clamped_prev')
  })

  it('clamps to next boundary when desired start is too close to the next clip', () => {
    const result = resolveCollision({
      operation: 'drag',
      group: 'video',
      layer: 1,
      clipId: 'moving',
      desiredStartFrame: 100,
      durationFrames: 30,
      laneClips: laneClips(['a', 0, 60], ['b', 110, 170]),
    })

    expect(result.startFrame).toBe(80)
    expect(result.reason).toBe('clamped_next')
  })

  it('detects overlap predicate correctly', () => {
    const moving = { clipId: 'moving', startFrame: 20, endFrame: 50 }
    const overlaps = hasOverlap(moving, laneClips(['a', 0, 10], ['b', 40, 80]))
    const nonOverlaps = hasOverlap(moving, laneClips(['a', 0, 20], ['b', 50, 90]))

    expect(overlaps).toBe(true)
    expect(nonOverlaps).toBe(false)
  })
})
