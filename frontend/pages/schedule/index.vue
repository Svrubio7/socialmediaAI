<template>
  <div class="container-wide py-8 lg:py-10">
    <NuxtLink
      :to="localePath('/dashboard')"
      class="inline-flex items-center gap-2 text-sm text-surface-400 hover:text-surface-200 mb-6 transition-colors"
    >
      <UiIcon name="ArrowLeft" :size="16" />
      Back to Dashboard
    </NuxtLink>

    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
      <div>
        <h1 class="text-3xl lg:text-4xl font-mono font-normal text-surface-100">Posting Schedule</h1>
        <p class="text-surface-400 mt-2">Manage your scheduled posts across platforms</p>
      </div>
      <Button variant="primary" :to="localePath('/publish')">
        <UiIcon name="CalendarPlus" :size="18" />
        Schedule a post
      </Button>
    </div>

    <!-- Platform filter -->
    <div class="flex flex-wrap gap-2 mb-6">
      <button
        v-for="pf in platformFilters"
        :key="pf.id"
        type="button"
        class="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all"
        :class="
          filterPlatform === pf.id
            ? 'bg-primary-500/20 text-primary-300 border border-primary-500/30'
            : 'bg-surface-800 text-surface-400 border border-surface-700 hover:border-surface-600'
        "
        @click="filterPlatform = pf.id"
      >
        <PlatformIcon :platform="pf.platformId" size="sm" variant="outline" />
        {{ pf.label }}
      </button>
    </div>

    <!-- Placeholder calendar (lighter schedule area) -->
    <Card class="border-l-4 border-l-amber-500 border border-amber-500/20 bg-surface-800 mb-6 pl-4">
      <h3 class="text-sm font-mono font-medium text-surface-400 mb-3">Calendar</h3>
      <div class="grid grid-cols-7 gap-px bg-surface-700 rounded-xl overflow-hidden text-center text-xs font-medium max-w-2xl">
        <div v-for="d in weekDayLabels" :key="d" class="bg-surface-700 py-2.5 text-surface-400">{{ d }}</div>
        <div
          v-for="i in 35"
          :key="i"
          class="aspect-square bg-surface-700/80 py-1.5 text-surface-500 flex items-center justify-center min-h-[44px]"
        >
          {{ calendarDayNumbers[i - 1] }}
        </div>
      </div>
    </Card>

    <!-- Scheduled posts list (lighter schedule area) -->
    <Card class="border-l-4 border-l-primary-500/50 border border-primary-500/20 bg-surface-800 pl-4">
      <h3 class="text-sm font-mono font-medium text-surface-400 mb-4">Scheduled posts</h3>
      <div v-if="loading" class="py-12 flex justify-center">
        <div class="flex flex-col items-center gap-3">
          <Skeleton variant="rounded" width="64px" height="48px" />
          <Skeleton variant="text" width="200px" />
          <Skeleton variant="text" width="160px" />
        </div>
      </div>
      <EmptyState
        v-else-if="filteredPosts.length === 0"
        icon="Calendar"
        title="No scheduled posts"
        description="Schedule content from the Publish page to see it here"
        action-label="Go to Publish"
        action-icon="Send"
        variant="primary"
        @action="goTo('/publish')"
      />
      <div v-else class="space-y-4">
        <div
          v-for="post in filteredPosts"
          :key="post.id"
          class="flex items-center gap-4 p-4 rounded-xl bg-surface-700/80 border border-surface-600"
        >
          <PlatformIcon :platform="post.platform" size="md" variant="outline" />
          <div class="flex-1 min-w-0">
            <p class="font-medium text-surface-100 truncate">{{ post.video_title || 'Video' }}</p>
            <p class="text-surface-400 text-sm mt-0.5">
              <UiIcon name="Clock" :size="14" class="inline mr-1" />
              {{ formatDateTime(post.scheduled_at) }}
            </p>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0">
            <Button variant="ghost" size="sm" :disabled="cancelling === post.id" @click="cancelPost(post.id)">
              <UiIcon name="X" :size="16" />
              Cancel
            </Button>
          </div>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
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
