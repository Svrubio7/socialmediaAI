<template>
  <div class="container-wide py-8 lg:py-12">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
      <div>
        <h1 class="text-xl lg:text-2xl font-mono font-normal text-surface-100">Videos</h1>
        <p class="text-surface-400 mt-1 text-sm">Manage and analyze your video content</p>
      </div>
      <UiButton variant="primary" class="rounded-xl" @click="showUpload = true">
        <template #icon-left><UiIcon name="Upload" :size="16" /></template>
        Upload Video
      </UiButton>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap items-center gap-4 mb-6">
      <div class="relative">
        <select 
          v-model="statusFilter" 
          class="input w-auto pr-10 appearance-none cursor-pointer"
        >
          <option value="">All Status</option>
          <option value="uploaded">Uploaded</option>
          <option value="processing">Processing</option>
          <option value="processed">Processed</option>
          <option value="failed">Failed</option>
        </select>
        <UiIcon name="ChevronDown" :size="16" class="absolute right-3 top-1/2 -translate-y-1/2 text-surface-500 pointer-events-none" />
      </div>
      
      <div class="flex-1 max-w-xs">
        <UiInput v-model="searchQuery" placeholder="Search videos..." type="search">
          <template #icon-left>
            <UiIcon name="Search" :size="18" />
          </template>
        </UiInput>
      </div>
    </div>

    <!-- Loading skeleton -->
    <div v-if="isLoading" class="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <SharedVideoCardSkeleton v-for="i in 6" :key="i" />
    </div>
    <SharedEmptyState
      v-else-if="filteredVideos.length === 0"
      icon="Video"
      title="No videos yet"
      description="Upload your first video to start analyzing patterns and generating strategies"
      action-label="Upload Video"
      action-icon="Upload"
      variant="primary"
      @action="showUpload = true"
    />
    <div v-else class="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <SharedVideoCard
        v-for="video in filteredVideos"
        :key="video.id"
        :video="video"
        :analyzing="analyzingId === video.id"
        @analyze="analyzeVideo"
        @edit="editVideo"
      />
    </div>

    <!-- Upload Modal -->
    <UiModal v-model="showUpload" title="Upload Video" size="lg">
      <div
        class="relative border-2 border-dashed border-surface-700 rounded-2xl p-8 lg:p-12 text-center transition-all duration-200 cursor-pointer"
        :class="{ 
          'border-primary-500 bg-primary-500/5': isDragging,
          'hover:border-surface-600 hover:bg-surface-800/30': !uploading && !isDragging,
          'pointer-events-none opacity-60': uploading
        }"
        @click="() => { if (!uploading) triggerFileInput() }"
        @drop.prevent="handleDrop"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
      >
        <input
          ref="fileInput"
          type="file"
          accept="video/*"
          class="hidden"
          @change="handleFileSelect"
        />
        
        <div class="w-16 h-16 mx-auto mb-4 rounded-2xl bg-primary-500/10 flex items-center justify-center">
          <UiIcon name="Upload" :size="32" class="text-primary-400" />
        </div>
        
        <p class="text-surface-200 font-medium mb-1">
          Drag and drop your video here
        </p>
        <p class="text-surface-500 text-sm mb-4">
          or click to browse
        </p>
        <p class="text-surface-600 text-xs">
          MP4, MOV, AVI up to 500MB
        </p>
      </div>

      <!-- Upload Progress -->
      <div v-if="uploading" class="mt-6">
        <div class="flex items-center justify-between text-sm mb-2">
          <span class="text-surface-300">{{ uploadingFileName }}</span>
          <span class="text-surface-400">{{ uploadProgress }}%</span>
        </div>
        <div class="h-2 bg-surface-800 rounded-full overflow-hidden">
          <div 
            class="h-full bg-gradient-to-r from-primary-500 to-accent-500 transition-all duration-300"
            :style="{ width: `${uploadProgress}%` }"
          />
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end gap-3">
          <UiButton variant="ghost" class="rounded-xl" :disabled="uploading" @click="showUpload = false">
            Cancel
          </UiButton>
        </div>
      </template>
    </UiModal>

    <UiModal v-model="showExistingProject" title="Project already exists" size="md">
      <p class="text-sm text-surface-200">
        This video already has its own project, are you sure you want start a new one?
      </p>
      <template #footer>
        <div class="flex justify-end gap-3">
          <UiButton variant="ghost" class="rounded-xl" @click="resetProjectFlow">
            Cancel
          </UiButton>
          <UiButton variant="secondary" class="rounded-xl" @click="openExistingProject">
            Keep editing
          </UiButton>
          <UiButton variant="primary" class="rounded-xl" @click="startNewProjectFromWarning">
            Start new project
          </UiButton>
        </div>
      </template>
    </UiModal>

    <UiModal v-model="showProjectNameModal" title="Name your project" size="md">
      <form class="space-y-4" @submit.prevent="createProjectFromVideo">
        <div>
          <label class="label text-sm">Project name</label>
          <UiInput v-model="newProjectName" placeholder="e.g. Instagram cutdown" required />
        </div>
        <div class="flex justify-end gap-3 pt-2">
          <UiButton variant="ghost" type="button" class="rounded-xl" @click="resetProjectFlow">
            Cancel
          </UiButton>
          <UiButton variant="primary" type="submit" class="rounded-xl" :disabled="creatingProject">
            {{ creatingProject ? 'Creating...' : 'Create project' }}
          </UiButton>
        </div>
      </form>
    </UiModal>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
definePageMeta({
  layout: 'app-sidebar',
  middleware: 'auth',
})

const api = useApi()
const toast = useToast()
const localePath = useLocalePath()
const editorRouting = useEditorRouting()
const showUpload = ref(false)
const uploadProgress = ref(0)
const uploadingFileName = ref('')
const statusFilter = ref('')
const searchQuery = ref('')
const isDragging = ref(false)
const isLoading = ref(true)
const fileInput = ref<HTMLInputElement | null>(null)
const videos = ref<any[]>([])
const analyzingId = ref<string | null>(null)
const pendingVideo = ref<any | null>(null)
const existingProject = ref<any | null>(null)
const showExistingProject = ref(false)
const showProjectNameModal = ref(false)
const newProjectName = ref('')
const checkingProject = ref(false)
const creatingProject = ref(false)
const preferredEditorEngine = computed<'legacy' | 'opencut'>(() =>
  editorRouting.isForkEnabledForUser.value ? 'opencut' : 'legacy'
)
let mediaUrlRefreshTimer: ReturnType<typeof setTimeout> | null = null
const MEDIA_URL_REFRESH_BUFFER_SECONDS = 90

function clearMediaUrlRefreshTimer() {
  if (!mediaUrlRefreshTimer) return
  clearTimeout(mediaUrlRefreshTimer)
  mediaUrlRefreshTimer = null
}

function scheduleMediaUrlRefresh(expiresIn?: number) {
  clearMediaUrlRefreshTimer()
  if (typeof expiresIn !== 'number' || !Number.isFinite(expiresIn) || expiresIn <= 0) return
  const refreshInMs = Math.max(30_000, (expiresIn - MEDIA_URL_REFRESH_BUFFER_SECONDS) * 1000)
  mediaUrlRefreshTimer = setTimeout(() => {
    void refreshVideoMediaUrls()
  }, refreshInMs)
}

async function refreshVideoMediaUrls() {
  const ids = videos.value.map((video) => String(video?.id || '')).filter(Boolean)
  if (!ids.length) return
  try {
    const resolved = await api.videos.mediaUrls(ids, {
      includeVideo: true,
      includeThumbnail: true,
    })
    const byId = new Map<string, { video_url?: string; thumbnail_url?: string }>()
    for (const item of resolved?.items ?? []) {
      const id = String(item?.id || '')
      if (!id) continue
      byId.set(id, item)
    }
    videos.value = videos.value.map((video) => {
      const id = String(video?.id || '')
      const media = byId.get(id)
      if (!media) return video
      const nextVideoUrl = media.video_url || video.video_url
      const nextThumbnail = media.thumbnail_url || video.thumbnail_url
      if (nextVideoUrl === video.video_url && nextThumbnail === video.thumbnail_url) return video
      return {
        ...video,
        video_url: nextVideoUrl,
        thumbnail_url: nextThumbnail,
      }
    })
    scheduleMediaUrlRefresh(resolved?.expires_in)
  } catch {
    // Keep existing URLs; list can still render with current data.
  }
}

async function fetchVideos() {
  isLoading.value = true
  try {
    const res = await api.videos.list({ limit: 100 })
    videos.value = (res as { items?: any[] })?.items ?? []
    await refreshVideoMediaUrls()
  } catch {
    videos.value = []
    clearMediaUrlRefreshTimer()
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchVideos)
onBeforeUnmount(() => {
  clearMediaUrlRefreshTimer()
})

const filteredVideos = computed(() => {
  return videos.value.filter(video => {
    const matchesStatus = !statusFilter.value || video.status === statusFilter.value
    const matchesSearch = !searchQuery.value ||
      (video.filename || '').toLowerCase().includes(searchQuery.value.toLowerCase())
    return matchesStatus && matchesSearch
  })
})

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    uploadFile(file)
  }
  target.value = ''
}

const handleDrop = (event: DragEvent) => {
  isDragging.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file && file.type.startsWith('video/')) {
    uploadFile(file)
  }
}

const uploading = ref(false)
const uploadFile = async (file: File) => {
  uploadingFileName.value = file.name
  uploadProgress.value = 10
  uploading.value = true
  try {
    await api.videos.upload(file)
    uploadProgress.value = 100
    toast.success('Video uploaded')
    await fetchVideos()
    showUpload.value = false
  } catch (e: any) {
    toast.error(e?.data?.detail ?? e?.message ?? 'Upload failed')
  } finally {
    uploadProgress.value = 0
    uploadingFileName.value = ''
    uploading.value = false
  }
}

const analyzeVideo = async (videoId: string) => {
  analyzingId.value = videoId
  try {
    await api.videos.analyze(videoId)
    toast.success('Analysis started')
    await fetchVideos()
  } catch (e: any) {
    toast.error(e?.data?.detail ?? e?.message ?? 'Analysis failed')
  } finally {
    analyzingId.value = null
  }
}

function inferAspectRatio(width?: number, height?: number) {
  const w = Number(width)
  const h = Number(height)
  if (!w || !h) return '16:9'
  const ratio = w / h
  const known = [
    { key: '16:9', value: 16 / 9 },
    { key: '9:16', value: 9 / 16 },
    { key: '1:1', value: 1 },
    { key: '4:5', value: 4 / 5 },
    { key: '4:3', value: 4 / 3 },
    { key: '21:9', value: 21 / 9 },
  ]
  let best = known[0]
  let score = Number.POSITIVE_INFINITY
  for (const option of known) {
    const delta = Math.abs(option.value - ratio)
    if (delta < score) {
      score = delta
      best = option
    }
  }
  return best.key
}

function buildProjectState(video: any, projectName: string) {
  const duration = Math.max(0.1, Number(video.duration) || 1)
  const clipId = `video-${Date.now()}-${Math.random().toString(16).slice(2)}`
  const baseEffects = {
    fadeIn: 0,
    fadeOut: 0,
    transition: undefined,
    transitionDuration: undefined,
    audioFadeIn: 0,
    audioFadeOut: 0,
    speed: 1,
    filter: 'None',
    brightness: 0,
    contrast: 1,
    saturation: 1,
    gamma: 1,
    hue: 0,
    blur: 0,
    opacity: 1,
    volume: 1,
    blendMode: 'normal',
    overlayColor: 'transparent',
    overlayOpacity: 0,
    overlayBlend: 'soft-light',
  }
  return {
    projectName,
    tracks: [
      {
        id: 'track-video',
        type: 'video',
        label: 'Video',
        clips: [
          {
            id: clipId,
            type: 'video',
            label: projectName,
            startTime: 0,
            duration,
            layer: 1,
            layerGroup: 'video',
            sourceId: video.id,
            sourceUrl: video.video_url,
            posterUrl: video.thumbnail_url,
            trimStart: 0,
            trimEnd: duration,
            aspectRatio: inferAspectRatio(video.width, video.height),
            fitMode: 'fit',
            position: { x: 0, y: 0 },
            size: { width: 100, height: 100 },
            lockAspectRatio: true,
            effects: { ...baseEffects },
          },
        ],
      },
      { id: 'track-graphics', type: 'graphics', label: 'Graphics', clips: [] },
      { id: 'track-audio', type: 'audio', label: 'Audio', clips: [] },
    ],
    selectedClipId: clipId,
    playheadTime: 0,
    timelineZoom: 1,
  }
}

function openProjectNameModal(video: any) {
  pendingVideo.value = video
  newProjectName.value = (video?.original_filename || video?.filename || '').trim()
  showProjectNameModal.value = true
}

function resetProjectFlow() {
  showExistingProject.value = false
  showProjectNameModal.value = false
  existingProject.value = null
  pendingVideo.value = null
  newProjectName.value = ''
}

async function createProjectFromVideo() {
  const video = pendingVideo.value
  if (!video || creatingProject.value) return
  const name = newProjectName.value.trim()
  if (!name) {
    toast.error('Project name is required')
    return
  }
  creatingProject.value = true
  try {
    const project = await api.projects.create({
      name,
      source_video_id: String(video.id),
      editor_engine: preferredEditorEngine.value,
    })
    if (preferredEditorEngine.value === 'legacy') {
      const state = buildProjectState(video, project?.name || name)
      await api.projects.update(project.id, { state, editor_engine: preferredEditorEngine.value })
    } else if (video.storage_path) {
      await api.projects.assets.register(project.id, {
        kind: 'video',
        storage_path: String(video.storage_path),
        filename: String(video.filename || video.original_filename || `${video.id}.mp4`),
        original_filename: String(video.original_filename || video.filename || `${video.id}.mp4`),
        file_size: typeof video.file_size === 'number' ? video.file_size : undefined,
        duration: typeof video.duration === 'number' ? video.duration : undefined,
        width: typeof video.width === 'number' ? video.width : undefined,
        height: typeof video.height === 'number' ? video.height : undefined,
        metadata: {
          project_id: project.id,
          source_video_id: String(video.id),
          opencut_media_id: `video_${video.id}`,
        },
      })
    }
    resetProjectFlow()
    await navigateTo(
      localePath(
        editorRouting.projectPathForEngine(project.id, preferredEditorEngine.value)
      )
    )
  } catch (e: any) {
    toast.error(e?.data?.detail ?? e?.message ?? 'Could not open editor')
  } finally {
    creatingProject.value = false
  }
}

async function openExistingProject() {
  if (!existingProject.value?.id) return
  const projectId = existingProject.value.id
  const projectEngine = existingProject.value.editor_engine as string | undefined
  resetProjectFlow()
  await navigateTo(localePath(editorRouting.projectPathForEngine(projectId, projectEngine)))
}

function startNewProjectFromWarning() {
  showExistingProject.value = false
  if (pendingVideo.value) {
    openProjectNameModal(pendingVideo.value)
  }
}

const editVideo = async (video: any) => {
  if (!video || checkingProject.value) return
  pendingVideo.value = video
  checkingProject.value = true
  try {
    const res = await api.projects.list({
      limit: 1,
      sourceVideoId: String(video.id),
      editorEngine: preferredEditorEngine.value,
    })
    let project = res?.items?.[0]
    if (!project) {
      const fallback = await api.projects.list({
        limit: 50,
        editorEngine: preferredEditorEngine.value,
      })
      const targetName = (video.original_filename || video.filename || '').trim().toLowerCase()
      if (targetName) {
        project = (fallback?.items ?? []).find((item: any) =>
          (item?.name || '').trim().toLowerCase() === targetName
        )
      }
    }
    if (project) {
      existingProject.value = project
      showExistingProject.value = true
      return
    }
    openProjectNameModal(video)
  } catch (e: any) {
    toast.error(e?.data?.detail ?? e?.message ?? 'Could not check existing projects')
  } finally {
    checkingProject.value = false
  }
}
</script>
