<template>
  <div class="container-wide py-8 lg:py-10">
    <!-- Header -->
    <div class="mb-6 lg:mb-8">
      <h1 class="text-3xl lg:text-4xl font-mono font-bold text-surface-100">Dashboard</h1>
      <p class="text-surface-400 mt-2">Welcome back! Here's an overview of your content.</p>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <template v-if="statsLoading">
        <StatCardSkeleton v-for="i in 4" :key="i" />
      </template>
      <template v-else>
        <StatCard
          v-for="stat in stats"
          :key="stat.label"
          :label="stat.label"
          :value="stat.value"
          :icon="stat.icon"
          :icon-bg="stat.iconBg"
          :icon-color="stat.iconColor"
          :change="stat.change"
        />
      </template>
    </div>

    <!-- Quick Actions -->
    <div class="grid md:grid-cols-3 gap-4 mb-8">
      <Card variant="interactive" to="/videos" class="group border-l-4 border-primary-500">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-primary-500/20 flex items-center justify-center flex-shrink-0 transition-transform duration-300 group-hover:scale-110">
            <Icon name="Upload" :size="24" class="text-primary-400" />
          </div>
          <div class="min-w-0">
            <h3 class="font-mono font-semibold text-surface-100">Upload Video</h3>
            <p class="text-surface-400 text-sm mt-0.5">Analyze patterns in your content</p>
          </div>
        </div>
      </Card>

      <Card variant="interactive" to="/strategies" class="group border-l-4 border-accent-500">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-accent-500/15 flex items-center justify-center flex-shrink-0 transition-transform duration-300 group-hover:scale-110">
            <Icon name="Target" :size="24" class="text-accent-400" />
          </div>
          <div class="min-w-0">
            <h3 class="font-mono font-semibold text-surface-100">Strategies</h3>
            <p class="text-surface-400 text-sm mt-0.5">Chat with the assistant for scripts and schedules</p>
          </div>
        </div>
      </Card>

      <Card variant="interactive" to="/publish" class="group border-l-4 border-emerald-500">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center flex-shrink-0 transition-transform duration-300 group-hover:scale-110">
            <Icon name="Send" :size="24" class="text-emerald-400" />
          </div>
          <div class="min-w-0">
            <h3 class="font-mono font-semibold text-surface-100">Publish Content</h3>
            <p class="text-surface-400 text-sm mt-0.5">Share to all platforms</p>
          </div>
        </div>
      </Card>
    </div>

    <!-- Recent Videos & Posting Schedule -->
    <div class="grid lg:grid-cols-2 gap-6">
      <!-- Recent Videos -->
      <Card class="flex flex-col min-h-[240px] border-l-4 border-l-primary-500/50">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-mono font-semibold text-surface-100">Recent Videos</h2>
          <Button variant="ghost" size="sm" to="/videos">
            View all
            <Icon name="ArrowRight" :size="16" />
          </Button>
        </div>

        <div v-if="videosLoading" class="flex-1 flex items-center justify-center py-8">
          <div class="flex flex-col items-center gap-3">
            <Skeleton variant="rounded" width="64px" height="48px" />
            <Skeleton variant="text" width="120px" />
            <Skeleton variant="text" width="80px" />
          </div>
        </div>
        <EmptyState
          v-else-if="recentVideos.length === 0"
          icon="Video"
          title="No videos yet"
          description="Upload your first video to start analyzing patterns"
          action-label="Upload Video"
          action-icon="Upload"
          variant="primary"
          @action="goTo('/videos')"
        />
        <div v-else class="space-y-3 flex-1">
          <div
            v-for="video in recentVideos"
            :key="video.id"
            class="flex items-center gap-4 p-3 rounded-xl bg-surface-800/50 hover:bg-surface-800 transition-colors"
          >
            <div class="w-16 h-12 bg-surface-700 rounded-lg flex items-center justify-center overflow-hidden flex-shrink-0">
              <img
                v-if="video.thumbnail_url"
                :src="video.thumbnail_url"
                :alt="video.filename"
                class="w-full h-full object-cover"
              />
              <Icon v-else name="Video" :size="20" class="text-surface-500" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium text-surface-100 truncate">{{ video.filename }}</p>
              <div class="flex items-center gap-2 mt-1">
                <StatusBadge :status="video.status" :show-dot="false" />
              </div>
            </div>
          </div>
        </div>
      </Card>

      <!-- Posting Schedule (Notion-style expandable) -->
      <Card
        class="flex flex-col min-h-[240px] border-l-4 border-l-amber-500 cursor-pointer transition-colors hover:bg-surface-900/50"
        @click="scheduleExpanded = !scheduleExpanded"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-amber-500/20 flex items-center justify-center flex-shrink-0">
              <Icon name="Calendar" :size="20" class="text-amber-400" />
            </div>
            <div>
              <h2 class="text-xl font-mono font-semibold text-surface-100">Posting Schedule</h2>
              <p class="text-surface-400 text-sm mt-0.5">
                {{ scheduleSummary }}
              </p>
            </div>
          </div>
          <Icon
            name="ChevronDown"
            :size="20"
            class="text-surface-500 transition-transform flex-shrink-0"
            :class="{ 'rotate-180': scheduleExpanded }"
          />
        </div>

        <div v-if="scheduleLoading" class="flex-1 flex items-center justify-center py-6">
          <div class="flex flex-col gap-2">
            <Skeleton variant="text" width="160px" height="32px" />
            <Skeleton variant="text" width="120px" height="24px" />
          </div>
        </div>
        <template v-else>
          <div v-if="scheduleExpanded" class="space-y-3 flex-1">
            <EmptyState
              v-if="scheduledPosts.length === 0"
              icon="Calendar"
              title="No upcoming posts"
              description="Schedule content from the Publish page"
              action-label="View schedule"
              action-icon="Calendar"
              variant="default"
              @action="goTo('/schedule')"
            />
            <template v-else>
              <div
                v-for="post in scheduledPosts.slice(0, 5)"
                :key="post.id"
                class="flex items-center gap-3 p-3 rounded-xl bg-surface-800/50"
              >
                <PlatformIcon :platform="post.platform" size="sm" variant="outline" />
                <div class="flex-1 min-w-0">
                  <p class="font-medium text-surface-100 truncate text-sm">{{ post.video_title || 'Video' }}</p>
                  <p class="text-surface-400 text-xs">{{ formatScheduleTime(post.scheduled_at) }}</p>
                </div>
              </div>
              <Button variant="ghost" size="sm" to="/schedule" class="w-full mt-2" @click.stop>
                Open full schedule
                <Icon name="ArrowRight" :size="16" />
              </Button>
            </template>
          </div>
          <NuxtLink
            v-else
            :to="localePath('/schedule')"
            class="inline-flex items-center gap-2 text-sm text-primary-400 hover:text-primary-300 transition-colors mt-2"
            @click.stop
          >
            View schedule
            <Icon name="ArrowRight" :size="14" />
          </NuxtLink>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: 'auth',
})

const api = useApi()
const localePath = useLocalePath()

const statsLoading = ref(true)
const videosLoading = ref(true)
const scheduleLoading = ref(true)
const scheduleExpanded = ref(false)
const scheduledPosts = ref<any[]>([])

interface StatItem {
  label: string
  value: string | number
  icon: string
  iconBg: string
  iconColor: string
  change?: number
}

const stats = ref<StatItem[]>([
    { label: 'Total Videos', value: '0', icon: 'Video', iconBg: 'bg-primary-500/20', iconColor: 'text-primary-400', change: 0 },
  { label: 'Patterns Found', value: '0', icon: 'Target', iconBg: 'bg-accent-500/15', iconColor: 'text-accent-400', change: 0 },
  { label: 'Posts Published', value: '0', icon: 'Send', iconBg: 'bg-emerald-500/20', iconColor: 'text-emerald-400', change: 0 },
  { label: 'Total Views', value: '0', icon: 'Eye', iconBg: 'bg-amber-500/20', iconColor: 'text-amber-400', change: 0 },
])

const recentVideos = ref<any[]>([])

const scheduleSummary = computed(() => {
  const n = scheduledPosts.value.length
  if (n === 0) return 'No upcoming posts'
  if (n === 1) return '1 post scheduled'
  return `${n} posts scheduled`
})

const prefs = usePreferences()
function formatScheduleTime(iso: string) {
  return prefs.formatInUserTz(iso)
}


async function fetchDashboard() {
  statsLoading.value = true
  try {
    const data = await api.analytics.dashboard()
    stats.value = [
      { label: 'Total Videos', value: data.video_count ?? 0, icon: 'Video', iconBg: 'bg-primary-500/20', iconColor: 'text-primary-400', change: 0 },
      { label: 'Patterns Found', value: data.pattern_count ?? 0, icon: 'Target', iconBg: 'bg-accent-500/15', iconColor: 'text-accent-400', change: 0 },
      { label: 'Posts Published', value: data.post_count ?? 0, icon: 'Send', iconBg: 'bg-emerald-500/20', iconColor: 'text-emerald-400', change: 0 },
      { label: 'Total Views', value: data.total_views ?? 0, icon: 'Eye', iconBg: 'bg-amber-500/20', iconColor: 'text-amber-400', change: 0 },
    ]
  } catch {
    // Keep default stats on error
  } finally {
    statsLoading.value = false
  }
}

async function fetchRecentVideos() {
  videosLoading.value = true
  try {
    const res = await api.videos.list({ limit: 5 })
    recentVideos.value = res?.items ?? []
  } catch {
    recentVideos.value = []
  } finally {
    videosLoading.value = false
  }
}

async function fetchScheduled() {
  scheduleLoading.value = true
  try {
    const res = await api.posts.scheduled()
    scheduledPosts.value = (res as { items?: any[] })?.items ?? []
  } catch {
    scheduledPosts.value = []
  } finally {
    scheduleLoading.value = false
  }
}

function goTo(path: string) {
  return navigateTo(localePath(path))
}

onMounted(() => {
  fetchDashboard()
  fetchRecentVideos()
  fetchScheduled()
})
</script>
