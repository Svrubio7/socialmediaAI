<template>
  <div class="container-wide py-6 lg:py-8">
    <NuxtLink
      :to="localePath('/dashboard')"
      class="inline-flex items-center gap-2 text-sm text-surface-400 hover:text-surface-200 mb-5 transition-colors"
    >
      <UiIcon name="ArrowLeft" :size="14" />
      Back to Dashboard
    </NuxtLink>

    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
      <div>
        <h1 class="text-xl lg:text-2xl font-mono font-normal text-surface-100">Video Editor</h1>
        <p class="text-surface-400 mt-1 text-sm">Edit and generate videos with timelines, layers, and templates</p>
      </div>
      <div class="flex flex-wrap items-center gap-3">
        <select
          v-model="selectedVideoId"
          class="input w-auto min-w-[180px] text-sm py-2.5"
          :disabled="videosLoading"
          @change="onVideoSelect"
        >
          <option value="">{{ videosLoading ? 'Loading...' : 'Choose video...' }}</option>
          <option v-for="v in videoList" :key="v.id" :value="v.id">
            {{ v.original_filename || v.filename }} ({{ formatDuration(v.duration) }})
          </option>
        </select>
        <UiButton variant="primary" :to="localePath('/videos')">
          <template #icon-left><UiIcon name="Upload" :size="16" /></template>
          Upload
        </UiButton>
      </div>
    </div>

    <!-- Timeline + ops (CapCut-like minimal UI) -->
    <UiCard class="border border-accent-500/20 bg-surface-700/30 dark:bg-surface-700/40 rounded-2xl mb-8">
      <div v-if="!selectedVideoId" class="min-h-[260px] flex flex-col items-center justify-center gap-5 text-center px-4">
        <div class="w-12 h-12 rounded-xl bg-accent-500/20 flex items-center justify-center">
          <UiIcon name="Scissors" :size="24" class="text-accent-400" />
        </div>
        <p class="text-surface-400 text-sm">Select a video to trim, reverse, duplicate, or export.</p>
        <UiButton variant="secondary" :to="localePath('/videos')">
          <template #icon-left><UiIcon name="Video" :size="16" /></template>
          Browse videos
        </UiButton>
      </div>
      <template v-else>
        <!-- Single-track timeline -->
        <div class="mb-5">
          <h3 class="text-xs font-mono font-medium text-surface-400 mb-1.5">Track 1</h3>
          <div class="h-12 rounded-xl bg-surface-600/30 dark:bg-surface-600/40 border border-surface-600/60 flex items-center px-3 overflow-x-auto">
            <div
              class="h-8 rounded-lg flex items-center gap-2 flex-shrink-0 px-3 font-medium text-surface-200 text-sm"
              :style="{ minWidth: clipWidth + 'px' }"
            >
              <UiIcon name="Video" :size="16" class="text-accent-400" />
              <span class="truncate">{{ selectedVideoName }}</span>
              <span class="text-surface-500 text-xs">{{ formatDuration(selectedDuration) }}</span>
            </div>
          </div>
        </div>
        <!-- Trim -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-5">
          <div>
            <label class="label text-sm">Trim start (s)</label>
            <UiInput v-model.number="trimStart" type="number" min="0" :max="selectedDuration" step="0.1" />
          </div>
          <div>
            <label class="label text-sm">Trim end (s)</label>
            <UiInput v-model.number="trimEnd" type="number" :min="trimStart" :max="selectedDuration" step="0.1" />
          </div>
        </div>
        <!-- Op buttons -->
        <div class="flex flex-wrap gap-3">
          <UiButton variant="secondary" size="sm" :disabled="opRunning" class="rounded-xl" @click="runOp('trim_clip')">
            <template #icon-left><UiIcon name="Scissors" :size="14" /></template>
            Apply trim
          </UiButton>
          <UiButton variant="secondary" size="sm" :disabled="opRunning" class="rounded-xl" @click="runOp('reverse_clip')">
            <template #icon-left><UiIcon name="RotateCcw" :size="14" /></template>
            Reverse
          </UiButton>
          <UiButton variant="secondary" size="sm" :disabled="opRunning" class="rounded-xl" @click="runOp('duplicate_clip')">
            <template #icon-left><UiIcon name="Copy" :size="14" /></template>
            Duplicate
          </UiButton>
          <UiButton variant="primary" size="sm" :disabled="opRunning" class="rounded-xl" @click="runOp('export_video')">
            <template #icon-left><UiIcon name="Download" :size="14" /></template>
            Export
          </UiButton>
        </div>
        <p v-if="opError" class="mt-3 text-sm text-red-400">{{ opError }}</p>
      </template>
    </UiCard>

    <!-- Edit templates (content library) -->
    <UiCard class="border-l-4 border-l-accent-500 border border-accent-500/20 bg-surface-700/30 dark:bg-surface-700/40 rounded-2xl">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-5">
        <h2 class="text-base font-mono font-medium text-surface-100">Edit templates</h2>
        <UiButton variant="secondary" size="sm" class="rounded-xl" @click="showCreateTemplate = true">
          <template #icon-left><UiIcon name="Plus" :size="14" /></template>
          Create template
        </UiButton>
      </div>
      <div v-if="templatesLoading" class="py-10 flex justify-center">
        <div class="flex flex-col items-center gap-3">
          <UiSkeleton variant="rounded" width="64px" height="64px" />
          <UiSkeleton variant="text" width="140px" />
        </div>
      </div>
      <SharedEmptyState
        v-else-if="editTemplates.length === 0"
        icon="FileStack"
        title="No edit templates yet"
        description="Create reusable edit styles to apply to raw footage"
        action-label="Create template"
        action-icon="Plus"
        variant="primary"
        @action="showCreateTemplate = true"
      />
      <div v-else class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="t in editTemplates"
          :key="t.id"
          class="p-4 rounded-xl bg-surface-600/25 dark:bg-surface-600/30 border border-surface-600/50 flex flex-col"
        >
          <div class="flex items-center gap-3 mb-2">
            <div class="w-9 h-9 rounded-lg bg-accent-500/20 flex items-center justify-center flex-shrink-0">
              <UiIcon name="FileStack" :size="18" class="text-accent-400" />
            </div>
            <div class="min-w-0 flex-1">
              <p class="font-medium text-surface-100 truncate text-sm">{{ t.name }}</p>
              <p v-if="t.description" class="text-surface-500 text-xs truncate">{{ t.description }}</p>
            </div>
          </div>
          <div class="mt-auto pt-3 flex flex-wrap gap-2">
            <UiButton
              v-if="selectedVideoId"
              variant="secondary"
              size="sm"
              class="rounded-xl"
              :disabled="applyingTemplate === t.id"
              @click="applyTemplate(t.id)"
            >
              <template #icon-left><UiIcon name="Play" :size="14" /></template>
              Apply
            </UiButton>
            <UiButton
              variant="ghost"
              size="sm"
              class="rounded-xl text-red-400 hover:text-red-300 hover:bg-red-500/10"
              :disabled="deletingTemplate === t.id"
              @click="deleteTemplate(t.id)"
            >
              <template #icon-left><UiIcon name="Trash2" :size="14" /></template>
              Delete
            </UiButton>
          </div>
        </div>
      </div>
    </UiCard>

    <!-- Create edit template modal -->
    <UiModal v-model="showCreateTemplate" title="Create edit template" size="md">
      <form @submit.prevent="createTemplate" class="space-y-4">
        <div>
          <label class="label text-sm">Name</label>
          <UiInput v-model="newTemplateName" placeholder="e.g. TikTok fast cuts" required />
        </div>
        <div>
          <label class="label text-sm">Description (optional)</label>
          <UiInput v-model="newTemplateDescription" placeholder="Short description of this edit style" />
        </div>
        <div class="flex justify-end gap-3 pt-2">
          <UiButton variant="ghost" type="button" class="rounded-xl" @click="showCreateTemplate = false">Cancel</UiButton>
          <UiButton variant="primary" type="submit" class="rounded-xl" :disabled="creatingTemplate">
            {{ creatingTemplate ? 'Creating…' : 'Create' }}
          </UiButton>
        </div>
      </form>
    </UiModal>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
definePageMeta({
  layout: 'app-sidebar',
  middleware: 'auth',
})

const route = useRoute()
const localePath = useLocalePath()
const api = useApi()
const toast = useToast()

const showCreateTemplate = ref(false)
const templatesLoading = ref(true)
const creatingTemplate = ref(false)
const deletingTemplate = ref<string | null>(null)
const editTemplates = ref<any[]>([])
const newTemplateName = ref('')
const newTemplateDescription = ref('')
const applyingTemplate = ref<string | null>(null)

const videoList = ref<any[]>([])
const videosLoading = ref(false)
const selectedVideoId = ref('')
const selectedVideoName = ref('')
const selectedDuration = ref(0)
const trimStart = ref(0)
const trimEnd = ref(0)
const opRunning = ref(false)
const opError = ref('')

const clipWidth = computed(() => Math.max(120, Math.min(400, (selectedDuration.value || 60) * 4)))

async function fetchVideos() {
  videosLoading.value = true
  try {
    const res = await api.videos.list({ limit: 50 })
    videoList.value = (res as { items?: any[] })?.items ?? []
  } catch {
    videoList.value = []
  } finally {
    videosLoading.value = false
  }
}

function formatDuration(s: number | undefined) {
  if (s == null || Number.isNaN(s)) return '0:00'
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}:${sec.toString().padStart(2, '0')}`
}

function onVideoSelect() {
  const id = selectedVideoId.value
  if (!id) {
    selectedVideoName.value = ''
    selectedDuration.value = 0
    trimStart.value = 0
    trimEnd.value = 0
    return
  }
  const v = videoList.value.find((x) => x.id === id)
  if (v) {
    selectedVideoName.value = v.original_filename || v.filename
    selectedDuration.value = Number(v.duration) || 0
    trimStart.value = 0
    trimEnd.value = selectedDuration.value
  }
  opError.value = ''
}

async function runOp(op: string) {
  const id = selectedVideoId.value
  if (!id) return
  if (op === 'trim_clip' && (trimEnd.value <= trimStart.value || selectedDuration.value <= 0)) {
    toast.error('Set trim start < end and duration > 0')
    return
  }
  opRunning.value = true
  opError.value = ''
  try {
    let params: Record<string, unknown> = {}
    if (op === 'trim_clip') {
      params = { start: Number(trimStart.value) || 0, end: Number(trimEnd.value) || selectedDuration.value }
    } else if (op === 'export_video') {
      params = { width: 1920, height: 1080 }
    }
    const res = await api.editorOps.execute(id, op, params) as { error?: string; output_path?: string }
    if (res?.error) {
      opError.value = res.error
      toast.error(res.error)
    } else {
      toast.success(op === 'export_video' ? 'Export completed (output on server)' : `Done: ${op}`)
    }
  } catch (e: any) {
    const msg = e?.data?.detail ?? e?.message ?? String(e)
    opError.value = msg
    toast.error(msg)
  } finally {
    opRunning.value = false
  }
}

async function fetchTemplates() {
  templatesLoading.value = true
  try {
    const res = await api.editTemplates.list({ limit: 50 })
    editTemplates.value = res?.items ?? []
  } catch {
    editTemplates.value = []
  } finally {
    templatesLoading.value = false
  }
}

async function createTemplate() {
  const name = newTemplateName.value.trim()
  if (!name) return
  creatingTemplate.value = true
  try {
    await api.editTemplates.create({
      name,
      description: newTemplateDescription.value.trim() || undefined,
      style_spec: {},
    })
    showCreateTemplate.value = false
    newTemplateName.value = ''
    newTemplateDescription.value = ''
    await fetchTemplates()
    toast.success('Template created')
  } catch (e: any) {
    toast.error(e?.data?.detail ?? 'Failed to create template')
  } finally {
    creatingTemplate.value = false
  }
}

async function applyTemplate(templateId: string) {
  const videoId = selectedVideoId.value
  if (!videoId) return
  applyingTemplate.value = templateId
  try {
    await api.editTemplates.apply(templateId, videoId)
    toast.success('Apply template queued (implementation in progress)')
  } catch (e: any) {
    toast.error(e?.data?.detail ?? 'Failed to apply template')
  } finally {
    applyingTemplate.value = null
  }
}

async function deleteTemplate(id: string) {
  deletingTemplate.value = id
  try {
    await api.editTemplates.delete(id)
    editTemplates.value = editTemplates.value.filter((t) => t.id !== id)
    toast.success('Template deleted')
  } catch (e: any) {
    toast.error(e?.data?.detail ?? 'Failed to delete')
  } finally {
    deletingTemplate.value = null
  }
}

onMounted(async () => {
  await fetchVideos()
  await fetchTemplates()
  const q = route.query?.video
  if (q && typeof q === 'string') {
    selectedVideoId.value = q
    onVideoSelect()
  }
})
</script>
