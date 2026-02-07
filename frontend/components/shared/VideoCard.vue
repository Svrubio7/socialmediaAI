<template>
  <UiCard variant="hover" padding="none" class="group overflow-hidden">
    <!-- Thumbnail -->
    <div class="relative aspect-video bg-surface-200/70 dark:bg-surface-800 overflow-hidden">
      <!-- Thumbnail image or placeholder -->
      <img 
        v-if="video.thumbnail_url" 
        :src="video.thumbnail_url" 
        :alt="video.filename"
        class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
      />
      <div v-else class="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-surface-200 to-surface-300 dark:from-surface-800 dark:to-surface-900">
        <UiIcon name="Video" :size="40" class="text-surface-500 dark:text-surface-600" />
      </div>
      
      <!-- Duration badge -->
      <div v-if="video.duration" class="absolute bottom-2 right-2 px-2 py-1 rounded bg-surface-900/80 text-xs font-normal text-surface-50">
        {{ formatDuration(video.duration) }}
      </div>
      
      <!-- Status indicator -->
      <div v-if="video.status === 'processing'" class="absolute inset-0 bg-surface-950/60 flex items-center justify-center">
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface-900/90">
          <div class="w-4 h-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
          <span class="text-sm text-surface-100">Processing...</span>
        </div>
      </div>
    </div>
    
    <!-- Content -->
    <div class="p-4">
      <!-- Title -->
      <h3 class="font-normal text-surface-900 dark:text-surface-100 truncate mb-2" :title="video.filename">
        {{ video.original_filename || video.filename }}
      </h3>
      
      <!-- Meta row -->
      <div class="flex items-center justify-between mb-4">
        <SharedStatusBadge :status="video.status" />
        <span class="text-xs text-surface-600 dark:text-surface-500">
          {{ formatDate(video.created_at) }}
        </span>
      </div>
      
      <!-- Actions -->
      <div class="flex flex-wrap gap-2">
        <UiButton 
          variant="ghost" 
          size="sm" 
          :disabled="video.status === 'processing'"
          class="flex-1 rounded-xl"
          @click="$emit('edit', video)"
        >
          <template #icon-left><UiIcon name="Scissors" :size="14" /></template>
          Edit
        </UiButton>
        <UiButton 
          variant="secondary" 
          size="sm" 
          :to="localePath(`/videos/${video.id}`)"
          class="flex-1 rounded-xl"
        >
          <template #icon-left><UiIcon name="Eye" :size="14" /></template>
          View
        </UiButton>
        <UiButton 
          variant="primary" 
          size="sm" 
          class="flex-1 rounded-xl"
          :disabled="video.status === 'processing'"
          :loading="analyzing"
          @click="$emit('analyze', video.id)"
        >
          <template #icon-left><UiIcon name="Sparkles" :size="14" /></template>
          Analyze
        </UiButton>
      </div>
    </div>
  </UiCard>
</template>

<script setup lang="ts">
interface Video {
  id: string
  filename: string
  original_filename?: string
  thumbnail_url?: string
  video_url?: string
  duration?: number
  width?: number
  height?: number
  status: 'uploaded' | 'processing' | 'processed' | 'failed'
  created_at: string
}

interface Props {
  video: Video
  analyzing?: boolean
}

withDefaults(defineProps<Props>(), { analyzing: false })

const localePath = useLocalePath()

defineEmits<{
  (e: 'analyze', id: string): void
  (e: 'edit', video: Video): void
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
