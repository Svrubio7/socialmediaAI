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
const supabase = useSupabaseClient()

onMounted(async () => {
  const projectId = route.params.id
  const returnTo = encodeURIComponent(route.query.returnTo?.toString() || '/videos')
  const isDev = window.location.port === '3001'

  // Get the current session to pass the auth token to the editor (different origin in dev)
  let tokenParam = ''
  if (isDev) {
    const { data: { session } } = await supabase.auth.getSession()
    if (session?.access_token) {
      tokenParam = `&access_token=${encodeURIComponent(session.access_token)}&refresh_token=${encodeURIComponent(session.refresh_token || '')}`
    }
  }

  if (isDev) {
    // In dev, the editor runs at localhost:3002 with no basePath, so /<id> is the correct path
    window.location.href = `http://localhost:3002/${projectId}?returnTo=${returnTo}${tokenParam}`
  } else {
    window.location.href = `/editor/${projectId}?returnTo=${returnTo}`
  }
})

useSeoMeta({
  title: 'Editor | Elevo',
  description: 'Video editor powered by Elevo',
})
</script>
