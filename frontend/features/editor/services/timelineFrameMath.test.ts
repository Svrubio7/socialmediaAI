import { describe, expect, it } from 'vitest'

import {
  clipRangeFrames,
  frameToPx,
  gapOverlapFrames,
  isAdjacentFrames,
  normalizeFps,
  pxToFrame,
  toFrame,
  toSec,
} from './timelineFrameMath'

describe('timelineFrameMath', () => {
  it('normalizes fps fallback', () => {
    expect(normalizeFps(undefined)).toBe(30)
    expect(normalizeFps(0)).toBe(30)
    expect(normalizeFps(60)).toBe(60)
  })

  it('converts between seconds and frames with round-trip behavior', () => {
    const frame = toFrame(2.5, 30)
    expect(frame).toBe(75)
    expect(toSec(frame, 30)).toBe(2.5)
  })

  it('builds end-exclusive frame ranges', () => {
    const range = clipRangeFrames(1, 2, 30)
    expect(range.startFrame).toBe(30)
    expect(range.durationFrames).toBe(60)
    expect(range.endFrame).toBe(90)
  })

  it('detects adjacency and overlap by frame gap', () => {
    const left = clipRangeFrames(0, 2, 30)
    const rightAdjacent = clipRangeFrames(2, 1, 30)
    const rightOverlap = clipRangeFrames(1.9, 1, 30)

    expect(isAdjacentFrames(left, rightAdjacent)).toBe(true)
    expect(gapOverlapFrames(left, rightAdjacent, 30).gapFrames).toBe(0)
    expect(gapOverlapFrames(left, rightOverlap, 30).isOverlap).toBe(true)
  })

  it('maps px to frame and back at timeline scale', () => {
    const pxPerSecond = 120
    const frame = pxToFrame(240, pxPerSecond, 30)
    expect(frame).toBe(60)
    expect(frameToPx(frame, pxPerSecond, 30)).toBe(240)
  })
})
