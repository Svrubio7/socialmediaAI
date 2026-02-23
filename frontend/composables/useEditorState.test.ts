import { describe, expect, it } from 'vitest'

import { useEditorState } from './useEditorState'

describe('useEditorState command history', () => {
  it('undoes and redoes add clip operations', () => {
    const editor = useEditorState()

    const created = editor.addClip('video', {
      type: 'video',
      label: 'A',
      startTime: 0,
      duration: 2,
      layer: 1,
      layerGroup: 'video',
    })

    expect(created).toBeTruthy()
    expect(editor.clips.value).toHaveLength(1)
    expect(editor.canUndo.value).toBe(true)

    expect(editor.undo()).toBe(true)
    expect(editor.clips.value).toHaveLength(0)

    expect(editor.redo()).toBe(true)
    expect(editor.clips.value).toHaveLength(1)
  })

  it('tracks update commands and ignores non-history patch updates', () => {
    const editor = useEditorState()
    const created = editor.addClip('video', {
      type: 'video',
      label: 'A',
      startTime: 0,
      duration: 2,
      layer: 1,
      layerGroup: 'video',
    })
    expect(created).toBeTruthy()
    if (!created) return

    expect(
      editor.updateClip(created.id, { startTime: 1, duration: 1.5 })
    ).toBe(true)
    expect(editor.clips.value[0].startTime).toBe(1)

    expect(
      editor.updateClip(
        created.id,
        {
          sourceUrl: 'https://example.com/video.mp4',
        },
        { recordHistory: false }
      )
    ).toBe(true)
    expect(editor.clips.value[0].sourceUrl).toBe('https://example.com/video.mp4')

    expect(editor.undo()).toBe(true)
    expect(editor.clips.value[0].startTime).toBe(0)
    expect(editor.clips.value[0].sourceUrl).toBeUndefined()
  })

  it('undoes split operations deterministically', () => {
    const editor = useEditorState()
    const created = editor.addClip('video', {
      type: 'video',
      label: 'Base',
      startTime: 0,
      duration: 6,
      layer: 1,
      layerGroup: 'video',
    })
    expect(created).toBeTruthy()
    if (!created) return

    editor.selectClip(created.id)
    expect(editor.splitSelectedClip(3)).toBe(true)
    expect(editor.clips.value).toHaveLength(2)

    expect(editor.undo()).toBe(true)
    expect(editor.clips.value).toHaveLength(1)
    expect(editor.clips.value[0].id).toBe(created.id)
    expect(editor.clips.value[0].duration).toBe(6)

    expect(editor.redo()).toBe(true)
    expect(editor.clips.value).toHaveLength(2)
  })

  it('removes and restores full layer clips via history', () => {
    const editor = useEditorState()
    const first = editor.addClip('video', {
      type: 'video',
      label: 'V1',
      startTime: 0,
      duration: 2,
      layer: 1,
      layerGroup: 'video',
    })
    const second = editor.addClip('video', {
      type: 'video',
      label: 'V2',
      startTime: 2,
      duration: 2,
      layer: 1,
      layerGroup: 'video',
    })
    expect(first && second).toBeTruthy()

    const removed = editor.removeLayerClips('video', 1)
    expect(removed).toBe(2)
    expect(editor.clips.value.filter((clip) => clip.layerGroup === 'video')).toHaveLength(
      0
    )

    expect(editor.undo()).toBe(true)
    expect(editor.clips.value.filter((clip) => clip.layerGroup === 'video')).toHaveLength(
      2
    )
  })
})
