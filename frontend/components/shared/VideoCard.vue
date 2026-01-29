<template>
  <Card variant="hover" padding="none" class="group overflow-hidden">
    <!-- Thumbnail -->
    <div class="relative aspect-video bg-surface-800 overflow-hidden">
      <!-- Thumbnail image or placeholder -->
      <img 
        v-if="video.thumbnail_url" 
        :src="video.thumbnail_url" 
        :alt="video.filename"
        class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
      />
      <div v-else class="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-surface-800 to-surface-900">
        <UiIcon name="Video" :size="40" class="text-surface-600" />
      </div>
      
      <!-- Duration badge -->
      <div v-if="video.duration" class="absolute bottom-2 right-2 px-2 py-1 rounded bg-surface-950/80 text-xs font-medium text-surface-200">
        {{ formatDuration(video.duration) }}
      </div>
      
      <!-- Status indicator -->
      <div v-if="video.status === 'processing'" class="absolute inset-0 bg-surface-950/60 flex items-center justify-center">
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface-900/90">
          <div class="w-4 h-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
          <span class="text-sm text-surface-200">Processing...</span>
        </div>
      </div>
    </div>
    
    <!-- Content -->
    <div class="p-4">
      <!-- Title -->
      <h3 class="font-medium text-surface-100 truncate mb-2" :title="video.filename">
        {{ video.original_filename || video.filename }}
      </h3>
      
      <!-- Meta row -->
      <div class="flex items-center justify-between mb-4">
        <StatusBadge :status="video.status" />
        <span class="text-xs text-surface-500">
          {{ formatDate(video.created_at) }}
        </span>
      </div>
      
      <!-- Actions -->
      <div class="flex flex-wrap gap-2">
        <Button 
          variant="ghost" 
          size="sm" 
          :to="localePath(`/editor?video=${video.id}`)"
          class="flex-1"
        >
          <UiIcon name="Scissors" :size="16" />
          <span>Edit</span>
        </Button>
        <Button 
          variant="secondary" 
          size="sm" 
          :to="localePath(`/videos/${video.id}`)"
          class="flex-1"
        >
          <UiIcon name="Eye" :size="16" />
          <span>View</span>
        </Button>
        <Button 
          variant="primary" 
          size="sm" 
          class="flex-1"
          :disabled="video.status === 'processing'"
          @click="$emit('analyze', video.id)"
        >
          <UiIcon name="Sparkles" :size="16" />
          <span>Analyze</span>
        </Button>
      </div>
    </div>
  </Card>
</template>

<script setup lang="ts">
interface Video {
  id: string
  filename: string
  original_filename?: string
  thumbnail_url?: string
  duration?: number
  status: 'uploaded' | 'processing' | 'processed' | 'failed'
  created_at: string
}

interface Props {
  video: Video
}

defineProps<Props>()

const localePath = useLocalePath()

defineEmits<{
  (e: 'analyze', id: string): void
}>()

const formatDuration = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })
}
</script>
