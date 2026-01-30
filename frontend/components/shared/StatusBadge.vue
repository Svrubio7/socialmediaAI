<template>
  <UiBadge :variant="badgeVariant" :dot="showDot">
    {{ label }}
  </UiBadge>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  status: 'uploaded' | 'processing' | 'processed' | 'failed' | 'scheduled' | 'published' | 'connected' | 'disconnected'
  showDot?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showDot: true,
})

const badgeVariant = computed(() => {
  const variants: Record<string, 'primary' | 'success' | 'warning' | 'danger' | 'accent' | 'neutral'> = {
    uploaded: 'primary',
    processing: 'warning',
    processed: 'success',
    failed: 'danger',
    scheduled: 'accent',
    published: 'success',
    connected: 'success',
    disconnected: 'neutral',
  }
  return variants[props.status] || 'neutral'
})

const label = computed(() => {
  const labels: Record<string, string> = {
    uploaded: 'Uploaded',
    processing: 'Processing',
    processed: 'Processed',
    failed: 'Failed',
    scheduled: 'Scheduled',
    published: 'Published',
    connected: 'Connected',
    disconnected: 'Not Connected',
  }
  return labels[props.status] || props.status
})
</script>
