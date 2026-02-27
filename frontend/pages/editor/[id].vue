<template>
  <div class="min-h-screen bg-background flex items-center justify-center">
    <div class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
      <p class="text-muted-foreground">Loading editor...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: false,
})

const route = useRoute()

onMounted(() => {
  const projectId = route.params.id
  const returnTo = encodeURIComponent(route.query.returnTo?.toString() || '/videos')
  const isDev = window.location.port === '3000'
  
  if (isDev) {
    window.location.href = `http://localhost:3002/editor/${projectId}?returnTo=${returnTo}`
  } else {
    window.location.href = `/editor/${projectId}?returnTo=${returnTo}`
  }
})

useSeoMeta({
  title: 'Editor | Elevo',
  description: 'Video editor powered by Elevo',
})
</script>
