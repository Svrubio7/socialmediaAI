<template>
  <section class="flex-1 min-h-0 flex flex-col bg-surface-900">
    <div class="flex-1 min-h-0 p-2 lg:p-3">
      <div ref="frameRef" class="relative h-full w-full rounded-xl border border-surface-800 bg-surface-950/70 overflow-hidden">
        <div class="absolute left-1/2 top-2 z-20 -translate-x-1/2 flex items-center gap-1 rounded-md border border-surface-800 bg-surface-900/90 p-1">
          <button type="button" class="overlay-tool" aria-label="Crop mode">
            <UiIcon name="Crop" :size="14" />
          </button>
          <button type="button" class="overlay-tool" aria-label="Fit mode">
            <UiIcon name="Ratio" :size="14" />
          </button>
          <button type="button" class="overlay-tool" aria-label="More options">
            <UiIcon name="MoreHorizontal" :size="14" />
          </button>
        </div>

        <div class="absolute inset-0">
          <div v-if="renderClips.length === 0" class="absolute inset-0 flex items-center justify-center text-sm text-surface-400">
            No preview available
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
                v-if="clip.type === 'video'"
                :ref="(el) => setVideoRef(clip.id, el as HTMLVideoElement | null)"
                :src="clip.sourceUrl || ''"
                class="h-full w-full rounded-md border border-surface-700 bg-black"
                :style="mediaStyle(clip)"
                playsinline
                @loadedmetadata="onVideoMetaLoaded(clip)"
              />
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
                class="absolute -bottom-2 -right-2 h-4 w-4 rounded-full border border-surface-50 bg-primary-400"
                aria-label="Resize clip"
                @pointerdown.stop="onClipPointerDown($event, clip, 'resize')"
              />
            </div>
          </template>
        </div>

        <button
          type="button"
          class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 h-16 w-16 rounded-full bg-surface-900/70 border border-surface-50/20 text-surface-50 hover:bg-surface-800 transition-colors"
          @click="togglePlay"
          aria-label="Play or pause"
        >
          <UiIcon :name="playing ? 'Pause' : 'Play'" :size="24" class="mx-auto" />
        </button>
      </div>
    </div>

    <div class="border-t border-surface-800 bg-surface-900 px-3 py-2">
      <div class="flex flex-wrap items-center justify-center gap-1.5 sm:gap-2">
        <button type="button" class="control-btn" @click="seekToStart" aria-label="Skip to start">
          <UiIcon name="ChevronsLeft" :size="16" />
        </button>
        <button type="button" class="control-btn" @click="seekBy(-5)" aria-label="Seek backward 5 seconds">
          <UiIcon name="ChevronLeft" :size="16" />
          <span class="text-[10px] leading-none">5</span>
        </button>
        <button type="button" class="h-10 w-10 rounded-full bg-primary-500 text-surface-950 hover:bg-primary-400 transition-colors" @click="togglePlay" aria-label="Play or pause">
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
          <input v-model.number="volume" type="range" min="0" max="1" step="0.01" class="w-24 accent-primary-500" />
          <button type="button" class="control-btn" @click="toggleFullscreen" aria-label="Fullscreen">
            <UiIcon name="Maximize" :size="14" />
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, toRefs, watch } from 'vue'
import type { EditorClip } from '~/composables/useEditorState'

interface Props {
  clips: EditorClip[]
  selectedClipId?: string | null
  currentTime: number
  duration: number
  playing: boolean
}

const props = withDefaults(defineProps<Props>(), {
  selectedClipId: null,
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
  'update:clip': [clipId: string, patch: Partial<EditorClip>]
  'update:clip-meta': [{ clipId: string; duration?: number }]
  'select-clip': [clipId: string]
  split: []
  duplicate: []
  delete: []
}>()

const frameRef = ref<HTMLDivElement | null>(null)
const volume = ref(1)

const videoRefs = new Map<string, HTMLVideoElement>()
function setVideoRef(id: string, el: HTMLVideoElement | null) {
  if (!el) {
    videoRefs.delete(id)
    return
  }
  videoRefs.set(id, el)
  el.volume = volume.value
}

const visualClips = computed(() => clips.value.filter((clip) => clip.type !== 'audio'))
const activeClips = computed(() => {
  const now = currentTime.value
  return visualClips.value.filter((clip) => now >= clip.startTime && now <= clip.startTime + clip.duration)
})
const activeVideoClips = computed(() => activeClips.value.filter((clip) => clip.type === 'video'))
const activeNonVideoClips = computed(() => activeClips.value.filter((clip) => clip.type !== 'video'))
const holdFrameClip = computed(() => {
  if (activeVideoClips.value.length > 0) return null
  const now = currentTime.value
  const pastVideos = visualClips.value.filter((clip) => clip.type === 'video' && now > clip.startTime + clip.duration)
  if (!pastVideos.length) return null
  const sorted = pastVideos.sort((a, b) => (a.startTime + a.duration) - (b.startTime + b.duration))
  return sorted.length ? sorted[sorted.length - 1] : null
})
const renderClips = computed(() => {
  const base = activeVideoClips.value.length > 0 ? activeVideoClips.value : holdFrameClip.value ? [holdFrameClip.value] : []
  const combined = [...base, ...activeNonVideoClips.value]
  return combined.sort((a, b) => (a.layer ?? 1) - (b.layer ?? 1))
})

function clipOpacity(clip: EditorClip) {
  if (holdFrameClip.value?.id === clip.id && currentTime.value > clip.startTime + clip.duration) {
    return 1
  }
  const fadeIn = clip.effects?.fadeIn ?? 0
  const fadeOut = clip.effects?.fadeOut ?? 0
  const localTime = currentTime.value - clip.startTime
  const remaining = clip.duration - localTime
  let opacity = 1
  if (fadeIn > 0) opacity = Math.min(opacity, Math.max(0, localTime / fadeIn))
  if (fadeOut > 0) opacity = Math.min(opacity, Math.max(0, remaining / fadeOut))
  return opacity
}

function clipFilter(clip: EditorClip) {
  const brightness = clip.effects?.brightness ?? 0
  const contrast = clip.effects?.contrast ?? 1
  const saturation = clip.effects?.saturation ?? 1
  const gamma = clip.effects?.gamma ?? 1
  const hue = clip.effects?.hue ?? 0
  const blur = clip.effects?.blur ?? 0
  const brightnessValue = Math.max(0, (1 + brightness) * gamma)
  return `brightness(${brightnessValue}) contrast(${contrast}) saturate(${saturation}) hue-rotate(${hue}deg) blur(${blur}px)`
}

function clipOverlayStyle(clip: EditorClip) {
  const color = clip.effects?.overlayColor
  const opacity = clip.effects?.overlayOpacity ?? 0
  if (!color || color === 'transparent' || opacity <= 0) return null
  return {
    background: color,
    opacity,
    mixBlendMode: clip.effects?.overlayBlend ?? 'soft-light',
  }
}

function clipBoxStyle(clip: EditorClip) {
  const position = clip.position ?? { x: 0, y: 0 }
  const size = clip.size ?? { width: 100, height: 100 }
  const rotation = clip.rotation ?? 0
  return {
    left: `${position.x}%`,
    top: `${position.y}%`,
    width: `${size.width}%`,
    height: `${size.height}%`,
    transform: `rotate(${rotation}deg)`,
    opacity: clipOpacity(clip),
    zIndex: clip.layer ?? 1,
    filter: clipFilter(clip),
  }
}

function mediaStyle(clip: EditorClip) {
  const fitMode = clip.fitMode ?? 'fit'
  const objectFit = fitMode === 'fill' ? 'cover' : fitMode === 'stretch' ? 'fill' : 'contain'
  return {
    objectFit,
  }
}

function shapeStyle(clip: EditorClip) {
  return {
    background: clip.style?.color ?? '#8f8cae80',
    border: clip.style?.outline ? '2px solid rgba(255,255,255,.7)' : 'none',
  }
}

function getClipMediaTime(clip: EditorClip) {
  const trimStart = clip.trimStart ?? 0
  const trimEnd = clip.trimEnd ?? trimStart + clip.duration
  const local = currentTime.value - clip.startTime + trimStart
  return Math.min(Math.max(trimStart, local), trimEnd)
}

watch([currentTime, activeVideoClips, holdFrameClip], () => {
  activeVideoClips.value.forEach((clip) => {
    const video = videoRefs.get(clip.id)
    if (!video) return
    const targetTime = getClipMediaTime(clip)
    if (Number.isFinite(targetTime) && Math.abs(video.currentTime - targetTime) > 0.2) {
      video.currentTime = targetTime
    }
    const playbackRate = clip.effects?.speed ?? 1
    if (video.playbackRate !== playbackRate) video.playbackRate = playbackRate
  })

  if (holdFrameClip.value) {
    const video = videoRefs.get(holdFrameClip.value.id)
    if (video) {
      const trimEnd = holdFrameClip.value.trimEnd ?? holdFrameClip.value.duration
      if (Number.isFinite(trimEnd)) video.currentTime = trimEnd
      video.pause()
    }
  }
})

async function syncActiveVideoPlayback(forceState?: boolean) {
  const shouldPlay = typeof forceState === 'boolean' ? forceState : playing.value
  const activeIds = new Set(activeVideoClips.value.map((clip) => clip.id))

  for (const [id, video] of videoRefs) {
    if (!activeIds.has(id)) {
      if (!video.paused) video.pause()
      continue
    }
    if (shouldPlay && video.paused) {
      try {
        await video.play()
      } catch {
        emit('update:playing', false)
      }
    } else if (!shouldPlay && !video.paused) {
      video.pause()
    }
  }
}

watch([playing, activeVideoClips], () => {
  syncActiveVideoPlayback()
})

watch(volume, (next) => {
  for (const video of videoRefs.values()) {
    video.volume = next
  }
})

function onVideoMetaLoaded(clip: EditorClip) {
  const video = videoRefs.get(clip.id)
  const duration = Number(video?.duration || 0)
  if (Number.isFinite(duration)) {
    emit('update:clip-meta', { clipId: clip.id, duration })
  }
}

function togglePlay() {
  emit('update:playing', !playing.value)
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
  const frame = frameRef.value
  if (!state || !frame) return
  const rect = frame.getBoundingClientRect()
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
  onClipPointerUp()
})
</script>

<style scoped>
.control-btn {
  height: 1.95rem;
  min-width: 1.95rem;
  border-radius: 0.5rem;
  border: 1px solid #2b2a25;
  background: #1a1b18;
  color: #d4d4d4;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.05rem;
  transition: color 150ms ease, border-color 150ms ease, background 150ms ease;
}

.control-btn:hover {
  color: #f5f5f5;
  border-color: #7d9a7d;
  background: #252622;
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
