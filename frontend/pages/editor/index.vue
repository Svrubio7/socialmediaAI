<template>
  <div class="container-wide py-8 lg:py-10">
    <NuxtLink
      :to="localePath('/dashboard')"
      class="inline-flex items-center gap-2 text-sm text-surface-400 hover:text-surface-200 mb-6 transition-colors"
    >
      <UiIcon name="ArrowLeft" :size="16" />
      Back to Dashboard
    </NuxtLink>

    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
      <div>
        <h1 class="text-3xl lg:text-4xl font-mono font-normal text-surface-100">Video Editor</h1>
        <p class="text-surface-400 mt-2">Edit and generate videos with timelines, layers, and templates</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <select
          v-model="selectedVideoId"
          class="input w-auto min-w-[200px]"
          :disabled="videosLoading"
          @change="onVideoSelect"
        >
          <option value="">{{ videosLoading ? 'Loading...' : 'Choose video...' }}</option>
          <option v-for="v in videoList" :key="v.id" :value="v.id">
            {{ v.original_filename || v.filename }} ({{ formatDuration(v.duration) }})
          </option>
        </select>
        <Button variant="primary" :to="localePath('/videos')">
          <UiIcon name="Upload" :size="18" />
          Upload
        </Button>
      </div>
    </div>

    <!-- Timeline + ops (CapCut-like minimal UI) -->
    <Card class="border border-accent-500/20 bg-surface-800/50 mb-10">
      <div v-if="!selectedVideoId" class="min-h-[320px] flex flex-col items-center justify-center gap-4 text-center">
        <div class="w-16 h-16 rounded-2xl bg-accent-500/20 flex items-center justify-center">
          <UiIcon name="Scissors" :size="32" class="text-accent-400" />
        </div>
        <p class="text-surface-400">Select a video to trim, reverse, duplicate, or export.</p>
        <Button variant="secondary" :to="localePath('/videos')">
          <UiIcon name="Video" :size="18" />
          Browse videos
        </Button>
      </div>
      <template v-else>
        <!-- Single-track timeline -->
        <div class="mb-6">
          <h3 class="text-sm font-mono font-medium text-surface-400 mb-2">Track 1</h3>
          <div class="h-14 rounded-xl bg-surface-700/50 border border-surface-600 flex items-center px-3 overflow-x-auto">
            <div
              class="h-10 rounded-lg flex items-center gap-2 flex-shrink-0 px-3 font-medium text-surface-200"
              :style="{ minWidth: clipWidth + 'px' }"
            >
              <UiIcon name="Video" :size="18" class="text-accent-400" />
              <span class="truncate">{{ selectedVideoName }}</span>
              <span class="text-surface-500 text-xs">{{ formatDuration(selectedDuration) }}</span>
            </div>
          </div>
        </div>
        <!-- Trim -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div>
            <label class="label">Trim start (s)</label>
            <Input v-model.number="trimStart" type="number" min="0" :max="selectedDuration" step="0.1" />
          </div>
          <div>
            <label class="label">Trim end (s)</label>
            <Input v-model.number="trimEnd" type="number" :min="trimStart" :max="selectedDuration" step="0.1" />
          </div>
        </div>
        <!-- Op buttons -->
        <div class="flex flex-wrap gap-3">
          <Button
            variant="secondary"
            size="sm"
            :disabled="opRunning"
            @click="runOp('trim_clip')"
          >
            <UiIcon name="Scissors" :size="16" />
            Apply trim
          </Button>
          <Button variant="secondary" size="sm" :disabled="opRunning" @click="runOp('reverse_clip')">
            <UiIcon name="RotateCcw" :size="16" />
            Reverse
          </Button>
          <Button variant="secondary" size="sm" :disabled="opRunning" @click="runOp('duplicate_clip')">
            <UiIcon name="Copy" :size="16" />
            Duplicate
          </Button>
          <Button variant="primary" size="sm" :disabled="opRunning" @click="runOp('export_video')">
            <UiIcon name="Download" :size="16" />
            Export
          </Button>
        </div>
        <p v-if="opError" class="mt-3 text-sm text-red-400">{{ opError }}</p>
      </template>
    </Card>

    <!-- Edit templates (content library) -->
    <Card class="border-l-4 border-l-accent-500 border border-accent-500/20 bg-surface-800/30">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <h2 class="text-xl font-mono font-medium text-surface-100">Edit templates</h2>
        <Button variant="secondary" size="sm" @click="showCreateTemplate = true">
          <UiIcon name="Plus" :size="18" />
          Create template
        </Button>
      </div>
      <div v-if="templatesLoading" class="py-12 flex justify-center">
        <div class="flex flex-col items-center gap-3">
          <Skeleton variant="rounded" width="80px" height="80px" />
          <Skeleton variant="text" width="160px" />
        </div>
      </div>
      <EmptyState
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
          class="p-4 rounded-xl bg-surface-800/50 border border-surface-700 flex flex-col"
        >
          <div class="flex items-center gap-3 mb-2">
            <div class="w-10 h-10 rounded-lg bg-accent-500/20 flex items-center justify-center flex-shrink-0">
              <UiIcon name="FileStack" :size="20" class="text-accent-400" />
            </div>
            <div class="min-w-0 flex-1">
              <p class="font-medium text-surface-100 truncate">{{ t.name }}</p>
              <p v-if="t.description" class="text-surface-500 text-xs truncate">{{ t.description }}</p>
            </div>
          </div>
          <div class="mt-auto pt-3 flex flex-wrap gap-2">
            <Button
              v-if="selectedVideoId"
              variant="secondary"
              size="sm"
              :disabled="applyingTemplate === t.id"
              @click="applyTemplate(t.id)"
            >
              <UiIcon name="Play" :size="16" />
              Apply
            </Button>
            <Button
              variant="ghost"
              size="sm"
              class="text-red-400 hover:text-red-300 hover:bg-red-500/10"
              :disabled="deletingTemplate === t.id"
              @click="deleteTemplate(t.id)"
            >
              <UiIcon name="Trash2" :size="16" />
              Delete
            </Button>
          </div>
        </div>
      </div>
    </Card>

    <!-- Create edit template modal -->
    <Modal v-model="showCreateTemplate" title="Create edit template" size="md">
      <form @submit.prevent="createTemplate" class="space-y-4">
        <div>
          <label class="label">Name</label>
          <Input v-model="newTemplateName" placeholder="e.g. TikTok fast cuts" required />
        </div>
        <div>
          <label class="label">Description (optional)</label>
          <Input v-model="newTemplateDescription" placeholder="Short description of this edit style" />
        </div>
        <div class="flex justify-end gap-3 pt-2">
          <Button variant="ghost" type="button" @click="showCreateTemplate = false">Cancel</Button>
          <Button variant="primary" type="submit" :disabled="creatingTemplate">
            {{ creatingTemplate ? 'Creating…' : 'Create' }}
          </Button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script setup lang="ts">
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
