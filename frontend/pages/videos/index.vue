<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-display font-bold">Videos</h1>
        <p class="text-surface-400 mt-1">Manage and analyze your video content</p>
      </div>
      <button @click="showUpload = true" class="btn-primary">
        Upload Video
      </button>
    </div>

    <!-- Upload Modal -->
    <div v-if="showUpload" class="fixed inset-0 bg-surface-950/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="card max-w-lg w-full">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-display font-semibold">Upload Video</h2>
          <button @click="showUpload = false" class="text-surface-400 hover:text-surface-100">
            ✕
          </button>
        </div>

        <div
          class="border-2 border-dashed border-surface-700 rounded-xl p-8 text-center hover:border-primary-500 transition-colors cursor-pointer"
          @click="triggerFileInput"
          @drop.prevent="handleDrop"
          @dragover.prevent
        >
          <input
            ref="fileInput"
            type="file"
            accept="video/*"
            class="hidden"
            @change="handleFileSelect"
          />
          <div class="text-4xl mb-4">📹</div>
          <p class="text-surface-300 mb-2">Drag and drop your video here</p>
          <p class="text-surface-500 text-sm">or click to browse</p>
          <p class="text-surface-500 text-xs mt-2">MP4, MOV, AVI up to 500MB</p>
        </div>

        <div v-if="uploadProgress > 0" class="mt-4">
          <div class="flex items-center justify-between text-sm mb-1">
            <span class="text-surface-400">Uploading...</span>
            <span class="text-surface-300">{{ uploadProgress }}%</span>
          </div>
          <div class="h-2 bg-surface-800 rounded-full overflow-hidden">
            <div 
              class="h-full bg-primary-500 transition-all duration-300"
              :style="{ width: `${uploadProgress}%` }"
            />
          </div>
        </div>

        <div class="flex justify-end gap-3 mt-6">
          <button @click="showUpload = false" class="btn-secondary">
            Cancel
          </button>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="flex items-center gap-4 mb-6">
      <select v-model="statusFilter" class="input w-auto">
        <option value="">All Status</option>
        <option value="uploaded">Uploaded</option>
        <option value="processing">Processing</option>
        <option value="processed">Processed</option>
        <option value="failed">Failed</option>
      </select>
    </div>

    <!-- Videos Grid -->
    <div v-if="videos.length === 0" class="card text-center py-16">
      <div class="text-6xl mb-4">📹</div>
      <h3 class="text-xl font-display font-semibold mb-2">No videos yet</h3>
      <p class="text-surface-400 mb-6">Upload your first video to start analyzing patterns</p>
      <button @click="showUpload = true" class="btn-primary">
        Upload Video
      </button>
    </div>

    <div v-else class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="video in videos" :key="video.id" class="card-hover">
        <div class="aspect-video bg-surface-800 rounded-lg mb-4 flex items-center justify-center">
          <span class="text-4xl">📹</span>
        </div>
        <h3 class="font-medium truncate">{{ video.filename }}</h3>
        <div class="flex items-center justify-between mt-2">
          <span 
            class="badge"
            :class="{
              'badge-success': video.status === 'processed',
              'badge-warning': video.status === 'processing',
              'badge-primary': video.status === 'uploaded',
              'badge-danger': video.status === 'failed',
            }"
          >
            {{ video.status }}
          </span>
          <span class="text-surface-500 text-sm">
            {{ formatDate(video.created_at) }}
          </span>
        </div>
        <div class="flex gap-2 mt-4">
          <NuxtLink :to="`/videos/${video.id}`" class="btn-secondary flex-1 text-center text-sm">
            View
          </NuxtLink>
          <button @click="analyzeVideo(video.id)" class="btn-primary flex-1 text-sm" :disabled="video.status === 'processing'">
            Analyze
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth',
})

const showUpload = ref(false)
const uploadProgress = ref(0)
const statusFilter = ref('')
const fileInput = ref<HTMLInputElement | null>(null)

const videos = ref<any[]>([])

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    uploadFile(file)
  }
}

const handleDrop = (event: DragEvent) => {
  const file = event.dataTransfer?.files?.[0]
  if (file && file.type.startsWith('video/')) {
    uploadFile(file)
  }
}

const uploadFile = async (file: File) => {
  // TODO: Implement actual upload
  console.log('Uploading:', file.name)
  
  // Simulate upload progress
  uploadProgress.value = 0
  const interval = setInterval(() => {
    uploadProgress.value += 10
    if (uploadProgress.value >= 100) {
      clearInterval(interval)
      setTimeout(() => {
        showUpload.value = false
        uploadProgress.value = 0
      }, 500)
    }
  }, 200)
}

const analyzeVideo = async (videoId: string) => {
  // TODO: Implement video analysis
  console.log('Analyzing video:', videoId)
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString()
}
</script>
