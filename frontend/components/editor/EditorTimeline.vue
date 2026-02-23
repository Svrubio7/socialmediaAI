<template>
  <section class="h-full min-h-0 border-t border-surface-800 bg-surface-900/70 flex flex-col timeline-container">
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
        <button
          type="button"
          class="tool-btn px-2"
          :class="snappingEnabled ? 'text-primary-200 border-primary-400/70' : ''"
          @click="emit('toggle-snapping')"
        >
          Snap {{ snappingEnabled ? 'On' : 'Off' }}
        </button>
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
            class="absolute top-0 h-full border-l border-surface-800 text-[clamp(0.6rem,0.7vw,0.7rem)] text-surface-400"
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
            :ref="(el) => setTrackRowRef(track.id, el as HTMLElement | null)"
          >
            <div
              v-if="track.isHeader"
              class="w-full px-2 text-xs uppercase tracking-widest text-surface-400"
              :class="hoverCreateGroup === track.group ? 'text-primary-200' : ''"
            >
              {{ track.label }}
            </div>
            <template v-else>
              <div
                class="w-20 shrink-0 px-2 text-xs uppercase tracking-wide text-surface-100 flex items-center gap-1 group"
                @wheel.prevent="onLabelWheel"
                @contextmenu.prevent="openLayerMenu($event, track)"
              >
                <span class="flex-1">{{ track.label }}</span>
                <button
                  type="button"
                  class="opacity-0 group-hover:opacity-100 transition-opacity text-surface-400 hover:text-surface-100"
                  @click.stop="emit('add-layer', { group: track.group ?? 'graphics' })"
                  aria-label="Add layer"
                >
                  <UiIcon name="Plus" :size="12" />
                </button>
              </div>
              <div
                class="relative flex-1 h-14 rounded-lg border border-surface-800 bg-surface-950/80"
                @mousemove="onLaneMouseMove($event, track)"
                @mouseleave="onLaneMouseLeave"
                @dragover.prevent
                @drop="onLaneDrop($event, track)"
              >
                <button
                  v-for="clip in track.clips"
                  :key="clip.id"
                  type="button"
                  class="group absolute top-1 h-12 rounded-md border text-left transition-all cursor-grab active:cursor-grabbing"
                  :class="[
                    clip.id === selectedClipId
                      ? 'border-primary-500 bg-primary-500/15 text-surface-100 shadow-[0_0_0_1px_rgba(105,117,101,.3)]'
                      : 'border-surface-700 bg-surface-800 text-surface-100 hover:border-primary-400',
                    snapPulseIds.has(clip.id) ? 'snap-highlight' : '',
                  ]"
                  :style="clipStyle(clip)"
                  @pointerdown.stop="startClipDrag($event, clip.id)"
                  @contextmenu.prevent="openClipMenu($event, clip)"
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
            </template>
          </div>
        </div>

        <div
          v-if="gapHover"
          class="absolute z-40 transition-plus"
          :style="{ left: `${gapHover.left}px`, top: `${gapHover.top}px` }"
          @mouseenter="onGapHoverEnter"
          @mouseleave="onGapHoverLeave"
        >
          <div class="relative">
            <button
              type="button"
              class="transition-plus-btn"
              @click.stop="openTransitionMenu($event)"
              aria-label="Add transition"
            >
              <UiIcon name="Plus" :size="12" class="mx-auto" />
            </button>
            <span class="transition-plus-tooltip">Add transition</span>
            <span class="absolute -bottom-4 left-1/2 -translate-x-1/2 rounded bg-black/80 px-1 text-[10px] text-surface-100">
              {{ gapHover.gapFrames }}f
            </span>
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

        <div
          v-if="props.showDiagnosticsOverlay && timelineDebugPayload"
          class="absolute right-2 top-10 z-40 w-[min(460px,95%)] rounded-lg border border-primary-500/60 bg-surface-950/95 p-2 text-[11px] leading-4 text-surface-100 shadow-lg"
        >
          <p class="text-primary-200 uppercase tracking-[0.16em] text-[10px]">Timeline Diagnostics</p>
          <p>FPS {{ timelineDebugPayload.fps }} | Clips {{ timelineDebugPayload.clips.length }} | Adjacency {{ timelineDebugPayload.adjacency.length }}</p>
          <p v-if="gapHover">Hovered boundary gap: {{ gapHover.gapFrames }}f</p>
          <p v-if="timelineDebugPayload.drag">
            Drag {{ timelineDebugPayload.drag.clipId }} {{ timelineDebugPayload.drag.desiredStartFrame }}f -> {{ timelineDebugPayload.drag.resolvedStartFrame }}f ({{ timelineDebugPayload.drag.reason }})
          </p>
          <p v-if="timelineDebugPayload.drag?.snapTargetFrame !== undefined">
            Snap target: {{ timelineDebugPayload.drag.snapTargetFrame }}f
          </p>
          <div class="mt-1 max-h-28 overflow-auto rounded border border-surface-800/70 bg-surface-900/70 p-1">
            <p
              v-for="clip in timelineDebugPayload.clips.slice(0, 20)"
              :key="clip.clipId"
              class="truncate"
            >
              {{ clip.clipId }} [{{ clip.startFrame }},{{ clip.endFrame }}) {{ clip.startSeconds.toFixed(3) }}s-{{ clip.endSeconds.toFixed(3) }}s
            </p>
          </div>
          <div class="mt-1 max-h-20 overflow-auto rounded border border-surface-800/70 bg-surface-900/70 p-1">
            <p
              v-for="edge in timelineDebugPayload.adjacency.slice(0, 12)"
              :key="`${edge.fromClipId}-${edge.toClipId}`"
              class="truncate"
            >
              {{ edge.fromClipId }} -> {{ edge.toClipId }} gap {{ edge.gapFrames }}f
            </p>
          </div>
          <div class="mt-1 max-h-16 overflow-auto rounded border border-surface-800/70 bg-surface-900/70 p-1">
            <p
              v-for="transition in timelineDebugPayload.transitions.slice(0, 8)"
              :key="`${transition.fromClipId}-${transition.toClipId}-${transition.name}`"
              class="truncate"
            >
              {{ transition.name }} {{ transition.fromClipId }} -> {{ transition.toClipId }} [{{ transition.startFrame }},{{ transition.endFrame }})
            </p>
          </div>
        </div>
      </div>
    </div>

    <div
      v-if="transitionMenu.open"
      ref="transitionMenuRef"
      class="fixed z-[60] w-64 rounded-lg border border-surface-800 bg-surface-950/95 p-3 shadow-xl"
      :style="{ left: `${transitionMenu.x}px`, top: `${transitionMenu.y}px` }"
      @click.stop
    >
      <div class="flex items-center justify-between mb-2">
        <p class="text-xs uppercase tracking-[0.2em] text-surface-400">Transition</p>
        <button type="button" class="text-surface-400 hover:text-surface-100" @click="closeTransitionMenu">
          <UiIcon name="X" :size="14" />
        </button>
      </div>
      <div class="space-y-1 max-h-40 overflow-auto pr-1">
        <button
          v-for="option in transitionOptions"
          :key="option"
          type="button"
          class="w-full rounded-md border px-2 py-1.5 text-left text-xs transition-colors"
          :class="transitionMenuName === option ? 'border-primary-500 bg-primary-500/15 text-surface-100' : 'border-surface-800 bg-surface-900/70 text-surface-200 hover:border-primary-400'"
          @click="transitionMenuName = option"
        >
          {{ option }}
        </button>
      </div>
      <div class="mt-3 space-y-1">
        <div class="flex items-center justify-between text-xs text-surface-200">
          <span>Duration (sec)</span>
          <input v-model.number="transitionMenuDuration" type="number" min="0" step="0.05" class="w-16 rounded bg-surface-900 border border-surface-800 px-2 py-1 text-right text-xs text-surface-100" />
        </div>
        <input v-model.number="transitionMenuDuration" type="range" min="0" max="2" step="0.05" class="w-full accent-primary-500" />
      </div>
      <button type="button" class="mt-3 w-full rounded-md border border-primary-500 bg-primary-500/20 px-3 py-2 text-xs text-surface-100 hover:border-primary-400" @click="applyTransitionMenu">
        Apply transition
      </button>
    </div>

    <div
      v-if="contextMenu.open"
      ref="contextMenuRef"
      class="fixed z-[60] w-44 rounded-lg border border-surface-800 bg-surface-950/95 p-2 shadow-xl"
      :style="{ left: `${contextMenu.x}px`, top: `${contextMenu.y}px` }"
      @click.stop
    >
      <template v-if="contextMenu.type === 'clip'">
        <button type="button" class="menu-item" @click="handleClipMenu('split')">Split</button>
        <button type="button" class="menu-item" @click="handleClipMenu('duplicate')">Duplicate</button>
        <button type="button" class="menu-item" @click="handleClipMenu('delete')">Delete</button>
        <div class="my-1 h-px bg-surface-800" />
        <button type="button" class="menu-item" @click="handleClipMenu('effects')">Effects</button>
        <button type="button" class="menu-item" @click="handleClipMenu('filters')">Filters</button>
        <button type="button" class="menu-item" @click="handleClipMenu('adjust')">Adjust</button>
        <button type="button" class="menu-item" @click="handleClipMenu('fade')">Fade</button>
        <button type="button" class="menu-item" @click="handleClipMenu('speed')">Speed</button>
      </template>
      <template v-else>
        <button type="button" class="menu-item" @click="handleLayerMenu('add')">Add layer</button>
        <button type="button" class="menu-item text-red-200 hover:text-red-50" @click="handleLayerMenu('delete')">Delete layer</button>
      </template>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, toRefs } from 'vue'
import type { EditorClip, EditorLayerGroup, EditorTrack } from '~/composables/useEditorState'
import { resolveCollision, type CollisionRange } from '~/features/editor/services/collisionResolver'
import {
  clipRangeFrames,
  durationFramesToSeconds,
  durationSecondsToFrames,
  gapOverlapFrames,
  normalizeFps,
  toFrame,
  toSec,
} from '~/features/editor/services/timelineFrameMath'
import type { TimelineDiagnosticsPayload } from '~/features/editor/services/timelineDiagnostics'

interface Props {
  tracks: EditorTrack[]
  playhead: number
  duration: number
  zoom: number
  fps?: number
  selectedClipId?: string | null
  snappingEnabled?: boolean
  showDiagnosticsOverlay?: boolean
  diagnosticsPayload?: TimelineDiagnosticsPayload | null
}

const props = withDefaults(defineProps<Props>(), {
  fps: 30,
  selectedClipId: null,
  snappingEnabled: true,
  showDiagnosticsOverlay: false,
  diagnosticsPayload: null,
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
  'move-clip': [{ clipId: string; startTime: number; layer?: number; group?: EditorLayerGroup; createLayer?: boolean }]
  'add-layer': [{ group: EditorLayerGroup }]
  'remove-layer': [{ group: EditorLayerGroup; layer: number }]
  'open-panel': [tab: string]
  'apply-transition-between': [{ fromClipId: string; toClipId: string; name?: string; duration?: number }]
  'drop-media': [{ group: EditorLayerGroup; layer: number; startTime: number; media: { id: string; type: 'video' | 'image' | 'audio'; name: string; duration?: number; storagePath?: string; sourceId?: string; sourceUrl?: string; thumbnail?: string } }]
  'toggle-snapping': []
}>()

const viewportRef = ref<HTMLDivElement | null>(null)
const tracksRef = ref<HTMLDivElement | null>(null)
const temporaryClipBounds = ref<Record<string, { startTime: number; duration: number }>>({})
const hoverLayerId = ref<string | null>(null)
const hoverCreateGroup = ref<EditorLayerGroup | null>(null)
const trackRowRefs = new Map<string, HTMLElement>()
const gapHover = ref<null | { fromClipId: string; toClipId: string; left: number; top: number; gapFrames: number }>(null)
const plusHovering = ref(false)
const snapPulseIds = ref(new Set<string>())
const dragDiagnostics = ref<null | {
  clipId: string
  desiredStartFrame: number
  resolvedStartFrame: number
  layer: number
  group: string
  reason: string
  snapTargetFrame?: number
}>(null)
const transitionMenu = ref({ open: false, x: 0, y: 0, fromClipId: '', toClipId: '' })
const transitionMenuName = ref('Cross fade')
const transitionMenuDuration = ref(0.6)
const transitionMenuRef = ref<HTMLDivElement | null>(null)
const contextMenu = ref<{ open: boolean; x: number; y: number; type: 'clip' | 'layer'; clipId?: string; group?: EditorLayerGroup; layer?: number }>({
  open: false,
  x: 0,
  y: 0,
  type: 'clip',
})
const contextMenuRef = ref<HTMLDivElement | null>(null)

const labelWidth = 80
const resolvedFps = computed(() => normalizeFps(props.fps))

const pxPerSecond = computed(() => 110 * props.zoom)
const trackWidth = computed(() => Math.max(1000, props.duration * pxPerSecond.value + labelWidth + 40))
const progressPercent = computed(() => {
  if (!props.duration) return 0
  return Math.min(100, (props.playhead / props.duration) * 100)
})

const timelineTicks = computed(() => {
  const ticks: { time: number; left: number; label: string }[] = []
  const total = Math.max(props.duration, 1)
  const minTickPx = 72
  const intervals = [0.25, 0.5, 1, 2, 5, 10, 15, 30, 60, 120, 300]
  const px = pxPerSecond.value
  let interval = intervals[intervals.length - 1]
  for (const candidate of intervals) {
    if (candidate * px >= minTickPx) {
      interval = candidate
      break
    }
  }
  for (let t = 0; t <= total + 0.0001; t += interval) {
    ticks.push({
      time: t,
      left: labelWidth + t * px,
      label: formatTickLabel(t, interval),
    })
  }
  return ticks
})

const timelineDebugPayload = computed(() => {
  if (!props.showDiagnosticsOverlay) return null
  if (!props.diagnosticsPayload) return null
  return {
    ...props.diagnosticsPayload,
    drag: dragDiagnostics.value ?? props.diagnosticsPayload.drag ?? null,
  }
})

const transitionOptions = [
  'None',
  'Cross fade',
  'Hard wipe',
]

const BOUNDARY_ACTIVATION_RADIUS_PX = 24
const SNAP_THRESHOLD_PX = 16
let gapHoverHideTimer: ReturnType<typeof setTimeout> | null = null

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

function clipRange(clip: EditorClip) {
  const geometry = clipGeometry(clip)
  return clipRangeFrames(geometry.startTime, geometry.duration, resolvedFps.value)
}

function laneCollisionRanges(track: EditorTrack, excludeClipId?: string): CollisionRange[] {
  return track.clips
    .filter((clip) => clip.id !== excludeClipId)
    .map((clip) => {
      const range = clipRange(clip)
      return {
        clipId: clip.id,
        startFrame: range.startFrame,
        endFrame: range.endFrame,
      }
    })
}

function clipStyle(clip: EditorClip) {
  const geometry = clipGeometry(clip)
  return {
    left: `${geometry.startTime * pxPerSecond.value}px`,
    width: `${Math.max(22, geometry.duration * pxPerSecond.value)}px`,
  }
}

function clampValue(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value))
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

function closeTransitionMenu() {
  transitionMenu.value = { open: false, x: 0, y: 0, fromClipId: '', toClipId: '' }
}

function closeContextMenu() {
  contextMenu.value = { open: false, x: 0, y: 0, type: 'clip' }
}

function closeMenus() {
  closeTransitionMenu()
  closeContextMenu()
}

function clearGapHoverHideTimer() {
  if (!gapHoverHideTimer) return
  clearTimeout(gapHoverHideTimer)
  gapHoverHideTimer = null
}

function scheduleGapHoverHide() {
  clearGapHoverHideTimer()
  gapHoverHideTimer = setTimeout(() => {
    if (!plusHovering.value && !transitionMenu.value.open) {
      gapHover.value = null
    }
  }, 90)
}

function openTransitionMenu(event: MouseEvent) {
  if (!gapHover.value) return
  clearGapHoverHideTimer()
  closeContextMenu()
  const { fromClipId, toClipId } = gapHover.value
  const fromClip = props.tracks.flatMap((track) => track.clips).find((clip) => clip.id === fromClipId)
  const storedName = fromClip?.effects?.transition
  transitionMenuName.value = storedName && transitionOptions.includes(storedName) ? storedName : 'Cross fade'
  transitionMenuDuration.value = fromClip?.effects?.transitionDuration ?? 0.6
  transitionMenu.value = {
    open: true,
    x: event.clientX,
    y: event.clientY,
    fromClipId,
    toClipId,
  }
  nextTick(() => {
    const pos = clampFixedMenuPosition(transitionMenu.value.x, transitionMenu.value.y, transitionMenuRef.value)
    transitionMenu.value = { ...transitionMenu.value, x: pos.x, y: pos.y }
  })
}

function onGapHoverEnter() {
  plusHovering.value = true
  clearGapHoverHideTimer()
}

function onGapHoverLeave() {
  plusHovering.value = false
  if (!transitionMenu.value.open) scheduleGapHoverHide()
}

function applyTransitionMenu() {
  if (!transitionMenu.value.open) return
  const name = transitionMenuName.value
  const duration = Number(transitionMenuDuration.value) || 0
  emit('apply-transition-between', {
    fromClipId: transitionMenu.value.fromClipId,
    toClipId: transitionMenu.value.toClipId,
    name: name === 'None' ? undefined : name,
    duration,
  })
  closeTransitionMenu()
}

function openClipMenu(event: MouseEvent, clip: EditorClip) {
  closeTransitionMenu()
  emit('select-clip', clip.id)
  contextMenu.value = {
    open: true,
    x: event.clientX,
    y: event.clientY,
    type: 'clip',
    clipId: clip.id,
  }
  nextTick(() => {
    const pos = clampFixedMenuPosition(contextMenu.value.x, contextMenu.value.y, contextMenuRef.value)
    contextMenu.value = { ...contextMenu.value, x: pos.x, y: pos.y }
  })
}

function handleClipMenu(action: 'split' | 'duplicate' | 'delete' | 'effects' | 'filters' | 'adjust' | 'fade' | 'speed') {
  const clipId = contextMenu.value.clipId
  if (clipId) emit('select-clip', clipId)
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

function openLayerMenu(event: MouseEvent, track: EditorTrack) {
  if (track.isHeader) return
  closeTransitionMenu()
  contextMenu.value = {
    open: true,
    x: event.clientX,
    y: event.clientY,
    type: 'layer',
    group: track.group ?? 'graphics',
    layer: track.layer ?? 1,
  }
  nextTick(() => {
    const pos = clampFixedMenuPosition(contextMenu.value.x, contextMenu.value.y, contextMenuRef.value)
    contextMenu.value = { ...contextMenu.value, x: pos.x, y: pos.y }
  })
}

function handleLayerMenu(action: 'add' | 'delete') {
  const group = contextMenu.value.group ?? 'graphics'
  const layer = contextMenu.value.layer ?? 1
  if (action === 'add') emit('add-layer', { group })
  if (action === 'delete') emit('remove-layer', { group, layer })
  closeContextMenu()
}

function triggerSnapPulse(...clipIds: string[]) {
  if (!clipIds.length) return
  const next = new Set(snapPulseIds.value)
  clipIds.forEach((id) => next.add(id))
  snapPulseIds.value = next
  window.setTimeout(() => {
    const updated = new Set(snapPulseIds.value)
    clipIds.forEach((id) => updated.delete(id))
    snapPulseIds.value = updated
  }, 240)
}

function setGapHoverAtBoundary(
  track: EditorTrack,
  fromClip: EditorClip,
  toClip: EditorClip,
  boundaryTime?: number,
  gapFramesOverride?: number
) {
  const rowEl = trackRowRefs.get(track.id)
  const tracksTop = tracksRef.value?.offsetTop ?? 0
  const rowTop = rowEl?.offsetTop ?? 0
  const rowHeight = rowEl?.offsetHeight ?? 56
  const fromRange = clipRange(fromClip)
  const toRange = clipRange(toClip)
  const fromEdge = toSec(fromRange.endFrame, resolvedFps.value)
  const toEdge = toSec(toRange.startFrame, resolvedFps.value)
  const gapInfo = gapOverlapFrames(fromRange, toRange, resolvedFps.value)
  const boundary = Number.isFinite(boundaryTime ?? Number.NaN)
    ? Number(boundaryTime)
    : (fromEdge + toEdge) / 2
  gapHover.value = {
    fromClipId: fromClip.id,
    toClipId: toClip.id,
    left: labelWidth + boundary * pxPerSecond.value,
    top: tracksTop + rowTop + rowHeight / 2,
    gapFrames: gapFramesOverride ?? gapInfo.gapFrames,
  }
}

function getAttachedBoundaries(track: EditorTrack) {
  const boundaries: Array<{
    fromClip: EditorClip
    toClip: EditorClip
    boundarySec: number
    fromEdgeSec: number
    toEdgeSec: number
    gapFrames: number
  }> = []
  if (track.isHeader || track.group !== 'video') return boundaries
  const sorted = track.clips
    .slice()
    .sort((a, b) => clipRange(a).startFrame - clipRange(b).startFrame)
  for (let i = 0; i < sorted.length - 1; i += 1) {
    const fromClip = sorted[i]
    const toClip = sorted[i + 1]
    const fromRange = clipRange(fromClip)
    const toRange = clipRange(toClip)
    const gap = gapOverlapFrames(fromRange, toRange, resolvedFps.value)
    if (!gap.isAdjacent) continue
    const fromEdgeSec = toSec(fromRange.endFrame, resolvedFps.value)
    const toEdgeSec = toSec(toRange.startFrame, resolvedFps.value)
    boundaries.push({
      fromClip,
      toClip,
      boundarySec: (fromEdgeSec + toEdgeSec) / 2,
      fromEdgeSec,
      toEdgeSec,
      gapFrames: gap.gapFrames,
    })
  }
  return boundaries
}

function findNearestBoundary(track: EditorTrack, pointerTime: number) {
  const pointerPx = pointerTime * pxPerSecond.value
  const boundaries = getAttachedBoundaries(track)
  let best:
    | {
        fromClip: EditorClip
        toClip: EditorClip
        boundarySec: number
        gapFrames: number
        distancePx: number
      }
    | null = null

  for (const boundary of boundaries) {
    const centerPx = boundary.boundarySec * pxPerSecond.value
    const fromEdgePx = boundary.fromEdgeSec * pxPerSecond.value
    const toEdgePx = boundary.toEdgeSec * pxPerSecond.value
    const distancePx = Math.min(
      Math.abs(pointerPx - centerPx),
      Math.abs(pointerPx - fromEdgePx),
      Math.abs(pointerPx - toEdgePx),
    )
    if (distancePx > BOUNDARY_ACTIVATION_RADIUS_PX) continue
    if (!best || distancePx < best.distancePx) {
      best = {
        fromClip: boundary.fromClip,
        toClip: boundary.toClip,
        boundarySec: boundary.boundarySec,
        gapFrames: boundary.gapFrames,
        distancePx,
      }
    }
  }
  return best
}

function onRulerClick(event: MouseEvent) {
  const target = event.currentTarget as HTMLElement
  const rect = target.getBoundingClientRect()
  const scrollLeft = viewportRef.value?.scrollLeft ?? 0
  const x = event.clientX - rect.left - labelWidth + scrollLeft
  const raw = Math.max(0, Math.min(props.duration, x / pxPerSecond.value))
  const frame = Math.max(0, toFrame(raw, resolvedFps.value))
  emit('update:playhead', toSec(frame, resolvedFps.value))
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

function onLaneMouseMove(event: MouseEvent, track: EditorTrack) {
  clearGapHoverHideTimer()
  if (track.isHeader || track.group !== 'video') {
    if (!plusHovering.value) gapHover.value = null
    return
  }
  if (!track.clips.length) {
    if (!plusHovering.value) gapHover.value = null
    return
  }
  const lane = event.currentTarget as HTMLElement
  const rect = lane.getBoundingClientRect()
  const scrollLeft = viewportRef.value?.scrollLeft ?? 0
  const x = event.clientX - rect.left + scrollLeft
  const time = x / pxPerSecond.value
  const nearest = findNearestBoundary(track, time)
  if (nearest) {
    setGapHoverAtBoundary(track, nearest.fromClip, nearest.toClip, nearest.boundarySec, nearest.gapFrames)
    return
  }
  if (!plusHovering.value) gapHover.value = null
}

function onLaneMouseLeave() {
  if (plusHovering.value || transitionMenu.value.open) return
  scheduleGapHoverHide()
}

function onLaneDrop(event: DragEvent, track: EditorTrack) {
  if (track.isHeader || !event.dataTransfer) return
  const raw = event.dataTransfer.getData('application/x-editor-media')
  if (!raw) return
  try {
    const media = JSON.parse(raw)
    const lane = event.currentTarget as HTMLElement
    const rect = lane.getBoundingClientRect()
    const scrollLeft = viewportRef.value?.scrollLeft ?? 0
    const x = event.clientX - rect.left + scrollLeft
    const startFrame = Math.max(0, toFrame(x / pxPerSecond.value, resolvedFps.value))
    emit('drop-media', {
      group: track.group ?? 'graphics',
      layer: track.layer ?? 1,
      startTime: toSec(startFrame, resolvedFps.value),
      media,
    })
  } catch {
    // Ignore invalid payloads from unrelated drags.
  }
}

function startTrim(event: PointerEvent, clipId: string, edge: TrimEdge) {
  closeMenus()
  plusHovering.value = false
  clearGapHoverHideTimer()
  gapHover.value = null
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
  window.addEventListener('pointercancel', onTrimEnd)
}

const clipDragState = ref<{
  clipId: string
  startX: number
  startY: number
  originStart: number
  originLayer?: number
  originGroup?: EditorLayerGroup
  duration: number
  pointerId: number
} | null>(null)

function startClipDrag(event: PointerEvent, clipId: string) {
  const clip = props.tracks.flatMap((track) => track.clips).find((item) => item.id === clipId)
  if (!clip) return
  closeMenus()
  plusHovering.value = false
  clearGapHoverHideTimer()
  gapHover.value = null
  const group = clip.layerGroup ?? (clip.type === 'audio' ? 'audio' : clip.type === 'video' ? 'video' : 'graphics')
  emit('select-clip', clipId)
  clipDragState.value = {
    clipId,
    startX: event.clientX,
    startY: event.clientY,
    originStart: clip.startTime,
    originLayer: clip.layer,
    originGroup: group,
    duration: clip.duration,
    pointerId: event.pointerId,
  }
  dragDiagnostics.value = null
  temporaryClipBounds.value = {}
  window.addEventListener('pointermove', onClipDragMove)
  window.addEventListener('pointerup', onClipDragEnd)
  window.addEventListener('pointercancel', onClipDragEnd)
}

function setTrackRowRef(id: string, el: HTMLElement | null) {
  if (!el) {
    trackRowRefs.delete(id)
    return
  }
  trackRowRefs.set(id, el)
}

function getTrackAtPointer(clientY: number) {
  for (const track of props.tracks) {
    if (track.isHeader) continue
    const el = trackRowRefs.get(track.id)
    if (!el) continue
    const rect = el.getBoundingClientRect()
    if (clientY >= rect.top && clientY <= rect.bottom) return track
  }
  return null
}

function getGroupTopRect(group: EditorLayerGroup) {
  for (const track of props.tracks) {
    if (track.isHeader) continue
    if (track.group !== group) continue
    const el = trackRowRefs.get(track.id)
    if (el) return el.getBoundingClientRect()
  }
  return null
}

function sortedTrackClips(track: EditorTrack, excludeId?: string) {
  return track.clips
    .filter((clip) => clip.id !== excludeId)
    .slice()
    .sort((a, b) => a.startTime - b.startTime)
}

function findTrackForClip(clipId: string) {
  for (const track of props.tracks) {
    const clip = track.clips.find((item) => item.id === clipId)
    if (clip) return { track, clip }
  }
  return null
}

function resolveNonOverlappingStart(track: EditorTrack, clip: EditorClip, desiredStart: number) {
  const sorted = sortedTrackClips(track, clip.id)
    .slice()
    .sort((left, right) => clipRange(left).startFrame - clipRange(right).startFrame)
  const desiredStartFrame = Math.max(0, toFrame(desiredStart, resolvedFps.value))
  const durationFrames = durationSecondsToFrames(clip.duration, resolvedFps.value)

  const prev = sorted.filter((entry) => clipRange(entry).endFrame <= desiredStartFrame).pop()
  const next = sorted.find((entry) => clipRange(entry).startFrame >= desiredStartFrame)

  const resolved = resolveCollision({
    operation: 'drag',
    group: track.group ?? 'graphics',
    layer: track.layer ?? 1,
    clipId: clip.id,
    desiredStartFrame,
    durationFrames,
    laneClips: laneCollisionRanges(track, clip.id),
  })

  let startFrame = resolved.startFrame
  let snapTargetFrame: number | undefined

  if (props.snappingEnabled) {
    const snapThresholdFrames = Math.max(1, Math.round((SNAP_THRESHOLD_PX / pxPerSecond.value) * resolvedFps.value))
    if (prev) {
      const prevEnd = clipRange(prev).endFrame
      if (Math.abs(startFrame - prevEnd) <= snapThresholdFrames) {
        startFrame = prevEnd
        snapTargetFrame = prevEnd
        triggerSnapPulse(clip.id, prev.id)
        setGapHoverAtBoundary(track, prev, clip, toSec(startFrame, resolvedFps.value), 0)
      }
    }
    if (snapTargetFrame === undefined && next) {
      const nextStart = clipRange(next).startFrame
      if (Math.abs((startFrame + durationFrames) - nextStart) <= snapThresholdFrames) {
        startFrame = nextStart - durationFrames
        snapTargetFrame = nextStart
        triggerSnapPulse(clip.id, next.id)
        setGapHoverAtBoundary(track, clip, next, toSec(startFrame + durationFrames, resolvedFps.value), 0)
      }
    }
  }

  if (snapTargetFrame === undefined) gapHover.value = null

  dragDiagnostics.value = {
    clipId: clip.id,
    desiredStartFrame,
    resolvedStartFrame: startFrame,
    layer: track.layer ?? 1,
    group: track.group ?? 'graphics',
    reason: resolved.reason,
    snapTargetFrame,
  }

  return {
    start: toSec(startFrame, resolvedFps.value),
    prev,
    next,
  }
}

function onClipDragMove(event: PointerEvent) {
  if (!clipDragState.value) return
  const state = clipDragState.value
  const deltaSeconds = (event.clientX - state.startX) / pxPerSecond.value
  const nextStart = Math.max(0, state.originStart + deltaSeconds)
  const targetTrack = getTrackAtPointer(event.clientY)
  const fallbackTrack = props.tracks.find((track) => track.group === state.originGroup && track.layer === state.originLayer)
  const activeTrack = targetTrack && targetTrack.group === state.originGroup ? targetTrack : fallbackTrack
  const clip = props.tracks.flatMap((track) => track.clips).find((item) => item.id === state.clipId)
  if (clip && activeTrack) {
    const resolved = resolveNonOverlappingStart(activeTrack, clip, nextStart)
    temporaryClipBounds.value[state.clipId] = {
      startTime: resolved.start,
      duration: state.duration,
    }
  } else {
    temporaryClipBounds.value[state.clipId] = {
      startTime: nextStart,
      duration: state.duration,
    }
  }
  if (activeTrack && activeTrack.group === state.originGroup) {
    hoverLayerId.value = activeTrack.id
  } else {
    hoverLayerId.value = null
  }

  const topRect = state.originGroup ? getGroupTopRect(state.originGroup) : null
  if (topRect && event.clientY < topRect.top - 6) {
    hoverCreateGroup.value = state.originGroup ?? null
  } else {
    hoverCreateGroup.value = null
  }
}

function onClipDragEnd() {
  if (!clipDragState.value) return
  const state = clipDragState.value
  const finalBounds = temporaryClipBounds.value[state.clipId]
  const targetTrack = hoverLayerId.value
    ? props.tracks.find((track) => track.id === hoverLayerId.value)
    : null
  const originTrack = findTrackForClip(state.clipId)?.track ?? null
  const activeTrack = targetTrack && targetTrack.group === state.originGroup
    ? targetTrack
    : originTrack
  let attachedBoundary: null | { track: EditorTrack; fromClip: EditorClip; toClip: EditorClip; boundarySec: number; gapFrames: number } = null
  if (activeTrack && activeTrack.group === 'video') {
    const candidates = getAttachedBoundaries(activeTrack).filter((entry) =>
      entry.fromClip.id === state.clipId || entry.toClip.id === state.clipId
    )
    const first = candidates[0]
    if (first) {
      attachedBoundary = {
        track: activeTrack,
        fromClip: first.fromClip,
        toClip: first.toClip,
        boundarySec: first.boundarySec,
        gapFrames: first.gapFrames,
      }
    }
  }
  if (finalBounds) {
    if (hoverCreateGroup.value && hoverCreateGroup.value === state.originGroup) {
      emit('move-clip', {
        clipId: state.clipId,
        startTime: finalBounds.startTime,
        group: state.originGroup,
        createLayer: true,
      })
    } else {
      emit('move-clip', {
        clipId: state.clipId,
        startTime: finalBounds.startTime,
        layer: targetTrack?.layer ?? state.originLayer,
        group: state.originGroup,
      })
    }
  }
  clipDragState.value = null
  dragDiagnostics.value = null
  hoverLayerId.value = null
  hoverCreateGroup.value = null
  plusHovering.value = false
  clearGapHoverHideTimer()
  if (attachedBoundary) {
    setGapHoverAtBoundary(
      attachedBoundary.track,
      attachedBoundary.fromClip,
      attachedBoundary.toClip,
      attachedBoundary.boundarySec,
      attachedBoundary.gapFrames
    )
  } else {
    gapHover.value = null
  }
  temporaryClipBounds.value = {}
  window.removeEventListener('pointermove', onClipDragMove)
  window.removeEventListener('pointerup', onClipDragEnd)
  window.removeEventListener('pointercancel', onClipDragEnd)
}

function onTrimMove(event: PointerEvent) {
  if (!trimState.value) return
  const state = trimState.value
  const deltaSeconds = (event.clientX - state.startX) / pxPerSecond.value
  const deltaFrames = toFrame(deltaSeconds, resolvedFps.value)
  const minDurationFrames = 1
  const clipEntry = findTrackForClip(state.clipId)
  if (!clipEntry) return
  const { track } = clipEntry
  const others = sortedTrackClips(track, state.clipId)
    .slice()
    .sort((left, right) => clipRange(left).startFrame - clipRange(right).startFrame)
  const originalRange = clipRangeFrames(state.originalStart, state.originalDuration, resolvedFps.value)
  const prev = others.filter((clip) => clipRange(clip).endFrame <= originalRange.startFrame).pop()
  const next = others.find((clip) => clipRange(clip).startFrame >= originalRange.endFrame)

  if (state.edge === 'start') {
    const maxStartFrame = originalRange.endFrame - minDurationFrames
    let nextStartFrame = Math.max(0, Math.min(maxStartFrame, originalRange.startFrame + deltaFrames))
    if (prev) {
      const prevEndFrame = clipRange(prev).endFrame
      nextStartFrame = Math.max(nextStartFrame, prevEndFrame)
    }
    nextStartFrame = Math.min(nextStartFrame, originalRange.endFrame - minDurationFrames)
    const nextDurationFrames = Math.max(minDurationFrames, originalRange.endFrame - nextStartFrame)
    temporaryClipBounds.value[state.clipId] = {
      startTime: toSec(nextStartFrame, resolvedFps.value),
      duration: durationFramesToSeconds(nextDurationFrames, resolvedFps.value),
    }
    return
  }

  let nextDurationFrames = Math.max(minDurationFrames, originalRange.durationFrames + deltaFrames)
  if (next) {
    const maxDurationFrames = Math.max(minDurationFrames, clipRange(next).startFrame - originalRange.startFrame)
    nextDurationFrames = Math.min(nextDurationFrames, maxDurationFrames)
  }
  temporaryClipBounds.value[state.clipId] = {
    startTime: state.originalStart,
    duration: durationFramesToSeconds(nextDurationFrames, resolvedFps.value),
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
  dragDiagnostics.value = null
  plusHovering.value = false
  clearGapHoverHideTimer()
  gapHover.value = null
  temporaryClipBounds.value = {}
  window.removeEventListener('pointermove', onTrimMove)
  window.removeEventListener('pointerup', onTrimEnd)
  window.removeEventListener('pointercancel', onTrimEnd)
}

function startPlayheadDrag(event: PointerEvent) {
  window.addEventListener('pointermove', onPlayheadDragMove)
  window.addEventListener('pointerup', stopPlayheadDrag)
  onPlayheadDragMove(event)
}

function onPlayheadDragMove(event: PointerEvent) {
  const viewport = viewportRef.value
  if (!viewport) return
  const rect = viewport.getBoundingClientRect()
  const x = event.clientX - rect.left - labelWidth + viewport.scrollLeft
  const raw = Math.max(0, Math.min(props.duration, x / pxPerSecond.value))
  const frame = Math.max(0, toFrame(raw, resolvedFps.value))
  emit('update:playhead', toSec(frame, resolvedFps.value))
}

function stopPlayheadDrag() {
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

function formatTickLabel(seconds: number, interval: number) {
  const safe = Math.max(0, seconds || 0)
  const minutes = Math.floor(safe / 60)
  const secs = Math.floor(safe % 60)
  if (interval >= 1) {
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }
  const hundredths = Math.floor((safe % 1) * 100)
  return `${minutes}:${secs.toString().padStart(2, '0')}.${hundredths.toString().padStart(2, '0')}`
}

const onGlobalPointerDown = (event: PointerEvent) => {
  if (transitionMenu.value.open && transitionMenuRef.value && !transitionMenuRef.value.contains(event.target as Node)) {
    closeTransitionMenu()
  }
  if (contextMenu.value.open && contextMenuRef.value && !contextMenuRef.value.contains(event.target as Node)) {
    closeContextMenu()
  }
}

const onGlobalKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') closeMenus()
}

onMounted(() => {
  window.addEventListener('pointerdown', onGlobalPointerDown)
  window.addEventListener('keydown', onGlobalKeyDown)
})

onBeforeUnmount(() => {
  clearGapHoverHideTimer()
  onTrimEnd()
  onClipDragEnd()
  stopPlayheadDrag()
  window.removeEventListener('pointerdown', onGlobalPointerDown)
  window.removeEventListener('keydown', onGlobalKeyDown)
})
</script>

<style scoped>
.tool-btn {
  height: 1.9rem;
  border-radius: 0.45rem;
  border: 1px solid #556152;
  background: #697565;
  color: #f5f5f5;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.9rem;
  font-size: 0.72rem;
  transition: color 150ms ease, border-color 150ms ease, background 150ms ease;
}

.tool-btn:hover {
  background: #7d9a7d;
  border-color: #697565;
}

.trim-handle {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 0.35rem;
  background: rgba(245, 245, 245, 0.95);
  cursor: ew-resize;
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

.snap-highlight {
  border-color: rgba(148, 255, 116, 0.95);
  background: rgba(148, 255, 116, 0.12);
  transition: background 140ms ease, border-color 140ms ease;
}

.transition-plus {
  transform: translate(-50%, -50%);
}

.transition-plus-btn {
  height: 1.6rem;
  width: 1.6rem;
  border-radius: 0.35rem;
  border: 1px solid rgba(240, 240, 240, 0.9);
  background: #f5f5f5;
  color: #1f1f1f;
  box-shadow: 0 6px 14px rgba(0, 0, 0, 0.35);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: transform 150ms ease, box-shadow 150ms ease;
}

.transition-plus-btn:hover {
  transform: none;
  box-shadow: 0 7px 15px rgba(0, 0, 0, 0.4);
}

.transition-plus-tooltip {
  position: absolute;
  left: 50%;
  bottom: 100%;
  transform: translate(-50%, -6px);
  padding: 0.2rem 0.45rem;
  border-radius: 0.35rem;
  background: rgba(12, 12, 12, 0.9);
  color: #f5f5f5;
  font-size: 0.68rem;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 150ms ease, transform 150ms ease;
}

.transition-plus:hover .transition-plus-tooltip {
  opacity: 1;
  transform: translate(-50%, -10px);
}

.timeline-container {
  container-type: inline-size;
}

@container (max-width: 700px) {
  .timeline-container :where(.text-xs) {
    font-size: 0.68rem;
  }

  .timeline-container :where(.text-sm) {
    font-size: 0.78rem;
  }
}
</style>
