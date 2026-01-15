<template>
  <NuxtLayout name="auth">
    <div class="card text-center">
      <div class="animate-spin w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full mx-auto mb-4" />
      <p class="text-surface-400">Completing sign in...</p>
    </div>
  </NuxtLayout>
</template>

<script setup lang="ts">
definePageMeta({
  layout: false,
})

// Supabase handles the callback automatically
// Redirect to dashboard after auth completes
const user = useSupabaseUser()

watch(user, (newUser) => {
  if (newUser) {
    navigateTo('/dashboard')
  }
}, { immediate: true })
</script>
