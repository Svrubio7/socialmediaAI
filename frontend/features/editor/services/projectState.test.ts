import { describe, expect, it } from 'vitest'

import {
  buildPersistedProjectState,
  ensureProjectStateV2,
  extractLegacyEditorState,
} from './projectState'

describe('projectState migration helpers', () => {
  it('normalizes legacy state into v2 shape while keeping compatibility fields', () => {
    const state = ensureProjectStateV2(
      {
        projectName: 'Legacy',
        tracks: [{ id: 'track-video', clips: [] }],
        transitions: [{ id: 't1', fromClipId: 'a', toClipId: 'b' }],
        timelineZoom: 1.25,
      },
      'Legacy'
    )
    expect(state.version).toBe(2)
    expect(Array.isArray(state.scenes)).toBe(true)
    expect(state.tracks).toHaveLength(1)
    expect(state.transitions).toHaveLength(1)
    expect(state.timelineViewState.zoomLevel).toBe(1.25)
  })

  it('extracts legacy editor state from a v2 document', () => {
    const legacy = extractLegacyEditorState(
      {
        version: 2,
        currentSceneId: 'scene_main',
        scenes: [{ id: 'scene_main', tracks: [{ id: 'a', clips: [] }] }],
        timelineViewState: { zoomLevel: 2, playheadTime: 3 },
      },
      'Demo'
    )
    expect(legacy.projectName).toBe('Demo')
    expect(legacy.tracks).toHaveLength(1)
    expect(Array.isArray(legacy.transitions)).toBe(true)
    expect(legacy.timelineZoom).toBe(2)
    expect(legacy.playheadTime).toBe(3)
  })

  it('builds persisted state with scene tracks and output settings', () => {
    const persisted = buildPersistedProjectState(
      {
        tracks: [{ id: 'track-video', clips: [] }],
        transitions: [{ id: 't1', fromClipId: 'clip-a', toClipId: 'clip-b' }],
        selectedClipId: 'clip-1',
        playheadTime: 4,
        timelineZoom: 1.5,
      },
      'My Project',
      {
        width: 1080,
        height: 1920,
        fps: 30,
        bitrate: '4M',
      }
    )
    expect(persisted.version).toBe(2)
    expect(persisted.metadata.name).toBe('My Project')
    expect(persisted.tracks).toHaveLength(1)
    expect(persisted.transitions).toHaveLength(1)
    expect(persisted.scenes[0].tracks).toHaveLength(1)
    expect(persisted.outputSettings.width).toBe(1080)
    expect(persisted.selectedClipId).toBe('clip-1')
  })
})
