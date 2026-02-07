<template>
  <header class="editor-header h-14 border-b border-surface-800 bg-surface-950/95 px-3 lg:px-4 backdrop-blur">
    <div class="h-full flex items-center justify-between gap-3">
      <div class="flex items-center gap-2 min-w-0">
        <button
          type="button"
          class="h-9 w-9 rounded-lg cream-btn transition-colors"
          @click="$emit('toggle-left')"
          aria-label="Toggle left sidebar"
        >
          <UiIcon name="Menu" :size="18" class="mx-auto" />
        </button>
        <button
          type="button"
          class="inline-flex items-center gap-2 rounded-lg px-2.5 py-1.5 cream-btn transition-colors"
          @click="$emit('go-home')"
        >
          <div class="h-6 w-6 rounded-md bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center">
            <span class="text-sm font-normal text-surface-950">E</span>
          </div>
          <span class="text-sm font-normal text-surface-900">Elevo<span class="text-primary-400">AI</span></span>
        </button>
        <input
          v-model="localProjectName"
          type="text"
          class="hidden sm:block w-44 lg:w-56 rounded-md border border-surface-800 bg-surface-900 px-3 py-1.5 text-sm text-surface-100 placeholder:text-surface-500 focus:outline-none focus:border-primary-400 transition-colors"
          placeholder="Untitled project"
          @blur="emitName"
          @keydown.enter.prevent="emitName"
        />
        <div class="hidden lg:inline-flex items-center gap-1 text-xs text-surface-400 ml-1">
          <UiIcon :name="saveIcon" :size="14" :class="saveIconClass" />
          <span>{{ saveLabel }}</span>
        </div>
      </div>

      <div class="hidden md:flex items-center gap-1">
        <button
          type="button"
          class="h-8 w-8 rounded-md transition-colors"
          :class="canUndoRef ? 'cream-btn' : 'cream-btn opacity-50 cursor-not-allowed'"
          :disabled="!canUndoRef"
          @click="$emit('undo')"
          aria-label="Undo"
        >
          <UiIcon name="Undo2" :size="15" class="mx-auto" />
        </button>
        <button
          type="button"
          class="h-8 w-8 rounded-md transition-colors"
          :class="canRedoRef ? 'cream-btn' : 'cream-btn opacity-50 cursor-not-allowed'"
          :disabled="!canRedoRef"
          @click="$emit('redo')"
          aria-label="Redo"
        >
          <UiIcon name="Redo2" :size="15" class="mx-auto" />
        </button>
      </div>

      <div class="flex items-center gap-2">
        <button
          type="button"
          class="inline-flex items-center gap-1.5 rounded-md cream-btn px-3 py-1.5 text-sm font-normal transition-colors"
          @click="$emit('export')"
        >
          <UiIcon name="ArrowUpToLine" :size="14" />
          Export
          <UiIcon name="ChevronDown" :size="14" />
        </button>
        <button
          type="button"
          class="hidden sm:flex h-8 w-8 items-center justify-center rounded-md cream-btn transition-colors"
          @click="$emit('help')"
          aria-label="Help"
        >
          <UiIcon name="HelpCircle" :size="15" />
        </button>
        <button
          type="button"
          class="hidden sm:flex h-8 w-8 items-center justify-center rounded-md cream-btn transition-colors"
          @click="$emit('feedback')"
          aria-label="Feedback"
        >
          <UiIcon name="MessageCircle" :size="15" />
        </button>
        <button
          type="button"
          class="h-8 w-8 rounded-full cream-btn text-sm font-normal"
          @click="$emit('account')"
        >
          {{ accountInitialRef }}
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, ref, toRefs, watch } from 'vue'

interface Props {
  projectName: string
  accountInitial?: string
  saveState?: 'saved' | 'saving' | 'error'
  canUndo?: boolean
  canRedo?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  accountInitial: 'S',
  saveState: 'saved',
  canUndo: false,
  canRedo: false,
})

const emit = defineEmits<{
  'update:projectName': [value: string]
  'toggle-left': []
  'go-home': []
  undo: []
  redo: []
  export: []
  help: []
  feedback: []
  account: []
}>()

const {
  accountInitial: accountInitialRef,
  canUndo: canUndoRef,
  canRedo: canRedoRef,
} = toRefs(props)

const localProjectName = ref(props.projectName)

watch(
  () => props.projectName,
  (next) => {
    if (next !== localProjectName.value) localProjectName.value = next
  }
)

const saveIcon = computed(() => {
  if (props.saveState === 'saving') return 'CloudUpload'
  if (props.saveState === 'error') return 'CircleAlert'
  return 'CloudCheck'
})

const saveIconClass = computed(() => {
  if (props.saveState === 'saving') return 'text-accent-200 animate-pulse'
  if (props.saveState === 'error') return 'text-red-400'
  return 'text-primary-400'
})

const saveLabel = computed(() => {
  if (props.saveState === 'saving') return 'Saving...'
  if (props.saveState === 'error') return 'Save failed'
  return 'Saved'
})

function emitName() {
  emit('update:projectName', localProjectName.value)
}
</script>
