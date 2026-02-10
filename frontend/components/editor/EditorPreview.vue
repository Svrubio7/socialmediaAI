<template>
  <section class="flex-1 min-h-0 h-full w-full flex flex-col bg-surface-900">
    <div class="flex-1 min-h-0 p-2 lg:p-3">
      <div ref="frameRef" class="relative h-full w-full rounded-xl border border-surface-800 bg-surface-950/70 overflow-hidden">
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
                  class="absolute group"
                  :style="clipBoxStyle(clip)"
                  :class="clip.id === selectedClipId ? 'ring-2 ring-primary-400/70' : ''"
                  @pointerdown.stop="onClipPointerDown($event, clip)"
                >
                  <video
                    v-if="clip.type === 'video' && shouldRenderVideo(clip)"
                    ref="activeVideoRef"
                    :key="activeVideoKey"
                    :src="activeVideoSrc"
                    :poster="clipPosterSource(clip)"
                    class="h-full w-full rounded-md border border-surface-700 bg-black block"
                    :style="mediaStyle(clip)"
                    preload="auto"
                    playsinline
                    @loadedmetadata="onActiveVideoMetadata"
                    @loadeddata="onActiveVideoData"
                    @canplay="onActiveVideoCanPlay"
                    @timeupdate="onActiveVideoTimeUpdate"
                    @error="onActiveVideoError"
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
                </div>
              </template>
            </div>
          </div>
        </div>

        <button
          type="button"
          class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 h-16 w-16 rounded-full cream-btn transition-colors"
          @click="togglePlay"
          aria-label="Play or pause"
        >
          <UiIcon :name="playing ? 'Pause' : 'Play'" :size="24" class="mx-auto" />
        </button>
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
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, toRefs, watch, type CSSProperties } from 'vue'
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
}

const props = withDefaults(defineProps<Props>(), {
  selectedClipId: null,
  volume: 1,
  showControls: true,
  fallbackUrl: '',
  fallbackPoster: '',
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
  split: []
  duplicate: []
  delete: []
}>()

const frameRef = ref<HTMLDivElement | null>(null)
const stageRef = ref<HTMLDivElement | null>(null)
const activeVideoRef = ref<unknown>(null)
const videoErrorCount = ref<Record<string, number>>({})
const volumeValue = computed(() => props.volume ?? 1)
const fallbackPoster = computed(() => props.fallbackPoster || '')
const MAX_PREVIEW_RECOVERY_ATTEMPTS = 2
const DEFAULT_STAGE_RATIO = 16 / 9
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

const visualClips = computed(() =>
  clips.value
    .filter((clip) => clip.type !== 'audio')
    .slice()
    .sort((a, b) => a.startTime - b.startTime)
)

const videoClips = computed(() => visualClips.value.filter((clip) => clip.type === 'video'))

function isClipActive(clip: EditorClip, time: number) {
  return time >= clip.startTime && time <= clip.startTime + clip.duration
}

const activeVideoClip = computed<EditorClip | null>(() => {
  const now = currentTime.value
  const active = videoClips.value
    .filter((clip) => isClipActive(clip, now))
    .sort((a, b) => ((a.layer ?? 1) - (b.layer ?? 1)) || (a.startTime - b.startTime))
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

const primaryVideoClip = computed<EditorClip | null>(() => activeVideoClip.value ?? fallbackVideoClip.value)

const activeOverlayClips = computed(() =>
  visualClips.value
    .filter((clip) => clip.type !== 'video' && isClipActive(clip, currentTime.value))
    .sort((a, b) => ((a.layer ?? 1) - (b.layer ?? 1)) || (a.startTime - b.startTime))
)

const renderClips = computed(() => {
  const base = primaryVideoClip.value ? [primaryVideoClip.value] : []
  const combined = [...base, ...activeOverlayClips.value]
  return combined.sort((a, b) => clipZIndex(a) - clipZIndex(b))
})

const fallbackMedia = computed(() => {
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
  const fromActive = parseAspectRatio(primaryVideoClip.value?.aspectRatio)
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
  }
})

function resolveVideoSource(clip: EditorClip) {
  return clip.sourceUrl || props.fallbackUrl || ''
}

const activeVideoSrc = computed(() => {
  const clip = primaryVideoClip.value
  if (!clip || clip.type !== 'video') return ''
  return resolveVideoSource(clip)
})

const activeVideoRetryCount = computed(() => {
  const source = activeVideoSrc.value
  if (!source) return 0
  return videoErrorCount.value[source] ?? 0
})

const activeVideoKey = computed(() => {
  const clip = primaryVideoClip.value
  if (!clip) return `none-${activeVideoSrc.value}-${activeVideoRetryCount.value}`
  return `${clip.id}-${activeVideoSrc.value}-${activeVideoRetryCount.value}`
})

function shouldRenderVideo(clip: EditorClip) {
  if (clip.type !== 'video') return false
  if (!primaryVideoClip.value || clip.id !== primaryVideoClip.value.id) return false
  if (!activeVideoSrc.value) return false
  if (isLikelyImage(activeVideoSrc.value)) return false
  return true
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

function getDisplayMediaTime(clip: EditorClip) {
  if (activeVideoClip.value?.id === clip.id) {
    return getClipMediaTime(clip, currentTime.value)
  }
  const { trimStart, trimEnd } = getTrimRange(clip)
  if (currentTime.value < clip.startTime) return trimStart
  if (currentTime.value > clip.startTime + clip.duration) return trimEnd
  return getClipMediaTime(clip, currentTime.value)
}

function getActiveVideoElement(): HTMLVideoElement | null {
  const candidate = activeVideoRef.value
  if (!candidate) return null
  if (candidate instanceof HTMLVideoElement) return candidate
  if (Array.isArray(candidate)) {
    const fromArray = candidate.find((entry) => entry instanceof HTMLVideoElement)
    return fromArray ?? null
  }
  if (typeof candidate === 'object' && candidate !== null && '$el' in candidate) {
    const maybeEl = (candidate as { $el?: unknown }).$el
    if (maybeEl instanceof HTMLVideoElement) return maybeEl
  }
  return null
}

function syncVideoVolume() {
  const video = getActiveVideoElement()
  if (!video) return
  video.volume = volumeValue.value
  video.muted = volumeValue.value <= 0
}

function syncVideoRate() {
  const video = getActiveVideoElement()
  const clip = primaryVideoClip.value
  if (!video || !clip) return
  const rate = clip.effects?.speed ?? 1
  if (video.playbackRate !== rate) video.playbackRate = rate
}

function syncVideoCurrentTime(force = false) {
  const video = getActiveVideoElement()
  const clip = primaryVideoClip.value
  if (!video || !clip) return
  if (!Number.isFinite(video.currentTime)) return
  const target = getDisplayMediaTime(clip)
  if (!Number.isFinite(target)) return
  const threshold = force ? 0.01 : (playing.value && activeVideoClip.value ? 0.35 : 0.05)
  if (Math.abs(video.currentTime - target) > threshold) {
    try {
      video.currentTime = target
    } catch {
      // Ignore transient seek errors while metadata is still loading.
    }
  }
}

function mapMediaTimeToTimeline(clip: EditorClip, mediaTime: number) {
  const { trimStart } = getTrimRange(clip)
  const speed = Math.max(0.01, clip.effects?.speed ?? 1)
  const timelineTime = clip.startTime + ((mediaTime - trimStart) / speed)
  return Math.min(Math.max(0, timelineTime), clip.startTime + clip.duration)
}

let videoTimelineSyncFrame: number | null = null

function stopVideoTimelineSync() {
  if (videoTimelineSyncFrame) {
    cancelAnimationFrame(videoTimelineSyncFrame)
    videoTimelineSyncFrame = null
  }
}

function syncTimelineFromActiveVideo() {
  const clip = activeVideoClip.value
  const video = getActiveVideoElement()
  if (!playing.value || !clip || !video) {
    stopVideoTimelineSync()
    return
  }
  const mediaTime = Number(video.currentTime)
  if (!Number.isFinite(mediaTime)) {
    videoTimelineSyncFrame = requestAnimationFrame(syncTimelineFromActiveVideo)
    return
  }
  const clamped = mapMediaTimeToTimeline(clip, mediaTime)
  if (Math.abs(clamped - currentTime.value) > 0.016) {
    emit('update:currentTime', clamped)
  }
  videoTimelineSyncFrame = requestAnimationFrame(syncTimelineFromActiveVideo)
}

function startVideoTimelineSync() {
  if (videoTimelineSyncFrame) return
  videoTimelineSyncFrame = requestAnimationFrame(syncTimelineFromActiveVideo)
}

async function syncVideoPlayback() {
  const video = getActiveVideoElement()
  if (!video) return
  const shouldPlay = Boolean(playing.value && activeVideoClip.value)
  if (!shouldPlay) {
    if (!video.paused) video.pause()
    return
  }
  try {
    await video.play()
  } catch {
    if (!video.muted) {
      video.muted = true
      try {
        await video.play()
        return
      } catch {
        // fall through
      }
    }
    emit('update:playing', false)
  }
}

watch(
  activeVideoKey,
  () => {
    nextTick(() => {
      syncVideoVolume()
      syncVideoRate()
      syncVideoCurrentTime(true)
      void syncVideoPlayback()
    })
  },
  { immediate: true }
)

watch(currentTime, () => {
  syncVideoCurrentTime()
})

watch(playing, () => {
  void syncVideoPlayback()
})

watch(
  () => activeVideoClip.value?.id,
  () => {
    void syncVideoPlayback()
  }
)

watch(volumeValue, () => {
  syncVideoVolume()
})

watch(
  [playing, () => activeVideoClip.value?.id],
  ([isPlaying, activeClipId]) => {
    if (isPlaying && activeClipId) {
      startVideoTimelineSync()
      return
    }
    stopVideoTimelineSync()
  },
  { immediate: true }
)

function onActiveVideoMetadata() {
  const clip = primaryVideoClip.value
  const video = getActiveVideoElement()
  if (!clip || !video) return
  const measuredDuration = Number(video.duration || 0)
  if (Number.isFinite(measuredDuration) && measuredDuration > 0) {
    emit('update:clip-meta', { clipId: clip.id, duration: measuredDuration })
  }
  syncVideoCurrentTime(true)
  syncVideoRate()
}

function onActiveVideoData() {
  const source = activeVideoSrc.value
  if (source && videoErrorCount.value[source]) {
    videoErrorCount.value = {
      ...videoErrorCount.value,
      [source]: 0,
    }
  }
  syncVideoCurrentTime(true)
  if (playing.value) {
    startVideoTimelineSync()
    void syncVideoPlayback()
  }
}

function onActiveVideoCanPlay() {
  syncVideoCurrentTime(true)
  if (playing.value) {
    startVideoTimelineSync()
    void syncVideoPlayback()
  }
}

function onActiveVideoTimeUpdate() {
  if (!playing.value || !activeVideoClip.value) return
  const video = getActiveVideoElement()
  if (!video) return
  const mediaTime = Number(video.currentTime)
  if (!Number.isFinite(mediaTime)) return
  const clamped = mapMediaTimeToTimeline(activeVideoClip.value, mediaTime)
  if (Math.abs(clamped - currentTime.value) > 0.016) {
    emit('update:currentTime', clamped)
  }
}

function onActiveVideoError() {
  const source = activeVideoSrc.value
  if (!source) return
  const attempts = videoErrorCount.value[source] ?? 0
  if (attempts >= MAX_PREVIEW_RECOVERY_ATTEMPTS) {
    emit('update:playing', false)
    // eslint-disable-next-line no-console
    console.warn('Preview video failed after retry attempts', source)
    return
  }
  videoErrorCount.value = {
    ...videoErrorCount.value,
    [source]: attempts + 1,
  }
  // eslint-disable-next-line no-console
  console.warn('Preview video failed to load, retrying', source)
}

function clipOpacity(clip: EditorClip) {
  if (clip.type === 'video' && primaryVideoClip.value?.id === clip.id && !activeVideoClip.value) {
    const base = Number(clip.effects?.opacity ?? clip.style?.opacity ?? 1)
    const safeBase = Number.isFinite(base) ? base : 1
    return Math.max(0, Math.min(1, safeBase))
  }
  const localTime = Number(currentTime.value) - Number(clip.startTime)
  if (localTime < 0 || localTime > clip.duration) return 0
  const fadeIn = Number(clip.effects?.fadeIn ?? 0)
  const fadeOut = Number(clip.effects?.fadeOut ?? 0)
  const remaining = clip.duration - localTime
  let opacity = 1
  if (fadeIn > 0) opacity = Math.min(opacity, Math.max(0, localTime / fadeIn))
  if (fadeOut > 0) opacity = Math.min(opacity, Math.max(0, remaining / fadeOut))
  const base = Number(clip.effects?.opacity ?? clip.style?.opacity ?? 1)
  const safeBase = Number.isFinite(base) ? base : 1
  const combined = opacity * safeBase
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
    zIndex: clipZIndex(clip),
  }
  if (Math.abs(safeRotation) > 0.01) {
    style.transform = `rotate(${safeRotation}deg)`
    style.transformOrigin = 'center center'
    style.willChange = 'transform'
  }
  if (filter) {
    style.filter = filter
  }
  if (blendMode) {
    style.mixBlendMode = blendMode as CSSProperties['mixBlendMode']
  }
  return style
}

function mediaStyle(clip: EditorClip): CSSProperties {
  const fitMode = clip.fitMode ?? 'fit'
  const objectFit = fitMode === 'fill' ? 'cover' : fitMode === 'stretch' ? 'fill' : 'contain'
  return {
    objectFit: objectFit as CSSProperties['objectFit'],
  }
}

function shapeStyle(clip: EditorClip): CSSProperties {
  return {
    background: clip.style?.color ?? '#8f8cae80',
    border: clip.style?.outline ? '2px solid rgba(255,255,255,.7)' : 'none',
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

function onVolumeInput(event: Event) {
  const target = event.target as HTMLInputElement | null
  const next = Number(target?.value ?? 1)
  emit('update:volume', Number.isFinite(next) ? next : 1)
}

type DragMode = 'move' | 'resize'
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

function onClipPointerDown(event: PointerEvent, clip: EditorClip, mode: DragMode = 'move') {
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
}

function formatTime(seconds: number) {
  if (!Number.isFinite(seconds)) return '0:00.00'
  const min = Math.floor(seconds / 60)
  const sec = Math.floor(seconds % 60)
  const hundredths = Math.floor((seconds % 1) * 100)
  return `${min}:${sec.toString().padStart(2, '0')}.${hundredths.toString().padStart(2, '0')}`
}

onBeforeUnmount(() => {
  stopVideoTimelineSync()
  if (frameResizeObserver) {
    frameResizeObserver.disconnect()
    frameResizeObserver = null
  }
  if (windowResizeCleanup) {
    windowResizeCleanup()
    windowResizeCleanup = null
  }
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
</style>
