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
      @undo="handleUndo"
      @redo="handleRedo"
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
              <option value="audio">Audio</option>
              <option value="fade">Fade</option>
              <option value="effects">Effects</option>
              <option value="filters">Filters</option>
              <option value="adjust">Adjust</option>
              <option value="speed">Speed</option>
              <option value="aspect">Aspect</option>
            </select>
          </div>
        </div>

        <div class="flex-1 min-h-0 h-full">
          <EditorPreview
            ref="previewRef"
            :clips="clips"
            :selected-clip-id="selectedClipId"
            :current-time="playheadTime"
            :duration="timelineDuration"
            :playing="isPlaying"
            :volume="previewVolume"
            :show-controls="false"
            :fallback-url="previewUrl"
            :fallback-poster="previewPoster"
            @update:current-time="setPlayhead"
            @update:playing="isPlaying = $event"
            @update:volume="previewVolume = $event"
            @update:clip="handleClipUpdate"
            @update:clip-meta="syncClipMeta"
            @select-clip="selectClip"
            @split="splitSelectedClipAtPlayhead"
            @duplicate="duplicateSelectedClipAction"
            @delete="removeSelectedClipAction"
            @open-panel="activeRightTab = $event"
          />
        </div>

        <div class="hidden lg:block editor-resizer editor-resizer-horizontal" @pointerdown.prevent="startResize('timeline', $event)" />

        <div ref="controlsRef" class="editor-controls">
          <button type="button" class="editor-btn" @click="seekToStart" aria-label="Skip to start">
            <UiIcon name="ChevronsLeft" :size="16" />
          </button>
          <button type="button" class="editor-btn" @click="seekBy(-5)" aria-label="Seek backward 5 seconds">
            <UiIcon name="ChevronLeft" :size="16" />
            <span class="text-[10px] leading-none">5</span>
          </button>
          <button type="button" class="editor-btn editor-btn-primary" @click="togglePlay" aria-label="Play or pause">
            <UiIcon :name="isPlaying ? 'Pause' : 'Play'" :size="18" class="mx-auto" />
          </button>
          <button type="button" class="editor-btn" @click="seekBy(5)" aria-label="Seek forward 5 seconds">
            <span class="text-[10px] leading-none">5</span>
            <UiIcon name="ChevronRight" :size="16" />
          </button>
          <button type="button" class="editor-btn" @click="seekToEnd" aria-label="Skip to end">
            <UiIcon name="ChevronsRight" :size="16" />
          </button>
          <span class="mx-2 text-sm font-normal text-surface-100 tabular-nums">
            {{ formatTime(playheadTime) }} / {{ formatTime(timelineDuration) }}
          </span>
          <div class="hidden lg:flex items-center gap-2">
            <button type="button" class="editor-btn" @click="splitSelectedClipAtPlayhead" aria-label="Split clip">
              <UiIcon name="Scissors" :size="14" />
            </button>
            <button type="button" class="editor-btn" @click="duplicateSelectedClipAction" aria-label="Duplicate clip">
              <UiIcon name="Copy" :size="14" />
            </button>
            <button type="button" class="editor-btn" @click="removeSelectedClipAction" aria-label="Delete clip">
              <UiIcon name="Trash2" :size="14" />
            </button>
          </div>
          <div class="hidden md:flex items-center gap-2 ml-2">
            <UiIcon name="Volume2" :size="14" class="text-surface-400" />
            <input v-model.number="previewVolume" type="range" min="0" max="1" step="0.01" class="w-24 accent-primary-500" />
            <button type="button" class="editor-btn" @click="togglePreviewFullscreen" aria-label="Fullscreen">
              <UiIcon name="Maximize" :size="14" />
            </button>
          </div>
        </div>

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
            @add-layer="handleAddLayer"
            @remove-layer="handleRemoveLayer"
            @open-panel="activeRightTab = $event"
            @apply-transition-between="applyTransitionBetweenClips"
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
        @apply:transition="applyTransition"
        @apply:audio="applyAudio"
        @apply:speed="applySpeed"
        @apply:filter="applyFilterPreset"
        @apply:layer="applyLayer"
        @apply:color="applyColorAdjust"
        @apply:aspect="applyAspectRatio"
        @apply:shape="applyShapeStyle"
      />
    </div>

    <input
      ref="importInputRef"
      type="file"
      accept="video/*,image/*,audio/*"
      class="hidden"
      @change="onImportSelected"
    />

    <UiToast />
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { EditorClip, EditorLayerGroup, EditorTrack } from '~/composables/useEditorState'
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

interface VideoMediaUrlItem {
  id: string
  video_url?: string
  thumbnail_url?: string
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
  exportState,
  loadState,
  resetState,
  addClip,
  updateClip,
  selectClip,
  removeSelectedClip,
  removeLayerClips,
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
const gridRef = ref<HTMLDivElement | null>(null)
const centerRef = ref<HTMLDivElement | null>(null)
const previewRef = ref<{ toggleFullscreen?: () => void } | null>(null)
const controlsRef = ref<HTMLDivElement | null>(null)
const previewVolume = ref(1)
const COLLAPSED_SIDEBAR_WIDTH = 67
const DEFAULT_SIDEBAR_WIDTH = 264
const MIN_SIDEBAR_WIDTH = 216
const leftWidth = ref(DEFAULT_SIDEBAR_WIDTH)
const rightWidth = ref(DEFAULT_SIDEBAR_WIDTH)
const timelineHeight = ref(280)
const resizerSize = 6
const previewUrl = ref('')
const previewPoster = ref('')
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

const extraLayers = ref<Record<EditorLayerGroup, number[]>>({
  video: [],
  graphics: [],
  audio: [],
})

let persistTimer: ReturnType<typeof setTimeout> | null = null
let resizeCleanup: (() => void) | null = null
let windowResizeCleanup: (() => void) | null = null
let mediaUrlRefreshTimer: ReturnType<typeof setTimeout> | null = null

const MEDIA_URL_REFRESH_BUFFER_SECONDS = 90
const runtimeConfig = useRuntimeConfig()
const apiBaseUrl = computed(() => {
  const raw = (runtimeConfig.public.apiUrl || '').trim()
  return raw ? raw.replace(/\/$/, '') : ''
})

const accountInitial = computed(() => {
  const name = auth.user?.name?.trim()
  if (name) return name.charAt(0).toUpperCase()
  const email = auth.user?.email?.trim()
  if (email) return email.charAt(0).toUpperCase()
  return 'S'
})

const desktopGridStyle = computed(() => {
  const leftColumn = leftCollapsed.value ? `${COLLAPSED_SIDEBAR_WIDTH}px` : `${leftWidth.value}px`
  const leftGrip = leftCollapsed.value ? 0 : resizerSize
  return {
    gridTemplateColumns: `${leftColumn} ${leftGrip}px minmax(0, 1fr) ${resizerSize}px ${rightWidth.value}px`,
  }
})

const layerTracks = computed<EditorTrack[]>(() => {
  const groupOrder: EditorLayerGroup[] = ['video', 'graphics', 'audio']
  const grouped = new Map<EditorLayerGroup, Map<number, EditorClip[]>>()
  groupOrder.forEach((group) => grouped.set(group, new Map()))

  for (const clip of tracks.value.flatMap((track) => track.clips)) {
    const group = clip.layerGroup ?? (clip.type === 'audio' ? 'audio' : clip.type === 'video' ? 'video' : 'graphics')
    const layer = clip.layer ?? 1
    const groupLayers = grouped.get(group)!
    if (!groupLayers.has(layer)) groupLayers.set(layer, [])
    groupLayers.get(layer)!.push(clip)
  }

  const results: EditorTrack[] = []
  for (const group of groupOrder) {
    const groupLayers = grouped.get(group)!
    const extra = extraLayers.value[group] ?? []
    extra.forEach((layer) => {
      if (!groupLayers.has(layer)) groupLayers.set(layer, [])
    })
    if (groupLayers.size === 0) groupLayers.set(1, [])

    const sortedLayers = Array.from(groupLayers.keys()).sort((a, b) => b - a)
    results.push({
      id: `${group}-header`,
      type: 'layer',
      label: `${group.charAt(0).toUpperCase()}${group.slice(1)} layers`,
      clips: [],
      group,
      isHeader: true,
    })
    sortedLayers.forEach((layer) => {
      results.push({
        id: `${group}-layer-${layer}`,
        type: 'layer',
        label: `Layer ${layer}`,
        layer,
        group,
        clips: groupLayers.get(layer)!.slice().sort((a, b) => a.startTime - b.startTime),
      })
    })
  }
  return results
})

const projectId = computed(() => String(route.params.id))

watch(duration, (nextDuration) => {
  if (playheadTime.value > nextDuration) setPlayhead(nextDuration)
  previewDuration.value = Math.max(1, nextDuration)
})

watch(
  () => route.params.id,
  async () => {
    await loadWorkspace()
  }
)

async function persistProjectState() {
  try {
    if (!projectId.value) return
    const state = sanitizeProjectStateForPersist({
      ...exportState(),
      outputSettings: outputSettings.value,
    })
    await api.projects.update(projectId.value, {
      name: projectName.value,
      state,
    })
    saveState.value = 'saved'
  } catch {
    saveState.value = 'error'
  }
}

function schedulePersist() {
  if (persistTimer) clearTimeout(persistTimer)
  persistTimer = setTimeout(() => {
    persistProjectState()
  }, 900)
}

function markLocalSaving() {
  saveState.value = 'saving'
  schedulePersist()
}

function handleProjectRename(nextName: string) {
  setProjectName(nextName)
  markLocalSaving()
}

function handleUndo() {
  if (undo()) {
    markLocalSaving()
  }
}

function handleRedo() {
  if (redo()) {
    markLocalSaving()
  }
}

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value))
}

function isProtectedMediaPath(url: string) {
  return url.includes('/videos/') && (url.includes('/stream') || url.includes('/thumbnail'))
}

function stripTransientMediaToken(url?: string) {
  if (!url || !isProtectedMediaPath(url)) return url
  try {
    const base = typeof window !== 'undefined' ? window.location.origin : 'http://localhost'
    const parsed = new URL(url, base)
    parsed.searchParams.delete('token')
    if (/^https?:\/\//i.test(url)) return parsed.toString()
    return `${parsed.pathname}${parsed.search}${parsed.hash}`
  } catch {
    const cleaned = url
      .replace(/([?&])token=[^&]*(&?)/, (_m, sep, tail) => (sep === '?' && tail ? '?' : sep))
      .replace(/[?&]$/, '')
    return cleaned
  }
}

function sanitizeProjectStateForPersist(state: any) {
  return {
    ...state,
    tracks: (state?.tracks ?? []).map((track: any) => ({
      ...track,
      clips: (track?.clips ?? []).map((clip: any) => ({
        ...clip,
        sourceUrl: clip?.type === 'video' && clip?.sourceId
          ? undefined
          : stripTransientMediaToken(clip?.sourceUrl),
        posterUrl: clip?.type === 'video' && clip?.sourceId
          ? undefined
          : stripTransientMediaToken(clip?.posterUrl),
      })),
    })),
  }
}

function syncPreviewFallbackMedia() {
  const firstVideo = tracks.value
    .flatMap((track) => track.clips)
    .filter((clip) => clip.type === 'video')
    .slice()
    .sort((a, b) => a.startTime - b.startTime)[0]
  previewUrl.value = firstVideo?.sourceUrl || ''
  previewPoster.value = firstVideo?.posterUrl || ''
  previewDuration.value = Math.max(1, duration.value)
}

function clearMediaUrlRefreshTimer() {
  if (!mediaUrlRefreshTimer) return
  clearTimeout(mediaUrlRefreshTimer)
  mediaUrlRefreshTimer = null
}

function scheduleMediaUrlRefresh(expiresIn?: number) {
  clearMediaUrlRefreshTimer()
  if (typeof expiresIn !== 'number' || !Number.isFinite(expiresIn) || expiresIn <= 0) return
  const refreshInMs = Math.max(30_000, (expiresIn - MEDIA_URL_REFRESH_BUFFER_SECONDS) * 1000)
  mediaUrlRefreshTimer = setTimeout(() => {
    void refreshProjectVideoSources()
  }, refreshInMs)
}

function collectTimelineVideoIds() {
  const ids = new Set<string>()
  for (const clip of tracks.value.flatMap((track) => track.clips)) {
    if (clip.type !== 'video' || !clip.sourceId) continue
    const id = String(clip.sourceId).trim()
    if (id) ids.add(id)
  }
  return Array.from(ids)
}

function startResize(type: 'left' | 'right' | 'timeline', event: PointerEvent) {
  const grid = gridRef.value
  const center = centerRef.value
  if (!grid || !center) return
  const gridRect = grid.getBoundingClientRect()
  const centerRect = center.getBoundingClientRect()

  const minLeft = MIN_SIDEBAR_WIDTH
  const minRight = MIN_SIDEBAR_WIDTH
  const minCenter = 420
  const minTimeline = 200
  const minPreview = 240

  function onMove(e: PointerEvent) {
    if (type === 'left') {
      const maxLeft = Math.max(minLeft, gridRect.width - minCenter - rightWidth.value - resizerSize * 2)
      leftWidth.value = clamp(e.clientX - gridRect.left, minLeft, maxLeft)
      return
    }

    if (type === 'right') {
      const maxRight = Math.max(minRight, gridRect.width - minCenter - (leftCollapsed.value ? COLLAPSED_SIDEBAR_WIDTH : leftWidth.value) - resizerSize * 2)
      rightWidth.value = clamp(gridRect.right - e.clientX, minRight, maxRight)
      return
    }

    const controlsHeight = controlsRef.value?.getBoundingClientRect().height ?? 0
    const pointerOffset = e.clientY - centerRect.top - controlsHeight - resizerSize
    const available = centerRect.height - controlsHeight - resizerSize
    const maxTimeline = Math.max(minTimeline, available - minPreview)
    timelineHeight.value = clamp(available - pointerOffset, minTimeline, maxTimeline)
  }

  function onUp() {
    window.removeEventListener('pointermove', onMove)
    window.removeEventListener('pointerup', onUp)
    resizeCleanup = null
  }

  window.addEventListener('pointermove', onMove)
  window.addEventListener('pointerup', onUp)
  resizeCleanup = onUp
  onMove(event)
}

function syncTimelineHeight() {
  const center = centerRef.value
  if (!center) return
  const rect = center.getBoundingClientRect()
  const controlsHeight = controlsRef.value?.getBoundingClientRect().height ?? 0
  const minTimeline = 200
  const minPreview = 240
  const maxTimeline = Math.max(minTimeline, rect.height - controlsHeight - resizerSize - minPreview)
  timelineHeight.value = clamp(timelineHeight.value, minTimeline, maxTimeline)
}

async function loadWorkspace() {
  try {
    saveState.value = 'saving'
    const project = await api.projects.get(projectId.value)
    if (project?.state && project.state.tracks) {
      loadState(project.state)
    } else {
      resetState()
    }
    setProjectName(project?.name || 'Untitled project')
    extraLayers.value = { video: [], graphics: [], audio: [] }
    if (project?.state?.outputSettings) {
      outputSettings.value = { ...outputSettings.value, ...project.state.outputSettings }
    }
    await loadMediaLibrary()
    hydrateProjectMedia()
    await refreshProjectVideoSources()
    applyVideoClipFallbacks()
    await refreshPersistedStreamTokens()
    saveState.value = 'saved'
  } catch (error: any) {
    saveState.value = 'error'
    toast.error(error?.data?.detail ?? 'Could not load editor workspace')
  }
}

async function refreshPersistedStreamTokens() {
  const clipEntries = tracks.value.flatMap((track) => track.clips)
  if (!clipEntries.length) return
  await Promise.all(
    clipEntries.map(async (clip) => {
      const patch: Partial<EditorClip> = {}
      const source = clip.sourceUrl
      if (source && isProtectedMediaPath(source)) {
        const refreshed = await api.withAccessToken(source)
        if (refreshed && refreshed !== source) patch.sourceUrl = refreshed
      }
      const poster = clip.posterUrl
      if (poster && isProtectedMediaPath(poster)) {
        const refreshedPoster = await api.withAccessToken(poster)
        if (refreshedPoster && refreshedPoster !== poster) patch.posterUrl = refreshedPoster
      }
      if (!Object.keys(patch).length) return
      updateClip(clip.id, patch, { recordHistory: false })
    })
  )
  syncPreviewFallbackMedia()
}

function buildStreamUrl(sourceId: string) {
  if (!apiBaseUrl.value) return ''
  return `${apiBaseUrl.value}/videos/${sourceId}/stream`
}

function buildThumbnailUrl(sourceId: string) {
  if (!apiBaseUrl.value) return ''
  return `${apiBaseUrl.value}/videos/${sourceId}/thumbnail`
}

function applyVideoClipFallbacks() {
  for (const clip of tracks.value.flatMap((track) => track.clips)) {
    if (clip.type !== 'video' || !clip.sourceId) continue
    const patch: Partial<EditorClip> = {}
    if (!clip.sourceUrl) {
      const streamUrl = buildStreamUrl(String(clip.sourceId))
      if (streamUrl) patch.sourceUrl = streamUrl
    }
    if (!clip.posterUrl) {
      const thumbUrl = buildThumbnailUrl(String(clip.sourceId))
      if (thumbUrl) patch.posterUrl = thumbUrl
    }
    if (!Object.keys(patch).length) continue
    updateClip(clip.id, patch, { recordHistory: false })
  }
  syncPreviewFallbackMedia()
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
        thumbnail: entry.thumbnail_url || undefined,
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
      const isAudio = asset.type === 'audio'
      const assetType = isAudio ? 'audio' : 'image'
      items.push({
        id: `asset-${asset.id}`,
        name: asset.filename || 'Asset',
        type: assetType,
        thumbnail: isAudio ? undefined : asset.url,
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

function hydrateProjectMedia() {
  const library = new Map<string, MediaLibraryItem>()
  for (const item of mediaItems.value) {
    if (item.sourceId) library.set(item.sourceId, item)
  }

  for (const clip of tracks.value.flatMap((track) => track.clips)) {
    if (!clip.sourceId) continue
    const match = library.get(clip.sourceId)
    if (!match) continue
    const patch: Partial<EditorClip> = {}
    if (!clip.sourceUrl && match.sourceUrl) patch.sourceUrl = match.sourceUrl
    if (!clip.posterUrl && match.thumbnail) patch.posterUrl = match.thumbnail
    if (Object.keys(patch).length) {
      updateClip(clip.id, patch, { recordHistory: false })
    }
  }

  syncPreviewFallbackMedia()
}

async function refreshProjectVideoSources() {
  const ids = collectTimelineVideoIds()
  if (!ids.length) {
    syncPreviewFallbackMedia()
    return
  }

  try {
    const response = await api.videos.mediaUrls(ids, {
      includeVideo: true,
      includeThumbnail: true,
    })
    const mediaById = new Map<string, VideoMediaUrlItem>()
    for (const item of response?.items ?? []) {
      if (!item?.id) continue
      mediaById.set(String(item.id), item)
    }

    for (const clip of tracks.value.flatMap((track) => track.clips)) {
      if (clip.type !== 'video' || !clip.sourceId) continue
      const resolved = mediaById.get(String(clip.sourceId))
      if (!resolved) continue

      const patch: Partial<EditorClip> = {}
      if (resolved.video_url && resolved.video_url !== clip.sourceUrl) patch.sourceUrl = resolved.video_url
      if (resolved.thumbnail_url && resolved.thumbnail_url !== clip.posterUrl) patch.posterUrl = resolved.thumbnail_url
      if (!Object.keys(patch).length) continue
      updateClip(clip.id, patch, { recordHistory: false })
    }

    mediaItems.value = mediaItems.value.map((item) => {
      if (item.type !== 'video' || !item.sourceId) return item
      const resolved = mediaById.get(String(item.sourceId))
      if (!resolved) return item
      const sourceUrl = resolved.video_url || item.sourceUrl
      const thumbnail = resolved.thumbnail_url || item.thumbnail
      if (sourceUrl === item.sourceUrl && thumbnail === item.thumbnail) return item
      return {
        ...item,
        sourceUrl,
        thumbnail,
      }
    })

    scheduleMediaUrlRefresh(response?.expires_in ?? undefined)
  } catch {
    // Keep existing URLs; editor remains usable with prior resolved links.
  }

  syncPreviewFallbackMedia()
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
  if (clip.type === 'video') {
    previewDuration.value = Math.max(previewDuration.value, payload.duration)
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
    } else if (mediaType === 'audio') {
      await api.branding.upload(file, 'audio')
    } else {
      throw new Error('Unsupported file type. Please upload a video, image, or audio file.')
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
  const layer = resolveLayerForGroup('graphics')
  const clip = addClip('graphics', {
    type: 'text',
    label: styleName,
    text: styleName === 'Plain text' ? 'Text' : styleName,
    startTime: playheadTime.value,
    duration: 3,
    layer,
    layerGroup: 'graphics',
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
  const layer = resolveLayerForGroup('graphics')
  const clip = addClip('graphics', {
    type: 'shape',
    label: shapeName,
    startTime: playheadTime.value,
    duration: 5,
    layer,
    layerGroup: 'graphics',
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
  const nextClip = findAdjacentNextClip(selectedClip.value)
  if (!nextClip) {
    toast.info('Drag the next clip against this one to apply a transition')
    return
  }
  const base = transitionName.toLowerCase().includes('fade') ? 0.6 : 0.4
  updateClip(selectedClip.value.id, {
    effects: {
      ...selectedClip.value.effects,
      transition: transitionName,
      transitionDuration: base,
      transitionWith: nextClip.id,
    },
  })
  markLocalSaving()
  toast.success(`${transitionName} applied between clips`)
}

async function handleAddMedia(item: MediaLibraryItem) {
  const layer = item.type === 'audio'
    ? resolveLayerForGroup('audio')
    : item.type === 'video'
      ? resolveLayerForGroup('video')
      : resolveLayerForGroup('graphics')
  if (item.type === 'video') {
    const clip = addClip('video', {
      type: 'video',
      label: item.name,
      startTime: duration.value,
      duration: item.duration ?? 4,
      layer,
      layerGroup: 'video',
      sourceId: item.sourceId,
      sourceUrl: item.sourceUrl,
      posterUrl: item.thumbnail,
      position: { x: 0, y: 0 },
      size: { width: 100, height: 100 },
      effects: { speed: 1, fadeIn: 0, fadeOut: 0, filter: 'None' },
    })
    if (clip && !previewUrl.value && item.sourceUrl) {
      previewUrl.value = item.sourceUrl
      previewPoster.value = item.thumbnail ?? ''
    }
    void refreshProjectVideoSources()
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
      layerGroup: 'audio',
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
    layerGroup: 'graphics',
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
const audioExtensions = new Set([
  'mp3',
  'wav',
  'm4a',
  'aac',
  'ogg',
  'flac',
])

function inferMediaType(file: File) {
  if (file.type.startsWith('image/')) return 'image'
  if (file.type.startsWith('video/')) return 'video'
  if (file.type.startsWith('audio/')) return 'audio'
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (!ext) return null
  if (imageExtensions.has(ext)) return 'image'
  if (videoExtensions.has(ext)) return 'video'
  if (audioExtensions.has(ext)) return 'audio'
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
  pruneTransitionsForAll()
  markLocalSaving()
}

const ATTACH_THRESHOLD_SECONDS = 0.05

function resolveClipGroup(clip: EditorClip) {
  return clip.layerGroup ?? (clip.type === 'audio' ? 'audio' : clip.type === 'video' ? 'video' : 'graphics')
}

function getLayerClips(group: EditorLayerGroup, layer: number, excludeId?: string) {
  return tracks.value
    .flatMap((track) => track.clips)
    .filter((entry) => {
      if (excludeId && entry.id === excludeId) return false
      const entryGroup = resolveClipGroup(entry)
      const entryLayer = entry.layer ?? 1
      return entryGroup === group && entryLayer === layer
    })
    .slice()
    .sort((a, b) => a.startTime - b.startTime)
}

function clampStartInLayer(group: EditorLayerGroup, layer: number, clipId: string, startTime: number, durationValue: number) {
  const peers = getLayerClips(group, layer, clipId)
  const desired = Math.max(0, startTime)
  const prev = peers.filter((clip) => clip.startTime + clip.duration <= desired).pop()
  const next = peers.find((clip) => clip.startTime >= desired)
  const minStart = prev ? prev.startTime + prev.duration : 0
  const maxStart = next ? next.startTime - durationValue : Number.POSITIVE_INFINITY
  if (maxStart < minStart) return minStart
  return Math.min(Math.max(desired, minStart), maxStart)
}

function getLayerNeighbors(group: EditorLayerGroup, layer: number, clipId: string) {
  const peers = getLayerClips(group, layer)
  const index = peers.findIndex((clip) => clip.id === clipId)
  return {
    prev: index > 0 ? peers[index - 1] : null,
    next: index >= 0 && index < peers.length - 1 ? peers[index + 1] : null,
  }
}

function findAdjacentNextClip(clip: EditorClip) {
  const group = resolveClipGroup(clip)
  if (group !== 'video') return null
  const layer = clip.layer ?? 1
  const peers = getLayerClips(group, layer, clip.id)
  const next = peers.find((entry) => entry.startTime >= clip.startTime + clip.duration - 0.0001)
  if (!next) return null
  const gap = next.startTime - (clip.startTime + clip.duration)
  if (Math.abs(gap) > ATTACH_THRESHOLD_SECONDS) return null
  return next
}

function isAttachedAdjacentPair(fromClip: EditorClip, toClip: EditorClip) {
  const fromGroup = resolveClipGroup(fromClip)
  const toGroup = resolveClipGroup(toClip)
  if (fromGroup !== 'video' || toGroup !== 'video') return false
  const fromLayer = fromClip.layer ?? 1
  const toLayer = toClip.layer ?? 1
  if (fromLayer !== toLayer) return false
  const layerClips = getLayerClips('video', fromLayer)
  const fromIndex = layerClips.findIndex((clip) => clip.id === fromClip.id)
  if (fromIndex < 0 || fromIndex >= layerClips.length - 1) return false
  const next = layerClips[fromIndex + 1]
  if (!next || next.id !== toClip.id) return false
  const gap = next.startTime - (fromClip.startTime + fromClip.duration)
  return Math.abs(gap) <= ATTACH_THRESHOLD_SECONDS
}

function clearClipTransition(clip: EditorClip) {
  if (!clip.effects?.transition && !clip.effects?.transitionWith) return
  updateClip(clip.id, {
    effects: {
      ...clip.effects,
      transition: undefined,
      transitionDuration: undefined,
      transitionWith: undefined,
    },
  }, { recordHistory: false })
}

function pruneTransitionsForLayer(group: EditorLayerGroup, layer: number) {
  if (group !== 'video') return
  const peers = getLayerClips(group, layer)
  for (let i = 0; i < peers.length; i += 1) {
    const clip = peers[i]
    const next = peers[i + 1]
    const transitionWith = clip.effects?.transitionWith
    const transitionName = clip.effects?.transition
    const durationValue = Number(clip.effects?.transitionDuration ?? 0)
    if (!transitionWith || !transitionName || durationValue <= 0) {
      if (transitionWith || transitionName) clearClipTransition(clip)
      continue
    }
    const gap = next ? next.startTime - (clip.startTime + clip.duration) : Number.POSITIVE_INFINITY
    const attached = next && next.id === transitionWith && Math.abs(gap) <= ATTACH_THRESHOLD_SECONDS
    if (!attached) clearClipTransition(clip)
  }
}

function pruneTransitionsForAll() {
  const layers = new Map<string, Set<number>>()
  for (const clip of tracks.value.flatMap((track) => track.clips)) {
    const group = resolveClipGroup(clip)
    const layer = clip.layer ?? 1
    if (!layers.has(group)) layers.set(group, new Set())
    layers.get(group)!.add(layer)
  }
  layers.forEach((layerSet, groupKey) => {
    const group = groupKey as EditorLayerGroup
    layerSet.forEach((layer) => pruneTransitionsForLayer(group, layer))
  })
}

function handleTimelineTrim(payload: { clipId: string; startTime: number; duration: number }) {
  const clip = tracks.value.flatMap((track) => track.clips).find((entry) => entry.id === payload.clipId)
  if (!clip) return

  const group = resolveClipGroup(clip)
  const layer = clip.layer ?? 1
  const neighbors = getLayerNeighbors(group, layer, clip.id)
  let nextStart = payload.startTime
  let nextDuration = Math.max(0.1, payload.duration)
  const originalEnd = clip.startTime + clip.duration
  const isStartTrim = Math.abs(payload.startTime - clip.startTime) > 0.0001

  if (isStartTrim) {
    if (neighbors.prev) {
      const prevEnd = neighbors.prev.startTime + neighbors.prev.duration
      nextStart = Math.max(nextStart, prevEnd)
    }
    nextStart = Math.min(nextStart, originalEnd - 0.1)
    nextDuration = Math.max(0.1, originalEnd - nextStart)
  } else if (neighbors.next) {
    const maxDuration = Math.max(0.1, neighbors.next.startTime - clip.startTime)
    nextDuration = Math.min(nextDuration, maxDuration)
  }

  const previousTrimStart = clip.trimStart ?? 0
  const startDelta = nextStart - clip.startTime
  const nextTrimStart = isStartTrim ? Math.max(0, previousTrimStart + startDelta) : previousTrimStart
  const nextTrimEnd = nextTrimStart + nextDuration

  updateClip(payload.clipId, {
    startTime: nextStart,
    duration: nextDuration,
    trimStart: nextTrimStart,
    trimEnd: nextTrimEnd,
  })
  pruneTransitionsForLayer(group, layer)
  markLocalSaving()
}

function handleTimelineMove(payload: { clipId: string; startTime: number; layer?: number; group?: EditorLayerGroup; createLayer?: boolean }) {
  const clip = tracks.value.flatMap((track) => track.clips).find((entry) => entry.id === payload.clipId)
  if (!clip) return
  const previousGroup = resolveClipGroup(clip)
  const previousLayer = clip.layer ?? 1
  const group = payload.group ?? previousGroup
  let nextLayer = payload.layer ?? previousLayer
  if (payload.createLayer && payload.group) {
    nextLayer = addLayer(payload.group)
  }
  const nextStart = clampStartInLayer(group, nextLayer ?? 1, clip.id, payload.startTime, clip.duration)
  updateClip(payload.clipId, {
    startTime: nextStart,
    layer: nextLayer ?? clip.layer,
    layerGroup: group,
  })
  pruneTransitionsForLayer(group, nextLayer ?? 1)
  if (previousGroup !== group || previousLayer !== nextLayer) {
    pruneTransitionsForLayer(previousGroup, previousLayer)
  }
  markLocalSaving()
}

function addLayer(group: EditorLayerGroup) {
  const existing = layerTracks.value.filter((track) => track.group === group && !track.isHeader).map((track) => track.layer ?? 0)
  const next = Math.max(0, ...existing) + 1
  const current = new Set(extraLayers.value[group] ?? [])
  current.add(next)
  extraLayers.value[group] = Array.from(current)
  markLocalSaving()
  return next
}

function resolveLayerForGroup(group: EditorLayerGroup) {
  const clip = selectedClip.value
  if (!clip) return undefined
  const clipGroup = clip.layerGroup ?? (clip.type === 'audio' ? 'audio' : clip.type === 'video' ? 'video' : 'graphics')
  if (clipGroup !== group) return undefined
  return clip.layer
}

function handleAddLayer(payload: { group: EditorLayerGroup }) {
  addLayer(payload.group)
}

function handleRemoveLayer(payload: { group: EditorLayerGroup; layer: number }) {
  const removed = removeLayerClips(payload.group, payload.layer)
  if (!removed) {
    toast.info('Layer is already empty')
    return
  }
  const current = new Set(extraLayers.value[payload.group] ?? [])
  current.delete(payload.layer)
  extraLayers.value[payload.group] = Array.from(current)
  pruneTransitionsForAll()
  markLocalSaving()
}

function applyTransitionBetweenClips(payload: { fromClipId: string; toClipId: string; name?: string; duration?: number }) {
  const fromClip = tracks.value.flatMap((track) => track.clips).find((entry) => entry.id === payload.fromClipId)
  const toClip = tracks.value.flatMap((track) => track.clips).find((entry) => entry.id === payload.toClipId)
  if (!fromClip) return
  const transitionName = payload.name
  const durationValue = Math.max(0, Number(payload.duration) || 0)
  if (!transitionName || transitionName === 'None' || durationValue <= 0) {
    clearClipTransition(fromClip)
    markLocalSaving()
    return
  }
  if (!toClip || !isAttachedAdjacentPair(fromClip, toClip)) {
    clearClipTransition(fromClip)
    toast.info('Transitions only apply to attached adjacent clips on the same video layer')
    markLocalSaving()
    return
  }
  updateClip(fromClip.id, {
    effects: {
      ...fromClip.effects,
      transition: transitionName,
      transitionDuration: durationValue,
      transitionWith: toClip.id,
    },
  })
  markLocalSaving()
}

function togglePlay() {
  isPlaying.value = !isPlaying.value
}

function seekBy(seconds: number) {
  const next = Math.min(Math.max(0, playheadTime.value + seconds), timelineDuration.value)
  setPlayhead(next)
}

function seekToStart() {
  setPlayhead(0)
}

function seekToEnd() {
  setPlayhead(timelineDuration.value)
}

function formatTime(seconds: number) {
  if (!Number.isFinite(seconds)) return '0:00.00'
  const min = Math.floor(seconds / 60)
  const sec = Math.floor(seconds % 60)
  const hundredths = Math.floor((seconds % 1) * 100)
  return `${min}:${sec.toString().padStart(2, '0')}.${hundredths.toString().padStart(2, '0')}`
}

function togglePreviewFullscreen() {
  previewRef.value?.toggleFullscreen?.()
}

async function executeEditorOp(op: string, params: Record<string, unknown>, successMessage?: string, targetClipId?: string) {
  if (operationRunning.value) {
    toast.info('Please wait for the current render to finish')
    return
  }
  const clip = targetClipId
    ? tracks.value.flatMap((track) => track.clips).find((entry) => entry.id === targetClipId)
    : selectedClip.value
  if (!clip || clip.type !== 'video' || !clip.sourceId) {
    toast.info('Select a video clip to render')
    return
  }

  operationRunning.value = true
  saveState.value = 'saving'
  isPlaying.value = false

  try {
    const shouldSaveToLibrary = op === 'export_video'
    const response = await api.editorOps.execute(String(clip.sourceId), op, params, {
      saveToLibrary: shouldSaveToLibrary,
      outputTitle: shouldSaveToLibrary ? `${projectName.value} - ${op}` : undefined,
    }) as EditorOpResponse
    if (response?.error) throw new Error(response.error)

    if (response?.output_url) {
      updateClip(clip.id, { sourceUrl: response.output_url }, { recordHistory: false })
      if (clip.id === selectedClipId.value) {
        previewUrl.value = response.output_url
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

function applyTransition(payload: { name?: string; duration?: number; commit?: boolean }) {
  if (!selectedClip.value) return
  const nextClip = findAdjacentNextClip(selectedClip.value)
  if (!payload.name || payload.name === 'None' || (payload.duration ?? 0) <= 0) {
    clearClipTransition(selectedClip.value)
    markLocalSaving()
    return
  }
  if (!nextClip) {
    if (payload.commit) {
      toast.info('Attach another clip to add a transition')
    }
    return
  }
  updateClip(selectedClip.value.id, {
    effects: {
      ...selectedClip.value.effects,
      transition: payload.name,
      transitionDuration: payload.duration ?? 0,
      transitionWith: nextClip.id,
    },
  }, { recordHistory: payload.commit === true })
  markLocalSaving()
}

function applyAudio(payload: { volume: number; fadeIn: number; fadeOut: number; commit?: boolean }) {
  if (!selectedClip.value) return
  updateClip(selectedClip.value.id, {
    effects: {
      ...selectedClip.value.effects,
      volume: payload.volume,
      audioFadeIn: payload.fadeIn,
      audioFadeOut: payload.fadeOut,
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

function applyLayer(payload: { opacity: number; blendMode: string; commit?: boolean }) {
  if (!selectedClip.value) return
  updateClip(selectedClip.value.id, {
    effects: {
      ...selectedClip.value.effects,
      opacity: payload.opacity,
      blendMode: payload.blendMode,
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

async function exportVideo() {
  if (operationRunning.value) {
    toast.info('Please wait for the current render to finish')
    return
  }
  operationRunning.value = true
  saveState.value = 'saving'

  try {
    const response = await api.projects.export(projectId.value, {
      output_title: `${projectName.value} - export`,
      output_settings: {
        width: outputSettings.value.width,
        height: outputSettings.value.height,
        fps: outputSettings.value.fps,
        bitrate: outputSettings.value.bitrate,
      },
    })
    if (response?.output_url) {
      window.open(response.output_url, '_blank', 'noopener')
    }
    saveState.value = 'saved'
    toast.success('Export completed')
  } catch (error: any) {
    saveState.value = 'error'
    toast.error(error?.data?.detail ?? error?.message ?? 'Export failed')
  } finally {
    operationRunning.value = false
  }
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
  syncTimelineHeight()
  const onResize = () => syncTimelineHeight()
  window.addEventListener('resize', onResize)
  windowResizeCleanup = () => window.removeEventListener('resize', onResize)
})

onBeforeUnmount(() => {
  if (resizeCleanup) resizeCleanup()
  if (windowResizeCleanup) windowResizeCleanup()
  if (persistTimer) clearTimeout(persistTimer)
  clearMediaUrlRefreshTimer()
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

.editor-resizer {
  background: rgba(105, 117, 101, 0.15);
  transition: background 150ms ease;
}

.editor-resizer:hover {
  background: rgba(105, 117, 101, 0.35);
}

.editor-resizer-vertical {
  cursor: col-resize;
}

.editor-resizer-horizontal {
  cursor: row-resize;
  height: 6px;
}

.editor-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0.6rem 0.75rem;
  border-top: 1px solid var(--cream-border);
  background: rgba(7, 8, 7, 0.9);
}

.editor-btn {
  height: 1.95rem;
  min-width: 1.95rem;
  border-radius: 0.5rem;
  border: 1px solid #556152;
  background: #697565;
  color: #f5f5f5;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.1rem;
  padding: 0 0.35rem;
  font-size: 0.72rem;
  transition: color 150ms ease, border-color 150ms ease, background 150ms ease;
}

.editor-btn:hover {
  background: #7d9a7d;
  border-color: #697565;
}

.dark .editor-controls {
  border-top: 1px solid #2b2a25;
  background: rgba(7, 8, 7, 0.9);
}

.editor-btn-primary {
  background: #697565;
  color: #f5f5f5;
  border-color: #556152;
}

.editor-btn-primary:hover {
  background: #7d9a7d;
}

</style>
