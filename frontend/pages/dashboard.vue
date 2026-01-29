<template>
  <div class="container-wide py-12 lg:py-14">
    <!-- Header -->
    <div class="mb-8 lg:mb-10">
      <h1 class="text-4xl lg:text-5xl font-mono font-normal text-surface-900 dark:text-surface-100">Dashboard</h1>
      <p class="text-surface-600 dark:text-surface-400 mt-3 text-lg">Welcome back! Here's an overview of your content.</p>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
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

    <!-- Overview section cards (bigger, rounded, whole-card click; visible hover, no icon hover) -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
      <Card
        v-for="section in overviewSections"
        :key="section.to"
        variant="interactive"
        :to="localePath(section.to)"
        class="group min-h-[180px] rounded-2xl p-8 lg:p-10 transition-all duration-200 hover:scale-[1.02] hover:shadow-xl hover:shadow-black/20 cursor-pointer"
        :class="section.edgeClass"
        padding="none"
      >
        <div class="flex items-start gap-5">
          <div
            class="w-16 h-16 rounded-xl flex items-center justify-center flex-shrink-0"
            :class="section.iconBg"
          >
            <UiIcon :name="section.icon" :size="32" class="text-surface-800 dark:text-surface-100" />
          </div>
          <div class="min-w-0 flex-1">
            <h3 class="font-mono font-medium text-xl text-surface-900 dark:text-surface-100">{{ section.title }}</h3>
            <p class="text-surface-600 dark:text-surface-400 text-base mt-2">{{ section.description }}</p>
            <p v-if="section.summary" class="text-surface-500 dark:text-surface-500 text-sm mt-3 font-medium">{{ section.summary }}</p>
          </div>
        </div>
      </Card>
    </div>

    <!-- Recent Videos & Posting Schedule -->
    <div class="grid lg:grid-cols-2 gap-8">
      <!-- Recent Videos -->
      <Card class="flex flex-col min-h-[320px] rounded-2xl border border-primary-500/25 hover:border-primary-500/40 transition-colors p-8 lg:p-10" padding="none">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-mono font-medium text-surface-900 dark:text-surface-100">Recent Videos</h2>
          <Button variant="ghost" size="sm" :to="localePath('/videos')">
            View all
            <UiIcon name="ArrowRight" :size="16" />
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
              <UiIcon v-else name="Video" :size="20" class="text-surface-500" />
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

      <!-- Posting Schedule (whole card links to schedule; no arrow) -->
      <Card
        variant="interactive"
        :to="localePath('/schedule')"
        class="flex flex-col min-h-[280px] rounded-2xl border border-amber-500/25 hover:border-amber-500/40 hover:scale-[1.02] hover:shadow-xl hover:shadow-black/20 bg-surface-200/80 dark:bg-surface-800/80 cursor-pointer transition-all duration-200"
        padding="lg"
      >
        <div class="flex items-center gap-4 mb-4">
          <div class="w-12 h-12 rounded-xl bg-amber-500/30 flex items-center justify-center flex-shrink-0">
            <UiIcon name="Calendar" :size="24" class="text-surface-800 dark:text-surface-100" />
          </div>
          <div>
            <h2 class="text-2xl font-mono font-medium text-surface-900 dark:text-surface-100">Posting Schedule</h2>
            <p class="text-surface-600 dark:text-surface-400 text-sm mt-0.5">{{ scheduleSummary }}</p>
          </div>
        </div>

        <div v-if="scheduleLoading" class="flex-1 flex items-center justify-center py-6">
          <div class="flex flex-col gap-2">
            <Skeleton variant="text" width="160px" height="32px" />
            <Skeleton variant="text" width="120px" height="24px" />
          </div>
        </div>
        <template v-else>
          <div class="flex-1 min-h-0">
            <div class="grid grid-cols-7 gap-px bg-surface-700 rounded-lg overflow-hidden text-center text-xs font-medium mb-4 max-w-xl">
              <div v-for="d in weekDayLabels" :key="d" class="bg-surface-800/80 py-1.5 text-surface-400">{{ d }}</div>
              <div
                v-for="i in 14"
                :key="i"
                class="aspect-square bg-surface-800/50 py-1 text-surface-500 flex items-center justify-center"
              >
                {{ scheduleDayLabels[i - 1] }}
              </div>
            </div>
            <template v-if="scheduledPosts.length > 0">
              <div
                v-for="post in scheduledPosts.slice(0, 3)"
                :key="post.id"
                class="flex items-center gap-3 p-3 rounded-xl bg-surface-800/50 mb-3"
              >
                <PlatformIcon :platform="post.platform" size="sm" variant="outline" />
                <div class="flex-1 min-w-0">
                  <p class="font-medium text-surface-100 truncate text-sm">{{ post.video_title || 'Video' }}</p>
                  <p class="text-surface-400 text-xs">{{ formatScheduleTime(post.scheduled_at) }}</p>
                </div>
              </div>
            </template>
            <span class="inline-flex items-center gap-2 text-sm text-primary-400 font-medium">
              View schedule
              <UiIcon name="ArrowRight" :size="14" />
            </span>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'app-sidebar',
  middleware: 'auth',
})

const api = useApi()
const localePath = useLocalePath()

const statsLoading = ref(true)
const videosLoading = ref(true)
const scheduleLoading = ref(true)
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
  { label: 'Total Videos', value: '0', icon: 'Video', iconBg: 'bg-primary-500/30', iconColor: 'text-surface-100', change: 0 },
  { label: 'Patterns Found', value: '0', icon: 'Target', iconBg: 'bg-accent-500/30', iconColor: 'text-surface-100', change: 0 },
  { label: 'Posts Published', value: '0', icon: 'Send', iconBg: 'bg-emerald-500/30', iconColor: 'text-surface-100', change: 0 },
  { label: 'Total Views', value: '0', icon: 'Eye', iconBg: 'bg-amber-500/30', iconColor: 'text-surface-100', change: 0 },
])

const recentVideos = ref<any[]>([])

const weekDayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const scheduleDayLabels = Array.from({ length: 14 }, (_, i) => (i + 1).toString())

const scheduleSummary = computed(() => {
  const n = scheduledPosts.value.length
  if (n === 0) return 'No upcoming posts'
  if (n === 1) return '1 post scheduled'
  return `${n} posts scheduled`
})

const overviewSections = computed(() => {
  const n = scheduledPosts.value.length
  const scheduleSummaryText = n === 0 ? 'No upcoming posts' : n === 1 ? '1 post scheduled' : `${n} posts scheduled`
  const videoCount = recentVideos.value.length
  const videosSummary = videoCount === 0 ? 'No videos yet' : videoCount === 1 ? '1 video' : `${videoCount} videos`
  return [
    { to: '/account/materials', title: 'Materials', description: 'Logos, images, and brand assets for your content', icon: 'Image', edgeClass: 'border border-primary-500/25 hover:border-primary-500/40', iconBg: 'bg-primary-500/30' },
    { to: '/strategies', title: 'Strategies', description: 'Chat with the assistant for scripts and schedules', icon: 'Target', edgeClass: 'border border-accent-500/25 hover:border-accent-500/40', iconBg: 'bg-accent-500/30' },
    { to: '/publish', title: 'Publish Content', description: 'Share to all platforms', icon: 'Send', edgeClass: 'border border-emerald-500/25 hover:border-emerald-500/40', iconBg: 'bg-emerald-500/30' },
    { to: '/schedule', title: 'Schedule', description: 'Manage your scheduled posts', icon: 'Calendar', edgeClass: 'border border-amber-500/25 hover:border-amber-500/40', iconBg: 'bg-amber-500/30', summary: scheduleSummaryText },
    { to: '/videos', title: 'Videos', description: 'Upload and analyze your videos', icon: 'Video', edgeClass: 'border border-primary-500/25 hover:border-primary-500/40', iconBg: 'bg-primary-500/30', summary: videosSummary },
    { to: '/analytics', title: 'Analytics', description: 'Views, engagement, and performance', icon: 'BarChart3', edgeClass: 'border border-amber-500/25 hover:border-amber-500/40', iconBg: 'bg-amber-500/30' },
  ]
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
      { label: 'Total Videos', value: data.video_count ?? 0, icon: 'Video', iconBg: 'bg-primary-500/30', iconColor: 'text-surface-100', change: 0 },
      { label: 'Patterns Found', value: data.pattern_count ?? 0, icon: 'Target', iconBg: 'bg-accent-500/30', iconColor: 'text-surface-100', change: 0 },
      { label: 'Posts Published', value: data.post_count ?? 0, icon: 'Send', iconBg: 'bg-emerald-500/30', iconColor: 'text-surface-100', change: 0 },
      { label: 'Total Views', value: data.total_views ?? 0, icon: 'Eye', iconBg: 'bg-amber-500/30', iconColor: 'text-surface-100', change: 0 },
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
