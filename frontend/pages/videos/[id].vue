<template>
  <div class="container-wide py-8 lg:py-10">
    <NuxtLink
      :to="localePath('/videos')"
      class="inline-flex items-center gap-2 text-sm text-surface-400 hover:text-surface-200 mb-6 transition-colors"
    >
      <UiIcon name="ArrowLeft" :size="16" />
      Back to Videos
    </NuxtLink>

    <div v-if="loading" class="py-12 flex justify-center">
      <div class="flex flex-col items-center gap-3">
        <UiSkeleton variant="rounded" width="64px" height="48px" />
        <UiSkeleton variant="text" width="200px" />
      </div>
    </div>
    <div v-else-if="error" class="text-red-400">{{ error }}</div>
    <template v-else-if="video">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 class="text-xl lg:text-2xl font-mono font-normal text-surface-100 truncate">
            {{ video.original_filename || video.filename }}
          </h1>
          <p class="text-surface-400 mt-1 text-sm">Uploaded {{ formatDate(video.created_at) }}</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <UiButton
            variant="secondary"
            size="sm"
            :disabled="video.status === 'processing'"
            @click="editVideo"
          >
            <template #icon-left><UiIcon name="Scissors" :size="14" /></template>
            Edit
          </UiButton>
          <UiButton
            variant="primary"
            size="sm"
            :disabled="video.status === 'processing'"
            :loading="analyzing"
            @click="analyzeVideo"
          >
            <template #icon-left><UiIcon name="Sparkles" :size="14" /></template>
            Analyze
          </UiButton>
          <UiButton
            variant="ghost"
            size="sm"
            class="text-red-400 hover:text-red-300 hover:bg-red-500/10"
            :loading="deleting"
            @click="deleteVideo"
          >
            <template #icon-left><UiIcon name="Trash2" :size="14" /></template>
            Delete
          </UiButton>
        </div>
      </div>

      <UiCard class="border-l-4 border-l-primary-500 mb-6">
        <div class="grid lg:grid-cols-[1.2fr_1fr] gap-6">
          <div class="rounded-xl overflow-hidden bg-surface-800/50 border border-surface-700 flex items-center justify-center min-h-[220px]">
            <img
              v-if="video.thumbnail_url"
              :src="video.thumbnail_url"
              :alt="video.filename"
              class="w-full h-full object-cover"
            />
            <UiIcon v-else name="Video" :size="42" class="text-surface-500" />
          </div>
          <div class="space-y-4">
            <div class="flex items-center gap-2">
              <SharedStatusBadge :status="video.status" />
              <span class="text-surface-500 text-xs">ID: {{ video.id.slice(0, 8) }}</span>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="label">Duration</p>
                <p class="text-surface-100 font-medium">{{ formatDuration(video.duration) }}</p>
              </div>
              <div>
                <p class="label">Size</p>
                <p class="text-surface-100 font-medium">{{ formatBytes(video.file_size) }}</p>
              </div>
              <div>
                <p class="label">Resolution</p>
                <p class="text-surface-100 font-medium">{{ formatResolution(video) }}</p>
              </div>
              <div>
                <p class="label">Filename</p>
                <p class="text-surface-100 font-medium truncate">{{ video.filename }}</p>
              </div>
            </div>
          </div>
        </div>
      </UiCard>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
definePageMeta({
  layout: 'app-sidebar',
  middleware: 'auth',
})

const route = useRoute()
const localePath = useLocalePath()
const api = useApi()
const toast = useToast()

const loading = ref(true)
const error = ref('')
const video = ref<any>(null)
const analyzing = ref(false)
const deleting = ref(false)

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function formatDuration(seconds?: number) {
  if (!seconds && seconds !== 0) return '-'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function formatBytes(bytes?: number) {
  if (!bytes && bytes !== 0) return '-'
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex += 1
  }
  return `${size.toFixed(size < 10 && unitIndex > 0 ? 1 : 0)} ${units[unitIndex]}`
}

function formatResolution(v: { width?: number; height?: number }) {
  if (!v.width || !v.height) return '-'
  return `${v.width}x${v.height}`
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

async function fetchVideo() {
  loading.value = true
  error.value = ''
  try {
    video.value = await api.videos.get(route.params.id as string)
  } catch {
    error.value = 'Video not found'
    video.value = null
  } finally {
    loading.value = false
  }
}

async function analyzeVideo() {
  if (!video.value) return
  analyzing.value = true
  try {
    await api.videos.analyze(video.value.id)
    toast.success('Analysis started')
    await fetchVideo()
  } catch (e: any) {
    toast.error(e?.data?.detail ?? e?.message ?? 'Analysis failed')
  } finally {
    analyzing.value = false
  }
}

async function editVideo() {
  if (!video.value) return
  try {
    const projectName = video.value.original_filename || video.value.filename || 'Untitled project'
    const project = await api.projects.create({ name: projectName })
    const duration = Math.max(0.1, Number(video.value.duration) || 1)
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
    const state = {
      projectName: project.name || projectName,
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
              sourceId: video.value.id,
              sourceUrl: video.value.video_url,
              posterUrl: video.value.thumbnail_url,
              trimStart: 0,
              trimEnd: duration,
              aspectRatio: inferAspectRatio(video.value.width, video.value.height),
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
    await api.projects.update(project.id, { state })
    await navigateTo(localePath(`/editor/${project.id}`))
  } catch (e: any) {
    toast.error(e?.data?.detail ?? e?.message ?? 'Could not open editor')
  }
}

function confirmDelete() {
  if (!import.meta.client) return false
  return window.confirm('Delete this video? This cannot be undone.')
}

async function deleteVideo() {
  if (!video.value || deleting.value) return
  if (!confirmDelete()) return
  deleting.value = true
  try {
    await api.videos.delete(video.value.id)
    toast.success('Video deleted')
    await navigateTo(localePath('/videos'))
  } catch (e: any) {
    toast.error(e?.data?.detail ?? e?.message ?? 'Delete failed')
  } finally {
    deleting.value = false
  }
}

onMounted(fetchVideo)
</script>
