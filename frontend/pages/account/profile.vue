<template>
  <div class="container-wide py-8 lg:py-10">
    <NuxtLink
      :to="localePath('/dashboard')"
      class="inline-flex items-center gap-2 text-sm text-surface-400 hover:text-surface-200 mb-6 transition-colors"
    >
      <UiIcon name="ArrowLeft" :size="16" />
      Back to Dashboard
    </NuxtLink>

    <h1 class="text-3xl lg:text-4xl font-mono font-bold text-surface-100 mb-2">Profile</h1>
    <p class="text-surface-400 mb-8">Your account information</p>

    <Card class="max-w-xl border-l-4 border-l-primary-500">
      <div class="flex flex-col sm:flex-row items-start gap-6">
        <div class="w-24 h-24 rounded-2xl bg-primary-500/20 flex items-center justify-center flex-shrink-0 overflow-hidden">
          <img
            v-if="user?.user_metadata?.avatar_url"
            :src="user.user_metadata.avatar_url"
            alt="Avatar"
            class="w-full h-full object-cover"
          />
          <UiIcon v-else name="User" :size="48" class="text-primary-400" />
        </div>
        <div class="flex-1 min-w-0 space-y-4">
          <div>
            <label class="label">Display name</label>
            <p class="font-medium text-surface-100">{{ user?.user_metadata?.name ?? '—' }}</p>
          </div>
          <div>
            <label class="label">Email</label>
            <p class="font-medium text-surface-100">{{ user?.email ?? '—' }}</p>
          </div>
          <p class="text-surface-500 text-sm">Profile editing can be added when backend supports it.</p>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: 'auth',
})

const localePath = useLocalePath()
const user = useSupabaseUser()
</script>
