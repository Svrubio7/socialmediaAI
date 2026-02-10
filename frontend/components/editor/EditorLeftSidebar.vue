<template>
  <aside class="h-full min-h-0 flex border-r border-surface-800 bg-surface-900">
    <nav class="w-[4.2rem] shrink-0 border-r border-surface-800 py-2">
      <button
        v-for="item in navItems"
        :key="item.key"
        type="button"
        class="mx-1 mb-1.5 flex w-[3.6rem] flex-col items-center gap-1 rounded-xl px-1 py-2 text-[10px] leading-tight transition-all"
        :class="item.key === activeSection ? 'bg-surface-800 text-surface-50 shadow-[inset_0_0_0_1px_rgba(105,117,101,.5)]' : 'text-surface-400 hover:bg-surface-800 hover:text-surface-100'"
        @click="$emit('update:activeSection', item.key)"
      >
        <UiIcon :name="item.icon" :size="18" />
        <span class="w-full text-center whitespace-normal break-words">{{ item.label }}</span>
      </button>
    </nav>

    <section
      v-if="!collapsed"
      class="flex-1 min-w-0 min-h-0 flex flex-col panel-container"
    >
      <div class="flex items-center justify-between px-4 pt-4 pb-3">
        <h2 class="text-base font-normal text-surface-100 tracking-tight">{{ sectionTitle }}</h2>
        <button
          type="button"
          class="h-8 w-8 rounded-md cream-btn transition-colors"
          aria-label="Panel options"
        >
          <UiIcon name="PanelLeft" :size="15" class="mx-auto" />
        </button>
      </div>

      <div class="px-4 pb-3" v-if="showSearch">
        <div class="relative">
          <UiIcon name="Search" :size="15" class="absolute left-3 top-2.5 text-surface-500" />
          <input
            v-model="searchQuery"
            type="text"
            class="w-full rounded-md border border-surface-800 bg-surface-950/60 py-2 pl-9 pr-3 text-sm text-surface-100 placeholder:text-surface-500 focus:outline-none focus:border-primary-400"
            :placeholder="searchPlaceholder"
          />
        </div>
      </div>

      <div class="min-h-0 overflow-y-auto px-4 pb-4 space-y-4">
        <template v-if="activeSection === 'media'">
          <button
            type="button"
            class="w-full inline-flex items-center justify-center gap-2 rounded-md cream-btn px-3 py-2.5 text-sm font-normal transition-colors"
            @click="$emit('import-media')"
          >
            <UiIcon name="Upload" :size="15" />
            Import media
            <UiIcon name="ChevronDown" :size="15" />
          </button>

          <div v-if="filteredMediaItems.length === 0" class="rounded-lg border border-dashed border-surface-800 p-4 text-xs text-surface-500">
            Your media library is empty.
          </div>

          <button
            v-for="item in filteredMediaItems"
            :key="item.id"
            type="button"
            class="w-full rounded-lg border border-surface-800 bg-surface-950/60 p-2 text-left hover:border-primary-400 transition-colors"
            @click="$emit('add-media', item)"
          >
            <div class="aspect-video rounded-md overflow-hidden bg-surface-800 mb-2 relative">
              <img v-if="item.thumbnail" :src="item.thumbnail" :alt="item.name" class="w-full h-full object-cover" />
              <div v-else class="w-full h-full flex items-center justify-center text-surface-500">
                <UiIcon :name="item.type === 'audio' ? 'Music2' : item.type === 'image' ? 'Image' : 'Video'" :size="22" />
              </div>
              <span v-if="item.duration" class="absolute left-1.5 bottom-1.5 rounded bg-black/70 px-1.5 py-0.5 text-[10px] text-white">
                {{ formatDuration(item.duration) }}
              </span>
            </div>
            <p class="truncate text-xs font-normal text-surface-100">{{ item.name }}</p>
          </button>
        </template>

        <template v-else-if="activeSection === 'text'">
          <div class="space-y-3">
            <button
              v-for="style in textStyles"
              :key="style.name"
              type="button"
              class="w-full rounded-lg border border-surface-800 bg-surface-950/60 p-3 text-left hover:border-primary-400 transition-colors"
              @click="$emit('add-text', style.name)"
            >
              <div class="h-[clamp(2.5rem,7vw,4rem)] rounded-md mb-2 flex items-center justify-center font-normal tracking-tight" :class="style.previewClass">
                {{ style.preview }}
              </div>
              <p class="text-xs text-surface-100">{{ style.name }}</p>
            </button>
          </div>
        </template>

        <template v-else-if="activeSection === 'transitions'">
          <div class="rounded-lg border border-surface-800 bg-surface-950/60 p-3 text-sm text-surface-100">
            Drag a transition between clips on the timeline.
          </div>
          <div class="space-y-2">
            <p class="text-xs uppercase tracking-wide text-surface-100">Fades &amp; blurs</p>
            <button
              v-for="transition in transitionItems"
              :key="transition"
              type="button"
              class="w-full rounded-lg border border-surface-800 bg-surface-800 px-3 py-2.5 text-left text-sm text-surface-50 hover:border-primary-400 transition-colors"
              @click="$emit('add-transition', transition)"
            >
              {{ transition }}
            </button>
          </div>
          <div class="space-y-2">
            <p class="text-xs uppercase tracking-wide text-surface-100">Wipes</p>
            <button
              v-for="transition in wipeTransitionItems"
              :key="transition"
              type="button"
              class="w-full rounded-lg border border-surface-800 bg-surface-800 px-3 py-2.5 text-left text-sm text-surface-50 hover:border-primary-400 transition-colors"
              @click="$emit('add-transition', transition)"
            >
              {{ transition }}
            </button>
          </div>
        </template>

        <template v-else-if="activeSection === 'graphics'">
          <p class="text-xs uppercase tracking-wide text-surface-100">Shapes</p>
          <div class="grid grid-cols-2 gap-2">
            <button
              v-for="shape in shapeItems"
              :key="shape"
              type="button"
              class="rounded-lg border border-surface-800 bg-surface-950/60 px-3 py-5 text-xs text-surface-100 hover:border-primary-400 transition-colors"
              @click="$emit('add-shape', shape)"
            >
              {{ shape }}
            </button>
          </div>
        </template>

        <template v-else-if="activeSection === 'templates'">
          <button
            v-for="template in templateItems"
            :key="template"
            type="button"
            class="w-full rounded-lg border border-surface-800 bg-surface-800 px-3 py-6 text-left text-sm font-normal text-surface-50 hover:border-primary-400 transition-colors"
          >
            {{ template }}
          </button>
        </template>

        <template v-else-if="activeSection === 'stock-images'">
          <div
            v-for="collection in stockCollections"
            :key="collection"
            class="rounded-lg border border-surface-800 bg-surface-950/60 p-3"
          >
            <div class="mb-2 flex items-center justify-between">
              <p class="text-sm font-normal text-surface-100">{{ collection }}</p>
              <UiIcon name="ChevronRight" :size="14" class="text-surface-500" />
            </div>
            <div class="grid grid-cols-3 gap-2">
              <div v-for="i in 3" :key="`${collection}-${i}`" class="aspect-square rounded-md bg-surface-800" />
            </div>
          </div>
        </template>

        <template v-else>
          <div class="rounded-lg border border-dashed border-surface-800 p-4 text-xs text-surface-500">
            Content for {{ sectionTitle }} will appear here.
          </div>
        </template>
      </div>
    </section>
  </aside>
</template>

<script setup lang="ts">
import { computed, ref, toRefs } from 'vue'

interface MediaItem {
  id: string
  name: string
  type: 'video' | 'image' | 'audio'
  thumbnail?: string
  duration?: number
  storagePath?: string
  sourceUrl?: string
  sourceId?: string
}

interface Props {
  activeSection: string
  collapsed?: boolean
  mediaItems?: MediaItem[]
}

const props = withDefaults(defineProps<Props>(), {
  collapsed: false,
  mediaItems: () => [],
})

const {
  activeSection,
  collapsed,
  mediaItems,
} = toRefs(props)

defineEmits<{
  'update:activeSection': [section: string]
  'import-media': []
  'add-media': [item: MediaItem]
  'add-text': [styleName: string]
  'add-shape': [shapeName: string]
  'add-transition': [transitionName: string]
}>()

const searchQuery = ref('')

const navItems = [
  { key: 'media', label: 'Media', icon: 'FolderOpen' },
  { key: 'record', label: 'Record', icon: 'Video' },
  { key: 'text', label: 'Text', icon: 'Type' },
  { key: 'music', label: 'Music', icon: 'Music' },
  { key: 'stock-video', label: 'Stock', icon: 'Clapperboard' },
  { key: 'stock-images', label: 'Images', icon: 'Image' },
  { key: 'templates', label: 'Templates', icon: 'LayoutTemplate' },
  { key: 'graphics', label: 'Graphics', icon: 'Shapes' },
  { key: 'transitions', label: 'Transitions', icon: 'Blend' },
  { key: 'brand-kit', label: 'Brand', icon: 'Palette' },
]

const textStyles = [
  { name: 'Plain text', preview: 'Text', previewClass: 'bg-black text-white text-xl' },
  { name: 'Creator', preview: 'CREATOR', previewClass: 'bg-[#2d3457] text-white text-lg' },
  { name: 'Text box', preview: 'Text box', previewClass: 'bg-[#f8fafc] text-slate-900 text-lg' },
  { name: 'Bubble', preview: 'Bubble', previewClass: 'bg-[#94ff74] text-[#1f2a19] text-lg' },
]

const transitionItems = ['Cross fade', 'Cross blur', 'Burn', 'Horizontal band']
const wipeTransitionItems = [
  'Hard wipe down',
  'Hard wipe up',
  'Hard wipe left',
  'Hard wipe right',
  'Soft wipe down',
  'Soft wipe up',
  'Soft wipe left',
  'Soft wipe right',
  'Diagonal soft wipe',
  'Blinds',
  'Barn doors - vertical',
  'Barn doors - horizontal',
  'Circular wipe',
  'Close',
]
const shapeItems = ['Square', 'Circle', 'Outline', 'Arrow']
const templateItems = ['All templates', 'YouTube', 'Instagram', 'Gaming', 'Corporate']
const stockCollections = ['Paper', 'Scenery', 'Working', 'Photography']

const sectionTitle = computed(() => {
  const item = navItems.find((entry) => entry.key === activeSection.value)
  return item ? item.label : 'Library'
})

const showSearch = computed(() => ['media', 'text', 'transitions', 'stock-images'].includes(activeSection.value))

const searchPlaceholder = computed(() => {
  if (activeSection.value === 'media') return 'Search media'
  if (activeSection.value === 'transitions') return 'Search transitions'
  if (activeSection.value === 'stock-images') return 'Search images'
  return 'Search'
})

const filteredMediaItems = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) return mediaItems.value
  return mediaItems.value.filter((item) => item.name.toLowerCase().includes(query))
})

function formatDuration(seconds: number) {
  const total = Math.max(0, Math.floor(seconds))
  const minutes = Math.floor(total / 60)
  const secs = total % 60
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}
</script>

<style scoped>
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
