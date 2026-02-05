<template>
  <aside class="h-full min-h-0 flex border-l border-surface-800 bg-surface-900">
    <section class="flex-1 min-w-0 min-h-0 flex flex-col panel-container">
      <div class="px-4 pt-4 pb-3 border-b border-surface-800">
        <div class="flex items-center justify-between">
          <h2 class="text-base font-normal text-surface-100 tracking-tight">{{ panelTitle }}</h2>
          <span class="text-xs text-surface-400 max-w-[140px] truncate" :title="selectedClip?.label">
            {{ selectedClip?.label || 'Clip' }}
          </span>
        </div>
      </div>

      <div class="min-h-0 overflow-y-auto p-4 space-y-4">
        <template v-if="activeTab === 'fade'">
          <div>
            <div class="mb-1 flex items-center justify-between text-sm text-surface-100">
              <span>Fade in</span>
              <input v-model.number="fadeIn" type="number" min="0" step="0.1" class="w-16 rounded bg-surface-950/60 border border-surface-800 px-2 py-1 text-right text-xs text-surface-100" />
            </div>
            <input v-model.number="fadeIn" type="range" min="0" max="5" step="0.1" class="w-full accent-primary-500" />
          </div>
          <div>
            <div class="mb-1 flex items-center justify-between text-sm text-surface-100">
              <span>Fade out</span>
              <input v-model.number="fadeOut" type="number" min="0" step="0.1" class="w-16 rounded bg-surface-950/60 border border-surface-800 px-2 py-1 text-right text-xs text-surface-100" />
            </div>
            <input v-model.number="fadeOut" type="range" min="0" max="5" step="0.1" class="w-full accent-primary-500" />
          </div>
          <button type="button" class="panel-action" @click="emitFade(true)">Apply fades</button>
        </template>

        <template v-else-if="activeTab === 'filters'">
          <div class="relative">
            <UiIcon name="Search" :size="15" class="absolute left-3 top-2.5 text-surface-500" />
            <input
              v-model="filterSearch"
              type="text"
              placeholder="Search filters"
              class="w-full rounded-md border border-surface-800 bg-surface-950/60 py-2 pl-9 pr-3 text-sm text-surface-100 placeholder:text-surface-500 focus:outline-none focus:border-primary-400"
            />
          </div>
          <div class="grid grid-cols-2 gap-2">
            <button
              v-for="preset in visibleFilterPresets"
              :key="preset.name"
              type="button"
              class="rounded-lg border p-2 text-left transition-colors"
              :class="selectedFilter === preset.name ? 'border-primary-500 bg-primary-500/15' : 'border-surface-800 bg-surface-950/60 hover:border-primary-400'"
              @click="selectFilter(preset.name)"
            >
              <div class="h-[clamp(2.5rem,7vw,4rem)] rounded-md mb-2" :style="{ background: preset.swatch }" />
              <p class="text-xs text-surface-100">{{ preset.name }}</p>
            </button>
          </div>
        </template>

        <template v-else-if="activeTab === 'speed'">
          <div class="flex items-center justify-between text-sm text-surface-100">
            <span>Speed</span>
            <input v-model.number="speedValue" type="number" min="0.1" max="16" step="0.1" class="w-16 rounded bg-surface-950/60 border border-surface-800 px-2 py-1 text-right text-xs text-surface-100" />
          </div>
          <input v-model.number="speedValue" type="range" min="0.1" max="4" step="0.1" class="w-full accent-primary-500" />
          <div class="grid grid-cols-5 gap-1">
            <button
              v-for="value in speedPresets"
              :key="value"
              type="button"
              class="rounded border px-1 py-1 text-xs transition-colors"
              :class="Math.abs(speedValue - value) < 0.05 ? 'border-primary-500 bg-primary-500/15 text-surface-50' : 'border-surface-800 bg-surface-950/60 text-surface-100 hover:border-primary-400'"
              @click="speedValue = value"
            >
              {{ value }}x
            </button>
          </div>
          <button type="button" class="panel-action" @click="emitSpeed(true)">Apply speed</button>
        </template>

        <template v-else-if="activeTab === 'adjust'">
          <div class="space-y-3">
            <div v-for="field in colorFields" :key="field.key">
              <div class="mb-1 flex items-center justify-between text-sm text-surface-100">
                <span>{{ field.label }}</span>
                <span class="text-xs text-surface-400">{{ field.value.toFixed(2) }}</span>
              </div>
              <input
                :value="field.value"
                type="range"
                :min="field.min"
                :max="field.max"
                :step="field.step"
                class="w-full accent-primary-500"
                @input="onColorInput(field.key, $event)"
              />
            </div>
          </div>
          <button type="button" class="panel-action" @click="emitAdjustColor(true)">Apply colour</button>
        </template>

        <template v-else-if="activeTab === 'aspect'">
          <p class="text-sm text-surface-100">Aspect ratio</p>
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="ratio in aspectRatios"
              :key="ratio.value"
              type="button"
              class="rounded border px-2 py-1.5 text-xs transition-colors"
              :class="selectedAspectRatio === ratio.value ? 'border-primary-500 bg-primary-500/15 text-surface-50' : 'border-surface-800 bg-surface-950/60 text-surface-100 hover:border-primary-400'"
              @click="selectedAspectRatio = ratio.value"
            >
              {{ ratio.value }}
            </button>
          </div>
          <p class="text-sm text-surface-100 mt-3">Fit mode</p>
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="mode in fitModes"
              :key="mode"
              type="button"
              class="rounded border px-2 py-1.5 text-xs transition-colors capitalize"
              :class="fitMode === mode ? 'border-primary-500 bg-primary-500/15 text-surface-50' : 'border-surface-800 bg-surface-950/60 text-surface-100 hover:border-primary-400'"
              @click="fitMode = mode"
            >
              {{ mode }}
            </button>
          </div>
          <button type="button" class="panel-action mt-3" @click="emitAspect(true)">Apply ratio</button>
        </template>

        <template v-else-if="activeTab === 'shape'">
          <div class="space-y-3">
            <label class="text-sm text-surface-100 block">Colour</label>
            <input v-model="shapeColor" type="color" class="h-10 w-full rounded bg-surface-950/60 border border-surface-800 p-1" />
            <label class="inline-flex items-center justify-between w-full rounded-md border border-surface-800 bg-surface-950/60 px-3 py-2 text-sm text-surface-100">
              <span>Outline</span>
              <input v-model="shapeOutline" type="checkbox" class="accent-primary-500" />
            </label>
          </div>
          <button type="button" class="panel-action" @click="emitShape">Apply shape style</button>
        </template>

        <template v-else>
          <div class="rounded-lg border border-dashed border-surface-800 p-4 text-sm text-surface-400">
            {{ panelTitle }} controls will appear here.
          </div>
        </template>
      </div>
    </section>

    <nav class="w-14 shrink-0 border-l border-surface-800 py-2">
      <button
        v-for="item in tabItems"
        :key="item.key"
        type="button"
        class="mx-1 mb-1.5 flex w-12 flex-col items-center gap-1 rounded-xl px-1 py-2 text-[10px] leading-tight transition-all"
        :class="item.key === activeTab ? 'bg-surface-800 text-surface-50 shadow-[inset_0_0_0_1px_rgba(105,117,101,.5)]' : 'text-surface-400 hover:bg-surface-800 hover:text-surface-100'"
        @click="$emit('update:activeTab', item.key)"
      >
        <UiIcon :name="item.icon" :size="18" />
        <span class="w-full text-center whitespace-normal break-words">{{ item.label }}</span>
      </button>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { computed, ref, toRefs, watch } from 'vue'
import type { EditorClip, EditorFitMode } from '~/composables/useEditorState'

interface Props {
  activeTab: string
  selectedClip?: EditorClip | null
}

const props = withDefaults(defineProps<Props>(), {
  selectedClip: null,
})

const {
  activeTab,
  selectedClip,
} = toRefs(props)

const emit = defineEmits<{
  'update:activeTab': [tab: string]
  'apply:fade': [{ fadeIn: number; fadeOut: number; commit?: boolean }]
  'apply:filter': [{ preset: string; commit?: boolean }]
  'apply:speed': [{ speed: number; commit?: boolean }]
  'apply:color': [{ brightness: number; contrast: number; saturation: number; gamma: number; commit?: boolean }]
  'apply:aspect': [{ ratio: string; fitMode: EditorFitMode; width: number; height: number; commit?: boolean }]
  'apply:shape': [{ color: string; outline: boolean; commit?: boolean }]
}>()

const tabItems = [
  { key: 'captions', label: 'Captions', icon: 'Captions' },
  { key: 'audio', label: 'Audio', icon: 'AudioLines' },
  { key: 'fade', label: 'Fade', icon: 'Blend' },
  { key: 'filters', label: 'Filters', icon: 'CircleEllipsis' },
  { key: 'effects', label: 'Effects', icon: 'WandSparkles' },
  { key: 'adjust', label: 'Adjust', icon: 'SlidersHorizontal' },
  { key: 'speed', label: 'Speed', icon: 'Gauge' },
  { key: 'shape', label: 'Shape', icon: 'Shapes' },
  { key: 'aspect', label: 'Ratio', icon: 'Ratio' },
]

const fadeIn = ref(0)
const fadeOut = ref(0)
const speedValue = ref(1)
const filterSearch = ref('')
const selectedFilter = ref('None')
const shapeColor = ref('#8f8cae')
const shapeOutline = ref(false)

const brightness = ref(0)
const contrast = ref(1)
const saturation = ref(1)
const gamma = ref(1)
const selectedAspectRatio = ref('16:9')
const fitMode = ref<EditorFitMode>('fit')
const syncing = ref(false)

const speedPresets = [0.1, 1, 2, 4, 16]
const fitModes: EditorFitMode[] = ['fit', 'fill', 'stretch']

const aspectRatios = [
  { value: '16:9', width: 1920, height: 1080 },
  { value: '9:16', width: 1080, height: 1920 },
  { value: '1:1', width: 1080, height: 1080 },
  { value: '4:5', width: 1080, height: 1350 },
  { value: '4:3', width: 1440, height: 1080 },
  { value: '21:9', width: 2520, height: 1080 },
]

const filterPresets = [
  { name: 'None', swatch: 'linear-gradient(135deg,#0f1a32,#23407a)' },
  { name: 'Retro', swatch: 'linear-gradient(135deg,#3f362f,#8f7a61)' },
  { name: 'Orange and teal', swatch: 'linear-gradient(135deg,#db7c2b,#2da1b0)' },
  { name: 'Bold and blue', swatch: 'linear-gradient(135deg,#1d4ed8,#0f172a)' },
  { name: 'Golden hour', swatch: 'linear-gradient(135deg,#f59e0b,#f97316)' },
  { name: 'Vibrant vlogger', swatch: 'linear-gradient(135deg,#7c3aed,#0ea5e9)' },
  { name: 'Purple undertone', swatch: 'linear-gradient(135deg,#4c1d95,#312e81)' },
  { name: 'Winter sunset', swatch: 'linear-gradient(135deg,#0ea5e9,#f97316)' },
  { name: '35mm', swatch: 'linear-gradient(135deg,#334155,#0f172a)' },
  { name: 'Contrast', swatch: 'linear-gradient(135deg,#111827,#6b7280)' },
  { name: 'Autumn', swatch: 'linear-gradient(135deg,#7c2d12,#f59e0b)' },
  { name: 'Winter', swatch: 'linear-gradient(135deg,#1e3a8a,#93c5fd)' },
]

const visibleFilterPresets = computed(() => {
  const q = filterSearch.value.trim().toLowerCase()
  if (!q) return filterPresets
  return filterPresets.filter((entry) => entry.name.toLowerCase().includes(q))
})

const panelTitle = computed(() => {
  return tabItems.find((item) => item.key === activeTab.value)?.label ?? 'Properties'
})

const colorFields = computed(() => [
  { key: 'brightness', label: 'Brightness', value: brightness.value, min: -1, max: 1, step: 0.05 },
  { key: 'contrast', label: 'Contrast', value: contrast.value, min: 0, max: 3, step: 0.05 },
  { key: 'saturation', label: 'Saturation', value: saturation.value, min: 0, max: 3, step: 0.05 },
  { key: 'gamma', label: 'Gamma', value: gamma.value, min: 0.1, max: 3, step: 0.05 },
])

watch(
  selectedClip,
  (clip) => {
    if (!clip) return
    syncing.value = true
    fadeIn.value = clip.effects?.fadeIn ?? fadeIn.value
    fadeOut.value = clip.effects?.fadeOut ?? fadeOut.value
    speedValue.value = clip.effects?.speed ?? speedValue.value
    selectedFilter.value = clip.effects?.filter ?? selectedFilter.value
    shapeColor.value = clip.style?.color ?? shapeColor.value
    shapeOutline.value = clip.style?.outline ?? shapeOutline.value
    selectedAspectRatio.value = clip.aspectRatio ?? selectedAspectRatio.value
    fitMode.value = clip.fitMode ?? fitMode.value
    brightness.value = clip.effects?.brightness ?? brightness.value
    contrast.value = clip.effects?.contrast ?? contrast.value
    saturation.value = clip.effects?.saturation ?? saturation.value
    gamma.value = clip.effects?.gamma ?? gamma.value
    requestAnimationFrame(() => {
      syncing.value = false
    })
  },
  { immediate: true }
)

watch([fadeIn, fadeOut], () => {
  if (syncing.value) return
  emitFade()
})

watch(speedValue, () => {
  if (syncing.value) return
  emitSpeed()
})

watch(selectedFilter, () => {
  if (syncing.value) return
  emit('apply:filter', { preset: selectedFilter.value, commit: false })
})

watch([brightness, contrast, saturation, gamma], () => {
  if (syncing.value) return
  emitAdjustColor()
})

watch([selectedAspectRatio, fitMode], () => {
  if (syncing.value) return
  emitAspect()
})

watch([shapeColor, shapeOutline], () => {
  if (syncing.value) return
  emitShape()
})

function emitFade(commit = false) {
  emit('apply:fade', { fadeIn: Number(fadeIn.value) || 0, fadeOut: Number(fadeOut.value) || 0, commit })
}

function emitSpeed(commit = false) {
  emit('apply:speed', { speed: Number(speedValue.value) || 1, commit })
}

function selectFilter(name: string) {
  selectedFilter.value = name
  emit('apply:filter', { preset: name, commit: false })
}

function updateColorField(key: string, value: number) {
  if (key === 'brightness') brightness.value = value
  if (key === 'contrast') contrast.value = value
  if (key === 'saturation') saturation.value = value
  if (key === 'gamma') gamma.value = value
}

function onColorInput(key: string, event: Event) {
  const target = event.target as HTMLInputElement | null
  updateColorField(key, Number(target?.value ?? 0))
}

function emitAdjustColor(commit = false) {
  emit('apply:color', {
    brightness: brightness.value,
    contrast: contrast.value,
    saturation: saturation.value,
    gamma: gamma.value,
    commit,
  })
}

function emitAspect(commit = false) {
  const selectedRatio = aspectRatios.find((ratio) => ratio.value === selectedAspectRatio.value) ?? aspectRatios[0]
  emit('apply:aspect', {
    ratio: selectedRatio.value,
    fitMode: fitMode.value,
    width: selectedRatio.width,
    height: selectedRatio.height,
    commit,
  })
}

function emitShape(commit = false) {
  emit('apply:shape', {
    color: shapeColor.value,
    outline: shapeOutline.value,
    commit,
  })
}
</script>

<style scoped>
.panel-action {
  width: 100%;
  border-radius: 0.5rem;
  border: 1px solid #556152;
  background: #697565;
  color: #f5f5f5;
  font-size: 0.82rem;
  font-weight: 400;
  padding: 0.58rem 0.75rem;
  transition: filter 150ms ease, border-color 150ms ease;
}

.panel-action:hover {
  filter: brightness(1.05);
  border-color: #7d9a7d;
}

.panel-container {
  container-type: inline-size;
}

@container (max-width: 220px) {
  .panel-container :where(.text-lg) {
    font-size: 0.95rem;
  }
  .panel-container :where(.text-base) {
    font-size: 0.88rem;
  }
  .panel-container :where(.text-sm) {
    font-size: 0.78rem;
  }
  .panel-container :where(.text-xs) {
    font-size: 0.68rem;
  }
}

@container (min-width: 300px) {
  .panel-container :where(.text-base) {
    font-size: 1rem;
  }
}
</style>
