<template>
  <div class="container-wide py-8 lg:py-12">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
      <div>
        <h1 class="text-3xl lg:text-4xl font-display font-bold text-surface-100">Videos</h1>
        <p class="text-surface-400 mt-2">Manage and analyze your video content</p>
      </div>
      <Button variant="primary" @click="showUpload = true">
        <Icon name="Upload" :size="18" />
        <span>Upload Video</span>
      </Button>
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
        <Icon name="ChevronDown" :size="16" class="absolute right-3 top-1/2 -translate-y-1/2 text-surface-500 pointer-events-none" />
      </div>
      
      <div class="flex-1 max-w-xs">
        <Input v-model="searchQuery" placeholder="Search videos..." type="search">
          <template #icon-left>
            <Icon name="Search" :size="18" />
          </template>
        </Input>
      </div>
    </div>

    <!-- Videos Grid or Empty State -->
    <EmptyState
      v-if="filteredVideos.length === 0 && !isLoading"
      icon="Video"
      title="No videos yet"
      description="Upload your first video to start analyzing patterns and generating strategies"
      action-label="Upload Video"
      action-icon="Upload"
      variant="primary"
      @action="showUpload = true"
    />

    <div v-else class="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <VideoCard
        v-for="video in filteredVideos"
        :key="video.id"
        :video="video"
        @analyze="analyzeVideo"
      />
    </div>

    <!-- Upload Modal -->
    <Modal v-model="showUpload" title="Upload Video" size="lg">
      <div
        class="relative border-2 border-dashed border-surface-700 rounded-2xl p-8 lg:p-12 text-center transition-all duration-200 cursor-pointer"
        :class="{ 
          'border-primary-500 bg-primary-500/5': isDragging,
          'hover:border-surface-600 hover:bg-surface-800/30': !isDragging
        }"
        @click="triggerFileInput"
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
          <Icon name="Upload" :size="32" class="text-primary-400" />
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
      <div v-if="uploadProgress > 0" class="mt-6">
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
          <Button variant="ghost" @click="showUpload = false">
            Cancel
          </Button>
        </div>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth',
})

const showUpload = ref(false)
const uploadProgress = ref(0)
const uploadingFileName = ref('')
const statusFilter = ref('')
const searchQuery = ref('')
const isDragging = ref(false)
const isLoading = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

// Mock data - replace with actual API calls
const videos = ref<any[]>([])

const filteredVideos = computed(() => {
  return videos.value.filter(video => {
    const matchesStatus = !statusFilter.value || video.status === statusFilter.value
    const matchesSearch = !searchQuery.value || 
      video.filename.toLowerCase().includes(searchQuery.value.toLowerCase())
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
}

const handleDrop = (event: DragEvent) => {
  isDragging.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file && file.type.startsWith('video/')) {
    uploadFile(file)
  }
}

const uploadFile = async (file: File) => {
  uploadingFileName.value = file.name
  uploadProgress.value = 0
  
  // Simulate upload progress
  const interval = setInterval(() => {
    uploadProgress.value += Math.random() * 15
    if (uploadProgress.value >= 100) {
      uploadProgress.value = 100
      clearInterval(interval)
      setTimeout(() => {
        showUpload.value = false
        uploadProgress.value = 0
        uploadingFileName.value = ''
        // TODO: Add video to list after actual upload
      }, 500)
    }
  }, 200)
}

const analyzeVideo = async (videoId: string) => {
  console.log('Analyzing video:', videoId)
  // TODO: Implement video analysis
}
</script>
