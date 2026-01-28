<template>
  <div class="container-wide py-8 lg:py-12">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
      <div>
        <h1 class="text-3xl lg:text-4xl font-mono font-bold text-surface-100">Analytics</h1>
        <p class="text-surface-400 mt-2">Track your content performance across platforms</p>
      </div>
      <div class="relative">
        <select v-model="dateRange" class="input w-auto pr-10 appearance-none cursor-pointer">
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="90">Last 90 days</option>
        </select>
        <Icon name="ChevronDown" :size="16" class="absolute right-3 top-1/2 -translate-y-1/2 text-surface-500 pointer-events-none" />
      </div>
    </div>

    <!-- Overview Stats -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 mb-8">
      <Card v-for="stat in overviewStats" :key="stat.label" :class="stat.borderClass">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-surface-400 text-sm mb-1">{{ stat.label }}</p>
            <p class="text-2xl lg:text-3xl font-mono font-bold text-surface-100">
              {{ formatNumber(stat.value) }}
            </p>
          </div>
          <div 
            class="w-10 h-10 lg:w-12 lg:h-12 rounded-xl flex items-center justify-center"
            :class="stat.iconBg"
          >
            <Icon :name="stat.icon" :size="20" :class="stat.iconColor" />
          </div>
        </div>
        <p 
          v-if="stat.change !== undefined" 
          class="text-sm mt-3 flex items-center gap-1"
          :class="stat.change >= 0 ? 'text-emerald-400' : 'text-red-400'"
        >
          <Icon :name="stat.change >= 0 ? 'TrendingUp' : 'TrendingDown'" :size="14" />
          <span>{{ stat.change >= 0 ? '+' : '' }}{{ stat.change }}% from last period</span>
        </p>
      </Card>
    </div>

    <!-- Platform Breakdown & Top Performing -->
    <div class="grid lg:grid-cols-2 gap-6 lg:gap-8 mb-8">
      <!-- Platform Performance -->
      <Card>
        <h2 class="text-xl font-mono font-semibold text-surface-100 mb-6">Platform Performance</h2>
        
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
                <Icon name="Heart" :size="14" class="text-rose-400" />
                {{ formatNumber(platform.likes) }}
              </span>
              <span class="flex items-center gap-1">
                <Icon name="MessageCircle" :size="14" class="text-primary-400" />
                {{ formatNumber(platform.comments) }}
              </span>
              <span class="flex items-center gap-1">
                <Icon name="Share2" :size="14" class="text-emerald-400" />
                {{ formatNumber(platform.shares) }}
              </span>
              <Badge variant="primary" class="ml-auto">{{ platform.engagement }}% engagement</Badge>
            </div>
          </div>
        </div>
      </Card>

      <!-- Top Performing Content -->
      <Card>
        <h2 class="text-xl font-mono font-semibold text-surface-100 mb-6">Top Performing Content</h2>
        
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
            <span class="text-2xl font-mono font-bold text-surface-600 w-8 text-center">
              #{{ index + 1 }}
            </span>
            <div class="w-16 h-12 bg-surface-700 rounded-lg flex items-center justify-center overflow-hidden flex-shrink-0">
              <img 
                v-if="video.thumbnail_url" 
                :src="video.thumbnail_url" 
                :alt="video.title"
                class="w-full h-full object-cover"
              />
              <Icon v-else name="Video" :size="20" class="text-surface-500" />
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
      <h2 class="text-xl font-mono font-semibold text-surface-100 mb-6">Pattern Insights</h2>
      
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
            <Icon :name="insight.icon" :size="18" class="text-primary-400" />
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
            <span class="text-sm font-semibold text-surface-200">{{ insight.score }}</span>
          </div>
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

const dateRange = ref('30')

const overviewStats = [
  { 
    label: 'Total Views', 
    value: 0, 
    icon: 'Eye',
    iconBg: 'bg-primary-500/20',
    iconColor: 'text-primary-400',
    borderClass: 'border-l-4 border-l-primary-500',
    change: 0,
  },
  { 
    label: 'Total Engagement', 
    value: 0, 
    icon: 'Heart',
    iconBg: 'bg-rose-500/20',
    iconColor: 'text-rose-400',
    borderClass: 'border-l-4 border-l-rose-500',
    change: 0,
  },
  { 
    label: 'Posts Published', 
    value: 0, 
    icon: 'Send',
    iconBg: 'bg-emerald-500/20',
    iconColor: 'text-emerald-400',
    borderClass: 'border-l-4 border-l-emerald-500',
    change: 0,
  },
  { 
    label: 'Avg. Engagement', 
    value: 0, 
    icon: 'TrendingUp',
    iconBg: 'bg-amber-500/20',
    iconColor: 'text-amber-400',
    borderClass: 'border-l-4 border-l-amber-500',
    change: 0,
  },
]

const platformStats = [
  { id: 'instagram' as const, name: 'Instagram', views: 0, likes: 0, comments: 0, shares: 0, engagement: 0 },
  { id: 'tiktok' as const, name: 'TikTok', views: 0, likes: 0, comments: 0, shares: 0, engagement: 0 },
  { id: 'youtube' as const, name: 'YouTube', views: 0, likes: 0, comments: 0, shares: 0, engagement: 0 },
  { id: 'facebook' as const, name: 'Facebook', views: 0, likes: 0, comments: 0, shares: 0, engagement: 0 },
]

const topVideos = ref<any[]>([])
const patternInsights = ref<any[]>([])

const formatNumber = (num: number) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}
</script>
