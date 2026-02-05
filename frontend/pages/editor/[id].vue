<template>
  <div class="h-screen w-screen overflow-hidden bg-surface-950 text-surface-100">
    <EditorHeader
      :project-name="projectName"
      :account-initial="accountInitial"
      :save-state="saveState"
      :can-undo="canUndo"
      :can-redo="canRedo"
      @toggle-left="leftCollapsed = !leftCollapsed"
      @go-home="navigateTo(localePath('/editor'))"
      @update:project-name="handleProjectRename"
      @undo="undo"
      @redo="redo"
      @export="exportVideo"
      @help="toast.info('Help center is coming soon')"
      @feedback="toast.info('Thanks! Feedback channel is coming soon')"
      @account="navigateTo(localePath('/account/profile'))"
    />

    <div
      ref="gridRef"
      class="h-[calc(100vh-56px)] flex flex-col lg:grid"
      :style="desktopGridStyle"
    >
      <EditorLeftSidebar
        class="hidden lg:flex"
        :active-section="activeLeftSection"
        :collapsed="leftCollapsed"
        :media-items="mediaItems"
        @update:active-section="activeLeftSection = $event"
        @import-media="openImportDialog"
        @add-media="handleAddMedia"
        @add-text="handleAddText"
        @add-shape="handleAddShape"
        @add-transition="handleAddTransition"
      />

      <div
        v-show="!leftCollapsed"
        class="hidden lg:block editor-resizer editor-resizer-vertical"
        @pointerdown.prevent="startResize('left', $event)"
      />

      <div ref="centerRef" class="min-h-0 flex flex-col border-x border-surface-800 lg:border-x-0">
        <div class="lg:hidden px-3 py-2 border-b border-surface-800 bg-surface-900">
          <div class="grid grid-cols-2 gap-2">
            <select v-model="activeLeftSection" class="mobile-select">
              <option value="media">Media</option>
              <option value="text">Text</option>
              <option value="graphics">Graphics</option>
              <option value="transitions">Transitions</option>
            </select>
            <select v-model="activeRightTab" class="mobile-select">
              <option value="fade">Fade</option>
              <option value="filters">Filters</option>
              <option value="adjust">Adjust</option>
              <option value="speed">Speed</option>
              <option value="aspect">Aspect</option>
            </select>
          </div>
        </div>

        <div class="flex-1 min-h-0">
          <EditorPreview
            :clips="clips"
            :selected-clip-id="selectedClipId"
            :current-time="playheadTime"
            :duration="timelineDuration"
            :playing="isPlaying"
            @update:current-time="setPlayhead"
            @update:playing="isPlaying = $event"
            @update:clip="handleClipUpdate"
            @update:clip-meta="syncClipMeta"
            @select-clip="selectClip"
            @split="splitSelectedClipAtPlayhead"
            @duplicate="duplicateSelectedClipAction"
            @delete="removeSelectedClipAction"
          />
        </div>

        <div class="hidden lg:block editor-resizer editor-resizer-horizontal" @pointerdown.prevent="startResize('timeline', $event)" />

        <div class="min-h-0" :style="{ height: `${timelineHeight}px` }">
          <EditorTimeline
            class="h-full"
            :tracks="layerTracks"
            :playhead="playheadTime"
            :duration="timelineDuration"
            :zoom="timelineZoom"
            :selected-clip-id="selectedClipId"
            @update:playhead="setPlayhead"
            @update:zoom="setTimelineZoom"
            @select-clip="selectClip"
            @split="splitSelectedClipAtPlayhead"
            @delete="removeSelectedClipAction"
            @duplicate="duplicateSelectedClipAction"
            @trim-clip="handleTimelineTrim"
            @move-clip="handleTimelineMove"
          />
        </div>
      </div>

      <div
        class="hidden lg:block editor-resizer editor-resizer-vertical"
        @pointerdown.prevent="startResize('right', $event)"
      />

      <EditorRightSidebar
        class="hidden lg:flex"
        :active-tab="activeRightTab"
        :selected-clip="selectedClip"
        @update:active-tab="activeRightTab = $event"
        @apply:fade="applyFade"
        @apply:speed="applySpeed"
        @apply:filter="applyFilterPreset"
        @apply:color="applyColorAdjust"
        @apply:aspect="applyAspectRatio"
        @apply:shape="applyShapeStyle"
      />
    </div>

    <input
      ref="importInputRef"
      type="file"
      accept="video/*,image/*"
      class="hidden"
      @change="onImportSelected"
    />

    <UiToast />
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { EditorClip, EditorTrack } from '~/composables/useEditorState'
import { useEditorState } from '~/composables/useEditorState'

definePageMeta({
  layout: false,
  middleware: 'auth',
})

interface MediaLibraryItem {
  id: string
  name: string
  type: 'video' | 'image' | 'audio'
  thumbnail?: string
  duration?: number
  sourceId?: string
  sourceUrl?: string
  storagePath?: string
}

interface EditorOpResponse {
  error?: string
  output_url?: string
  output_video_id?: string
}

const route = useRoute()
const localePath = useLocalePath()
const api = useApi()
const toast = useToast()
const auth = useAuthStore()

const {
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
  setSourceVideoClip,
  addClip,
  updateClip,
  selectClip,
  removeSelectedClip,
  duplicateSelectedClip,
  splitSelectedClip,
  setPlayhead,
  setTimelineZoom,
  undo,
  redo,
} = useEditorState()

const activeLeftSection = ref('media')
const activeRightTab = ref('fade')
const leftCollapsed = ref(false)
const previewUrl = ref('')
const previewDuration = ref(0)
const timelineDuration = computed(() => Math.max(duration.value, previewDuration.value, 1))
const isPlaying = ref(false)
const saveState = ref<'saved' | 'saving' | 'error'>('saved')
const operationRunning = ref(false)
const importInputRef = ref<HTMLInputElement | null>(null)
const mediaItems = ref<MediaLibraryItem[]>([])
const outputSettings = ref({
  width: 1920,
  height: 1080,
  fps: 30,
  bitrate: '8M',
})

let saveStateTimer: ReturnType<typeof setTimeout> | null = null
let playbackFrame: number | null = null
let lastFrameTime = 0

const accountInitial = computed(() => {
  const name = auth.user?.name?.trim()
  if (name) return name.charAt(0).toUpperCase()
  const email = auth.user?.email?.trim()
  if (email) return email.charAt(0).toUpperCase()
  return 'S'
})

const desktopGridStyle = computed(() => {
  return {
    gridTemplateColumns: `${leftCollapsed.value ? '56px' : 'minmax(256px, 276px)'} minmax(0, 1fr) minmax(256px, 276px)`,
  }
})

const layerTracks = computed<EditorTrack[]>(() => {
  const layers = new Map<number, EditorClip[]>()
  for (const clip of tracks.value.flatMap((track) => track.clips)) {
    const layer = clip.layer ?? 1
    if (!layers.has(layer)) layers.set(layer, [])
    layers.get(layer)!.push(clip)
  }
  const sortedLayers = Array.from(layers.keys()).sort((a, b) => b - a)
  return sortedLayers.map((layer) => ({
    id: `layer-${layer}`,
    type: 'layer',
    label: `Layer ${layer}`,
    layer,
    clips: layers.get(layer)!.slice().sort((a, b) => a.startTime - b.startTime),
  }))
})

const workspaceVideoId = computed(() => String(route.params.id))

watch(duration, (nextDuration) => {
  if (playheadTime.value > nextDuration) setPlayhead(nextDuration)
})

watch(
  () => route.params.id,
  async () => {
    await loadWorkspace()
  }
)

function markLocalSaving() {
  saveState.value = 'saving'
  if (saveStateTimer) clearTimeout(saveStateTimer)
  saveStateTimer = setTimeout(() => {
    saveState.value = 'saved'
  }, 420)
}

function handleProjectRename(nextName: string) {
  setProjectName(nextName)
  markLocalSaving()
}

async function loadWorkspace() {
  try {
    const source = await api.videos.get(workspaceVideoId.value)
    previewUrl.value = source?.video_url || source?.thumbnail_url || ''
    previewDuration.value = Number(source?.duration) || 1
    setProjectName(source?.original_filename || source?.filename || 'Untitled video')
    setSourceVideoClip({
      sourceId: workspaceVideoId.value,
      sourceUrl: previewUrl.value,
      label: source?.original_filename || source?.filename || 'Source clip',
      duration: Number(source?.duration) || 1,
      aspectRatio: inferAspectRatio(source?.width, source?.height),
    })
    outputSettings.value.width = Number(source?.width) || outputSettings.value.width
    outputSettings.value.height = Number(source?.height) || outputSettings.value.height
    await loadMediaLibrary()
    saveState.value = 'saved'
  } catch (error: any) {
    saveState.value = 'error'
    toast.error(error?.data?.detail ?? 'Could not load editor workspace')
  }
}

async function loadMediaLibrary() {
  const items: MediaLibraryItem[] = []

  try {
    const videos = await api.videos.list({ limit: 24 })
    for (const entry of (videos?.items ?? [])) {
      items.push({
        id: `video-${entry.id}`,
        name: entry.original_filename || entry.filename,
        type: 'video',
        thumbnail: entry.thumbnail_url || entry.video_url,
        duration: Number(entry.duration) || undefined,
        sourceId: String(entry.id),
        sourceUrl: entry.video_url,
      })
    }
  } catch {
    // Keep loading other media sources.
  }

  try {
    const branding = await api.branding.list()
    for (const asset of (branding?.items ?? [])) {
      const assetType = asset.type === 'audio' ? 'audio' : 'image'
      items.push({
        id: `asset-${asset.id}`,
        name: asset.filename || 'Asset',
        type: assetType,
        thumbnail: asset.url,
        sourceId: String(asset.id),
        sourceUrl: asset.url,
        storagePath: asset.storage_path,
      })
    }
  } catch {
    // Optional source.
  }

  mediaItems.value = items
}

function syncPreviewDuration(nextDuration: number) {
  if (!Number.isFinite(nextDuration) || nextDuration <= 0) return
  previewDuration.value = nextDuration
  const videoTrack = tracks.value.find((track) => track.type === 'video')
  const audioTrack = tracks.value.find((track) => track.type === 'audio')
  const mainVideoClip = videoTrack?.clips[0]
  const mainAudioClip = audioTrack?.clips[0]
  if (mainVideoClip) {
    updateClip(mainVideoClip.id, { duration: nextDuration, trimEnd: nextDuration }, { recordHistory: false })
  }
  if (mainAudioClip) {
    updateClip(mainAudioClip.id, { duration: nextDuration }, { recordHistory: false })
  }
}

function syncClipMeta(payload: { clipId: string; duration?: number }) {
  const clip = tracks.value.flatMap((track) => track.clips).find((entry) => entry.id === payload.clipId)
  if (!clip || !payload.duration || !Number.isFinite(payload.duration)) return
  updateClip(clip.id, {
    duration: Math.max(0.1, payload.duration),
    trimEnd: Math.max(0.1, payload.duration),
  }, { recordHistory: false })
  if (clip.sourceId === workspaceVideoId.value) {
    previewDuration.value = payload.duration
  }
}

function openImportDialog() {
  importInputRef.value?.click()
}

async function onImportSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const mediaType = inferMediaType(file)
  try {
    saveState.value = 'saving'
    if (mediaType === 'image') {
      await api.branding.upload(file, 'image')
    } else if (mediaType === 'video') {
      await api.videos.upload(file, file.name)
    } else {
      throw new Error('Unsupported file type. Please upload a video or image file.')
    }
    await loadMediaLibrary()
    toast.success('Media uploaded to your library')
    saveState.value = 'saved'
  } catch (error: any) {
    saveState.value = 'error'
    toast.error(error?.data?.detail ?? 'Could not upload media')
  } finally {
    input.value = ''
  }
}

function handleAddText(styleName: string) {
  const layer = selectedClip.value?.layer
  const clip = addClip('graphics', {
    type: 'text',
    label: styleName,
    text: styleName === 'Plain text' ? 'Text' : styleName,
    startTime: playheadTime.value,
    duration: 3,
    layer,
    position: { x: 28, y: 22 },
    size: { width: 42, height: 18 },
    lockAspectRatio: false,
    style: { color: '#ffffff', outline: true },
  })
  if (clip) {
    activeRightTab.value = 'shape'
    markLocalSaving()
  }
}

function handleAddShape(shapeName: string) {
  const layer = selectedClip.value?.layer
  const clip = addClip('graphics', {
    type: 'shape',
    label: shapeName,
    startTime: playheadTime.value,
    duration: 5,
    layer,
    position: { x: 24, y: 18 },
    size: { width: 38, height: 38 },
    lockAspectRatio: false,
    style: { color: '#8f8cae', outline: false },
  })
  if (clip) {
    activeRightTab.value = 'shape'
    markLocalSaving()
  }
}

function handleAddTransition(transitionName: string) {
  if (!selectedClip.value) {
    toast.info('Select a clip to apply a transition')
    return
  }
  const isFade = transitionName.toLowerCase().includes('fade')
  const base = isFade ? 0.6 : 0.4
  updateClip(selectedClip.value.id, {
    effects: {
      ...selectedClip.value.effects,
      fadeIn: base,
      fadeOut: base,
    },
  })
  markLocalSaving()
  toast.success(`${transitionName} applied`)
}

async function handleAddMedia(item: MediaLibraryItem) {
  const layer = selectedClip.value?.layer
  if (item.type === 'video') {
    addClip('video', {
      type: 'video',
      label: item.name,
      startTime: duration.value,
      duration: item.duration ?? 4,
      layer,
      sourceId: item.sourceId,
      sourceUrl: item.sourceUrl,
      position: { x: 0, y: 0 },
      size: { width: 100, height: 100 },
      effects: { speed: 1, fadeIn: 0, fadeOut: 0, filter: 'None' },
    })
    toast.info('Video added to the timeline')
    markLocalSaving()
    return
  }

  if (item.type === 'audio') {
    addClip('audio', {
      type: 'audio',
      label: item.name,
      startTime: playheadTime.value,
      duration: 6,
      layer,
      sourceId: item.sourceId,
      sourceUrl: item.sourceUrl,
    })
    toast.info('Audio added to the timeline')
    markLocalSaving()
    return
  }

  addClip('graphics', {
    type: 'image',
    label: item.name,
    startTime: playheadTime.value,
    duration: 3,
    layer,
    sourceId: item.sourceId,
    sourceUrl: item.sourceUrl,
    position: { x: 30, y: 18 },
    size: { width: 40, height: 40 },
    rotation: 0,
    lockAspectRatio: true,
  })
  markLocalSaving()
}

const imageExtensions = new Set([
  'jpg',
  'jpeg',
  'png',
  'gif',
  'webp',
  'bmp',
  'tiff',
  'tif',
  'heic',
  'heif',
  'svg',
])

const videoExtensions = new Set([
  'mp4',
  'mov',
  'm4v',
  'webm',
  'mkv',
  'avi',
  'mpeg',
  'mpg',
  'ogv',
  '3gp',
  '3g2',
  'ts',
])

function inferMediaType(file: File) {
  if (file.type.startsWith('image/')) return 'image'
  if (file.type.startsWith('video/')) return 'video'
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (!ext) return null
  if (imageExtensions.has(ext)) return 'image'
  if (videoExtensions.has(ext)) return 'video'
  return null
}

function handleClipUpdate(clipId: string, patch: Partial<EditorClip>) {
  updateClip(clipId, patch, { recordHistory: false })
  markLocalSaving()
}

function splitSelectedClipAtPlayhead() {
  if (!splitSelectedClip(playheadTime.value)) {
    toast.info('Move playhead inside a clip to split it')
    return
  }
  markLocalSaving()
}

function duplicateSelectedClipAction() {
  if (!duplicateSelectedClip()) {
    toast.info('Select a clip to duplicate')
    return
  }
  markLocalSaving()
}

function removeSelectedClipAction() {
  if (!removeSelectedClip()) {
    toast.info('Select a clip to delete')
    return
  }
  markLocalSaving()
}

function handleTimelineTrim(payload: { clipId: string; startTime: number; duration: number }) {
  const clip = tracks.value.flatMap((track) => track.clips).find((entry) => entry.id === payload.clipId)
  if (!clip) return

  updateClip(payload.clipId, {
    startTime: payload.startTime,
    duration: payload.duration,
    trimStart: payload.startTime,
    trimEnd: payload.startTime + payload.duration,
  })
  markLocalSaving()

  if (clip.type === 'video' && clip.sourceId === workspaceVideoId.value) {
    const trimStart = Math.max(0, payload.startTime)
    const trimEnd = Math.max(trimStart + 0.1, trimStart + payload.duration)
    executeEditorOp('trim_clip', {
      start: trimStart,
      end: trimEnd,
    }, 'Trim applied')
    updateClip(payload.clipId, {
      startTime: 0,
      duration: Math.max(0.1, trimEnd - trimStart),
      trimStart,
      trimEnd,
    }, { recordHistory: false })
  }
}

function handleTimelineMove(payload: { clipId: string; startTime: number; layer?: number }) {
  const clip = tracks.value.flatMap((track) => track.clips).find((entry) => entry.id === payload.clipId)
  if (!clip) return
  updateClip(payload.clipId, {
    startTime: payload.startTime,
    layer: payload.layer ?? clip.layer,
  })
  markLocalSaving()
}

async function executeEditorOp(op: string, params: Record<string, unknown>, successMessage?: string) {
  if (operationRunning.value) {
    toast.info('Please wait for the current render to finish')
    return
  }
  operationRunning.value = true
  saveState.value = 'saving'
  isPlaying.value = false

  try {
    const shouldSaveToLibrary = op === 'export_video'
    const response = await api.editorOps.execute(workspaceVideoId.value, op, params, {
      saveToLibrary: shouldSaveToLibrary,
      outputTitle: shouldSaveToLibrary ? `${projectName.value} - ${op}` : undefined,
    }) as EditorOpResponse
    if (response?.error) throw new Error(response.error)

    if (response?.output_url) {
      previewUrl.value = response.output_url
      const mainVideoClip = tracks.value.find((track) => track.type === 'video')?.clips[0]
      if (mainVideoClip) {
        updateClip(mainVideoClip.id, { sourceUrl: response.output_url }, { recordHistory: false })
      }
    }

    saveState.value = 'saved'
    toast.success(successMessage ?? `${op} completed`)
    if (op === 'export_video' && response?.output_url) {
      window.open(response.output_url, '_blank', 'noopener')
    }
  } catch (error: any) {
    saveState.value = 'error'
    toast.error(error?.data?.detail ?? error?.message ?? `Operation failed: ${op}`)
  } finally {
    operationRunning.value = false
  }
}

function applyFade(payload: { fadeIn: number; fadeOut: number; commit?: boolean }) {
  if (!selectedClip.value) return
  updateClip(selectedClip.value.id, {
    effects: {
      ...selectedClip.value.effects,
      fadeIn: payload.fadeIn,
      fadeOut: payload.fadeOut,
    },
  }, { recordHistory: payload.commit === true })
  markLocalSaving()
}

function applySpeed(payload: { speed: number; commit?: boolean }) {
  if (!selectedClip.value) return
  updateClip(selectedClip.value.id, {
    effects: {
      ...selectedClip.value.effects,
      speed: payload.speed,
    },
  }, { recordHistory: payload.commit === true })
  markLocalSaving()
}

const filterColorMap: Record<string, {
  brightness: number
  contrast: number
  saturation: number
  gamma: number
  hue?: number
  overlayColor?: string
  overlayOpacity?: number
  overlayBlend?: string
}> = {
  None: { brightness: 0, contrast: 1, saturation: 1, gamma: 1, hue: 0, overlayColor: 'transparent', overlayOpacity: 0, overlayBlend: 'soft-light' },
  Retro: { brightness: -0.05, contrast: 1.1, saturation: 0.86, gamma: 1.1, hue: -5, overlayColor: '#c9a06f', overlayOpacity: 0.1, overlayBlend: 'soft-light' },
  'Orange and teal': { brightness: 0.05, contrast: 1.2, saturation: 1.2, gamma: 1, hue: 5, overlayColor: '#2da1b0', overlayOpacity: 0.12, overlayBlend: 'overlay' },
  'Bold and blue': { brightness: -0.03, contrast: 1.28, saturation: 1.1, gamma: 1.05, hue: -2, overlayColor: '#1d4ed8', overlayOpacity: 0.08, overlayBlend: 'soft-light' },
  'Golden hour': { brightness: 0.08, contrast: 1.15, saturation: 1.15, gamma: 0.95, hue: 6, overlayColor: '#f59e0b', overlayOpacity: 0.12, overlayBlend: 'soft-light' },
  'Vibrant vlogger': { brightness: 0.05, contrast: 1.25, saturation: 1.32, gamma: 1.05, hue: 0, overlayColor: '#7c3aed', overlayOpacity: 0.08, overlayBlend: 'overlay' },
  'Purple undertone': { brightness: 0, contrast: 1.18, saturation: 1.08, gamma: 1.12, hue: 2, overlayColor: '#4c1d95', overlayOpacity: 0.1, overlayBlend: 'soft-light' },
  'Winter sunset': { brightness: 0.04, contrast: 1.16, saturation: 1.05, gamma: 0.96, hue: -4, overlayColor: '#0ea5e9', overlayOpacity: 0.08, overlayBlend: 'soft-light' },
  '35mm': { brightness: -0.05, contrast: 1.22, saturation: 0.8, gamma: 1.08, hue: -6, overlayColor: '#111827', overlayOpacity: 0.1, overlayBlend: 'soft-light' },
  Contrast: { brightness: -0.02, contrast: 1.4, saturation: 1.05, gamma: 1, hue: 0, overlayColor: 'transparent', overlayOpacity: 0, overlayBlend: 'soft-light' },
  Autumn: { brightness: 0.03, contrast: 1.2, saturation: 1.15, gamma: 0.98, hue: 8, overlayColor: '#f59e0b', overlayOpacity: 0.1, overlayBlend: 'soft-light' },
  Winter: { brightness: 0.01, contrast: 1.22, saturation: 0.92, gamma: 1.06, hue: -8, overlayColor: '#93c5fd', overlayOpacity: 0.08, overlayBlend: 'soft-light' },
}

function applyFilterPreset(payload: { preset: string; commit?: boolean }) {
  const config = filterColorMap[payload.preset] ?? filterColorMap.None
  if (!selectedClip.value) return
  updateClip(selectedClip.value.id, {
    effects: {
      ...selectedClip.value.effects,
      filter: payload.preset,
      brightness: config.brightness,
      contrast: config.contrast,
      saturation: config.saturation,
      gamma: config.gamma,
      hue: config.hue ?? 0,
      overlayColor: config.overlayColor,
      overlayOpacity: config.overlayOpacity ?? 0,
      overlayBlend: config.overlayBlend ?? 'soft-light',
    },
  }, { recordHistory: payload.commit === true })
  markLocalSaving()
}

function applyColorAdjust(payload: { brightness: number; contrast: number; saturation: number; gamma: number; commit?: boolean }) {
  if (!selectedClip.value) return
  updateClip(selectedClip.value.id, {
    effects: {
      ...selectedClip.value.effects,
      brightness: payload.brightness,
      contrast: payload.contrast,
      saturation: payload.saturation,
      gamma: payload.gamma,
    },
  }, { recordHistory: payload.commit === true })
  markLocalSaving()
}

function applyAspectRatio(payload: { ratio: string; fitMode: 'fit' | 'fill' | 'stretch'; width: number; height: number; commit?: boolean }) {
  if (!selectedClip.value) return
  updateClip(selectedClip.value.id, {
    aspectRatio: payload.ratio,
    fitMode: payload.fitMode,
  }, { recordHistory: payload.commit === true })
  markLocalSaving()
}

function applyShapeStyle(payload: { color: string; outline: boolean; commit?: boolean }) {
  if (!selectedClip.value || selectedClip.value.type !== 'shape') {
    toast.info('Select a shape clip first')
    return
  }
  updateClip(selectedClip.value.id, {
    style: {
      ...selectedClip.value.style,
      color: payload.color,
      outline: payload.outline,
    },
  }, { recordHistory: payload.commit === true })
  markLocalSaving()
}

function exportVideo() {
  executeEditorOp('export_video', {
    width: outputSettings.value.width,
    height: outputSettings.value.height,
    fps: outputSettings.value.fps,
    bitrate: outputSettings.value.bitrate,
  }, 'Export completed')
}

function inferAspectRatio(width?: number, height?: number) {
  const w = Number(width)
  const h = Number(height)
  if (!w || !h) return '16:9'
  const ratio = w / h
  const known = [
    { key: '16:9', value: 16 / 9 },
    { key: '9:16', value: 9 / 16 },
    { key: '1:1', value: 1 },
    { key: '4:5', value: 4 / 5 },
    { key: '4:3', value: 4 / 3 },
    { key: '21:9', value: 21 / 9 },
  ]
  let best = known[0]
  let score = Number.POSITIVE_INFINITY
  for (const option of known) {
    const delta = Math.abs(option.value - ratio)
    if (delta < score) {
      score = delta
      best = option
    }
  }
  return best.key
}

onMounted(async () => {
  await auth.initialize()
  await loadWorkspace()
})

function stopPlaybackLoop() {
  if (playbackFrame) {
    cancelAnimationFrame(playbackFrame)
    playbackFrame = null
  }
  lastFrameTime = 0
}

function startPlaybackLoop() {
  if (playbackFrame) return
  playbackFrame = requestAnimationFrame(function step(now: number) {
    if (!isPlaying.value) {
      stopPlaybackLoop()
      return
    }
    if (!lastFrameTime) lastFrameTime = now
    const delta = (now - lastFrameTime) / 1000
    lastFrameTime = now
    const next = playheadTime.value + delta
    if (next >= timelineDuration.value) {
      setPlayhead(timelineDuration.value)
      isPlaying.value = false
      stopPlaybackLoop()
      return
    }
    setPlayhead(next)
    playbackFrame = requestAnimationFrame(step)
  })
}

watch(isPlaying, (playing) => {
  if (playing) {
    startPlaybackLoop()
  } else {
    stopPlaybackLoop()
  }
})

onBeforeUnmount(() => {
  stopPlaybackLoop()
})
</script>

<style scoped>
.mobile-select {
  width: 100%;
  border-radius: 0.5rem;
  border: 1px solid #2b2a25;
  background: #121310;
  color: #f5f5f5;
  font-size: 0.82rem;
  padding: 0.42rem 0.6rem;
}
</style>
