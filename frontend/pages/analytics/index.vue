<template>
  <div class="container-wide py-8 lg:py-12">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
      <div>
        <h1 class="text-3xl lg:text-4xl font-mono font-normal text-surface-100">Analytics</h1>
        <p class="text-surface-400 mt-2">Track your content performance across platforms</p>
      </div>
      <div class="relative">
        <select v-model="dateRange" class="input w-auto pr-10 appearance-none cursor-pointer" @change="fetchData">
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="90">Last 90 days</option>
        </select>
        <UiIcon name="ChevronDown" :size="16" class="absolute right-3 top-1/2 -translate-y-1/2 text-surface-500 pointer-events-none" />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <div class="flex flex-col items-center gap-4">
        <Skeleton variant="rounded" width="200px" height="80px" />
        <Skeleton variant="text" width="160px" />
      </div>
    </div>

    <!-- Error -->
    <Card v-else-if="error" class="border-l-4 border-l-red-500 mb-8">
      <p class="text-surface-100 font-medium">Could not load analytics</p>
      <p class="text-surface-400 text-sm mt-1">{{ error }}</p>
      <Button variant="secondary" class="mt-4" @click="fetchData">Retry</Button>
    </Card>

    <template v-else>
    <!-- Overview Stats -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 mb-8">
      <Card v-for="stat in overviewStats" :key="stat.label" :class="stat.borderClass">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-surface-400 text-sm mb-1">{{ stat.label }}</p>
            <p class="text-2xl lg:text-3xl font-mono font-normal text-surface-100">
              {{ formatStatValue(stat) }}
            </p>
          </div>
          <div 
            class="w-10 h-10 lg:w-12 lg:h-12 rounded-xl flex items-center justify-center"
            :class="stat.iconBg"
          >
            <UiIcon :name="stat.icon" :size="20" :class="stat.iconColor" />
          </div>
        </div>
        <p 
          v-if="stat.change !== undefined && stat.change !== null" 
          class="text-sm mt-3 flex items-center gap-1"
          :class="stat.change >= 0 ? 'text-emerald-400' : 'text-red-400'"
        >
          <UiIcon :name="stat.change >= 0 ? 'TrendingUp' : 'TrendingDown'" :size="14" />
          <span>{{ stat.change >= 0 ? '+' : '' }}{{ stat.change }}% from last period</span>
        </p>
      </Card>
    </div>

    <!-- Platform Breakdown & Top Performing -->
    <div class="grid lg:grid-cols-2 gap-6 lg:gap-8 mb-8">
      <!-- Platform Performance -->
      <Card>
        <h2 class="text-xl font-mono font-medium text-surface-100 mb-6">Platform Performance</h2>
        
        <div class="space-y-4">
          <div 
            v-for="platform in platformStats" 
            :key="platform.id" 
            class="p-4 rounded-xl bg-surface-800/50"
          >
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-3">
                <PlatformIcon :platform="platform.id" size="md" />
                <span class="font-medium text-surface-100">{{ platform.name }}</span>
              </div>
              <span class="text-surface-300 font-medium">{{ formatNumber(platform.views) }} views</span>
            </div>
            <div class="flex items-center gap-4 text-sm text-surface-400">
              <span class="flex items-center gap-1">
                <UiIcon name="Heart" :size="14" class="text-rose-400" />
                {{ formatNumber(platform.likes) }}
              </span>
              <span class="flex items-center gap-1">
                <UiIcon name="MessageCircle" :size="14" class="text-primary-400" />
                {{ formatNumber(platform.comments) }}
              </span>
              <span class="flex items-center gap-1">
                <UiIcon name="Share2" :size="14" class="text-emerald-400" />
                {{ formatNumber(platform.shares) }}
              </span>
              <Badge variant="primary" class="ml-auto">{{ platform.engagement }}% engagement</Badge>
            </div>
          </div>
        </div>
      </Card>

      <!-- Top Performing Content -->
      <Card>
        <h2 class="text-xl font-mono font-medium text-surface-100 mb-6">Top Performing Content</h2>
        
        <EmptyState
          v-if="topVideos.length === 0"
          icon="BarChart3"
          title="No data yet"
          description="Publish content to see your top performers"
          variant="default"
        />

        <div v-else class="space-y-3">
          <div 
            v-for="(video, index) in topVideos" 
            :key="video.id" 
            class="flex items-center gap-4 p-3 rounded-xl bg-surface-800/50"
          >
            <span class="text-2xl font-mono font-normal text-surface-600 w-8 text-center">
              #{{ index + 1 }}
            </span>
            <div class="w-16 h-12 bg-surface-700 rounded-lg flex items-center justify-center overflow-hidden flex-shrink-0">
              <img 
                v-if="video.thumbnail_url" 
                :src="video.thumbnail_url" 
                :alt="video.title"
                class="w-full h-full object-cover"
              />
              <UiIcon v-else name="Video" :size="20" class="text-surface-500" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium text-surface-100 truncate">{{ video.title }}</p>
              <p class="text-surface-400 text-sm">{{ formatNumber(video.views) }} views</p>
            </div>
            <Badge variant="success">{{ video.engagement }}%</Badge>
          </div>
        </div>
      </Card>
    </div>

    <!-- Pattern Insights -->
    <Card>
      <h2 class="text-xl font-mono font-medium text-surface-100 mb-6">Pattern Insights</h2>
      
      <EmptyState
        v-if="patternInsights.length === 0"
        icon="Lightbulb"
        title="No insights yet"
        description="Analyze more videos to get pattern insights and recommendations"
        variant="default"
      />

      <div v-else class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div 
          v-for="insight in patternInsights" 
          :key="insight.pattern" 
          class="p-4 rounded-xl bg-surface-800/50"
        >
          <div class="flex items-center gap-2 mb-2">
            <UiIcon :name="insight.icon" :size="18" class="text-primary-400" />
            <h3 class="font-medium text-surface-100">{{ insight.pattern }}</h3>
          </div>
          <p class="text-surface-400 text-sm mb-3">{{ insight.description }}</p>
          <div class="flex items-center gap-3">
            <div class="flex-1 h-2 bg-surface-700 rounded-full overflow-hidden">
              <div 
                class="h-full bg-gradient-to-r from-primary-500 to-accent-500 transition-all duration-500"
                :style="{ width: `${insight.score}%` }"
              />
            </div>
            <span class="text-sm font-medium text-surface-200">{{ insight.score }}</span>
          </div>
        </div>
      </div>
    </Card>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'app-sidebar',
  middleware: 'auth',
})

const api = useApi()
const dateRange = ref('30')
const loading = ref(true)
const error = ref<string | null>(null)

interface OverviewStat {
  label: string
  value: number
  icon: string
  iconBg: string
  iconColor: string
  borderClass: string
  change?: number
  format?: 'number' | 'percent'
}

const overviewStats = ref<OverviewStat[]>([
  { label: 'Total Views', value: 0, icon: 'Eye', iconBg: 'bg-primary-500/20', iconColor: 'text-primary-400', borderClass: 'border-l-4 border-l-primary-500', change: 0, format: 'number' },
  { label: 'Total Engagement', value: 0, icon: 'Heart', iconBg: 'bg-rose-500/20', iconColor: 'text-rose-400', borderClass: 'border-l-4 border-l-rose-500', change: 0, format: 'number' },
  { label: 'Posts Published', value: 0, icon: 'Send', iconBg: 'bg-emerald-500/20', iconColor: 'text-emerald-400', borderClass: 'border-l-4 border-l-emerald-500', change: 0, format: 'number' },
  { label: 'Avg. Engagement', value: 0, icon: 'TrendingUp', iconBg: 'bg-amber-500/20', iconColor: 'text-amber-400', borderClass: 'border-l-4 border-l-amber-500', change: 0, format: 'percent' },
])

const platformOrder = ['instagram', 'tiktok', 'youtube', 'facebook'] as const
const platformNames: Record<string, string> = { instagram: 'Instagram', tiktok: 'TikTok', youtube: 'YouTube', facebook: 'Facebook' }

const platformStats = ref<{ id: 'instagram' | 'tiktok' | 'youtube' | 'facebook'; name: string; views: number; likes: number; comments: number; shares: number; engagement: number }[]>([])

const topVideos = ref<any[]>([])
const patternInsights = ref<any[]>([])

function formatNumber(num: number): string {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

function formatStatValue(stat: OverviewStat): string {
  if (stat.format === 'percent') return `${Number(stat.value).toFixed(1)}%`
  return formatNumber(stat.value)
}

async function fetchData() {
  loading.value = true
  error.value = null
  const days = Number(dateRange.value)
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - days)
  const startDate = start.toISOString().slice(0, 10)
  const endDate = end.toISOString().slice(0, 10)
  try {
    const [dashboardRes, topRes] = await Promise.all([
      api.analytics.dashboard({ start_date: startDate, end_date: endDate }),
      api.analytics.topPerformers({ limit: 10 }),
    ])
    const d = dashboardRes as any
    overviewStats.value = [
      { label: 'Total Views', value: d.total_views ?? 0, icon: 'Eye', iconBg: 'bg-primary-500/20', iconColor: 'text-primary-400', borderClass: 'border-l-4 border-l-primary-500', change: undefined, format: 'number' },
      { label: 'Total Engagement', value: d.total_engagement ?? 0, icon: 'Heart', iconBg: 'bg-rose-500/20', iconColor: 'text-rose-400', borderClass: 'border-l-4 border-l-rose-500', change: undefined, format: 'number' },
      { label: 'Posts Published', value: d.post_count ?? 0, icon: 'Send', iconBg: 'bg-emerald-500/20', iconColor: 'text-emerald-400', borderClass: 'border-l-4 border-l-emerald-500', change: undefined, format: 'number' },
      { label: 'Avg. Engagement', value: d.average_engagement_rate ?? 0, icon: 'TrendingUp', iconBg: 'bg-amber-500/20', iconColor: 'text-amber-400', borderClass: 'border-l-4 border-l-amber-500', change: undefined, format: 'percent' },
    ]
    const breakdown = d.platform_breakdown ?? {}
    platformStats.value = platformOrder.map((id) => {
      const m = breakdown[id] ?? {}
      const views = m.views ?? 0
      const eng = (m as any).engagement_rate ?? 0
      return {
        id,
        name: platformNames[id] ?? id,
        views,
        likes: m.likes ?? 0,
        comments: m.comments ?? 0,
        shares: m.shares ?? 0,
        engagement: Math.round(eng * 10) / 10,
      }
    })
    const topItems = (topRes as any)?.items ?? d.top_performing_videos ?? []
    topVideos.value = topItems.map((v: any) => ({
      id: v.id,
      title: v.filename ?? v.title ?? 'Video',
      thumbnail_url: v.thumbnail_url,
      views: v.views ?? 0,
      engagement: v.engagement_rate ?? (v.views ? ((v.likes ?? 0) / v.views * 100) : 0),
    }))
    patternInsights.value = []
  } catch (e: any) {
    error.value = e?.data?.detail?.message ?? e?.message ?? 'Failed to load analytics'
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
watch(dateRange, fetchData)
</script>
