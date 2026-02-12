<template>
  <section class="flex-1 min-h-0 h-full w-full flex flex-col bg-surface-900">
    <div class="flex-1 min-h-0 p-2 lg:p-3">
      <div
        ref="frameRef"
        class="relative h-full w-full rounded-xl border border-surface-800 bg-surface-950/70 overflow-hidden"
        @mousemove="onFrameMouseMove"
        @mouseleave="onFrameMouseLeave"
      >
        <div class="absolute inset-0 flex items-center justify-center">
          <div
            ref="stageRef"
            class="relative overflow-hidden rounded-md border border-surface-700 bg-black"
            :style="stageStyle"
          >
            <div class="absolute inset-0">
              <div v-if="renderClips.length === 0" class="absolute inset-0 flex items-center justify-center text-sm text-surface-400">
                <template v-if="fallbackMedia">
                  <video
                    v-if="fallbackMedia.type === 'video'"
                    :src="fallbackMedia.src"
                    :poster="fallbackPoster || ''"
                    class="h-full w-full rounded-md border border-surface-700 bg-black object-contain"
                    preload="auto"
                    playsinline
                  />
                  <img
                    v-else
                    :src="fallbackMedia.src"
                    alt="Preview"
                    class="h-full w-full rounded-md border border-surface-700 bg-black object-contain"
                  />
                </template>
                <span v-else>No preview available</span>
              </div>

              <template v-else>
                <div
                  v-for="clip in renderClips"
                  :key="clip.id"
                  class="absolute group overflow-hidden"
                  :data-clip-id="clip.id"
                  :style="clipBoxStyle(clip)"
                  :class="clip.id === selectedClipId ? 'ring-2 ring-primary-400/70' : ''"
                  @pointerdown.stop="onClipPointerDown($event, clip)"
                  @contextmenu.prevent="openContextMenu($event, clip)"
                >
                  <video
                    v-if="clip.type === 'video' && canRenderVideo(clip)"
                    :ref="setVideoRef(clip.id)"
                    :key="videoKey(clip)"
                    :src="resolveVideoSource(clip)"
                    :poster="clipPosterSource(clip)"
                    class="h-full w-full rounded-md border border-surface-700 bg-black block"
                    :style="mediaStyle(clip)"
                    preload="auto"
                    playsinline
                    @loadedmetadata="onVideoMetadata(clip)"
                    @loadeddata="onVideoData(clip)"
                    @canplay="onVideoCanPlay(clip)"
                    @error="onVideoError(clip)"
                  />
                  <template v-else-if="clip.type === 'video'">
                    <img
                      v-if="clipPosterSource(clip)"
                      :src="clipPosterSource(clip)"
                      :alt="clip.label"
                      class="h-full w-full rounded-md border border-surface-700 bg-black object-contain"
                      :style="mediaStyle(clip)"
                    />
                    <div
                      v-else
                      class="flex h-full w-full items-center justify-center rounded-md border border-surface-700 bg-surface-900 text-center text-sm text-surface-400"
                    >
                      Video unavailable
                    </div>
                  </template>
                  <img
                    v-else-if="clip.type === 'image'"
                    :src="clip.sourceUrl || ''"
                    :alt="clip.label"
                    class="h-full w-full rounded-md border border-surface-700 bg-black object-contain"
                    :style="mediaStyle(clip)"
                  />
                  <div
                    v-else-if="clip.type === 'shape'"
                    class="h-full w-full rounded-md"
                    :style="shapeStyle(clip)"
                  />
                  <div
                    v-else-if="clip.type === 'text'"
                    class="h-full w-full px-2 py-1 flex items-center justify-center text-sm font-normal text-white bg-black/35 rounded-md"
                  >
                    {{ clip.text || 'Text' }}
                  </div>

                  <div
                    v-if="clipOverlayStyle(clip)"
                    class="pointer-events-none absolute inset-0 rounded-md"
                    :style="clipOverlayStyle(clip)"
                  />

                  <button
                    v-if="clip.id === selectedClipId"
                    type="button"
                    class="absolute -bottom-2 -right-2 h-4 w-4 rounded-full border border-surface-50 bg-[var(--cream-ui)]"
                    aria-label="Resize clip"
                    @pointerdown.stop="onClipPointerDown($event, clip, 'resize')"
                  />
                  <div
                    v-if="showCropOverlay(clip)"
                    class="absolute inset-0 z-40"
                    @pointerdown.stop="onCropPointerDown($event, clip, 'move')"
                  >
                    <div class="crop-window absolute" :style="cropWindowStyle(clip)">
                      <span class="crop-handle crop-handle-tl" @pointerdown.stop="onCropPointerDown($event, clip, 'tl')" />
                      <span class="crop-handle crop-handle-tr" @pointerdown.stop="onCropPointerDown($event, clip, 'tr')" />
                      <span class="crop-handle crop-handle-bl" @pointerdown.stop="onCropPointerDown($event, clip, 'bl')" />
                      <span class="crop-handle crop-handle-br" @pointerdown.stop="onCropPointerDown($event, clip, 'br')" />
                    </div>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>

        <div
          v-if="isFullscreen"
          class="absolute inset-x-0 bottom-0 pointer-events-none transition-opacity duration-200"
          :class="showFullscreenControls ? 'opacity-100' : 'opacity-0'"
        >
          <div class="pointer-events-auto mx-auto mb-3 w-[min(92%,720px)] rounded-xl border border-surface-800 bg-surface-950/90 px-3 py-2 shadow-lg">
            <div class="flex flex-wrap items-center justify-center gap-2">
              <button type="button" class="control-btn" @click="seekToStart" aria-label="Skip to start">
                <UiIcon name="ChevronsLeft" :size="16" />
              </button>
              <button type="button" class="control-btn" @click="seekBy(-5)" aria-label="Seek backward 5 seconds">
                <UiIcon name="ChevronLeft" :size="16" />
                <span class="text-[10px] leading-none">5</span>
              </button>
              <button type="button" class="h-9 w-9 rounded-full cream-btn transition-colors" @click="togglePlay" aria-label="Play or pause">
                <UiIcon :name="playing ? 'Pause' : 'Play'" :size="16" class="mx-auto" />
              </button>
              <button type="button" class="control-btn" @click="seekBy(5)" aria-label="Seek forward 5 seconds">
                <span class="text-[10px] leading-none">5</span>
                <UiIcon name="ChevronRight" :size="16" />
              </button>
              <button type="button" class="control-btn" @click="seekToEnd" aria-label="Skip to end">
                <UiIcon name="ChevronsRight" :size="16" />
              </button>
              <span class="mx-2 text-xs font-normal text-surface-100 tabular-nums">
                {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
              </span>
              <button type="button" class="control-btn" @click="$emit('split')" aria-label="Split clip">
                <UiIcon name="Scissors" :size="14" />
              </button>
              <button type="button" class="control-btn" @click="$emit('duplicate')" aria-label="Duplicate clip">
                <UiIcon name="Copy" :size="14" />
              </button>
              <button type="button" class="control-btn" @click="$emit('delete')" aria-label="Delete clip">
                <UiIcon name="Trash2" :size="14" />
              </button>
              <div class="flex items-center gap-2">
                <UiIcon name="Volume2" :size="14" class="text-surface-400" />
                <input :value="volumeValue" type="range" min="0" max="1" step="0.01" class="w-20 accent-primary-500" @input="onVolumeInput" />
              </div>
              <button type="button" class="control-btn" @click="toggleFullscreen" aria-label="Exit fullscreen">
                <UiIcon name="Minimize" :size="14" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showControls" class="border-t border-surface-800 bg-surface-900 px-3 py-2">
      <div class="flex flex-wrap items-center justify-center gap-1.5 sm:gap-2">
        <button type="button" class="control-btn" @click="seekToStart" aria-label="Skip to start">
          <UiIcon name="ChevronsLeft" :size="16" />
        </button>
        <button type="button" class="control-btn" @click="seekBy(-5)" aria-label="Seek backward 5 seconds">
          <UiIcon name="ChevronLeft" :size="16" />
          <span class="text-[10px] leading-none">5</span>
        </button>
        <button type="button" class="h-10 w-10 rounded-full cream-btn transition-colors" @click="togglePlay" aria-label="Play or pause">
          <UiIcon :name="playing ? 'Pause' : 'Play'" :size="18" class="mx-auto" />
        </button>
        <button type="button" class="control-btn" @click="seekBy(5)" aria-label="Seek forward 5 seconds">
          <span class="text-[10px] leading-none">5</span>
          <UiIcon name="ChevronRight" :size="16" />
        </button>
        <button type="button" class="control-btn" @click="seekToEnd" aria-label="Skip to end">
          <UiIcon name="ChevronsRight" :size="16" />
        </button>
        <span class="mx-2 text-sm font-normal text-surface-100 tabular-nums">
          {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
        </span>
        <div class="hidden lg:flex items-center gap-2">
          <button type="button" class="control-btn" @click="$emit('split')" aria-label="Split clip">
            <UiIcon name="Scissors" :size="14" />
          </button>
          <button type="button" class="control-btn" @click="$emit('duplicate')" aria-label="Duplicate clip">
            <UiIcon name="Copy" :size="14" />
          </button>
          <button type="button" class="control-btn" @click="$emit('delete')" aria-label="Delete clip">
            <UiIcon name="Trash2" :size="14" />
          </button>
        </div>
        <div class="hidden md:flex items-center gap-2 ml-2">
          <UiIcon name="Volume2" :size="14" class="text-surface-400" />
          <input :value="volumeValue" type="range" min="0" max="1" step="0.01" class="w-24 accent-primary-500" @input="onVolumeInput" />
          <button type="button" class="control-btn" @click="toggleFullscreen" aria-label="Fullscreen">
            <UiIcon name="Maximize" :size="14" />
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="contextMenu.open"
      ref="contextMenuRef"
      class="fixed z-[70] w-44 rounded-lg border border-surface-800 bg-surface-950/95 p-2 shadow-xl"
      :style="{ left: `${contextMenu.x}px`, top: `${contextMenu.y}px` }"
      @click.stop
    >
      <button type="button" class="menu-item" @click="handleContextAction('split')">Split</button>
      <button type="button" class="menu-item" @click="handleContextAction('duplicate')">Duplicate</button>
      <button type="button" class="menu-item" @click="handleContextAction('delete')">Delete</button>
      <div class="my-1 h-px bg-surface-800" />
      <button type="button" class="menu-item" @click="handleContextAction('effects')">Effects</button>
      <button type="button" class="menu-item" @click="handleContextAction('filters')">Filters</button>
      <button type="button" class="menu-item" @click="handleContextAction('adjust')">Adjust</button>
      <button type="button" class="menu-item" @click="handleContextAction('fade')">Fade</button>
      <button type="button" class="menu-item" @click="handleContextAction('speed')">Speed</button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, toRefs, watch, type CSSProperties, type ComponentPublicInstance } from 'vue'
import type { EditorClip } from '~/composables/useEditorState'

interface Props {
  clips: EditorClip[]
  selectedClipId?: string | null
  currentTime: number
  duration: number
  playing: boolean
  volume?: number
  showControls?: boolean
  fallbackUrl?: string
  fallbackPoster?: string
  cropMode?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  selectedClipId: null,
  volume: 1,
  showControls: true,
  fallbackUrl: '',
  fallbackPoster: '',
  cropMode: false,
})

const {
  clips,
  selectedClipId,
  currentTime,
  duration,
  playing,
} = toRefs(props)

const emit = defineEmits<{
  'update:currentTime': [value: number]
  'update:playing': [value: boolean]
  'update:volume': [value: number]
  'update:clip': [clipId: string, patch: Partial<EditorClip>]
  'update:clip-meta': [{ clipId: string; duration?: number }]
  'select-clip': [clipId: string]
  'open-panel': [tab: string]
  split: []
  duplicate: []
  delete: []
  'set-crop-mode': [enabled: boolean]
}>()

const frameRef = ref<HTMLDivElement | null>(null)
const stageRef = ref<HTMLDivElement | null>(null)
const videoRefs = ref(new Map<string, HTMLVideoElement>())
const videoErrorCount = ref<Record<string, number>>({})
const sourceDurations = ref<Record<string, number>>({})
const contextMenu = ref<{ open: boolean; x: number; y: number; clipId?: string }>({ open: false, x: 0, y: 0 })
const contextMenuRef = ref<HTMLDivElement | null>(null)
const isFullscreen = ref(false)
const showFullscreenControls = ref(false)
let fullscreenHideTimer: ReturnType<typeof setTimeout> | null = null
const volumeValue = computed(() => props.volume ?? 1)
const fallbackPoster = computed(() => props.fallbackPoster || '')
const MAX_PREVIEW_RECOVERY_ATTEMPTS = 2
const DEFAULT_STAGE_RATIO = 16 / 9
const TIMELINE_WRITE_THRESHOLD = 0.01
const PLAYING_DRIFT_SEEK_THRESHOLD = 0.35
const frameSize = ref({ width: 0, height: 0 })
let frameResizeObserver: ResizeObserver | null = null
let windowResizeCleanup: (() => void) | null = null

const imageExtensions = [
  '.jpg',
  '.jpeg',
  '.png',
  '.gif',
  '.webp',
  '.bmp',
  '.svg',
  '.tiff',
  '.tif',
  '.heic',
  '.heif',
]

function isLikelyImage(url?: string) {
  if (!url) return false
  const clean = url.split('?')[0].toLowerCase()
  return imageExtensions.some((ext) => clean.endsWith(ext))
}

function clampValue(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value))
}

function sourceKeyForClip(clip: EditorClip) {
  const sourceId = String(clip.sourceId ?? '').trim()
  if (sourceId) return `id:${sourceId}`
  const sourceUrl = String(clip.sourceUrl ?? '').trim()
  if (sourceUrl) return `url:${sourceUrl}`
  return ''
}

function getKnownSourceDuration(clip: EditorClip) {
  const key = sourceKeyForClip(clip)
  if (!key) return null
  const value = Number(sourceDurations.value[key] ?? 0)
  if (!Number.isFinite(value) || value <= 0) return null
  return value
}

const visualClips = computed(() =>
  clips.value
    .filter((clip) => clip.type !== 'audio')
    .slice()
    .sort((a, b) => a.startTime - b.startTime)
)

const videoClips = computed(() => visualClips.value.filter((clip) => clip.type === 'video'))

const ATTACH_THRESHOLD_SECONDS = 0.05
const ALLOWED_TRANSITIONS = new Set([
  'Cross fade',
  'Hard wipe',
])
const OPACITY_TRANSITIONS = new Set(['Cross fade'])

interface TransitionPair {
  fromId: string
  toId: string
  cutTime: number
  t0: number
  t1: number
  duration: number
  name: string
  fromClip: EditorClip
  toClip: EditorClip
  mode: 'centered' | 'post_cut'
  outgoingSampleStart: number
}

function isClipActive(clip: EditorClip, time: number) {
  return time >= clip.startTime && time <= clip.startTime + clip.duration
}

function resolveTransitionWindow(clip: EditorClip, next: EditorClip, requestedDuration: number) {
  const desired = Math.min(Math.max(0, requestedDuration), clip.duration, next.duration, 2)
  if (desired <= 0.01) return null

  const cutTime = next.startTime
  const outSpeed = Math.max(0.01, clip.effects?.speed ?? 1)
  const inSpeed = Math.max(0.01, next.effects?.speed ?? 1)
  const outTrim = getTrimRange(clip)
  const inTrim = getTrimRange(next)
  const outSourceDuration = getKnownSourceDuration(clip)

  // Handle available after clip out-point and before next clip in-point.
  const outHandleSource = outSourceDuration ? Math.max(0, outSourceDuration - outTrim.trimEnd) : 0
  const inHandleSource = Math.max(0, inTrim.trimStart)
  const outHandleTimeline = outHandleSource / outSpeed
  const inHandleTimeline = inHandleSource / inSpeed

  const maxPre = Math.min(desired, clip.duration, inHandleTimeline)
  const maxPost = Math.min(desired, next.duration, outHandleTimeline)
  const centeredHalf = desired / 2

  let pre = Math.min(centeredHalf, maxPre)
  let post = Math.min(desired - pre, maxPost)

  if (pre + post < desired) {
    const preRoom = Math.max(0, maxPre - pre)
    const addPre = Math.min(desired - (pre + post), preRoom)
    pre += addPre
    post = Math.min(desired - pre, maxPost)
  }

  const centeredDuration = pre + post
  if (centeredDuration > 0.01) {
    return {
      cutTime,
      t0: cutTime - pre,
      t1: cutTime + post,
      duration: centeredDuration,
      mode: 'centered' as const,
      outgoingSampleStart: cutTime - pre,
    }
  }

  // Fallback that never freezes: post-cut window with outgoing remap.
  const fallbackDuration = Math.min(desired, clip.duration, next.duration)
  if (fallbackDuration <= 0.01) return null
  return {
    cutTime,
    t0: cutTime,
    t1: cutTime + fallbackDuration,
    duration: fallbackDuration,
    mode: 'post_cut' as const,
    outgoingSampleStart: clip.startTime + Math.max(0, clip.duration - fallbackDuration),
  }
}

const transitionPairs = computed<TransitionPair[]>(() => {
  const pairs: TransitionPair[] = []
  const layerMap = new Map<number, EditorClip[]>()
  for (const clip of videoClips.value) {
    const layer = clip.layer ?? 1
    if (!layerMap.has(layer)) layerMap.set(layer, [])
    layerMap.get(layer)!.push(clip)
  }
  layerMap.forEach((layerClips) => {
    const sorted = layerClips.slice().sort((a, b) => a.startTime - b.startTime)
    for (let i = 0; i < sorted.length - 1; i += 1) {
      const clip = sorted[i]
      const next = sorted[i + 1]
      const name = clip.effects?.transition
      const duration = Number(clip.effects?.transitionDuration ?? 0)
      if (!name || duration <= 0) continue
      if (!ALLOWED_TRANSITIONS.has(name)) continue
      if (clip.effects?.transitionWith !== next.id) continue
      const gap = next.startTime - (clip.startTime + clip.duration)
      if (Math.abs(gap) > ATTACH_THRESHOLD_SECONDS) continue
      const window = resolveTransitionWindow(clip, next, duration)
      if (!window) continue
      pairs.push({
        fromId: clip.id,
        toId: next.id,
        cutTime: window.cutTime,
        t0: window.t0,
        t1: window.t1,
        duration: window.duration,
        name,
        fromClip: clip,
        toClip: next,
        mode: window.mode,
        outgoingSampleStart: window.outgoingSampleStart,
      })
    }
  })
  return pairs
})

const transitionOutMap = computed(() => {
  const map = new Map<string, TransitionPair>()
  transitionPairs.value.forEach((pair) => map.set(pair.fromId, pair))
  return map
})

const transitionInMap = computed(() => {
  const map = new Map<string, TransitionPair>()
  transitionPairs.value.forEach((pair) => map.set(pair.toId, pair))
  return map
})

const activeTransition = computed<TransitionPair | null>(() => {
  if (!transitionPairs.value.length) return null
  const now = currentTime.value
  const matches = transitionPairs.value.filter((pair) => now >= pair.t0 && now <= pair.t1)
  if (!matches.length) return null
  const sorted = matches.slice().sort((a, b) => clipZIndex(a.toClip) - clipZIndex(b.toClip))
  return sorted[sorted.length - 1] ?? null
})

const activeVideoClip = computed<EditorClip | null>(() => {
  const now = currentTime.value
  const active = videoClips.value
    .filter((clip) => isClipActive(clip, now))
    .sort((a, b) => clipZIndex(a) - clipZIndex(b))
  return active.length ? active[active.length - 1] : null
})

const fallbackVideoClip = computed<EditorClip | null>(() => {
  if (activeVideoClip.value) return null
  if (!videoClips.value.length) return null
  const now = currentTime.value
  const past = videoClips.value.filter((clip) => now > clip.startTime + clip.duration)
  if (past.length) return past[past.length - 1]
  const upcoming = videoClips.value.find((clip) => clip.startTime >= now)
  return upcoming ?? videoClips.value[0]
})

const primaryVideoClip = computed<EditorClip | null>(() => {
  if (activeTransition.value) return activeTransition.value.toClip
  return activeVideoClip.value ?? fallbackVideoClip.value
})

const secondaryVideoClip = computed<EditorClip | null>(() => {
  if (!activeTransition.value) return null
  return activeTransition.value.fromClip
})

const clockVideoClip = computed<EditorClip | null>(() => {
  if (!activeTransition.value) return activeVideoClip.value
  return currentTime.value < activeTransition.value.cutTime
    ? activeTransition.value.fromClip
    : activeTransition.value.toClip
})

const playbackVideoClipIds = computed(() => {
  if (!playing.value) return []
  if (activeTransition.value) return [activeTransition.value.fromId, activeTransition.value.toId]
  if (activeVideoClip.value) return [activeVideoClip.value.id]
  return []
})

const activeVideoClips = computed(() => {
  const clips: EditorClip[] = []
  if (primaryVideoClip.value) clips.push(primaryVideoClip.value)
  if (secondaryVideoClip.value && secondaryVideoClip.value.id !== primaryVideoClip.value?.id) {
    clips.push(secondaryVideoClip.value)
  }
  return clips
})

const activeOverlayClips = computed(() =>
  visualClips.value
    .filter((clip) => clip.type !== 'video' && isClipActive(clip, currentTime.value))
    .sort((a, b) => ((a.layer ?? 1) - (b.layer ?? 1)) || (a.startTime - b.startTime))
)

const renderClips = computed(() => {
  const combined = [...activeVideoClips.value, ...activeOverlayClips.value]
  return combined.sort((a, b) => clipStackOrder(a) - clipStackOrder(b))
})

const aspectClip = computed<EditorClip | null>(() => {
  if (primaryVideoClip.value) return primaryVideoClip.value
  if (!videoClips.value.length) return null
  return videoClips.value[0] ?? null
})

const clipBackdropSet = computed(() => {
  const sorted = renderClips.value.slice().sort((a, b) => clipStackOrder(a) - clipStackOrder(b))
  const set = new Set<string>()
  let hasBackdrop = false
  for (const clip of sorted) {
    if (hasBackdrop) set.add(clip.id)
    const opacity = clipOpacity(clip)
    if (opacity > 0.01) hasBackdrop = true
  }
  return set
})

const fallbackMedia = computed(() => {
  if (visualClips.value.length > 0) return null
  if (props.fallbackUrl) {
    if (isLikelyImage(props.fallbackUrl)) return { type: 'image' as const, src: props.fallbackUrl }
    return { type: 'video' as const, src: props.fallbackUrl }
  }
  if (props.fallbackPoster) return { type: 'image' as const, src: props.fallbackPoster }
  return null
})

function parseAspectRatio(value?: string) {
  if (!value) return null
  const normalized = value.trim()
  if (!normalized) return null
  if (normalized.includes(':')) {
    const [leftRaw, rightRaw] = normalized.split(':', 2)
    const left = Number(leftRaw)
    const right = Number(rightRaw)
    if (!Number.isFinite(left) || !Number.isFinite(right) || right <= 0 || left <= 0) return null
    return left / right
  }
  const ratio = Number(normalized)
  if (!Number.isFinite(ratio) || ratio <= 0) return null
  return ratio
}

const stageAspectRatio = computed(() => {
  const fromActive = parseAspectRatio(aspectClip.value?.aspectRatio)
  if (fromActive) return fromActive
  const fromTimeline = parseAspectRatio(videoClips.value[0]?.aspectRatio)
  if (fromTimeline) return fromTimeline
  return DEFAULT_STAGE_RATIO
})

const stageStyle = computed<CSSProperties>(() => {
  const width = frameSize.value.width
  const height = frameSize.value.height
  if (!width || !height || width < 8 || height < 8) {
    return {
      width: '100%',
      height: '100%',
    }
  }

  const ratio = stageAspectRatio.value
  const frameRatio = width / height

  let stageWidth = width
  let stageHeight = height

  if (frameRatio > ratio) {
    stageHeight = height
    stageWidth = height * ratio
  } else {
    stageWidth = width
    stageHeight = width / ratio
  }

  return {
    width: `${Math.max(1, Math.floor(stageWidth))}px`,
    height: `${Math.max(1, Math.floor(stageHeight))}px`,
    isolation: 'isolate',
  }
})

function resolveVideoSource(clip: EditorClip) {
  return clip.sourceUrl || props.fallbackUrl || ''
}

function videoKey(clip: EditorClip) {
  const source = resolveVideoSource(clip)
  const retry = videoErrorCount.value[clip.id] ?? 0
  return `${clip.id}-${source}-${retry}`
}

function canRenderVideo(clip: EditorClip) {
  if (clip.type !== 'video') return false
  const source = resolveVideoSource(clip)
  if (!source) return false
  if (isLikelyImage(source)) return false
  return true
}

function resolveVideoRefElement(el: Element | ComponentPublicInstance | null) {
  if (!el) return null
  if (el instanceof HTMLVideoElement) return el
  if ('$el' in el) {
    const root = (el as { $el?: unknown }).$el
    if (root instanceof HTMLVideoElement) return root
    if (root instanceof Element) {
      const nestedVideo = root.querySelector('video')
      if (nestedVideo instanceof HTMLVideoElement) return nestedVideo
    }
  }
  return null
}

function setVideoRef(id: string) {
  return (el: Element | ComponentPublicInstance | null) => {
    const video = resolveVideoRefElement(el)
    if (!video) {
      videoRefs.value.delete(id)
      return
    }
    videoRefs.value.set(id, video)
    const clip = activeVideoMap.value.get(id)
    if (clip) syncVideoElement(clip, true)
  }
}

function clipPosterSource(clip: EditorClip) {
  if (clip.posterUrl) return clip.posterUrl
  const source = resolveVideoSource(clip)
  if (source && isLikelyImage(source)) return source
  if (fallbackPoster.value) return fallbackPoster.value
  return ''
}

function getTrimRange(clip: EditorClip) {
  const trimStart = clip.trimStart ?? 0
  const trimEnd = clip.trimEnd ?? (trimStart + clip.duration)
  return {
    trimStart,
    trimEnd: Math.max(trimStart + 0.01, trimEnd),
  }
}

function getClipMediaTime(clip: EditorClip, timelineTime: number) {
  const { trimStart, trimEnd } = getTrimRange(clip)
  const speed = Math.max(0.01, clip.effects?.speed ?? 1)
  const local = (timelineTime - clip.startTime) * speed + trimStart
  return Math.min(Math.max(trimStart, local), trimEnd)
}

function getClipMediaTimeWithTransitionHandles(clip: EditorClip, timelineTime: number) {
  const transitionOut = transitionOutMap.value.get(clip.id)
  const transitionIn = transitionInMap.value.get(clip.id)
  const outActive = transitionOut && timelineTime >= transitionOut.t0 && timelineTime <= transitionOut.t1 ? transitionOut : null
  const inActive = transitionIn && timelineTime >= transitionIn.t0 && timelineTime <= transitionIn.t1 ? transitionIn : null

  if (!outActive && !inActive) return getClipMediaTime(clip, timelineTime)

  const { trimStart, trimEnd } = getTrimRange(clip)
  const speed = Math.max(0.01, clip.effects?.speed ?? 1)
  let sampleTime = timelineTime
  let minMediaTime = trimStart
  let maxMediaTime = trimEnd

  if (outActive) {
    if (outActive.mode === 'post_cut') {
      sampleTime = outActive.outgoingSampleStart + (timelineTime - outActive.t0)
    } else {
      const sourceDuration = getKnownSourceDuration(clip)
      if (sourceDuration) maxMediaTime = Math.max(trimEnd, sourceDuration)
    }
  }

  if (inActive) {
    minMediaTime = 0
  }

  const mediaTime = (sampleTime - clip.startTime) * speed + trimStart
  return clampValue(mediaTime, minMediaTime, Math.max(minMediaTime + 0.01, maxMediaTime))
}

function mapMediaTimeToTimeline(clip: EditorClip, mediaTime: number) {
  const { trimStart } = getTrimRange(clip)
  const speed = Math.max(0.01, clip.effects?.speed ?? 1)
  const timelineTime = clip.startTime + ((mediaTime - trimStart) / speed)
  return Math.min(Math.max(0, timelineTime), clip.startTime + clip.duration)
}

const activeVideoMap = computed(() => {
  const map = new Map<string, EditorClip>()
  activeVideoClips.value.forEach((clip) => map.set(clip.id, clip))
  return map
})

const activeVideoIds = computed(() => activeVideoClips.value.map((clip) => clip.id).join('|'))

function getVideoElement(clipId: string) {
  return videoRefs.value.get(clipId) ?? null
}

function syncVideoElement(clip: EditorClip, force = false) {
  const video = getVideoElement(clip.id)
  if (!video) return
  const targetTime = getClipMediaTimeWithTransitionHandles(clip, currentTime.value)
  const drift = Number.isFinite(targetTime) ? Math.abs(video.currentTime - targetTime) : 0
  const isClockClip = Boolean(playing.value && clockVideoClip.value?.id === clip.id)
  const seekThreshold = force ? 0.01 : (isClockClip ? PLAYING_DRIFT_SEEK_THRESHOLD : 0.05)
  const shouldSeek = force || !playing.value || drift > PLAYING_DRIFT_SEEK_THRESHOLD
  if (Number.isFinite(targetTime) && shouldSeek && drift > seekThreshold) {
    try {
      video.currentTime = targetTime
    } catch {
      // Ignore seek errors while metadata is still loading.
    }
  }
  const rate = Math.max(0.01, clip.effects?.speed ?? 1)
  if (video.playbackRate !== rate) video.playbackRate = rate
  const isAudibleClip = Boolean(playing.value && clockVideoClip.value?.id === clip.id)
  const baseVolume = volumeValue.value
  const clipVolume = clip.effects?.volume ?? 1
  const nextVolume = isAudibleClip ? Math.max(0, Math.min(1, baseVolume * clipVolume)) : 0
  video.volume = nextVolume
  video.muted = nextVolume <= 0
}

async function syncActiveVideoPlayback() {
  const playbackSet = new Set(playbackVideoClipIds.value)
  let playbackFailed = false
  for (const [clipId, video] of videoRefs.value.entries()) {
    const clip = activeVideoMap.value.get(clipId)
    if (!clip) {
      if (!video.paused) video.pause()
      continue
    }
    syncVideoElement(clip)
    if (!playbackSet.has(clipId)) {
      if (!video.paused) video.pause()
      continue
    }
    try {
      await video.play()
    } catch {
      if (!video.muted) {
        video.muted = true
        try {
          await video.play()
        } catch {
          playbackFailed = true
        }
      } else {
        playbackFailed = true
      }
    }
  }
  if (playbackFailed) emit('update:playing', false)
}

function syncActiveVideoTimes(force = false) {
  activeVideoClips.value.forEach((clip) => syncVideoElement(clip, force))
}

type PlaybackClockMode = 'idle' | 'video-clock' | 'gap-clock'
let playbackClockFrame: number | null = null
let lastGapTime = 0

function stopPlaybackClock() {
  if (playbackClockFrame) {
    cancelAnimationFrame(playbackClockFrame)
    playbackClockFrame = null
  }
  lastGapTime = 0
}

function resolvePlaybackClockMode(): PlaybackClockMode {
  if (!playing.value) return 'idle'
  if (clockVideoClip.value) return 'video-clock'
  return 'gap-clock'
}

function finishPlaybackAtTimelineEnd() {
  emit('update:currentTime', duration.value)
  emit('update:playing', false)
  stopPlaybackClock()
}

function runPlaybackClock(now: number) {
  const mode = resolvePlaybackClockMode()
  if (mode === 'idle') {
    stopPlaybackClock()
    return
  }

  if (mode === 'video-clock') {
    lastGapTime = 0
    const clockClip = clockVideoClip.value
    const video = clockClip ? getVideoElement(clockClip.id) : null
    if (clockClip && video && Number.isFinite(video.currentTime)) {
      const nextTime = clampValue(
        mapMediaTimeToTimeline(clockClip, Number(video.currentTime)),
        0,
        duration.value
      )
      if (nextTime >= duration.value - 0.001) {
        finishPlaybackAtTimelineEnd()
        return
      }
      if (Math.abs(nextTime - currentTime.value) > TIMELINE_WRITE_THRESHOLD) {
        emit('update:currentTime', nextTime)
      }
    }
  } else {
    if (!lastGapTime) lastGapTime = now
    const delta = Math.max(0, (now - lastGapTime) / 1000)
    lastGapTime = now
    const next = clampValue(currentTime.value + delta, 0, duration.value)
    if (next >= duration.value - 0.001) {
      finishPlaybackAtTimelineEnd()
      return
    }
    if (Math.abs(next - currentTime.value) > TIMELINE_WRITE_THRESHOLD) {
      emit('update:currentTime', next)
    }
  }

  playbackClockFrame = requestAnimationFrame(runPlaybackClock)
}

function ensurePlaybackClock() {
  if (!playing.value) {
    stopPlaybackClock()
    return
  }
  if (playbackClockFrame) return
  playbackClockFrame = requestAnimationFrame(runPlaybackClock)
}

watch(
  activeVideoIds,
  () => {
    syncActiveVideoTimes(true)
    void syncActiveVideoPlayback()
    ensurePlaybackClock()
  },
  { immediate: true }
)

watch(currentTime, () => {
  if (!playing.value) syncActiveVideoTimes()
})

watch(playing, () => {
  syncActiveVideoTimes(true)
  void syncActiveVideoPlayback()
  ensurePlaybackClock()
})

watch(
  () => clockVideoClip.value?.id,
  () => {
    syncActiveVideoTimes(true)
    void syncActiveVideoPlayback()
    ensurePlaybackClock()
  }
)

watch(volumeValue, () => {
  syncActiveVideoTimes(true)
})

watch(
  () => props.cropMode,
  (enabled) => {
    if (!enabled) onCropPointerUp()
  }
)

function onVideoMetadata(clip: EditorClip) {
  const video = getVideoElement(clip.id)
  if (!video) return
  const measuredDuration = Number(video.duration || 0)
  if (Number.isFinite(measuredDuration) && measuredDuration > 0) {
    const key = sourceKeyForClip(clip)
    if (key) {
      sourceDurations.value = {
        ...sourceDurations.value,
        [key]: measuredDuration,
      }
    }
    emit('update:clip-meta', { clipId: clip.id, duration: measuredDuration })
  }
  syncVideoElement(clip, true)
}

function onVideoData(clip: EditorClip) {
  if (videoErrorCount.value[clip.id]) {
    videoErrorCount.value = { ...videoErrorCount.value, [clip.id]: 0 }
  }
  syncVideoElement(clip, true)
  if (playing.value) {
    void syncActiveVideoPlayback()
    ensurePlaybackClock()
  }
}

function onVideoCanPlay(clip: EditorClip) {
  syncVideoElement(clip, true)
  if (playing.value) {
    void syncActiveVideoPlayback()
    ensurePlaybackClock()
  }
}

function onVideoError(clip: EditorClip) {
  const attempts = videoErrorCount.value[clip.id] ?? 0
  if (attempts >= MAX_PREVIEW_RECOVERY_ATTEMPTS) {
    emit('update:playing', false)
    // eslint-disable-next-line no-console
    console.warn('Preview video failed after retry attempts', clip.sourceUrl)
    return
  }
  videoErrorCount.value = {
    ...videoErrorCount.value,
    [clip.id]: attempts + 1,
  }
  // eslint-disable-next-line no-console
  console.warn('Preview video failed to load, retrying', clip.sourceUrl)
}

function easeInOut(value: number) {
  const t = Math.max(0, Math.min(1, value))
  return t * t * (3 - 2 * t)
}

function transitionProgress(pair?: TransitionPair | null) {
  if (!pair || pair.duration <= 0) return null
  const length = pair.t1 - pair.t0
  if (length <= 0.0001) return null
  if (currentTime.value < pair.t0 || currentTime.value > pair.t1) return null
  const u = clampValue((currentTime.value - pair.t0) / length, 0, 1)
  return easeInOut(u)
}

function clampPercent(value: number) {
  return Math.max(0, Math.min(100, value))
}

function buildHardWipe(direction: 'left' | 'right' | 'up' | 'down', progress: number) {
  const pct = clampPercent(progress * 100)
  if (direction === 'right') return { clipPath: `inset(0 ${100 - pct}% 0 0)` }
  if (direction === 'left') return { clipPath: `inset(0 0 0 ${100 - pct}%)` }
  if (direction === 'down') return { clipPath: `inset(0 0 ${100 - pct}% 0)` }
  return { clipPath: `inset(${100 - pct}% 0 0 0)` }
}

function transitionStyleForClip(clip: EditorClip): CSSProperties | null {
  const inTransition = transitionInMap.value.get(clip.id)
  const inProgress = transitionProgress(inTransition)
  const inName = inTransition?.name

  if (inTransition && inProgress !== null && inName) {
    switch (inName) {
      case 'Hard wipe':
        return buildHardWipe('right', inProgress)
      default:
        return null
    }
  }

  return null
}

function clipOpacity(clip: EditorClip) {
  if (clip.type === 'video') {
    const isPrimary = primaryVideoClip.value?.id === clip.id
    const isSecondary = secondaryVideoClip.value?.id === clip.id
    if (!isPrimary && !isSecondary) return 0
  } else if (!isClipActive(clip, currentTime.value)) {
    return 0
  }

  const outTransition = transitionOutMap.value.get(clip.id)
  const inTransition = transitionInMap.value.get(clip.id)
  const outProgress = transitionProgress(outTransition)
  const inProgress = transitionProgress(inTransition)
  const inTransitionWindow = outProgress !== null || inProgress !== null
  const transitionName = outTransition?.name || inTransition?.name
  const usesOpacity = transitionName ? OPACITY_TRANSITIONS.has(transitionName) : false

  const localTime = clampValue(currentTime.value - clip.startTime, 0, clip.duration)
  let opacity = 1
  if (!inTransitionWindow) {
    const fadeIn = Number(clip.effects?.fadeIn ?? 0)
    const fadeOut = Number(clip.effects?.fadeOut ?? 0)
    const remaining = clip.duration - localTime
    if (fadeIn > 0) opacity = Math.min(opacity, Math.max(0, localTime / fadeIn))
    if (fadeOut > 0) opacity = Math.min(opacity, Math.max(0, remaining / fadeOut))
  }
  const base = Number(clip.effects?.opacity ?? clip.style?.opacity ?? 1)
  const safeBase = Number.isFinite(base) ? base : 1
  let combined = opacity * safeBase
  if (usesOpacity) {
    if (outProgress !== null) combined *= 1 - outProgress
    if (inProgress !== null) combined *= inProgress
  }
  if (!Number.isFinite(combined)) return 1
  return Math.max(0, Math.min(1, combined))
}

function clipFilter(clip: EditorClip) {
  const brightness = clip.effects?.brightness ?? 0
  const contrast = clip.effects?.contrast ?? 1
  const saturation = clip.effects?.saturation ?? 1
  const gamma = clip.effects?.gamma ?? 1
  const hue = clip.effects?.hue ?? 0
  const blur = clip.effects?.blur ?? 0
  const isIdentity = (
    Math.abs(brightness) < 0.0001
    && Math.abs(contrast - 1) < 0.0001
    && Math.abs(saturation - 1) < 0.0001
    && Math.abs(gamma - 1) < 0.0001
    && Math.abs(hue) < 0.0001
    && Math.abs(blur) < 0.0001
  )
  if (isIdentity) return undefined
  const brightnessValue = Math.max(0, (1 + brightness) * gamma)
  return `brightness(${brightnessValue}) contrast(${contrast}) saturate(${saturation}) hue-rotate(${hue}deg) blur(${blur}px)`
}

function clipOverlayStyle(clip: EditorClip): CSSProperties | null {
  const color = clip.effects?.overlayColor
  const opacity = clip.effects?.overlayOpacity ?? 0
  if (!color || color === 'transparent' || opacity <= 0) return null
  return {
    background: color,
    opacity,
    mixBlendMode: (clip.effects?.overlayBlend ?? 'soft-light') as CSSProperties['mixBlendMode'],
  }
}

function clipZIndex(clip: EditorClip) {
  const group = clip.layerGroup ?? (clip.type === 'video' ? 'video' : clip.type === 'audio' ? 'audio' : 'graphics')
  const groupOffset = group === 'graphics' ? 100 : 0
  return groupOffset + (clip.layer ?? 1)
}

function clipStackOrder(clip: EditorClip) {
  let z = clipZIndex(clip)
  if (primaryVideoClip.value && secondaryVideoClip.value) {
    if (clip.id === primaryVideoClip.value.id && secondaryVideoClip.value.id !== clip.id) {
      z += 0.2
    }
  }
  return z
}

function clipBoxStyle(clip: EditorClip): CSSProperties {
  const position = clip.position ?? { x: 0, y: 0 }
  const size = clip.size ?? { width: 100, height: 100 }
  const x = Number(position.x)
  const y = Number(position.y)
  const width = Number(size.width)
  const height = Number(size.height)
  const rotation = Number(clip.rotation ?? 0)
  const rawBlend = clip.effects?.blendMode
  const cssBlendMap: Record<string, string> = {
    softlight: 'soft-light',
    hardlight: 'hard-light',
  }
  const blendMode = rawBlend && rawBlend !== 'normal' ? (cssBlendMap[rawBlend] || rawBlend) : undefined
  const filter = clipFilter(clip)
  const transitionStyle = transitionStyleForClip(clip)
  const safeX = Number.isFinite(x) ? x : 0
  const safeY = Number.isFinite(y) ? y : 0
  const safeWidth = Number.isFinite(width) && width > 0 ? width : 100
  const safeHeight = Number.isFinite(height) && height > 0 ? height : 100
  const isNormalized =
    safeWidth <= 1.2 &&
    safeHeight <= 1.2 &&
    safeX >= 0 &&
    safeY >= 0 &&
    safeX <= 1.2 &&
    safeY <= 1.2
  const normalizedX = isNormalized ? safeX * 100 : safeX
  const normalizedY = isNormalized ? safeY * 100 : safeY
  const normalizedWidth = isNormalized ? safeWidth * 100 : safeWidth
  const normalizedHeight = isNormalized ? safeHeight * 100 : safeHeight
  const safeRotation = Number.isFinite(rotation) ? rotation : 0
  const safeOpacity = clipOpacity(clip)
  const style: CSSProperties = {
    left: `${normalizedX}%`,
    top: `${normalizedY}%`,
    width: `${normalizedWidth}%`,
    height: `${normalizedHeight}%`,
    opacity: safeOpacity,
    zIndex: clipStackOrder(clip),
  }
  if (Math.abs(safeRotation) > 0.01) {
    style.transform = `rotate(${safeRotation}deg)`
    style.transformOrigin = 'center center'
    style.willChange = 'transform'
  }
  const transitionFilter = transitionStyle?.filter ? String(transitionStyle.filter) : ''
  if (filter || transitionFilter) {
    const parts = [filter, transitionFilter].filter(Boolean)
    style.filter = parts.join(' ')
  }
  if (transitionStyle) {
    if (transitionStyle.clipPath) style.clipPath = transitionStyle.clipPath
    if (transitionStyle.WebkitMaskImage) style.WebkitMaskImage = transitionStyle.WebkitMaskImage
    if (transitionStyle.maskImage) style.maskImage = transitionStyle.maskImage
    if (transitionStyle.WebkitMaskSize) style.WebkitMaskSize = transitionStyle.WebkitMaskSize
    if (transitionStyle.maskSize) style.maskSize = transitionStyle.maskSize
    if (transitionStyle.WebkitMaskRepeat) style.WebkitMaskRepeat = transitionStyle.WebkitMaskRepeat
    if (transitionStyle.maskRepeat) style.maskRepeat = transitionStyle.maskRepeat
  }
  if (blendMode && clipBackdropSet.value.has(clip.id)) {
    style.mixBlendMode = blendMode as CSSProperties['mixBlendMode']
  }
  return style
}

function mediaStyle(clip: EditorClip): CSSProperties {
  const fitMode = clip.fitMode ?? 'fit'
  const objectFit = fitMode === 'fill' ? 'cover' : fitMode === 'stretch' ? 'fill' : 'contain'
  const style: CSSProperties = {
    objectFit: objectFit as CSSProperties['objectFit'],
  }
  if (clip.type !== 'video') return style
  const crop = clip.crop ?? { x: 0, y: 0, width: 1, height: 1 }
  const x = clampValue(Number(crop.x ?? 0), 0, 1)
  const y = clampValue(Number(crop.y ?? 0), 0, 1)
  const width = clampValue(Number(crop.width ?? 1), 0.05, 1)
  const height = clampValue(Number(crop.height ?? 1), 0.05, 1)
  const hasCrop = Math.abs(x) > 0.0001 || Math.abs(y) > 0.0001 || Math.abs(width - 1) > 0.0001 || Math.abs(height - 1) > 0.0001
  if (!hasCrop) return style
  style.objectFit = 'fill'
  style.transformOrigin = 'top left'
  style.transform = `translate(${-((x / width) * 100)}%, ${-((y / height) * 100)}%) scale(${1 / width}, ${1 / height})`
  style.willChange = 'transform'
  return style
}

function shapeStyle(clip: EditorClip): CSSProperties {
  const fillColor = clip.style?.color ?? '#8f8cae80'
  const useOutline = Boolean(clip.style?.outline)
  const shapeType = (clip.style?.shapeType ?? 'square').toLowerCase()
  if (shapeType === 'outline') {
    return {
      background: 'transparent',
      border: `2px solid ${fillColor}`,
      borderRadius: '0.35rem',
    }
  }
  if (shapeType === 'circle') {
    return {
      background: fillColor,
      border: useOutline ? '2px solid rgba(255,255,255,.7)' : 'none',
      borderRadius: '9999px',
    }
  }
  if (shapeType === 'arrow') {
    return {
      background: fillColor,
      border: useOutline ? '1px solid rgba(255,255,255,.7)' : 'none',
      clipPath: 'polygon(0 22%,66% 22%,66% 0,100% 50%,66% 100%,66% 78%,0 78%)',
    }
  }
  return {
    background: fillColor,
    border: useOutline ? '2px solid rgba(255,255,255,.7)' : 'none',
    borderRadius: '0.35rem',
  }
}

function togglePlay() {
  const next = !playing.value
  emit('update:playing', next)
}

function seekBy(seconds: number) {
  const nextTime = Math.min(Math.max(0, currentTime.value + seconds), duration.value || 0)
  emit('update:currentTime', nextTime)
}

function seekToStart() {
  emit('update:currentTime', 0)
}

function seekToEnd() {
  emit('update:currentTime', duration.value || 0)
}

async function toggleFullscreen() {
  const target = frameRef.value
  if (!target) return
  if (document.fullscreenElement) {
    await document.exitFullscreen()
    return
  }
  await target.requestFullscreen()
}

function clampFixedMenuPosition(x: number, y: number, menu: HTMLElement | null) {
  if (!menu) return { x, y }
  const padding = 12
  const rect = menu.getBoundingClientRect()
  const maxX = Math.max(padding, window.innerWidth - rect.width - padding)
  const maxY = Math.max(padding, window.innerHeight - rect.height - padding)
  return {
    x: clampValue(x, padding, maxX),
    y: clampValue(y, padding, maxY),
  }
}

function closeContextMenu() {
  contextMenu.value = { open: false, x: 0, y: 0 }
}

function openContextMenu(event: MouseEvent, clip: EditorClip) {
  closeContextMenu()
  emit('select-clip', clip.id)
  contextMenu.value = {
    open: true,
    x: event.clientX,
    y: event.clientY,
    clipId: clip.id,
  }
  nextTick(() => {
    const pos = clampFixedMenuPosition(contextMenu.value.x, contextMenu.value.y, contextMenuRef.value)
    contextMenu.value = { ...contextMenu.value, x: pos.x, y: pos.y }
  })
}

function handleContextAction(action: 'split' | 'duplicate' | 'delete' | 'effects' | 'filters' | 'adjust' | 'fade' | 'speed') {
  if (contextMenu.value.clipId) emit('select-clip', contextMenu.value.clipId)
  if (action === 'split') emit('split')
  if (action === 'duplicate') emit('duplicate')
  if (action === 'delete') emit('delete')
  if (action === 'effects') emit('open-panel', 'effects')
  if (action === 'filters') emit('open-panel', 'filters')
  if (action === 'adjust') emit('open-panel', 'adjust')
  if (action === 'fade') emit('open-panel', 'fade')
  if (action === 'speed') emit('open-panel', 'speed')
  closeContextMenu()
}

function revealFullscreenControls() {
  showFullscreenControls.value = true
  if (fullscreenHideTimer) clearTimeout(fullscreenHideTimer)
  fullscreenHideTimer = setTimeout(() => {
    showFullscreenControls.value = false
  }, 2200)
}

function onFrameMouseMove(event: MouseEvent) {
  if (!isFullscreen.value || !frameRef.value) return
  const rect = frameRef.value.getBoundingClientRect()
  if (event.clientY >= rect.bottom - 90) {
    revealFullscreenControls()
  }
}

function onFrameMouseLeave() {
  if (!isFullscreen.value) return
  showFullscreenControls.value = false
  if (fullscreenHideTimer) {
    clearTimeout(fullscreenHideTimer)
    fullscreenHideTimer = null
  }
}

function handleFullscreenChange() {
  isFullscreen.value = Boolean(document.fullscreenElement)
  if (isFullscreen.value) {
    revealFullscreenControls()
    return
  }
  showFullscreenControls.value = false
  if (fullscreenHideTimer) {
    clearTimeout(fullscreenHideTimer)
    fullscreenHideTimer = null
  }
}

const onGlobalPointerDown = (event: PointerEvent) => {
  if (!contextMenu.value.open || !contextMenuRef.value) return
  if (!contextMenuRef.value.contains(event.target as Node)) closeContextMenu()
}

const onGlobalKeyDown = (event: KeyboardEvent) => {
  if (event.key !== 'Escape') return
  closeContextMenu()
  if (props.cropMode) emit('set-crop-mode', false)
}

function onVolumeInput(event: Event) {
  const target = event.target as HTMLInputElement | null
  const next = Number(target?.value ?? 1)
  emit('update:volume', Number.isFinite(next) ? next : 1)
}

type DragMode = 'move' | 'resize'
type CropHandle = 'move' | 'tl' | 'tr' | 'bl' | 'br'

const MIN_CROP_SIZE = 0.08
const dragState = ref<{
  mode: DragMode
  clipId: string
  startX: number
  startY: number
  originX: number
  originY: number
  originWidth: number
  originHeight: number
  lockAspectRatio: boolean
} | null>(null)

const cropState = ref<{
  clipId: string
  handle: CropHandle
  startX: number
  startY: number
  originCrop: { x: number; y: number; width: number; height: number }
  rect: DOMRect
} | null>(null)

function getClipCrop(clip: EditorClip) {
  const crop = clip.crop ?? { x: 0, y: 0, width: 1, height: 1 }
  const x = clampValue(Number(crop.x ?? 0), 0, 1)
  const y = clampValue(Number(crop.y ?? 0), 0, 1)
  const width = clampValue(Number(crop.width ?? 1), MIN_CROP_SIZE, 1)
  const height = clampValue(Number(crop.height ?? 1), MIN_CROP_SIZE, 1)
  return {
    x,
    y,
    width: Math.max(MIN_CROP_SIZE, Math.min(width, 1 - x)),
    height: Math.max(MIN_CROP_SIZE, Math.min(height, 1 - y)),
  }
}

function showCropOverlay(clip: EditorClip) {
  return Boolean(props.cropMode && clip.type === 'video' && clip.id === selectedClipId.value)
}

function cropWindowStyle(clip: EditorClip): CSSProperties {
  const crop = getClipCrop(clip)
  return {
    left: `${crop.x * 100}%`,
    top: `${crop.y * 100}%`,
    width: `${crop.width * 100}%`,
    height: `${crop.height * 100}%`,
    boxShadow: '0 0 0 9999px rgba(0,0,0,0.45)',
  }
}

function onCropPointerDown(event: PointerEvent, clip: EditorClip, handle: CropHandle) {
  const target = (event.currentTarget as HTMLElement).closest(`[data-clip-id="${clip.id}"]`) as HTMLElement | null
  if (!target) return
  cropState.value = {
    clipId: clip.id,
    handle,
    startX: event.clientX,
    startY: event.clientY,
    originCrop: getClipCrop(clip),
    rect: target.getBoundingClientRect(),
  }
  window.addEventListener('pointermove', onCropPointerMove)
  window.addEventListener('pointerup', onCropPointerUp)
  window.addEventListener('pointercancel', onCropPointerUp)
}

function onCropPointerMove(event: PointerEvent) {
  const state = cropState.value
  if (!state) return
  const clip = visualClips.value.find((entry) => entry.id === state.clipId)
  if (!clip) return
  const dx = (event.clientX - state.startX) / Math.max(1, state.rect.width)
  const dy = (event.clientY - state.startY) / Math.max(1, state.rect.height)
  const origin = state.originCrop
  let next = { ...origin }

  if (state.handle === 'move') {
    next.x = clampValue(origin.x + dx, 0, 1 - origin.width)
    next.y = clampValue(origin.y + dy, 0, 1 - origin.height)
  } else {
    if (state.handle === 'tl' || state.handle === 'bl') {
      const maxLeft = origin.x + origin.width - MIN_CROP_SIZE
      next.x = clampValue(origin.x + dx, 0, maxLeft)
      next.width = clampValue(origin.width - (next.x - origin.x), MIN_CROP_SIZE, 1 - next.x)
    }
    if (state.handle === 'tr' || state.handle === 'br') {
      next.width = clampValue(origin.width + dx, MIN_CROP_SIZE, 1 - origin.x)
    }
    if (state.handle === 'tl' || state.handle === 'tr') {
      const maxTop = origin.y + origin.height - MIN_CROP_SIZE
      next.y = clampValue(origin.y + dy, 0, maxTop)
      next.height = clampValue(origin.height - (next.y - origin.y), MIN_CROP_SIZE, 1 - next.y)
    }
    if (state.handle === 'bl' || state.handle === 'br') {
      next.height = clampValue(origin.height + dy, MIN_CROP_SIZE, 1 - origin.y)
    }
  }

  emit('update:clip', state.clipId, {
    crop: next,
  })
}

function onCropPointerUp() {
  cropState.value = null
  window.removeEventListener('pointermove', onCropPointerMove)
  window.removeEventListener('pointerup', onCropPointerUp)
  window.removeEventListener('pointercancel', onCropPointerUp)
}

function onClipPointerDown(event: PointerEvent, clip: EditorClip, mode: DragMode = 'move') {
  if (showCropOverlay(clip)) return
  closeContextMenu()
  emit('select-clip', clip.id)
  const position = clip.position ?? { x: 0, y: 0 }
  const size = clip.size ?? { width: 100, height: 100 }
  dragState.value = {
    mode,
    clipId: clip.id,
    startX: event.clientX,
    startY: event.clientY,
    originX: position.x,
    originY: position.y,
    originWidth: size.width,
    originHeight: size.height,
    lockAspectRatio: clip.lockAspectRatio ?? false,
  }
  window.addEventListener('pointermove', onClipPointerMove)
  window.addEventListener('pointerup', onClipPointerUp)
  window.addEventListener('pointercancel', onClipPointerUp)
}

function onClipPointerMove(event: PointerEvent) {
  const state = dragState.value
  const stage = stageRef.value ?? frameRef.value
  if (!state || !stage) return
  const rect = stage.getBoundingClientRect()
  const dxPercent = ((event.clientX - state.startX) / rect.width) * 100
  const dyPercent = ((event.clientY - state.startY) / rect.height) * 100

  if (state.mode === 'move') {
    const maxX = Math.max(0, 100 - state.originWidth)
    const maxY = Math.max(0, 100 - state.originHeight)
    const nextX = Math.min(maxX, Math.max(0, state.originX + dxPercent))
    const nextY = Math.min(maxY, Math.max(0, state.originY + dyPercent))
    emit('update:clip', state.clipId, { position: { x: nextX, y: nextY } })
    return
  }

  let nextWidth = Math.min(100, Math.max(5, state.originWidth + dxPercent))
  let nextHeight = Math.min(100, Math.max(5, state.originHeight + dyPercent))
  if (state.lockAspectRatio && state.originHeight) {
    const ratio = state.originWidth / state.originHeight
    nextHeight = Math.min(100, Math.max(5, nextWidth / ratio))
  }
  emit('update:clip', state.clipId, {
    size: { width: nextWidth, height: nextHeight },
  })
}

function onClipPointerUp() {
  dragState.value = null
  window.removeEventListener('pointermove', onClipPointerMove)
  window.removeEventListener('pointerup', onClipPointerUp)
  window.removeEventListener('pointercancel', onClipPointerUp)
}

function formatTime(seconds: number) {
  if (!Number.isFinite(seconds)) return '0:00.00'
  const min = Math.floor(seconds / 60)
  const sec = Math.floor(seconds % 60)
  const hundredths = Math.floor((seconds % 1) * 100)
  return `${min}:${sec.toString().padStart(2, '0')}.${hundredths.toString().padStart(2, '0')}`
}

onBeforeUnmount(() => {
  stopPlaybackClock()
  if (frameResizeObserver) {
    frameResizeObserver.disconnect()
    frameResizeObserver = null
  }
  if (windowResizeCleanup) {
    windowResizeCleanup()
    windowResizeCleanup = null
  }
  if (fullscreenHideTimer) {
    clearTimeout(fullscreenHideTimer)
    fullscreenHideTimer = null
  }
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  window.removeEventListener('pointerdown', onGlobalPointerDown)
  window.removeEventListener('keydown', onGlobalKeyDown)
  onCropPointerUp()
  onClipPointerUp()
})

onMounted(() => {
  const applySize = (width: number, height: number) => {
    if (!Number.isFinite(width) || !Number.isFinite(height)) return
    const safeWidth = Math.max(0, width)
    const safeHeight = Math.max(0, height)
    frameSize.value = {
      width: safeWidth,
      height: safeHeight,
    }
  }

  const measure = () => {
    const rect = frameRef.value?.getBoundingClientRect()
    if (!rect) return
    applySize(rect.width, rect.height)
  }

  measure()

  if (typeof ResizeObserver !== 'undefined' && frameRef.value) {
    frameResizeObserver = new ResizeObserver((entries) => {
      const entry = entries[0]
      if (entry?.contentRect) {
        applySize(entry.contentRect.width, entry.contentRect.height)
        return
      }
      measure()
    })
    frameResizeObserver.observe(frameRef.value)
  }

  const onResize = () => measure()
  window.addEventListener('resize', onResize)
  windowResizeCleanup = () => window.removeEventListener('resize', onResize)

  document.addEventListener('fullscreenchange', handleFullscreenChange)
  window.addEventListener('pointerdown', onGlobalPointerDown)
  window.addEventListener('keydown', onGlobalKeyDown)
  isFullscreen.value = Boolean(document.fullscreenElement)

  let tries = 0
  const maxTries = 12
  const rafMeasure = () => {
    tries += 1
    if (frameSize.value.width > 8 && frameSize.value.height > 8) return
    if (tries >= maxTries) return
    requestAnimationFrame(rafMeasure)
  }
  requestAnimationFrame(rafMeasure)
})

defineExpose({
  toggleFullscreen,
})
</script>

<style scoped>
.control-btn {
  height: 1.95rem;
  min-width: 1.95rem;
  border-radius: 0.5rem;
  border: 1px solid #556152;
  background: #697565;
  color: #f5f5f5;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.05rem;
  transition: color 150ms ease, border-color 150ms ease, background 150ms ease;
}

.control-btn:hover {
  background: #7d9a7d;
  border-color: #697565;
}

.menu-item {
  width: 100%;
  border-radius: 0.45rem;
  padding: 0.4rem 0.55rem;
  font-size: 0.72rem;
  text-align: left;
  color: #e8e9e5;
  transition: background 150ms ease, color 150ms ease, border-color 150ms ease;
}

.menu-item:hover {
  background: rgba(105, 117, 101, 0.2);
  color: #f5f5f5;
}

.overlay-tool {
  height: 1.75rem;
  width: 1.75rem;
  border-radius: 0.4rem;
  color: #b0b0b0;
  transition: color 150ms ease, background 150ms ease;
}

.overlay-tool:hover {
  color: #f5f5f5;
  background: #252622;
}

.crop-window {
  border: 1px solid rgba(255, 255, 255, 0.95);
  cursor: move;
}

.crop-handle {
  position: absolute;
  width: 0.65rem;
  height: 0.65rem;
  border-radius: 9999px;
  border: 1px solid rgba(20, 20, 20, 0.8);
  background: #f5f5f5;
}

.crop-handle-tl {
  top: -0.35rem;
  left: -0.35rem;
  cursor: nwse-resize;
}

.crop-handle-tr {
  top: -0.35rem;
  right: -0.35rem;
  cursor: nesw-resize;
}

.crop-handle-bl {
  bottom: -0.35rem;
  left: -0.35rem;
  cursor: nesw-resize;
}

.crop-handle-br {
  bottom: -0.35rem;
  right: -0.35rem;
  cursor: nwse-resize;
}
</style>
