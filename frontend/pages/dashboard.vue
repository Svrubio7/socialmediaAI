<template>
  <div class="container-wide py-8 lg:py-10">
    <!-- Header -->
    <div class="mb-6 lg:mb-8">
      <h1 class="text-xl lg:text-2xl font-mono font-normal text-surface-100">Dashboard</h1>
      <p class="text-surface-400 mt-1 text-sm">Welcome back! Here's an overview of your content.</p>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <template v-if="statsLoading">
        <SharedStatCardSkeleton v-for="i in 4" :key="i" />
      </template>
      <template v-else>
        <SharedStatCard
          v-for="stat in stats"
          :key="stat.label"
          :label="stat.label"
          :value="stat.value"
          :icon="stat.icon"
          :icon-bg="stat.iconBg"
          :icon-color="stat.iconColor"
          :change="stat.change"
          card-class="bg-surface-700/20 dark:bg-surface-700/30 p-4 rounded-2xl border border-surface-600/40"
        />
      </template>
    </div>

    <!-- Overview section cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
      <NuxtLink
        v-for="section in overviewSections"
        :key="section.to"
        :to="section.href"
        class="block no-underline group min-h-[120px] rounded-2xl p-5 lg:p-6 transition-all duration-200 hover:scale-[1.01] hover:shadow-lg cursor-pointer bg-surface-700/20 dark:bg-surface-700/30"
        :class="section.edgeClass"
      >
        <div class="flex items-start gap-4">
          <div
            class="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0"
            :class="section.iconBg"
          >
            <UiIcon :name="section.icon" :size="22" class="text-surface-800 dark:text-surface-100" />
          </div>
          <div class="min-w-0 flex-1">
            <h3 class="font-mono font-medium text-base text-surface-900 dark:text-surface-100">{{ section.title }}</h3>
            <p class="text-surface-600 dark:text-surface-400 text-sm mt-1">{{ section.description }}</p>
            <p v-if="section.summary" class="text-surface-500 dark:text-surface-500 text-xs mt-2 font-medium">{{ section.summary }}</p>
          </div>
        </div>
      </NuxtLink>
    </div>

    <!-- Recent Videos & Posting Schedule -->
    <div class="grid lg:grid-cols-2 gap-6">
      <!-- Recent Videos (whole card links to /videos) -->
      <NuxtLink
        :to="videosHref"
        class="flex flex-col min-h-[280px] rounded-2xl border border-primary-500/20 hover:border-primary-500/35 hover:scale-[1.01] hover:shadow-lg cursor-pointer transition-all duration-200 p-5 lg:p-6 bg-surface-700/20 dark:bg-surface-700/30 block no-underline"
      >
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-mono font-medium text-surface-900 dark:text-surface-100">Recent Videos</h2>
          <span class="rounded-xl inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-primary-400">
            View all
            <UiIcon name="ArrowRight" :size="14" />
          </span>
        </div>

        <div v-if="videosLoading" class="flex-1 flex items-center justify-center py-6">
          <div class="flex flex-col items-center gap-2">
            <UiSkeleton variant="rounded" width="56px" height="40px" />
            <UiSkeleton variant="text" width="100px" />
            <UiSkeleton variant="text" width="64px" />
          </div>
        </div>
        <SharedEmptyState
          v-else-if="recentVideos.length === 0"
          icon="Video"
          title="No videos yet"
          description="Click to go to Videos and upload your first video"
          variant="primary"
        />
        <div v-else class="space-y-2 flex-1">
          <div
            v-for="video in recentVideos"
            :key="video.id"
            class="flex items-center gap-3 p-2.5 rounded-xl bg-surface-600/25 dark:bg-surface-600/30 hover:bg-surface-600/40 transition-colors"
          >
            <div class="w-12 h-9 bg-surface-600/50 rounded-lg flex items-center justify-center overflow-hidden flex-shrink-0">
              <img
                v-if="video.thumbnail_url"
                :src="video.thumbnail_url"
                :alt="video.filename"
                class="w-full h-full object-cover"
              />
              <UiIcon v-else name="Video" :size="16" class="text-surface-500" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium text-surface-100 truncate text-sm">{{ video.filename }}</p>
              <div class="flex items-center gap-2 mt-0.5">
                <SharedStatusBadge :status="video.status" :show-dot="false" />
              </div>
            </div>
          </div>
        </div>
      </NuxtLink>

      <!-- Posting Schedule (whole card links to schedule) -->
      <NuxtLink
        :to="scheduleHref"
        class="flex flex-col min-h-[280px] rounded-2xl border border-amber-500/20 hover:border-amber-500/35 hover:scale-[1.01] hover:shadow-lg cursor-pointer transition-all duration-200 bg-surface-700/20 dark:bg-surface-700/30 p-5 lg:p-6 block no-underline"
      >
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-xl bg-amber-500/25 flex items-center justify-center flex-shrink-0">
            <UiIcon name="Calendar" :size="20" class="text-surface-800 dark:text-surface-100" />
          </div>
          <div>
            <h2 class="text-lg font-mono font-medium text-surface-900 dark:text-surface-100">Posting Schedule</h2>
            <p class="text-surface-600 dark:text-surface-400 text-xs mt-0.5">{{ scheduleSummary }}</p>
          </div>
        </div>

        <div v-if="scheduleLoading" class="flex-1 flex items-center justify-center py-4">
          <div class="flex flex-col gap-2">
            <UiSkeleton variant="text" width="140px" height="24px" />
            <UiSkeleton variant="text" width="100px" height="20px" />
          </div>
        </div>
        <template v-else>
          <div class="flex-1 min-h-0 flex flex-col">
            <!-- Full-month calendar (Notion-like, compact) -->
            <div class="grid grid-cols-7 gap-px bg-surface-600/20 dark:bg-surface-600/30 rounded-xl overflow-hidden text-center max-w-md mb-4">
              <div v-for="d in weekDayLabels" :key="d" class="py-1.5 text-[10px] font-medium uppercase tracking-wide text-surface-500 bg-surface-600/30 dark:bg-surface-600/40">{{ d }}</div>
              <div
                v-for="cell in calendarCells"
                :key="cell.key"
                class="min-h-[1.5rem] py-1 flex flex-col items-center justify-start text-surface-400"
                :class="[
                  cell.isCurrentMonth ? 'bg-surface-600/20 dark:bg-surface-600/25' : 'bg-surface-700/10 dark:bg-surface-700/15 text-surface-500',
                  cell.isToday ? 'bg-amber-500/15 dark:bg-amber-500/20' : '',
                ]"
              >
                <span class="text-[11px] font-medium" :class="cell.isToday ? 'text-amber-400' : ''">{{ cell.label }}</span>
                <span
                  v-if="cell.hasScheduled"
                  class="w-1 h-1 rounded-full bg-primary-400 mt-0.5"
                  role="presentation"
                />
              </div>
            </div>
            <template v-if="scheduledPosts.length > 0">
              <div class="space-y-2 mb-3">
                <div
                  v-for="post in scheduledPosts.slice(0, 3)"
                  :key="post.id"
                  class="flex items-center gap-3 p-2.5 rounded-lg bg-surface-600/25 dark:bg-surface-600/30"
                >
                  <SharedPlatformIcon :platform="post.platform" size="sm" variant="outline" />
                  <div class="flex-1 min-w-0">
                    <p class="font-medium text-surface-100 truncate text-xs">{{ post.video_title || 'Video' }}</p>
                    <p class="text-surface-500 text-[11px] mt-0.5">{{ formatScheduleTime(post.scheduled_at) }}</p>
                  </div>
                </div>
              </div>
            </template>
            <span class="inline-flex items-center gap-2 text-xs text-primary-400 font-medium mt-3">
              View schedule
              <UiIcon name="ArrowRight" :size="12" />
            </span>
          </div>
        </template>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'

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

const scheduleSummary = computed(() => {
  const n = scheduledPosts.value.length
  if (n === 0) return 'No upcoming posts'
  if (n === 1) return '1 post scheduled'
  return `${n} posts scheduled`
})

const calendarCells = computed(() => {
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth()
  const today = `${year}-${String(month + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
  const first = new Date(year, month, 1)
  const last = new Date(year, month + 1, 0)
  const startPad = (first.getDay() + 6) % 7
  const daysInMonth = last.getDate()
  let endPad = (7 - ((startPad + daysInMonth) % 7)) % 7
  let total = startPad + daysInMonth + endPad
  if (total < 42) {
    endPad += 42 - total
    total = 42
  }
  const prevMonth = month === 0 ? 11 : month - 1
  const prevYear = month === 0 ? year - 1 : year
  const prevLast = new Date(prevYear, prevMonth + 1, 0).getDate()
  const scheduledDates = new Set(
    (scheduledPosts.value as { scheduled_at?: string }[])
      .map((p) => {
        if (!p.scheduled_at) return ''
        const d = new Date(p.scheduled_at)
        return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
      })
      .filter(Boolean)
  )
  const cells: { key: string; label: string; isCurrentMonth: boolean; isToday: boolean; hasScheduled: boolean }[] = []
  let i = 0
  for (; i < startPad; i++) {
    const d = prevLast - startPad + i + 1
    cells.push({
      key: `p-${i}`,
      label: String(d),
      isCurrentMonth: false,
      isToday: false,
      hasScheduled: false,
    })
  }
  for (let d = 1; d <= daysInMonth; d++, i++) {
    const dateKey = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    cells.push({
      key: `c-${d}`,
      label: String(d),
      isCurrentMonth: true,
      isToday: dateKey === today,
      hasScheduled: scheduledDates.has(dateKey),
    })
  }
  for (let d = 1; i < total; d++, i++) {
    cells.push({
      key: `n-${d}`,
      label: String(d),
      isCurrentMonth: false,
      isToday: false,
      hasScheduled: false,
    })
  }
  return cells
})

const overviewSections = computed(() => {
  const n = scheduledPosts.value.length
  const scheduleSummaryText = n === 0 ? 'No upcoming posts' : n === 1 ? '1 post scheduled' : `${n} posts scheduled`
  const videoCount = recentVideos.value.length
  const videosSummary = videoCount === 0 ? 'No videos yet' : videoCount === 1 ? '1 video' : `${videoCount} videos`
  const base = [
    { to: '/account/branding', title: 'Branding', description: 'Logos, images, and brand assets for your content', icon: 'Image', edgeClass: 'border border-primary-500/25 hover:border-primary-500/40', iconBg: 'bg-primary-500/30' },
    { to: '/strategies', title: 'Strategies', description: 'Chat with the assistant for scripts and schedules', icon: 'Target', edgeClass: 'border border-accent-500/25 hover:border-accent-500/40', iconBg: 'bg-accent-500/30' },
    { to: '/publish', title: 'Publish Content', description: 'Share to all platforms', icon: 'Send', edgeClass: 'border border-emerald-500/25 hover:border-emerald-500/40', iconBg: 'bg-emerald-500/30' },
    { to: '/schedule', title: 'Schedule', description: 'Manage your scheduled posts', icon: 'Calendar', edgeClass: 'border border-amber-500/25 hover:border-amber-500/40', iconBg: 'bg-amber-500/30', summary: scheduleSummaryText },
    { to: '/videos', title: 'Videos', description: 'Upload and analyze your videos', icon: 'Video', edgeClass: 'border border-primary-500/25 hover:border-primary-500/40', iconBg: 'bg-primary-500/30', summary: videosSummary },
    { to: '/editor', title: 'Editor', description: 'Edit and generate videos with timelines, layers, and templates', icon: 'Scissors', edgeClass: 'border border-accent-500/25 hover:border-accent-500/40', iconBg: 'bg-accent-500/30' },
    { to: '/analytics', title: 'Analytics', description: 'Views, engagement, and performance', icon: 'BarChart3', edgeClass: 'border border-amber-500/25 hover:border-amber-500/40', iconBg: 'bg-amber-500/30' },
  ]
  return base.map((s) => ({ ...s, href: localePath(s.to) }))
})

const videosHref = computed(() => localePath('/videos'))
const scheduleHref = computed(() => localePath('/schedule'))

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
