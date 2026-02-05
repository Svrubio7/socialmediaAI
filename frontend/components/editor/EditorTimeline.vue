<template>
  <section class="h-[40vh] min-h-[240px] max-h-[420px] border-t border-surface-800 bg-surface-900/70 flex flex-col">
    <div class="px-4 pt-2 pb-1">
      <div class="relative h-3 rounded-full bg-surface-800 overflow-hidden">
        <div class="absolute inset-y-0 left-0 bg-primary-500/40" :style="{ width: `${progressPercent}%` }" />
        <div
          class="absolute top-0 h-3 w-0.5 bg-primary-200"
          :style="{ left: `${progressPercent}%` }"
        />
      </div>
    </div>

    <div class="px-3 pb-2 flex items-center justify-between gap-2">
      <div class="flex items-center gap-1">
        <button type="button" class="tool-btn" @click="$emit('split')" aria-label="Split at playhead">
          <UiIcon name="Scissors" :size="14" />
        </button>
        <button type="button" class="tool-btn" @click="$emit('delete')" aria-label="Delete selected clip">
          <UiIcon name="Trash2" :size="14" />
        </button>
        <button type="button" class="tool-btn" @click="$emit('duplicate')" aria-label="Duplicate selected clip">
          <UiIcon name="Copy" :size="14" />
        </button>
      </div>
      <div class="flex items-center gap-1.5 text-xs text-surface-200">
        <button type="button" class="tool-btn" @click="changeZoom(-0.1)" aria-label="Zoom out">
          <UiIcon name="Minus" :size="14" />
        </button>
        <span class="min-w-11 text-center tabular-nums">{{ Math.round(zoom * 100) }}%</span>
        <button type="button" class="tool-btn" @click="changeZoom(0.1)" aria-label="Zoom in">
          <UiIcon name="Plus" :size="14" />
        </button>
        <button type="button" class="tool-btn px-2" @click="fitTimeline">Fit</button>
      </div>
    </div>

    <div
      ref="viewportRef"
      class="relative flex-1 min-h-0 overflow-x-auto overflow-y-auto px-3 pb-3"
      @wheel="onWheel"
    >
      <div class="relative" :style="{ width: `${trackWidth}px`, minWidth: '100%' }">
        <div class="sticky top-0 z-20 h-8 border-b border-surface-800 bg-surface-900" @click="onRulerClick">
          <div
            v-for="tick in timelineTicks"
            :key="tick.time"
            class="absolute top-0 h-full border-l border-surface-800 text-[10px] text-surface-400"
            :style="{ left: `${tick.left}px` }"
          >
            <span class="absolute top-1 left-1">{{ tick.label }}</span>
          </div>
        </div>

        <div ref="tracksRef" class="space-y-2 pt-2">
          <div
            v-for="track in tracks"
            :key="track.id"
            class="relative flex items-center gap-2"
            :class="hoverLayerId === track.id ? 'bg-primary-500/5 rounded-lg' : ''"
          >
            <div
              class="w-20 shrink-0 px-2 text-xs uppercase tracking-wide text-surface-300"
              @wheel.prevent="onLabelWheel"
            >
              {{ track.label }}
            </div>
            <div class="relative flex-1 h-14 rounded-lg border border-surface-800 bg-surface-950/80">
              <button
                v-for="clip in track.clips"
                :key="clip.id"
                type="button"
                class="group absolute top-1 h-12 rounded-md border text-left transition-all cursor-grab active:cursor-grabbing"
                :class="clip.id === selectedClipId ? 'border-primary-500 bg-primary-500/15 text-surface-100 shadow-[0_0_0_1px_rgba(105,117,101,.3)]' : 'border-surface-700 bg-surface-800 text-surface-100 hover:border-primary-400'"
                :style="clipStyle(clip)"
                @pointerdown.stop="startClipDrag($event, clip.id)"
              >
                <span class="block truncate px-3 pt-1 text-xs font-normal">{{ clip.label }}</span>
                <span class="block px-3 text-[11px] text-surface-300/80">{{ formatDuration(clip.duration) }}</span>

                <span
                  v-if="clip.id === selectedClipId"
                  class="trim-handle left-0"
                  @pointerdown.stop="startTrim($event, clip.id, 'start')"
                />
                <span
                  v-if="clip.id === selectedClipId"
                  class="trim-handle right-0"
                  @pointerdown.stop="startTrim($event, clip.id, 'end')"
                />
              </button>
            </div>
          </div>
        </div>

        <div
          class="absolute top-0 bottom-0 z-30 w-0.5 bg-primary-100"
          :style="{ left: `${playhead * pxPerSecond + labelWidth}px` }"
          @pointerdown.prevent="startPlayheadDrag"
        >
          <div
            class="absolute -top-1 -left-2 h-4 w-4 rounded-full bg-surface-100 border border-primary-300 cursor-grab active:cursor-grabbing"
            @pointerdown.prevent.stop="startPlayheadDrag"
          />
          <div class="absolute -top-6 -left-5 rounded bg-primary-500 px-1.5 py-0.5 text-[10px] text-surface-950">
            {{ formatDuration(playhead) }}
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, toRefs } from 'vue'
import type { EditorClip, EditorTrack } from '~/composables/useEditorState'

interface Props {
  tracks: EditorTrack[]
  playhead: number
  duration: number
  zoom: number
  selectedClipId?: string | null
}

const props = withDefaults(defineProps<Props>(), {
  selectedClipId: null,
})

const {
  tracks,
  playhead,
  duration,
  zoom,
  selectedClipId,
} = toRefs(props)

const emit = defineEmits<{
  'update:playhead': [time: number]
  'update:zoom': [zoom: number]
  'select-clip': [clipId: string]
  split: []
  delete: []
  duplicate: []
  'trim-clip': [{ clipId: string; startTime: number; duration: number }]
  'move-clip': [{ clipId: string; startTime: number; layer?: number }]
}>()

const viewportRef = ref<HTMLDivElement | null>(null)
const tracksRef = ref<HTMLDivElement | null>(null)
const temporaryClipBounds = ref<Record<string, { startTime: number; duration: number }>>({})
const hoverLayerId = ref<string | null>(null)

const labelWidth = 80

const pxPerSecond = computed(() => 110 * props.zoom)
const trackWidth = computed(() => Math.max(1000, props.duration * pxPerSecond.value + labelWidth + 40))
const progressPercent = computed(() => {
  if (!props.duration) return 0
  return Math.min(100, (props.playhead / props.duration) * 100)
})

const timelineTicks = computed(() => {
  const ticks: { time: number; left: number; label: string }[] = []
  const total = Math.max(props.duration, 1)
  const interval = props.zoom < 0.5 ? 2 : props.zoom > 2 ? 0.5 : 1
  for (let t = 0; t <= total + 0.0001; t += interval) {
    ticks.push({
      time: t,
      left: labelWidth + t * pxPerSecond.value,
      label: formatDuration(t),
    })
  }
  return ticks
})

type TrimEdge = 'start' | 'end'
const trimState = ref<{
  clipId: string
  edge: TrimEdge
  startX: number
  originalStart: number
  originalDuration: number
} | null>(null)

function clipGeometry(clip: EditorClip) {
  return temporaryClipBounds.value[clip.id] ?? { startTime: clip.startTime, duration: clip.duration }
}

function clipStyle(clip: EditorClip) {
  const geometry = clipGeometry(clip)
  return {
    left: `${geometry.startTime * pxPerSecond.value}px`,
    width: `${Math.max(22, geometry.duration * pxPerSecond.value)}px`,
  }
}

function onRulerClick(event: MouseEvent) {
  const target = event.currentTarget as HTMLElement
  const rect = target.getBoundingClientRect()
  const scrollLeft = viewportRef.value?.scrollLeft ?? 0
  const x = event.clientX - rect.left - labelWidth + scrollLeft
  const time = Math.max(0, Math.min(props.duration, x / pxPerSecond.value))
  emit('update:playhead', time)
}

function changeZoom(delta: number) {
  const next = Math.min(4, Math.max(0.1, props.zoom + delta))
  emit('update:zoom', next)
}

function fitTimeline() {
  const viewport = viewportRef.value
  if (!viewport || props.duration <= 0) return
  const next = Math.min(4, Math.max(0.1, (viewport.clientWidth - (labelWidth + 80)) / (props.duration * 110)))
  emit('update:zoom', next)
}

function onWheel(event: WheelEvent) {
  const viewport = viewportRef.value
  if (!viewport) return
  if (Math.abs(event.deltaY) >= Math.abs(event.deltaX)) {
    event.preventDefault()
    const delta = event.deltaY > 0 ? -0.1 : 0.1
    changeZoom(delta)
  } else {
    viewport.scrollLeft += event.deltaX
  }
}

function onLabelWheel(event: WheelEvent) {
  const viewport = viewportRef.value
  if (!viewport) return
  viewport.scrollTop += event.deltaY
}

function startTrim(event: PointerEvent, clipId: string, edge: TrimEdge) {
  const clip = props.tracks.flatMap((track) => track.clips).find((item) => item.id === clipId)
  if (!clip) return
  trimState.value = {
    clipId,
    edge,
    startX: event.clientX,
    originalStart: clip.startTime,
    originalDuration: clip.duration,
  }
  temporaryClipBounds.value = {}
  window.addEventListener('pointermove', onTrimMove)
  window.addEventListener('pointerup', onTrimEnd)
}

const clipDragState = ref<{
  clipId: string
  startX: number
  startY: number
  originStart: number
  originLayer?: number
  duration: number
  pointerId: number
} | null>(null)

function startClipDrag(event: PointerEvent, clipId: string) {
  const clip = props.tracks.flatMap((track) => track.clips).find((item) => item.id === clipId)
  if (!clip) return
  emit('select-clip', clipId)
  clipDragState.value = {
    clipId,
    startX: event.clientX,
    startY: event.clientY,
    originStart: clip.startTime,
    originLayer: clip.layer,
    duration: clip.duration,
    pointerId: event.pointerId,
  }
  temporaryClipBounds.value = {}
  window.addEventListener('pointermove', onClipDragMove)
  window.addEventListener('pointerup', onClipDragEnd)
}

function getTrackAtPointer(clientY: number) {
  const container = tracksRef.value
  const viewport = viewportRef.value
  if (!container || !viewport) return null
  const rect = container.getBoundingClientRect()
  const relativeY = clientY - rect.top + viewport.scrollTop
  const rowHeight = 64
  const index = Math.max(0, Math.min(props.tracks.length - 1, Math.floor(relativeY / rowHeight)))
  return props.tracks[index] ?? null
}

function onClipDragMove(event: PointerEvent) {
  if (!clipDragState.value) return
  const state = clipDragState.value
  const deltaSeconds = (event.clientX - state.startX) / pxPerSecond.value
  const nextStart = Math.max(0, state.originStart + deltaSeconds)
  temporaryClipBounds.value[state.clipId] = {
    startTime: nextStart,
    duration: state.duration,
  }
  const targetTrack = getTrackAtPointer(event.clientY)
  hoverLayerId.value = targetTrack?.id ?? null
}

function onClipDragEnd() {
  if (!clipDragState.value) return
  const state = clipDragState.value
  const finalBounds = temporaryClipBounds.value[state.clipId]
  const targetTrack = hoverLayerId.value
    ? props.tracks.find((track) => track.id === hoverLayerId.value)
    : null
  if (finalBounds) {
    emit('move-clip', {
      clipId: state.clipId,
      startTime: finalBounds.startTime,
      layer: targetTrack?.layer ?? state.originLayer,
    })
  }
  clipDragState.value = null
  hoverLayerId.value = null
  temporaryClipBounds.value = {}
  window.removeEventListener('pointermove', onClipDragMove)
  window.removeEventListener('pointerup', onClipDragEnd)
}

function onTrimMove(event: PointerEvent) {
  if (!trimState.value) return
  const state = trimState.value
  const deltaSeconds = (event.clientX - state.startX) / pxPerSecond.value
  const minDuration = 0.1

  if (state.edge === 'start') {
    const maxStart = state.originalStart + state.originalDuration - minDuration
    const nextStart = Math.max(0, Math.min(maxStart, state.originalStart + deltaSeconds))
    const nextDuration = state.originalDuration - (nextStart - state.originalStart)
    temporaryClipBounds.value[state.clipId] = { startTime: nextStart, duration: nextDuration }
    return
  }

  const nextDuration = Math.max(minDuration, state.originalDuration + deltaSeconds)
  temporaryClipBounds.value[state.clipId] = {
    startTime: state.originalStart,
    duration: nextDuration,
  }
}

function onTrimEnd() {
  if (!trimState.value) return
  const state = trimState.value
  const finalBounds = temporaryClipBounds.value[state.clipId]
  if (finalBounds) {
    emit('trim-clip', {
      clipId: state.clipId,
      startTime: finalBounds.startTime,
      duration: finalBounds.duration,
    })
  }
  trimState.value = null
  temporaryClipBounds.value = {}
  window.removeEventListener('pointermove', onTrimMove)
  window.removeEventListener('pointerup', onTrimEnd)
}

const playheadDragState = ref<{ pointerId: number } | null>(null)

function startPlayheadDrag(event: PointerEvent) {
  playheadDragState.value = { pointerId: event.pointerId }
  window.addEventListener('pointermove', onPlayheadDragMove)
  window.addEventListener('pointerup', stopPlayheadDrag)
  onPlayheadDragMove(event)
}

function onPlayheadDragMove(event: PointerEvent) {
  const viewport = viewportRef.value
  if (!viewport) return
  const rect = viewport.getBoundingClientRect()
  const x = event.clientX - rect.left - labelWidth + viewport.scrollLeft
  const time = Math.max(0, Math.min(props.duration, x / pxPerSecond.value))
  emit('update:playhead', time)
}

function stopPlayheadDrag() {
  playheadDragState.value = null
  window.removeEventListener('pointermove', onPlayheadDragMove)
  window.removeEventListener('pointerup', stopPlayheadDrag)
}

function formatDuration(seconds: number) {
  const safe = Math.max(0, seconds || 0)
  const minutes = Math.floor(safe / 60)
  const secs = Math.floor(safe % 60)
  const hundredths = Math.floor((safe % 1) * 100)
  return `${minutes}:${secs.toString().padStart(2, '0')}.${hundredths.toString().padStart(2, '0')}`
}

onBeforeUnmount(() => {
  onTrimEnd()
  onClipDragEnd()
  stopPlayheadDrag()
})
</script>

<style scoped>
.tool-btn {
  height: 1.9rem;
  border-radius: 0.45rem;
  border: 1px solid #2b2a25;
  background: #1a1b18;
  color: #d4d4d4;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.9rem;
  font-size: 0.72rem;
  transition: color 150ms ease, border-color 150ms ease, background 150ms ease;
}

.tool-btn:hover {
  color: #f5f5f5;
  border-color: #7d9a7d;
  background: #252622;
}

.trim-handle {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 0.35rem;
  background: rgba(245, 245, 245, 0.95);
  cursor: ew-resize;
}
</style>
