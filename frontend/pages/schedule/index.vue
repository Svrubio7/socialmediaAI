<template>
  <div class="container-wide py-8 lg:py-10">
    <NuxtLink
      :to="localePath('/dashboard')"
      class="inline-flex items-center gap-2 text-sm text-surface-400 hover:text-surface-200 mb-6 transition-colors"
    >
      <UiIcon name="ArrowLeft" :size="16" />
      Back to Dashboard
    </NuxtLink>

    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
      <div>
        <h1 class="text-xl lg:text-2xl font-mono font-normal text-surface-100">Posting Schedule</h1>
        <p class="text-surface-400 mt-1 text-sm">Manage your scheduled posts</p>
      </div>
      <UiButton variant="primary" class="rounded-xl" :to="localePath('/publish')">
        <template #icon-left><UiIcon name="CalendarPlus" :size="16" /></template>
        Schedule a post
      </UiButton>
    </div>

    <!-- Platform filter -->
    <div class="flex flex-wrap gap-2 mb-5">
      <button
        v-for="pf in platformFilters"
        :key="pf.id"
        type="button"
        class="toggle-pill"
        :class="filterPlatform === pf.id ? 'toggle-pill-active' : 'toggle-pill-inactive'"
        @click="filterPlatform = pf.id"
      >
        <SharedPlatformIcon :platform="pf.platformId" size="sm" variant="outline" />
        {{ pf.label }}
      </button>
    </div>

    <!-- Calendar (Notion-like, lighter) -->
    <UiCard class="border-l-4 border-l-amber-500 border border-amber-500/20 bg-surface-700/30 dark:bg-surface-700/40 mb-5 pl-4 rounded-2xl">
      <h3 class="text-xs font-mono font-medium text-surface-400 mb-2">Calendar</h3>
      <div class="grid grid-cols-7 gap-px bg-surface-600/20 dark:bg-surface-600/30 rounded-xl overflow-hidden text-center text-xs font-medium max-w-2xl">
        <div v-for="d in weekDayLabels" :key="d" class="py-2 text-surface-500 bg-surface-600/30 dark:bg-surface-600/40">{{ d }}</div>
        <div
          v-for="i in 35"
          :key="i"
          class="min-h-[2.5rem] py-1.5 bg-surface-600/15 dark:bg-surface-600/20 text-surface-400 flex items-center justify-center"
        >
          {{ calendarDayNumbers[i - 1] }}
        </div>
      </div>
    </UiCard>

    <!-- Scheduled posts list -->
    <UiCard class="border-l-4 border-l-primary-500/50 border border-primary-500/20 bg-surface-700/30 dark:bg-surface-700/40 pl-4 rounded-2xl">
      <h3 class="text-xs font-mono font-medium text-surface-400 mb-3">Scheduled posts</h3>
      <div v-if="loading" class="py-12 flex justify-center">
        <div class="flex flex-col items-center gap-3">
          <UiSkeleton variant="rounded" width="64px" height="48px" />
          <UiSkeleton variant="text" width="200px" />
          <UiSkeleton variant="text" width="160px" />
        </div>
      </div>
      <SharedEmptyState
        v-else-if="filteredPosts.length === 0"
        icon="Calendar"
        title="No scheduled posts"
        description="Schedule content from the Publish page to see it here"
        action-label="Go to Publish"
        action-icon="Send"
        variant="primary"
        @action="goTo('/publish')"
      />
      <div v-else class="space-y-3">
        <div
          v-for="post in filteredPosts"
          :key="post.id"
          class="flex items-center gap-3 p-3 rounded-xl bg-surface-600/25 dark:bg-surface-600/30 border border-surface-600/40"
        >
          <SharedPlatformIcon :platform="post.platform" size="sm" variant="outline" />
          <div class="flex-1 min-w-0">
            <p class="font-medium text-surface-100 truncate text-sm">{{ post.video_title || 'Video' }}</p>
            <p class="text-surface-400 text-xs mt-0.5 inline-flex items-center gap-1">
              <UiIcon name="Clock" :size="12" />
              {{ formatDateTime(post.scheduled_at) }}
            </p>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0">
            <UiButton variant="ghost" size="sm" class="rounded-xl" :disabled="cancelling === post.id" @click="cancelPost(post.id)">
              <template #icon-left><UiIcon name="X" :size="14" /></template>
              Cancel
            </UiButton>
          </div>
        </div>
      </div>
    </UiCard>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
definePageMeta({
  layout: 'app-sidebar',
  middleware: 'auth',
})

const localePath = useLocalePath()
const api = useApi()

const weekDayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const calendarDayNumbers = Array.from({ length: 35 }, (_, i) => (i >= 31 ? '' : (i + 1).toString()))

const loading = ref(true)
const cancelling = ref<string | null>(null)
const posts = ref<any[]>([])
const filterPlatform = ref<string>('all')

const platformFilters = [
  { id: 'all', platformId: 'instagram' as const, label: 'All' },
  { id: 'instagram', platformId: 'instagram' as const, label: 'Instagram' },
  { id: 'tiktok', platformId: 'tiktok' as const, label: 'TikTok' },
  { id: 'youtube', platformId: 'youtube' as const, label: 'YouTube' },
  { id: 'facebook', platformId: 'facebook' as const, label: 'Facebook' },
]

const filteredPosts = computed(() => {
  if (filterPlatform.value === 'all') return posts.value
  return posts.value.filter((p) => p.platform?.toLowerCase() === filterPlatform.value)
})

const prefs = usePreferences()
function formatDateTime(iso: string) {
  return prefs.formatInUserTz(iso, { weekday: 'short' })
}

function goTo(path: string) {
  return navigateTo(localePath(path))
}

async function fetchScheduled() {
  loading.value = true
  try {
    const res = await api.posts.scheduled()
    posts.value = (res as { items?: any[] })?.items ?? []
  } catch {
    posts.value = []
  } finally {
    loading.value = false
  }
}

async function cancelPost(postId: string) {
  cancelling.value = postId
  try {
    await api.posts.cancel(postId)
    posts.value = posts.value.filter((p) => p.id !== postId)
  } catch {
    // keep list
  } finally {
    cancelling.value = null
  }
}

onMounted(fetchScheduled)
</script>
